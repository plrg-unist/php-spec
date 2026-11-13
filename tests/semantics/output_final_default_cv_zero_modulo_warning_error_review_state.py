#!/usr/bin/env python3
"""Quiet-zero MOD RHS CVs retain compiled lines, private cells and string identity."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_quiet_zero_modulo_warning_error_review_state as previous
import output_final_default_cv_zero_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {name: sources.CASES['native-default-cv-zero-warning-modulo-' + name]
         for name in sources.VALUES}


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = VARIABLE n_right* z_right', 'S.ORIGIN = (porigin_operator)',
        '$lookup(S.ENV, n_right*) = (n_cell)',
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        'S_warned = $leading_warning(S, true, z)', 'S_raw = $dz_raw(S)',
        'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
    if name == 'integer':
        bindings += [
            'S_line = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
            'S_line_raw = $dz_raw(S_line)',
            'S_line_generated = $throwable_transition(S_line, S_line_raw)',
            'S_ref = S[.REFCELLS = S.REFCELLS ++ [n_cell]]',
            'S_ref_raw = $dz_raw(S_ref)',
            'S_ref_generated = $throwable_transition(S_ref, S_ref_raw)']
        return bindings, [
            ('genuine own right CV retains its compiled line and quiet-zero capture',
             r'n_right* = $ptascii("b") /\ z_right = 8 /\ z = 8 /\ '
             r'pvalue_right = PINT 0 /\ S.STORE[n_cell] = DEFINED (PINT 0) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'$ob_object_modulo_integer(pvalue_right) = (0) /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8 /\ '
             r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS /\ ' +
             previous.LIVE + r' /\ ' + previous.CAPTURE),
            ('forged CV read line preserves the complete Error but loses compiled-child authority',
             r'$integer_slot_rank(S_line, porigin_operator, [PCFIELD 1], S_line.RESULT) = (8) /\ '
             r'~$integer_operand_source(S_line, porigin_operator, [PCFIELD 1], S_line.RESULT) /\ '
             r'$ob_object_error_operand_value(S_line, S_line.RESULT, [PCFIELD 1], z) = eps /\ '
             r'S_line_raw = S_raw /\ S_line_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_line, S_line_generated) = eps'),
            ('reference-marked same right cell preserves source and Error but is outside the private reader',
             r'$integer_operand_source(S_ref, porigin_operator, [PCFIELD 1], S_ref.RESULT) /\ '
             r'$integer_slot_rank(S_ref, porigin_operator, [PCFIELD 1], S_ref.RESULT) = (8) /\ '
             r'$ob_object_error_operand_value(S_ref, S_ref.RESULT, [PCFIELD 1], z) = eps /\ '
             r'S_ref_raw = S_raw[.REFCELLS = S_ref.REFCELLS] /\ '
             r'S_ref_generated = S_generated[.REFCELLS = S_ref.REFCELLS] /\ '
             r'$ob_object_division_error_source(S_ref_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_ref_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_ref, S_ref_generated) = eps')]
    bindings += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
        'S_request = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED pvalue_request)][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]]',
        'S_request_raw = $dz_raw(S_request)',
        'S_request_generated = $throwable_transition(S_request, S_request_raw)',
        'S_invalid = S_request[.STRINGDATA = S.STRINGDATA]']
    return bindings, [
        ('own variable source permits a valid same-byte request carrier stored in the private cell',
         r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0")) /\ '
         r'$integer_operand_source(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) /\ '
         r'$integer_slot_rank(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) = (8) /\ '
         r'$ob_object_string_value(S_request, pvalue_request) /\ '
         r'$ob_object_error_operand_value(S_request, S_request.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
         r'$ob_object_modulo_integer(pvalue_request) = (0) /\ '
         r'S_request_raw.COMPLETION = S_raw.COMPLETION /\ '
         r'S_request_raw.RESULT = S_raw.RESULT /\ S_request_raw.EVENTS = S_raw.EVENTS /\ '
         r'$ob_object_division_error_capture(S_request, S_request_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('same-byte carrier without its request-data identity fails the private read',
         r'$integer_operand_source(S_invalid, porigin_operator, [PCFIELD 1], S_invalid.RESULT) /\ '
         r'$integer_slot_rank(S_invalid, porigin_operator, [PCFIELD 1], S_invalid.RESULT) = (8) /\ '
         r'$ob_object_modulo_integer(pvalue_request) = (0) /\ '
         r'~$ob_object_string_value(S_invalid, pvalue_request) /\ '
         r'$ob_object_error_operand_value(S_invalid, S_invalid.RESULT, [PCFIELD 1], z) = eps')]


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
        'tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_quiet_zero_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_quiet_zero_modulo_warning_error_review_state.py',
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
