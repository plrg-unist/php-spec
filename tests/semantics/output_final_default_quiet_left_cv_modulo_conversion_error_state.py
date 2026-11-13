#!/usr/bin/env python3
"""Quiet left CVs retain one- and two-cell cleanup after noisy RHS MOD conversion."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_cv_modulo_conversion_error_state as shared
import output_final_default_left_cv_modulo_warning_error_state as single
import output_final_default_quiet_left_cv_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = shared.division
prior = shared.prior
PREFIX = shared.PREFIX
CASES = {form: sources.CASES['native-default-quiet-left-cv-modulo-conversion-error-' + form + '-both']
         for form in ['constant', 'cv']}
ERROR = shared.ERROR
CAPTURE = shared.CAPTURE


def bindings_for(form, fixture, path):
    base = single if form == 'constant' else shared.previous
    bindings, checks = base.lifecycle('float-prefix' if form == 'constant' else 'string-zero', fixture, path)
    if form == 'constant':
        bindings = [binding for binding in bindings if 'n_cell_other' not in binding and 'S_other' not in binding]
        checks = [(label, r' /\ '.join(part for part in condition.split(r' /\ ') if 'n_cell_other' not in part))
                  for label, condition in checks[:4]]
    notice = 'S_warned = $leading_warning(S, true, z)'
    assert bindings.count(notice) == 1
    bindings = [
        'S_warned = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("0.5x"), z)'
        if binding == notice else binding for binding in bindings]
    old_error = [binding for binding in bindings if binding.startswith('pobreturnerror = ')]
    assert len(old_error) == 1
    bindings.remove(old_error[0])
    index = bindings.index('S_capture_found = $drive_steps(S, 1)')
    bindings[index:index] = [
        'S_generated.COMPLETION = THROWING n_exception', ERROR,
        'pobobjectreturn_seed = pobobjectreturn[.SOURCE = $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_DIVISION_ERROR pobreturnerror))]',
        'S_seed = $ob_object_final_capture(S_generated, pobobjectreturn, pobobjectreturn_seed.SOURCE)',
        'S_seed_post = $literal_reference_debt_step(S, $sensitive_trace_freeze(S_seed))']
    old_seek = prior.seek('S_exit', 'S_capture', 1)
    index = bindings.index(old_seek[0])
    assert bindings[index:index + len(old_seek)] == old_seek
    bindings[index:index + len(old_seek)] = [
        *prior.seek('S_leave', 'S_capture', 8),
        'S_queue_found = $drive_steps(S_leave, 1)', 'S_queue_found.COMPLETION = BUDGET',
        'S_queue = S_queue_found[.COMPLETION = NORMAL]',
        'S_queue.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        *prior.seek('S_exit', 'S_queue', 1)]
    return bindings, checks


def original(form):
    line = 7 if form == 'constant' else 8
    conditions = [
        f'z = {line}', f'z_left = {line}', 'n_left* = $ptascii("left")',
        'pfunction.CVS = ' + ('[$ptascii("left")]' if form == 'constant' else '[$ptascii("left"), $ptascii("right")]'),
        'S.CVS = pfunction.CVS', '|S.ENV| = ' + ('1' if form == 'constant' else '2'),
        'pvalue_left = PINT 1', '$compiled_read(S, porigin_left) = eps',
        'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x"))',
        '$string_long($ptascii("0.5x")) = STRINT 0 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps)',
        '$ob_object_modulo_integer(pvalue_left) = (1)', '$ob_object_modulo_integer(pvalue_right) = eps',
        '$long_convertible(pvalue_right)', '$ob_object_string_value(S, pvalue_right)',
        '$ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        '$integer_operand_source(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left)',
        '$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) = (8)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = ' + ('(1)' if form == 'constant' else '(8)'),
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})',
        '(HCELL n_cell_left) <- S.ALLOCATIONS', '~(n_cell_left <- S.REFCELLS)',
        '$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1', '$heap_owners($heap_graph(S), HCELL n_cell_left) = 1',
        'S_left.RESULT = KNOWN (PINT 1)', 'S_right.RESULT = KNOWN pvalue_right',
        'S_left.EVENTS = S.EVENTS', 'S_right.EVENTS = S.EVENTS',
        'S_integer_left.COMPLETION = NORMAL', 'S_integer_left.RESULT = KNOWN (PINT 1)', 'S_integer_left.EVENTS = S.EVENTS',
        'S_integer_right.COMPLETION = NORMAL', 'S_integer_right.RESULT = KNOWN (PINT 0)', 'S_integer_right.EVENTS = S_warned.EVENTS',
        'S_warned.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) ' + str(line) +
        ', DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision') + ' ' + str(line) + ']',
        'S_request = S_reference', 'S_request.RESULT = KNOWN (PINT 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.EVENTS = S_warned.EVENTS', 'S_request.STORE = S.STORE',
        '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        '~$error_handler_eligible(S, 2)', '~$error_handler_eligible(S, 8192)',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)', '$ob_object_return_error_live(S_generated, pobreturnerror)']
    if form == 'constant':
        conditions += ['pvalue_right_compiled = PSTRING ($ptascii("0.5x"))',
                       'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled)']
    else:
        conditions += [f'z_right = {line}', 'n_right* = $ptascii("right")', '$compiled_read(S, porigin_right) = eps',
                       'n_cell_left =/= n_cell_right', '(HCELL n_cell_right) <- S.ALLOCATIONS', '~(n_cell_right <- S.REFCELLS)',
                       '$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1', '$heap_owners($heap_graph(S), HCELL n_cell_right) = 1']
    return r' /\ '.join(conditions)


def frontier(form, fixture, path):
    bindings, _ = bindings_for(form, fixture, path)
    index = bindings.index('pobobjectreturn_seed = pobobjectreturn[.SOURCE = $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_DIVISION_ERROR pobreturnerror))]')
    return bindings[:index], [('genuine quiet left CV and noisy RHS reach their exact Error before capture admission', original(form))]


def lifecycle(form, fixture, path):
    line = 7 if form == 'constant' else 8
    bindings, checks = bindings_for(form, fixture, path)
    checks[0] = ('own quiet left CV retains original source and storage through actual RHS conversion and capture',
        original(form) + r' /\ ' + CAPTURE + r' /\ $source_exception_transition(S, S_generated) = S_seed /\ ' +
        shared.seed_identity() + r' /\ ' + shared.post_identity() + r' /\ S_capture_found = $drive_steps(S_seed_post, 0) /\ '
        r'S_capture.STORE[n_cell_left] = DEFINED pvalue_left /\ ' +
        (r'S_capture.STORE[n_cell_right] = DEFINED pvalue_right /\ ' if form == 'cv' else '') +
        r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
        r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
        r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    nodes = '[HCELL n_cell_left]' if form == 'constant' else '[HCELL n_cell_left, HCELL n_cell_right]'
    jobs = '[DESTRUCTION_VALUE (HCELL n_cell_left)]' if form == 'constant' else '[DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)]'
    checks[1] = ('the actual compiled-CV queue retires one or two original private cells before C0',
        '$destructor_frame_nodes(S_leave) = ' + nodes + r' /\ $destructor_frame_jobs(S_leave) = ' + jobs + r' /\ '
        'pdestructionrelease.JOBS = ' + jobs + r' /\ S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
        r'$destructor_borrowed_context(S_leave) = (pcallcontext) /\ S_queue.CURRENT = eps /\ S_queue.FRAMES = eps /\ S_queue.ORIGIN = eps /\ '
        r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ ' +
        (r'S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ ' if form == 'cv' else '') +
        r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ ' + checks[1][1] + r' /\ ' + prior.public('S_queue'))
    def fatal(number):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() +
                b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                b' on line ' + str(number).encode() + b'\n')
    checks[2] = ('C0 preserves the RHS Warning and Deprecated before the original fatal trace',
        checks[2][1].replace(prior.value(fatal(8)), prior.value(fatal(line))).replace(' 8 /\\ ', ' ' + str(line) + ' /\\ '))
    checks[3] = ('the retired source receipt owns neither private operand cells nor its actual Error', checks[3][1])
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'source_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            source = CASES[name]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = lifecycle(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
                'tests/semantics/output_final_default_quiet_left_cv_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_both_cv_modulo_conversion_error_state.py',
                'tests/semantics/output_final_default_left_cv_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_pair_modulo_warning_error_state.py',
                'tests/semantics/output_final_default_cv_pair_modulo_warning_error_sources.py',
                'tests/semantics/output_final_modulo_error_sources.py',
                'tests/semantics/output_final_modulo_error_review_state.py',
                'tests/semantics/output_final_division_error_sources.py',
                'tests/semantics/output_final_division_error_review_state.py',
                'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
                'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
                'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
            watched += [Path(__file__), path, fixture, directory / 'checked.json']
            fp = lambda: {str(p): prior.common.sha(p) for p in watched}
            record = {'id': name, 'groups': [label for label, _ in checks], 'before': fp(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
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
        assert report['revision'] == report['after_revision'], 'revision changed'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
