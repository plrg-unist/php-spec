#!/usr/bin/env python3
"""Independent undefined-source originals, public handler admission and a frontier control."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import ENV, recorded
from recorded_worker import Worker
from source_undefined_protocol import HELPERS

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-undefined-review')
CASES = ('computed-mutation', 'empty-defined', 'throw-family')
b64 = lambda value: base64.b64encode(value).decode()
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, env=ENV, text=True).strip()


def setup_checks(fixture, source):
    start = '$php_startup_run($review_program(), 0, ' + json.dumps(b64(bytes(source))) + ', {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})'
    setup = 'dec $review_program() : program\ndef $review_program() = ' + fixture + '\n' + HELPERS
    direct = [
        'S_initial = ' + start,
        'S_before = $source_cv_seek(S_initial, 15, 0, 1500)', '$source_cv_stage(S_before, 15, 0)',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_READ_RESULT psourceoperand',
        '$error_call_valid(S_pending, perrorcall)', '$call_task_valid(S_pending, ERROR_HANDLER_INVOKE perrorcall)',
        '$call_entry_check(S_pending[.COMPLETION = NORMAL]) = S_pending[.COMPLETION = NORMAL]',
        '$task_nodes(perrorcall.RESUME) = eps', 'S_pending.REPORTING = 0',
        '$call_task_valid(S_pending[.CODE = eps], ERROR_HANDLER_INVOKE perrorcall)',
        '~$call_descriptors_valid(S_pending[.CODE = eps])',
        'S_no_code = $call_entry_check(S_pending[.CODE = eps][.COMPLETION = NORMAL])',
        'S_no_code.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'S_no_code.TODO = eps',
        '~$call_task_valid(S_pending[.SOURCES = eps], ERROR_HANDLER_INVOKE perrorcall)',
        '~$call_task_valid(S_pending[.ORIGIN = (psourceoperand.SITE)], ERROR_HANDLER_INVOKE perrorcall)',
        '~$call_task_valid(S_pending[.ERRORHANDLER.CALLBACK = eps], ERROR_HANDLER_INVOKE perrorcall)',
        '~$call_task_valid(S_pending, ERROR_HANDLER_INVOKE perrorcall[.SITE = psourceoperand.SITE])',
        '~$call_task_valid(S_pending, ERROR_HANDLER_INVOKE perrorcall[.EVENT = WARNING $ptascii("foreign") perrorcall.LINE])',
        '~$call_task_valid(S_pending, ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_NAME_RESULT psourceoperand 15])',
        'S_entered = $drive(S_pending[.COMPLETION = NORMAL], 1)',
        'S_entered.CURRENT = (pcallcontext)', 'pcallcontext.ARGC = 4',
        '$error_context_valid(S_entered, pcallcontext)', '$call_current_valid(S_entered)',
        '$call_frames_valid(S_entered, S_entered.FRAMES)', '$call_descriptors_valid(S_entered)',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        '$eval_trace_preparser(S_entered, (pcallcontext), pframe) = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("eval")', 'ptraceframe.LINE = 15', 'ptraceframe.ARGS = eps', '~ptraceframe.HASARGS',
        'S_returned = $source_cv_seek(S_entered, 15, 3, 2000)', '$source_cv_stage(S_returned, 15, 3)',
        'S_returned.RESULT = KNOWN (PBOOL false)', '$call_descriptors_valid(S_returned)',
        'S_result = $drive(S_returned[.COMPLETION = NORMAL], 1)',
        'S_result.TODO = (SOURCE_READ_RESULT psourceoperand) :: ptask_tail*',
        '$lookup(S_result.ENV, $ptascii("reviewDirect")) = (n_cell)',
        'S_result.STORE[n_cell] = DEFINED (POBJECT n_object)', '(HOBJECT n_object) <- S_result.ALLOCATIONS',
        '$task_nodes(SOURCE_READ_RESULT psourceoperand) = eps', '$heap_valid($heap_graph(S_result))',
        'S_frozen = $drive(S_result[.COMPLETION = NORMAL], 1)', 'S_frozen.RESULT = KNOWN PNULL',
        'S_frozen.TODO = (EVAL_REQUEST psourceoperand.SITE 15) :: ptask_tail*',
        'S_finished = $drive(S_frozen[.COMPLETION = NORMAL], 1)',
        'S_finished.RESULT = KNOWN (PBOOL false)', 'S_finished.FILESEQ = 0', 'S_finished.EVALCONTEXTS = eps',
        '$call_descriptors_valid(S_finished)', '$heap_valid($heap_graph(S_finished))',
    ]
    dynamic = [
        'S_initial = ' + start,
        'S_before = $source_cv_seek(S_initial, 18, 10, 2000)', '$source_cv_stage(S_before, 18, 10)',
        '$source_name_pending(S_before[.COMPLETION = NORMAL])',
        'S_pending = $drive_steps(S_before[.COMPLETION = NORMAL], 1)',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_NAME_RESULT psourceoperand z',
        'psourceoperand.INPUT = KNOWN (PSTRING $ptascii("reviewDynamic"))',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_pending, perrorcall)',
        '$call_entry_check(S_pending[.COMPLETION = NORMAL]) = S_pending[.COMPLETION = NORMAL]',
        '~$call_task_valid(S_pending[.CODE = eps], ERROR_HANDLER_INVOKE perrorcall)',
        '~$call_task_valid(S_pending[.SOURCES = eps], ERROR_HANDLER_INVOKE perrorcall)',
        '~$call_task_valid(S_pending, ERROR_HANDLER_INVOKE perrorcall[.SITE = psourceoperand.SITE])',
        '~$call_task_valid(S_pending, ERROR_HANDLER_INVOKE perrorcall[.RESUME = SOURCE_READ_RESULT psourceoperand])',
        'S_entered = $drive(S_pending[.COMPLETION = NORMAL], 1)',
        'S_entered.CURRENT = (pcallcontext)', '$error_context_valid(S_entered, pcallcontext)',
        '$call_current_valid(S_entered)', '$call_frames_valid(S_entered, S_entered.FRAMES)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$eval_trace_preparser(S_entered, (pcallcontext), pframe) = eps',
        'S_returned = $source_cv_seek(S_entered, 18, 3, 2000)', '$source_cv_stage(S_returned, 18, 3)',
        'S_result = $drive(S_returned[.COMPLETION = NORMAL], 1)',
        'S_result.TODO = (SOURCE_NAME_RESULT psourceoperand z) :: ptask_tail*',
        '$lookup(S_result.ENV, $ptascii("reviewDynamic")) = (n_cell)',
        'S_result.STORE[n_cell] = DEFINED (PSTRING $ptascii(' + json.dumps('echo "wrong-body|";') + '))',
        'S_frozen = $drive(S_result[.COMPLETION = NORMAL], 1)', 'S_frozen.RESULT = KNOWN PNULL',
        'S_frozen.TODO = ptask_tail*', '$call_descriptors_valid(S_frozen)', '$heap_valid($heap_graph(S_frozen))',
        'S_nul = $source_cv_seek(S_frozen, 22, 1, 2000)', '$source_cv_stage(S_nul, 22, 1)',
        'S_nul.TODO = (ERROR_HANDLER_INVOKE perrorcall_nul) :: ptask_nul_tail*',
        'perrorcall_nul.RESUME = SOURCE_NAME_RESULT psourceoperand_nul z_nul',
        'psourceoperand_nul.INPUT = KNOWN (PSTRING ($ptascii("review") ++ [0] ++ $ptascii("nul")))',
        'perrorcall_nul.MESSAGE = $ptascii("Undefined variable $review") ++ [0] ++ $ptascii("nul")',
        '$error_call_valid(S_nul, perrorcall_nul)', '$call_descriptors_valid(S_nul)',
        'S_done = $drive(S_nul[.COMPLETION = NORMAL], 3000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVALCONTEXTS = eps', 'S_done.FILESEQ = 0', 'S_done.FRAMES = eps', 'S_done.TODO = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return setup, {'direct': direct, 'dynamic': dynamic}


def prepare(out, flags):
    source = SOURCES / 'computed-mutation.php'
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'adapter')
    try:
        fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
    finally:
        adapter.close()
    setup, groups = setup_checks(fixture, source)
    for name, checks in groups.items():
        (out / (name + '.watsup')).write_text(setup + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n')
    return groups


def compare(out, flags, startup, name):
    source = SOURCES / (name + '.php')
    directory = out / name
    directory.mkdir()
    native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
    seconds, cap = (30, 45) if name == 'undefined-name' else (60, 90)
    model = recorded([str(R / 'bin/php-semantics'), str(source), '--startup-ini', str(startup),
        '--steps', '100000', '--timeout', str(seconds)], directory / 'model', cap)
    outcome = json.loads((directory / 'model.stdout').read_bytes())
    native_stdout = (directory / 'native.stdout').read_bytes()
    common = (native['exit'] == 0 and not native['timeout'] and not model['timeout']
        and not (directory / 'native.stderr').read_bytes() and not (directory / 'model.stderr').read_bytes()
        and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program')
    if name == 'undefined-name':
        passed = (common and model['exit'] == 1 and
            native_stdout == b'H:Undefined variable $missingName:7|E:missing-name|END' and
            outcome.get('status') == 'unsupported' and outcome.get('exit_status') is None and
            outcome.get('reason') == 'error-handler ingress requires a producer continuation' and
            outcome.get('stdout') == '' and outcome.get('stderr') == '' and outcome.get('events') == [])
    else:
        passed = (common and model['exit'] == 0 and native_stdout.endswith(b'END') and b'wrong-' not in native_stdout
            and outcome.get('status') == 'normal' and outcome.get('exit_status') == 0 and outcome.get('reason') is None
            and base64.b64decode(outcome['stdout']) == native_stdout and outcome.get('stderr') == '')
    return {'id': name, 'passed': passed, 'agreement': int(passed and name != 'undefined-name'),
        'native': native, 'model': model, 'outcome': outcome}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('all', 'sources', 'states', 'control', 'prepare'), default='all')
    args = parser.parse_args()
    out = Path(tempfile.mkdtemp(prefix='source-undefined-review-', dir=R / '.tools'))
    print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', runner, R / 'spec/schema.json',
        R / 'bin/php-semantics', R / '.tools/php/bin/php', R / '.tools/php-file.so',
        R / 'frontend/worker.php', R / 'frontend/target.php', R / '_build/default/adapter/main.exe',
        R / 'tests/semantics/profile.json', R / 'tests/semantics/error_handler_run.py',
        R / 'tests/semantics/recorded_worker.py', R / 'tests/semantics/source_undefined_protocol.py',
        Path(__file__), *sorted(SOURCES.glob('*.php'))]
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = head()
    profile = dict(json.loads((R / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    startup = out / 'startup.json'
    startup.write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
    report = {'revision': revision, 'inputs': before, 'mode': args.mode, 'profile': profile, 'rows': [],
        'passed': False, 'native_target': 'PHP 8.5.10 CLI NTS64, Zend source 34308a6666b2d489c509541ea9befea9e2b42348',
        'compiler': {'source': 'da36ac3c434cd291940293a63da64544307730a3', 'mode': 'SL', 'cache': False, 'det': True},
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    try:
        if args.mode in ('all', 'sources'):
            for name in CASES:
                row = compare(out, flags, startup, name)
                report['rows'].append(row)
                print(name, row['passed'], flush=True)
                assert row['passed']
        if args.mode in ('all', 'states', 'prepare'):
            groups = prepare(out, flags)
            report['state_checks'] = {name: len(checks) for name, checks in groups.items()}
            if args.mode != 'prepare':
                for name, checks in groups.items():
                    process = recorded([str(runner), '--sl', *map(str, modules), str(out / (name + '.watsup'))], out / name, 120)
                    passed = (process['exit'] == 0 and not process['timeout'] and
                        (out / (name + '.stdout')).read_bytes() == b'true\n' and not (out / (name + '.stderr')).read_bytes())
                    report['rows'].append({'id': name, 'checks': len(checks), 'process': process, 'passed': passed})
                    print(name, passed, flush=True)
                    assert passed
        if args.mode in ('all', 'control'):
            row = compare(out, flags, startup, 'undefined-name')
            report['rows'].append(row)
            print('undefined-name', row['passed'], 'Unsupported control; zero agreement', flush=True)
            assert row['passed']
        report['passed'] = True
    finally:
        report['inputs_stable'] = before == {str(path.relative_to(R)): digest(path) for path in watched}
        report['head_stable'] = revision == head()
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed'] and report['inputs_stable'] and report['head_stable']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
