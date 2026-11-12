#!/usr/bin/env python3
"""A quiet numeric string divisor retains original source and nonowning FINAL error retirement."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_default_scalar_zero_division_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
CASES = {'string-float-negative': sources.CASES['native-default-scalar-zero-warning-division-string-float-negative']}


def lifecycle(name, fixture, path):
    operator = 'DIVIDE'
    message = b'Division by zero'
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT ' + operator + ' (VARIABLE n_left* z_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$coerce_number(pvalue_right) = COERCED pnumber_right false',
        '$lookup(S.ENV, n_left*) = (n_cell_left)', 'S.STORE[n_cell_left] = DEFINED pvalue_left',
        'S_left = $resolve_at($hold_task_inputs(S), VARIABLE n_left* z_left, z)',
        'S_right = $resolve_at(S_left, S.RESULT, z)',
        'S_warned = $leading_warning(S, true, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror)',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE ' + prior.value(message) + ', LINE z}',
        *prior.seek('S_exit', 'S_capture', 1),
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
        'S_zero = $drive_steps(S_retired, 0)']
    original = r'$string_bytes(pvalue_left) = ($ptascii("1.5x")) /\ $ob_object_string_value(S, pvalue_left)'
    fatal = (b'Fatal error: Uncaught DivisionByZeroError: ' + message + b' in ' + bytes(path) + b':7\nStack trace:\n'
             b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) + b' on line 7\n')
    checks = [
        ('genuine default Warning precedes DivisionByZeroError and retains original compiled numeric-string scratch',
         original + r' /\ $ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left) /\ S_left.RESULT = KNOWN pvalue_left /\ S_right.RESULT = KNOWN pvalue_right /\ $string_bytes(pvalue_right) = ($ptascii("-0.0")) /\ $compiled_read(S, porigin_right) = (PSTRING ($ptascii("-0.0"))) /\ $integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ $integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ $ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ $num_zero(pnumber_right) /\ $value_nodes(pvalue_right) = eps /\ $ob_object_string_value(S, pvalue_right) /\ $ob_object_division_number(pvalue_right) /\ S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ $coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ ~$ob_object_division_number(pvalue_left) /\ ~$error_handler_eligible(S, 2) /\ $arithmetic_copy_swap(S, porigin_operator, ' + operator + r', VARIABLE n_left* z_left, S.RESULT) = (false) /\ S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 7] /\ S_request.RESULT = KNOWN pvalue_right /\ S_request.COMPLETION = THROWN "DivisionByZeroError" ' + prior.value(message) + r' 7 /\ S_request.EVENTS = S_warned.EVENTS /\ z = 7 /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('real private CV retirement precedes native C0 reporting',
         r'~((HCELL n_cell_left) <- S_exit.ALLOCATIONS) /\ $heap_count(HCELL n_cell_left, $machine_roots(S_exit)) = 0 /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.DESTRUCTION.RELEASES = eps /\ $ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ ' + prior.public('S_exit')),
        ('C0 preserves the default Warning before fatal DivisionByZeroError and native receiver release',
         'S_report.EVENTS = S_warned.EVENTS ++ [STDERR ' + prior.value(fatal) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("DivisionByZeroError")) ' + prior.value(message) + r' 7 /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1 /\ ' + prior.public('S_report')),
        ('retired receipt retains source without operand or Error ownership',
         r'~((HCELL n_cell_left) <- S_retired.ALLOCATIONS) /\ $heap_count(HCELL n_cell_left, $machine_roots(S_retired)) = 0 /\ ~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $ob_object_division_error_source(S_retired, pfunction, pobreturnerror) /\ $ob_object_source_generated_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ $ob_object_source_kind(pobobjectreturn_capture.SOURCE) = "DivisionByZeroError" /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ ~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ $ob_object_error_operand_value(S_retired, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ S_retired.EVENTS = S_report.EVENTS /\ S_zero = S_retired[.COMPLETION = BUDGET] /\ ' + prior.public('S_retired'))]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'mode': 'SL_mode/cache=false/det=true', 'native_agreement_credit': 0, 'records': [], 'passed': False}
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
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
                'tests/semantics/output_final_default_scalar_zero_division_warning_error_sources.py', 'tests/semantics/output_final_division_error_review_state.py',
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
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
