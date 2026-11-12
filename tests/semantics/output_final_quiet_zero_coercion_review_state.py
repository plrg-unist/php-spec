#!/usr/bin/env python3
"""Quiet zero-error captures validate both original string identities."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_quiet_zero_coercion_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
CASES = {'division': sources.DIVISION, 'modulo': sources.MODULO, 'noisy': sources.NOISY}
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')


def authority(name, fixture, path):
    operator = 'DIVIDE' if name == 'division' else 'MODULO'
    message = 'Division by zero' if name == 'division' else 'Modulo by zero'
    other = 'MODULO' if name == 'division' else 'DIVIDE'
    bindings = division.start(fixture, path) + [
        f'S.TODO = (BINARY_RIGHT {operator} poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_left = $resolve_at(S_inputs, poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        f'pobreturnerror = {{SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("{message}"), LINE z}}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pvalue_bad_left = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.0"))',
        'pvalue_bad_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
        f'S_bad_left = S[.TODO = (BINARY_RIGHT {operator} (KNOWN pvalue_bad_left) z) :: ptask_tail*]',
        'S_bad_right = S[.RESULT = KNOWN pvalue_bad_right]',
        'S_bad_left_generated = $throwable_transition(S_bad_left, $dz_raw(S_bad_left))',
        'S_bad_right_generated = $throwable_transition(S_bad_right, $dz_raw(S_bad_right))',
        'S_good_right = S_bad_right[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]]',
        'S_good_right_generated = $throwable_transition(S_good_right, $dz_raw(S_good_right))',
        f'S_plain_left = S[.TODO = (BINARY_RIGHT {operator} (KNOWN (PSTRING ($ptascii("1")))) z) :: ptask_tail*]',
        'S_plain_right = S[.RESULT = KNOWN (PSTRING ($ptascii("0")))]',
        'S_null_right = S[.RESULT = KNOWN PNULL]',
        'S_false_right = S[.RESULT = KNOWN (PBOOL false)]',
        f'S_other = S[.TODO = (BINARY_RIGHT {other} poperand_left z) :: ptask_tail*]',
        'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))']
    raw_result = ('S.RESULT = KNOWN pvalue_right /\\ S_request.RESULT = KNOWN pvalue_right'
                  if name == 'division' else
                  'pvalue_right = PNULL /\\ S_request.RESULT = KNOWN (PINT 0) /\\ S_request.RESULT =/= S_right.RESULT')
    checks = [
        ('real ordered reads preserve original operands and opcode-specific scratch',
         r'S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         + raw_result + r' /\ S_request.TODO = ptask_tail* /\ S_request.HELD = S.HELD /\ S_request.EVENTS = S.EVENTS /\ '
         + f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("{message}")) z'),
        ('genuine capture retains source authority and native owners',
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ $ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_generated, pobreturnerror) /\ pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror) /\ S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_DIVISION_ERROR pobreturnerror))) /\ $ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ '
         + prior.public('S_capture')),
        ('unfiltered KNOWN left still needs a validated string identity',
         f'$ob_object_division_operands({operator}, pvalue_bad_left, pvalue_right) /\\ '
         + r'$ob_object_error_operand_value(S_bad_left, KNOWN pvalue_bad_left, [PCFIELD 0], z) = (pvalue_bad_left) /\ ~$string_carrier_valid(S_bad_left, pvalue_bad_left) /\ $call_current_valid(S_bad_left) /\ S_bad_left_generated.COMPLETION = THROWING n_exception /\ $ob_object_return_error_live(S_bad_left_generated, pobreturnerror) /\ $ob_object_division_error_capture(S_bad_left, S_bad_left_generated) = eps'),
        ('unfiltered KNOWN right still needs a validated string identity',
         f'$ob_object_division_operands({operator}, pvalue_left, pvalue_bad_right) /\\ '
         + r'$ob_object_error_operand_value(S_bad_right, KNOWN pvalue_bad_right, [PCFIELD 1], z) = (pvalue_bad_right) /\ ~$string_carrier_valid(S_bad_right, pvalue_bad_right) /\ $call_current_valid(S_bad_right) /\ S_bad_right_generated.COMPLETION = THROWING n_exception /\ $ob_object_return_error_live(S_bad_right_generated, pobreturnerror) /\ $ob_object_division_error_capture(S_bad_right, S_bad_right_generated) = eps'),
        ('a real rootless request string grants exactly the existing capture',
         r'$string_carrier_valid(S_good_right, pvalue_bad_right) /\ $value_nodes(pvalue_bad_right) = eps /\ S_good_right_generated.COMPLETION = THROWING n_exception /\ $ob_object_division_error_capture(S_good_right, S_good_right_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('promoted plain-string NULL and false guards use real equal successors',
         r'$throwable_transition(S_plain_left, $dz_raw(S_plain_left)) = S_generated /\ $throwable_transition(S_plain_right, $dz_raw(S_plain_right)) = S_generated /\ $throwable_transition(S_null_right, $dz_raw(S_null_right)) = S_generated /\ $throwable_transition(S_false_right, $dz_raw(S_false_right)) = S_generated /\ $ob_object_division_error_capture(S_plain_left, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ $ob_object_division_error_capture(S_plain_right, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ $ob_object_division_error_capture(S_null_right, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ $ob_object_division_error_capture(S_false_right, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('a coherent wrong opcode and a changed materialization both refuse',
         r'S_other_generated.COMPLETION = THROWING n_exception /\ $call_current_valid(S_other) /\ $ob_object_division_error_capture(S_other, S_other_generated) = eps /\ $ob_object_division_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ $ob_object_division_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]
    if name == 'modulo':
        checks.append(('string-long saturation stays distinct from float-long and noisy strings',
            r'$ob_object_division_number(PSTRING ($ptascii("1.5"))) /\ $ob_object_modulo_integer(PSTRING ($ptascii("1.5"))) = eps /\ ~$ob_object_division_number(PSTRING ($ptascii("1x"))) /\ $ob_object_modulo_integer(PSTRING ($ptascii("1x"))) = eps /\ $string_long($ptascii("9223372036854775808")) = STRINT 9223372036854775807 eps /\ $ob_object_modulo_integer(PSTRING ($ptascii("9223372036854775808"))) = (9223372036854775807) /\ $ob_object_modulo_integer(PFLOAT 4890909195324358656) = eps'))
    return bindings, checks


def noisy(fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'S_observed = $source_exception_transition(S, S_generated)']
    checks = [
        ('fully numeric fractional string is quiet DIV and noisy MOD',
         r'$string_bytes(pvalue_left) = ($ptascii("1.5")) /\ $string_carrier_valid(S, pvalue_left) /\ pvalue_right = PNULL /\ $coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) false /\ $ob_object_division_number(pvalue_left) /\ $string_long($ptascii("1.5")) = STRINT 1 (STRINGPRECISIONLOSS :: eps) /\ $ob_object_modulo_integer(pvalue_left) = eps /\ ~$ob_object_division_operands(MODULO, pvalue_left, pvalue_right)'),
        ('real54 preserves its diagnostic before the zero-error request',
         r'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) z /\ S_request.RESULT = KNOWN (PINT 0) /\ S_request.EVENTS =/= S.EVENTS /\ S_generated.COMPLETION = THROWING n_exception'),
        ('noisy zero error earns no FINAL capture',
         r'$ob_object_division_error_capture(S, S_generated) = eps /\ S_observed = S_generated')]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-quiet-zero-coercion-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    head = lambda: subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300, 'records': [], 'passed': False}
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [ROOT / rel for rel in modules + ['spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_quiet_zero_coercion_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py',
        'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py']] + [Path(__file__)]
    fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
    jobs = []
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(CASES[name]).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            cache = directory / 'checked.json'; cache.write_text(json.dumps(checked) + '\n')
            bindings, checks = noisy(checked['fixture'], path) if name == 'noisy' else authority(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched += [path, fixture, cache]
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'source_sha256': hashlib.sha256(CASES[name]).hexdigest(), 'passed': False}
            report['records'].append(record)
            jobs.append((record, directory, fixture, checks))
        report['before'] = fingerprint()
        for record, directory, fixture, checks in jobs:
            if args.prepare_only:
                record['prepared'] = True
                continue
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
                record['tool_exit'] = result.returncode
                assert result.returncode == 0 and not result.stderr, 'fixture runner failed; see state.stderr'
                record['observed'] = json.loads(result.stdout)
                assert record['observed'] == [True] * len(checks), record['observed']
                record['passed'] = True
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record['seconds'] = time.monotonic() - started
        report['after'] = fingerprint()
        report['after_revision'] = head()
        assert report['before'] == report['after'], 'watched inputs changed'
        assert report['revision'] == report['after_revision'], 'revision changed'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        report['after'] = fingerprint()
        report['after_revision'] = head()
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
