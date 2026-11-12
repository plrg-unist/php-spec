#!/usr/bin/env python3
"""Quiet divisor capture preserves original types, carriers and diagnostic bounds."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_null_division_warning_error_review_state as previous
import output_final_default_scalar_zero_division_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = division.prior
PREFIX = previous.PREFIX
CASES = {name: sources.CASES['native-default-scalar-zero-warning-division-' + name]
         for name in ['false', 'float-positive', 'string-integer']}
CASES['nonzero'] = CASES['false'].replace(b'$a / false', b'$a / 1')
CASES['noisy'] = CASES['false'].replace(b'$a / false', b"$a / '0x'")
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
AUTHORITY = (r'z = 7 /\ $string_bytes(pvalue_left) = ($ptascii("1.5x")) /\ '
             r'$coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ '
             r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$compiled_read(S, porigin_right) = (pvalue_compiled) /\ '
             r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_compiled) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
             r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
             r'~$error_handler_eligible(S, 2)')
ZERO = (r'S_raw.RESULT = KNOWN pvalue_right /\ '
        r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ '
        r'S_raw.EVENTS = $leading_warning(S, true, z).EVENTS /\ '
        r'$ob_object_return_error_live(S_generated, pobreturnerror)')


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE poperand_left z) :: ptask_tail*',
        'poperand_left = VARIABLE n_left* z_left',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_right) = (pvalue_compiled)',
        '$lookup(S.ENV, n_left*) = (n_cell)', 'S.STORE[n_cell] = DEFINED pvalue_left',
        '$coerce_number(pvalue_right) = COERCED pnumber_right b_right',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)']
    if name == 'nonzero':
        return bindings, [
            ('a genuine nonzero CONST passes quiet admission but cannot mint a zero-error capture',
             AUTHORITY + r' /\ pvalue_right = PINT 1 /\ ~b_right /\ '
             r'$ob_object_division_number(pvalue_right) /\ ~$num_zero(pnumber_right) /\ '
             r'S_raw.COMPLETION = NORMAL /\ S_raw.RESULT = KNOWN (PFLOAT 4609434218613702656) /\ '
             r'S_raw.EVENTS = $leading_warning(S, true, z).EVENTS /\ '
             r'S_generated = S_raw /\ $ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += ['S_generated.COMPLETION = THROWING n_exception',
                 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}']
    if name == 'noisy':
        return bindings, [
            ('a genuine leading-numeric RHS retains two ordered Warnings through default capture',
             AUTHORITY + r' /\ b_right /\ $num_zero(pnumber_right) /\ '
             r'pvalue_compiled = PSTRING ($ptascii("0x")) /\ $ob_object_string_value(S, pvalue_right) /\ '
             r'~$ob_object_division_number(pvalue_right) /\ '
             r'S_raw.RESULT = KNOWN pvalue_right /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ '
             r'S_raw.EVENTS = $leading_warning($leading_warning(S, true, z), true, z).EVENTS /\ '
             r'S_raw.EVENTS =/= $leading_warning(S, true, z).EVENTS /\ '
             r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')]
    if name in ['false', 'float-positive']:
        original, replacement = ('PBOOL false', 'PNULL') if name == 'false' else (
            'PFLOAT 0', 'PFLOAT 9223372036854775808')
        bindings += ['S_changed = S[.RESULT = KNOWN (' + replacement + ')]',
                     'S_changed_raw = $dz_raw(S_changed)',
                     'S_changed_generated = $throwable_transition(S_changed, S_changed_raw)']
        return bindings, [
            ('the original typed zero retains its own compiled source, Warning and exact capture',
             AUTHORITY + r' /\ pvalue_right = ' + original + r' /\ ~b_right /\ '
             r'$num_zero(pnumber_right) /\ $ob_object_division_number(pvalue_right) /\ ' + ZERO + r' /\ ' + CAPTURE),
            ('an equal materialized Error cannot authenticate a substituted zero type or sign',
             r'S_changed_raw.RESULT = KNOWN (' + replacement + r') /\ '
             r'S_changed_generated = S_generated /\ '
             r'$ob_object_division_number(' + replacement + r') /\ '
             r'$integer_slot_rank(S_changed, porigin_operator, [PCFIELD 1], S_changed.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_changed, porigin_operator, [PCFIELD 1], S_changed.RESULT) /\ '
             r'$ob_object_division_error_capture(S_changed, S_changed_generated) = eps')]

    bindings += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
        'S_bad = S[.RESULT = KNOWN pvalue_request]',
        'S_valid = S_bad[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]]',
        'S_valid_generated = $throwable_transition(S_valid, $dz_raw(S_valid))',
        'S_masked = S[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
        'S_masked_raw = $dz_raw(S_masked)',
        'S_masked_generated = $throwable_transition(S_masked, S_masked_raw)',
        'S_hidden = S[.DISPLAYINI = ($ptascii("0"))][.DISPLAYMODIFIED = true]',
        'S_hidden_raw = $dz_raw(S_hidden)',
        'S_hidden_generated = $throwable_transition(S_hidden, S_hidden_raw)',
        'S_stdout = S[.DISPLAYINI = ($ptascii("stdout"))][.DISPLAYMODIFIED = true]',
        'S_stdout_raw = $dz_raw(S_stdout)',
        'S_stdout_generated = $throwable_transition(S_stdout, S_stdout_raw)']
    return bindings, [
        ('the original numeric string keeps its interned carrier and raw scratch through materialization',
         AUTHORITY + r' /\ pvalue_compiled = PSTRING ($ptascii("0")) /\ '
         r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0")) /\ '
         r'$ob_object_string_value(S, pvalue_right) /\ ~b_right /\ $num_zero(pnumber_right) /\ '
         + ZERO + r' /\ ' + CAPTURE),
        ('equal bytes with invalid or valid request identity cannot replace the original compiled carrier',
         r'$string_plain(pvalue_request) = $string_plain(pvalue_right) /\ '
         r'~$ob_object_string_value(S_bad, pvalue_request) /\ '
         r'$ob_object_division_error_capture(S_bad, S_generated) = eps /\ '
         r'$ob_object_string_value(S_valid, pvalue_request) /\ '
         r'$ob_object_division_number(pvalue_request) /\ '
         r'$ob_object_return_error_live(S_valid_generated, pobreturnerror) /\ '
         r'~$integer_operand_source(S_valid, porigin_operator, [PCFIELD 1], S_valid.RESULT) /\ '
         r'$ob_object_division_error_capture(S_valid, S_valid_generated) = eps'),
        ('mask and hidden display preserve capture while buffered stdout Warning remains Unsupported',
         r'S_masked_raw.RESULT = KNOWN pvalue_right /\ S_masked_raw.EVENTS = S.EVENTS /\ '
         r'$ob_object_division_error_capture(S_masked, S_masked_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'S_hidden_raw.RESULT = KNOWN pvalue_right /\ S_hidden_raw.EVENTS = S.EVENTS /\ '
         r'$ob_object_division_error_capture(S_hidden, S_hidden_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'S_stdout_raw.OUTPUTBLOCKED /\ '
         r'S_stdout_raw.COMPLETION = UNSUPPORTED "stdout diagnostic rendering inside an output buffer" /\ '
         r'$ob_object_division_error_capture(S_stdout, S_stdout_generated) = eps'),
        ('current scope, native owners, source line, original materialization and Warning events remain required',
         r'$heap_count(HCELL n_cell, $machine_roots(S)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_generated)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_generated)) = 1 /\ '
         r'$ob_object_division_error_capture(S[.CURRENT = eps], S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps /\ '
         r'~$ob_object_division_error_source(S_generated, pfunction, pobreturnerror[.LINE = $(z + 1)]) /\ '
         r'$ob_object_division_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
         r'$ob_object_division_error_capture(S, S_generated[.EVENTS = S.EVENTS]) = eps')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output; out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / name for name in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_default_scalar_zero_division_warning_error_sources.py',
        'tests/semantics/output_final_default_null_division_warning_error_sources.py',
        'tests/semantics/output_final_default_division_warning_error_sources.py',
        'tests/semantics/output_final_default_null_division_warning_error_review_state.py',
        'tests/semantics/output_final_division_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py']] + [Path(__file__)]
    fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False, 'before': fingerprint()}
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
            inputs = lambda: {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
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
            assert record['inputs_before'] == record['inputs_after'], 'fixture inputs changed'
            record['passed'] = True
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(name, len(checks), record['seconds'], flush=True)
        report['after'] = fingerprint()
        assert report['before'] == report['after'], 'watched inputs changed'
        assert report['revision'] == head(), 'revision changed'
        report['passed'] = all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if 'after' not in report:
            report['after'] = fingerprint()
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
