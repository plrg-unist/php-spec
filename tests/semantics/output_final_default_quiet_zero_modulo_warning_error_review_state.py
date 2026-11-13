#!/usr/bin/env python3
"""Quiet MOD zero conversion never substitutes original source or string identity."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_review_state as previous
import output_final_default_quiet_zero_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {name: sources.CASES['native-default-quiet-zero-warning-modulo-' + name]
         for name in ['null', 'string']}
CASES['nonzero'] = sources.prior.WARNING.replace(b"'1x' % 0", b"'1x' % true")
CASES['noisy-rhs'] = sources.prior.WARNING.replace(b"'1x' % 0", b"'1x' % '0.5'")
CAPTURE = previous.CAPTURE
OWN = previous.OWN
LIVE = previous.LIVE


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)',
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
        '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
        '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
        'S_warned = $leading_warning(S, true, z)', 'S_raw = $dz_raw(S)']
    if name == 'nonzero':
        bindings += [
            'S_false = S[.RESULT = KNOWN (PBOOL false)]', 'S_false_raw = $dz_raw(S_false)',
            'S_generated = $throwable_transition(S_false, S_false_raw)',
            'S_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
        return bindings, [
            ('genuine original TRUE divisor converts to1 and returns modulo0 with one Warning',
             OWN + r' /\ z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
             r'pvalue_right = PBOOL true /\ pvalue_right_compiled = PBOOL true /\ '
             r'$ob_object_modulo_integer(pvalue_right) = (1) /\ '
             r'S_raw.COMPLETION = NORMAL /\ S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS'),
            ('substituted false is a quiet zero and raises a real Error without original TRUE source authority',
             r'$ob_object_modulo_integer(PBOOL false) = (0) /\ '
             r'$ob_object_error_operand_value(S_false, S_false.RESULT, [PCFIELD 1], z) = (PBOOL false) /\ '
             r'$integer_slot_rank(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) /\ '
             r'S_false_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
             r'S_false_raw.RESULT = KNOWN (PINT 0) /\ S_false_raw.EVENTS = S_raw.EVENTS /\ ' + LIVE +
             r' /\ $ob_object_division_error_capture(S_false, S_generated) = eps')]
    bindings += [
        'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
    if name == 'noisy-rhs':
        bindings += [
            'S_mask = S[.REPORTING = 2][.REPORTINGINI = $ptascii("2")][.REPORTINGMODIFIED = true]',
            'S_mask_raw = $dz_raw(S_mask)', 'S_mask_generated = $throwable_transition(S_mask, S_mask_raw)']
        return bindings, [
            ('genuine fractional RHS retains precision loss after the sole left Warning and before zero Error',
             OWN + r' /\ z = 6 /\ pvalue_right_compiled = PSTRING ($ptascii("0.5")) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5")) /\ '
             r'$string_long($ptascii("0.5")) = STRINT 0 (STRINGPRECISIONLOSS :: eps) /\ '
             r'$ob_object_modulo_integer(pvalue_right) = eps /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
             r'S_raw.RESULT = KNOWN (PINT 0) /\ '
             r'S_raw.EVENTS = S_warned.EVENTS ++ [DIAGNOSTIC "Deprecated" ' +
             prior.value(b'Implicit conversion from float-string "0.5" to int loses precision') + r' 6] /\ ' +
             LIVE + r' /\ $ob_object_division_error_capture(S, S_generated) = eps'),
            ('Warning-only mask cannot turn noisy RHS conversion into a quiet zero operand',
             r'pfunction.CVS = eps /\ S_mask.CVS = eps /\ S_mask.ENV = eps /\ '
             r'$ob_object_string_value(S_mask, pvalue_left) /\ $ob_object_string_value(S_mask, pvalue_right) /\ '
             r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
             r'$ob_object_final_native_method(S_mask) = (pobobjectreturn) /\ $call_current_valid(S_mask) /\ '
             r'$integer_standard_object_handlers(S_mask, POBJECT pobobjectreturn.OBJECT) /\ '
             r'~$error_handler_eligible(S_mask, 2) /\ S_mask.HELD = eps /\ $tasks_nodes(S_mask.TODO) = eps /\ '
             r'S_mask.RETIREDOWNERS = eps /\ $base_nodes(S_mask.BASE) = eps /\ '
             r'$ob_object_error_operand_value(S_mask, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$ob_object_error_operand_value(S_mask, S_mask.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
             r'$integer_operand_source(S_mask, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
             r'$integer_operand_source(S_mask, porigin_operator, [PCFIELD 1], S_mask.RESULT) /\ '
             r'$integer_slot_rank(S_mask, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
             r'$integer_slot_rank(S_mask, porigin_operator, [PCFIELD 1], S_mask.RESULT) = (1) /\ '
             r'S_mask_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
             r'S_mask_raw.RESULT = KNOWN (PINT 0) /\ '
             r'S_mask_raw.EVENTS = $leading_warning(S_mask, true, z).EVENTS /\ '
             r'S_mask_raw.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6] /\ '
             r'$ob_object_division_error_source(S_mask_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_mask_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_mask, S_mask_generated) = eps')]
    original = 'PNULL' if name == 'null' else 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'
    compiled = 'PNULL' if name == 'null' else 'PSTRING ($ptascii("0"))'
    checks = [
        ('own original quiet-zero CONST is distinct from raw converted PINT0 and captures the actual Error',
         OWN + r' /\ z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
         'pvalue_right = ' + original + r' /\ pvalue_right_compiled = ' + compiled + r' /\ '
         r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
         r'pvalue_right =/= PINT 0 /\ $ob_object_modulo_integer(pvalue_right) = (0) /\ '
         r'$value_nodes(pvalue_right) = eps /\ '
         r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
         r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS /\ ' + LIVE + r' /\ ' + CAPTURE)]
    if name == 'null':
        bindings += [
            'S_false = S[.RESULT = KNOWN (PBOOL false)]', 'S_false_raw = $dz_raw(S_false)',
            'S_false_generated = $throwable_transition(S_false, S_false_raw)']
        checks += [
            ('false substitution preserves the complete generated Error but cannot replace original NULL',
             r'$ob_object_modulo_integer(PBOOL false) = (0) /\ '
             r'$ob_object_error_operand_value(S_false, S_false.RESULT, [PCFIELD 1], z) = (PBOOL false) /\ '
             r'$integer_slot_rank(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) /\ '
             r'S_false_raw = S_raw /\ S_false_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_false, S_false_generated) = eps')]
    else:
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
            'S_request = S[.RESULT = KNOWN pvalue_request][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]]',
            'S_request_raw = $dz_raw(S_request)',
            'S_request_generated = $throwable_transition(S_request, S_request_raw)']
        checks += [
            ('valid same-byte quiet request RHS retains Error and converted scratch but lacks its own CONST identity',
             r'$ob_object_string_value(S_request, pvalue_request) /\ $ob_object_modulo_integer(pvalue_request) = (0) /\ '
             r'$ob_object_error_operand_value(S_request, S_request.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
             r'$integer_slot_rank(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) /\ '
             r'S_request_raw.EVENTS = S_raw.EVENTS /\ S_request_raw.RESULT = KNOWN (PINT 0) /\ '
             r'$ob_object_return_error_live(S_request_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_request, S_request_generated) = eps')]
    return bindings, checks


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
        'tests/semantics/output_final_default_quiet_zero_modulo_warning_error_sources.py',
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
