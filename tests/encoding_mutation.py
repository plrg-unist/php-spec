#!/usr/bin/env python3
"""Checked encoding provenance cannot override fresh payload mutation."""
import base64
import copy
import json
from validate import ROOT, Worker, require, normalize, structurally_equal


def main():
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'zend.multibyte=1',
                       '-d', 'internal_encoding=UTF-8', '-d', 'mbstring.substitute_character=65533',
                       str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    try:
        source = b'<?php declare(encoding="SJIS"); $\xff=1; /*\xff*/'
        parsed = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')
        checked = require(adapter.call(op='elaborate', ast=parsed['ast']), 'checked fixture')['ast']
        first = require(frontend.call(op='print', ast=checked), 'print')['source']
        provenance = copy.deepcopy(checked)
        provenance['encoding']['original'] = base64.b64encode(b'<?php echo "must never print";').decode()
        provenance = require(adapter.call(op='check', ast=provenance), 'changed provenance')['ast']
        assert require(frontend.call(op='print', ast=provenance), 'provenance print')['source'] == first
        changed = copy.deepcopy(checked)
        # The checked variable name now denotes U+3042, not the decoder's U+FFFD.
        changed['program'][1]['fields'][0]['fields'][0]['fields'][0]['bytes'] = base64.b64encode('あ'.encode()).decode()
        changed = require(adapter.call(op='elaborate', ast=changed), 'changed checked name')['ast']
        printed = require(frontend.call(op='print', ast=changed), 'changed print')['source']
        assert printed != first
        assert require(frontend.call(op='oracle', source=printed), 'changed oracle')['accepted']
        reparsed = require(frontend.call(op='parse', source=printed), 'changed reparse')['ast']
        assert structurally_equal(normalize(changed), normalize(reparsed))
        print(json.dumps({'checks': 3, 'passed': 3, 'properties': ['unused spelling provenance', 'checked name mutation affects source', 'mutated byte payload roundtrip']}))
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    main()
