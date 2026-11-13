#!/usr/bin/env python3
"""Own right conversion diagnostics survive empty-CV native FINAL Error cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_constant_modulo_warning_error_state as previous
import output_final_default_right_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'both': sources.CASES['native-default-right-modulo-conversion-error-both']}


def lifecycle(name, fixture, path):
    bindings, checks = previous.lifecycle('float-string', fixture, path)
    replacements = {
        'S.RESULT = KNOWN (PINT 0)': 'S.RESULT = KNOWN pvalue_right',
        'S_integer_right = $integer_coerce(S_integer_left, PINT 0, z)':
            'S_integer_right = $integer_coerce(S_integer_left, pvalue_right, z)',
        'S_warned = $leading_warning(S, true, z)':
            'S_warned = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("0.5x"), z)',
        'S_reference = $binary_apply(S_right, MODULO, pvalue_left, PINT 0, z)[.HELD = S.HELD]':
            'S_reference = $binary_apply(S_right, MODULO, pvalue_left, pvalue_right, z)[.HELD = S.HELD]'}
    assert all(bindings.count(binding) == 1 for binding in replacements)
    bindings = [replacements.get(binding, binding) for binding in bindings]
    bindings += ['$compiled_read(S, porigin_right) = (pvalue_right_compiled)']
    deprecated = prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
    checks[0] = ('quiet original left1 precedes its own noisy right0 before exact raw54/152 and capture',
        r'z = 6 /\ pfunction.CVS = eps /\ S.CVS = eps /\ S.ENV = eps /\ '
        r'pvalue_left_compiled = PINT 1 /\ pvalue_left = PINT 1 /\ '
        r'pvalue_right_compiled = PSTRING ($ptascii("0.5x")) /\ '
        r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled) /\ '
        r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
        r'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (6) /\ '
        r'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (6) /\ '
        r'$string_long($ptascii("0.5x")) = STRINT 0 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps) /\ '
        r'$ob_object_modulo_integer(pvalue_left) = (1) /\ $ob_object_modulo_integer(pvalue_right) = eps /\ '
        r'$long_convertible(pvalue_right) /\ $ob_object_string_value(S, pvalue_right) /\ '
        r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
        r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
        r'S_left.RESULT = KNOWN (PINT 1) /\ S_right.RESULT = KNOWN pvalue_right /\ '
        r'S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ '
        r'S_integer_left.RESULT = KNOWN (PINT 1) /\ S_integer_left.COMPLETION = NORMAL /\ '
        r'S_integer_left.EVENTS = S.EVENTS /\ S_integer_right.RESULT = KNOWN (PINT 0) /\ '
        r'S_integer_right.COMPLETION = NORMAL /\ S_integer_right.EVENTS = S_warned.EVENTS /\ '
        r'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6, '
        r'DIAGNOSTIC "Deprecated" ' + deprecated + r' 6] /\ '
        r'S_request = S_reference /\ S_request.RESULT = KNOWN (PINT 0) /\ '
        r'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ '
        r'S_request.EVENTS = S_warned.EVENTS /\ '
        r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')
    checks[3] = ('C0 preserves the right Warning and Deprecated before the original fatal Error', checks[3][1])
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
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
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir()
            source = CASES[name]
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
                'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_constant_modulo_warning_error_sources.py',
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
