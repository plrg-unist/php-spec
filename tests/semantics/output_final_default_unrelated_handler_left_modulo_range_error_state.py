#!/usr/bin/env python3
"""Staged FLOAT range Warnings preserve original reads and FINAL cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_unrelated_warning_handler_modulo_error_state as previous
import output_final_default_left_modulo_range_error_state as range_state
import output_final_default_unrelated_handler_left_modulo_range_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
shared = previous.shared
PREFIX = previous.PREFIX
CAPTURE = previous.CAPTURE
CASES = {name: sources.CASES['native-default-unrelated-handler-left-modulo-range-error-' + name]
         for name in ['constant-infinite', 'cv-pair-finite']}


def bindings_for(name, fixture, path):
    return previous.bindings_for(name, fixture, path)


def original(name):
    form, kind = name.rsplit('-', 1)
    bits, converted, _ = range_state.FLOATS[kind]
    condition = previous.original(form + '-float')
    message = range_state.message(kind)
    old_message = b'Implicit conversion from float 1.5 to int loses precision'
    replacements = {
        '$float_long(4609434218613702656, true) = (i_left, [PRECISIONLOSS])':
            '$float_long(' + str(bits) + ', true) = (i_left, [RANGEWARNING])',
        'PFLOAT 4609434218613702656': 'PFLOAT ' + str(bits),
        'i_left = 1': 'i_left = ' + str(converted),
        'pintegerconversion_left.NOTICES = [(8192, ': 'pintegerconversion_left.NOTICES = [(2, ',
        'DIAGNOSTIC "Deprecated" ': 'DIAGNOSTIC "Warning" ',
        prior.value(old_message): prior.value(message),
        r'$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192)':
            r'~$error_handler_eligible(S, 2) /\ $error_handler_eligible(S, 8192)'}
    for old, new in replacements.items():
        assert condition.count(old) >= 1, old
        condition = condition.replace(old, new)
    return condition + r' /\ $typed_tag(pvalue_left) = "float" /\ S.ERRORHANDLER.LEVELS = 8192 /\ ' + \
        r'S.ERRORHANDLER.CALLBACK =/= eps /\ S.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]'


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    index = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:index], [('genuine FLOAT range conversion and saved integer precede the live MOD Error',
                               original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]


def lifecycle(name, fixture, path):
    form, _ = name.rsplit('-', 1)
    bindings, checks = previous.lifecycle(form + '-float', fixture, path)
    old = previous.original(form + '-float')
    assert checks[0][1].count(old) == 1
    checks[0] = ('actual FLOAT range staged completion retains source and exact driver closure',
                 checks[0][1].replace(old, original(name)))
    checks[2] = ('C0 preserves the sole range Warning and no handler output after actual retirement', checks[2][1])
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
