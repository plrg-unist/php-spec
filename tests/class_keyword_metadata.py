#!/usr/bin/env python3
"""Check the authenticated class keyword line across fresh transport."""
import base64
import copy
import json
from validate import ROOT, Worker, normalize, require, structurally_equal


CASES = [
    (b'<?php class C {}', 1),
    (b'<?php\nreadonly\nclass C {}', 3),
    (b'<?php\nreadonly\nclass\nC {}', 3),
    (b'<?php\n#[A(Foo::class)]\nfinal\nclass C {}', 4),
    (b'<?php\n$o = new\nreadonly\nclass {};', 4),
    (b'<?php\n$o = new #[A(Foo::class)]\nreadonly /* class decoy */\nclass {};', 4),
    (b'<?php\n$o = new readonly /* comment\nclass fake */\nclass {};', 4),
]


def class_node(value):
    if isinstance(value, dict):
        if value.get('node') == 'Stmt_Class':
            return value
        children = value.values()
    elif isinstance(value, list):
        children = value
    else:
        return None
    for child in children:
        found = class_node(child)
        if found is not None:
            return found
    return None


def main():
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n',
                       str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    checks = 0
    try:
        for source, line in CASES:
            parsed = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')
            assert parsed['accepted'], parsed
            ast = parsed['ast']
            node = class_node(ast)
            assert node['meta']['classKeywordLine'] == {'int': str(line)}
            checked = require(adapter.call(op='elaborate', ast=ast, fixture=True), 'check')
            assert checked['ast'] == ast
            printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
            assert printed['ast'] == ast
            reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
            assert reparsed['accepted'] and structurally_equal(normalize(ast), normalize(reparsed['ast']))
            malformed = copy.deepcopy(ast)
            class_node(malformed)['meta']['classKeywordLine'] = {'bytes': 'MQ=='}
            assert not adapter.call(op='check', ast=malformed)['ok']
            checks += 5
    finally:
        frontend.close()
        adapter.close()
    print(json.dumps({'profiles': len(CASES), 'checks': checks, 'result': 'pass'}))


if __name__ == '__main__':
    main()
