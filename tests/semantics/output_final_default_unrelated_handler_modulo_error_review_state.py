#!/usr/bin/env python3
"""Staged MOD capture authenticates cached integers, pointers and current reads."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time

from recorded_worker import Worker
import output_final_default_unrelated_handler_modulo_error_state as author
import output_final_default_unrelated_handler_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = author.prior
PREFIX = author.PREFIX
ORIGINAL = sources.CASES['native-default-unrelated-handler-modulo-error-cv-pair']
OWN = ORIGINAL.replace(b"$left = '1x';", b"$left = '1x'; $other = '1x';")
CONST = sources.CASES['native-default-unrelated-handler-modulo-error-constant']
UNUSED = CONST.replace(b"return '1x' % 0;", b"$unused = 0; return '1x' % 0;")
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'snapshots': OWN, 'constant': CONST,
         'carrier': ORIGINAL, 'handlers': ORIGINAL, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE


def task(operation='pintegeroperation', phase='INTEGER_RIGHT i_left',
         conversion='pintegerconversion', cursor='0'):
    return '(INTEGER_OPERATOR_WARNING ' + operation + ' (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def authority(name, fixture, path):
    form = 'constant' if name in ['constant', 'unused-cv'] else 'cv-pair'
    bindings, _ = author.frontier(form, fixture, path)
    genuine = author.original(form)
    if name in ['source', 'snapshots']:
        genuine = genuine.replace('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                                  'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]').replace('|S.ENV| = 2', '|S.ENV| = 3')
    if name == 'source':
        bindings += ['pintegeroperation_other = pintegeroperation[.LEFT = VARIABLE ($ptascii("other")) z_left][.LEFTPOINTER = INTEGER_CV ($ptascii("other"))]',
                     'S_other = S[.TODO = ' + task('pintegeroperation_other') + ']']
        checks = [('the original staged pair retains own reads, actual warning and live Error', genuine + r' /\ ' + CAPTURE),
                  ('an equal-valued foreign variable cannot replace the original left read',
                   r'$integer_pointer_value(S_other, pintegeroperation_other.LEFTPOINTER) = (pvalue_left) /\ '
                   r'~$integer_operation_source(S_other, pintegeroperation_other) /\ '
                   r'$ob_object_division_error_capture(S_other, S_generated) = eps')]
        for label, changes in [
            ('each read line must be its own compiled expression line',
             [('left_line', '[.LEFT = VARIABLE n_left* $(z_left + 1)]'),
              ('right_line', '[.RIGHT = VARIABLE n_right* $(z_right + 1)]')]),
            ('KNOWN values cannot replace the original private CV producers',
             [('left_known', '[.LEFT = KNOWN pvalue_left][.LEFTPOINTER = INTEGER_COPY pvalue_left]'),
              ('right_known', '[.RIGHT = KNOWN pvalue_right][.RIGHTPOINTER = INTEGER_COPY pvalue_right]')])]:
            conditions = []
            for suffix, update in changes:
                operation = 'pintegeroperation_' + suffix
                state = 'S_' + suffix
                bindings += [operation + ' = pintegeroperation' + update,
                             state + ' = S[.TODO = ' + task(operation) + ']']
                conditions += ['~$integer_operation_source(' + state + ', ' + operation + ')',
                               '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
            checks += [(label, r' /\ '.join(conditions))]
        conditions = []
        for side, field in [('left', 0), ('right', 1)]:
            state = 'S_reference_' + side
            bindings += [state + ' = S[.REFCELLS = S.REFCELLS ++ [n_cell_' + side + ']]']
            conditions += ['$ob_object_error_operand_value(' + state + ', pintegeroperation.' + side.upper() + ', [PCFIELD ' + str(field) + '], z) = eps',
                           '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
        return bindings, checks + [('reference marking on either genuine cell refuses this private-cell contour', r' /\ '.join(conditions))]
    if name == 'snapshots':
        bindings += [
            'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
            'S_saved_raw = $dz_raw(S_saved)', 'S_saved_generated = $throwable_transition(S_saved, S_saved_raw)',
            '$integer_conversion(PBOOL false) = (pintegerconversion_false)',
            'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_false') + ']',
            'S_snapshot_raw = $dz_raw(S_snapshot)', 'S_snapshot_generated = $throwable_transition(S_snapshot, S_snapshot_raw)',
            '$lookup(S.ENV, $ptascii("other")) = (n_cell_other)',
            'pintegeroperation_foreign = pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_cell_other]',
            'S_foreign = S[.REFCELLS = S.REFCELLS ++ [n_cell_other]][.TODO = ' + task('pintegeroperation_foreign') + ']',
            'S_foreign_raw = $dz_raw(S_foreign)', 'S_foreign_generated = $throwable_transition(S_foreign, S_foreign_raw)',
            'S_cursor = S[.TODO = ' + task(cursor='1') + ']',
            'S_phase = S[.TODO = ' + task(phase='INTEGER_LEFT') + ']', 'S_phase_raw = $dz_raw(S_phase)']
        return bindings, [
            ('a forged cached left integer preserves the real zero Error but fails reconversion',
             genuine + r' /\ ' + CAPTURE + r' /\ '
             r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 0) /\ '
             r'S_saved_raw = S_request /\ S_saved_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_saved, S_saved_generated) = eps'),
            ('an equal-zero BOOL snapshot cannot replace the current PINT RHS conversion',
             r'pintegerconversion_false.INPUT = PBOOL false /\ pintegerconversion_false.VALUE = 0 /\ '
             r'pintegerconversion_false.NOTICES = eps /\ '
             r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_false, 0) /\ '
             r'S_snapshot_raw = S_request /\ S_snapshot_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_snapshot, S_snapshot_generated) = eps'),
            ('an operation-valid live foreign CELL pointer still fails canonical own selection',
             r'n_cell_other =/= n_cell_left /\ (HCELL n_cell_other) <- S_foreign.ALLOCATIONS /\ '
             r'$integer_warning_valid(S_foreign, pintegeroperation_foreign, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
             r'$integer_pointer_value(S_foreign, pintegeroperation_foreign.LEFTPOINTER) = (pvalue_left) /\ '
             r'$integer_pointer_select(S_foreign, pintegeroperation.LEFT) = (pintegeroperation.LEFTPOINTER) /\ '
             r'pintegeroperation_foreign.LEFTPOINTER =/= pintegeroperation.LEFTPOINTER /\ '
             r'$ob_object_error_operand_value(S_foreign, pintegeroperation.LEFT, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'S_foreign_raw = S_request[.REFCELLS = S_foreign.REFCELLS] /\ '
             r'$ob_object_return_error_live(S_foreign_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_foreign, S_foreign_generated) = eps'),
            ('an empty RHS notice list cannot authenticate cursor one',
             r'~$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ '
             r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
            ('a valid LEFT phase advances normally and cannot borrow the actual RIGHT-phase Error',
             r'$integer_warning_valid(S_phase, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0) /\ '
             r'S_phase_raw.COMPLETION = NORMAL /\ S_phase_raw.RESULT = KNOWN PNULL /\ '
             r'S_phase_raw.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 0)) :: ptask_tail* /\ '
             r'S_phase_raw.EVENTS = S.EVENTS /\ S_phase_raw.STORE = S.STORE /\ '
             r'$ob_object_division_error_capture(S_phase, S_generated) = eps')]
    if name == 'constant':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1x"))',
            'pintegeroperation_request = pintegeroperation[.LEFT = KNOWN pvalue_request][.LEFTPOINTER = INTEGER_COPY pvalue_request]',
            'S_request_left = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("1x")]][.TODO = ' + task('pintegeroperation_request') + ']',
            'S_request_next = S_generated[.STRINGDATA = S_request_left.STRINGDATA]',
            'pintegeroperation_false = pintegeroperation[.RIGHT = KNOWN (PBOOL false)][.RIGHTPOINTER = INTEGER_COPY (PBOOL false)]',
            '$integer_conversion(PBOOL false) = (pintegerconversion_false)',
            'S_false = S[.TODO = ' + task('pintegeroperation_false', conversion='pintegerconversion_false') + ']']
        return bindings, [
            ('the genuine compiled constants retain staged capture with no cells', genuine + r' /\ ' + CAPTURE),
            ('a valid same-byte REQUEST cannot replace the compiled left constant',
             r'$ob_object_string_value(S_request_left, pvalue_request) /\ '
             r'$integer_pointer_select(S_request_left, pintegeroperation_request.LEFT) = (pintegeroperation_request.LEFTPOINTER) /\ '
             r'$integer_slot_rank(S_request_left, porigin_operator, [PCFIELD 0], pintegeroperation_request.LEFT) = (1) /\ '
             r'~$integer_operand_source(S_request_left, porigin_operator, [PCFIELD 0], pintegeroperation_request.LEFT) /\ '
             r'$ob_object_return_error_live(S_request_next, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_request_left, S_request_next) = eps'),
            ('quiet BOOL zero cannot replace the compiled PINT zero source',
             r'pintegerconversion_false.VALUE = 0 /\ pintegerconversion_false.NOTICES = eps /\ '
             r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], pintegeroperation_false.RIGHT) /\ '
             r'$ob_object_division_error_capture(S_false, S_generated) = eps')]
    if name == 'carrier':
        bindings += [
            'pvalue_request_left = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1x"))',
            'pvalue_request_right = PSTRING_CARRIER (REQUEST_STRING $(|S.STRINGDATA| + 1)) ($ptascii("0"))',
            '$integer_conversion(pvalue_request_right) = (pintegerconversion_request)',
            'S_carrier = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("1x"), $ptascii("0")]][.STORE = $set_cell($set_cell(S.STORE, n_cell_left, DEFINED pvalue_request_left), n_cell_right, DEFINED pvalue_request_right)][.TODO = ' + task(conversion='pintegerconversion_request') + ']',
            'S_carrier_raw = $dz_raw(S_carrier)', 'S_carrier_generated = $throwable_transition(S_carrier, S_carrier_raw)',
            'S_invalid = S_carrier[.STRINGDATA = S.STRINGDATA]',
            'S_invalid_next = S_carrier_generated[.STRINGDATA = S.STRINGDATA]']
        return bindings, [
            ('authenticated current REQUEST values retain their own staged reads and quiet RHS snapshot',
             genuine + r' /\ ' + CAPTURE + r' /\ $call_current_valid(S_carrier) /\ '
             r'$ob_object_error_operand_value(S_carrier, pintegeroperation.LEFT, [PCFIELD 0], z) = (pvalue_request_left) /\ '
             r'$ob_object_error_operand_value(S_carrier, pintegeroperation.RIGHT, [PCFIELD 1], z) = (pvalue_request_right) /\ '
             r'S_carrier_raw = S_request[.STORE = S_carrier.STORE][.STRINGDATA = S_carrier.STRINGDATA] /\ '
             r'$ob_object_return_error_live(S_carrier_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_carrier, S_carrier_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('missing REQUEST identities refuse both current reads and the same live Error',
             r'~$ob_object_string_value(S_invalid, pvalue_request_left) /\ ~$ob_object_string_value(S_invalid, pvalue_request_right) /\ '
             r'$ob_object_error_operand_value(S_invalid, pintegeroperation.LEFT, [PCFIELD 0], z) = eps /\ '
             r'$ob_object_error_operand_value(S_invalid, pintegeroperation.RIGHT, [PCFIELD 1], z) = eps /\ '
             r'$ob_object_division_error_capture(S_invalid, S_invalid_next) = eps')]
    if name == 'handlers':
        bindings += [
            'S_warning = S[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("unused_modulo_deprecated"))), LEVELS 2}]',
            'S_warning_raw = $dz_raw(S_warning)', 'S_warning_generated = $throwable_transition(S_warning, S_warning_raw)',
            'S_none = S[.ERRORHANDLER = eps]', 'S_none_raw = $dz_raw(S_none)',
            'S_none_generated = $throwable_transition(S_none, S_none_raw)']
        return bindings, [
            ('a currently eligible Warning handler refuses this unrelated-handler staged contour',
             genuine + r' /\ ' + CAPTURE + r' /\ $call_current_valid(S_warning) /\ '
             r'$error_handler_eligible(S_warning, 2) /\ ~$error_handler_eligible(S_warning, 8192) /\ '
             r'S_warning_raw = S_request[.ERRORHANDLER = S_warning.ERRORHANDLER] /\ '
             r'$ob_object_return_error_live(S_warning_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_warning, S_warning_generated) = eps'),
            ('a constructed staged state without the selected unrelated handler remains outside this contour',
             r'$call_current_valid(S_none) /\ ~$error_handler_eligible(S_none, 2) /\ ~$error_handler_eligible(S_none, 8192) /\ '
             r'S_none_raw = S_request[.ERRORHANDLER = eps] /\ '
             r'$ob_object_return_error_live(S_none_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_none, S_none_generated) = eps')]
    genuine = genuine.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
    bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_unused)', 'S.STORE[n_unused] = DEFINED (PINT 0)']
    return bindings, [('a real unused cell preserves the CONST/CONST empty-CV refusal',
        genuine + r' /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
        r'$heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
        r'$ob_object_division_error_capture(S, S_generated) = eps')]


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
        report.setdefault('after', fingerprint())
        report.setdefault('after_revision', head())
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
