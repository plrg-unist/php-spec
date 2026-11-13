#!/usr/bin/env python3
"""Noisy left CVs retain their own read and the original noisy RHS CONST."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_modulo_conversion_error_review_state as previous
import output_final_default_both_left_cv_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
OWN = sources.CASES['native-default-both-left-cv-modulo-conversion-error-string-notices'].replace(
    b"        return $left % '0.5x';", b"        $other = '1.5x';\n        return $left % '0.5x';")
HANDLERS = sources.CASES['native-default-both-left-cv-modulo-conversion-error-string-notices'].replace(
    b'declare(strict_types=0);', b'declare(strict_types=0); function ob_both_left_cv_handler($level, $message) {}')
UNUSED = previous.sources.CASES['native-default-both-modulo-conversion-error-string-notices'].replace(
    b"        return '1.5x' % '0.5x';", b"        $unused = 0;\n        return '1.5x' % '0.5x';")
assert OWN != sources.CASES['native-default-both-left-cv-modulo-conversion-error-string-notices']
CASES = {'source': OWN, 'carrier': OWN, 'handlers': HANDLERS, 'unused-cv': UNUSED}
WARNING = r'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered"))'
LEFT = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision')
RIGHT = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
LIVE = r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_generated, pobreturnerror)'


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)']
    error = 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}'
    if name == 'handlers':
        bindings += [
            'poperand_left = VARIABLE n_left* z_left',
            '$call_target(S, $ptascii("ob_both_left_cv_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_silent_generated.COMPLETION = THROWING n_exception', error,
            'S_warning = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_both_left_cv_handler"))), LEVELS 2}]',
            'S_deprecated = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_both_left_cv_handler"))), LEVELS 8192}]',
            'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning.ERRORHANDLER]',
            'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated.ERRORHANDLER]']
        return bindings, [
            ('masked eligible Warning or Deprecated callbacks cannot borrow a real both-noisy Error',
             r'z = 7 /\ z_left = 7 /\ n_left* = $ptascii("left") /\ '
             r'pfunction_handler.NAME = $ptascii("ob_both_left_cv_handler") /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 0], poperand_left) /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 1], S_silent.RESULT) /\ '
             r'$integer_slot_rank(S_silent, porigin_operator, [PCFIELD 0], poperand_left) = (8) /\ '
             r'$integer_slot_rank(S_silent, porigin_operator, [PCFIELD 1], S_silent.RESULT) = (1) /\ '
             r'$call_current_valid(S_warning) /\ $call_current_valid(S_deprecated) /\ '
             r'S_silent_generated.EVENTS = S.EVENTS /\ '
             r'$error_handler_eligible(S_warning, 2) /\ ~$error_handler_eligible(S_warning, 8192) /\ '
             r'~$error_handler_eligible(S_deprecated, 2) /\ $error_handler_eligible(S_deprecated, 8192) /\ '
             r'$ob_object_division_error_source(S_warning_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_warning_next, pobreturnerror) /\ '
             r'$ob_object_division_error_source(S_deprecated_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_deprecated_next, pobreturnerror) /\ '
             r'$machine_roots(S_warning_next) = $machine_roots(S_silent_generated) /\ '
             r'$machine_roots(S_deprecated_next) = $machine_roots(S_silent_generated) /\ '
             r'$ob_object_division_error_capture(S_warning, S_warning_next) = eps /\ '
             r'$ob_object_division_error_capture(S_deprecated, S_deprecated_next) = eps')]
    bindings += [
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception', error]
    line = '7' if name == 'unused-cv' else '8'
    notices = ', '.join([WARNING + ' ' + line, LEFT + ' ' + line, WARNING + ' ' + line, RIGHT + ' ' + line])
    noisy = (r'$ob_object_modulo_integer(pvalue_left) = eps /\ $long_convertible(pvalue_left) /\ '
             r'$ob_object_modulo_integer(pvalue_right) = eps /\ $long_convertible(pvalue_right)')
    if name == 'unused-cv':
        bindings += ['poperand_left = KNOWN pvalue_left', '$lookup(S.ENV, $ptascii("unused")) = (n_unused)']
        return bindings, [
            ('a genuine unused private cell cannot broaden the original both-CONST empty-CV bound',
             r'z = 7 /\ pfunction.CVS = [$ptascii("unused")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
             r'S.STORE[n_unused] = DEFINED (PINT 0) /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
             r'~(n_unused <- S.REFCELLS) /\ $heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
             r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ ' + noisy + r' /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], poperand_left) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 7 /\ '
             'S_raw.EVENTS = S.EVENTS ++ [' + notices + r'] /\ ' + LIVE + r' /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += [
        'poperand_left = VARIABLE n_left* z_left',
        '$lookup(S.ENV, n_left*) = (n_cell)', 'S.STORE[n_cell] = DEFINED pvalue_left',
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'S.STORE[n_other] = DEFINED pvalue_left']
    genuine = (
        r'z = 8 /\ z_left = 8 /\ n_left* = $ptascii("left") /\ '
        r'pfunction.CVS = [$ptascii("left"), $ptascii("other")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 2 /\ '
        r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
        r'pvalue_right_compiled = PSTRING ($ptascii("0.5x")) /\ '
        r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
        r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
        r'n_cell =/= n_other /\ (HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS) /\ '
        r'$heap_count(HCELL n_cell, $machine_roots(S)) = 1 /\ $heap_owners($heap_graph(S), HCELL n_cell) = 1 /\ '
        r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], poperand_left) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (8) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ ' + noisy + r' /\ '
        r'$ob_object_string_value(S, pvalue_left) /\ $ob_object_string_value(S, pvalue_right) /\ '
        r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
        r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8 /\ '
        r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S.EVENTS ++ [' + notices + r'] /\ ' + LIVE)
    if name == 'carrier':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5x"))',
            'S_request = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED pvalue_request)][.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5x")]]',
            'S_request_raw = $dz_raw(S_request)', 'S_request_generated = $throwable_transition(S_request, S_request_raw)',
            'S_invalid = S_request[.STRINGDATA = S.STRINGDATA]',
            'pvalue_right_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0.5x"))',
            'S_right = S[.RESULT = KNOWN pvalue_right_request][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0.5x")]]',
            'S_right_raw = $dz_raw(S_right)', 'S_right_generated = $throwable_transition(S_right, S_right_raw)']
        return bindings, [
            ('a current REQUEST header stored in the own left CV preserves both original conversion pairs',
             genuine + r' /\ ' + CAPTURE + r' /\ '
             r'$call_current_valid(S_request) /\ $integer_operand_source(S_request, porigin_operator, [PCFIELD 0], poperand_left) /\ '
             r'$ob_object_error_operand_value(S_request, poperand_left, [PCFIELD 0], z) = (pvalue_request) /\ '
             r'$ob_object_string_value(S_request, pvalue_request) /\ '
             r'S_request_raw = S_raw[.STORE = S_request.STORE][.STRINGDATA = S_request.STRINGDATA] /\ '
             r'S_request_generated = S_generated[.STORE = S_request.STORE][.STRINGDATA = S_request.STRINGDATA] /\ '
             r'$ob_object_division_error_capture(S_request, S_request_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('same-byte left storage without its REQUEST identity fails the own private read',
             r'$integer_operand_source(S_invalid, porigin_operator, [PCFIELD 0], poperand_left) /\ '
             r'~$ob_object_string_value(S_invalid, pvalue_request) /\ '
             r'$ob_object_error_operand_value(S_invalid, poperand_left, [PCFIELD 0], z) = eps'),
            ('valid same-byte right REQUEST data retains the real Error but cannot replace its original CONST',
             r'$call_current_valid(S_right) /\ $ob_object_string_value(S_right, pvalue_right_request) /\ '
             r'$ob_object_error_operand_value(S_right, S_right.RESULT, [PCFIELD 1], z) = (pvalue_right_request) /\ '
             r'$integer_slot_rank(S_right, porigin_operator, [PCFIELD 1], S_right.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_right, porigin_operator, [PCFIELD 1], S_right.RESULT) /\ '
             r'S_right_raw = S_raw[.STRINGDATA = S_right.STRINGDATA] /\ '
             r'S_right_generated = S_generated[.STRINGDATA = S_right.STRINGDATA] /\ '
             r'$ob_object_division_error_source(S_right_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_right_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_right, S_right_generated) = eps')]
    bindings += [
        'S_other = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE ($ptascii("other")) z_left) z) :: ptask_tail*]',
        'S_line = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* $(z_left + 1)) z) :: ptask_tail*]',
        'S_known = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*]',
        'S_reference = S[.REFCELLS = S.REFCELLS ++ [n_cell]]',
        'S_reference_raw = $dz_raw(S_reference)',
        'S_reference_generated = $throwable_transition(S_reference, S_reference_raw)',
        'S_swapped = S_generated[.EVENTS = S.EVENTS ++ [' + WARNING + ' 8, ' + RIGHT + ' 8, ' + WARNING + ' 8, ' + LEFT + ' 8]]']
    checks = [('the own noisy left CV precedes its original noisy RHS CONST with distinct ordered diagnostic pairs',
               genuine + r' /\ ' + CAPTURE)]
    for suffix, label, operand in [('other', 'same-valued other CV', 'VARIABLE ($ptascii("other")) z_left'),
                                    ('line', 'forged left read line', 'VARIABLE n_left* $(z_left + 1)'),
                                    ('known', 'resolved value substituted for its left CV', 'KNOWN pvalue_left')]:
        state = 'S_' + suffix
        checks.append((label + ' keeps the raw Error but lacks its original left source',
            '$integer_slot_rank(' + state + ', porigin_operator, [PCFIELD 0], ' + operand + ') = ' + ('eps' if suffix == 'known' else '(8)') + r' /\ ' +
            '~$integer_operand_source(' + state + ', porigin_operator, [PCFIELD 0], ' + operand + r') /\ ' +
            '$ob_object_error_operand_value(' + state + ', ' + operand + r', [PCFIELD 0], z) = ' + ('(pvalue_left)' if suffix == 'known' else 'eps') + r' /\ ' +
            '$dz_raw(' + state + r') = S_raw /\ $ob_object_division_error_capture(' + state + r', S_generated) = eps'))
    checks += [
        ('reference-marking the actual left cell retains the real Error outside the private reader boundary',
         r'$integer_operand_source(S_reference, porigin_operator, [PCFIELD 0], poperand_left) /\ '
         r'$ob_object_error_operand_value(S_reference, poperand_left, [PCFIELD 0], z) = eps /\ '
         r'S_reference_raw = S_raw[.REFCELLS = S_reference.REFCELLS] /\ '
         r'S_reference_generated = S_generated[.REFCELLS = S_reference.REFCELLS] /\ '
         r'$ob_object_division_error_source(S_reference_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_reference_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_reference, S_reference_generated) = eps'),
        ('a live same-source Error cannot swap the distinct left and right diagnostic pairs',
         LIVE + r' /\ S_swapped.EVENTS =/= S_generated.EVENTS /\ '
         r'$ob_object_division_error_source(S_swapped, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_swapped, pobreturnerror) /\ '
         r'$machine_roots(S_swapped) = $machine_roots(S_generated) /\ '
         r'$ob_object_division_error_capture(S, S_swapped) = eps')]
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
        'tests/semantics/output_final_default_both_left_cv_modulo_conversion_error_sources.py',
        'tests/semantics/output_final_default_both_modulo_conversion_error_sources.py',
        'tests/semantics/output_final_default_both_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
        'tests/semantics/output_final_default_right_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
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
