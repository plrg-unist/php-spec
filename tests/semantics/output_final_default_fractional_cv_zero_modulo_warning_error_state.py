#!/usr/bin/env python3
"""One quiet-zero CV retires after fractional MOD notices and before FINAL C0."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_cv_zero_modulo_warning_error_state as previous
import output_final_default_fractional_cv_zero_modulo_warning_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {'string-zero': sources.CASES['native-default-fractional-cv-zero-warning-modulo-string-zero']}


def lifecycle(name, fixture, path):
    bindings, checks = previous.lifecycle('numeric-string', fixture, path)
    bindings = [binding for binding in bindings if 'n_cell_other' not in binding and 'S_other' not in binding]
    checks = checks[:4]
    def converted(text):
        text = r' /\ '.join(part for part in text.split(r' /\ ') if 'n_cell_other' not in part)
        return (text.replace('"1x"', '"-1.5x"')
                .replace('STRINT 1 (LEADINGNUMBER :: eps)', 'STRINT $(-1) (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps)')
                .replace('S_integer_left.RESULT = KNOWN (PINT 1)', 'S_integer_left.RESULT = KNOWN (PINT $(-1))')
                .replace('[$ptascii("b"), $ptascii("c")]', '[$ptascii("b")]')
                .replace('|S.ENV| = 2', '|S.ENV| = 1')
                .replace('z = 8', 'z = 7').replace('z_right = 8', 'z_right = 7')
                .replace('$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (8)', '$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (7)')
                .replace('$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (8)', '$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (7)')
                .replace(prior.value(b'Modulo by zero') + ' 8', prior.value(b'Modulo by zero') + ' 7'))
    bindings = [converted(binding).replace('S_warned = $leading_warning(S, true, z)',
        'S_warned = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("-1.5x"), z)')
        for binding in bindings]
    checks = [(label, converted(condition)) for label, condition in checks]
    deprecated = prior.value(b'Implicit conversion from float-string "-1.5x" to int loses precision')
    warning = 'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 8]'
    notices = ('S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 7, '
               'DIAGNOSTIC "Deprecated" ' + deprecated + ' 7]')
    assert checks[0][1].count(warning) == 1
    checks[0] = ('own quiet string-zero CV follows signed fractional conversion and both diagnostics into capture',
                 checks[0][1].replace(warning, notices) + r' /\ ~$error_handler_eligible(S, 8192) /\ |S_request.EVENTS| = $(|S.EVENTS| + 2)')
    checks[1] = ('actual right CV retires before native C0 readiness', checks[1][1])
    def fatal(line):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(line).encode() + b'\nStack trace:\n'
                b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) + b' on line ' + str(line).encode() + b'\n')
    checks[2] = ('C0 preserves Warning and Deprecated before the original fatal trace',
                 checks[2][1].replace(prior.value(fatal(8)), prior.value(fatal(7))))
    checks[3] = ('retired receipt keeps source without private-cell or Error ownership', checks[3][1])
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
                'tests/semantics/output_final_default_fractional_cv_zero_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_fractional_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_review_state.py',
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
