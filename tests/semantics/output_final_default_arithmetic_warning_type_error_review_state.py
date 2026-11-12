#!/usr/bin/env python3
"""Default arithmetic Warning capture preserves configuration and physical order."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_default_arithmetic_warning_type_error_sources as sources
import output_final_quiet_arithmetic_type_coercion_review_state as quiet

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
SWAPPED = sources.MULTIPLY.replace(b"$a = '1.5x'", b"$a = 'X'").replace(
    b"$a * 'X'", b"'1.5x' * $a")
REFERENCE = sources.ADD.replace(b"        return $a + 'X';",
                                 b"        $r =& $a;\n        return $a + 'X';")
CASES = {'add': sources.ADD, 'multiply-order': SWAPPED,
         'normal': sources.NORMAL, 'reference': REFERENCE,
         'legacy-subtract': sources.SUBTRACT}
assert PREFIX == quiet.PREFIX and sources.SUBTRACT == quiet.sources.NOISY


def inputs(fixture, path):
    return division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT pbin poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
        'S_left = $resolve_at($hold_task_inputs(S), poperand_left, z)',
        'S_left.RESULT = KNOWN pvalue_left',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_right.RESULT = KNOWN pvalue_right',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)']


def rejection():
    return ['S_request.COMPLETION = THROWN "TypeError" preqbytes_message z',
            'S_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE preqbytes_message, LINE z}']


def add(fixture, path):
    bindings = inputs(fixture, path) + rejection() + [
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'S_other = S[.TODO = (BINARY_RIGHT SUBTRACT poperand_left z) :: ptask_tail*]',
        'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
        'pobreturnerror_other = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string - string")]',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5x"))',
        'S_bad = S[.STORE[n_cell] = DEFINED pvalue_bad]',
        'S_bad_request = $dz_raw(S_bad)',
        'S_bad_generated = $throwable_transition(S_bad, S_bad_request)',
        'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("1.5x")]]',
        'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))',
        'S_masked = S[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
        'S_masked_request = $dz_raw(S_masked)',
        'S_masked_generated = $throwable_transition(S_masked, S_masked_request)',
        'S_hidden = S[.DISPLAYINI = ($ptascii("0"))][.DISPLAYMODIFIED = true]',
        'S_hidden_request = $dz_raw(S_hidden)',
        'S_hidden_generated = $throwable_transition(S_hidden, S_hidden_request)',
        'S_stdout = S[.DISPLAYINI = ($ptascii("stdout"))][.DISPLAYMODIFIED = true]',
        'S_stdout_request = $dz_raw(S_stdout)',
        'S_stdout_generated = $throwable_transition(S_stdout, S_stdout_request)']
    checks = [
        ('actual Warning and RHS scratch authenticate nonowning capture',
         r'pbin = ADD /\ z = 7 /\ ~$error_handler_eligible(S, 2) /\ '
         r'$string_bytes(pvalue_left) = ($ptascii("1.5x")) /\ '
         r'$coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ '
         r'$string_bytes(pvalue_right) = ($ptascii("X")) /\ $coerce_number(pvalue_right) = BADNUMBER /\ '
         r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left) /\ '
         r'$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right) /\ '
         r'$arithmetic_copy_swap(S, porigin_operator, ADD, poperand_left, poperand_right) = (false) /\ '
         r'S_request.RESULT = KNOWN pvalue_right /\ '
         r'S_request.EVENTS = S.EVENTS ++ [$event_source(S, DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) z)] /\ '
         r'preqbytes_message = $ptascii("Unsupported operand types: string + string") /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
        ('coherent opcode and normalized successor substitutions refuse',
         r'S_other_generated.COMPLETION = THROWING n_exception /\ $call_current_valid(S_other) /\ '
         r'$ob_object_arithmetic_type_error_source(S_other_generated, pfunction, pobreturnerror_other) /\ '
         r'$ob_object_return_error_live(S_other_generated, pobreturnerror_other) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S.EVENTS]) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps'),
        ('leading bytes cannot forge a live private string identity',
         r'~$string_carrier_valid(S_bad, pvalue_bad) /\ '
         r'$ob_object_error_operand_value(S_bad, poperand_left, [PCFIELD 0], z) = eps /\ '
         r'S_bad_request.COMPLETION = THROWN "TypeError" preqbytes_message z /\ '
         r'S_bad_request.EVENTS = S_request.EVENTS /\ '
         r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_bad, S_bad_generated) = eps /\ '
         r'$string_carrier_valid(S_good, pvalue_bad) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('masked default Warning keeps the TypeError and capture',
         r'S_masked_request.COMPLETION = THROWN "TypeError" preqbytes_message z /\ '
         r'S_masked_request.RESULT = KNOWN pvalue_right /\ S_masked_request.EVENTS = S.EVENTS /\ '
         r'$ob_object_arithmetic_type_error_capture(S_masked, S_masked_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('display suppression admits while buffered stdout remains Unsupported',
         r'$display_state_valid(S_hidden) /\ $display_state_valid(S_stdout) /\ '
         r'S_hidden_request.COMPLETION = THROWN "TypeError" preqbytes_message z /\ '
         r'S_hidden_request.EVENTS = S.EVENTS /\ '
         r'$ob_object_arithmetic_type_error_capture(S_hidden, S_hidden_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'S_stdout_request.COMPLETION = UNSUPPORTED "stdout diagnostic rendering inside an output buffer" /\ '
         r'S_stdout_request.OUTPUTBLOCKED /\ '
         r'$ob_object_arithmetic_type_error_capture(S_stdout, S_stdout_generated) = eps')]
    return bindings, checks


def swapped(fixture, path):
    bindings = inputs(fixture, path) + rejection() + [
        'S_physical_request = $binary_apply(S_right[.TODO = ptask_tail*][.HELD = S.HELD], MULTIPLY, pvalue_right, pvalue_left, z)',
        'S_physical_generated = $throwable_transition(S, S_physical_request)']
    return bindings, [
        ('real raw source and live Error cannot override swapped MUL exclusion',
         r'pbin = MULTIPLY /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
         r'$arithmetic_copy_swap(S, porigin_operator, MULTIPLY, poperand_left, poperand_right) = (true) /\ '
         r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left) /\ '
         r'$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right) /\ '
         r'S_request.EVENTS = S.EVENTS ++ [$event_source(S, DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) z)] /\ '
         r'$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = eps /\ '
         r'$source_exception_transition(S, S_generated) = S_generated'),
        ('coherent physical-first failure candidate also grants no receipt',
         r'S_physical_request.COMPLETION = THROWN "TypeError" preqbytes_message z /\ '
         r'S_physical_request.EVENTS = S.EVENTS /\ '
         r'S_physical_generated.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_arithmetic_type_error_source(S_physical_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_physical_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_physical_generated) = eps')]


def authority(name, fixture, path):
    return swapped(fixture, path) if name == 'multiply-order' else add(fixture, path)


def normal(fixture, path):
    return inputs(fixture, path), [
        ('normal leading arithmetic preserves Warning and3.5 without a receipt',
         r'S_request.COMPLETION = NORMAL /\ S_generated = S_request /\ '
         r'S_request.RESULT = KNOWN (PFLOAT 4615063718147915776) /\ '
         r'S_request.EVENTS = S.EVENTS ++ [$event_source(S, DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) z)] /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = eps /\ '
         r'$source_exception_transition(S, S_generated) = S_generated /\ pobobjectreturn.SOURCE = eps')]


def reference(fixture, path):
    return inputs(fixture, path) + rejection(), [
        ('actual shared-reference reads retain the existing capture boundary',
         r'n_cell <- S.REFCELLS /\ $heap_count(HCELL n_cell, $machine_roots(S)) = 2 /\ '
         r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = eps /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = eps /\ '
         r'$source_exception_transition(S, S_generated) = S_generated /\ pobobjectreturn.SOURCE = eps')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / name for name in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_default_arithmetic_warning_type_error_sources.py',
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
            controls = {'normal': normal, 'reference': reference, 'legacy-subtract': quiet.noisy}
            bindings, checks = (controls[name](checked['fixture'], path) if name in controls else
                                authority(name, checked['fixture'], path))
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            inputs_before = {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': inputs_before, 'passed': False}
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
                record.update(seconds=time.monotonic() - started,
                              inputs_after={str(item): prior.common.sha(item) for item in [path, cache, fixture]})
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
