#!/usr/bin/env python3
"""NaN MOD notices retain source, payload, ordering and reporting-mask authority."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_left_modulo_range_error_review_state as previous
import output_final_default_left_modulo_nan_error_state as author
import output_final_default_left_modulo_nan_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = previous.prior
PREFIX = author.PREFIX
ORIGINAL = sources.CASES['native-default-left-modulo-nan-error-cv-pair']
OWN = ORIGINAL.replace(b'$left = NAN;', b'$left = NAN; $other = NAN;')
CONST = sources.CASES['native-default-left-modulo-nan-error-constant']
HANDLERS = ORIGINAL.replace(b'declare(strict_types=0);',
    b'declare(strict_types=0); function ob_left_modulo_range_handler($level, $message) {}')
UNUSED = CONST.replace(b'return NAN % 0;', b'$unused = 0; return NAN % 0;')
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'constant': CONST, 'carrier': ORIGINAL, 'prior-values': ORIGINAL,
         'masked': ORIGINAL, 'handlers': HANDLERS, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE
ALTERNATE = 'PFLOAT 9221120237041090561'


def notices(line, reverse=False):
    entries = ['DIAGNOSTIC "Warning" ' + prior.value(author.WARNING) + ' ' + str(line),
               'DIAGNOSTIC "Deprecated" ' + prior.value(author.DEPRECATED) + ' ' + str(line)]
    return '[' + ', '.join(reversed(entries) if reverse else entries) + ']'


def authority(name, fixture, path):
    if name not in ['prior-values', 'masked']:
        bindings, checks = previous.authority(name, fixture, path)
        old = previous.author.original('constant-infinite' if name in ['constant', 'unused-cv'] else 'cv-pair-finite')
        new = author.original('constant-nan' if name in ['constant', 'unused-cv'] else 'cv-pair-nan')
        if name == 'source':
            old = old.replace('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                              'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]').replace('|S.ENV| = 2', '|S.ENV| = 3')
            new = new.replace('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                              'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]').replace('|S.ENV| = 2', '|S.ENV| = 3')
        elif name == 'unused-cv':
            old = old.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
            new = new.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
        assert sum(old in condition for _, condition in checks) == 1
        checks = [(label.replace('range Warning', 'NaN notices').replace('range-Warning', 'NaN').replace('sole left NaN notices', 'ordered left NaN notices').replace('sole NaN notices', 'ordered NaN notices').replace('infinite CONST', 'NAN CONST'),
                   condition.replace(old, new)) for label, condition in checks]
        if name == 'source':
            bindings = ['S_bad_line = S_generated[.EVENTS = S.EVENTS ++ ' + notices(9) + ']'
                        if binding.startswith('S_bad_line = ') else binding for binding in bindings]
            bindings += ['S_swapped = S_generated[.EVENTS = S.EVENTS ++ ' + notices(8, reverse=True) + ']']
            checks += [('the same live Error cannot reverse the NaN Warning and Deprecated',
                r'$ob_object_return_error_live(S_swapped, pobreturnerror) /\ '
                r'$ob_object_division_error_source(S_swapped, pfunction, pobreturnerror) /\ '
                r'$machine_roots(S_swapped) = $machine_roots(S_generated) /\ '
                r'$ob_object_division_error_capture(S, S_swapped) = eps')]
        if name == 'constant':
            bindings += ['S_payload = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (' + ALTERNATE + ')) z) :: ptask_tail*]',
                         'S_payload_raw = $dz_raw(S_payload)', 'S_payload_generated = $throwable_transition(S_payload, S_payload_raw)']
            checks += [('an equal-diagnostic NaN payload cannot replace the actual compiled NAN constant',
                r'$integer_slot_rank(S_payload, porigin_operator, [PCFIELD 0], KNOWN (' + ALTERNATE + r')) = (1) /\ '
                r'~$integer_operand_source(S_payload, porigin_operator, [PCFIELD 0], KNOWN (' + ALTERNATE + r')) /\ '
                r'S_payload_raw = S_raw /\ S_payload_generated = S_generated /\ '
                r'$ob_object_division_error_capture(S_payload, S_payload_generated) = eps')]
        return bindings, checks
    bindings, _ = author.frontier('cv-pair-nan', fixture, path)
    bindings += ['S_raw = S_request']
    genuine = author.original('cv-pair-nan')
    if name == 'masked':
        parts = [genuine, CAPTURE]
        for reporting, selected in [(2, [('Warning', author.WARNING)]), (8192, [('Deprecated', author.DEPRECATED)]), (1, [])]:
            state = 'S_mask_' + str(reporting)
            bindings += [state + ' = S[.REPORTING = ' + str(reporting) + '][.REPORTINGINI = $ptascii("' + str(reporting) + '")][.REPORTINGMODIFIED = true]',
                         state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            expected = '[' + ', '.join('DIAGNOSTIC "' + level + '" ' + prior.value(message) + ' 8' for level, message in selected) + ']'
            parts += ['$call_current_valid(' + state + ')',
                      state + '_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8',
                      state + '_raw.RESULT = KNOWN (PINT 0)', state + '_raw.STORE = ' + state + '.STORE',
                      state + '_raw.EVENTS = S.EVENTS ++ ' + expected,
                      '$ob_object_return_error_live(' + state + '_generated, pobreturnerror)',
                      '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ((pobobjectreturn, pobreturnerror))']
        return bindings, [('intrinsic NaN notices retain actual capture when either or both visible notices are masked', r' /\ '.join(parts))]
    checks = []
    for suffix, value, expected in [
        ('precision', 'PFLOAT 4609434218613702656', '[DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float 1.5 to int loses precision') + ' 8]'),
        ('range', 'PFLOAT 5055640609639927018', '[DIAGNOSTIC "Warning" ' + prior.value(b'The float 1.0E+30 is not representable as an int, cast occurred') + ' 8]'),
        ('payload', ALTERNATE, notices(8))]:
        state = 'S_' + suffix
        bindings += [state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))]',
                     state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        checks += [('the current private ' + suffix + ' value retains its own intrinsic notice class and capture',
            genuine + r' /\ ' +
            '$ob_object_error_operand_value(' + state + ', VARIABLE n_left* z_left, [PCFIELD 0], z) = (' + value + r') /\ ' +
            state + '_raw.STORE = ' + state + r'.STORE /\ ' +
            state + '_raw.EVENTS = S.EVENTS ++ ' + expected + r' /\ ' +
            '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
            '$ob_object_division_error_capture(' + state + ', ' + state + r'_generated) = ((pobobjectreturn, pobreturnerror))')]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_final_default_left_modulo_nan_error_sources.py',
        'tests/semantics/output_final_default_left_modulo_nan_error_state.py',
        'tests/semantics/output_final_default_left_modulo_range_error_review_state.py',
        'tests/semantics/output_final_default_left_modulo_range_error_sources.py',
        'tests/semantics/output_final_default_left_modulo_range_error_state.py',
        'tests/semantics/output_final_default_left_modulo_deprecation_error_sources.py',
        'tests/semantics/output_final_default_left_modulo_deprecation_error_state.py',
        'tests/semantics/output_final_default_both_cv_modulo_conversion_error_state.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_left_cv_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_right_cv_modulo_conversion_error_state.py',
        'tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_cv_pair_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_both_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_right_modulo_conversion_error_review_state.py',
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
