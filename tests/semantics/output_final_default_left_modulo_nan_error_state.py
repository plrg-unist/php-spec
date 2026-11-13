#!/usr/bin/env python3
"""NaN conversion retains both notices, original source and real FINAL cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_left_modulo_deprecation_error_state as previous
import output_final_default_left_modulo_nan_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CAPTURE = previous.CAPTURE
CASES = {form + '-nan': sources.CASES['native-default-left-modulo-nan-error-' + form]
         for form in ['constant', 'cv-pair']}
WARNING = b'The float NAN is not representable as an int, cast occurred'
DEPRECATED = b'Implicit conversion from float NAN to int loses precision'


def bindings_for(name, fixture, path):
    return previous.bindings_for(name, fixture, path)


def original(name):
    _, kind, line, _ = previous.shape(name)
    condition = previous.original(name)
    old_message = prior.value(previous.message(kind))
    assert condition.count(old_message) == 2
    condition = condition.replace(old_message, prior.value(DEPRECATED))
    replacements = {
        'PFLOAT 4609434218613702656': 'PFLOAT 9221120237041090560',
        'pintegerconversion.VALUE = 1': 'pintegerconversion.VALUE = 0',
        'pintegerconversion.NOTICES = [(8192, ' + prior.value(DEPRECATED) + ')]':
            'pintegerconversion.NOTICES = [(2, ' + prior.value(WARNING) + '), (8192, ' + prior.value(DEPRECATED) + ')]',
        'S_integer_left.RESULT = KNOWN (PINT 1)': 'S_integer_left.RESULT = KNOWN (PINT 0)',
        'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Deprecated" ' + prior.value(DEPRECATED) + ' ' + str(line) + ']':
            'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ' + prior.value(WARNING) + ' ' + str(line) +
            ', DIAGNOSTIC "Deprecated" ' + prior.value(DEPRECATED) + ' ' + str(line) + ']'}
    assert all(old in condition for old in replacements)
    for old, new in replacements.items():
        condition = condition.replace(old, new)
    return condition + r' /\ $float_long(9221120237041090560, true) = (0, [RANGEWARNING, PRECISIONLOSS])'


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:index], [('genuine NAN reads retain both intrinsic notices before the actual live Error', original(name))]


def lifecycle(name, fixture, path):
    bindings, checks = previous.lifecycle(name, fixture, path)
    old = previous.original(name)
    assert checks[0][1].count(old) == 1
    checks[0] = ('original NAN conversion preserves both notices and stored values through actual production capture',
                 checks[0][1].replace(old, original(name)))
    checks[2] = ('C0 preserves the NAN Warning then Deprecated before the original fatal trace', checks[2][1])
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
            source = CASES[name]
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
                'tests/semantics/output_final_default_left_modulo_nan_error_sources.py',
                'tests/semantics/output_final_default_left_modulo_range_error_sources.py',
                'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_both_cv_modulo_conversion_error_state.py',
                'tests/semantics/output_final_default_left_modulo_deprecation_error_sources.py',
                'tests/semantics/output_final_default_left_modulo_deprecation_error_state.py',
                'tests/semantics/output_final_default_left_cv_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_right_cv_modulo_conversion_error_state.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_constant_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_left_cv_modulo_warning_error_sources.py',
                'tests/semantics/output_final_default_cv_pair_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_pair_modulo_warning_error_sources.py',
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
