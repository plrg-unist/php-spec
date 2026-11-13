#!/usr/bin/env python3
"""Both MOD conversion diagnostics survive empty-CV native FINAL Error cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_right_modulo_conversion_error_state as previous
import output_final_default_both_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'string-notices': sources.CASES['native-default-both-modulo-conversion-error-string-notices']}


def lifecycle(name, fixture, path):
    bindings, checks = previous.lifecycle('both', fixture, path)
    right_notices = 'S_warned = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("0.5x"), z)'
    both_notices = 'S_warned = $long_string_notices($long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("1.5x"), z), LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("0.5x"), z)'
    assert bindings.count(right_notices) == 1
    bindings = [both_notices if binding == right_notices else binding for binding in bindings]
    warning = r'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 6'
    deprecated_left = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision') + ' 6'
    deprecated_right = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision') + ' 6'
    condition = checks[0][1]
    replacements = {
        r'pvalue_left_compiled = PINT 1 /\ pvalue_left = PINT 1':
            r'pvalue_left_compiled = PSTRING ($ptascii("1.5x")) /\ pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled) /\ pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ $ob_object_string_value(S, pvalue_left)',
        '$ob_object_modulo_integer(pvalue_left) = (1)':
            r'$ob_object_modulo_integer(pvalue_left) = eps /\ $long_convertible(pvalue_left)',
        'S_left.RESULT = KNOWN (PINT 1)': 'S_left.RESULT = KNOWN pvalue_left',
        'S_integer_left.EVENTS = S.EVENTS':
            'S_integer_left.EVENTS = S.EVENTS ++ [' + warning + ', ' + deprecated_left + ']',
        'S_warned.EVENTS = [OUTPUT ([80]), ' + warning + ', ' + deprecated_right + ']':
            'S_warned.EVENTS = [OUTPUT ([80]), ' + warning + ', ' + deprecated_left + ', ' + warning + ', ' + deprecated_right + ']'}
    assert all(condition.count(old) == 1 for old in replacements)
    for old, new in replacements.items():
        condition = condition.replace(old, new)
    checks[0] = ('own noisy CONST pair retains ordered left/right conversion before exact raw54/152 and actual capture', condition)
    checks[3] = ('C0 preserves both operands diagnostics before the original fatal Error', checks[3][1])
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
                'tests/semantics/output_final_default_both_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_right_modulo_conversion_error_state.py',
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
