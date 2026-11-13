#!/usr/bin/env python3
"""Preserve omitted and explicit-empty hook parameter lists through checked syntax."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from validate import ROOT, Worker, normalize, require, structurally_equal

CASES = [
    (b'<?php class C { public $p = 0 { set { $this->p = $value; } } }', False, 0),
    (b'<?php class C { public $p = 0 { set() { $this->p = $value; } } }', True, 0),
    (b'<?php class C { public $p = 0 { SeT /* name */ ( /* empty */ ) { $this->p = 1; } } }', True, 0),
    (b'<?php class C { public int $p = 0 { set() => 1; } }', True, 0),
    (b'<?php trait T { public $p = 0 { set => $value; } } class C { use T; }', False, 0),
    (b'<?php trait T { public $p = 0 { set() => 1; } } class C { use T; }', True, 0),
    (b'<?php class C { public $p = 0 { set($incoming) { $this->p = $incoming; } } }', True, 1),
]


def hook(ast):
    pending = [ast]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if value.get('node') == 'PropertyHook': return value
            pending.extend(value.values())
        elif isinstance(value, list): pending.extend(value)
    raise AssertionError('property hook missing')


def roundtrip(frontend, adapter, source, present, count, target, request=None):
    target.mkdir(); (target / 'source.php').write_bytes(source)
    if request is None:
        oracle = require(frontend.call(op='oracle', source=base64.b64encode(source).decode()), 'original parser')
        assert oracle['accepted']
        parsed = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')
    else:
        parsed = require(frontend.call(**request, source=base64.b64encode(source).decode()), 'source service')
        oracle = {'accepted': parsed['accepted'], 'via': request['op'] + ' native parser'}
    assert parsed['accepted']; ast = parsed['ast']; node = hook(ast)
    assert node['meta']['hookParameterList'] is present and len(node['fields'][4]) == count
    checked = require(adapter.call(op='elaborate', ast=ast, fixture=True), 'checked')
    assert checked['ast'] == ast
    printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
    out_oracle = require(frontend.call(op='oracle', source=printed['source']), 'printed parser')
    assert out_oracle['accepted']
    reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
    # Eval input has no source-encoding envelope; the printed file has one.
    left = ast['program'] if request and request['op'] == 'parse-eval' else ast
    right = reparsed['ast']['program'] if request and request['op'] == 'parse-eval' else reparsed['ast']
    assert reparsed['accepted'] and structurally_equal(normalize(left), normalize(right))
    assert hook(reparsed['ast'])['meta']['hookParameterList'] is present
    printed2 = require(frontend.call(op='print', ast=reparsed['ast']), 'second print')
    assert printed2['source'] == printed['source']
    for name, value in [('parsed', parsed), ('checked', checked), ('oracle', oracle), ('printed-oracle', out_oracle)]:
        (target / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    (target / 'printed.php').write_bytes(base64.b64decode(printed['source']))
    return ast


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--prior-basic', type=Path, help='observe saved basic prints without repeating their checked round trips')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), *(ROOT / p for p in ('frontend/worker.php', 'frontend/SourcePrinter.php',
        'spec/php.watsup', 'spec/schema.json', 'scripts/generate-schema.py', 'tests/validate.py',
        '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so'))]
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'source_agreement_credit': 0, 'records': [], 'passed': False}
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', str(ROOT / 'frontend/worker.php')])
    try:
        prior = json.loads((args.prior_basic / 'report.json').read_text()) if args.prior_basic else None
        if prior: assert prior['passed'] and len(prior['records']) == len(CASES)
        for index, (source, present, count) in enumerate(CASES):
            if prior:
                assert prior['records'][index]['source_sha256'] == hashlib.sha256(source).hexdigest()
                target = out / str(index); target.mkdir()
                for name, data in [('original', source), ('printed', (args.prior_basic / str(index) / 'printed.php').read_bytes())]:
                    result = require(frontend.call(op='oracle', source=base64.b64encode(data).decode()), name + ' parser')
                    assert result['accepted']; (target / (name + '-oracle.json')).write_text(json.dumps(result) + '\n')
            else:
                ast = roundtrip(frontend, adapter, source, present, count, out / str(index))
            report['records'].append({'id': str(index), 'presence': present, 'params': count,
                'source_sha256': hashlib.sha256(source).hexdigest(), 'roundtrip_reused': bool(prior), 'passed': True})
        if not prior:
            missing = copy.deepcopy(ast); hook(missing)['fields'][4] = []; hook(missing)['meta'].pop('hookParameterList')
            assert not frontend.call(op='print', ast=missing)['ok']
            malformed = copy.deepcopy(ast); hook(malformed)['meta']['hookParameterList'] = {'int': '1'}
            assert not adapter.call(op='check', ast=malformed)['ok']
            report['negative_checks'] = 2
        for mode in ['encoded', 'file', 'eval']:
            flags = ['-d', 'zend.multibyte=1', '-d', 'internal_encoding=UTF-8'] if mode == 'encoded' else ['-d', 'short_open_tag=1', '-d', 'precision=14']
            worker = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(ROOT / 'frontend/worker.php')])
            try:
                for present in [False, True]:
                    source = b'<?php class C { public $p = 0 { set /* name */ ' + (b'( /* empty */ ) ' if present else b'') + b'{ $this->p = $value; } } }'
                    request = None
                    if mode == 'encoded': source = b'\xff\xfe' + source.decode().encode('utf-16le')
                    else:
                        request = {'op': 'parse-' + mode, 'id': '0', 'mode': mode, 'profile': 'cli-raw-85'}
                        if mode == 'eval': source = source[len(b'<?php '):]
                        else: request.update(requested='aGVhZGVyLnBocA==', resolved=None, opened='aGVhZGVyLnBocA==')
                    name = mode + '-' + str(present).lower()
                    roundtrip(worker, adapter, source, present, 0, out / name, request)
                    report['records'].append({'id': name, 'presence': present, 'params': 0,
                        'source_sha256': hashlib.sha256(source).hexdigest(), 'passed': True})
            finally: worker.close()
        report['passed'] = True
    finally:
        try: adapter.close()
        finally: frontend.close()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p): sha(p) for p in paths}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('checked hook parameter-list profiles', len(report['records']))


if __name__ == '__main__': main()
