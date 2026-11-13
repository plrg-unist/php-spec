#!/usr/bin/env python3
"""Noisy MOD right constants retain their exact kind, source and empty-CV bound."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_review_state as previous
import output_final_default_right_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
STRING_SOURCE = sources.CASES['native-default-right-modulo-conversion-error-both'].replace(
    b'declare(strict_types=0);', b'declare(strict_types=0); function ob_right_handler($level, $message) {}')
CASES = {'string-authority': STRING_SOURCE, 'string-handlers': STRING_SOURCE,
         'float-authority': sources.CASES['native-default-right-modulo-conversion-error-float-deprecated']}
CASES['unused-cv'] = CASES['float-authority'].replace(
    b'        return 1 % 0.5;', b'        $unused = 0;\n        return 1 % 0.5;')
assert CASES['unused-cv'] != CASES['float-authority']
STRING_DEPRECATED = prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
FLOAT_DEPRECATED = prior.value(b'Implicit conversion from float 0.5 to int loses precision')
OTHER_DEPRECATED = prior.value(b'Implicit conversion from float-string "0.5" to int loses precision')


def authority(name, fixture, path):
    start = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN (PINT 1)) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)']
    error = 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}'
    bindings = start + [
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
        'S_integer_left = $integer_coerce(S, PINT 1, z)',
        'S_integer_right = $integer_coerce(S_integer_left, pvalue_right, z)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception', error]
    genuine = (r'$compiled_read(S, porigin_left) = (PINT 1) /\ '
               r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
               r'$ob_object_error_operand_value(S, KNOWN (PINT 1), [PCFIELD 0], z) = (PINT 1) /\ '
               r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN (PINT 1)) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN (PINT 1)) = (1) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
               r'$ob_object_modulo_integer(PINT 1) = (1) /\ $ob_object_modulo_integer(pvalue_right) = eps /\ '
               r'$long_convertible(pvalue_right) /\ $value_nodes(pvalue_right) = eps /\ '
               r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
               r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ '
               r'$base_nodes(S.BASE) = eps /\ '
               r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
               r'S_integer_left = S[.RESULT = KNOWN (PINT 1)] /\ '
               r'S_integer_right.COMPLETION = NORMAL /\ S_integer_right.RESULT = KNOWN (PINT 0) /\ '
               r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) z /\ '
               r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_integer_right.EVENTS /\ ' + previous.LIVE)
    float_value = (r'pvalue_right_compiled = PFLOAT 4602678819172646912 /\ '
                   r'pvalue_right = PFLOAT 4602678819172646912 /\ '
                   r'$string_bytes(pvalue_right) = eps')
    if name == 'unused-cv':
        bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_unused)']
        return bindings, [
            ('genuine float conversion and source Error retain the explicit empty-CV refusal with a real unused local',
             genuine + r' /\ ' + float_value + r' /\ z = 7 /\ '
             r'pfunction.CVS = [$ptascii("unused")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
             r'S.STORE[n_unused] = DEFINED (PINT 0) /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
             r'~(n_unused <- S.REFCELLS) /\ $heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
             r'S_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + FLOAT_DEPRECATED + r' 7] /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    empty = r'z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps'
    if name in ['string-authority', 'string-handlers']:
        request_bindings = [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0.5x"))',
            'S_request = S[.RESULT = KNOWN pvalue_request][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0.5x")]]',
            'S_request_raw = $dz_raw(S_request)',
            'S_request_generated = $throwable_transition(S_request, S_request_raw)']
        handler_bindings = [
            '$call_target(S, $ptascii("ob_right_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_silent_generated.COMPLETION = THROWING n_exception', error,
            'S_warning_handler = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_right_handler"))), LEVELS 2}]',
            'S_deprecated_handler = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_right_handler"))), LEVELS 8192}]',
            'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning_handler.ERRORHANDLER]',
            'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated_handler.ERRORHANDLER]']
        checks = [
            ('genuine own string RHS retains ordered Warning and string-Deprecated before actual capture',
             genuine + r' /\ ' + empty + r' /\ '
             r'pvalue_right_compiled = PSTRING ($ptascii("0.5x")) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
             r'$ob_object_string_value(S, pvalue_right) /\ '
             r'$string_long($ptascii("0.5x")) = STRINT 0 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps) /\ '
             r'S_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6, '
             r'DIAGNOSTIC "Deprecated" ' + STRING_DEPRECATED + r' 6] /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('valid same-byte request carrier retains real conversion and Error but cannot replace its own compiled RHS',
             r'$call_current_valid(S_request) /\ $ob_object_string_value(S_request, pvalue_request) /\ '
             r'$value_nodes(pvalue_request) = eps /\ $ob_object_modulo_integer(pvalue_request) = eps /\ '
             r'$ob_object_error_operand_value(S_request, S_request.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
             r'$integer_slot_rank(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) /\ '
             r'S_request_raw = S_raw[.STRINGDATA = S_request.STRINGDATA] /\ '
             r'S_request_generated = S_generated[.STRINGDATA = S_request.STRINGDATA] /\ '
             r'$ob_object_division_error_source(S_request_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_request_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_request, S_request_generated) = eps'),
            ('derived eligible callbacks under silent reporting cannot borrow the original live Error',
             r'pfunction_handler.NAME = $ptascii("ob_right_handler") /\ '
             r'$call_current_valid(S_warning_handler) /\ $call_current_valid(S_deprecated_handler) /\ '
             r'S_silent_generated.EVENTS = S.EVENTS /\ '
             r'$error_handler_eligible(S_warning_handler, 2) /\ ~$error_handler_eligible(S_warning_handler, 8192) /\ '
             r'~$error_handler_eligible(S_deprecated_handler, 2) /\ $error_handler_eligible(S_deprecated_handler, 8192) /\ '
             r'$ob_object_division_error_source(S_warning_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_warning_next, pobreturnerror) /\ '
             r'$ob_object_division_error_source(S_deprecated_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_deprecated_next, pobreturnerror) /\ '
             r'$machine_roots(S_warning_next) = $machine_roots(S_silent_generated) /\ '
             r'$machine_roots(S_deprecated_next) = $machine_roots(S_silent_generated) /\ '
             r'$ob_object_division_error_capture(S_warning_handler, S_warning_next) = eps /\ '
             r'$ob_object_division_error_capture(S_deprecated_handler, S_deprecated_next) = eps')]
        if name == 'string-authority':
            return bindings + request_bindings, checks[:2]
        return start + handler_bindings, checks[2:]
    bindings += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0.5"))',
        'S_kind = S[.RESULT = KNOWN pvalue_request][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0.5")]]',
        'S_kind_raw = $dz_raw(S_kind)', 'S_kind_generated = $throwable_transition(S_kind, S_kind_raw)',
        'S_line = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (PINT 1)) $(z + 1)) :: ptask_tail*]',
        'S_line_generated = $throwable_transition(S_line, $dz_raw(S_line))',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]']
    return bindings, [
        ('genuine half-valued float RHS truncates to zero with float-Deprecated and actual capture',
         genuine + r' /\ ' + empty + r' /\ ' + float_value + r' /\ '
         r'S_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + FLOAT_DEPRECATED + r' 6] /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('same-zero string kind and forged operation line retain real Errors without borrowing the original float source',
         r'$call_current_valid(S_kind) /\ $ob_object_string_value(S_kind, pvalue_request) /\ '
         r'$ob_object_modulo_integer(pvalue_request) = eps /\ '
         r'$ob_object_error_operand_value(S_kind, S_kind.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
         r'~$integer_operand_source(S_kind, porigin_operator, [PCFIELD 1], S_kind.RESULT) /\ '
         r'S_kind_raw.COMPLETION = S_raw.COMPLETION /\ S_kind_raw.RESULT = S_raw.RESULT /\ '
         r'S_kind_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + OTHER_DEPRECATED + r' 6] /\ '
         r'$ob_object_division_error_source(S_kind_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_kind_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_kind, S_kind_generated) = eps /\ '
         r'$throwable_field(S_line_generated, n_exception, "line") = PINT 7 /\ '
         r'$ob_object_return_error_live(S_line_generated, pobreturnerror_line) /\ '
         r'~$ob_object_division_error_source(S_line_generated, pfunction, pobreturnerror_line) /\ '
         r'$ob_object_division_error_capture(S_line, S_line_generated) = eps')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
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
        report['passed'] = (all(record['passed'] for record in report['records']) and
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
