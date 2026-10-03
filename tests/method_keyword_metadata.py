#!/usr/bin/env python3
"""Preserve method keyword lines independently of modifier/name positions."""
import base64
import copy
import json
from validate import ROOT, Worker, normalize, require, structurally_equal


CASES = [
    (b'<?php class C { public function f() {} }', {}, 1),
    (b'<?php\nclass Prefix {}\nclass Bad {\n public readonly function\n f() {}\n}\n', {}, 4),
    (b'<?php\nclass Prefix {}\nclass Bad {\n public readonly\nfunction  f() {}\n}\n', {}, 5),
    (b'<?php\nclass Prefix {}\nclass Bad {\n #[Marker]\n public\n readonly /* modifier\n continued */\n function /* keyword\n continued */ &\n f() {}\n}\n', {}, 8),
    (b'<?php\nclass Prefix {}\nclass Bad {\n #[Marker]\n public\n abstract /* modifier\n continued */\n final\n function /* keyword\n continued */ &\n f();\n}\n', {}, 9),
    (b'<?php\nclass C {\npublic\nstatic /* modifier */\nfunction /* keyword */ & f() {}\n}\n', {}, 5),
    (b'\xff\xfe' + '<?php\r\nclass C {\r\npublic\r\nfunction\r\nf() {}\r\n}\r\n'.encode('utf-16le'),
     {'zend.multibyte': '1', 'internal_encoding': 'UTF-8'}, 4),
]


COMBINED_CASES = [
    (b'<?php\nabstract class C { public ' + order + b' function f(); }\n', 2, order.split())
    for order in (b'readonly abstract final', b'readonly final abstract', b'abstract readonly final',
                  b'abstract final readonly', b'final readonly abstract', b'final abstract readonly')
] + [
    (b'<?php\nabstract class C {\n #[Marker(new readonly class {})]\n public abstract /* final readonly */ final\n readonly\n function f();\n}\n', 6, [b'abstract', b'final', b'readonly']),
    (b'<?php\nabstract class C {\n public readonly /* abstract final */\n final\n abstract\n function /* final */ &f();\n}\n', 6, [b'readonly', b'final', b'abstract']),
]
CASES += [(source, {}, line) for source, line, order in COMBINED_CASES]
MODIFIER_ATTRIBUTES = {'readonly': 'methodReadonlyTokenPos', 'abstract': 'methodAbstractTokenPos', 'final': 'methodFinalTokenPos'}


def modifier_order(ast):
    metadata = method(ast)['meta']
    positions = {name: int(metadata[attribute]['int']) for name, attribute in MODIFIER_ATTRIBUTES.items()}
    keyword = int(metadata['methodKeywordTokenPos']['int'])
    assert len(set(positions.values())) == 3
    assert all(int(metadata['startTokenPos']['int']) <= position < keyword for position in positions.values())
    return [name.encode() for name in sorted(positions, key=positions.get)]


def method(ast):
    pending = [ast]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if value.get('node') == 'Stmt_ClassMethod':
                return value
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    raise AssertionError('method missing')


def main():
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    originals = []
    checks = 0
    try:
        for source, ini, line in CASES:
            flags = [item for key, value in ini.items() for item in ['-d', key + '=' + value]]
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags,
                               str(ROOT / 'frontend/worker.php')])
            try:
                parsed = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')
                assert parsed['accepted'], parsed
                ast = parsed['ast']
                assert method(ast)['meta']['methodKeywordLine'] == {'int': str(line)}
                checked = require(adapter.call(op='elaborate', ast=ast, fixture=True), 'check')
                assert checked['ast'] == ast
                printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
                assert printed['ast'] == ast
                reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
                assert reparsed['accepted'] and structurally_equal(normalize(ast), normalize(reparsed['ast']))
                combined = next((order for original, _, order in COMBINED_CASES if original == source), None)
                if combined is not None:
                    assert modifier_order(ast) == combined
                    assert modifier_order(reparsed['ast']) == combined
                    checks += 2
                    if source == COMBINED_CASES[0][0]:
                        for attribute in ['methodKeywordTokenPos', *MODIFIER_ATTRIBUTES.values()]:
                            invalid = copy.deepcopy(ast)
                            method(invalid)['meta'][attribute] = {'bytes': 'NA=='}
                            assert not adapter.call(op='check', ast=invalid)['ok']
                            checks += 1
                        metadata = method(ast)['meta']
                        name_metadata = method(ast)['fields'][3]['meta']
                        start = int(metadata['startTokenPos']['int'])
                        keyword = int(metadata['methodKeywordTokenPos']['int'])
                        name_start = int(name_metadata['startTokenPos']['int'])
                        end = int(metadata['endTokenPos']['int'])
                        invalid_positions = [
                            ('method', 'startTokenPos', -1),
                            ('method', 'endTokenPos', start - 1),
                            ('name', 'startTokenPos', -1),
                            ('name', 'endTokenPos', name_start - 1),
                            ('name', 'endTokenPos', end + 1),
                            ('method', 'methodKeywordTokenPos', -1),
                            ('method', 'methodKeywordTokenPos', name_start),
                            ('method', 'methodReadonlyTokenPos', -1),
                            ('method', 'methodAbstractTokenPos', -1),
                            ('method', 'methodFinalTokenPos', -1),
                            ('method', 'methodReadonlyTokenPos', keyword),
                            ('method', 'methodReadonlyTokenPos', start - 1),
                            ('method', 'methodReadonlyTokenPos', int(metadata['methodAbstractTokenPos']['int'])),
                        ]
                        for target, attribute, position in invalid_positions:
                            invalid = copy.deepcopy(ast)
                            header = method(invalid)
                            destination = header['meta'] if target == 'method' else header['fields'][3]['meta']
                            destination[attribute] = {'int': str(position)}
                            assert not frontend.call(op='print', ast=invalid)['ok'], (target, attribute, position)
                            checks += 1
                else:
                    assert not any(attribute in method(ast)['meta'] for attribute in ['methodKeywordTokenPos', *MODIFIER_ATTRIBUTES.values()])
                malformed = copy.deepcopy(ast)
                method(malformed)['meta']['methodKeywordLine'] = {'bytes': 'NA=='}
                assert not adapter.call(op='check', ast=malformed)['ok']
                originals.append(ast)
                checks += 5
            finally:
                frontend.close()
        before = copy.deepcopy(originals[1])
        after = copy.deepcopy(originals[2])
        del method(before)['meta']['methodKeywordLine']
        del method(after)['meta']['methodKeywordLine']
        assert before == after, 'keyword split changed pre-existing AST metadata'
        checks += 1
    finally:
        adapter.close()
    print(json.dumps({'profiles': len(CASES), 'checks': checks, 'result': 'pass'}))


if __name__ == '__main__':
    main()
