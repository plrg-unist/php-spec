#!/usr/bin/env python3
"""Private scalar CV errors bind source children without owning their cells."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_scalar_cv_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
CASES = {'authority': sources.DIVISION, 'catch': sources.CATCH, 'override': sources.OVERRIDE}
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')


def authority(fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT DIVIDE (VARIABLE n_left* z_left) z) :: ptask_tail*',
        'S.RESULT = VARIABLE n_right* z_right', 'S.ORIGIN = (porigin_operator)',
        '$lookup(S.ENV, n_left*) = (n_cell_left)', '$lookup(S.ENV, n_right*) = (n_cell_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_read_left = $resolve_at(S_inputs, VARIABLE n_left* z_left, z)',
        'S_read_right = $resolve_at(S_read_left, S.RESULT, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Division by zero"), LINE z}',
        'S_fake = S[.TODO = (BINARY_RIGHT DIVIDE (VARIABLE n_right* z_left) z) :: ptask_tail*]',
        'S_fake_request = $dz_raw(S_fake)', 'S_fake_generated = $throwable_transition(S_fake, S_fake_request)',
        'S_line = S[.TODO = (BINARY_RIGHT DIVIDE (VARIABLE n_left* $(z_left + 1)) z) :: ptask_tail*]',
        'S_ref = S[.REFCELLS = S.REFCELLS ++ [n_cell_left]]',
        'S_extra = S[.HELD = [HCELL n_cell_left]]',
        'S_undefined = S[.STORE = $set_cell(S.STORE, n_cell_left, UNDEFINED)]',
        'S_owning = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (POBJECT n_object))]',
        'S_backed = S[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_cell_left, LINE z, VALUE n_left*}]]',
        'S_borrowed = S[.BORROWEDREAD = ({SITE porigin_operator, OP IDENTICAL, LEFT n_left*, LEFTLINE z_left, RIGHT n_right*, LINE z, CELL n_cell_left, BASE S.BASE})]',
        'S.CLASSES = [pclassdesc]', 'pclassdesc.METHODS = [pmethoddesc]', 'pmethoddesc.FUNCTION = pfunction',
        'pfunction_global = pfunction[.CODE = pfunction.CODE[.GLOBALS = [[PCFIELD 0]]]]',
        'pfunction_static = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = pfunction.CODE.EXPRESSIONS ++ [CODESTATIC [PCFIELD 0] n_left* z_left z false]]]',
        'S_global = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.FUNCTION = pfunction_global]]]]]',
        'S_static = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.FUNCTION = pfunction_static]]]]]',
        'pvalue_carrier = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("bad"))',
        'S_carrier = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED pvalue_carrier)][.STRINGDATA = S.STRINGDATA ++ [$ptascii("bad")]]',
        'S_carrier_invalid = S_carrier[.STRINGDATA = S.STRINGDATA]',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*']
    checks = [
        ('actual distinct zero cells and original ordered reads capture once',
         r'n_left* = $ptascii("a") /\ n_right* = $ptascii("b") /\ n_cell_left =/= n_cell_right /\ z_left = 8 /\ z_right = 8 /\ z = 8 /\ S.STORE[n_cell_left] = DEFINED (PINT 0) /\ S.STORE[n_cell_right] = DEFINED (PINT 0) /\ S_read_left = S_inputs[.RESULT = KNOWN (PINT 0)] /\ S_read_right = S_read_left /\ S_request = $dz_request(S, z) /\ S_request.RESULT = KNOWN (PINT 0) /\ S_request.EVENTS = S.EVENTS /\ S_generated.RESULT = KNOWN (PARRAY 0) /\ $ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (PINT 0) /\ $ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (PINT 0) /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, (OBJECT_DIVISION_ERROR pobreturnerror)) /\ pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror) /\ $heap_count(HCELL n_cell_left, $machine_roots(S_capture)) = 1 /\ $heap_count(HCELL n_cell_right, $machine_roots(S_capture)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1'),
        ('equal raw and materialized errors do not authenticate the wrong child',
         r'$call_current_valid(S_fake) /\ S_fake_request = S_request /\ S_fake_generated = S_generated /\ $ob_object_division_error_source(S_fake_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_fake_generated, pobreturnerror) /\ $ob_object_error_operand_value(S, VARIABLE n_right* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 1], z) = eps /\ $ob_object_division_error_capture(S_fake, S_fake_generated) = eps /\ $dz_raw(S_line) = S_request /\ $ob_object_error_operand_value(S_line, VARIABLE n_left* $(z_left + 1), [PCFIELD 0], z) = eps /\ $ob_object_division_error_capture(S_line, S_generated) = eps /\ $ob_object_division_error_capture(S, S_generated[.RESULT = S.RESULT]) = eps'),
        ('private-cell ownership and read constraints remain mandatory',
         r'$ob_object_error_operand_value(S_ref, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_extra, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_undefined, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_owning, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_backed, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_borrowed, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_global, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_static, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps'),
        ('validated carriers and legacy known operands keep distinct bounds',
         r'$string_carrier_valid(S_carrier, pvalue_carrier) /\ $ob_object_error_operand_value(S_carrier, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_carrier) /\ $value_nodes(pvalue_carrier) = eps /\ $ob_object_error_operand_value(S_carrier_invalid, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ $ob_object_error_operand_value(S_global, KNOWN pvalue_carrier, [PCFIELD 0], z) = (pvalue_carrier) /\ $ob_object_error_operand_value(S_borrowed, KNOWN (PINT 0), [PCFIELD 1], z) = (PINT 0) /\ $ob_object_return_error_operand(S_global[.RESULT = KNOWN (PINT 42)], z) /\ ~$ob_object_return_error_operand(S_global[.RESULT = KNOWN pvalue_carrier], z)')]
    checks += [
        ('charged successor follows real throwable begin',
         r'S_observed.COMPLETION = THROWING n_exception /\ S_capture = $throwable_begin(S_observed) /\ S_capture_found = $throwable_begin(S_observed)[.COMPLETION = BUDGET] /\ S_capture.RESULT = KNOWN PNULL /\ S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*'),
        ('charged call descriptors remain valid', '$call_descriptors_valid(S_capture)'),
        ('charged heap remains valid', '$heap_valid($heap_graph(S_capture))'),
        ('charged output state remains valid', '$output_state_valid(S_capture)'),
        ('charged destruction state remains valid', '$destruction_state_valid(S_capture)')]
    return bindings, checks


def clearing(name, fixture, path):
    bindings, checks = getattr(division, name)(fixture, path)
    bindings = [binding.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                'BINARY_RIGHT DIVIDE (VARIABLE n_left* z_left) z') for binding in bindings]
    bindings += ['S.RESULT = VARIABLE n_right* z_right', '$lookup(S.ENV, n_left*) = (n_cell_left)',
                 '$lookup(S.ENV, n_right*) = (n_cell_right)']
    checks = [(label, condition.replace('S_caught.CVS = eps /\\ S_caught.ENV = eps',
                                       'S_caught.CVS = S.CVS /\\ S_caught.ENV = S.ENV'))
              for label, condition in checks]
    checks.insert(0, ('genuine CV error metadata preserves both real scalar cells',
        r'n_cell_left =/= n_cell_right /\ S_request.RESULT = KNOWN (PINT 0) /\ S_generated.RESULT = KNOWN (PARRAY 0) /\ pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror) /\ $heap_count(HCELL n_cell_left, $machine_roots(S_capture)) = 1 /\ $heap_count(HCELL n_cell_right, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')))
    label, condition = checks[-1]
    checks[-1] = (label, condition + r' /\ ~((HCELL n_cell_left) <- S_restored.ALLOCATIONS) /\ ~((HCELL n_cell_right) <- S_restored.ALLOCATIONS) /\ $heap_count(HCELL n_cell_left, $machine_roots(S_restored)) = 0 /\ $heap_count(HCELL n_cell_right, $machine_roots(S_restored)) = 0')
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-scalar-cv-error-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    head = lambda: subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()
    report = {'revision': head(), 'mode': 'SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300, 'records': [], 'passed': False}
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    inputs = modules + ['spec/php.watsup', 'spec/semantics/modules.json', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/recorded_worker.py',
        'tests/semantics/output_final_scalar_cv_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py']
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir()
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
            bindings, checks = authority(checked['fixture'], path) if name == 'authority' else clearing(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / rel for rel in inputs] + [Path(__file__), path, fixture, directory / 'checked.json']
            fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'source_sha256': hashlib.sha256(CASES[name]).hexdigest(),
                      'before': fingerprint(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record['prepared'] = True
                continue
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
                record['observed'] = json.loads(result.stdout)
                assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
                record['passed'] = True
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record.update(seconds=time.monotonic() - started, after=fingerprint())
                record['passed'] = record['passed'] and record['before'] == record['after']
            assert record['passed'], 'watched inputs changed'
        report['after_revision'] = head()
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records']) and report['revision'] == report['after_revision']
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
