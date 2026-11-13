#!/usr/bin/env python3
"""Float range MOD warnings retain own reads and intrinsic notice-class boundaries."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_modulo_conversion_error_review_state as previous
import output_final_default_left_modulo_range_error_state as author
import output_final_default_left_modulo_range_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
PREFIX = author.PREFIX
ORIGINAL = sources.CASES['native-default-left-modulo-range-error-cv-pair-finite']
OWN = ORIGINAL.replace(b'$left = 1e30;', b'$left = 1e30; $other = 1e30;')
CONST = sources.CASES['native-default-left-modulo-range-error-constant-infinite']
HANDLERS = ORIGINAL.replace(b'declare(strict_types=0);',
    b'declare(strict_types=0); function ob_left_modulo_range_handler($level, $message) {}')
UNUSED = CONST.replace(b'return 1e999 % 0;', b'$unused = 0; return 1e999 % 0;')
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'constant': CONST, 'carrier': ORIGINAL,
         'prior-values': ORIGINAL, 'handlers': HANDLERS, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE


def authority(name, fixture, path):
    form = 'constant-infinite' if name in ['constant', 'unused-cv'] else 'cv-pair-finite'
    bindings, _ = author.frontier(form, fixture, path)
    bindings += ['S_raw = S_request']
    genuine = author.original(form)
    if name == 'source':
        genuine = genuine.replace('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                                  'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]').replace('|S.ENV| = 2', '|S.ENV| = 3')
    if name == 'unused-cv':
        genuine = genuine.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
        bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_unused)', 'S.STORE[n_unused] = DEFINED (PINT 0)']
        return bindings, [('a genuine unused CV retains the range-Warning CONST/CONST empty-CV boundary',
            genuine + r' /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
            r'$heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
            r'$ob_object_division_error_capture(S, S_generated) = eps')]
    if name == 'constant':
        bindings += ['S_false = S[.RESULT = KNOWN (PBOOL false)]',
                     'S_false_raw = $dz_raw(S_false)', 'S_false_generated = $throwable_transition(S_false, S_false_raw)']
        return bindings, [
            ('the original infinite CONST warns before the actual compiled quiet zero', genuine + r' /\ ' + CAPTURE),
            ('a quiet BOOL zero cannot replace the original compiled PINT zero',
             r'$ob_object_modulo_integer(PBOOL false) = (0) /\ '
             r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) /\ '
             r'S_false_raw = S_raw /\ S_false_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_false, S_false_generated) = eps')]
    if name == 'carrier':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
            'S_request_right = S[.STORE = $set_cell(S.STORE, n_cell_right, DEFINED pvalue_request)][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]]',
            'S_request_right_raw = $dz_raw(S_request_right)',
            'S_request_right_generated = $throwable_transition(S_request_right, S_request_right_raw)',
            'S_invalid = S_request_right[.STRINGDATA = S.STRINGDATA]']
        return bindings, [
            ('an authenticated current REQUEST in the own quiet RHS preserves the sole range Warning',
             genuine + r' /\ ' + CAPTURE + r' /\ '
             r'$ob_object_error_operand_value(S_request_right, S_request_right.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
             r'S_request_right_raw = S_raw[.STORE = S_request_right.STORE][.STRINGDATA = S_request_right.STRINGDATA] /\ '
             r'S_request_right_generated = S_generated[.STORE = S_request_right.STORE][.STRINGDATA = S_request_right.STRINGDATA] /\ '
             r'$ob_object_division_error_capture(S_request_right, S_request_right_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('missing REQUEST identity refuses the own quiet RHS read',
             r'~$ob_object_string_value(S_invalid, pvalue_request) /\ '
             r'$ob_object_error_operand_value(S_invalid, S_invalid.RESULT, [PCFIELD 1], z) = eps')]
    if name == 'prior-values':
        checks = []
        for suffix, value, level, message in [
            ('precision', 'PFLOAT 4609434218613702656', 'Deprecated', b'Implicit conversion from float 1.5 to int loses precision'),
            ('leading', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', 'Warning', b'A non-numeric value encountered')]:
            state = 'S_' + suffix
            bindings += [state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))]',
                         state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            checks += [('the prior ' + suffix + ' notice class keeps its own private-cell capture',
                genuine + r' /\ ' +
                '$ob_object_error_operand_value(' + state + ', VARIABLE n_left* z_left, [PCFIELD 0], z) = (' + value + r') /\ ' +
                state + '_raw.STORE = ' + state + r'.STORE /\ ' +
                state + '_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "' + level + '" ' + prior.value(message) + r' 8] /\ ' +
                '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
                '$ob_object_division_error_capture(' + state + ', ' + state + r'_generated) = ((pobobjectreturn, pobreturnerror))')]
        bindings += [
            'S_nan = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (PFLOAT 9221120237041090560))][.REPORTING = 2][.REPORTINGINI = $ptascii("2")][.REPORTINGMODIFIED = true]',
            '$integer_conversion(PFLOAT 9221120237041090560) = (pintegerconversion_nan)',
            'S_nan_raw = $dz_raw(S_nan)', 'S_nan_generated = $throwable_transition(S_nan, S_nan_raw)']
        checks += [('the admitted NaN notice vector retains capture with only visible Warning',
            genuine + r' /\ $call_current_valid(S_nan) /\ '
            r'$float_long(9221120237041090560, true) = (0, [RANGEWARNING, PRECISIONLOSS]) /\ '
            r'pintegerconversion_nan.VALUE = 0 /\ pintegerconversion_nan.NOTICES = [(2, ' +
            prior.value(b'The float NAN is not representable as an int, cast occurred') + '), (8192, ' +
            prior.value(b'Implicit conversion from float NAN to int loses precision') + r')] /\ '
            r'$ob_object_error_operand_value(S_nan, VARIABLE n_left* z_left, [PCFIELD 0], z) = (PFLOAT 9221120237041090560) /\ '
            r'$integer_operand_source(S_nan, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) /\ '
            r'~$error_handler_eligible(S_nan, 2) /\ ~$error_handler_eligible(S_nan, 8192) /\ '
            r'S_nan_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8 /\ '
            r'S_nan_raw.RESULT = KNOWN (PINT 0) /\ S_nan_raw.STORE = S_nan.STORE /\ '
            r'S_nan_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" ' +
            prior.value(b'The float NAN is not representable as an int, cast occurred') + r' 8] /\ '
            r'$ob_object_division_error_source(S_nan_generated, pfunction, pobreturnerror) /\ '
            r'$ob_object_return_error_live(S_nan_generated, pobreturnerror) /\ '
            r'$ob_object_division_error_capture(S_nan, S_nan_generated) = ((pobobjectreturn, pobreturnerror))')]
        return bindings, checks
    if name == 'handlers':
        bindings += [
            '$call_target(S, $ptascii("ob_left_modulo_range_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_warning = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_left_modulo_range_handler"))), LEVELS 2}]',
            'S_deprecated = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_left_modulo_range_handler"))), LEVELS 8192}]']
        bindings += [
            'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning.ERRORHANDLER]',
            'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated.ERRORHANDLER]']
        return bindings, [('eligible masked Warning and Deprecated handlers remain outside the fresh default range-Warning contour',
            genuine + r' /\ $call_current_valid(S_warning) /\ $call_current_valid(S_deprecated) /\ '
            r'S_silent_generated.EVENTS = S.EVENTS /\ '
            r'$ob_object_division_error_capture(S_silent, S_silent_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
            r'$error_handler_eligible(S_warning, 2) /\ ~$error_handler_eligible(S_warning, 8192) /\ '
            r'~$error_handler_eligible(S_deprecated, 2) /\ $error_handler_eligible(S_deprecated, 8192) /\ '
            r'$ob_object_return_error_live(S_warning_next, pobreturnerror) /\ '
            r'$ob_object_return_error_live(S_deprecated_next, pobreturnerror) /\ '
            r'$ob_object_division_error_capture(S_warning, S_warning_next) = eps /\ '
            r'$ob_object_division_error_capture(S_deprecated, S_deprecated_next) = eps')]
    bindings += [
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'S.STORE[n_other] = DEFINED pvalue_left',
        'S_other = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE ($ptascii("other")) z_left) z) :: ptask_tail*]',
        'S_line_left = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* $(z_left + 1)) z) :: ptask_tail*]',
        'S_line_right = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
        'S_known_left = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*]',
        'S_known_right = S[.RESULT = KNOWN pvalue_right]',
        'S_reference_left = S[.REFCELLS = S.REFCELLS ++ [n_cell_left]]',
        'S_reference_right = S[.REFCELLS = S.REFCELLS ++ [n_cell_right]]',
        'S_bad_line = S_generated[.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" ' + prior.value(author.message('finite')) + ' 9]]']
    checks = [('the two original private CVs preserve the sole left range Warning before live Error capture', genuine + r' /\ ' + CAPTURE)]
    for state, side, operand in [
        ('S_other', 0, 'VARIABLE ($ptascii("other")) z_left'),
        ('S_line_left', 0, 'VARIABLE n_left* $(z_left + 1)'),
        ('S_line_right', 1, 'S_line_right.RESULT'),
        ('S_known_left', 0, 'KNOWN pvalue_left'),
        ('S_known_right', 1, 'S_known_right.RESULT')]:
        bindings += [state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        expected = '(pvalue_left)' if state == 'S_known_left' else '(pvalue_right)' if state == 'S_known_right' else 'eps'
        checks += [(state + ' cannot substitute the original private source despite the same raw Error',
            '~$integer_operand_source(' + state + ', porigin_operator, [PCFIELD ' + str(side) + '], ' + operand + r') /\ ' +
            '$ob_object_error_operand_value(' + state + ', ' + operand + ', [PCFIELD ' + str(side) + '], z) = ' + expected + r' /\ ' +
            state + r'_raw = S_raw /\ ' + state + r'_generated = S_generated /\ ' +
            '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = eps')]
    for side in ['left', 'right']:
        state = 'S_reference_' + side
        operand = 'VARIABLE n_left* z_left' if side == 'left' else state + '.RESULT'
        field = '0' if side == 'left' else '1'
        bindings += [state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        checks += [('the reference-marked ' + side + ' cell retains the Error outside the private reader',
            '$ob_object_error_operand_value(' + state + ', ' + operand + ', [PCFIELD ' + field + r'], z) = eps /\ ' +
            state + '_raw = S_raw[.REFCELLS = ' + state + r'.REFCELLS] /\ ' +
            state + '_generated = S_generated[.REFCELLS = ' + state + r'.REFCELLS] /\ ' +
            '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
            '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = eps')]
    checks += [('an authentic live Error cannot borrow a range Warning from the wrong source line',
        r'$ob_object_return_error_live(S_bad_line, pobreturnerror) /\ '
        r'$machine_roots(S_bad_line) = $machine_roots(S_generated) /\ '
        r'$ob_object_division_error_capture(S, S_bad_line) = eps')]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_final_default_left_modulo_range_error_sources.py',
        'tests/semantics/output_final_default_left_modulo_range_error_state.py',
        'tests/semantics/output_final_default_left_modulo_deprecation_error_sources.py',
        'tests/semantics/output_final_default_left_modulo_deprecation_error_state.py',
        'tests/semantics/output_final_default_both_cv_modulo_conversion_error_state.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_left_cv_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_right_cv_modulo_conversion_error_state.py',
        'tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_cv_pair_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_both_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_right_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_review_state.py',
        'tests/semantics/output_final_modulo_error_sources.py',
        'tests/semantics/output_final_modulo_error_review_state.py',
        'tests/semantics/output_final_division_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
    watched += [Path(__file__)]
    fingerprint = lambda: {str(p): prior.common.sha(p) for p in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'module_count': len(modules), 'fixture_timeout_seconds': 300,
              'source_agreement_credit': 0, 'before': fingerprint(), 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name])
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
            cache = directory / 'checked.json'
            cache.write_text(json.dumps(checked) + '\n')
            bindings, checks = authority(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            inputs = lambda: {str(p): prior.common.sha(p) for p in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': inputs(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, fixture_execution_credit=0)
                continue
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
        report['passed'] = (not args.prepare_only and all(record['passed'] for record in report['records']) and
                            report['before'] == report['after'] and report['revision'] == report['after_revision'])
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
