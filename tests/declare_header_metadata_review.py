#!/usr/bin/env python3
"""Independent declare-header token receipts through checked reconstruction."""
import base64
import copy
import hashlib
import json

from validate import ROOT, Worker, normalize, require, structurally_equal

KEYS = ('declareHeaderCloseLine', 'declareHeaderCloseTokenPos')
PAIR = ['declare(encoding=1)\n{echo "B|";}', 'declare(encoding=1\n){echo "B|";}']


def declares(ast):
    found, pending = [], [ast]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if value.get('node') == 'Stmt_Declare': found.append(value)
            pending.extend(value.values())
        elif isinstance(value, list): pending.extend(value)
    return sorted(found, key=lambda node: int(node['meta']['startTokenPos']['int']))


def without_receipts(ast):
    result = copy.deepcopy(ast)
    for node in declares(result):
        for key in KEYS: node['meta'].pop(key, None)
    return result


def main():
    cases = []
    for index, body in enumerate(PAIR):
        cases += [('pair-file-' + str(index), ('<?php\n' + body + '\n').encode(), {}, 'file', [2 + index], 6 + index),
                  ('pair-eval-' + str(index), (body + '\n').encode(), {}, 'eval', [1 + index], 5 + index)]
    for name, body, lines in [
        ('repeated', 'declare(\n encoding=123,\n ENCODING=1.25\n); echo "B|";', [5]),
        ('comments', 'declare(\n encoding="a)" /* ( ) */\n) /* (\n ) */ { echo "B|"; }', [4]),
        ('parentheses', 'declare(\n encoding=((123 . "x)"))\n);', [4]),
        ('body-lines', 'declare(encoding=1)\n{\n echo "B|";\n}', [2]),
        ('colon', 'declare(\n encoding=1\n):\necho "B|";\nenddeclare;', [4]),
        ('bare-body', 'declare(\n encoding=1\n)\necho "B|";', [4]),
        ('semicolon', 'declare(encoding=1)\n;', [2]),
        ('heredoc', 'declare(encoding=<<<TXT\ntext ) (\nTXT\n);', [5]),
        ('ordinary-directive', 'declare(\n Foo=(function(){ return ")"; })\n);', [4]),
        ('nested-header', 'declare(\n encoding=1,\n Foo=function() {\n  declare(\n   encoding=2\n  );\n }\n);', [9, 7]),
    ]:
        cases.append((name, ('<?php\n' + body + '\n').encode(), {}, 'file', lines, None))
    cases.append(('crlf', b'<?php\r\ndeclare(\r\n ticks=0\r\n) { echo "B|"; }\r\n', {}, 'file', [4], None))
    text = '<?php\ndeclare(\n ticks=0\n) { echo "B|"; }\n'
    cases.append(('utf16', b'\xff\xfe' + text.encode('utf-16le'),
                  {'zend.multibyte': '1', 'internal_encoding': 'UTF-8'}, 'file', [4], None))
    cases.append(('latin1', b'<?php\ndeclare(\n ticks=0 /*\xff ) ( */\n) { echo "B|"; }\n',
                  {'zend.multibyte': '1', 'internal_encoding': 'UTF-8', 'zend.script_encoding': 'ISO-8859-1'}, 'file', [4], None))
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    originals, records = {}, []
    try:
        for name, source, ini, mode, lines, token in cases:
            flags = [part for key, value in ini.items() for part in ('-d', key + '=' + value)]
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(ROOT / 'frontend/worker.php')])
            try:
                packet = {'op': 'parse', 'source': base64.b64encode(source).decode()}
                if mode == 'eval': packet.update(op='parse-eval', id='1', mode='eval', profile='cli-raw-85')
                parsed = require(frontend.call(**packet), name + ' parse'); assert parsed['accepted'], parsed
                ast = parsed['ast']; nodes = declares(ast)
                assert [int(node['meta'][KEYS[0]]['int']) for node in nodes] == lines, name
                if token is not None: assert nodes[0]['meta'][KEYS[1]] == {'int': str(token)}, name
                checked = require(adapter.call(op='elaborate', ast=ast, fixture=True), name + ' checked')
                assert checked['ast'] == ast
                printed = require(frontend.call(op='print', ast=checked['ast']), name + ' fresh print')
                assert printed['ast'] == ast
                reparsed = require(frontend.call(op='parse', source=printed['source']), name + ' printed parse')
                assert reparsed['accepted'] and structurally_equal(normalize(ast), normalize(reparsed['ast']))
                for key in KEYS:
                    edited = copy.deepcopy(ast); declares(edited)[0]['meta'][key] = {'int': '99'}
                    changed = require(adapter.call(op='elaborate', ast=edited), name + ' edited receipt')['ast']
                    assert changed == edited
                    assert require(frontend.call(op='print', ast=changed), name + ' edited print')['source'] == printed['source']
                    absent = copy.deepcopy(ast); del declares(absent)[0]['meta'][key]
                    assert require(adapter.call(op='elaborate', ast=absent), name + ' absent receipt')['ast'] == absent
                    malformed = copy.deepcopy(ast); declares(malformed)[0]['meta'][key] = {'bytes': 'MQ=='}
                    assert not adapter.call(op='check', ast=malformed)['ok']
                    expected = int(nodes[0]['meta'][key]['int'])
                    bad_fixture = checked['fixture'].replace('M' + key + ' (' + str(expected) + ')', 'M' + key + ' ("bad")', 1)
                    assert bad_fixture != checked['fixture']
                    assert not adapter.call(op='elaborate_fixture', fixture=bad_fixture)['ok']
                empty = without_receipts(ast)
                assert require(adapter.call(op='elaborate', ast=empty), name + ' no receipt')['ast'] == empty
                originals[name] = ast
                records.append({'id': name, 'mode': mode, 'ini': ini,
                    'source_sha256': hashlib.sha256(source).hexdigest(),
                    'receipts': [{key: node['meta'][key] for key in KEYS} for node in nodes]})
            finally:
                frontend.close()
        for mode in ('file', 'eval'):
            left, right = [originals['pair-' + mode + '-' + str(index)] for index in (0, 1)]
            assert left != right and without_receipts(left) == without_receipts(right)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', str(ROOT / 'frontend/worker.php')])
        try:
            control = require(frontend.call(op='parse', source=base64.b64encode(b'<?php echo "B|";').decode()), 'nondeclare control')
            assert control['accepted'] and not declares(control['ast'])
            assert all(key not in control['ast']['program'][0]['meta'] for key in KEYS)
        finally:
            frontend.close()
    finally:
        adapter.close()
    print(json.dumps({'passed': True, 'profiles': len(cases), 'records': records,
                      'scope': 'checked lexical receipt transport and fresh printing; semantic receipt guards are separate'}))


if __name__ == '__main__':
    main()
