#!/usr/bin/env python3
"""Precision-only left MOD conversion retains source authority and old notice boundaries."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_modulo_conversion_error_review_state as previous
import output_final_default_left_modulo_deprecation_error_state as author
import output_final_default_left_modulo_deprecation_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
PREFIX = author.PREFIX
ORIGINAL = sources.CASES['native-default-left-modulo-deprecation-error-cv-pair-string']
OWN = ORIGINAL.replace(b"$left = '1.5';", b"$left = '1.5'; $other = '1.5';")
CONST = sources.CASES['native-default-left-modulo-deprecation-error-constant-string']
HANDLERS = ORIGINAL.replace(b'declare(strict_types=0);',
    b'declare(strict_types=0); function ob_left_modulo_deprecation_handler($level, $message) {}')
UNUSED = CONST.replace(b"return '1.5' % 0;", b"$unused = 0; return '1.5' % 0;")
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'constant': CONST, 'carrier': ORIGINAL,
         'handlers': HANDLERS, 'masked': HANDLERS, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE
LIVE = r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_generated, pobreturnerror)'


def authority(name, fixture, path):
    form = 'constant-string' if name in ['constant', 'unused-cv'] else 'cv-pair-string'
    bindings, _ = author.frontier(form, fixture, path)
    bindings += ['S_raw = S_request']
    genuine = author.original(form)
    if name == 'source':
        genuine = genuine.replace('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                                  'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]').replace('|S.ENV| = 2', '|S.ENV| = 3')
    if name == 'unused-cv':
        genuine = genuine.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
        bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_unused)', 'S.STORE[n_unused] = DEFINED (PINT 0)']
        return bindings, [('a genuine unused CV retains the precision-only CONST/CONST empty-CV boundary',
            genuine + r' /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
            r'$heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
            r'$ob_object_division_error_capture(S, S_generated) = eps')]
    if name == 'constant':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5"))',
            'S_request_left = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_request) z) :: ptask_tail*][.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5")]]',
            'S_request_left_raw = $dz_raw(S_request_left)',
            'S_request_left_generated = $throwable_transition(S_request_left, S_request_left_raw)',
            'S_false = S[.RESULT = KNOWN (PBOOL false)]',
            'S_false_raw = $dz_raw(S_false)', 'S_false_generated = $throwable_transition(S_false, S_false_raw)']
        return bindings, [
            ('the original precision-only left CONST precedes the actual compiled quiet zero', genuine + r' /\ ' + CAPTURE),
            ('a valid same-byte REQUEST cannot replace the original precision-only left CONST',
             r'$ob_object_string_value(S_request_left, pvalue_request) /\ '
             r'$ob_object_error_operand_value(S_request_left, KNOWN pvalue_request, [PCFIELD 0], z) = (pvalue_request) /\ '
             r'$integer_slot_rank(S_request_left, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) = (1) /\ '
             r'~$integer_operand_source(S_request_left, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) /\ '
             r'S_request_left_raw = S_raw[.STRINGDATA = S_request_left.STRINGDATA] /\ '
             r'S_request_left_generated = S_generated[.STRINGDATA = S_request_left.STRINGDATA] /\ '
             r'$ob_object_return_error_live(S_request_left_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_request_left, S_request_left_generated) = eps'),
            ('a quiet BOOL zero cannot replace the original compiled PINT zero',
             r'$ob_object_modulo_integer(PBOOL false) = (0) /\ '
             r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) /\ '
             r'S_false_raw = S_raw /\ S_false_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_false, S_false_generated) = eps')]
    if name == 'carrier':
        checks = []
        for side, text in [(0, '1.5'), (1, '0')]:
            state = 'S_request_' + str(side)
            cell = 'n_cell_left' if side == 0 else 'n_cell_right'
            operand = 'VARIABLE n_left* z_left' if side == 0 else state + '.RESULT'
            bindings += [
                'pvalue_request_' + str(side) + ' = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("' + text + '"))',
                state + ' = S[.STORE = $set_cell(S.STORE, ' + cell + ', DEFINED pvalue_request_' + str(side) + ')][.STRINGDATA = S.STRINGDATA ++ [$ptascii("' + text + '")]]',
                state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)',
                state + '_invalid = ' + state + '[.STRINGDATA = S.STRINGDATA]']
            checks += [
                ('an authenticated current REQUEST in the own ' + ('noisy left' if side == 0 else 'quiet right') + ' cell preserves precision-only capture',
                 genuine + r' /\ ' + CAPTURE + r' /\ ' +
                 '$ob_object_error_operand_value(' + state + ', ' + operand + ', [PCFIELD ' + str(side) + '], z) = (pvalue_request_' + str(side) + r') /\ ' +
                 state + '_raw = S_raw[.STORE = ' + state + '.STORE][.STRINGDATA = ' + state + r'.STRINGDATA] /\ ' +
                 state + '_generated = S_generated[.STORE = ' + state + '.STORE][.STRINGDATA = ' + state + r'.STRINGDATA] /\ ' +
                 '$ob_object_division_error_capture(' + state + ', ' + state + r'_generated) = ((pobobjectreturn, pobreturnerror))'),
                ('missing REQUEST identity refuses the own ' + ('left' if side == 0 else 'right') + ' private read',
                 '~$ob_object_string_value(' + state + '_invalid, pvalue_request_' + str(side) + r') /\ ' +
                 '$ob_object_error_operand_value(' + state + '_invalid, ' + ('VARIABLE n_left* z_left' if side == 0 else state + '_invalid.RESULT') + ', [PCFIELD ' + str(side) + r'], z) = eps')]
        return bindings, checks
    if name in ['handlers', 'masked']:
        bindings += [
            '$call_target(S, $ptascii("ob_left_modulo_deprecation_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_warning = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_left_modulo_deprecation_handler"))), LEVELS 2}]',
            'S_deprecated = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_left_modulo_deprecation_handler"))), LEVELS 8192}]']
        if name == 'handlers':
            bindings += [
                'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning.ERRORHANDLER]',
                'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated.ERRORHANDLER]']
            return bindings, [('eligible masked Warning and Deprecated handlers remain outside the fresh default precision-only contour',
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
            'pvalue_prefix = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x"))',
            'S_prefix = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED pvalue_prefix)][.REPORTING = 8192][.REPORTINGINI = $ptascii("8192")][.REPORTINGMODIFIED = true]',
            '$integer_conversion(pvalue_prefix) = (pintegerconversion_prefix)',
            'S_prefix_raw = $dz_raw(S_prefix)', 'S_prefix_generated = $throwable_transition(S_prefix, S_prefix_raw)',
            'pvalue_leading = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))',
            'S_leading = S_deprecated[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED pvalue_leading)]',
            '$integer_conversion(pvalue_leading) = (pintegerconversion_leading)',
            'S_leading_raw = $dz_raw(S_leading)', 'S_leading_generated = $throwable_transition(S_leading, S_leading_raw)']
        return bindings, [
            ('masked leading-plus-precision notices retain their intrinsic two-notice class and old capture',
             genuine + r' /\ pintegerconversion_prefix.NOTICES = [(2, $ptascii("A non-numeric value encountered")), (8192, ' +
             prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision') + r')] /\ '
             r'S_prefix_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' +
             prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision') + r' 8] /\ '
             r'S_prefix_raw.RESULT = KNOWN (PINT 0) /\ '
             r'$ob_object_division_error_capture(S_prefix, S_prefix_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('a leading-only conversion retains its old capture with an eligible unrelated Deprecated handler',
             r'pintegerconversion_leading.NOTICES = [(2, $ptascii("A non-numeric value encountered"))] /\ '
             r'$error_handler_eligible(S_leading, 8192) /\ ~$error_handler_eligible(S_leading, 2) /\ '
             r'S_leading_raw.EVENTS = S.EVENTS /\ '
             r'$ob_object_division_error_capture(S_leading, S_leading_generated) = ((pobobjectreturn, pobreturnerror))')]
    bindings += [
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'S.STORE[n_other] = DEFINED pvalue_left',
        'S_other = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE ($ptascii("other")) z_left) z) :: ptask_tail*]',
        'S_line_left = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* $(z_left + 1)) z) :: ptask_tail*]',
        'S_line_right = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
        'S_known_left = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*]',
        'S_known_right = S[.RESULT = KNOWN pvalue_right]',
        'S_reference_left = S[.REFCELLS = S.REFCELLS ++ [n_cell_left]]',
        'S_reference_right = S[.REFCELLS = S.REFCELLS ++ [n_cell_right]]',
        'S_bad_line = S_generated[.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + prior.value(author.message('string')) + ' 9]]']
    checks = [('the two original private CVs preserve the sole left precision diagnostic before live Error capture', genuine + r' /\ ' + CAPTURE)]
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
    checks += [('an authentic live Error cannot borrow a precision diagnostic from the wrong source line',
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
