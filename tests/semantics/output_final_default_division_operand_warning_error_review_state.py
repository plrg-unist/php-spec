#!/usr/bin/env python3
"""Ordered DIV Warnings retain compiled or current operand authority."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_null_division_warning_error_review_state as previous
import output_final_default_division_operand_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = division.prior
PREFIX = previous.PREFIX
CASES = {
    'constant': sources.CASES['native-default-division-operand-warning-both-constant'],
    'current': sources.CASES['native-default-division-operand-warning-right-cv'],
}
CASES['nonzero'] = CASES['current'].replace(b"$b = '0x';", b"$b = '1x';").replace(
    b"$c = '0x';", b"$c = '1x';")
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
AUTHORITY = (r'$ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
             r'S_left.RESULT = KNOWN pvalue_left /\ S_right.RESULT = KNOWN pvalue_right /\ '
             r'S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ '
             r'~$error_handler_eligible(S, 2) /\ b_right')
ZERO = (r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ '
        r'S_raw.RESULT = KNOWN pvalue_right /\ '
        r'S_raw.EVENTS = $leading_warning($leading_warning(S, b_left, z), b_right, z).EVENTS /\ '
        r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ '
        r'$ob_object_return_error_live(S_generated, pobreturnerror)')


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE (VARIABLE n_left* z_left) z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$lookup(S.ENV, n_left*) = (n_cell_left)', 'S.STORE[n_cell_left] = DEFINED pvalue_left']
    if name == 'constant':
        bindings += ['S.RESULT = KNOWN pvalue_right']
    else:
        bindings += ['S.RESULT = VARIABLE n_right* z_right',
                     '$lookup(S.ENV, n_right*) = (n_cell_right)',
                     '$lookup(S.ENV, $ptascii("c")) = (n_cell_other)',
                     'S.STORE[n_cell_right] = DEFINED pvalue_right',
                     'S.STORE[n_cell_other] = DEFINED pvalue_right']
    bindings += [
        '$coerce_number(pvalue_left) = COERCED pnumber_left b_left',
        '$coerce_number(pvalue_right) = COERCED pnumber_right b_right',
        'S_left = $resolve_at($hold_task_inputs(S), VARIABLE n_left* z_left, z)',
        'S_right = $resolve_at(S_left, S.RESULT, z)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)']
    if name == 'nonzero':
        return bindings, [
            ('an authentic noisy nonzero CV warns but cannot mint a zero Error',
             AUTHORITY + r' /\ z = 9 /\ ~b_left /\ '
             r'$string_bytes(pvalue_left) = ($ptascii("1.5")) /\ '
             r'$string_bytes(pvalue_right) = ($ptascii("1x")) /\ '
             r'$ob_object_string_value(S, pvalue_left) /\ $ob_object_string_value(S, pvalue_right) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'~$num_zero(pnumber_right) /\ S_raw.COMPLETION = NORMAL /\ '
             r'S_raw.RESULT = KNOWN (PFLOAT 4609434218613702656) /\ '
             r'S_raw.EVENTS = $leading_warning(S, true, z).EVENTS /\ '
             r'S_generated = S_raw /\ $ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += ['S_generated.COMPLETION = THROWING n_exception',
                 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}']
    if name == 'constant':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0x"))',
            'S_bad = S[.RESULT = KNOWN pvalue_request]',
            'S_valid = S_bad[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0x")]]',
            'S_valid_raw = $dz_raw(S_valid)',
            'S_valid_generated = $throwable_transition(S_valid, S_valid_raw)',
            'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]']
        return bindings, [
            ('the original CONST keeps two ordered Warnings and its interned raw operand',
             AUTHORITY + r' /\ z = 7 /\ b_left /\ '
             r'$compiled_read(S, porigin_right) = (PSTRING ($ptascii("0x"))) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
             r'S_raw.EVENTS =/= $leading_warning(S, true, z).EVENTS /\ ' + ZERO + r' /\ ' + CAPTURE),
            ('equal valid request bytes cannot replace the original compiled carrier',
             r'~$ob_object_string_value(S_bad, pvalue_request) /\ '
             r'$ob_object_division_error_capture(S_bad, S_generated) = eps /\ '
             r'$ob_object_string_value(S_valid, pvalue_request) /\ '
             r'S_valid_raw.RESULT = KNOWN pvalue_request /\ '
             r'S_valid_generated.EVENTS = S_generated.EVENTS /\ '
             r'$ob_object_return_error_live(S_valid_generated, pobreturnerror) /\ '
             r'~$integer_operand_source(S_valid, porigin_operator, [PCFIELD 1], S_valid.RESULT) /\ '
             r'$ob_object_division_error_capture(S_valid, S_valid_generated) = eps'),
            ('exact Warning projection source native context and nonowning inputs remain required',
             r'$ob_object_division_error_capture(S, S_generated[.EVENTS = S.EVENTS]) = eps /\ '
             r'$ob_object_division_error_capture(S, S_generated[.EVENTS = $leading_warning(S, true, z).EVENTS]) = eps /\ '
             r'$ob_object_division_error_capture(S, S_generated[.RESULT = KNOWN pvalue_right]) = eps /\ '
             r'~$ob_object_division_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
             r'$ob_object_division_error_capture(S[.CURRENT = eps], S_generated) = eps /\ '
             r'$ob_object_division_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps /\ '
             r'$ob_object_division_error_capture(S[.TODO = (BINARY_RIGHT MULTIPLY (VARIABLE n_left* z_left) z) :: ptask_tail*], S_generated) = eps')]

    bindings += [
        'pvalue_left_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5"))',
        'S_bad_left = S[.STORE[n_cell_left] = DEFINED pvalue_left_request]',
        'S_good_left = S_bad_left[.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5")]]',
        'pvalue_right_request = PSTRING_CARRIER (REQUEST_STRING (|S_good_left.STRINGDATA|)) ($ptascii("0x"))',
        'S_bad_right = S_good_left[.STORE[n_cell_right] = DEFINED pvalue_right_request]',
        'S_good = S_bad_right[.STRINGDATA = S_good_left.STRINGDATA ++ [$ptascii("0x")]]',
        'S_good_raw = $dz_raw(S_good)', 'S_good_generated = $throwable_transition(S_good, S_good_raw)',
        'S_other = S[.RESULT = VARIABLE ($ptascii("c")) z_right]',
        'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
        'S_copy = S[.RESULT = KNOWN pvalue_right]',
        'S_copy_generated = $throwable_transition(S_copy, $dz_raw(S_copy))',
        'S_line = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
        'S_line_generated = $throwable_transition(S_line, $dz_raw(S_line))']
    return bindings, [
        ('quiet full-numeric left and leading-zero right retain their own three private cells',
         AUTHORITY + r' /\ z = 9 /\ z_left = 9 /\ z_right = 9 /\ ~b_left /\ '
         r'$string_bytes(pvalue_left) = ($ptascii("1.5")) /\ '
         r'$ob_object_division_number(pvalue_left) /\ ~$ob_object_division_number(pvalue_right) /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
         r'n_cell_left =/= n_cell_right /\ n_cell_left =/= n_cell_other /\ n_cell_right =/= n_cell_other /\ '
         r'$heap_count(HCELL n_cell_left, $machine_roots(S_generated)) = 1 /\ '
         r'$heap_count(HCELL n_cell_right, $machine_roots(S_generated)) = 1 /\ '
         r'$heap_count(HCELL n_cell_other, $machine_roots(S_generated)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_generated)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_generated)) = 1 /\ ' + ZERO + r' /\ ' + CAPTURE),
        ('current left and right carriers need valid identities while the same own-CV values remain admitted',
         r'~$ob_object_string_value(S_bad_left, pvalue_left_request) /\ '
         r'$ob_object_error_operand_value(S_bad_left, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ '
         r'$ob_object_division_error_capture(S_bad_left, S_generated) = eps /\ '
         r'~$ob_object_string_value(S_bad_right, pvalue_right_request) /\ '
         r'$ob_object_division_error_capture(S_bad_right, S_generated) = eps /\ '
         r'$ob_object_string_value(S_good, pvalue_left_request) /\ '
         r'$ob_object_string_value(S_good, pvalue_right_request) /\ '
         r'$ob_object_error_operand_value(S_good, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left_request) /\ '
         r'$ob_object_error_operand_value(S_good, S_good.RESULT, [PCFIELD 1], z) = (pvalue_right_request) /\ '
         r'S_good_raw.RESULT = KNOWN pvalue_right_request /\ S_good_raw.EVENTS = S_raw.EVENTS /\ '
         r'$ob_object_return_error_live(S_good_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('the same Error cannot authenticate another CV a KNOWN copy or a wrong read line',
         r'S_other_generated = S_generated /\ S_copy_generated = S_generated /\ S_line_generated = S_generated /\ '
         r'~$integer_operand_source(S_other, porigin_operator, [PCFIELD 1], S_other.RESULT) /\ '
         r'$ob_object_error_operand_value(S_other, S_other.RESULT, [PCFIELD 1], z) = eps /\ '
         r'$ob_object_division_error_capture(S_other, S_other_generated) = eps /\ '
         r'~$integer_operand_source(S_copy, porigin_operator, [PCFIELD 1], S_copy.RESULT) /\ '
         r'$ob_object_division_error_capture(S_copy, S_copy_generated) = eps /\ '
         r'~$integer_operand_source(S_line, porigin_operator, [PCFIELD 1], S_line.RESULT) /\ '
         r'$ob_object_division_error_capture(S_line, S_line_generated) = eps')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output; out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/semantics/modules.json',
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
    watched += [Path(__file__), Path(previous.__file__)]
    fingerprint = lambda: {str(p): prior.common.sha(p) for p in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'module_count': len(modules), 'fixture_timeout_seconds': 300, 'source_agreement_credit': 0,
              'before': fingerprint(), 'records': [], 'passed': False}
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
            inputs = lambda: {str(p): prior.common.sha(p) for p in [path, cache, fixture]}
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
            assert record['inputs_before'] == record['inputs_after']
            record['passed'] = True
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(name, len(checks), record['seconds'], flush=True)
        report.update(after=fingerprint(), after_revision=head())
        report['passed'] = report['before'] == report['after'] and report['revision'] == report['after_revision']
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if 'after' not in report:
            report['after'] = fingerprint()
        if 'after_revision' not in report:
            report['after_revision'] = head()
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
