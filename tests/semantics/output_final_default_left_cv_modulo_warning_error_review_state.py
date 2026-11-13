#!/usr/bin/env python3
"""Left MOD CV capture preserves its RHS source and private-CV pair admission."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_cv_zero_modulo_warning_error_review_state as previous
import output_final_default_left_cv_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'rhs-source': sources.CASES['native-default-left-cv-warning-modulo-integer-prefix']}
CASES['both-cv'] = CASES['rhs-source'].replace(b"$c = '1x';", b'$c = 0;').replace(b'return $b % 0;', b'return $b % $c;')


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* z_left) z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)', '$lookup(S.ENV, n_left*) = (n_cell_left)',
        '$ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        'S_warned = $leading_warning(S, true, z)', 'S_raw = $dz_raw(S)',
        'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
    genuine = (r'n_left* = $ptascii("b") /\ z_left = 8 /\ z = 8 /\ '
               r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")) /\ '
               r'$ob_object_string_value(S, pvalue_left) /\ '
               r'$string_long($ptascii("1x")) = STRINT 1 (LEADINGNUMBER :: eps) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) /\ '
               r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
               r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) = (8) /\ '
               r'$ob_object_modulo_integer(pvalue_right) = (0) /\ '
               r'~$error_handler_eligible(S, 2) /\ '
               r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8 /\ '
               r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_warned.EVENTS /\ '
               r'$ob_object_final_native_method(S) = (pobobjectreturn) /\ $call_current_valid(S) /\ '
               r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ '
               r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
               r'$heap_count(HOBJECT n_object, $machine_roots(S_generated)) = 2 /\ '
               r'$heap_count(HOBJECT n_exception, $machine_roots(S_generated)) = 1')
    if name == 'both-cv':
        bindings += ['S.RESULT = VARIABLE n_right* z_right', '$lookup(S.ENV, n_right*) = (n_cell_right)']
        return bindings, [
            ('genuine private 8x8 operands retain their read/source/quiet Error facts and capture',
             genuine + r' /\ n_right* = $ptascii("c") /\ z_right = 8 /\ '
             r'pvalue_right = PINT 0 /\ n_cell_left =/= n_cell_right /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'~(n_cell_left <- S.REFCELLS) /\ ~(n_cell_right <- S.REFCELLS) /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1 /\ '
             r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
             r'($string_bytes(pvalue_right) = eps \/ $ob_object_string_value(S, pvalue_right)) /\ '
             r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ '
             r'$base_nodes(S.BASE) = eps /\ '
             r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
             r'$ob_object_modulo_integer(pvalue_left) = eps /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')]
    bindings += [
        'S.RESULT = KNOWN (PINT 0)',
        'S_false = S[.RESULT = KNOWN (PBOOL false)]', 'S_false_raw = $dz_raw(S_false)',
        'S_false_generated = $throwable_transition(S_false, S_false_raw)']
    return bindings, [
        ('genuine private left8 and original constant right1 retain quiet-zero capture',
         genuine + r' /\ pvalue_right = PINT 0 /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('same-Error false RHS substitution keeps rank1 and quiet zero but lacks the original constant source',
         r'$ob_object_modulo_integer(PBOOL false) = (0) /\ '
         r'$ob_object_error_operand_value(S_false, S_false.RESULT, [PCFIELD 1], z) = (PBOOL false) /\ '
         r'$integer_slot_rank(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) = (1) /\ '
         r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], S_false.RESULT) /\ '
         r'S_false_raw = S_raw /\ S_false_generated = S_generated /\ '
         r'$ob_object_division_error_capture(S_false, S_false_generated) = eps')]


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
        'tests/semantics/output_final_default_left_cv_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_cv_zero_modulo_warning_error_review_state.py',
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
