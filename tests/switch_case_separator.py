#!/usr/bin/env python3
"""Switch case separators survive checked AST and fresh source printing."""
import base64
import copy
from validate import ROOT, Worker, require, normalize, structurally_equal

CASES = [
    (b'<?php switch (1) { case 1: echo 1; }', [False]),
    (b'<?php switch (1) { case 1; echo 1; }', [True]),
    (b'<?php switch (1) { default: echo 1; }', [False]),
    (b'<?php switch (1) { default; echo 1; }', [True]),
    (b'<?php switch (1) { case 1; echo 1; default: echo 2; }', [True, False]),
    (b'<?php\nswitch (1) {\n case 1 /* note */\n ; echo 1;\n default /* note */ : echo 2;\n}', [True, False]),
    (b'<?php switch (1): case 1; echo 1; default: echo 2; endswitch;', [True, False]),
]


def cases(ast):
    return ast['program'][0]['fields'][1]


def main():
    php = ROOT / '.tools/php/bin/php'
    frontend = Worker([str(php), '-n', str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    try:
        for source, expected in CASES:
            parsed = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')
            assert parsed['accepted'], parsed
            ast = parsed['ast']
            assert [node['meta']['caseSemicolon'] for node in cases(ast)] == expected
            checked = require(adapter.call(op='check', ast=ast, fixture=True), 'check')
            assert checked['ast'] == ast
            printed = require(frontend.call(op='print', ast=ast), 'print')
            reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
            assert reparsed['accepted']
            assert [node['meta']['caseSemicolon'] for node in cases(reparsed['ast'])] == expected
            assert structurally_equal(normalize(ast), normalize(reparsed['ast']))
        ast = require(frontend.call(op='parse', source=base64.b64encode(CASES[1][0]).decode()), 'parse')['ast']
        for value in (None, 1, 'true', {'int': '1'}):
            edited = copy.deepcopy(ast)
            cases(edited)[0]['meta']['caseSemicolon'] = value
            assert not adapter.call(op='check', ast=edited).get('ok')
    finally:
        frontend.close()
        adapter.close()
    print('7 switch separator source/roundtrip profiles and malformed-bool controls passed')


if __name__ == '__main__':
    main()
