#!/usr/bin/env python3
"""Reached include/eval encoding bodies preserve returns and caller work."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess

from encoding_declare_protocol import MESSAGE, PREFIX, ParserWorker, nodes, public
from encoding_list_sources import HASHES, ORACLE, SOURCE
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(out):
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    validate = runpy.run_path(str(ROOT / 'bin/php-semantics'))['dynamic_parser_stderr']
    frontend = ParserWorker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        for name in ('include-main', 'eval'):
            target = out / name; target.mkdir()
            path = SOURCE / (name + '.php')
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            if name == 'eval':
                code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                         if node['node'] == 'Scalar_String'
                         and base64.b64decode(node['fields'][0]['bytes']).startswith(b'declare(Foo=4,')]
                packet = {'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                          'profile': 'cli-raw-85', 'source': b64(code)}
            else:
                child = SOURCE / 'child.php'; code = child.read_bytes(); identity = b64(os.fsencode(child))
                packet = {'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
                          'source': b64(code), 'requested': identity, 'resolved': identity, 'opened': identity}
            unit = frontend.request(packet)
            raw = (frontend.output / 'stderr').read_bytes()
            delta = raw[len(frontend.recorded_stderr):]
            assert unit['accepted'] and validate(unit, packet['mode'], delta), (name, unit, delta)
            assert delta and not validate(unit, packet['mode'], delta + b'Unexpected\n')
            assert not validate(unit, packet['mode'], b'')
            frontend.recorded_stderr.extend(delta)
            checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
            response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked
            checks = ['U_main = ' + main,
                'S_wait = $php_file_run(U_main,2500,' + term(os.fsencode(path)) + ',' + term(os.fsencode(ROOT)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING', '$test_outputs(S_wait.EVENTS) = $ptascii("M|")']
            if name == 'eval':
                checks += ['S_wait.EVALCONTEXTS = [pevalcontext]', 'pevalcontext.UNIT = 1',
                    'pevalcontext.BYTES = ' + term(code), '$eval_response_valid(S_wait,' + response + ')',
                    'S_start = $eval_resume(S_wait,' + response + ')']
            else:
                opened = ('FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED '
                          + term(os.fsencode(child)) + ' ' + term(os.fsencode(child)) + ' ' + term(code))
                checks += ['S_wait.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
                    'pfilecontext.PHASE = FILE_RESOLVE_WAIT', 'pfilecontext.REQUESTED = ' + term(os.fsencode(child)),
                    '$file_open_response_valid(S_wait,' + opened + ')', 'S_parse = $file_open_resume(S_wait,' + opened + ')',
                    'S_parse.COMPLETION = SOURCE_PENDING', '$file_parse_response_valid(S_parse,' + response + ')',
                    'S_start = $file_parse_resume(S_parse,' + response + ')']
            line = 1 if name == 'eval' else 2
            encoding = 'DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) ' + str(line)
            unknown = 'DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii("Unsupported declare \'Foo\'")) ' + str(line)
            checks += ['S_front_found = $test_encoding_seek(S_start,1,2500)',
                'S_front_found.COMPLETION = NORMAL \\/ S_front_found.COMPLETION = BUDGET',
                'S_front = S_front_found[.COMPLETION = NORMAL]', '$test_encoding_front(S_front,1)',
                'S_front.ORIGIN = (PORIGIN 1 pcpath)',
                'S_front.TODO = (STMT statement) :: ptask_tail*',
                'statement = NStmtDeclare (SEQUENCE phpType49*) (SEQUENCE statement_body*) metadata',
                'S_front.EVENTS = S_wait.EVENTS ++ [' + encoding + ',' + encoding + ',' + unknown + ']',
                '~$unknown_declare_valid(S_front,statement)',
                '~$encoding_declare_valid(S_front[.ORIGIN = eps],statement)',
                '~$encoding_declare_valid(S_front[.ORIGIN = (PORIGIN 0 pcpath)],statement)', *public('S_front'),
                'S_body_found = $drive_steps(S_front,1)',
                'S_body_found.COMPLETION = NORMAL \\/ S_body_found.COMPLETION = BUDGET',
                'S_body = S_body_found[.COMPLETION = NORMAL]',
                'S_body.TODO = $statement_tasks(statement_body*,$origin_child(S_front.ORIGIN,[PCFIELD 1]),0) ++ ptask_tail*',
                'S_body.EVENTS = S_front.EVENTS', *public('S_body'),
                'S_zero = $drive_steps(S_body,0)', 'S_zero = S_body[.COMPLETION = BUDGET]',
                'S_resume = S_zero[.COMPLETION = NORMAL]', 'S_resume = S_body',
                'S_final = $drive_steps(S_resume,2500)', 'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
                '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps('M|E|8|A|' if name == 'eval' else 'M|C|7|A|') + ')',
                '|S_final.SOURCES| = 2', 'S_final.EVALCONTEXTS = eps', 'S_final.FILECONTEXTS = eps', *public('S_final')]
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\nvar U : program\ndec $main() : bool\ndef $main() = true\n'
                + ''.join('  -- if ' + check + '\n' for check in checks))
    finally:
        try:
            adapter.close()
        finally:
            frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=('fixtures', 'check'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve()
    if args.phase == 'fixtures': out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    paths = [Path(__file__), *(ROOT / name for name in ('bin/php-semantics', 'spec/semantics/92-strict-compiler.watsup',
        'spec/semantics/93-strict-declarations.watsup', 'spec/semantics/194-compiler-preflight.watsup',
        'spec/semantics/modules.json', 'frontend/worker.php',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/profile.json',
        'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/encoding_list_sources.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        'tests/semantics/_build/default/numeric_runner.exe')), *(SOURCE / name for name in HASHES)]
    if args.phase == 'check':
        paths += [out / name / file for name in ('include-main', 'eval') for file in ('assertions.json', 'protocol.watsup')]
    inputs = {str(path): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    report = {'head': head, 'phase': args.phase, 'inputs': inputs, 'profile': profile,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': [], 'passed': False}
    try:
        if args.phase == 'fixtures':
            prepare(out)
            report['passed'] = True
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in ('include-main', 'eval'):
                target = out / name
                run = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *modules, str(target / 'protocol.watsup')], target / 'check', 180)
                passed = (run['exit'] == 0 and not run['timeout'] and not run['group_after']
                    and (target / 'check.stdout').read_bytes() == b'true\n' and not (target / 'check.stderr').read_bytes())
                row = {'id': name, 'passed': passed, 'process': run,
                       'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0}
                report['records'].append(row); print(name, 'pass' if passed else 'fail', flush=True)
                if not passed: break
            report['passed'] = len(report['records']) == 2 and all(row['passed'] for row in report['records'])
    finally:
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = inputs == {str(path): sha(path) for path in paths}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
