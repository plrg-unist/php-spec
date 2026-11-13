#!/usr/bin/env python3
"""Precision-only staged MOD retains snapshot, source and notice-class authority."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_unrelated_handler_modulo_error_review_state as previous
import output_final_default_unrelated_warning_handler_modulo_error_state as author
import output_final_default_unrelated_warning_handler_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
PREFIX = author.PREFIX
ORIGINAL = sources.CASES['native-default-unrelated-warning-handler-modulo-error-cv-pair-string']
OWN = ORIGINAL.replace(b"$left = '1.5';", b"$left = '1.5'; $other = '1.5';")
CONST = sources.CASES['native-default-unrelated-warning-handler-modulo-error-constant-string']
UNUSED = CONST.replace(b"return '1.5' % 0;", b"$unused = 0; return '1.5' % 0;")
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'snapshots': OWN, 'constant': CONST, 'carrier': ORIGINAL,
         'handlers': ORIGINAL, 'unused-cv': UNUSED, 'classes': ORIGINAL}
CAPTURE = author.CAPTURE


def authority(name, fixture, path):
    if name != 'classes':
        bindings, checks = previous.authority(name, fixture, path)
        form = 'constant' if name in ['constant', 'unused-cv'] else 'cv-pair'
        old, new = previous.author.original(form), author.original(form + '-string')
        for source, replacement in [
            ('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
             'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]'),
            ('|S.ENV| = 2', '|S.ENV| = 3')]:
            if name in ['source', 'snapshots']:
                old, new = old.replace(source, replacement), new.replace(source, replacement)
        if name == 'unused-cv':
            old = old.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
            new = new.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
        assert sum(old in condition for _, condition in checks) == 1
        checks = [(label.replace('actual warning', 'actual Deprecated notice'), condition.replace(old, new))
                  for label, condition in checks]
        bindings = [binding.replace('$ptascii("1x")', '$ptascii("1.5")').replace('unused_modulo_deprecated', 'unused_modulo_warning')
                    for binding in bindings]
        if name == 'handlers':
            bindings = [binding.replace('LEVELS 2}', 'LEVELS 8192}') for binding in bindings]
            old_flags = r'$error_handler_eligible(S_warning, 2) /\ ~$error_handler_eligible(S_warning, 8192)'
            new_flags = r'~$error_handler_eligible(S_warning, 2) /\ $error_handler_eligible(S_warning, 8192)'
            assert checks[0][1].count(old_flags) == 1
            checks[0] = ('a currently eligible Deprecated handler refuses this unrelated-handler precision contour',
                         checks[0][1].replace(old_flags, new_flags))
        return bindings, checks
    bindings, _ = author.frontier('cv-pair-string', fixture, path)
    checks = []
    for suffix, value, levels, accepted in [
        ('float', 'PFLOAT 4609434218613702656', '[8192]', True),
        ('leading', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', '[2]', False),
        ('range', 'PFLOAT 5055640609639927018', '[2]', False),
        ('nan', 'PFLOAT 9221120237041090560', '[2, 8192]', False),
        ('quiet', 'PINT 1', 'eps', False)]:
        state = 'S_' + suffix
        conversion = 'pintegerconversion_' + suffix
        bindings += ['$integer_conversion(' + value + ') = (' + conversion + ')',
                     'i_saved_' + suffix + ' = ' + conversion + '.VALUE',
                     '(z_level_' + suffix + ', ptbytes_notice_' + suffix + ')* = ' + conversion + '.NOTICES',
                     state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))][.TODO = ' +
                     previous.task(phase='INTEGER_RIGHT i_saved_' + suffix) + ']',
                     state + '_raw = $dz_raw(' + state + ')',
                     state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        predicate = (('$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ') +
                     ('((pobobjectreturn, pobreturnerror))' if accepted else 'eps'))
        conditions = ([author.original('cv-pair-string'), CAPTURE] if not checks else []) + [
            'z_level_' + suffix + '* = ' + levels,
            '$ob_object_error_operand_value(' + state + ', pintegeroperation.LEFT, [PCFIELD 0], z) = (' + value + ')',
            '$integer_warning_valid(' + state + ', pintegeroperation, INTEGER_RIGHT i_saved_' + suffix + ', pintegerconversion, 0)',
            state + '.RESULT = KNOWN PNULL',
            state + '_raw = S_request[.STORE = ' + state + '.STORE]',
            '$ob_object_return_error_live(' + state + '_generated, pobreturnerror)', predicate]
        checks += [('current ' + suffix + ' conversion rederives its cached integer and complete intrinsic notice class',
                    r' /\ '.join(conditions))]
    return bindings, checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
    watched += [Path(module.__file__) for module in list(sys.modules.values())
                if getattr(module, '__file__', None) and Path(module.__file__).parent == Path(__file__).parent]
    fingerprint = lambda: {str(p): prior.common.sha(p) for p in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true', 'module_count': len(modules),
              'fixture_timeout_seconds': 300, 'source_agreement_credit': 0, 'native_agreement_credit': 0,
              'before': fingerprint(), 'records': [], 'passed': False}
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
            record = {'id': name, 'groups': [label for label, _ in checks], 'inputs_before': inputs(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, fixture_execution_credit=0)
                continue
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
        report['passed'] = (not args.prepare_only and all(record['passed'] for record in report['records']) and
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
