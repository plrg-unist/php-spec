#!/usr/bin/env python3
"""Noisy own-CV pairs preserve one- and two-cell cleanup through FINAL Errors."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_cv_pair_modulo_warning_error_state as previous
import output_final_default_both_cv_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
CASES = {name: sources.CASES['native-default-both-cv-modulo-conversion-error-' + name]
         for name in ['string-notices', 'same-cv']}
ERROR = 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}'
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'


def shape(name):
    if name == 'same-cv':
        return 7, '0.5x', 0, 'value', 'value', '[$ptascii("value")]', 1, 'n_cell_left = n_cell_right'
    return 8, '1.5x', 1, 'left', 'right', '[$ptascii("left"), $ptascii("right")]', 2, 'n_cell_left =/= n_cell_right'


def bindings_for(name, fixture, path):
    line, left, _, _, _, _, _, _ = shape(name)
    bindings, checks = previous.lifecycle('string-zero', fixture, path)
    notice = 'S_warned = $leading_warning(S, true, z)'
    index = bindings.index(notice)
    bindings[index:index + 1] = [
        f'S_warned_left = $long_string_notices(S, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("{left}"), z)',
        'S_warned = $long_string_notices(S_warned_left, LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps, $ptascii("0.5x"), z)']
    old_error = [binding for binding in bindings if binding.startswith('pobreturnerror = ')]
    assert len(old_error) == 1
    bindings.remove(old_error[0])
    index = bindings.index('S_capture_found = $drive_steps(S, 1)')
    bindings[index:index] = [
        'S_generated.COMPLETION = THROWING n_exception', ERROR,
        'pobobjectreturn_seed = pobobjectreturn[.SOURCE = $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_DIVISION_ERROR pobreturnerror))]',
        'S_seed = $ob_object_final_capture(S_generated, pobobjectreturn, pobobjectreturn_seed.SOURCE)']
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


def original(name):
    line, left, left_int, left_name, right_name, cvs, count, relation = shape(name)
    warning = f'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) {line}'
    deprecated = lambda value: 'DIAGNOSTIC "Deprecated" ' + prior.value(
        b'Implicit conversion from float-string "' + value.encode() + b'" to int loses precision') + ' ' + str(line)
    conditions = [
        f'z = {line}', f'z_left = {line}', f'z_right = {line}',
        f'n_left* = $ptascii("{left_name}")', f'n_right* = $ptascii("{right_name}")',
        f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS', f'|S.ENV| = {count}', relation,
        f'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("{left}"))',
        'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x"))',
        '$compiled_read(S, porigin_left) = eps', '$compiled_read(S, porigin_right) = eps',
        f'$string_long($ptascii("{left}")) = STRINT {left_int} (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps)',
        '$string_long($ptascii("0.5x")) = STRINT 0 (LEADINGNUMBER :: STRINGPRECISIONLOSS :: eps)',
        '$ob_object_modulo_integer(pvalue_left) = eps', '$long_convertible(pvalue_left)',
        '$ob_object_modulo_integer(pvalue_right) = eps', '$long_convertible(pvalue_right)',
        '$ob_object_string_value(S, pvalue_left)', '$ob_object_string_value(S, pvalue_right)',
        '$ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        '$integer_operand_source(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left)',
        '$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) = (8)',
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8)',
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
        f'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})',
        '(HCELL n_cell_left) <- S.ALLOCATIONS', '(HCELL n_cell_right) <- S.ALLOCATIONS',
        '~(n_cell_left <- S.REFCELLS)', '~(n_cell_right <- S.REFCELLS)',
        '$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1', '$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1',
        '$heap_owners($heap_graph(S), HCELL n_cell_left) = 1', '$heap_owners($heap_graph(S), HCELL n_cell_right) = 1',
        'S_left.RESULT = KNOWN pvalue_left', 'S_right.RESULT = KNOWN pvalue_right',
        'S_left.EVENTS = S.EVENTS', 'S_right.EVENTS = S.EVENTS',
        'S_integer_left.COMPLETION = NORMAL', f'S_integer_left.RESULT = KNOWN (PINT {left_int})',
        'S_integer_left.EVENTS = S_warned_left.EVENTS',
        'S_warned_left.EVENTS = [OUTPUT ([80]), ' + warning + ', ' + deprecated(left) + ']',
        'S_integer_right.COMPLETION = NORMAL', 'S_integer_right.RESULT = KNOWN (PINT 0)',
        'S_integer_right.EVENTS = S_warned.EVENTS',
        'S_warned.EVENTS = S_warned_left.EVENTS ++ [' + warning + ', ' + deprecated('0.5x') + ']',
        'S_request = S_reference', 'S_request.RESULT = KNOWN (PINT 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.EVENTS = S_warned.EVENTS', 'S_request.STORE = S.STORE',
        '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        '~$error_handler_eligible(S, 2)', '~$error_handler_eligible(S, 8192)',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)',
        '$ob_object_return_error_live(S_generated, pobreturnerror)']
    return r' /\ '.join(conditions)


def seed_identity():
    return (r'S_generated.FRAMES = [pframe] /\ ptask_native* = pobobjectreturn.TAIL /\ '
        r'S_seed = S_generated[.FRAMES = [pframe[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_seed) :: ptask_native*]]] /\ '
        r'S_seed.STORE = S_generated.STORE /\ S_seed.EVENTS = S_generated.EVENTS /\ '
        r'S_seed.OBJECTS = S_generated.OBJECTS /\ S_seed.ALLOCATIONS = S_generated.ALLOCATIONS /\ '
        r'S_seed.CURRENT = S_generated.CURRENT /\ S_seed.TODO = S_generated.TODO /\ S_seed.COMPLETION = S_generated.COMPLETION /\ '
        r'$machine_roots(S_seed) = $machine_roots(S_generated) /\ $heap_graph(S_seed) = $heap_graph(S_generated) /\ '
        r'$ob_object_source_birth(pobobjectreturn_seed.SOURCE) = eps /\ '
        r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_seed) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn)')


def lifecycle(name, fixture, path):
    line, _, _, _, _, _, _, _ = shape(name)
    bindings, checks = bindings_for(name, fixture, path)
    checks[0] = ('genuine own CV reads retain stored operands through ordered conversion and actual capture',
        original(name) + r' /\ ' + CAPTURE + r' /\ $source_exception_transition(S, S_generated) = S_seed /\ ' +
        seed_identity() + r' /\ S_capture_found = $drive_steps(S_seed, 0) /\ '
        r'S_capture.STORE[n_cell_left] = DEFINED pvalue_left /\ S_capture.STORE[n_cell_right] = DEFINED pvalue_right /\ '
        r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
        r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
        r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    nodes = '[HCELL n_cell_left]' if name == 'same-cv' else '[HCELL n_cell_left, HCELL n_cell_right]'
    jobs = '[DESTRUCTION_VALUE (HCELL n_cell_left)]' if name == 'same-cv' else '[DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)]'
    checks[1] = ('the actual compiled-CV queue releases each private cell once before native C0',
        '$destructor_frame_nodes(S_leave) = ' + nodes + r' /\ $destructor_frame_jobs(S_leave) = ' + jobs + r' /\ '
        'pdestructionrelease.JOBS = ' + jobs + r' /\ S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
        r'$destructor_borrowed_context(S_leave) = (pcallcontext) /\ '
        r'S_queue.CURRENT = eps /\ S_queue.FRAMES = eps /\ S_queue.ORIGIN = eps /\ '
        r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ '
        r'$heap_count(HCELL n_cell_left, $machine_roots(S_queue)) = 1 /\ '
        r'$heap_count(HCELL n_cell_right, $machine_roots(S_queue)) = 1 /\ '
        r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ ' +
        checks[1][1] + r' /\ ' + prior.public('S_queue'))
    def fatal(number):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() +
                b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                b' on line ' + str(number).encode() + b'\n')
    checks[2] = ('C0 preserves the ordered diagnostics and original fatal line after actual CV retirement',
                 checks[2][1].replace(prior.value(fatal(8)), prior.value(fatal(line))).replace(' 8 /\\ ', ' ' + str(line) + ' /\\ '))
    checks[3] = ('the retired receipt retains source without either operand cell or Error ownership', checks[3][1])
    return bindings, checks


def prospective_lifecycle(name, fixture, path):
    bindings, checks = lifecycle(name, fixture, path)
    index = bindings.index('S_capture_found = $drive_steps(S, 1)')
    bindings[index] = 'S_capture_found = $drive_steps(S_seed, 0)'
    checks[0] = ('prospective nonowning annotation drives existing cleanup after genuine raw conversion',
        checks[0][1].replace(CAPTURE, r'$ob_object_division_error_capture(S, S_generated) = eps').replace(
            '$source_exception_transition(S, S_generated) = S_seed', '$source_exception_transition(S, S_generated) = S_generated'))
    return bindings, [('genuine original CV reads and diagnostics reach their exact live Error before capture admission',
                       original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps'), *checks]


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
                'tests/semantics/output_final_default_both_cv_modulo_conversion_error_sources.py',
                'tests/semantics/output_final_default_both_modulo_conversion_error_sources.py',
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
