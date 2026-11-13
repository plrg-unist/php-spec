#!/usr/bin/env python3
"""Both noisy MOD constants retain source, conversion order and empty-CV bounds."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_right_modulo_conversion_error_review_state as previous
import output_final_default_both_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
LIVE = previous.previous.LIVE
STRING_SOURCE = sources.CASES['native-default-both-modulo-conversion-error-string-notices'].replace(
    b'declare(strict_types=0);', b'declare(strict_types=0); function ob_both_handler($level, $message) {}')
CASES = {'string-left': STRING_SOURCE, 'string-right': STRING_SOURCE, 'string-handlers': STRING_SOURCE,
         'float-authority': sources.CASES['native-default-both-modulo-conversion-error-float-deprecated']}
CASES['unused-cv'] = CASES['float-authority'].replace(
    b'        return 1.5 % 0.5;', b'        $unused = 0;\n        return 1.5 % 0.5;')
assert CASES['unused-cv'] != CASES['float-authority']
WARNING = r'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered"))'
STRING_LEFT = prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision')
STRING_RIGHT = prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
FLOAT_LEFT = prior.value(b'Implicit conversion from float 1.5 to int loses precision')
FLOAT_RIGHT = prior.value(b'Implicit conversion from float 0.5 to int loses precision')
KIND_LEFT = prior.value(b'Implicit conversion from float-string "1.5" to int loses precision')
STRING_KINDS = (r'pvalue_left_compiled = PSTRING ($ptascii("1.5x")) /\ '
                r'pvalue_right_compiled = PSTRING ($ptascii("0.5x")) /\ '
                r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
                r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x"))')
FLOAT_KINDS = (r'pvalue_left_compiled = PFLOAT 4609434218613702656 /\ '
               r'pvalue_left = PFLOAT 4609434218613702656 /\ '
               r'pvalue_right_compiled = PFLOAT 4602678819172646912 /\ '
               r'pvalue_right = PFLOAT 4602678819172646912 /\ '
               r'$string_bytes(pvalue_left) = eps /\ $string_bytes(pvalue_right) = eps')


def authority(name, fixture, path):
    start = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)']
    error = 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}'
    empty = r'z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps'
    noisy = (r'$ob_object_modulo_integer(pvalue_left) = eps /\ $long_convertible(pvalue_left) /\ '
             r'$ob_object_modulo_integer(pvalue_right) = eps /\ $long_convertible(pvalue_right)')
    if name == 'string-handlers':
        bindings = start + [
            '$call_target(S, $ptascii("ob_both_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_silent_generated.COMPLETION = THROWING n_exception', error,
            'S_warning_handler = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_both_handler"))), LEVELS 2}]',
            'S_deprecated_handler = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_both_handler"))), LEVELS 8192}]',
            'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning_handler.ERRORHANDLER]',
            'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated_handler.ERRORHANDLER]']
        return bindings, [
            ('eligible Warning and Deprecated callbacks under silent reporting cannot borrow a real both-noisy Error',
             empty + r' /\ ' + noisy + r' /\ '
             r'pfunction_handler.NAME = $ptascii("ob_both_handler") /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 1], S_silent.RESULT) /\ '
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
    bindings = start + [
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
        '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception', error]
    genuine = (r'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled) /\ '
               r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
               r'$ob_object_error_operand_value(S, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
               r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ ' +
               noisy + r' /\ $value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
               r'($string_bytes(pvalue_left) = eps \/ $ob_object_string_value(S, pvalue_left)) /\ '
               r'($string_bytes(pvalue_right) = eps \/ $ob_object_string_value(S, pvalue_right)) /\ '
               r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
               r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ '
               r'$base_nodes(S.BASE) = eps /\ '
               r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
               r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) z /\ '
               r'S_raw.RESULT = KNOWN (PINT 0) /\ ' + LIVE)
    capture = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
    string_events = (WARNING + ' 6, DIAGNOSTIC "Deprecated" ' + STRING_LEFT + ' 6, ' +
                     WARNING + ' 6, DIAGNOSTIC "Deprecated" ' + STRING_RIGHT + ' 6')
    if name in ['string-left', 'string-right']:
        left = name == 'string-left'
        side = 0 if left else 1
        value = '1.5x' if left else '0.5x'
        replacement = ('S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_request) z) :: ptask_tail*]'
                       if left else 'S[.RESULT = KNOWN pvalue_request]')
        operand = 'KNOWN pvalue_request' if left else 'S_request.RESULT'
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("' + value + '"))',
            'S_request = ' + replacement + '[.STRINGDATA = S.STRINGDATA ++ [$ptascii("' + value + '")]]',
            'S_request_raw = $dz_raw(S_request)',
            'S_request_generated = $throwable_transition(S_request, S_request_raw)']
        refusal = (
            r'$call_current_valid(S_request) /\ $ob_object_string_value(S_request, pvalue_request) /\ '
            r'$value_nodes(pvalue_request) = eps /\ $ob_object_modulo_integer(pvalue_request) = eps /\ '
            '$ob_object_error_operand_value(S_request, ' + operand + ', [PCFIELD ' + str(side) + '], z) = (pvalue_request) /\\ ' +
            '$integer_slot_rank(S_request, porigin_operator, [PCFIELD ' + str(side) + '], ' + operand + ') = (1) /\\ ' +
            '~$integer_operand_source(S_request, porigin_operator, [PCFIELD ' + str(side) + '], ' + operand + ') /\\ ' +
            r'S_request_raw = S_raw[.STRINGDATA = S_request.STRINGDATA] /\ '
            r'S_request_generated = S_generated[.STRINGDATA = S_request.STRINGDATA] /\ '
            r'$ob_object_division_error_source(S_request_generated, pfunction, pobreturnerror) /\ '
            r'$ob_object_return_error_live(S_request_generated, pobreturnerror) /\ '
            r'$ob_object_division_error_capture(S_request, S_request_generated) = eps')
        if left:
            return bindings, [
                ('genuine own string constants preserve distinguishable left then right Warning/Deprecated pairs',
                 genuine + r' /\ ' + empty + r' /\ ' + STRING_KINDS + r' /\ '
                 'S_raw.EVENTS = S.EVENTS ++ [' + string_events + r'] /\ ' + capture),
                ('valid same-byte left REQUEST carrier keeps the real Error but cannot replace its own compiled left',
                 refusal)]
        swapped = (WARNING + ' 6, DIAGNOSTIC "Deprecated" ' + STRING_RIGHT + ' 6, ' +
                   WARNING + ' 6, DIAGNOSTIC "Deprecated" ' + STRING_LEFT + ' 6')
        bindings += ['S_swapped = S_generated[.EVENTS = S.EVENTS ++ [' + swapped + ']]']
        return bindings, [
            ('valid same-byte right REQUEST carrier keeps the real Error but cannot replace its own compiled right',
             refusal),
            ('a live same-source Error cannot replace the actual left-before-right diagnostic order',
             empty + r' /\ ' + noisy + r' /\ ' + capture + r' /\ '
             'S_raw.EVENTS = S.EVENTS ++ [' + string_events + r'] /\ '
             r'S_swapped.EVENTS =/= S_generated.EVENTS /\ '
             r'$ob_object_division_error_source(S_swapped, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_swapped, pobreturnerror) /\ '
             r'$machine_roots(S_swapped) = $machine_roots(S_generated) /\ '
             r'$ob_object_division_error_capture(S, S_swapped) = eps')]
    line = '7' if name == 'unused-cv' else '6'
    float_events = ('DIAGNOSTIC "Deprecated" ' + FLOAT_LEFT + ' ' + line +
                    ', DIAGNOSTIC "Deprecated" ' + FLOAT_RIGHT + ' ' + line)
    if name == 'unused-cv':
        bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_unused)']
        return bindings, [
            ('a genuine allocated unused CV keeps both float conversions and the live Error but refuses empty-CV capture',
             genuine + r' /\ ' + FLOAT_KINDS + r' /\ z = 7 /\ '
             r'pfunction.CVS = [$ptascii("unused")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
             r'S.STORE[n_unused] = DEFINED (PINT 0) /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
             r'~(n_unused <- S.REFCELLS) /\ $heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
             'S_raw.EVENTS = S.EVENTS ++ [' + float_events + r'] /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5"))',
        'S_kind = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_request) z) :: ptask_tail*][.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5")]]',
        'S_kind_raw = $dz_raw(S_kind)', 'S_kind_generated = $throwable_transition(S_kind, S_kind_raw)']
    return bindings, [
        ('genuine own float constants retain distinct left and right float-Deprecated messages before capture',
         genuine + r' /\ ' + empty + r' /\ ' + FLOAT_KINDS + r' /\ '
         'S_raw.EVENTS = S.EVENTS ++ [' + float_events + r'] /\ ' + capture),
        ('a valid equal-integer string kind cannot borrow the original left float source',
         r'$call_current_valid(S_kind) /\ $ob_object_string_value(S_kind, pvalue_request) /\ '
         r'$ob_object_modulo_integer(pvalue_request) = eps /\ $long_convertible(pvalue_request) /\ '
         r'$ob_object_error_operand_value(S_kind, KNOWN pvalue_request, [PCFIELD 0], z) = (pvalue_request) /\ '
         r'$integer_slot_rank(S_kind, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) = (1) /\ '
         r'~$integer_operand_source(S_kind, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) /\ '
         r'S_kind_raw.COMPLETION = S_raw.COMPLETION /\ S_kind_raw.RESULT = S_raw.RESULT /\ '
         'S_kind_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + KIND_LEFT +
         ' 6, DIAGNOSTIC "Deprecated" ' + FLOAT_RIGHT + r' 6] /\ '
         r'$ob_object_division_error_source(S_kind_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_kind_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_kind, S_kind_generated) = eps')]


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
        'tests/semantics/output_final_default_both_modulo_conversion_error_sources.py',
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
