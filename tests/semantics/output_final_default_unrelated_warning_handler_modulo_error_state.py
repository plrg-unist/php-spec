#!/usr/bin/env python3
"""Precision-only staged MOD conversions preserve original reads and FINAL cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_unrelated_handler_modulo_error_state as previous
import output_final_default_unrelated_warning_handler_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
shared = previous.shared
PREFIX = previous.PREFIX
CAPTURE = previous.CAPTURE
CASES = {name: sources.CASES['native-default-unrelated-warning-handler-modulo-error-' + name]
         for name in ['constant-float', 'cv-pair-string']}


def bindings_for(name, fixture, path):
    form, _ = name.rsplit('-', 1)
    return previous.bindings_for(form, fixture, path)


def original(name):
    form, kind = name.rsplit('-', 1)
    condition = previous.original(form)
    message = (b'Implicit conversion from float-string "1.5" to int loses precision' if kind == 'string'
               else b'Implicit conversion from float 1.5 to int loses precision')
    left = ('PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5"))' if kind == 'string'
            else 'PFLOAT 4609434218613702656')
    conversion = ('$string_long($ptascii("1.5")) = STRINT i_left (STRINGPRECISIONLOSS :: eps)' if kind == 'string'
                  else '$float_long(4609434218613702656, true) = (i_left, [PRECISIONLOSS])')
    replacements = {
        'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))': 'pvalue_left = ' + left,
        '$string_long($ptascii("1x")) = STRINT i_left (LEADINGNUMBER :: eps)': conversion,
        'pintegerconversion_left.NOTICES = [(2, ($ptascii("A non-numeric value encountered")))]':
            'pintegerconversion_left.NOTICES = [(8192, ' + prior.value(message) + ')]',
        'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered"))':
            'DIAGNOSTIC "Deprecated" ' + prior.value(message),
        r'~$error_handler_eligible(S, 2) /\ $error_handler_eligible(S, 8192)':
            r'$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192)'}
    for old, new in replacements.items():
        assert condition.count(old) == 1, old
        condition = condition.replace(old, new)
    if kind == 'string':
        condition = condition.replace('$ptascii("1x")', '$ptascii("1.5")')
    else:
        condition = r' /\ '.join(part for part in condition.split(r' /\ ')
                                if part != '$ob_object_string_value(S, pvalue_left)')
        condition = condition.replace('pvalue_left_compiled = PSTRING ($ptascii("1x"))',
                                      'pvalue_left_compiled = PFLOAT 4609434218613702656')
    return condition


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:index], [('genuine original precision-only pointers and saved integer precede the live MOD Error',
                               original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]


def lifecycle(name, fixture, path):
    form, _ = name.rsplit('-', 1)
    bindings, checks = previous.lifecycle(form, fixture, path)
    old = previous.original(form)
    assert checks[0][1].count(old) == 1
    checks[0] = ('actual precision-only staged completion retains source and exact driver closure',
                 checks[0][1].replace(old, original(name)))
    checks[2] = ('C0 preserves the sole Deprecated notice and no handler output after actual retirement', checks[2][1])
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--frontier', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true', 'module_count': len(modules),
              'source_agreement_credit': 0, 'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = args.output / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
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
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = (frontier if args.frontier else lifecycle)(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
                'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
            watched += [Path(module.__file__) for module in list(sys.modules.values())
                        if getattr(module, '__file__', None) and Path(module.__file__).parent == Path(__file__).parent]
            watched += [path, fixture, directory / 'checked.json']
            fp = lambda: {str(p): prior.common.sha(p) for p in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'before': fp(), 'passed': False}
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
                record.update(seconds=time.monotonic() - started, after=fp())
            assert record['before'] == record['after']
            record['passed'] = True
        report['after_revision'] = head()
        assert report['revision'] == report['after_revision']
        report['passed'] = all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(args.output / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
