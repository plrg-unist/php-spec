#!/usr/bin/env python3
"""Quiet staged MOD preserves current values, selected handlers and real cells."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_unrelated_warning_handler_modulo_error_review_state as previous
import output_final_default_selected_handlers_quiet_modulo_error_state as author
import output_final_default_selected_handlers_quiet_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
PREFIX = author.PREFIX
ORIGINAL = sources.CASES['native-default-selected-handlers-quiet-modulo-error-cv-pair']
OWN = ORIGINAL.replace(b'$left = 1;', b'$left = 1; $other = 1;')
CONST = sources.CASES['native-default-selected-handlers-quiet-modulo-error-constant']
SAME = sources.CASES['native-default-selected-handlers-quiet-modulo-error-same-cv']
UNUSED = CONST.replace(b'return 1 % 0;', b'$unused = 0; return 1 % 0;')
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'snapshots': OWN, 'constant': CONST, 'carrier': ORIGINAL,
         'masks': ORIGINAL, 'values': ORIGINAL, 'same-cell': SAME, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE
task = previous.previous.task


def authority(name, fixture, path):
    if name in ['source', 'snapshots', 'constant', 'carrier', 'unused-cv']:
        bindings, checks = previous.authority(name, fixture, path)
        form = 'constant' if name in ['constant', 'unused-cv'] else 'cv-pair'
        old, new = previous.author.original(form + '-string'), author.original(form)
        if name in ['source', 'snapshots']:
            for source, replacement in [
                ('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                 'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]'),
                ('|S.ENV| = 2', '|S.ENV| = 3')]:
                old, new = old.replace(source, replacement), new.replace(source, replacement)
        if name == 'unused-cv':
            old = old.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
            new = new.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
        assert sum(old in condition for _, condition in checks) == 1
        checks = [(label.replace('actual Deprecated notice', 'quiet current values').replace('same-byte REQUEST', 'numeric-equivalent REQUEST'),
                   condition.replace(old, new)) for label, condition in checks]
        bindings = [binding.replace('$ptascii("1.5")', '$ptascii("1")') for binding in bindings]
        return bindings, checks
    bindings, _ = author.frontier('same-cv' if name == 'same-cell' else 'cv-pair', fixture, path)
    if name == 'same-cell':
        bindings += ['S_marked = S[.REFCELLS = S.REFCELLS ++ [n_cell_left]]']
        return bindings, [
            ('two genuine reads of one quiet cell retain one owning root and actual capture',
             author.original('same-cv') + r' /\ ' + CAPTURE + r' /\ '
             r'n_cell_left = n_cell_right /\ pintegeroperation.LEFTPOINTER = pintegeroperation.RIGHTPOINTER /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S_generated)) = 1'),
            ('marking the shared cell as a reference cannot borrow the original same-cell Error',
             r'$ob_object_error_operand_value(S_marked, pintegeroperation.LEFT, [PCFIELD 0], z) = eps /\ '
             r'$ob_object_error_operand_value(S_marked, pintegeroperation.RIGHT, [PCFIELD 1], z) = eps /\ '
             r'$ob_object_division_error_capture(S_marked, S_generated) = eps')]
    if name == 'masks':
        conditions = [author.original('cv-pair'), CAPTURE]
        for level in [2, 8192]:
            state = 'S_mask_' + str(level)
            bindings += [state + ' = S[.ERRORHANDLER.LEVELS = ' + str(level) + ']',
                         state + '_raw = $dz_raw(' + state + ')',
                         state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            conditions += ['$call_current_valid(' + state + ')',
                           '$error_handler_eligible(' + state + ', ' + str(level) + ')',
                           '~$error_handler_eligible(' + state + ', ' + str(8192 if level == 2 else 2) + ')',
                           state + '_raw = S_request[.ERRORHANDLER = ' + state + '.ERRORHANDLER]',
                           '$ob_object_return_error_live(' + state + '_generated, pobreturnerror)',
                           '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ((pobobjectreturn, pobreturnerror))']
        bindings += ['S_none = S[.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]',
                     'S_none_raw = $dz_raw(S_none)', 'S_none_generated = $throwable_transition(S_none, S_none_raw)']
        return bindings, [
            ('either or both selected numeric classes remain uncalled for quiet conversions', r' /\ '.join(conditions)),
            ('a constructed stage without any selected numeric handler remains outside this producer',
             r'$call_current_valid(S_none) /\ ~$error_handler_eligible(S_none, 2) /\ ~$error_handler_eligible(S_none, 8192) /\ '
             r'S_none_raw = S_request[.ERRORHANDLER = S_none.ERRORHANDLER] /\ '
             r'$ob_object_return_error_live(S_none_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_none, S_none_generated) = eps')]
    conditions = [author.original('cv-pair'), CAPTURE]
    for suffix, value, integer in [
        ('null', 'PNULL', 0), ('false', 'PBOOL false', 0), ('true', 'PBOOL true', 1),
        ('float', 'PFLOAT 4607182418800017408', 1),
        ('string', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))', 1)]:
        state, conversion = 'S_quiet_' + suffix, 'pintegerconversion_quiet_' + suffix
        bindings += ['$integer_conversion(' + value + ') = (' + conversion + ')',
                     state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))][.TODO = ' +
                     task(phase='INTEGER_RIGHT ' + str(integer)) + ']',
                     state + '_raw = $dz_raw(' + state + ')',
                     state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        conditions += [conversion + '.VALUE = ' + str(integer), conversion + '.NOTICES = eps',
                       '$ob_object_error_operand_value(' + state + ', pintegeroperation.LEFT, [PCFIELD 0], z) = (' + value + ')',
                       state + '_raw = S_request[.STORE = ' + state + '.STORE]',
                       '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ((pobobjectreturn, pobreturnerror))']
    checks = [('current quiet NULL, Boolean, exact FLOAT and numeric-string values authenticate their saved integers', r' /\ '.join(conditions))]
    bindings += ['$integer_conversion(PBOOL false) = (pintegerconversion_right_false)',
                 'S_right_false = S[.STORE = $set_cell(S.STORE, n_cell_right, DEFINED (PBOOL false))][.TODO = ' +
                 task(conversion='pintegerconversion_right_false') + ']',
                 'S_right_false_raw = $dz_raw(S_right_false)',
                 'S_right_false_generated = $throwable_transition(S_right_false, S_right_false_raw)']
    checks += [('a genuinely current BOOL-zero RHS is accepted only with its exact current snapshot',
        r'pintegerconversion_right_false.INPUT = PBOOL false /\ pintegerconversion_right_false.VALUE = 0 /\ '
        r'pintegerconversion_right_false.NOTICES = eps /\ '
        r'$ob_object_error_operand_value(S_right_false, pintegeroperation.RIGHT, [PCFIELD 1], z) = (PBOOL false) /\ '
        r'S_right_false_raw = S_request[.STORE = S_right_false.STORE] /\ '
        r'$ob_object_division_error_capture(S_right_false, S_right_false_generated) = ((pobobjectreturn, pobreturnerror))')]
    for suffix, value, levels in [
        ('precision', 'PFLOAT 4609434218613702656', '[8192]'),
        ('leading', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', '[2]'),
        ('nan', 'PFLOAT 9221120237041090560', '[2, 8192]')]:
        state, conversion = 'S_noisy_' + suffix, 'pintegerconversion_noisy_' + suffix
        bindings += ['$integer_conversion(' + value + ') = (' + conversion + ')',
                     'i_saved_' + suffix + ' = ' + conversion + '.VALUE',
                     '(z_level_' + suffix + ', ptbytes_notice_' + suffix + ')* = ' + conversion + '.NOTICES',
                     state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))][.TODO = ' +
                     task(phase='INTEGER_RIGHT i_saved_' + suffix) + ']',
                     state + '_raw = $dz_raw(' + state + ')',
                     state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        checks += [('intrinsic ' + suffix + ' notices cannot use the quiet class despite the same Error and no visible notice',
            'z_level_' + suffix + '* = ' + levels + r' /\ ' +
            state + r'.EVENTS = [OUTPUT ([80])] /\ ' +
            '$ob_object_error_operand_value(' + state + ', pintegeroperation.LEFT, [PCFIELD 0], z) = (' + value + r') /\ ' +
            state + '_raw = S_request[.STORE = ' + state + r'.STORE] /\ ' +
            '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
            '$ob_object_division_error_capture(' + state + ', ' + state + r'_generated) = eps')]
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
