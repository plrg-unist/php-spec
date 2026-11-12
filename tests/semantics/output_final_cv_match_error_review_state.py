#!/usr/bin/env python3
"""CV match errors bind the real delayed subject without retaining its cell."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_match_error_review_state as match
import output_final_cv_match_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = match.prior
CASES = {
    'authority': sources.SCAN.replace(b'$s = 3;', b'$s = 3;\n        $u = 3;'),
    'table': sources.SCAN.replace(b'$s = 3', b'$s = true').replace(
        b"2 => 'H'", b"1 => 'H', 2 => 'I'"),
    'mutate': sources.MUTATE,
    'catch': sources.CATCH,
    'override': sources.OVERRIDE,
}


def capture(message):
    return [
        'S.TODO = (MATCH_SCAN porigin_match (VARIABLE n_name* z_origin) n_arm 0) :: ptask_tail*',
        'porigin_match = PORIGIN n_unit pcpath_match',
        '$match_line(S, porigin_match, eps) = (z)',
        '$lookup(S.ENV, n_name*) = (n_cell)',
        'S_read = $quiet_operand(S, VARIABLE n_name* z_origin)',
        'S_request = $dz_raw(S)',
        'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_match, OBJECT n_exception, MESSAGE ' + prior.value(message) + ', LINE z}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_capture_found = $drive_steps(S, 1)',
        'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
    ]


def authority(fixture, path):
    bindings = match.start(fixture, path) + capture(b'Unhandled match case 3') + [
        '$lookup(S.ENV, $ptascii("u")) = (n_other)',
        'S_fake = S[.TODO = (MATCH_SCAN porigin_match (VARIABLE ($ptascii("u")) z_origin) n_arm 0) :: ptask_tail*]',
        'S_fake_request = $dz_raw(S_fake)',
        'S_fake_generated = $throwable_transition(S_fake, S_fake_request)',
        'S_line = S[.TODO = (MATCH_SCAN porigin_match (VARIABLE n_name* $(z_origin + 1)) n_arm 0) :: ptask_tail*]',
        'S_ref = S[.REFCELLS = S.REFCELLS ++ [n_cell]]',
        'S_extra = S[.HELD = [HCELL n_cell]]',
        'S_undefined = S[.STORE = $set_cell(S.STORE, n_cell, UNDEFINED)]',
        'S_owning = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED (POBJECT n_object))]',
        'S_backed = S[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_cell, LINE z, VALUE n_name*}]]',
        'S_borrowed = S[.BORROWEDREAD = ({SITE porigin_match, OP IDENTICAL, LEFT n_name*, LEFTLINE z_origin, RIGHT n_name*, LINE z, CELL n_cell, BASE S.BASE})]',
        'pfunction_unit = pfunction[.CODE = pfunction.CODE[.UNIT = $(n_unit + 1)]]',
        'pfunction_cvs = pfunction[.CVS = eps]',
        'pfunction_global = pfunction[.CODE = pfunction.CODE[.GLOBALS = [pcpath_match]]]',
        'pfunction_static = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = pfunction.CODE.EXPRESSIONS ++ [CODESTATIC pcpath_match n_name* z_origin z false]]]',
        'pfunction_line = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = [CODEEXPR (pcpath_match ++ [PCFIELD 0]) $(z_origin + 1) false]]]',
        'pfunction_fold = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = [CODEEXPR (pcpath_match ++ [PCFIELD 0]) z_origin true]]]',
        'pvalue_carrier = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("bad"))',
        'S_carrier = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED pvalue_carrier)][.STRINGDATA = S.STRINGDATA ++ [$ptascii("bad")]]',
        'S_carrier_invalid = S_carrier[.STRINGDATA = S.STRINGDATA]',
        'S_rebound = S_capture[.STORE = $set_cell(S_capture.STORE, n_cell, DEFINED (PINT 99))]',
        'pobreturnerror_message = pobreturnerror[.MESSAGE = $ptascii("Unhandled match case 99")]',
        'pobobjectreturn_message = pobobjectreturn_capture[.SOURCE = (OBJECT_MATCH_ERROR pobreturnerror_message)]',
        'S_message = S_capture[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_message) :: ptask_native*]]]',
    ]
    checks = [
        ('real private CV read and materialized request keep the current subject',
         r'n_name* = $ptascii("s") /\ n_cell =/= n_other /\ S.STORE[n_cell] = DEFINED (PINT 3) /\ S.STORE[n_other] = DEFINED (PINT 3) /\ $match_scalar(S, porigin_match) = eps /\ $match_table(S, porigin_match) = (false) /\ S_read = S[.RESULT = KNOWN (PINT 3)] /\ S_request = $dz_request(S, z) /\ S_request.EVENTS = S.EVENTS /\ $ob_object_match_error_operand(S, porigin_match, VARIABLE n_name* z_origin, z) /\ $ob_object_match_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, (OBJECT_MATCH_ERROR pobreturnerror))'),
        ('equal wrong-CV errors and wrong source lines cannot mint authority',
         r'$call_current_valid(S_fake) /\ S_fake_request = S_request /\ S_fake_generated = S_generated /\ $ob_object_match_error_source(S_fake_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_fake_generated, pobreturnerror) /\ ~$match_operand_valid(S_fake, porigin_match, VARIABLE ($ptascii("u")) z_origin) /\ $ob_object_match_error_capture(S_fake, S_fake_generated) = eps /\ $dz_raw(S_line) = S_request /\ $ob_object_match_error_capture(S_line, S_generated) = eps /\ $ob_object_match_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps'),
        ('raw reference undefined owning backed and borrowed reads stay outside',
         r'$quiet_operand(S_ref, VARIABLE n_name* z_origin) = S_ref[.RESULT = KNOWN (PINT 3)] /\ $match_error_text(S_ref, VARIABLE n_name* z_origin, PINT 3) = $ptascii("of type int") /\ ~$ob_object_match_error_operand(S_ref, porigin_match, VARIABLE n_name* z_origin, z) /\ $quiet_operand(S_undefined, VARIABLE n_name* z_origin) = S_undefined[.RESULT = KNOWN PNULL] /\ ~$ob_object_match_error_operand(S_undefined, porigin_match, VARIABLE n_name* z_origin, z) /\ ~$ob_object_match_error_operand(S_extra, porigin_match, VARIABLE n_name* z_origin, z) /\ ~$ob_object_match_error_operand(S_owning, porigin_match, VARIABLE n_name* z_origin, z) /\ ~$ob_object_match_error_operand(S_backed, porigin_match, VARIABLE n_name* z_origin, z) /\ ~$ob_object_match_error_operand(S_borrowed, porigin_match, VARIABLE n_name* z_origin, z)'),
        ('retained source shape requires its own compiled private literal CV',
         r'$ob_object_match_subject_source(S_capture, pfunction, porigin_match) /\ ~$ob_object_match_subject_source(S_capture, pfunction_unit, porigin_match) /\ ~$ob_object_match_subject_source(S_capture, pfunction_cvs, porigin_match) /\ ~$ob_object_match_subject_source(S_capture, pfunction_global, porigin_match) /\ ~$ob_object_match_subject_source(S_capture, pfunction_static, porigin_match) /\ ~$ob_object_match_subject_source(S_capture, pfunction_line, porigin_match) /\ ~$ob_object_match_subject_source(S_capture, pfunction_fold, porigin_match)'),
        ('string carrier identity is checked before borrowing the subject',
         r'$string_carrier_valid(S_carrier, pvalue_carrier) /\ $value_nodes(pvalue_carrier) = eps /\ $ob_object_match_error_operand(S_carrier, porigin_match, VARIABLE n_name* z_origin, z) /\ ~$ob_object_match_error_operand(S_carrier_invalid, porigin_match, VARIABLE n_name* z_origin, z)'),
        ('issued error freezes the message rather than rereading the live CV',
         r'pobobjectreturn_capture.SOURCE = (OBJECT_MATCH_ERROR pobreturnerror) /\ $ob_object_match_error_source(S_rebound, pfunction, pobreturnerror) /\ $ob_object_source_live(S_rebound, pobobjectreturn_capture.SOURCE) /\ $ob_object_final_saved_context(S_rebound) = ((pcallcontext, pobobjectreturn_capture)) /\ $ob_object_final_saved_context(S_message) = eps /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1'),
        ('charged driver uses real capture and Throwable administration',
         r'S_capture = $throwable_begin($literal_reference_debt_step(S, $sensitive_trace_freeze(S_observed))) /\ S_capture.RESULT = KNOWN PNULL /\ S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*'),
        ('charged state remains publicly valid', prior.public('S_capture')),
    ]
    return bindings, checks


def table(fixture, path):
    bindings = match.start(fixture, path) + capture(b'Unhandled match case true')
    checks = [
        ('table fallback preserves a bool CV and the real raw Error text',
         r'S.STORE[n_cell] = DEFINED (PBOOL true) /\ $match_scalar(S, porigin_match) = eps /\ $match_table(S, porigin_match) = (true) /\ $code_match_table(pfunction.CODE.EXPRESSIONS, pcpath_match) = (true) /\ S_read = S[.RESULT = KNOWN (PBOOL true)] /\ S_request = $dz_request(S, z) /\ $ob_object_match_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ $ob_object_match_subject_source(S_capture, pfunction, porigin_match) /\ $ob_object_match_error_source(S_capture, pfunction, pobreturnerror)'),
        ('table capture keeps the same native and Error owner counts',
         r'pobobjectreturn_capture.SOURCE = (OBJECT_MATCH_ERROR pobreturnerror) /\ $heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
    ]
    return bindings, checks


def mutate(fixture, path):
    bindings = match.start(fixture, path) + capture(b'Unhandled match case 4') + [
        *prior.seek('S_exit', 'S_capture', 1),
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_zero = $drive_steps(S_exit, 0)',
    ]
    checks = [
        ('scan Error reads the condition-mutated subject rather than its initializer',
         r'S.STORE[n_cell] = DEFINED (PINT 4) /\ $match_table(S, porigin_match) = (false) /\ S_read = S[.RESULT = KNOWN (PINT 4)] /\ S_request = $dz_request(S, z) /\ $ob_object_match_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ pobobjectreturn_capture.SOURCE = (OBJECT_MATCH_ERROR pobreturnerror)'),
        ('actual CV retirement leaves the frozen error and original C0 ready',
         r'~((HCELL n_cell) <- S_exit.ALLOCATIONS) /\ $heap_count(HCELL n_cell, $machine_roots(S_exit)) = 0 /\ S_exit.CVS = eps /\ S_exit.ENV = eps /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.DESTRUCTION.RELEASES = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ $ob_object_match_error_source(S_exit, pfunction, pobreturnerror) /\ $ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ S_zero = S_exit[.COMPLETION = BUDGET] /\ ' + prior.public('S_exit')),
    ]
    return bindings, checks


def clearing(name, fixture, path):
    bindings, checks = match.clearing(name, fixture, path)
    bindings = [binding.replace('MATCH_SCAN porigin_operator (KNOWN (PINT z_subject))',
                                'MATCH_SCAN porigin_operator (VARIABLE n_name* z_origin)')
                for binding in bindings]
    bindings += ['$lookup(S.ENV, n_name*) = (n_cell)']
    checks = [(label, condition.replace('S_caught.CVS = eps /\\ S_caught.ENV = eps',
                                        'S_caught.CVS = S.CVS /\\ S_caught.ENV = S.ENV'))
              for label, condition in checks]
    checks.insert(0, ('real CV match history exists before the in-body override',
        r'pobobjectreturn_capture.SOURCE = (OBJECT_MATCH_ERROR pobreturnerror) /\ $heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1'))
    label, condition = checks[-1]
    checks[-1] = (label, condition + r' /\ ~((HCELL n_cell) <- S_restored.ALLOCATIONS) /\ $heap_count(HCELL n_cell, $machine_roots(S_restored)) = 0')
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
    watched = [ROOT / rel for rel in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/output_final_cv_match_error_sources.py',
        'tests/semantics/output_final_match_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py',
        'tests/semantics/output_deprecation_warning_review_state.py',
        'tests/semantics/output_api_failure_sources.py', 'tests/semantics/recorded_worker.py']]
    watched.append(Path(__file__))
    fingerprint = lambda: {str(path): prior.common.sha(path) for path in watched}
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'mode': 'AL_mode/cache=false/det=true', 'native_agreement_credit': 0,
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
                assert parsed['accepted'], parsed
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = (clearing(name, checked['fixture'], path) if name in ('catch', 'override')
                                else globals()[name](checked['fixture'], path))
            fixture = directory / 'state.watsup'
            fixture.write_text(match.PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            local = [path, fixture, directory / 'checked.json']
            record = {'id': name, 'source_sha256': hashlib.sha256(CASES[name]).hexdigest(),
                      'groups': [label for label, _ in checks],
                      'before': {str(item): prior.common.sha(item) for item in local}, 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record['prepared'] = True
                continue
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
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
                record.update(seconds=time.monotonic() - started,
                              after={str(item): prior.common.sha(item) for item in local})
            assert record['before'] == record['after'], 'fixture inputs changed'
            print(name, record['passed'], flush=True)
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
