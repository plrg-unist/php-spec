#!/usr/bin/env python3
"""Own noisy RHS CVs keep their stored value until FINAL Error retirement."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_cv_zero_modulo_warning_error_state as previous
import output_final_default_right_cv_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'both': sources.CASES['native-default-right-cv-modulo-conversion-error-both']}


def lifecycle(name, fixture, path):
    bindings, checks = previous.lifecycle('numeric-string', fixture, path)
    bindings = [binding for binding in bindings if 'n_cell_other' not in binding and 'S_other' not in binding]
    old_notice = 'S_warned = $leading_warning(S, true, z)'
    new_notice = 'S_warned = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("0.5x"), z)'
    assert bindings.count(old_notice) == 1
    bindings = [new_notice if binding == old_notice else binding for binding in bindings]
    deprecated = prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
    checks = checks[:4]
    checks[0] = ('own noisy RHS CV reads once without rewriting storage before exact raw54/152 and capture',
        r'z = 7 /\ z_right = 7 /\ n_right* = $ptascii("right") /\ '
        r'pfunction.CVS = [$ptascii("right")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
        r'pvalue_left_compiled = PINT 1 /\ pvalue_left = PINT 1 /\ '
        r'$compiled_read(S, porigin_right) = eps /\ '
        r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
        r'$string_long($ptascii("0.5x")) = STRINT 0 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps) /\ '
        r'$ob_object_modulo_integer(pvalue_left) = (1) /\ $ob_object_modulo_integer(pvalue_right) = eps /\ '
        r'$long_convertible(pvalue_right) /\ $ob_object_string_value(S, pvalue_right) /\ '
        r'$ob_object_error_operand_value(S, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
        r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
        r'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (7) /\ '
        r'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (7) /\ '
        r'~(n_cell_right <- S.REFCELLS) /\ (HCELL n_cell_right) <- S.ALLOCATIONS /\ '
        r'$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1 /\ '
        r'$heap_owners($heap_graph(S), HCELL n_cell_right) = 1 /\ '
        r'S_left.RESULT = KNOWN (PINT 1) /\ S_right.RESULT = KNOWN pvalue_right /\ '
        r'S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ '
        r'S_integer_left.RESULT = KNOWN (PINT 1) /\ S_integer_left.EVENTS = S.EVENTS /\ '
        r'S_integer_right.RESULT = KNOWN (PINT 0) /\ S_integer_right.EVENTS = S_warned.EVENTS /\ '
        r'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 7, '
        r'DIAGNOSTIC "Deprecated" ' + deprecated + r' 7] /\ '
        r'S_request = S_reference /\ S_request.RESULT = KNOWN (PINT 0) /\ '
        r'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 7 /\ '
        r'S_request.EVENTS = S_warned.EVENTS /\ S_request.STORE = S.STORE /\ '
        r'S_capture.STORE[n_cell_right] = DEFINED pvalue_right /\ '
        r'$heap_count(HCELL n_cell_right, $machine_roots(S_capture)) = 1 /\ '
        r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
        r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
        r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
        r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
        r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
        r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    def without_other(condition):
        return r' /\ '.join(part for part in condition.split(r' /\ ') if 'n_cell_other' not in part)
    checks[1] = ('the original RHS private cell retires before native C0 readiness', without_other(checks[1][1]))
    def fatal(line):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(line).encode() +
                b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                b' on line ' + str(line).encode() + b'\n')
    checks[2] = ('C0 preserves both RHS diagnostics before the original fatal trace',
                 checks[2][1].replace(prior.value(fatal(8)), prior.value(fatal(7))).replace(' 8 /\\ ', ' 7 /\\ '))
    checks[3] = ('retired source receipt owns neither the RHS private cell nor its Error', without_other(checks[3][1]))
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'source_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False}
    try:
        for name, source in CASES.items():
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = lifecycle(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
                'tests/semantics/output_final_default_right_cv_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py',
                'tests/semantics/output_final_modulo_error_sources.py',
                'tests/semantics/output_final_modulo_error_review_state.py',
                'tests/semantics/output_final_division_error_sources.py',
                'tests/semantics/output_final_division_error_review_state.py',
                'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
                'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
                'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
            watched += [Path(__file__), path, fixture, directory / 'checked.json']
            fp = lambda: {str(p): prior.common.sha(p) for p in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'before': fp(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
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
                record.update(seconds=time.monotonic() - started, after=fp())
            assert record['before'] == record['after']
            record['passed'] = True
        report['after_revision'] = head()
        assert report['revision'] == report['after_revision'], 'revision changed'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
