#!/usr/bin/env python3
"""Checked-source header reductions versus ordered compiler diagnostics."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from encoding_header_sources import CASES, HASHES, SOURCE
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def headers(ast):
    pending = [(node, ['PCINDEX ' + str(i)]) for i, node in enumerate(ast['program'])]
    result = []
    while pending:
        node, path = pending.pop()
        if node['node'] == 'Stmt_Declare':
            for item in node['fields'][0]:
                name = item['fields'][0]
                if base64.b64decode(name['fields'][0]['bytes']).lower() == b'encoding':
                    result.append((int(node['meta']['declareHeaderCloseTokenPos']['int']),
                        int(item['meta']['startTokenPos']['int']), path))
        for field, value in enumerate(node['fields']):
            if isinstance(value, dict) and 'node' in value:
                pending.append((value, path + ['PCFIELD ' + str(field)]))
            elif isinstance(value, list):
                pending.extend((child, path + ['PCFIELD ' + str(field), 'PCINDEX ' + str(i)])
                    for i, child in enumerate(value) if isinstance(child, dict) and 'node' in child)
    return sorted(result)


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for name, (_, lines, fatal) in CASES.items():
            if name.startswith(('include-', 'eval-')) or name == 'once-normal':
                continue
            label = name.replace('-', '_'); path = SOURCE / (name + '.php')
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'], (name, parsed)
            program = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            file = '$base64(' + json.dumps(b64(bytes(path))) + ')'
            p = 'P_' + label
            checks += ['U_' + label + ' = ' + program, p + ' = $ppstart(0,U_' + label + ',' + file + ')']
            completion = 'PPCNORMAL' if fatal is None else 'PPCABRUPT (STATICBYTES ($base64(' + json.dumps(b64(fatal[0])) + ')) ' + str(fatal[1]) + ')'
            checks.append(p + '.COMPLETION = ' + completion)
            ordered = headers(parsed['ast']); assert len(ordered) == len(lines)
            names = ['pldiagnostic_' + label + '_' + str(i) for i in range(len(lines))]
            if name == 'mixed-lines': names.append('pldiagnostic_foo')
            checks.append(p + '.DIAGNOSTICS = [' + ','.join(names) + ']')
            for i, (line, (token, _, occurrence)) in enumerate(zip(lines, ordered)):
                diagnostic = names[i]; location = 'pllocation_' + label + '_' + str(i)
                statement = 'statement_' + label + '_' + str(i)
                route = '[' + ','.join(occurrence) + ']'
                checks += [diagnostic + ' = PLDIAGNOSTIC "warning" "encoding-disabled" eps ' + location,
                    location + '.UNIT = 0', location + '.FILE = ' + file,
                    location + '.LINE = ' + str(line), location + '.PATH = ' + route,
                    '$occurrence_node(' + p + '.FOLD.SOURCE.OCCURRENCES,' + route + ') = (' + statement + ')',
                    '$declare_header_receipt(' + statement + ') = ((' + str(line) + ',' + str(token) + '))',
                    '$encoding_declare_line(' + statement + ') = (' + str(line) + ')']
            if name == 'mixed-lines':
                checks += ['pldiagnostic_foo = PLDIAGNOSTIC "warning" "unknown-declare" ([$ptascii("Foo")]) pllocation_foo',
                    'pllocation_foo.LINE = 3', 'pllocation_foo.PATH = [PCINDEX 0]',
                    'pllocation_foo.UNIT = 0', 'pllocation_foo.FILE = ' + file]
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    count = prepare(out)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [Path(__file__), ROOT / 'tests/semantics/encoding_header_sources.py', SOURCE / 'hashes.json',
        *(SOURCE / name for name in HASHES), *modules, *(ROOT / path for path in
        ['spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php', '.tools/php-file.so',
         '.tools/php/bin/php', '_build/default/adapter/main.exe', 'tests/semantics/profile.json',
         'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
         'tests/semantics/_build/default/numeric_runner.exe']), out / 'protocol.watsup', out / 'assertions.json']
    inputs = {str(path): sha(path) for path in watched}
    run = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
        *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
    report = {'head': head, 'premises': count, 'module_count': len(modules), 'inputs': inputs, 'process': run,
        'stdout': (out / 'check.stdout').read_text(), 'stderr': (out / 'check.stderr').read_text(),
        'inputs_stable': inputs == {str(path): sha(path) for path in watched},
        'head_stable': head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    report['passed'] = (run['exit'] == 0 and not run['timeout'] and not run['group_after']
        and report['stdout'] == 'true\n' and not report['stderr'] and report['inputs_stable'] and report['head_stable'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('pass' if report['passed'] else 'fail', count, flush=True); assert report['passed']


if __name__ == '__main__':
    main()
