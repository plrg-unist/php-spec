#!/usr/bin/env python3
"""Visible precision diagnostics retain their profile and CONST-pair boundary."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_review_state as previous
import output_final_default_fractional_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'profiles': sources.CASES['native-default-fractional-warning-modulo-positive']}
CASES['cv-scope'] = CASES['profiles'].replace(b"        return '1.5x' % 0;",
    b"        $b = '1.5x';\n        $c = 0;\n        return $b % $c;")
DEPRECATED = prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision')


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        '$string_bytes(pvalue_left) = (n_bytes_left*)',
        'S_notices = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, n_bytes_left*, z)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
    genuine = (r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
               r'$string_long(n_bytes_left*) = STRINT 1 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps) /\ '
               r'pvalue_right = PINT 0 /\ $ob_object_modulo_integer(pvalue_right) = (0) /\ '
               r'$ob_object_modulo_integer(pvalue_left) = eps /\ '
               r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
               r'$ob_object_string_value(S, pvalue_left) /\ '
               r'($string_bytes(pvalue_right) = eps \/ $ob_object_string_value(S, pvalue_right)) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], poperand_left) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
               r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
               r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ '
               r'$base_nodes(S.BASE) = eps /\ '
               r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
               r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) z /\ '
               r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_notices.EVENTS /\ '
               r'S_notices.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) z, '
               r'DIAGNOSTIC "Deprecated" ' + DEPRECATED + r' z] /\ '
               r'|S_raw.EVENTS| = $(|S.EVENTS| + 2) /\ ' + previous.LIVE)
    if name == 'cv-scope':
        bindings += [
            'poperand_left = VARIABLE n_left* z_left', 'S.RESULT = VARIABLE n_right* z_right',
            '$lookup(S.ENV, n_left*) = (n_cell_left)', '$lookup(S.ENV, n_right*) = (n_cell_right)']
        return bindings, [
            ('genuine private8x8 retains source/read/raw/visible-two bounds and captures',
             genuine + r' /\ z = 8 /\ z_left = 8 /\ z_right = 8 /\ '
             r'n_left* = $ptascii("b") /\ n_right* = $ptascii("c") /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (8) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'n_cell_left =/= n_cell_right /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1 /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')]
    bindings += [
        'poperand_left = KNOWN pvalue_left', 'S.RESULT = KNOWN (PINT 0)',
        'S_deprecated = S[.REPORTING = 8192][.REPORTINGINI = $ptascii("8192")][.REPORTINGMODIFIED = true]',
        'S_deprecated_raw = $dz_raw(S_deprecated)',
        'S_deprecated_generated = $throwable_transition(S_deprecated, S_deprecated_raw)',
        'S_none = S[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
        'S_none_raw = $dz_raw(S_none)', 'S_none_generated = $throwable_transition(S_none, S_none_raw)']
    return bindings, [
        ('original CONST1x1 admits both visible notices and the actual generated Error',
         genuine + r' /\ z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('Deprecated-only reporting retains the genuine Error and one event while visible-two capture refuses',
         r'$call_current_valid(S_deprecated) /\ '
         r'$ob_object_final_native_method(S_deprecated) = (pobobjectreturn) /\ '
         r'~$error_handler_eligible(S_deprecated, 2) /\ ~$error_handler_eligible(S_deprecated, 8192) /\ '
         r'S_deprecated_raw.COMPLETION = S_raw.COMPLETION /\ S_deprecated_raw.RESULT = S_raw.RESULT /\ '
         r'S_deprecated_raw.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" ' + DEPRECATED + r' 6] /\ '
         r'S_deprecated_raw.EVENTS = $long_string_notices(S_deprecated, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, n_bytes_left*, z).EVENTS /\ '
         r'|S_deprecated_raw.EVENTS| = $(|S_deprecated.EVENTS| + 1) /\ '
         r'$ob_object_division_error_source(S_deprecated_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_deprecated_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_deprecated, S_deprecated_generated) = eps'),
        ('reporting zero retains the genuine Error without either event and visible-two capture refuses',
         r'$call_current_valid(S_none) /\ $ob_object_final_native_method(S_none) = (pobobjectreturn) /\ '
         r'~$error_handler_eligible(S_none, 2) /\ ~$error_handler_eligible(S_none, 8192) /\ '
         r'S_none_raw.COMPLETION = S_raw.COMPLETION /\ S_none_raw.RESULT = S_raw.RESULT /\ '
         r'S_none_raw.EVENTS = S.EVENTS /\ '
         r'S_none_raw.EVENTS = $long_string_notices(S_none, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, n_bytes_left*, z).EVENTS /\ '
         r'$ob_object_division_error_source(S_none_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_none_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_none, S_none_generated) = eps')]


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
