#!/usr/bin/env python3
"""Keep misplaced namespaces checked so compilation owns their diagnostic."""
import base64
from corpus import phpt
from validate import ROOT, Worker, normalize, require, structurally_equal


SOURCES = [
    b'<?php\nclass A extends Exception { public function __wakeup() {} }\nnamespace N;\n',
    *(base64.b64decode(phpt(ROOT / name)['source_b64']) for name in (
        'vendor/php-src/Zend/tests/function_outside_namespace.phpt',
        'vendor/php-src/Zend/tests/namespaces/ns_068.phpt',
        'vendor/php-src/Zend/tests/namespaces/ns_083.phpt')),
    b'<?php namespace N; class A {}',
]
REJECTED = [
    b'<?php class A {} namespace ;',
    b'<?php class A { namespace N;',
    b'<?php namespace N; namespace M {}',
    b'<?php namespace N { namespace M {} }',
    b'<?php class A {} namespace N; class self {}',
]


def main():
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    try:
        for source in SOURCES:
            encoded = base64.b64encode(source).decode()
            assert require(frontend.call(op='oracle', source=encoded), 'parse oracle')['accepted']
            parsed = require(frontend.call(op='parse', source=encoded), 'parse')
            assert parsed['accepted'], parsed
            checked = require(adapter.call(op='check', ast=parsed['ast']), 'checked AST')
            assert checked['ast'] == parsed['ast']
            printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
            reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
            assert reparsed['accepted']
            assert structurally_equal(normalize(parsed['ast']), normalize(reparsed['ast']))
        for source in REJECTED:
            result = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'invalid source')
            assert not result['accepted'], result
    finally:
        frontend.close()
        adapter.close()
    print('namespace placement: five original/printed checked sources; five syntax or unrelated-namespace rejections')


if __name__ == '__main__':
    main()
