#!/usr/bin/env python3
"""MOD Warning capture preserves source identity and rejects masked precision loss."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_state as author
import output_final_default_constant_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = author.division
prior = author.prior
PREFIX = author.PREFIX
CASES = {'authority': sources.WARNING, 'nonzero': sources.NONZERO, 'noisy': sources.NOISY,
         'unused-cv': sources.WARNING.replace(b"        return '1x' % 0;",
                                             b"        $unused = 0;\n        return '1x' % 0;")}
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
OWN = (r'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled) /\ '
       r'pvalue_left_compiled = PSTRING ($ptascii("1x")) /\ '
       r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
       r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1)')
LIVE = (r'$ob_object_final_native_method(S) = (pobobjectreturn) /\ $call_current_valid(S) /\ '
        r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ '
        r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
        r'$heap_count(HOBJECT n_object, $machine_roots(S_generated)) = 2 /\ '
        r'$heap_count(HOBJECT n_exception, $machine_roots(S_generated)) = 1')


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
            'S_zero = S[.RESULT = KNOWN (PINT 0)]', 'S_zero_raw = $dz_raw(S_zero)',
            'S_generated = $throwable_transition(S_zero, S_zero_raw)',
            'S_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
        return bindings, [
            ('genuine source divisor1 produces normal modulo0 and retains its Warning',
             OWN + r' /\ z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
             r'pvalue_right = PINT 1 /\ pvalue_right_compiled = PINT 1 /\ '
             r'S_raw.COMPLETION = NORMAL /\ S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS'),
            ('substituted zero produces a real Error but cannot replace the compiled divisor1',
             r'$ob_object_error_operand_value(S_zero, S_zero.RESULT, [PCFIELD 1], z) = (PINT 0) /\ '
             r'$integer_slot_rank(S_zero, porigin_operator, [PCFIELD 1], S_zero.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_zero, porigin_operator, [PCFIELD 1], S_zero.RESULT) /\ '
             r'S_zero_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
             r'S_zero_raw.RESULT = KNOWN (PINT 0) /\ S_zero_raw.EVENTS = S_raw.EVENTS /\ ' + LIVE +
             r' /\ $ob_object_division_error_capture(S_zero, S_generated) = eps')]
    bindings += [
        'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
    if name == 'noisy':
        bindings += [
            'S_mask = S[.REPORTING = 2][.REPORTINGINI = $ptascii("2")][.REPORTINGMODIFIED = true]',
            'S_mask_raw = $dz_raw(S_mask)', 'S_mask_generated = $throwable_transition(S_mask, S_mask_raw)']
        return bindings, [
            ('genuine fractional prefix retains both integer-conversion notices before actual capture',
             OWN.replace('"1x"', '"1.5x"') + r' /\ z = 6 /\ '
             r'$string_long($ptascii("1.5x")) = STRINT 1 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps) /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
             r'S_raw.RESULT = KNOWN (PINT 0) /\ |S_raw.EVENTS| = 3 /\ '
             r'S_raw.EVENTS[0] = OUTPUT ([80]) /\ S_raw.EVENTS[1] = DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6 /\ '
             r'S_raw.EVENTS[2] = DIAGNOSTIC "Deprecated" ' +
             prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision') + r' 6 /\ ' +
             LIVE + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('hiding Deprecated preserves one Warning and real source authority without making conversion quiet',
             r'pfunction.CVS = eps /\ S_mask.CVS = eps /\ S_mask.ENV = eps /\ '
             r'$ob_object_final_native_method(S_mask) = (pobobjectreturn) /\ $call_current_valid(S_mask) /\ '
             r'~$error_handler_eligible(S_mask, 2) /\ '
             r'$integer_operand_source(S_mask, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
             r'$integer_operand_source(S_mask, porigin_operator, [PCFIELD 1], S_mask.RESULT) /\ '
             r'S_mask_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
             r'S_mask_raw.RESULT = KNOWN (PINT 0) /\ '
             r'S_mask_raw.EVENTS = $leading_warning(S_mask, true, z).EVENTS /\ '
             r'S_mask_raw.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6] /\ '
             r'$ob_object_division_error_source(S_mask_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_mask_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_mask, S_mask_generated) = eps')]
    if name == 'unused-cv':
        bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_cell_unused)']
        return bindings, [
            ('genuine unused scalar CV retains original MOD source and Error but stays outside empty-CV capture',
             OWN + r' /\ z = 7 /\ |pfunction.CVS| = 1 /\ |S.CVS| = 1 /\ |S.ENV| = 1 /\ '
             r'(HCELL n_cell_unused) <- S.ALLOCATIONS /\ S.STORE[n_cell_unused] = DEFINED (PINT 0) /\ '
             r'$heap_count(HCELL n_cell_unused, $machine_roots(S_generated)) = 1 /\ '
             r'pvalue_right = PINT 0 /\ pvalue_right_compiled = PINT 0 /\ '
             r'$value_nodes(pvalue_left) = eps /\ $ob_object_string_value(S, pvalue_left) /\ '
             r'$ob_object_error_operand_value(S, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (PINT 0) /\ '
             r'~$error_handler_eligible(S, 2) /\ S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ '
             r'S.RETIREDOWNERS = eps /\ $base_nodes(S.BASE) = eps /\ '
             r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
             r'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (7) /\ '
             r'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (7) /\ '
             r'$string_long($ptascii("1x")) = STRINT 1 (LEADINGNUMBER :: eps) /\ '
             r'$ob_object_modulo_integer(pvalue_left) = eps /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 7 /\ '
             r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS /\ ' +
             LIVE + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1x"))',
        'S_request = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_request) z) :: ptask_tail*][.STRINGDATA = S.STRINGDATA ++ [$ptascii("1x")]]',
        'S_request_raw = $dz_raw(S_request)',
        'S_request_generated = $throwable_transition(S_request, S_request_raw)',
        'S_line = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) $(z + 1)) :: ptask_tail*]',
        'S_line_generated = $throwable_transition(S_line, $dz_raw(S_line))']
    return bindings, [
        ('own empty-CV integer-prefix CONST pair captures genuine raw54 scratch and materialized Error',
         OWN + r' /\ z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
         r'pvalue_right = PINT 0 /\ pvalue_right_compiled = PINT 0 /\ '
         r'$string_long($ptascii("1x")) = STRINT 1 (LEADINGNUMBER :: eps) /\ '
         r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
         r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS /\ ' + LIVE + r' /\ ' + CAPTURE),
        ('same-byte valid request string keeps the real Error but cannot replace its own interned CONST',
         r'$ob_object_string_value(S_request, pvalue_request) /\ '
         r'$ob_object_error_operand_value(S_request, KNOWN pvalue_request, [PCFIELD 0], z) = (pvalue_request) /\ '
         r'$integer_slot_rank(S_request, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) = (1) /\ '
         r'~$integer_operand_source(S_request, porigin_operator, [PCFIELD 0], KNOWN pvalue_request) /\ '
         r'S_request_raw.EVENTS = S_raw.EVENTS /\ S_request_raw.RESULT = KNOWN (PINT 0) /\ '
         r'$ob_object_return_error_live(S_request_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_request, S_request_generated) = eps'),
        ('changed operation line and missing Warning cannot borrow the original Error authority',
         r'$code_expression_at_source(S_line, porigin_operator, [PCFIELD 1]) = (6) /\ '
         r'$throwable_field(S_line_generated, n_exception, "line") = PINT 7 /\ '
         r'$ob_object_division_error_capture(S_line, S_line_generated) = eps /\ '
         r'$ob_object_division_error_capture(S, S_generated[.EVENTS = S.EVENTS]) = eps /\ '
         r'$ob_object_division_error_capture(S[.CURRENT = eps], S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps')]


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
        'tests/semantics/output_final_default_constant_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
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
