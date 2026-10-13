"""Emit orphaned Fiber close, main continuation and budget checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_active_finalizer_state import PREFIX
from request_environment_state import request_fixture

HEAD = '27a92e4b5e88928c5946dc5634b7d505d1de256e'
REPORT_SHA = '6c34b110874904b46bb86ecd3543267c939b50bdaf6f086ff381e9e7e6341630'
INPUTS = {
    'early-drop': ('b5f984949246524e37940a3befc44b0e86d22d1dcbf69b282c8f78e38995900f',
                   '7fcd8fad0c2a3598b23750dcc3e3413a78e3203c95a23b98b5fd3867678f1834',
                   'b58230a6e3e249e67619eca3421115b54b9bfc1249e06cbe14a1f2af891c9e09',
                   'U;B:1;', 'U;B:1;D;L;G;E;', 5, 6),
    'late-drop': ('d81a2b4cb19860160ff707d2159e77a1451d075d062c5219132c537ac3ad5e85',
                  '322afa59b3a8f62cf986250ca20e7784a546c10d2f45fcec40286c99fd66c256',
                  '06f05b0ebc1af12d555f9fe36947c1c007737694e38ab1c7d9dc131bd9a7041f',
                  'U;B:1;L;G;', 'U;B:1;L;G;D;E;', 8, 9),
}
QUIET = r'''
dec $rc_quiet(pevent*) : bool
def $rc_quiet(eps) = true
def $rc_quiet((OUTPUT n*) :: pevent_tail*) = $rc_quiet(pevent_tail*)
def $rc_quiet(pevent*) = false -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))',
            f'$rc_quiet({state}.EVENTS)']


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
    for case, (source_sha, checked_sha, request_sha, prefix, expected, index_drop, index_next) in INPUTS.items():
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
            1: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")', 'S.CURRENT = eps',
                f'S.TODO = (AT (PORIGIN n_unit ([PCINDEX {index_drop}])) (STMT statement_drop)) :: ptask_tail*'],
            2: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")', 'S.CURRENT = (pcallcontext)',
                'pcallcontext.TARGET = METHOD_TARGET n_object porigin_destructor'],
            3: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}D;")', 'S.CURRENT = eps',
                f'S.TODO = (AT (PORIGIN n_unit ([PCINDEX {index_next}])) (STMT statement_next)) :: ptask_tail*'],
        }
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
            'S_drop = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
            'S_drop.COMPLETION = NORMAL', '$af_stage(S_drop, 1)',
            'S_drop.CURRENT = eps', 'S_drop.GLOBALTABLE = eps', 'S_drop.ACTIVEFIBER = eps',
            'S_drop.FIBERCALLERS = eps', 'S_drop.FIBERCLOSERS = eps',
            f'S_drop.TODO = (AT (PORIGIN n_unit ([PCINDEX {index_drop}])) (STMT statement_drop)) :: ptask_drop*',
            f'porigin_drop = PORIGIN n_unit ([PCINDEX {index_drop}])',
            '$origin_node(S_drop.SOURCES, porigin_drop) = (statement_drop)',
            'statement_drop = NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_w) metadata_w])) metadata_drop',
            '$base64(text_w) = $ptascii("w")',
            '$lookup(S_drop.ENV, $ptascii("w")) = (n_w)',
            'S_drop.STORE[n_w] = DEFINED (POBJECT n_fiber)',
            '$fiber_at(S_drop, n_fiber) = (pfiber)', 'pfiber.STATUS = FIBER_SUSPENDED',
            'pfiber.VM = (pfibervm)', 'pfibervm.CURRENT = (pcallcontext_f)',
            'pcallcontext_f.FUNCTION = PORIGIN n_unit ([PCINDEX 1])',
            '$function_at($all_functions(S_drop), pcallcontext_f.FUNCTION) = (pfunction_f)',
            'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
            'pfunction_f.SIGNATURE.RETURNS = eps', 'pfibervm.TABLE.ENV = eps',
            '$af_pending(pfibervm.TODO) = (FINALLY_REF_RETURN porigin_final porigin_return_source (REFERENCE n_cell) 3)',
            '$origin_node(S_drop.SOURCES, porigin_return_source) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return)',
            '$base64(text_x) = $ptascii("x")',
            'n_cell <- S_drop.REFCELLS', '(HCELL n_cell) <- S_drop.ALLOCATIONS',
            'S_drop.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '(HCELL n_cell) <- $node_children(S_drop, HOBJECT n_fiber)',
            'pfibervm.FRAMES = pframe_worker :: pframe_rest*',
            'pframe_worker.CONTEXT = (pcallcontext_worker)',
            'pcallcontext_worker.TARGET = CLOSURE_TARGET n_worker',
            'pfiber.TARGET = (pcallcontext_worker.TARGET)',
            'pcallcontext_f.CALLSITE = (porigin_call)',
            '$origin_child((pcallcontext_worker.FUNCTION), [PCFIELD 6, PCINDEX 0, PCFIELD 0, PCFIELD 1]) = (porigin_call)',
            '$origin_node(S_drop.SOURCES, porigin_call) = (NExprFuncCall (NName (BYTES text_f) metadata_f) (SEQUENCE eps) metadata_call)',
            '$base64(text_f) = $ptascii("f")',
            '$origin_child((pcallcontext_worker.FUNCTION), [PCFIELD 6, PCINDEX 1]) = (porigin_worker_r)',
            '$origin_node(S_drop.SOURCES, porigin_worker_r) = (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_r) metadata_r])) metadata_worker_r)',
            '$base64(text_r) = $ptascii("R;")',
        ] + public('S_drop')
        assertions += [
            f'porigin_next = PORIGIN n_unit ([PCINDEX {index_next}])',
            '$origin_node(S_drop.SOURCES, porigin_next) = (statement_next)',
        ]
        if case == 'early-drop':
            assertions += ['statement_next = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_next) metadata_next])) metadata_next_statement',
                           '$base64(text_next) = $ptascii("L;")']
        else:
            assertions += ['statement_next = NStmtExpression (NExprFuncCall (NName (BYTES text_next) metadata_next) (SEQUENCE eps) metadata_next_call) metadata_next_statement',
                           '$base64(text_next) = $ptascii("gc_collect_cycles")']
        assertions += [
            'S_active = $af_find($drive_steps(S_drop, 1), 2000, 2)',
            'S_active.COMPLETION = NORMAL', '$af_stage(S_active, 2)',
            'S_active.CURRENT = (pcallcontext_destructor)',
            'pcallcontext_destructor.TARGET = METHOD_TARGET n_object porigin_destructor',
            'pcallcontext_destructor.FUNCTION = porigin_destructor',
            '$origin_child((porigin_destructor), [PCFIELD 6, PCINDEX 0]) = (porigin_d)',
            '$origin_node(S_active.SOURCES, porigin_d) = (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_d) metadata_d])) metadata_d_statement)',
            '$base64(text_d) = $ptascii("D;")',
            'S_active.ACTIVEFIBER = (n_fiber)',
            'S_active.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*',
            'pfiberclose.OBJECT = n_fiber', 'pfiberclose.PREVIOUS = eps',
            'pfiberclose.VM.GLOBAL', 'pfiberclose.VM.CURRENT = eps',
            '(AT porigin_next (STMT statement_next)) <- pfiberclose.VM.TODO',
        ] + public('S_active')
        assertions += [
            'S_caller = $af_find($drive_steps(S_active, 1), 2000, 3)',
            'S_caller.COMPLETION = NORMAL', '$af_stage(S_caller, 3)',
            'S_caller.TODO = (AT porigin_next (STMT statement_next)) :: ptask_caller*',
            'S_caller.CURRENT = eps', 'S_caller.GLOBALTABLE = eps',
            'S_caller.FRAMES = eps', 'S_caller.HELD = eps', 'S_caller.RETIREDOWNERS = eps',
            'S_caller.ACTIVEFIBER = eps', 'S_caller.FIBERCLOSERS = eps', 'S_caller.FIBERCALLERS = eps',
            'S_caller.DESTRUCTION.CALLS = eps', 'S_caller.DESTRUCTION.RELEASES = eps',
            'S_caller.DESTRUCTION.OPERATIONS = eps',
            '$lookup(S_caller.ENV, $ptascii("w")) = eps', '$lookup(S_caller.ENV, $ptascii("r")) = eps',
            '$fiber_at(S_caller, n_fiber) = eps', 'S_caller.OBJECTS[n_fiber] = FIBER pfiber_closed',
            'pfiber_closed.STATUS = FIBER_TERMINATED', 'pfiber_closed.VM = eps',
            '~pfiber_closed.RETURNED', 'pfiber_closed.GRACEFUL',
            '~((HCELL n_cell) <- S_caller.ALLOCATIONS)', '~((HOBJECT n_fiber) <- S_caller.ALLOCATIONS)',
            '~((HOBJECT n_object) <- S_caller.ALLOCATIONS)',
            'H_caller = $heap_graph(S_caller)', '~((HCELL n_cell) <- H_caller.ROOTS)',
            '~((HOBJECT n_fiber) <- H_caller.ROOTS)', '~((HOBJECT n_object) <- H_caller.ROOTS)',
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
            '~((HCELL n_cell) <- S_whole.ALLOCATIONS)', '~((HOBJECT n_fiber) <- S_whole.ALLOCATIONS)',
            '~((HOBJECT n_object) <- S_whole.ALLOCATIONS)',
        ] + public('S_whole')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-close-caller.watsup'
        path.write_text(PREFIX + QUIET + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case + '-close-caller', 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD, 'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
