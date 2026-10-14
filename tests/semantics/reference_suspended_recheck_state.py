"""Emit late typed-reference recheck error and successful Fiber delivery checks."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_active_finalizer_state import PREFIX
from reference_orphaned_cv_state import QUIET, public, sha
from request_environment_state import request_fixture

HEAD = 'ee915d448d1b148735c841401c7d6ead940ab7c0'
REPORT_SHA = '4e32c88a1e26b8f6581620724d790b76e9bc0f4b576151fbbf6e1ec23c51c0d5'
MESSAGE = 'f(): Return value must be of type int, string returned'
INPUTS = {
    'bad': ('5ae948e2f7f3cc0b89d934fedbddf645368c066013c5a61a4db01198f3781f47',
            'ade3c341d2ebf19a706c1100fb750bc31aef0bc4c208fc46d3ce7914cca5d5e6',
            '7c04e493615a99f0a156d61590c4fb3e1694e056d0e1bb2be32c00b176a2db79',
            'B:1;S:1;T:0;T:' + MESSAGE + ';S2:0;T2:1;X:bad;E;'),
    'int': ('ad01b861077ec7c5874eb153c0f9de0fcd81c96af6eaef3199fcd3187cd4be9c',
            '5dd3ded0b047f10d9c7c7f530fee032e1ded598ec7fc77af420757438feefdc4',
            '6bec264c8b706e0bc0e6131320818bb9bf24385da6aed9e25a850e274294788a',
            'B:1;R:2;A:3;S:0;T:1;S2:0;T2:1;X:3;E;'),
}
ERROR_TASK = r'''
dec $sr_error_task(ptask) : ptask?
def $sr_error_task(FINALLY_RESUME porigin (n)) = (FINALLY_RESUME porigin (n))
def $sr_error_task(ptask) = eps -- otherwise
dec $sr_error_tasks(ptask*) : ptask?
def $sr_error_tasks(eps) = eps
def $sr_error_tasks(ptask :: ptask_tail*) = (ptask_error)
  -- if $sr_error_task(ptask) = (ptask_error)
def $sr_error_tasks(ptask :: ptask_tail*) = $sr_error_tasks(ptask_tail*)
  -- if $sr_error_task(ptask) = eps
'''


def source_f(state):
    return ['pcallcontext_f.FUNCTION = PORIGIN n_unit ([PCINDEX 1])',
            f'$function_at($all_functions({state}), pcallcontext_f.FUNCTION) = (pfunction_f)',
            'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
            'pfunction_f.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]',
            '$origin_child((pcallcontext_f.FUNCTION), [PCFIELD 5, PCINDEX 1]) = (porigin_owner)',
            '$origin_child((porigin_owner), [PCFIELD 0, PCINDEX 0]) = (porigin_return)',
            f'$origin_node({state}.SOURCES, porigin_return) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return)',
            '$base64(text_x) = $ptascii("x")',
            'pcallcontext_worker.TARGET = CLOSURE_TARGET n_worker',
            '$origin_child((PORIGIN n_unit ([PCINDEX 2])), [PCFIELD 0, PCFIELD 1, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (pcallcontext_worker.FUNCTION)',
            'pcallcontext_f.CALLSITE = (porigin_call)',
            '$origin_child((pcallcontext_worker.FUNCTION), [PCFIELD 6, PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 1]) = (porigin_call)',
            f'$origin_node({state}.SOURCES, porigin_call) = (NExprFuncCall (NName (BYTES text_f) metadata_f) (SEQUENCE eps) metadata_call)',
            '$base64(text_f) = $ptascii("f")']


def global_cell(state, value):
    return [f'$fiber_globals({state}) = psymboltable_{state}',
            f'$lookup(psymboltable_{state}.ENV, $ptascii("x")) = (n_cell)',
            f'{state}.STORE[n_cell] = DEFINED {value}',
            f'n_cell <- {state}.REFCELLS', f'(HCELL n_cell) <- {state}.ALLOCATIONS']


def preserved(state):
    return [f'{state}.OBJECTS[n_error] = THROWABLE pthrowable_error',
            f'$throwable_previous_id({state}, n_error) = eps',
            f'$throwable_field({state}, n_error, "line") = PINT 2',
            f'$throwable_field({state}, n_error, "trace") = PARRAY n_trace',
            f'$trace_graph_valid({state}, n_trace)',
            f'$heap_reach([HARRAY n_trace], eps, $heap_graph({state}).EDGES) = pnode_trace*',
            f'({state}.ARRAYS[n_trace_part] = S_parked.ARRAYS[n_trace_part])*']


def drained(state):
    return [f'{state}.CURRENT = eps', f'{state}.FRAMES = eps', f'{state}.HELD = eps',
            f'{state}.RETIREDOWNERS = eps', f'{state}.ACTIVEFIBER = eps',
            f'{state}.FIBERCALLERS = eps', f'{state}.FIBERCLOSERS = eps',
            f'{state}.DESTRUCTION.CALLS = eps', f'{state}.DESTRUCTION.RELEASES = eps',
            f'{state}.DESTRUCTION.OPERATIONS = eps', f'{state}.DESTRUCTION.FRAMES = eps']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.raw / 'report.json'
    assert sha(report_path) == REPORT_SHA
    report = json.loads(report_path.read_text())
    assert report['revision'] == report['head_after'] == HEAD and report['status_after'] == ''
    assert report['complete'] and report['passed'] and report['workers_closed']
    assert report['model_evaluations'] == report['source_agreements'] == 2
    assert report['pins'] == report['pins_after'] and report['module_stats'] == report['module_stats_after']
    rows = {row['id']: row for row in report['results']}
    assert rows.keys() == INPUTS.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for case, (source_sha, checked_sha, request_sha, expected) in INPUTS.items():
        directory = args.raw / case
        checked_path, request_path = directory / 'checked.json', directory / 'request.json'
        assert sha(checked_path) == checked_sha and sha(request_path) == request_sha
        checked, facts = json.loads(checked_path.read_text()), json.loads(request_path.read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert sha(source) == rows[case]['source_sha256'] == source_sha
        for engine in ('native', 'model'):
            assert base64.b64decode(rows[case][engine]['stdout']) == expected.encode()
            assert base64.b64decode(rows[case][engine]['stderr']) == b''
            assert rows[case][engine]['exit_status'] == 0
        assert checked['ok'] and checked['fixture']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET']
        stages = {}
        if case == 'bad':
            stages[1] = ['$af_outputs(S.EVENTS) = $ptascii("B:1;S:1;T:0;")',
                '$fiber_globals(S) = psymboltable', '$lookup(psymboltable.ENV, $ptascii("w")) = (n_w)',
                'S.STORE[n_w] = DEFINED (POBJECT n_fiber)', '$fiber_at(S, n_fiber) = (pfiber)',
                'pfiber.STATUS = FIBER_SUSPENDED', 'pfiber.VM = (pfibervm)',
                '$sr_error_tasks(pfibervm.TODO) =/= eps']
            stages[2] = ['$af_outputs(S.EVENTS) = $ptascii("B:1;S:1;T:0;")',
                'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)']
            prefix = 'B:1;S:1;T:0;T:' + MESSAGE + ';'
            assertions += ['S_parked = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
                'S_parked.COMPLETION = NORMAL', '$af_stage(S_parked, 1)',
                '$fiber_globals(S_parked) = psymboltable_parked',
                '$lookup(psymboltable_parked.ENV, $ptascii("w")) = (n_w)',
                'S_parked.STORE[n_w] = DEFINED (POBJECT n_fiber)',
                '$fiber_at(S_parked, n_fiber) = (pfiber_parked)',
                'pfiber_parked.STATUS = FIBER_SUSPENDED', 'pfiber_parked.VM = (pfibervm)',
                'pfibervm.CURRENT = (pcallcontext_f)',
                'pfibervm.FRAMES = pframe_worker :: pframe_tail*',
                'pframe_worker.CONTEXT = (pcallcontext_worker)',
                '$sr_error_tasks(pfibervm.TODO) = (FINALLY_RESUME porigin_owner (n_error))',
            ] + source_f('S_parked') + global_cell('S_parked', 'pvalue_bad') + [
                '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
                'S_parked.OBJECTS[n_error] = THROWABLE pthrowable_error',
                'pthrowable_error.KIND = "TypeError"',
                'pthrowable_error.ORIGIN = (pcallcontext_f.FUNCTION)',
                '$string_bytes($throwable_field(S_parked, n_error, "message")) = ($ptascii("' + MESSAGE + '"))',
                '$throwable_previous_id(S_parked, n_error) = eps',
                '$throwable_field(S_parked, n_error, "line") = PINT 2',
                '$throwable_field(S_parked, n_error, "trace") = PARRAY n_trace',
                '$trace_graph_valid(S_parked, n_trace)',
                'pnode_trace* = $heap_reach([HARRAY n_trace], eps, $heap_graph(S_parked).EDGES)',
                'pnode_trace* = (HARRAY n_trace_part)*',
            ] + public('S_parked') + [
                'S_catch = $af_find($drive_steps(S_parked, 1), 2000, 2)',
                'S_catch.COMPLETION = NORMAL', '$af_stage(S_catch, 2)',
                'S_catch.CURRENT = (pcallcontext_worker)', 'S_catch.ACTIVEFIBER = (n_fiber)',
                '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
                'S_catch.STORE[n_e] = DEFINED (POBJECT n_error)',
                '$lookup(S_catch.ENV, $ptascii("r")) = eps',
                '$lookup(S_catch.ENV, $ptascii("a")) = eps',
            ] + global_cell('S_catch', 'pvalue_bad') + preserved('S_catch') + public('S_catch')
            previous, budget_state = 'S_catch', 'S_catch'
        else:
            stages[1] = ['$af_outputs(S.EVENTS) = $ptascii("B:1;")',
                '$af_function(S, $ptascii("f"))',
                'S.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) 2 true porigin_return) :: ptask_tail*',
                'S.STORE[n_cell] = DEFINED (PINT 2)']
            stages[2] = ['$af_outputs(S.EVENTS) = $ptascii("B:1;")',
                'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                'S.RESULT = REFERENCE n_cell', '$lookup(S.ENV, $ptascii("r")) = eps']
            stages[3] = ['$af_outputs(S.EVENTS) = $ptascii("B:1;")',
                'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("r")) = (n_cell)', '$lookup(S.ENV, $ptascii("a")) = (n_cell)']
            stages[4] = ['$af_outputs(S.EVENTS) = $ptascii("B:1;R:2;")',
                'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("r")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (PINT 3)']
            prefix = 'B:1;R:2;A:3;'
            assertions += ['S_selected = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
                'S_selected.COMPLETION = NORMAL', '$af_stage(S_selected, 1)',
                'S_selected.CURRENT = (pcallcontext_f)', 'S_selected.ACTIVEFIBER = (n_fiber)',
                'S_selected.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) 2 true porigin_return) :: ptask_selected*',
                'S_selected.FRAMES = pframe_worker :: pframe_tail*',
                'pframe_worker.CONTEXT = (pcallcontext_worker)',
            ] + source_f('S_selected') + global_cell('S_selected', '(PINT 2)') + public('S_selected')
            for label, stage, value in [('returned', 2, 2), ('alias', 3, 2), ('written', 4, 3)]:
                prior = {'returned': 'selected', 'alias': 'returned', 'written': 'alias'}[label]
                state = 'S_' + label
                assertions += [f'{state} = $af_find($drive_steps(S_{prior}, 1), 2000, {stage})',
                    f'{state}.COMPLETION = NORMAL', f'$af_stage({state}, {stage})',
                    f'{state}.CURRENT = (pcallcontext_worker)', f'{state}.ACTIVEFIBER = (n_fiber)']
                if label == 'returned':
                    assertions += [f'{state}.RESULT = REFERENCE n_cell']
                else:
                    assertions += [f'$lookup({state}.ENV, $ptascii("r")) = (n_cell)',
                                   f'$lookup({state}.ENV, $ptascii("a")) = (n_cell)']
                assertions += global_cell(state, f'(PINT {value})') + public(state)
            previous, budget_state = 'S_written', 'S_alias'
        stages[5] = [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")',
            'S.CURRENT = eps',
            'S.TODO = (AT (PORIGIN n_unit ([PCINDEX ' + ('9' if case == 'bad' else '7') + '])) (STMT statement_next)) :: ptask_tail*']
        assertions += [f'S_main = $af_find($drive_steps({previous}, 1), 2000, 5)',
            'S_main.COMPLETION = NORMAL', '$af_stage(S_main, 5)',
            '$fiber_at(S_main, n_fiber) = (pfiber_done)',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.VM = eps',
            'pfiber_done.FINISH = eps', 'pfiber_done.RETURNED',
            '~pfiber_done.FAILED', '~pfiber_done.GRACEFUL',
            '$lookup(S_main.ENV, $ptascii("r")) = eps', '$lookup(S_main.ENV, $ptascii("a")) = eps',
        ] + global_cell('S_main', 'pvalue_bad' if case == 'bad' else '(PINT 3)') + drained('S_main') + public('S_main')
        assertions += [f'S_zero = $drive({budget_state}, 0)', 'S_zero.COMPLETION = BUDGET',
            f'S_zero.TODO = {budget_state}.TODO', f'S_zero.ENV = {budget_state}.ENV',
            f'S_zero.ACTIVEFIBER = {budget_state}.ACTIVEFIBER',
            f'S_zero.FIBERCALLERS = {budget_state}.FIBERCALLERS',
            'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 1000)',
            f'S_whole = $drive({budget_state}, 1001)', 'S_adjacent = S_whole',
            'S_whole.COMPLETION = NORMAL', 'S_whole.EXITSTATUS = 0',
            f'$af_outputs(S_whole.EVENTS) = $ptascii("{expected}")', 'S_whole.TODO = eps',
            'S_whole.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            '$lookup(S_whole.ENV, $ptascii("w")) = eps',
            '$lookup(S_whole.ENV, $ptascii("r")) = eps', '$lookup(S_whole.ENV, $ptascii("a")) = eps',
            '~((HOBJECT n_fiber) <- S_whole.ALLOCATIONS)',
        ] + global_cell('S_whole', 'pvalue_bad' if case == 'bad' else '(PINT 3)') + drained('S_whole') + public('S_whole')
        if case == 'bad':
            assertions += ['~((HOBJECT n_error) <- S_whole.ALLOCATIONS)',
                           '(~((HARRAY n_trace_part) <- S_whole.ALLOCATIONS))*']
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-late-recheck.watsup'
        path.write_text(PREFIX + QUIET + ERROR_TASK + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case + '-late-recheck', 'source_id': case,
                        'fixture': str(path.resolve()), 'fixture_sha256': sha(path),
                        'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD,
                'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0,
                'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
