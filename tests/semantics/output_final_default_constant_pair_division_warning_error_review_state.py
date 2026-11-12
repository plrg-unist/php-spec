#!/usr/bin/env python3
"""Empty-CV CONST pairs retain exact source identity and their native error."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_left_division_warning_error_review_state as previous
import output_final_default_constant_pair_division_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = division.prior
PREFIX = previous.PREFIX
CASES = {name: sources.CASES['native-default-constant-pair-warning-division-' + name]
         for name in ['integer', 'leading-string']}
CASES['unused-cvs'] = previous.CASES['constant-pair']
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
AUTHORITY = (r'z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
             r'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_compiled) /\ '
             r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
             r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
             r'$ob_object_string_value(S, pvalue_right) /\ ~$error_handler_eligible(S, 2) /\ b_right /\ '
             r'S_raw.RESULT = KNOWN pvalue_right /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ '
             r'S_raw.EVENTS = $leading_warning($leading_warning(S, b_left, z), b_right, z).EVENTS /\ '
             r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
             r'$heap_count(HOBJECT n_object, $machine_roots(S_generated)) = 2 /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_generated)) = 1')


def authority(name, fixture, path):
    if name == 'unused-cvs':
        return previous.authority('constant-pair', fixture, path)
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_left) = (pvalue_compiled)',
        '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
        '$coerce_number(pvalue_left) = COERCED pnumber_left b_left',
        '$coerce_number(pvalue_right) = COERCED pnumber_right b_right',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}']
    checks = [
        ('the actual empty-CV method authenticates both original CONST slots and the materialized native Error',
         AUTHORITY + r' /\ ' + CAPTURE),
        ('capture retains exact Warning projection scratch current context and nonowning bounds',
         r'$ob_object_division_error_capture(S, S_generated[.EVENTS = S.EVENTS]) = eps /\ '
         r'$ob_object_division_error_capture(S, S_generated[.RESULT = KNOWN pvalue_right]) = eps /\ '
         r'$ob_object_division_error_capture(S[.CURRENT = eps], S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S[.TODO = (BINARY_RIGHT MULTIPLY (KNOWN pvalue_left) z) :: ptask_tail*], S_generated) = eps')]
    if name == 'integer':
        bindings += [
            'S_wrong = S[.TODO = (BINARY_RIGHT DIVIDE (KNOWN (PINT 2)) z) :: ptask_tail*]',
            'S_wrong_generated = $throwable_transition(S_wrong, $dz_raw(S_wrong))',
            'S_line = S[.TODO = (BINARY_RIGHT DIVIDE (KNOWN pvalue_left) $(z + 1)) :: ptask_tail*]',
            'S_line_generated = $throwable_transition(S_line, $dz_raw(S_line))']
        checks += [
            ('a different integer preserves the equal Error but cannot replace its original compiled left value',
             r'pvalue_left = PINT 1 /\ ~b_left /\ S_wrong_generated = S_generated /\ '
             r'$ob_object_error_operand_value(S_wrong, KNOWN (PINT 2), [PCFIELD 0], z) = (PINT 2) /\ '
             r'$integer_slot_rank(S_wrong, porigin_operator, [PCFIELD 0], KNOWN (PINT 2)) = (1) /\ '
             r'~$integer_operand_source(S_wrong, porigin_operator, [PCFIELD 0], KNOWN (PINT 2)) /\ '
             r'$ob_object_division_error_capture(S_wrong, S_wrong_generated) = eps'),
            ('a real error raised on a changed operation line lacks the original compiled RHS line',
             r'$code_expression_at_source(S_line, porigin_operator, [PCFIELD 1]) = (6) /\ '
             r'S_line_generated.COMPLETION = THROWING n_exception /\ '
             r'$throwable_field(S_line_generated, n_exception, "line") = PINT 7 /\ '
             r'$ob_object_division_error_capture(S_line, S_line_generated) = eps')]
    else:
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5x"))',
            'S_valid = S[.TODO = (BINARY_RIGHT DIVIDE (KNOWN pvalue_request) z) :: ptask_tail*][.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5x")]]',
            'S_valid_raw = $dz_raw(S_valid)',
            'S_valid_generated = $throwable_transition(S_valid, S_valid_raw)',
            'pvalue_request_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0x"))',
            'S_right = S[.RESULT = KNOWN pvalue_request_right][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0x")]]',
            'S_right_raw = $dz_raw(S_right)',
            'S_right_generated = $throwable_transition(S_right, S_right_raw)']
        checks += [
            ('a valid same-byte request left carrier cannot replace its own interned CONST',
             r'b_left /\ pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
             r'$ob_object_string_value(S_valid, pvalue_request) /\ '
             r'$ob_object_error_operand_value(S_valid, KNOWN pvalue_request, [PCFIELD 0], z) = (pvalue_request) /\ '
             r'$integer_slot_rank(S_valid, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) = (1) /\ '
             r'~$integer_operand_source(S_valid, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) /\ '
             r'S_valid_raw.EVENTS = S_raw.EVENTS /\ '
             r'$ob_object_return_error_live(S_valid_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_valid, S_valid_generated) = eps'),
            ('a valid same-byte request right carrier keeps real warnings and Error without compiled RHS authority',
             r'$ob_object_string_value(S_right, pvalue_request_right) /\ '
             r'$ob_object_error_operand_value(S_right, S_right.RESULT, [PCFIELD 1], z) = (pvalue_request_right) /\ '
             r'$integer_slot_rank(S_right, porigin_operator, [PCFIELD 1], S_right.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_right, porigin_operator, [PCFIELD 1], S_right.RESULT) /\ '
             r'S_right_raw.RESULT = KNOWN pvalue_request_right /\ S_right_raw.EVENTS = S_raw.EVENTS /\ '
             r'$ob_object_return_error_live(S_right_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_right, S_right_generated) = eps')]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output; out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/semantics/modules.json',
        'tests/semantics/output_final_default_constant_pair_division_warning_error_sources.py',
        'tests/semantics/output_final_default_constant_left_division_warning_error_sources.py',
        'tests/semantics/output_final_default_division_operand_warning_error_sources.py',
        'tests/semantics/output_final_default_cv_zero_division_warning_error_sources.py',
        'tests/semantics/output_final_default_division_warning_error_sources.py',
        'tests/semantics/output_final_division_error_sources.py',
        'tests/semantics/output_final_default_null_division_warning_error_review_state.py',
        'tests/semantics/output_final_default_null_division_warning_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
    watched += [Path(__file__), Path(previous.__file__), Path(previous.previous.__file__)]
    fingerprint = lambda: {str(p): prior.common.sha(p) for p in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'module_count': len(modules), 'fixture_timeout_seconds': 300,
              'source_agreement_credit': 0, 'before': fingerprint(), 'records': [], 'passed': False}
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
