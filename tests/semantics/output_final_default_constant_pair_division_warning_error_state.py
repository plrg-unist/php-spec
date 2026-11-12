#!/usr/bin/env python3
"""Original CONST pairs survive empty-CV FINAL error retirement."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_default_constant_pair_division_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT DIVIDE poperand_left z')
CASES = {'leading-string': sources.CASES['native-default-constant-pair-warning-division-leading-string']}


def lifecycle(name, fixture, path):
    message = b'Division by zero'
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
        '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
        'S_left = $resolve_at($hold_task_inputs(S), KNOWN pvalue_left, z)',
        'S_right = $resolve_at(S_left, S.RESULT, z)',
        'S_warned = $leading_warning($leading_warning(S, true, z), true, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror)',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE ' + prior.value(message) + ', LINE z}',
        *prior.seek('S_leave', 'S_capture', 8),
        'S_stage_found = $drive_steps(S_leave, 1)', 'S_stage_found.COMPLETION = BUDGET',
        'S_stage = S_stage_found[.COMPLETION = NORMAL]',
        'S_stage.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_exit_found = $drive_steps(S_stage, 1)', 'S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        *prior.seek('S_retired', 'S_report', 2),
        'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'pobobjectreturn_site = pobobjectreturn_capture[.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror_site)]',
        'pdestructioncleanup_site = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_site pobdeactivate pobreturnerror.SITE n_exception]',
        'S_receipt_site = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_site]]',
        'S_zero = $drive_steps(S_capture, 0)', 'S_leave_zero = $drive_steps(S_leave, 0)',
        'S_stage_zero = $drive_steps(S_stage, 0)', 'S_exit_zero = $drive_steps(S_exit, 0)',
        'S_retired_zero = $drive_steps(S_retired, 0)']
    original = (r'z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
                r'pvalue_left_compiled = PSTRING ($ptascii("1.5x")) /\ '
                r'pvalue_right_compiled = PSTRING ($ptascii("0x")) /\ '
                r'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled) /\ '
                r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
                r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
                r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")) /\ '
                r'$ob_object_string_value(S, pvalue_left) /\ $ob_object_string_value(S, pvalue_right) /\ '
                r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
                r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
                r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
                r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
                r'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (6) /\ '
                r'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (6)')
    fatal = (b'Fatal error: Uncaught DivisionByZeroError: ' + message + b' in ' + bytes(path) + b':6\nStack trace:\n'
             b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) + b' on line 6\n')
    checks = [
        ('both original CONST operands warn through raw35 and exact152 before actual capture',
         original + r' /\ $ob_object_error_operand_value(S, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ $ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ S_left.RESULT = KNOWN pvalue_left /\ S_right.RESULT = KNOWN pvalue_right /\ S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ $coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ $coerce_number(pvalue_right) = COERCED (NINT 0) true /\ $value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ ~$error_handler_eligible(S, 2) /\ $arithmetic_copy_swap(S, porigin_operator, DIVIDE, KNOWN pvalue_left, S.RESULT) = (false) /\ S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6, DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6] /\ S_request.RESULT = KNOWN pvalue_right /\ S_request.COMPLETION = THROWN "DivisionByZeroError" ' + prior.value(message) + r' 6 /\ S_request.EVENTS = S_warned.EVENTS /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('captured four-field source adds no owner and survives a public zero budget',
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $output_final_cv_unwind(S_capture) /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture')),
        ('actual bare VM exit processes its empty release before native C0 readiness',
         r'S_leave.TODO = [THROW_SEARCH n_exception] /\ S_leave_zero = S_leave[.COMPLETION = BUDGET] /\ S_stage.CURRENT = eps /\ S_stage.FRAMES = eps /\ S_stage.ORIGIN = eps /\ pdestructionrelease.JOBS = eps /\ S_stage.DESTRUCTION.RELEASES = [pdestructionrelease] /\ ~$ob_object_final_cv_ready(S_stage, pobobjectreturn_capture, pdestructionframe, n_exception) /\ S_stage_zero = S_stage[.COMPLETION = BUDGET] /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ S_exit.DESTRUCTION.RELEASES = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.VALUE = KNOWN PNULL /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ pdestructionframe.CALLER = eps /\ pdestructionframe.ORIGIN = eps /\ $ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ S_exit.EVENTS = S_warned.EVENTS /\ S_exit_zero = S_exit[.COMPLETION = BUDGET] /\ ' + prior.public('S_exit')),
        ('C0 preserves both Warnings before fatal DivisionByZeroError and native receiver release',
         'S_report.EVENTS = S_warned.EVENTS ++ [STDERR ' + prior.value(fatal) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("DivisionByZeroError")) ' + prior.value(message) + r' 6 /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1 /\ ' + prior.public('S_report')),
        ('retired Error leaves an authenticated static source and native receipt without operand ownership',
         r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $ob_object_division_error_source(S_retired, pfunction, pobreturnerror) /\ $ob_object_source_generated_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ $ob_object_source_kind(pobobjectreturn_capture.SOURCE) = "DivisionByZeroError" /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ ~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ S_retired.EVENTS = S_report.EVENTS /\ S_retired_zero = S_retired[.COMPLETION = BUDGET] /\ ' + prior.public('S_retired'))]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir()
            source = CASES[name]
            path = directory / 'source.php'; path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = lifecycle(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
                'tests/semantics/output_final_default_constant_pair_division_warning_error_sources.py',
                'tests/semantics/output_final_default_constant_left_division_warning_error_sources.py',
                'tests/semantics/output_final_default_division_operand_warning_error_sources.py',
                'tests/semantics/output_final_default_cv_zero_division_warning_error_sources.py',
                'tests/semantics/output_final_default_null_division_warning_error_sources.py',
                'tests/semantics/output_final_default_division_warning_error_sources.py',
                'tests/semantics/output_final_division_error_sources.py',
                'tests/semantics/output_final_division_error_review_state.py',
                'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
                'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
                'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
            watched += [Path(__file__), path, fixture, directory / 'checked.json']
            fp = lambda: {str(p): prior.common.sha(p) for p in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'before': fp(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
                record['observed'] = json.loads(result.stdout)
                assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record.update(seconds=time.monotonic() - started, after=fp())
            assert record['before'] == record['after']
            record['passed'] = True
        report['after_revision'] = head()
        assert report['revision'] == report['after_revision'], 'revision changed'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
