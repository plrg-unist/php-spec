#!/usr/bin/env python3
"""Reached selected HALT lookup Errors across main, included and eval files."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import halt_absent_sources as cases
import halt_lookup_protocol as previous
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MESSAGE = '$ptascii("Undefined constant \\"__COMPILER_HALT_OFFSET__\\"")'
STATE_CASES = ('main-absent', 'child-present-main-absent', 'main-present-eval-absent')


def b64(value):
    return base64.b64encode(value).decode()


def term(value):
    return '$base64(' + json.dumps(b64(value)) + ')'


def checked(adapter, parsed):
    assert parsed['accepted'], parsed
    return adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']


def setup(name, directory, main, child, frontend, adapter):
    filename = term(os.fsencode(directory / 'main.php'))
    if name == 'main-absent':
        return ['S_seed = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(directory / 'main.php'))) + ')',
                'S_seed.COMPLETION = BUDGET'], 0, filename
    if name == 'child-present-main-absent':
        child_name = os.fsencode(directory / 'child.php')
        source = child.read_bytes()
        parsed = frontend.request({'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
            'requested': b64(b'child.php'), 'resolved': b64(child_name), 'opened': b64(child_name),
            'source': b64(source)})
        unit = checked(adapter, parsed)
        response = ('FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED ' +
                    term(child_name) + ' ' + term(child_name) + ' ' + term(source))
        checks = ['S_open = $php_file_run(' + main + ',2500,' + filename + ',' + term(os.fsencode(directory)) + ')',
                  'S_open.COMPLETION = SOURCE_PENDING', 'S_open.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
                  '$file_open_response_valid(S_open,' + response + ')',
                  'S_parse = $file_open_resume(S_open,' + response + ')',
                  'S_parse.COMPLETION = SOURCE_PENDING',
                  'S_seed = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + term(source) + ' ' + unit + ')',
                  'S_seed.COMPLETION = NORMAL']
        return checks, 0, filename
    code = b'return $lookup("__COMPILER_HALT_OFFSET__");'
    parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
        'profile': 'cli-raw-85', 'source': b64(code)})
    unit = checked(adapter, parsed)
    checks = ['S_wait = $php_run(' + main + ',2500,' + json.dumps(b64(os.fsencode(directory / 'main.php'))) + ')',
              'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*',
              'pevalcontext.BYTES = ' + term(code),
              'S_seed = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + term(code) + ' ' + unit + ')',
              'S_seed.COMPLETION = NORMAL']
    return checks, 1, filename


def assertions(name, directory, main, child, expected, frontend, adapter):
    checks, unit, mainfile = setup(name, directory, main, child, frontend, adapter)
    checks += previous.reach('S', 'S_seed', unit, 1)
    call = 'pconfigcall_S'
    sourcefile = '$call_sourcefile(S.FILES,' + call + '.SITE)'
    checks += [call + '.KIND = INTRINSIC_CONSTANT', call + '.SELECTION = (n_selection)',
               call + '.SITE = PORIGIN ' + str(unit) + ' pcpath',
               call + '.SENT = [NAMED_SENT (KNOWN pvalue_query)]',
               '$string_bytes(pvalue_query) = $ptascii("__COMPILER_HALT_OFFSET__")',
               '$dynamic_halt_lookup(S,' + sourcefile + ',S.DECLARATIONS) = HALT_ABSENT',
               '$dynamic_halt_valid(S,' + call + ')',
               '~$dynamic_halt_valid(S,' + call + '[.SELECTION = (S.SELECTSEQ)])',
               '~$dynamic_halt_valid(S,' + call + '[.NAMED = true])',
               '~$dynamic_halt_valid(S,' + call + '[.OWNER = (0)])',
               '~$dynamic_halt_valid(S,' + call + '[.SENT = eps])']
    if name == 'child-present-main-absent':
        childfile = term(os.fsencode(directory / 'child.php'))
        checks += [sourcefile + ' = ' + mainfile,
                   '$dynamic_halt_lookup(S,' + childfile + ',S.DECLARATIONS) = HALT_OFFSET 97',
                   '$test_outputs(S.EVENTS) = $ptascii("I:97|")',
                   childfile + ' <- S.INCLUDEDOPENED']
    elif name == 'main-present-eval-absent':
        checks += [sourcefile + ' = pevalcontext.FILE',
                   '$dynamic_halt_lookup(S,' + mainfile + ',S.DECLARATIONS) = HALT_OFFSET z_main']
    else:
        checks += [sourcefile + ' = ' + mainfile]
    checks += ['S_budget = $drive_steps(S,0)', 'S_budget.COMPLETION = BUDGET',
               'S_restored = S_budget[.COMPLETION = NORMAL]', 'S_restored = S',
               'S_error = $dynamic_halt_receive(S_restored,' + call + ')',
               'S_error.COMPLETION = THROWING n_error',
               'S_error.TODO = ptask_error*',
               'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
               'pthrowable.KIND = "Error"', 'pthrowable.ORIGIN = (' + call + '.SITE)',
               '$string_bytes($throwable_field(S_error,n_error,"message")) = ' + MESSAGE,
               '$throwable_field(S_error,n_error,"line") = PINT ' + call + '.LINE',
               '$string_bytes($throwable_field(S_error,n_error,"file")) = (' + sourcefile + ')',
               '$throwable_field(S_error,n_error,"previous") = PNULL',
               '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
               'S_error.ARRAYS[n_trace].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_frame))) :: pentry_trace*',
               '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING $ptascii("constant")',
               '$trace_array_field(S_error,n_frame,$ptascii("file")) = PSTRING (' + sourcefile + ')',
               '$trace_array_field(S_error,n_frame,$ptascii("line")) = PINT ' + call + '.LINE',
               '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
               'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_query)]',
               *['S_error.' + field + ' = S.' + field for field in
                 ('SOURCES', 'FILES', 'DECLARATIONS', 'INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS', 'EVENTS')],
               'S_step_found = $drive_steps(S_restored,1)',
               'S_step_found.COMPLETION = NORMAL \\/ S_step_found.COMPLETION = BUDGET',
               'S_step = S_step_found[.COMPLETION = NORMAL]',
               'S_step.TODO = (THROW_SEARCH n_error) :: ptask_error*',
               'S_step.OBJECTS[n_error] = S_error.OBJECTS[n_error]',
               *previous.public('S_step'),
               'S_final = $drive_steps(S_step,10000)', 'S_final.COMPLETION = NORMAL',
               'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = ' + term(expected),
               *previous.public('S_final')]
    if name == 'child-present-main-absent':
        checks += previous.reach('S_child', 'S_seed', 1, 1)
        checks += ['pdeclaration_enter = PDENTER 1 (pfilecontext.SITE) S_child.REPORTING',
                   'pdeclaration_prefix* = [PDENTER 0 eps S_child.REPORTING,PDEXIT 0 PCSCOMPLETE]',
                   'S_child.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter,PDEXIT 1 PCSCOMPLETE]',
                   '$dynamic_halt_lookup(S_child,' + term(os.fsencode(directory / 'child.php')) + ',pdeclaration_prefix* ++ [pdeclaration_enter]) = HALT_UNKNOWN',
                   'S_unknown = S_child[.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter]]',
                   'S_child.TODO = (CONFIG_INVOKE pconfigcall_child) :: ptask_child*',
                   '$dynamic_halt_valid(S_unknown,pconfigcall_child)',
                   '$dynamic_halt_receive(S_unknown,pconfigcall_child).COMPLETION = UNSUPPORTED "halt offset constant query"']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    selection = {name: cases.CASES[name] for name in STATE_CASES if not args.case or name in args.case}
    assert selection and set(args.case) <= selection.keys()
    sources, out = args.sources.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert json.loads((sources / 'native-report.json').read_text())['result'] == 'pass'
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        for name, (source, child_source, expected) in selection.items():
            directory = sources / name
            assert (directory / 'main.php').read_bytes() == source
            assert child_source is None or (directory / 'child.php').read_bytes() == child_source
            assert (directory / 'native-stdout').read_bytes() == expected
            parsed = frontend.request({'op': 'parse', 'source': b64(source)})
            main_fixture = checked(adapter, parsed)
            checks = assertions(name, directory, main_fixture,
                directory / 'child.php' if child_source is not None else None,
                expected, frontend, adapter)
            target = out / name
            target.mkdir()
            (target / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
            fixture = target / 'protocol.watsup'
            fixture.write_text(previous.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + check + '\n' for check in checks))
            modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(fixture)]
            result = subprocess.run(command, cwd=ROOT, env=types.ENV, capture_output=True, timeout=150)
            (target / 'stdout').write_bytes(result.stdout)
            (target / 'stderr').write_bytes(result.stderr)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            records.append({'id': name, 'pass': passed, 'checks': len(checks), 'exit': result.returncode,
                            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(), 'command': command})
            print(name, passed, len(checks), flush=True)
            if not passed:
                break
    finally:
        adapter.close()
        frontend.close()
    report = {'result': 'pass' if len(records) == len(selection) and all(r['pass'] for r in records) else 'fail',
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'runtime_sha256': hashlib.sha256((ROOT / 'spec/semantics/400-dynamic-constants.watsup').read_bytes()).hexdigest(),
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
