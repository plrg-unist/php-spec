#!/usr/bin/env python3
"""Quiet coercion errors preserve their actual retired native receipt."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_quiet_zero_coercion_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')


def lifecycle(fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* z_left) z) :: ptask_tail*',
        'S.RESULT = VARIABLE n_right* z_right', 'S.ORIGIN = (porigin_operator)',
        '$lookup(S.ENV, n_left*) = (n_cell_left)',
        '$lookup(S.ENV, n_right*) = (n_cell_right)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror)',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}',
        *prior.seek('S_exit', 'S_capture', 1),
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        *prior.seek('S_retired', 'S_report', 2),
        'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'pobobjectreturn_site = pobobjectreturn_capture[.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror_site)]',
        'pdestructioncleanup_site = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_site pobdeactivate pobreturnerror.SITE n_exception]',
        'S_receipt_site = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_site]]',
        'S_zero = $drive_steps(S_retired, 0)']
    checks = [
        ('actual retired Error receipt needs no operand cells',
         r'~((HCELL n_cell_left) <- S_retired.ALLOCATIONS) /\ ~((HCELL n_cell_right) <- S_retired.ALLOCATIONS) /\ $heap_count(HCELL n_cell_left, $machine_roots(S_retired)) = 0 /\ $heap_count(HCELL n_cell_right, $machine_roots(S_retired)) = 0 /\ ~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $ob_object_division_error_source(S_retired, pfunction, pobreturnerror) /\ $ob_object_source_generated_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ $ob_object_source_kind(pobobjectreturn_capture.SOURCE) = "DivisionByZeroError" /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ S_retired.EVENTS = S_report.EVENTS'),
        ('retired receipts retain compiled source and public validity',
         r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ $ob_object_error_operand_value(S_retired, VARIABLE n_right* z_right, [PCFIELD 1], z) = eps /\ S_zero = S_retired[.COMPLETION = BUDGET] /\ ' + prior.public('S_retired'))]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    path = out / 'source.php'; path.write_bytes(sources.MODULO)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'mode': 'SL_mode/cache=false/det=true', 'native_agreement_credit': 0, 'passed': False}
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources.MODULO).decode()})
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        finally:
            adapter.close()
        (out / 'checked.json').write_text(json.dumps(checked) + '\n')
        bindings, checks = lifecycle(checked['fixture'], path)
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
            ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
            ''.join('  -- if ' + binding + '\n' for binding in bindings))
        watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
            'tests/semantics/output_final_quiet_zero_coercion_sources.py', 'tests/semantics/output_final_division_error_review_state.py',
            'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
            'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
            'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
            '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
        watched += [Path(__file__), path, fixture, out / 'checked.json']
        fp = lambda: {str(p): prior.common.sha(p) for p in watched}
        report.update(groups=[label for label, _ in checks], before=fp())
        started = time.monotonic()
        try:
            result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT / module) for module in modules], str(fixture)], out, 'state', 300)
            report['observed'] = json.loads(result.stdout)
            assert result.returncode == 0 and not result.stderr and report['observed'] == [True] * len(checks), (result.returncode, result.stderr, report['observed'])
        except subprocess.TimeoutExpired as error:
            (out / 'state.stdout').write_bytes(error.stdout or b'')
            (out / 'state.stderr').write_bytes(error.stderr or b'')
            (out / 'state.exit').write_text('timeout\n')
            raise
        finally:
            report.update(seconds=time.monotonic() - started, after=fp())
        assert report['before'] == report['after']
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
