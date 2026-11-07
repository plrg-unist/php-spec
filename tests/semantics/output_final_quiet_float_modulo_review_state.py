#!/usr/bin/env python3
"""Quiet float modulo keeps exact kernel authority and clears consumed errors."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_modulo_error_review_state as modulo
import output_final_quiet_float_modulo_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = modulo.prior
CASES = {'authority': sources.RIGHT_FLOAT, 'catch': sources.CATCH, 'override': sources.OVERRIDE}
PREFIX = modulo.PREFIX.replace('BINARY_RIGHT MODULO (KNOWN (PINT 1)) z',
                               'BINARY_RIGHT MODULO (KNOWN pvalue_left) z')


def authority(fixture, path):
    bindings = modulo.division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right', 'S.ORIGIN = (porigin_operator)',
        'S_inputs = $resolve_at($resolve_at($hold_task_inputs(S), KNOWN pvalue_left, z), S.RESULT, z)',
        'S_left = $integer_coerce(S_inputs, pvalue_left, z)',
        'S_right = $integer_coerce(S_left, pvalue_right, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*']
    checks = [
        ('fresh right-float source retains ordered54 and exact152 scratch',
         r'pvalue_left = PINT 1 /\ pvalue_right = PFLOAT 0 /\ z = 6 /\ S_left.RESULT = KNOWN (PINT 1) /\ S_right.RESULT = KNOWN (PINT 0) /\ S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ S_request = $dz_request(S, z) /\ S_request = $integer_result(S_right, $integer_binary(MODULO, 1, 0), z)[.HELD = S.HELD] /\ S_request.RESULT = KNOWN (PINT 0) /\ S_request.RESULT =/= S.RESULT /\ S_request.TODO = ptask_tail* /\ S_request.EVENTS = S.EVENTS /\ S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 6 /\ S_generated.RESULT = KNOWN (PARRAY 0)'),
        ('actual observer admits native metadata without adding roots',
         r'$ob_object_division_operands(MODULO, pvalue_left, pvalue_right) /\ $ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_generated, pobreturnerror) /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_DIVISION_ERROR pobreturnerror))) /\ pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror) /\ $ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
        ('same error kind cannot replace the real successor or operand proof',
         r'$ob_object_division_error_capture(S, S_generated[.RESULT = S.RESULT]) = eps /\ $ob_object_division_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ $ob_object_division_error_capture(S, S_generated[.EVENTS = S.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps /\ $ob_object_division_error_capture(S[.TODO = (BINARY_RIGHT DIVIDE (KNOWN pvalue_left) z) :: ptask_tail*], S_generated) = eps /\ $ob_object_division_error_capture(S[.RESULT = KNOWN (PFLOAT 4602678819172646912)], S_generated) = eps /\ $ob_object_division_error_capture(S[.RESULT = KNOWN PNULL], S_generated) = eps /\ $ob_object_division_error_capture(S[.RESULT = KNOWN (PBOOL false)], S_generated) = eps /\ $ob_object_division_error_capture(S[.RESULT = KNOWN (PSTRING ($ptascii("0")))], S_generated) = eps'),
        ('quiet normalization is symmetric at zero and signed range edges',
         r'$ob_object_modulo_integer(PINT 0) = (0) /\ $ob_object_division_operands(MODULO, PFLOAT 4607182418800017408, PINT 0) /\ $ob_object_division_operands(MODULO, PINT 1, PFLOAT 0) /\ $ob_object_modulo_integer(PFLOAT 9223372036854775808) = (0) /\ $ob_object_modulo_integer(PFLOAT 13830554455654793216) = ($(-1)) /\ $ob_object_modulo_integer(PFLOAT 14114281232179134464) = ($(-9223372036854775808)) /\ $ob_object_modulo_integer(PFLOAT 4890909195324358655) = (9223372036854774784) /\ $ob_object_modulo_integer(PFLOAT 4890909195324358656) = eps /\ $ob_object_modulo_integer(PFLOAT 14114281232179134465) = eps /\ $ob_object_modulo_integer(PFLOAT 1) = eps /\ $ob_object_modulo_integer(PFLOAT 9223372036854775809) = eps /\ ~$ob_object_division_operands(MODULO, PINT 1, PFLOAT 4602678819172646912) /\ ~$ob_object_division_operands(MODULO, PFLOAT 4602678819172646912, PINT 0) /\ $ob_object_division_operands(DIVIDE, PFLOAT 4602678819172646912, PFLOAT 0) /\ ~$ob_object_division_operands(SHIFTLEFT, PFLOAT 4607182418800017408, PINT 0)')]
    return bindings, checks


def clearing(name, fixture, path):
    bindings, checks = getattr(modulo, name)(fixture, path)
    bindings = [binding.replace('BINARY_RIGHT MODULO (KNOWN (PINT 1)) z',
                                'BINARY_RIGHT MODULO (KNOWN (PFLOAT 4607182418800017408)) z')
                for binding in bindings]
    checks.insert(0, ('both original floats produce one genuine quiet error before clearing',
        r'S.RESULT = KNOWN (PFLOAT 0) /\ S_request.RESULT = KNOWN (PINT 0) /\ S_request.EVENTS = S.EVENTS /\ S_generated.RESULT = KNOWN (PARRAY 0) /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ pobobjectreturn_capture.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror) /\ ' + prior.public('S_capture')))
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-quiet-float-modulo-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    head = lambda: subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()
    report = {'revision': head(), 'mode': 'SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300, 'records': [], 'passed': False}
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    inputs = modules + ['spec/php.watsup', 'spec/semantics/modules.json', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/recorded_worker.py',
        'tests/semantics/output_final_quiet_float_modulo_sources.py',
        'tests/semantics/output_final_modulo_error_review_state.py',
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
