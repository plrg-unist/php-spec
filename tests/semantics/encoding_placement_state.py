#!/usr/bin/env python3
"""Checked encoding declaration paths, warning prefix, and compile-fatal guard."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

from encoding_declare_protocol import MESSAGE
from encoding_placement_sources import HASHES, SOURCE
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
FATAL = 'Encoding declaration pragma must be the very first statement in the script'


def fixture(name):
    path = SOURCE / (name + '.php')
    return path, {'op': 'parse', 'source': b64(path.read_bytes())}


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checked = {}
    try:
        for name in ('late', 'namespace', 'child'):
            path, request = fixture(name)
            parsed = frontend.request(request)
            assert parsed['accepted'], (name, parsed)
            response = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert response['ok'], (name, response)
            checked[name] = (path, response['fixture'])
    finally:
        adapter.close(); frontend.close()

    checks = []
    for name in ('late', 'namespace', 'child'):
        path, program = checked[name]
        source = '$base64(' + json.dumps(b64(os.fsencode(path))) + ')'
        checks += ['U_' + name.replace('-', '_') + ' = ' + program,
            'P_' + name.replace('-', '_') + ' = $ppstart(0,U_' + name.replace('-', '_') + ',' + source + ')']
    for name, statement_path, item_path, line in [
        ('late', '[PCINDEX 1]', '[PCINDEX 1,PCFIELD 0,PCINDEX 0]', 3),
        ('namespace', '[PCINDEX 0,PCFIELD 1,PCINDEX 0]', '[PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 0,PCINDEX 0]', 3),
        ('child', '[PCINDEX 0]', '[PCINDEX 0,PCFIELD 0,PCINDEX 0]', 2)]:
        p = 'P_' + name
        checks += [p + '.DIAGNOSTICS = [pldiagnostic_' + name + ']',
            'pldiagnostic_' + name + ' = PLDIAGNOSTIC "warning" "encoding-disabled" eps pllocation_' + name,
            'pllocation_' + name + '.UNIT = 0',
            'pllocation_' + name + '.PATH = ' + statement_path,
            'pllocation_' + name + '.LINE = ' + str(line),
            '$plmessage(pldiagnostic_' + name + ') = $ptascii(' + json.dumps(MESSAGE) + ')',
            '$occurrence_node(' + p + '.FOLD.SOURCE.OCCURRENCES,' + statement_path + ') = (statement_' + name + ')',
            '$encoding_declare_line(statement_' + name + ') = (' + str(line) + ')',
            '$occurrence_node(' + p + '.FOLD.SOURCE.OCCURRENCES,' + item_path + ') = (pcnode_' + name + ')']
    checks += [
        'P_late.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii(' + json.dumps(FATAL) + ')) 3)',
        'P_namespace.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii(' + json.dumps(FATAL) + ')) 3)',
        'P_child.COMPLETION = PPCNORMAL',
        '$encoding_declare_late(P_late,[PCINDEX 1])',
        '$encoding_declare_late(P_namespace,[PCINDEX 0,PCFIELD 1,PCINDEX 0])',
        '~$encoding_declare_late(P_child,[PCINDEX 0])',
        'P_nested_reset = P_namespace[.COMPLETION = PPCNORMAL][.DIAGNOSTICS = eps]',
        '$ppencoding_node(P_nested_reset,[PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 0,PCINDEX 0],pcnode_namespace).DIAGNOSTICS = [pldiagnostic_namespace]',
        'P_nested_bad = P_nested_reset[.FOLD.SOURCE.OCCURRENCES = eps]',
        '$ppencoding_node(P_nested_bad,[PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 0,PCINDEX 0],pcnode_namespace).COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source shape")',
        '~$encoding_declare_late(P_nested_bad,[PCINDEX 0,PCFIELD 1,PCINDEX 0])']
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    count = prepare(out)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [Path(__file__), ROOT / 'spec/semantics/92-strict-compiler.watsup',
               ROOT / 'spec/semantics/modules.json', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               out / 'protocol.watsup', out / 'assertions.json', *(SOURCE / name for name in HASHES)]
    inputs = {str(path): sha(path) for path in watched}
    run = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
    report = {'head': head, 'module_count': len(modules), 'premises': count, 'inputs': inputs,
              'process': run, 'stdout': (out / 'check.stdout').read_text(errors='replace'),
              'stderr': (out / 'check.stderr').read_text(errors='replace'),
              'head_stable': head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'inputs_stable': inputs == {str(path): sha(path) for path in watched}}
    report['passed'] = (run['exit'] == 0 and not run['timeout'] and not run['group_after']
                        and report['stdout'] == 'true\n' and report['stderr'] == ''
                        and report['head_stable'] and report['inputs_stable'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('pass' if report['passed'] else 'fail', count, flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
