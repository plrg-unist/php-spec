#!/usr/bin/env python3
"""A BAD physical first operand skips its leading lexical left without new authority."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_arithmetic_warning_type_error_review_state as previous
import output_final_swapped_left_arithmetic_type_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
PREFIX = previous.PREFIX
CASES = dict.fromkeys(('authority', 'profiles', 'legacy58'), sources.MULTIPLY)
assert sources.MULTIPLY == previous.CASES['multiply-order']


def authority(name, fixture, path):
    if name == 'legacy58':
        return previous.swapped(fixture, path)
    bindings = previous.inputs(fixture, path) + previous.rejection()
    capture = r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
    if name == 'profiles':
        bindings += [
            'S_masked = S[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
            'S_masked_request = $dz_raw(S_masked)',
            'S_masked_generated = $throwable_transition(S_masked, S_masked_request)',
            'S_hidden = S[.DISPLAYINI = ($ptascii("0"))][.DISPLAYMODIFIED = true]',
            'S_hidden_request = $dz_raw(S_hidden)',
            'S_hidden_generated = $throwable_transition(S_hidden, S_hidden_request)',
            'S_stdout = S[.DISPLAYINI = ($ptascii("stdout"))][.DISPLAYMODIFIED = true]',
            'S_stdout_request = $dz_raw(S_stdout)',
            'S_stdout_generated = $throwable_transition(S_stdout, S_stdout_request)']
        return bindings, [
            ('masked reporting preserves actual first-BAD dispatch while the old quiet arm stays false',
             r'$arithmetic_copy_swap(S_masked, porigin_operator, MULTIPLY, poperand_left, poperand_right) = (true) /\ '
             r'$default_multiply_first_bad_error(S_masked, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
             r'~$quiet_multiply_error(S_masked, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
             r'S_masked_request.COMPLETION = THROWN "TypeError" pobreturnerror.MESSAGE z /\ '
             r'S_masked_request.RESULT = KNOWN pvalue_right /\ S_masked_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_arithmetic_type_error_capture(S_masked, S_masked_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('display suppression preserves the same quiet physical Error',
             r'$display_state_valid(S_hidden) /\ '
             r'S_hidden_request.COMPLETION = THROWN "TypeError" pobreturnerror.MESSAGE z /\ '
             r'S_hidden_request.RESULT = KNOWN pvalue_right /\ S_hidden_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_arithmetic_type_error_capture(S_hidden, S_hidden_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('skipped Warning reaches no buffered stdout diagnostic renderer',
             r'$display_state_valid(S_stdout) /\ ~S_stdout_request.OUTPUTBLOCKED /\ '
             r'S_stdout_request.COMPLETION = THROWN "TypeError" pobreturnerror.MESSAGE z /\ '
             r'S_stdout_request.RESULT = KNOWN pvalue_right /\ S_stdout_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_arithmetic_type_error_capture(S_stdout, S_stdout_generated) = ((pobobjectreturn, pobreturnerror))')]

    bindings += [
        'S_physical = $binary_apply(S_right, MULTIPLY, pvalue_right, pvalue_left, z)[.HELD = S.HELD]',
        'S_lexical = $binary_apply(S_right, MULTIPLY, pvalue_left, pvalue_right, z)[.HELD = S.HELD]',
        'S_lexical_generated = $throwable_transition(S, S_lexical)',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]', 'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("X"))',
        'S_bad = S[.STORE[n_cell] = DEFINED pvalue_bad]',
        'S_bad_generated = $throwable_transition(S_bad, $dz_raw(S_bad))',
        'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("X")]]',
        'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))',
        'S_copy = S[.RESULT = KNOWN pvalue_right]',
        'S_copy_generated = $throwable_transition(S_copy, $dz_raw(S_copy))',
        'S_other = S[.TODO = (BINARY_RIGHT ADD poperand_left z) :: ptask_tail*]',
        'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
        'pobreturnerror_other = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string + string")]',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'S_zero = $drive_steps(S_capture, 0)']
    return bindings, [
        ('genuine physical first-BAD dispatch skips the leading literal and keeps original RHS scratch',
         r'pbin = MULTIPLY /\ z = 7 /\ '
         r'$coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ '
         r'$coerce_number(pvalue_right) = BADNUMBER /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
         r'$arithmetic_copy_swap(S, porigin_operator, MULTIPLY, poperand_left, poperand_right) = (true) /\ '
         r'~$quiet_multiply_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
         r'~$default_multiply_warning_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
         r'$default_multiply_first_bad_error(S_right, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
         r'S_request = S_physical /\ S_request.RESULT = KNOWN pvalue_right /\ '
         r'S_request.COMPLETION = THROWN "TypeError" pobreturnerror.MESSAGE z /\ '
         r'S_request.EVENTS = S.EVENTS /\ ' + capture),
        ('real charged capture retains native owners without metadata roots',
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ '
         r'S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture')),
        ('pure BAD classification cannot authorize an invalid string carrier',
         r'~$string_carrier_valid(S_bad, pvalue_bad) /\ '
         r'~$default_multiply_first_bad_error(S_bad, poperand_left, poperand_right, pvalue_left, pvalue_bad, z) /\ '
         r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_bad, S_bad_generated) = eps /\ '
         r'$string_carrier_valid(S_good, pvalue_bad) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('equal KNOWN copies exchanged values and lexical successors lose physical source authority',
         r'$ob_object_return_error_live(S_copy_generated, pobreturnerror) /\ '
         r'$arithmetic_copy_swap(S_copy, porigin_operator, MULTIPLY, poperand_left, KNOWN pvalue_right) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S_copy, S_copy_generated) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S_copy, S_generated) = eps /\ '
         r'~$default_multiply_first_bad_error(S, poperand_left, poperand_right, pvalue_right, pvalue_left, z) /\ '
         r'S_lexical.EVENTS = $leading_warning(S, true, z).EVENTS /\ S_lexical.EVENTS =/= S.EVENTS /\ '
         r'$ob_object_return_error_live(S_lexical_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_lexical_generated) = eps'),
        ('own opcode current line scratch events and native root bounds remain necessary',
         r'$ob_object_return_error_live(S_other_generated, pobreturnerror_other) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps /\ '
         r'~$default_multiply_first_bad_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, $(z + 1)) /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
         r'$ob_object_arithmetic_type_error_capture(S[.CURRENT = eps], S_generated) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN pvalue_left]) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]


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
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_swapped_left_arithmetic_type_error_sources.py',
        'tests/semantics/output_final_default_arithmetic_warning_type_error_review_state.py',
        'tests/semantics/output_final_default_arithmetic_warning_type_error_sources.py',
        'tests/semantics/output_final_quiet_arithmetic_type_coercion_review_state.py',
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
                assert result.returncode == 0 and not result.stderr, (result.returncode, result.stderr)
                record['observed'] = json.loads(result.stdout)
                assert record['observed'] == [True] * len(checks), record['observed']
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record.update(seconds=time.monotonic() - started, inputs_after=inputs())
            assert record['inputs_before'] == record['inputs_after'], 'fixture inputs changed'
            record['passed'] = True
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
