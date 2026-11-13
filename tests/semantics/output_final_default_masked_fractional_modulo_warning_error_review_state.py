#!/usr/bin/env python3
"""Masked fractional MOD keeps exact diagnostic history and independent handler bounds."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_review_state as previous
import output_final_default_masked_fractional_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'projection': sources.CASES['native-default-masked-fractional-warning-modulo-warning-only'],
         'handlers': sources.CASES['native-default-masked-fractional-warning-modulo-neither'].replace(
             b'error_reporting(1);', b'function ob_mask_handler($number, $message) {} error_reporting(1);')}
DEPRECATED = prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision')
WARNING = r'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 7'


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN (PINT 0)', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
    genuine = (r'z = 7 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
               r'pvalue_left_compiled = PSTRING ($ptascii("1.5x")) /\ '
               r'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled) /\ '
               r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
               r'$string_long($ptascii("1.5x")) = STRINT 1 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps) /\ '
               r'$ob_object_modulo_integer(pvalue_left) = eps /\ '
               r'$ob_object_error_operand_value(S, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
               r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (PINT 0) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
               r'$value_nodes(pvalue_left) = eps /\ $ob_object_string_value(S, pvalue_left) /\ '
               r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
               r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ '
               r'$base_nodes(S.BASE) = eps /\ '
               r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
               r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 7 /\ '
               r'S_raw.RESULT = KNOWN (PINT 0) /\ ' + previous.LIVE)
    if name == 'handlers':
        bindings += [
            '$call_target(S, $ptascii("ob_mask_handler"), eps) = (pfunction_handler)',
            'S_warning_handler = S[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_mask_handler"))), LEVELS 2}]',
            'S_deprecated_handler = S[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_mask_handler"))), LEVELS 8192}]',
            'S_warning_handler_next = S_generated[.ERRORHANDLER = S_warning_handler.ERRORHANDLER]',
            'S_deprecated_handler_next = S_generated[.ERRORHANDLER = S_deprecated_handler.ERRORHANDLER]']
        return bindings, [
            ('authentic no-event mask1 source keeps the generated Error and capture',
             genuine + r' /\ S.REPORTING = 1 /\ S.REPORTINGINI = $ptascii("1") /\ '
             r'S.REPORTINGMODIFIED /\ S.EVENTS = [OUTPUT ([80])] /\ S_raw.EVENTS = S.EVENTS /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('derived eligible callbacks remain disallowed under mask1 with the original live Error',
             r'pfunction_handler.NAME = $ptascii("ob_mask_handler") /\ '
             r'$value_nodes(PSTRING ($ptascii("ob_mask_handler"))) = eps /\ '
             r'$call_current_valid(S_warning_handler) /\ $call_current_valid(S_deprecated_handler) /\ '
             r'S_warning_handler.REPORTING = 1 /\ S_deprecated_handler.REPORTING = 1 /\ '
             r'$error_handler_eligible(S_warning_handler, 2) /\ ~$error_handler_eligible(S_warning_handler, 8192) /\ '
             r'~$error_handler_eligible(S_deprecated_handler, 2) /\ $error_handler_eligible(S_deprecated_handler, 8192) /\ '
             r'$ob_object_division_error_source(S_warning_handler_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_warning_handler_next, pobreturnerror) /\ '
             r'$ob_object_division_error_source(S_deprecated_handler_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_deprecated_handler_next, pobreturnerror) /\ '
             r'$machine_roots(S_warning_handler_next) = $machine_roots(S_generated) /\ '
             r'$machine_roots(S_deprecated_handler_next) = $machine_roots(S_generated) /\ '
             r'$ob_object_division_error_capture(S_warning_handler, S_warning_handler_next) = eps /\ '
             r'$ob_object_division_error_capture(S_deprecated_handler, S_deprecated_handler_next) = eps')]
    bindings += [
        'S_deprecated = S[.REPORTING = 8193][.REPORTINGINI = $ptascii("8193")][.REPORTINGMODIFIED = true]',
        'S_deprecated_raw = $dz_raw(S_deprecated)',
        'S_deprecated_generated = $throwable_transition(S_deprecated, S_deprecated_raw)',
        'S_none = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
        'S_none_raw = $dz_raw(S_none)', 'S_none_generated = $throwable_transition(S_none, S_none_raw)',
        'S_drop = S_generated[.EVENTS = S.EVENTS]',
        'S_duplicate = S_generated[.EVENTS = S_generated.EVENTS ++ [' + WARNING + ']]',
        'S_wrong = S_deprecated_generated[.EVENTS = S_generated.EVENTS]',
        'S_hidden = S_none_generated[.EVENTS = S_none.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + DEPRECATED + ' 7]]']
    return bindings, [
        ('authentic Warning-only mask3 source captures without exposing Deprecated',
         genuine + r' /\ S.REPORTING = 3 /\ S.REPORTINGINI = $ptascii("3") /\ '
         r'S.REPORTINGMODIFIED /\ S.EVENTS = [OUTPUT ([80])] /\ '
         r'S_raw.EVENTS = S.EVENTS ++ [' + WARNING + r'] /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('derived Deprecated-only and silent masks capture the same conversion and original Error',
         r'$call_current_valid(S_deprecated) /\ $call_current_valid(S_none) /\ '
         r'~$error_handler_eligible(S_deprecated, 2) /\ ~$error_handler_eligible(S_deprecated, 8192) /\ '
         r'~$error_handler_eligible(S_none, 2) /\ ~$error_handler_eligible(S_none, 8192) /\ '
         r'S_deprecated_raw.COMPLETION = S_raw.COMPLETION /\ S_deprecated_raw.RESULT = S_raw.RESULT /\ '
         r'S_none_raw.COMPLETION = S_raw.COMPLETION /\ S_none_raw.RESULT = S_raw.RESULT /\ '
         r'S_deprecated_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + DEPRECATED + r' 7] /\ '
         r'S_none_raw.EVENTS = S.EVENTS /\ '
         r'$ob_object_division_error_capture(S_deprecated, S_deprecated_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$ob_object_division_error_capture(S_none, S_none_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('missing repeated substituted or hidden events cannot borrow the original live Error',
         r'$ob_object_division_error_source(S_drop, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_drop, pobreturnerror) /\ '
         r'$ob_object_division_error_source(S_duplicate, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_duplicate, pobreturnerror) /\ '
         r'$ob_object_division_error_source(S_wrong, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_wrong, pobreturnerror) /\ '
         r'$ob_object_division_error_source(S_hidden, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_hidden, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S, S_drop) = eps /\ '
         r'$ob_object_division_error_capture(S, S_duplicate) = eps /\ '
         r'$ob_object_division_error_capture(S_deprecated, S_wrong) = eps /\ '
         r'$ob_object_division_error_capture(S_none, S_hidden) = eps')]


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
        'tests/semantics/output_final_default_masked_fractional_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_fractional_modulo_warning_error_sources.py',
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
