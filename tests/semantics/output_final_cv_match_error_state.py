#!/usr/bin/env python3
"""A generated match fact survives real subject-cell retirement before C0."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_match_error_review_state as match
import output_final_cv_match_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = match.prior


def lifecycle(fixture, path, stage):
    bindings = match.start(fixture, path) + [
        'S.TODO = (MATCH_SCAN porigin_match (VARIABLE n_name* z_origin) n_arm 0) :: ptask_tail*',
        '$match_line(S, porigin_match, eps) = (z)',
        '$lookup(S.ENV, n_name*) = (n_cell)',
        'S_read = $quiet_operand(S, VARIABLE n_name* z_origin)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_match, OBJECT n_exception, MESSAGE $ptascii("Unhandled match case 3"), LINE z}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
    ]
    if stage == 'release':
        bindings += [*prior.seek('S_exit', 'S_capture', 1),
            'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
            'S_exit_zero = $drive_steps(S_exit, 0)']
    checks = [
        ('own private CV is borrowed at the real exhausted transition',
         r'n_name* = $ptascii("s") /\ z_origin = 7 /\ z = 7 /\ S.STORE[n_cell] = DEFINED (PINT 3) /\ $heap_count(HCELL n_cell, $machine_roots(S)) = 1 /\ $heap_owners($heap_graph(S), HCELL n_cell) = 1 /\ $match_scalar(S, porigin_match) = eps /\ $match_table(S, porigin_match) = (false) /\ S_read = S[.RESULT = KNOWN (PINT 3)] /\ S_request = $dz_request(S, z) /\ S_request.EVENTS = S.EVENTS /\ $ob_object_match_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('actual charged capture preserves the current native and Error owners',
         r'S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, (OBJECT_MATCH_ERROR pobreturnerror)) /\ pobobjectreturn_capture.SOURCE = (OBJECT_MATCH_ERROR pobreturnerror) /\ $ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ $heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
        ('real CV release precedes original native C0 without a metadata owner',
         r'~((HCELL n_cell) <- S_exit.ALLOCATIONS) /\ $heap_count(HCELL n_cell, $machine_roots(S_exit)) = 0 /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.CVS = eps /\ S_exit.ENV = eps /\ S_exit.DESTRUCTION.RELEASES = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.VALUE = KNOWN PNULL /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ $ob_object_match_error_source(S_exit, pfunction, pobreturnerror) /\ $ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ S_exit_zero = S_exit[.COMPLETION = BUDGET] /\ ' + prior.public('S_exit')),
    ]
    checks = checks[:2] if stage == 'capture' else [checks[0], checks[2]]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=['capture', 'release'], default='release')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    path = out / 'source.php'; path.write_bytes(sources.SCAN)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'mode': 'AL_mode/cache=false/det=true', 'stage': args.stage, 'native_agreement_credit': 0, 'passed': False}
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources.SCAN).decode()})
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        finally:
            adapter.close()
        (out / 'checked.json').write_text(json.dumps(checked) + '\n')
        bindings, checks = lifecycle(checked['fixture'], path, args.stage)
        fixture = out / 'state.watsup'
        fixture.write_text(match.PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
            ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
            ''.join('  -- if ' + binding + '\n' for binding in bindings))
        watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
            'tests/semantics/output_final_cv_match_error_sources.py', 'tests/semantics/output_final_match_error_review_state.py',
            'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
            'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
            'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
            '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
        watched += [Path(__file__), path, fixture, out / 'checked.json']
        fp = lambda: {str(p): prior.common.sha(p) for p in watched}
        report.update(groups=[label for label, _ in checks], before=fp())
        started = time.monotonic()
        try:
            result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
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
