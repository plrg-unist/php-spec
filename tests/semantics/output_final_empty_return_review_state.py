#!/usr/bin/env python3
"""Empty native method frames retain real return-error owners until C0 reporting."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_return_type_review_state as prior
import output_final_empty_return_sources as sources

ROOT = Path(__file__).resolve().parents[2]
CASES = {'core': sources.STRICT, 'weak': sources.CASES['empty-weak-return-coercion'],
         'catch': sources.CATCH, 'override': sources.OVERRIDE}
PREFIX = prior.OVERRIDE_PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 8) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
def $dp_phase(S, n) = false -- otherwise''')


def core(fixture, path):
    bindings = prior.start(fixture, path) + prior.capture() + [
        'S.OBJECTS[n_object] = INSTANCE porigin_class',
        'pobobjectreturn_legacy = pobobjectreturn_capture[.SOURCE = (OBJECT_LEGACY_THROW pobreturnerror.SITE n_exception)]',
        'S_legacy = S_capture[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_legacy) :: ptask_native*]]]',
        *prior.seek('S_leave', 'S_capture', 8),
        'S_zero = $drive_steps(S_leave, 0)',
        'S_stage_found = $drive_steps(S_leave, 1)', 'S_stage_found.COMPLETION = BUDGET',
        'S_stage = S_stage_found[.COMPLETION = NORMAL]',
        'S_stage.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_stage_zero = $drive_steps(S_stage, 0)',
        'S_exit_found = $drive_steps(S_stage, 1)', 'S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_exit_zero = $drive_steps(S_exit, 0)',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        *prior.seek('S_retired', 'S_report', 2),
        'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]']
    fatal = (b'Fatal error: Uncaught TypeError: ' + prior.MESSAGE + b' in ' + os.fsencode(path) + b':6\nStack trace:\n'
             b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + os.fsencode(path) + b' on line 6\n')
    checks = [
        ('empty method keeps genuine producer and old ctor gate distinct', r'S.CVS = eps /\ S.ENV = eps /\ S.SYMBOLS = eps /\ pfunction.CVS = eps /\ $effective_method(S, porigin_class, $ptascii("__destruct"), |S.CLASSES|) = eps /\ $ob_object_final_native_method(S) = (pobobjectreturn) /\ $ob_object_final_cv_method(S) = eps /\ $ob_object_final_source_method(S) = eps /\ $ob_object_return_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ $ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ pobreturnerror.LINE = 6'),
        ('only real return-error tag admits empty lifetime context', r'$ob_object_final_source_method(S_capture) = (pobobjectreturn_capture) /\ $ob_object_final_cv_method(S_capture) = eps /\ $ob_object_final_source_method(S_legacy) = eps /\ $ob_object_final_cv_method(S_legacy) = eps /\ $heap_graph(S_legacy) = $heap_graph(S_capture) /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
        ('bare no-CV VM exit and zero budget preserve both C owners', r'S_leave.TODO = [THROW_SEARCH n_exception] /\ S_leave.CVS = eps /\ S_leave.ENV = eps /\ S_leave.CURRENT = (pcallcontext) /\ $heap_count(HOBJECT n_object, $machine_roots(S_leave)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_leave)) = 1 /\ S_zero = S_leave[.COMPLETION = BUDGET]'),
        ('real empty-release administration precedes original null-C report', r'S_stage.CURRENT = eps /\ S_stage.FRAMES = eps /\ S_stage.ORIGIN = eps /\ pdestructionrelease.JOBS = eps /\ S_stage.DESTRUCTION.RELEASES = [pdestructionrelease] /\ S_stage_zero = S_stage[.COMPLETION = BUDGET] /\ ~$ob_object_final_cv_ready(S_stage, pobobjectreturn_capture, pdestructionframe, n_exception) /\ S_stage.EVENTS = [OUTPUT ([80])] /\ $heap_count(HOBJECT n_object, $machine_roots(S_stage)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_stage)) = 1 /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ S_exit.DESTRUCTION.RELEASES = eps /\ S_exit.DESTRUCTION.CALLS = eps /\ S_exit.DESTRUCTION.OPERATIONS = eps /\ S_exit.DESTRUCTION.CLEANUPS = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.VALUE = KNOWN PNULL /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ pdestructionframe.CALLER = eps /\ pdestructionframe.ORIGIN = eps /\ $ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ S_exit.EVENTS = [OUTPUT ([80])] /\ S_exit_zero = S_exit[.COMPLETION = BUDGET] /\ ' + prior.public('S_exit')),
        ('actual C0 reports original generated error before cast release', 'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + prior.value(fatal) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("TypeError")) ' + prior.value(prior.MESSAGE) + r' 6 /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1'),
        ('retired empty-method error leaves authenticated native receipt', r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ S_retired.EVENTS = S_report.EVENTS /\ ' + prior.public('S_retired')),
    ]
    return bindings, checks


def control(name, fixture, path):
    if name == 'weak':
        bindings, checks = prior.weak(fixture, path)
        checks[0] = (checks[0][0], checks[0][1] + r' /\ S.CVS = eps /\ S.ENV = eps /\ pfunction.CVS = eps')
        return bindings, checks
    bindings, checks = prior.clearing(name, fixture, path)
    checks[0] = (checks[0][0], checks[0][1] + r' /\ S.CVS = eps /\ S.ENV = eps /\ pfunction.CVS = eps')
    if name == 'catch':
        checks[0] = (checks[0][0], checks[0][1] + r' /\ S_caught.CVS = eps /\ S_caught.ENV = eps')
    checks[1] = (checks[1][0], checks[1][1] + r' /\ S_H.CVS = eps /\ S_H.ENV = eps')
    return bindings, checks


def fingerprint(fixture):
    values = prior.fingerprint(fixture)
    for name in ('tests/semantics/output_final_empty_return_sources.py', 'tests/semantics/output_final_empty_return_review_state.py'):
        values[name] = prior.common.sha(ROOT / name)
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checked-root', type=Path)
    parser.add_argument('--native-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-empty-return-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': prior.common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir(); source = CASES[name]
            if args.native_root and name in ('core', 'weak'):
                path = args.native_root / ('native-01' if name == 'core' else 'native-02') / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name != 'core':
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'; assert path.read_bytes() == source
            else:
                path = directory / 'source.php'; path.write_bytes(source)
            if args.checked_root:
                cache = args.checked_root / ('baseline-01/checked.json' if name == 'core' else f'control-preparation-01/{name}/checked.json')
                checked = json.loads(cache.read_text())
            else:
                frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': prior.common.base64.b64encode(source).decode()})
                finally:
                    frontend.close()
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = core(checked['fixture'], path) if name == 'core' else control(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + b + '\n' for b in bindings))
            record = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(), 'fixture_sha256': prior.common.sha(fixture), 'groups': [label for label, _ in checks], 'before': fingerprint(fixture), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text()); started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            finally:
                record['seconds'] = round(time.monotonic() - started, 3); record['after'] = fingerprint(fixture)
            record['observed'] = [value == b'true' for value in re.findall(rb'true|false', result.stdout)]
            assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            assert record['before'] == record['after'], 'watched inputs changed'
            record['passed'] = True
        assert report['records'], 'no fixture selected'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
        report['prepared'] = args.prepare_only
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}; raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n'); print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
