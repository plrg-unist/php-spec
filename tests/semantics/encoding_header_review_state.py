#!/usr/bin/env python3
"""Independent header-line/body execution, receipt refusals and included return."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

from encoding_declare_protocol import CLI, MESSAGE, PREFIX, ParserWorker, public
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('encoding_headers')
KEYS = ('declareHeaderCloseLine', 'declareHeaderCloseTokenPos')
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks, asts = [], {}
    try:
        for name in ('same-ast-a', 'same-ast-b', 'include-normal'):
            parsed = frontend.request({'op': 'parse', 'source': b64((SOURCE / (name + '.php')).read_bytes())})
            assert parsed['accepted']; asts[name] = parsed['ast']
        for name, ast in asts.items():
            checks.append('U_' + name.replace('-', '_') + ' = ' + adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture'])
        for tag, name, line, token in [('A', 'same-ast-a', 2, 6), ('B', 'same-ast-b', 3, 7)]:
            state = 'S_' + tag
            checks += ['U_' + name.replace('-', '_') + ' = PROGRAM ([statement_' + tag + '])',
                'statement_' + tag + ' = NStmtDeclare (SEQUENCE phpType49_' + tag + '*) (SEQUENCE statement_' + tag + '_body*) metadata_' + tag,
                '$declare_header_receipt(statement_' + tag + ') = ((' + str(line) + ',' + str(token) + '))',
                state + '_start = $php_run(U_' + name.replace('-', '_') + ',0,' + json.dumps(b64(os.fsencode(SOURCE / (name + '.php')))) + ')',
                state + '_found = $test_encoding_seek(' + state + '_start,0,2500)',
                state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
                state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_encoding_front(' + state + ',0)',
                state + '.TODO = (STMT statement_' + tag + ') :: ptask_' + tag + '*',
                state + '.EVENTS = [DIAGNOSTIC "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) ' + str(line) + ']',
                state + '_zero = $drive_steps(' + state + ',0)', state + '_zero = ' + state + '[.COMPLETION = BUDGET]',
                state + '_enter = $drive_steps(' + state + '_zero[.COMPLETION = NORMAL],1)',
                state + '_enter.COMPLETION = NORMAL \\/ ' + state + '_enter.COMPLETION = BUDGET',
                state + '_body = ' + state + '_enter[.COMPLETION = NORMAL]',
                state + '_body.TODO = $statement_tasks(statement_' + tag + '_body*,$origin_child(' + state + '.ORIGIN,[PCFIELD 1]),0) ++ ptask_' + tag + '*',
                *public(state), *public(state + '_body'),
                state + '_final = $drive_steps(' + state + '_body,2500)', state + '_final.COMPLETION = NORMAL',
                state + '_final.TODO = eps', '$test_outputs(' + state + '_final.EVENTS) = $ptascii("B|")', *public(state + '_final')]
        for name, key, value in [('line-zero', KEYS[0], 0), ('line-before', KEYS[0], 1),
                ('line-after', KEYS[0], 4), ('token-negative', KEYS[1], -1),
                ('token-item', KEYS[1], 5), ('token-body', KEYS[1], 9), ('token-after', KEYS[1], 14),
                ('line-only', KEYS[1], None), ('token-only', KEYS[0], None), ('both-absent', None, None)]:
            changed = copy.deepcopy(asts['same-ast-a']); meta = changed['program'][0]['meta']
            if key is None:
                for field in KEYS: del meta[field]
            elif value is None: del meta[key]
            else: meta[key] = {'int': str(value)}
            tag = name.replace('-', '_')
            fixture = adapter.request({'op': 'check', 'ast': changed, 'fixture': True})['fixture']
            checks += ['U_' + tag + ' = ' + fixture, 'U_' + tag + ' = PROGRAM ([statement_' + tag + '])',
                '$declare_header_receipt(statement_' + tag + ') = eps', '$encoding_declare_line(statement_' + tag + ') = eps',
                'P_' + tag + ' = $ppstart(0,U_' + tag + ',$ptascii("receipt.php"))',
                'P_' + tag + '.COMPLETION = PPCABRUPT (UNSUPPORTED text_' + tag + ')']
        changed = copy.deepcopy(asts['same-ast-a'])
        body_meta = changed['program'][0]['fields'][1][0]['meta']
        body_meta['endTokenPos'] = {'int': str(int(body_meta['startTokenPos']['int']) - 1)}
        checks += ['U_empty_echo = ' + adapter.request({'op': 'check', 'ast': changed, 'fixture': True})['fixture'],
            'U_empty_echo = PROGRAM ([statement_empty_echo])', '$declare_header_receipt(statement_empty_echo) = eps',
            'P_empty_echo = $ppstart(0,U_empty_echo,$ptascii("receipt.php"))',
            'P_empty_echo.COMPLETION = PPCABRUPT (UNSUPPORTED text_empty_echo)']
        checks += [
            'statement_duplicate = NStmtDeclare (SEQUENCE phpType49_A*) (SEQUENCE statement_A_body*) ((MdeclareHeaderCloseLine 2) :: metadata_A)',
            '$declare_header_receipt(statement_duplicate) = eps', '$encoding_declare_line(statement_duplicate) = eps']
        legacy = frontend.request({'op': 'parse', 'source': b64(b'<?php declare(encoding=1) { echo "B|"; }')})['ast']
        for key in KEYS: del legacy['program'][0]['meta'][key]
        checks += ['U_legacy = ' + adapter.request({'op': 'check', 'ast': legacy, 'fixture': True})['fixture'],
            'U_legacy = PROGRAM ([statement_legacy])', '$encoding_declare_line(statement_legacy) = (1)',
            '$ppstart(0,U_legacy,$ptascii("legacy.php")).COMPLETION = PPCNORMAL']

        child = SOURCE / 'normal-child.php'; code = child.read_bytes(); identity = b64(os.fsencode(child))
        unit = frontend.request({'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
            'source': b64(code), 'requested': identity, 'resolved': identity, 'opened': identity})
        raw = (frontend.output / 'stderr').read_bytes(); delta = raw[len(frontend.recorded_stderr):]
        assert unit['accepted'] and CLI['dynamic_parser_stderr'](unit, 'file', delta)
        frontend.recorded_stderr.extend(delta)
        accepted = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
        opened = 'FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED ' + term(os.fsencode(child)) + ' ' + term(os.fsencode(child)) + ' ' + term(code)
        checks += ['S_wait = $php_file_run(U_include_normal,2500,' + term(os.fsencode(SOURCE / 'include-normal.php')) + ',' + term(os.fsencode(ROOT)) + ')',
            'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
            '$file_open_response_valid(S_wait,' + opened + ')', 'S_parse = $file_open_resume(S_wait,' + opened + ')',
            '$file_parse_response_valid(S_parse,' + accepted + ')', 'S_include = $file_parse_resume(S_parse,' + accepted + ')',
            'S_child_found = $test_encoding_seek(S_include,1,2500)',
            'S_child_found.COMPLETION = NORMAL \\/ S_child_found.COMPLETION = BUDGET',
            'S_child = S_child_found[.COMPLETION = NORMAL]', '$test_encoding_front(S_child,1)',
            'S_child.ORIGIN = (PORIGIN 1 pcpath_child)',
            'S_child.EVENTS = S_wait.EVENTS ++ [DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) 5,DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii("Unsupported declare \'Foo\'")) 3]',
            *public('S_child'), 'S_final = $drive_steps(S_child,2500)', 'S_final.COMPLETION = NORMAL',
            'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = $ptascii("M|C|7|A|")',
            '|S_final.SOURCES| = 2', 'S_final.FILECONTEXTS = eps', *public('S_final')]
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\n' + PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    paths = [Path(__file__), *(ROOT / name for name in ('spec/php.watsup', 'spec/schema.json', 'spec/semantics/92-strict-compiler.watsup',
        'spec/semantics/modules.json', 'bin/php-semantics', 'frontend/worker.php', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/profile.json',
        'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/semantics/error_handler_run.py')),
        *[SOURCE / (name + '.php') for name in ('same-ast-a', 'same-ast-b', 'include-normal', 'normal-child')]]
    before = {str(path): sha(path) for path in paths}; count = prepare(out)
    before.update({str(out / name): sha(out / name) for name in ('assertions.json', 'protocol.watsup')})
    modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    run = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(out / 'protocol.watsup')], out / 'check', 180)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    report = {'head': head, 'module_count': len(modules), 'premises': count, 'inputs': before, 'process': run,
              'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'head_stable': head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'inputs_stable': before == {path: sha(Path(path)) for path in before},
              'stdout': (out / 'check.stdout').read_text(), 'stderr': (out / 'check.stderr').read_text()}
    report['passed'] = (run['exit'] == 0 and not run['timeout'] and not run['group_after'] and report['stdout'] == 'true\n'
                        and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n'); print('pass' if report['passed'] else 'fail', count)
    assert report['passed']


if __name__ == '__main__': main()
