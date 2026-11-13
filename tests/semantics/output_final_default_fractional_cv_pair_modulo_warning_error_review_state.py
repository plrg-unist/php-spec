#!/usr/bin/env python3
"""Fractional CV-pair MOD capture keeps right-cell authority and the old empty-CV bound."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_review_state as previous
import output_final_default_fractional_cv_pair_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'right-authority': sources.CASES['native-default-fractional-cv-pair-warning-modulo-integer-zero']}
CASES['unused-cv-boundary'] = CASES['right-authority'].replace(
    b"$b = '1.5x';", b'$b = 0;').replace(b'        $c = 0;\n', b'').replace(
    b'return $b % $c;', b"return '1.5x' % 0;")


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        '$string_bytes(pvalue_left) = (n_bytes_left*)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (n_rank_left)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (n_rank_right)',
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
               r'|S_raw.EVENTS| = $(|S.EVENTS| + 2) /\ ' + previous.LIVE)
    if name == 'unused-cv-boundary':
        bindings += ['poperand_left = KNOWN pvalue_left', 'S.RESULT = KNOWN (PINT 0)',
                     '$lookup(S.ENV, $ptascii("b")) = (n_cell_unused)']
        return bindings, [
            ('genuine CONST1x1 precision pair with an actual unused local retains the old empty-CV refusal',
             genuine + r' /\ z = 7 /\ n_rank_left = 1 /\ n_rank_right = 1 /\ '
             r'pfunction.CVS = [$ptascii("b")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
             r'S.STORE[n_cell_unused] = DEFINED (PINT 0) /\ '
             r'(HCELL n_cell_unused) <- S.ALLOCATIONS /\ ~(n_cell_unused <- S.REFCELLS) /\ '
             r'$heap_count(HCELL n_cell_unused, $machine_roots(S)) = 1 /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += [
        'poperand_left = VARIABLE n_left* z_left', 'S.RESULT = VARIABLE n_right* z_right',
        '$lookup(S.ENV, n_left*) = (n_cell_left)', '$lookup(S.ENV, n_right*) = (n_cell_right)',
        'S_line = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
        'S_line_raw = $dz_raw(S_line)', 'S_line_generated = $throwable_transition(S_line, S_line_raw)',
        'S_ref = S[.REFCELLS = S.REFCELLS ++ [n_cell_right]]',
        'S_ref_raw = $dz_raw(S_ref)', 'S_ref_generated = $throwable_transition(S_ref, S_ref_raw)']
    return bindings, [
        ('genuine own two-cell8x8 precision pair captures with both diagnostics intact',
         genuine + r' /\ z = 8 /\ z_left = 8 /\ z_right = 8 /\ '
         r'n_left* = $ptascii("b") /\ n_right* = $ptascii("c") /\ '
         r'n_cell_left =/= n_cell_right /\ n_rank_left = 8 /\ n_rank_right = 8 /\ '
         r'$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1 /\ '
         r'$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1 /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('changed right-read line retains complete Error but loses own-child and private-reader authority',
         r'$integer_slot_rank(S_line, porigin_operator, [PCFIELD 1], S_line.RESULT) = (8) /\ '
         r'~$integer_operand_source(S_line, porigin_operator, [PCFIELD 1], S_line.RESULT) /\ '
         r'$ob_object_error_operand_value(S_line, S_line.RESULT, [PCFIELD 1], z) = eps /\ '
         r'S_line_raw = S_raw /\ S_line_generated = S_generated /\ '
         r'$ob_object_division_error_capture(S_line, S_line_generated) = eps'),
        ('marked right cell preserves source/live Error and exact states modulo REFCELLS while read and capture refuse',
         r'$integer_operand_source(S_ref, porigin_operator, [PCFIELD 1], S_ref.RESULT) /\ '
         r'$integer_slot_rank(S_ref, porigin_operator, [PCFIELD 1], S_ref.RESULT) = (8) /\ '
         r'$ob_object_error_operand_value(S_ref, S_ref.RESULT, [PCFIELD 1], z) = eps /\ '
         r'S_ref_raw = S_raw[.REFCELLS = S_ref.REFCELLS] /\ '
         r'S_ref_generated = S_generated[.REFCELLS = S_ref.REFCELLS] /\ '
         r'$ob_object_division_error_source(S_ref_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_ref_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_ref, S_ref_generated) = eps')]


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
        'tests/semantics/output_final_default_fractional_cv_pair_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_fractional_left_cv_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_fractional_left_cv_modulo_warning_error_review_state.py',
        'tests/semantics/output_final_default_fractional_cv_zero_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_fractional_cv_zero_modulo_warning_error_review_state.py',
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
