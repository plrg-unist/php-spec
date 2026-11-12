#!/usr/bin/env python3
"""Default NULL DIV capture preserves original constant source and raw scratch."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_default_null_division_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
CASES = {'authority': sources.DIVISION, 'profiles': sources.DIVISION,
         'source': sources.DIVISION.replace(b'$a / null', b'$a / 0')}


def start(fixture, path):
    return division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE poperand_left z) :: ptask_tail*',
        'S.RESULT = KNOWN PNULL', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        'S_left = $resolve_at($hold_task_inputs(S), poperand_left, z)',
        'S_right = $resolve_at(S_left, S.RESULT, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}']


def authority(name, fixture, path):
    if name == 'source':
        return division.start(fixture, path) + [
            'S.TODO = (BINARY_RIGHT DIVIDE poperand_left z) :: ptask_tail*',
            'S.RESULT = KNOWN (PINT 0)', 'S.ORIGIN = (porigin_operator)',
            'S_original_request = $dz_raw(S)',
            'S_original_generated = $throwable_transition(S, S_original_request)',
            'S_candidate = S[.RESULT = KNOWN PNULL]',
            'S_request = $dz_raw(S_candidate)',
            'S_generated = $throwable_transition(S_candidate, S_request)',
            'S_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}'], [
                ('a genuine original integer-zero DIV retains its capture but refuses substituted NULL',
                 r'z = 7 /\ $ob_object_division_operator(S, porigin_operator) = (DIVIDE) /\ '
                 r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
                 r'$integer_slot_rank(S_candidate, porigin_operator, [PCFIELD 1], S_candidate.RESULT) = (1) /\ '
                 r'~$integer_operand_source(S_candidate, porigin_operator, [PCFIELD 1], S_candidate.RESULT) /\ '
                 r'S_request.COMPLETION = THROWN "DivisionByZeroError" pobreturnerror.MESSAGE z /\ '
                 r'S_request.RESULT = KNOWN PNULL /\ '
                 r'S_request.EVENTS = $leading_warning(S, true, z).EVENTS /\ '
                 r'S_original_generated = S_generated /\ '
                 r'$ob_object_division_error_capture(S, S_original_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
                 r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ '
                 r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
                 r'$ob_object_division_error_capture(S_candidate, S_generated) = eps')]
    bindings = start(fixture, path)
    capture = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
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
            ('masked Warning captures without making leading conversion quiet',
             r'~$ob_object_division_operands(DIVIDE, pvalue_left, PNULL) /\ '
             r'S_masked_request.COMPLETION = THROWN "DivisionByZeroError" pobreturnerror.MESSAGE z /\ '
             r'S_masked_request.RESULT = KNOWN PNULL /\ S_masked_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_division_error_capture(S_masked, S_masked_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('hidden display preserves the same zero error and default capture',
             r'$display_state_valid(S_hidden) /\ '
             r'S_hidden_request.COMPLETION = THROWN "DivisionByZeroError" pobreturnerror.MESSAGE z /\ '
             r'S_hidden_request.RESULT = KNOWN PNULL /\ S_hidden_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_division_error_capture(S_hidden, S_hidden_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('reached buffered stdout Warning remains explicit Unsupported',
             r'$display_state_valid(S_stdout) /\ S_stdout_request.OUTPUTBLOCKED /\ '
             r'S_stdout_request.COMPLETION = UNSUPPORTED "stdout diagnostic rendering inside an output buffer" /\ '
             r'$ob_object_division_error_capture(S_stdout, S_stdout_generated) = eps')]

    bindings += [
        'S_reference = $binary_apply(S_right, DIVIDE, pvalue_left, PNULL, z)[.HELD = S.HELD]',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]', 'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5x"))',
        'S_bad = S[.STORE[n_cell] = DEFINED pvalue_bad]',
        'S_bad_generated = $throwable_transition(S_bad, $dz_raw(S_bad))',
        'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("1.5x")]]',
        'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))',
        'S_copy = S[.TODO = (BINARY_RIGHT DIVIDE (KNOWN pvalue_left) z) :: ptask_tail*]',
        'S_copy_generated = $throwable_transition(S_copy, $dz_raw(S_copy))',
        'S_int = S[.RESULT = KNOWN (PINT 0)]',
        'S_int_request = $dz_raw(S_int)',
        'S_int_generated = $throwable_transition(S_int, S_int_request)',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'S_zero = $drive_steps(S_capture, 0)']
    return bindings, [
        ('real default raw35 keeps Warning before the original NULL zero error and RHS scratch',
         r'z = 7 /\ ~$error_handler_eligible(S, 2) /\ '
         r'$coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ '
         r'$ob_object_string_value(S, pvalue_left) /\ $value_nodes(pvalue_left) = eps /\ '
         r'$ob_object_division_operator(S, porigin_operator) = (DIVIDE) /\ '
         r'$compiled_read(S, porigin_right) = (PNULL) /\ $coerce_number(PNULL) = COERCED (NINT 0) false /\ '
         r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
         r'$arithmetic_copy_swap(S, porigin_operator, DIVIDE, poperand_left, S.RESULT) = (false) /\ '
         r'~$ob_object_division_operands(DIVIDE, pvalue_left, PNULL) /\ '
         r'S_request = S_reference /\ S_request.RESULT = KNOWN PNULL /\ '
         r'S_request.COMPLETION = THROWN "DivisionByZeroError" pobreturnerror.MESSAGE z /\ '
         r'S_request.EVENTS = $leading_warning(S, true, z).EVENTS /\ S_request.EVENTS =/= S.EVENTS /\ ' + capture),
        ('charged source capture retains native roots and exact public zero-budget state',
         r'pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ '
         r'S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture')),
        ('leading numeric bytes cannot forge a valid private string identity',
         r'~$string_carrier_valid(S_bad, pvalue_bad) /\ '
         r'$ob_object_error_operand_value(S_bad, poperand_left, [PCFIELD 0], z) = eps /\ '
         r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_bad, S_bad_generated) = eps /\ '
         r'$string_carrier_valid(S_good, pvalue_bad) /\ '
         r'$ob_object_division_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('equal KNOWN copies and substituted integer zero cannot forge original NULL source',
         r'S_copy_generated = S_generated /\ '
         r'$ob_object_error_operand_value(S_copy, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
         r'$ob_object_division_error_capture(S_copy, S_copy_generated) = eps /\ '
         r'$ob_object_return_error_live(S_int_generated, pobreturnerror) /\ '
         r'S_int_request.RESULT = KNOWN (PINT 0) /\ S_int_generated = S_generated /\ '
         r'$ob_object_division_error_capture(S_int, S_int_generated) = eps'),
        ('own opcode source line current scratch events and native owner bounds remain necessary',
         r'$ob_object_division_error_capture(S[.TODO = (BINARY_RIGHT MULTIPLY poperand_left z) :: ptask_tail*], S_generated) = eps /\ '
         r'~$ob_object_division_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
         r'~$ob_object_division_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
         r'$ob_object_division_error_capture(S[.CURRENT = eps], S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
         r'$ob_object_division_error_capture(S, S_generated[.EVENTS = S.EVENTS]) = eps /\ '
         r'$ob_object_division_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]


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
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_default_null_division_warning_error_sources.py',
        'tests/semantics/output_final_division_error_sources.py',
        'tests/semantics/output_final_default_division_warning_error_sources.py',
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
