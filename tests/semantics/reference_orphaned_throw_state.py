"""Emit orphaned Fiber destructor-error delivery and main continuation checks."""
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

HEAD = '0df6172ce050608c3bb32958053da060049abda6'
REPORT_SHA = '234821e87d7e41eb05587e3e3d5a549b9ab8f8f34382d3aae42ac3f3f80aaca3'
INPUTS = {
    'early-drop': ('4f4f7905202fbaa7c14ff8fefcdb0b7bd54f3312e883294d4360f89b19493478',
                   'c7993c9dd57a71eee3881cff9e2ad013eb5d8d63b4774cf3e8241f30ec9c0951',
                   '4ec8380653e9a57a8dbac143b24839c7069b1ed45a9bc1f7c20a2ab8e2e618aa',
                   'U;B:1;D;', 'U;B:1;D;C:old;P:none;L;G;E;', 6),
    'late-drop': ('5a72fc2381b0927f432e04b2f99f60103f07f45d23d8a419cc864c159ec5a336',
                  '582ac170d2c974697f1971274c4257a2f6de1dcf376bcdc27fefd74d133183c8',
                  '0dacd80ef9e501482374d5326cfff0ea5dac4f65f8417b3767e2ae68f2aad442',
                  'U;B:1;L;G;D;', 'U;B:1;L;G;D;C:old;P:none;E;', 9),
}


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
    assert report['pins'] == report['pins_after'] and report['module_stats'] == report['module_stats_after']
    assert report['model_evaluations'] == report['source_agreements'] == 2
    rows = {row['id']: row for row in report['results']}
    assert rows.keys() == INPUTS.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for case, (source_sha, checked_sha, request_sha, prefix, expected, index_next) in INPUTS.items():
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
        stages = {
            1: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")',
                'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = METHOD_TARGET n_object porigin_destructor',
                'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*'],
            2: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")', 'S.CURRENT = eps',
                '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)'],
            3: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}C:old;P:none;")', 'S.CURRENT = eps',
                f'S.TODO = (AT (PORIGIN n_unit ([PCINDEX {index_next}])) (STMT statement_next)) :: ptask_tail*'],
        }
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
            'S_throw = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
            'S_throw.COMPLETION = NORMAL', '$af_stage(S_throw, 1)',
            'S_throw.CURRENT = (pcallcontext_destructor)',
            'pcallcontext_destructor.TARGET = METHOD_TARGET n_old_object porigin_destructor',
            'pcallcontext_destructor.FUNCTION = porigin_destructor',
            'pcallcontext_destructor.LEXICAL_CLASS = (PORIGIN n_unit ([PCINDEX 0]))',
            '$origin_child((porigin_destructor), [PCFIELD 6, PCINDEX 1]) = (porigin_throw_statement)',
            '$origin_node(S_throw.SOURCES, porigin_throw_statement) = (NStmtExpression (NExprThrow expression_new metadata_throw) metadata_statement)',
            '$origin_child((porigin_throw_statement), [PCFIELD 0]) = (porigin_throw)',
            '$origin_child((porigin_throw), [PCFIELD 0]) = (porigin_new)',
            'S_throw.ORIGIN = (porigin_throw)',
            'expression_new = NExprNew (NName (BYTES text_exception) metadata_exception) (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text_message) metadata_message) (BOOLEAN false) (BOOLEAN false) metadata_arg])) metadata_new',
            '$base64(text_exception) = $ptascii("Exception")', '$base64(text_message) = $ptascii("old")',
            'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*', 'n_error =/= n_old_object',
            'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Exception"', 'pthrowable_error.ORIGIN = (porigin_new)',
            '$object_name(S_throw, n_error) = $ptascii("Exception")',
            '$throwable_previous_id(S_throw, n_error) = eps',
            '$string_bytes($throwable_field(S_throw, n_error, "message")) = ($ptascii("old"))',
            '$throwable_field(S_throw, n_error, "line") = PINT 2',
            '$throwable_field(S_throw, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_throw, n_trace)',
            'pnode_trace* = $heap_reach([HARRAY n_trace], eps, $heap_graph(S_throw).EDGES)',
            'pnode_trace* = (HARRAY n_trace_part)*',
            'S_throw.ACTIVEFIBER = (n_fiber)',
            'S_throw.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*', 'pfiberclose.OBJECT = n_fiber',
            'pfiberclose.EXIT =/= n_error',
        ] + public('S_throw')
        assertions += [
            'S_catch = $af_find($drive_steps(S_throw, 1), 2000, 2)',
            'S_catch.COMPLETION = NORMAL', '$af_stage(S_catch, 2)',
            'S_catch.CURRENT = eps', 'S_catch.GLOBALTABLE = eps',
            '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
            'S_catch.STORE[n_e] = DEFINED (POBJECT n_error)', '$throwable_previous_id(S_catch, n_error) = eps',
            '$throwable_field(S_catch, n_error, "line") = PINT 2',
            '$throwable_field(S_catch, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_catch, n_trace)',
            '$heap_reach([HARRAY n_trace], eps, $heap_graph(S_catch).EDGES) = pnode_trace*',
            '(S_catch.ARRAYS[n_trace_part] = S_throw.ARRAYS[n_trace_part])*',
            '$lookup(S_catch.ENV, $ptascii("w")) = eps', '$lookup(S_catch.ENV, $ptascii("r")) = eps',
        ] + public('S_catch')
        assertions += [
            f'porigin_next = PORIGIN n_unit ([PCINDEX {index_next}])',
            '$origin_node(S_throw.SOURCES, porigin_next) = (statement_next)',
        ]
        if case == 'early-drop':
            assertions += ['statement_next = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_next) metadata_next])) metadata_next_statement',
                           '$base64(text_next) = $ptascii("L;")']
        else:
            assertions += ['statement_next = NStmtExpression (NExprFuncCall (NName (BYTES text_next) metadata_next) (SEQUENCE eps) metadata_next_call) metadata_next_statement',
                           '$base64(text_next) = $ptascii("gc_collect_cycles")']
        assertions += [
            'S_caller = $af_find($drive_steps(S_catch, 1), 2000, 3)',
            'S_caller.COMPLETION = NORMAL', '$af_stage(S_caller, 3)',
            'S_caller.TODO = (AT porigin_next (STMT statement_next)) :: ptask_caller*',
            '$lookup(S_caller.ENV, $ptascii("e")) = (n_e)',
            'S_caller.STORE[n_e] = DEFINED (POBJECT n_error)',
            '$lookup(S_caller.ENV, $ptascii("p")) = (n_p)', 'S_caller.STORE[n_p] = DEFINED PNULL',
            '$throwable_previous_id(S_caller, n_error) = eps',
            '$throwable_field(S_caller, n_error, "line") = PINT 2',
            '$throwable_field(S_caller, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_caller, n_trace)',
            '$heap_reach([HARRAY n_trace], eps, $heap_graph(S_caller).EDGES) = pnode_trace*',
            '(S_caller.ARRAYS[n_trace_part] = S_throw.ARRAYS[n_trace_part])*',
            'S_caller.CURRENT = eps', 'S_caller.GLOBALTABLE = eps', 'S_caller.FRAMES = eps',
            'S_caller.HELD = eps', 'S_caller.RETIREDOWNERS = eps', 'S_caller.ACTIVEFIBER = eps',
            'S_caller.FIBERCLOSERS = eps', 'S_caller.FIBERCALLERS = eps',
            'S_caller.DESTRUCTION.CALLS = eps', 'S_caller.DESTRUCTION.RELEASES = eps',
            'S_caller.DESTRUCTION.OPERATIONS = eps',
            '$lookup(S_caller.ENV, $ptascii("w")) = eps', '$lookup(S_caller.ENV, $ptascii("r")) = eps',
            '$fiber_at(S_caller, n_fiber) = eps', 'S_caller.OBJECTS[n_fiber] = FIBER pfiber_closed',
            'pfiber_closed.STATUS = FIBER_TERMINATED', 'pfiber_closed.VM = eps',
            '~pfiber_closed.RETURNED', 'pfiber_closed.FAILED', '~pfiber_closed.GRACEFUL',
            '~((HOBJECT n_fiber) <- S_caller.ALLOCATIONS)', '~((HOBJECT n_old_object) <- S_caller.ALLOCATIONS)',
            '(HOBJECT n_error) <- S_caller.ALLOCATIONS',
        ] + public('S_caller')
        assertions += [
            'S_zero = $drive(S_caller, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero.TODO = S_caller.TODO', 'S_zero.ENV = S_caller.ENV',
            'S_zero.ALLOCATIONS = S_caller.ALLOCATIONS', 'S_zero.FIBERCLOSERS = S_caller.FIBERCLOSERS',
            'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 1000)',
            'S_whole = $drive(S_caller, 1001)', 'S_adjacent = S_whole',
            'S_whole.COMPLETION = NORMAL', f'$af_outputs(S_whole.EVENTS) = $ptascii("{expected}")',
            'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
            'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps', 'S_whole.ACTIVEFIBER = eps',
            'S_whole.FIBERCALLERS = eps', 'S_whole.FIBERCLOSERS = eps',
            'S_whole.DESTRUCTION.CALLS = eps', 'S_whole.DESTRUCTION.RELEASES = eps',
            'S_whole.DESTRUCTION.OPERATIONS = eps',
            '$lookup(S_whole.ENV, $ptascii("w")) = eps', '$lookup(S_whole.ENV, $ptascii("r")) = eps',
            '~((HOBJECT n_fiber) <- S_whole.ALLOCATIONS)', '~((HOBJECT n_old_object) <- S_whole.ALLOCATIONS)',
            '~((HOBJECT n_error) <- S_whole.ALLOCATIONS)',
        ] + public('S_whole')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-throw-caller.watsup'
        path.write_text(PREFIX + QUIET + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case + '-throw-caller', 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD, 'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
