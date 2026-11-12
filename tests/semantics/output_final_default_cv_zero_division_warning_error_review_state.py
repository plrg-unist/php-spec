#!/usr/bin/env python3
"""Own RHS CV capture preserves current values, source identity and private cells."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_null_division_warning_error_review_state as previous
import output_final_default_cv_zero_division_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = division.prior
PREFIX = previous.PREFIX
CASES = {name: sources.CASES['native-default-cv-zero-warning-division-' + name]
         for name in ['integer', 'numeric-string']}
CASES['reference'] = CASES['integer'].replace(b'$c = 0;', b'$c =& $b;')
CASES['nonzero'] = CASES['integer'].replace(b'$b = 0;', b'$b = 1;').replace(b'$c = 0;', b'$c = 1;')
CASES['noisy'] = CASES['integer'].replace(b'$b = 0;', b"$b = '0x';").replace(b'$c = 0;', b"$c = '0x';")
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
AUTHORITY = (r'z = 9 /\ z_left = 9 /\ z_right = 9 /\ '
             r'n_left* = $ptascii("a") /\ n_right* = $ptascii("b") /\ '
             r'$compiled_read(S, porigin_right) = eps /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
             r'$coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ '
             r'~$error_handler_eligible(S, 2)')
ZERO = (r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ '
        r'S_raw.RESULT = KNOWN pvalue_right /\ '
        r'S_raw.EVENTS = $leading_warning(S, true, z).EVENTS /\ '
        r'$ob_object_return_error_live(S_generated, pobreturnerror)')


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE poperand_left z) :: ptask_tail*',
        'poperand_left = VARIABLE n_left* z_left', 'S.RESULT = VARIABLE n_right* z_right',
        'S.ORIGIN = (porigin_operator)', '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$lookup(S.ENV, n_left*) = (n_cell_left)', '$lookup(S.ENV, n_right*) = (n_cell_right)',
        '$lookup(S.ENV, $ptascii("c")) = (n_cell_other)',
        'S.STORE[n_cell_left] = DEFINED pvalue_left', 'S.STORE[n_cell_right] = DEFINED pvalue_right',
        'S.STORE[n_cell_other] = DEFINED pvalue_right',
        '$coerce_number(pvalue_right) = COERCED pnumber_right b_right',
        'S_left = $resolve_at($hold_task_inputs(S), poperand_left, z)',
        'S_right = $resolve_at(S_left, S.RESULT, z)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)']
    if name == 'nonzero':
        return bindings, [
            ('a genuine private nonzero CV passes source/read/quiet admission but cannot mint a zero Error',
             AUTHORITY + r' /\ pvalue_right = PINT 1 /\ ~b_right /\ '
             r'$ob_object_division_number(pvalue_right) /\ ~$num_zero(pnumber_right) /\ '
             r'S_raw.COMPLETION = NORMAL /\ S_raw.RESULT = KNOWN (PFLOAT 4609434218613702656) /\ '
             r'S_raw.EVENTS = $leading_warning(S, true, z).EVENTS /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += ['S_generated.COMPLETION = THROWING n_exception',
                 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}']
    if name == 'noisy':
        return bindings, [
            ('a genuine leading-numeric right CV retains two Warnings through default capture',
             AUTHORITY + r' /\ b_right /\ $num_zero(pnumber_right) /\ '
             r'$string_bytes(pvalue_right) = ($ptascii("0x")) /\ '
             r'$ob_object_string_value(S, pvalue_right) /\ ~$ob_object_division_number(pvalue_right) /\ '
             r'S_raw.RESULT = KNOWN pvalue_right /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ '
             r'S_raw.EVENTS = $leading_warning($leading_warning(S, true, z), true, z).EVENTS /\ '
             r'S_raw.EVENTS =/= $leading_warning(S, true, z).EVENTS /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')]
    if name == 'reference':
        return bindings, [
            ('a genuine source alias has quiet zero value and CV rank but fails private nonreference admission',
             r'z = 9 /\ n_cell_right = n_cell_other /\ n_cell_right <- S.REFCELLS /\ '
             r'pvalue_right = PINT 0 /\ ~$error_handler_eligible(S, 2) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S)) = 2 /\ '
             r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = eps /\ '
             + ZERO + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]
    if name == 'integer':
        bindings += [
            'S_other = S[.RESULT = VARIABLE ($ptascii("c")) z_right]',
            'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
            'S_copy = S[.RESULT = KNOWN pvalue_right]',
            'S_copy_generated = $throwable_transition(S_copy, $dz_raw(S_copy))',
            'S_line = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
            'S_line_generated = $throwable_transition(S_line, $dz_raw(S_line))']
        return bindings, [
            ('the original quiet right CV borrows its own value while all three distinct cells keep one owner',
             AUTHORITY + r' /\ pvalue_right = PINT 0 /\ ~b_right /\ '
             r'n_cell_left =/= n_cell_right /\ n_cell_left =/= n_cell_other /\ n_cell_right =/= n_cell_other /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S_generated)) = 1 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S_generated)) = 1 /\ '
             r'$heap_count(HCELL n_cell_other, $machine_roots(S_generated)) = 1 /\ ' + ZERO + r' /\ ' + CAPTURE),
            ('a genuine same-valued other CV and a KNOWN copy cannot replace the original source operand',
             r'S_other_generated = S_generated /\ S_copy_generated = S_generated /\ '
             r'$integer_slot_rank(S_other, porigin_operator, [PCFIELD 1], S_other.RESULT) = (8) /\ '
             r'~$integer_operand_source(S_other, porigin_operator, [PCFIELD 1], S_other.RESULT) /\ '
             r'$ob_object_error_operand_value(S_other, S_other.RESULT, [PCFIELD 1], z) = eps /\ '
             r'$ob_object_division_error_capture(S_other, S_other_generated) = eps /\ '
             r'~$integer_operand_source(S_copy, porigin_operator, [PCFIELD 1], S_copy.RESULT) /\ '
             r'$ob_object_division_error_capture(S_copy, S_copy_generated) = eps'),
            ('the exact compiled right-read line remains necessary despite the same materialized Error',
             r'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (z_right) /\ '
             r'S_line_generated = S_generated /\ '
             r'~$integer_operand_source(S_line, porigin_operator, [PCFIELD 1], S_line.RESULT) /\ '
             r'$ob_object_error_operand_value(S_line, S_line.RESULT, [PCFIELD 1], z) = eps /\ '
             r'$ob_object_division_error_capture(S_line, S_line_generated) = eps')]

    bindings += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
        'S_bad = S[.STORE[n_cell_right] = DEFINED pvalue_request]',
        'S_valid = S_bad[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]]',
        'S_valid_raw = $dz_raw(S_valid)',
        'S_valid_generated = $throwable_transition(S_valid, S_valid_raw)']
    return bindings, [
        ('the original string CV keeps its live carrier through quiet reads and raw division scratch',
         AUTHORITY + r' /\ pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0")) /\ '
         r'$ob_object_string_value(S, pvalue_right) /\ ~b_right /\ $num_zero(pnumber_right) /\ '
         r'S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ '
         r'S_right.RESULT = KNOWN pvalue_right /\ ' + ZERO + r' /\ ' + CAPTURE),
        ('an invalid current carrier refuses while the same valid current request value remains an own-CV read',
         r'$string_plain(pvalue_request) = $string_plain(pvalue_right) /\ '
         r'~$ob_object_string_value(S_bad, pvalue_request) /\ '
         r'$ob_object_error_operand_value(S_bad, S_bad.RESULT, [PCFIELD 1], z) = eps /\ '
         r'$ob_object_division_error_capture(S_bad, S_generated) = eps /\ '
         r'$ob_object_string_value(S_valid, pvalue_request) /\ '
         r'$ob_object_error_operand_value(S_valid, S_valid.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
         r'$integer_operand_source(S_valid, porigin_operator, [PCFIELD 1], S_valid.RESULT) /\ '
         r'S_valid_raw.RESULT = KNOWN pvalue_request /\ S_valid_raw.EVENTS = S_raw.EVENTS /\ '
         r'$heap_count(HCELL n_cell_right, $machine_roots(S_valid_generated)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_valid_generated)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_valid_generated)) = 1 /\ '
         r'$ob_object_division_error_capture(S_valid, S_valid_generated) = ((pobobjectreturn, pobreturnerror))')]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output; out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / name for name in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_default_cv_zero_division_warning_error_sources.py',
        'tests/semantics/output_final_default_null_division_warning_error_sources.py',
        'tests/semantics/output_final_default_division_warning_error_sources.py',
        'tests/semantics/output_final_default_null_division_warning_error_review_state.py',
        'tests/semantics/output_final_division_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py']] + [Path(__file__)]
    fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False, 'before': fingerprint()}
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
            bindings, checks = authority(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            inputs = lambda: {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': inputs(), 'passed': False}
            report['records'].append(record)
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
                record.update(seconds=time.monotonic() - started, inputs_after=inputs())
            assert record['inputs_before'] == record['inputs_after'], 'fixture inputs changed'
            record['passed'] = True
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(name, len(checks), record['seconds'], flush=True)
        report['after'] = fingerprint()
        assert report['before'] == report['after'], 'watched inputs changed'
        assert report['revision'] == head(), 'revision changed'
        report['passed'] = all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if 'after' not in report:
            report['after'] = fingerprint()
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
