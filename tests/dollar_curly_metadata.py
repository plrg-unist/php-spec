#!/usr/bin/env python3
"""Legacy interpolation grammar flags survive checked fresh printing."""
import base64
import copy
from validate import ROOT, Worker, normalize, require, structurally_equal
from destructuring_metadata import nodes

CASES = [
    (b'<?php function f(){return "${name}";}', [1]),
    (b'<?php function f(){return "${a[0]}";}', [1]),
    (b'<?php function f(){return "${$name}";}', [2]),
    (b'<?php function f(){return "${\'name\'}";}', [2]),
    (b'<?php function f(){return "${(NAME)}";}', [2]),
    (b'<?php function f(){return "${(NAME)[0]}";}', [2]),
    (b'<?php function f(){return "{${$name}}{$name}";}', []),
    (b'<?php function f(){return "${a[/*key*/0]}";}', [1]),
    (b'<?php function f(){return "${ /*value*/ $name}";}', [2]),
    (b'<?php function f(){return "${ /*value*/ (NAME)}";}', [2]),
    (b'<?php function f(){return <<<END\n${name}\n${$name}\nEND;}', [1, 2]),
    (b'<?php function f(){return `${name}`;}', [1]),
]


def flagged(ast):
    for kind in ('Expr_Variable', 'Expr_ArrayDimFetch'):
        for node in nodes(ast, kind):
            if 'encapsVarKind' in node['meta']:
                yield node


def main():
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    checks = 0
    try:
        for encoding in ('plain', 'UTF-16BE'):
            flags = [] if encoding == 'plain' else ['-d', 'zend.multibyte=1', '-d', 'internal_encoding=UTF-8']
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(ROOT / 'frontend/worker.php')])
            try:
                for source, expected in CASES:
                    code = source if encoding == 'plain' else b'\xfe\xff' + source.decode().encode('utf-16be')
                    ast = require(frontend.call(op='parse', source=base64.b64encode(code).decode()), 'parse')['ast']
                    assert sorted(int(node['meta']['encapsVarKind']['int']) for node in flagged(ast)) == sorted(expected)
                    checked = require(adapter.call(op='elaborate', ast=ast, fixture=True), 'elaborate')
                    assert checked['ast'] == ast
                    printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
                    assert printed['ast'] == ast
                    reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
                    assert reparsed['accepted'] and structurally_equal(normalize(ast), normalize(reparsed['ast'])), source
                    second = require(frontend.call(op='print', ast=reparsed['ast']), 'second print')
                    assert second['source'] == printed['source']
                    checks += 6
                    if not expected:
                        continue
                    for value in (True, None, {'bytes': 'MQ=='}, {'int': '01'}):
                        malformed = copy.deepcopy(ast)
                        next(flagged(malformed))['meta']['encapsVarKind'] = value
                        assert not adapter.call(op='check', ast=malformed).get('ok')
                        checks += 1
                    for kind in (0, -1, 3):
                        malformed = copy.deepcopy(ast)
                        next(flagged(malformed))['meta']['encapsVarKind'] = {'int': str(kind)}
                        assert not frontend.call(op='print', ast=malformed).get('ok')
                        checks += 1
                    malformed = copy.deepcopy(ast)
                    target = next(flagged(malformed))
                    target['meta']['encapsVarKind'] = {'int': '2' if target['meta']['encapsVarKind'] == {'int': '1'} else '1'}
                    assert not frontend.call(op='print', ast=malformed).get('ok')
                    checks += 1
            finally:
                frontend.close()
    finally:
        adapter.close()
    print(len(CASES) * 2, 'source/encoding profiles;', checks, 'checked legacy interpolation checks passed')


if __name__ == '__main__':
    main()
