"""Emit selected-return cycle retention, request close and continuation checks."""
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

HEAD = '059bc886c838af92ab443b953c77cd51876892fe'
REPORT_SHA = '1015b27c6a8f58fdecd493aef5d3bd72ded159a89b86819b6f0326bb9267bd1f'
CATALOGUE_SHA = 'cd41445b6ca8d132ddf9915fb8792ef08c58a5ac2628df78d9903bf65a5af6aa'
INPUTS = {
    'cycle': ('d9a454fe692154fcae72fa4e8e8ca70f0ae786382795cff8b4778d49b77453a5',
              '8ec12b5f4e3277ea72a61ea780543af702caf7cf48a4ad5f8119c31c321af89b',
              'dbbc4625c159ab3efb276be3e79e3ffcd9128dc510f4896462c0a9048b05bbb8',
              'U;B:1;L;G;E;D;'),
    'null-control': ('1e2329f2101e08e78e44b394b2b908dde77c509531215b6f444687f82d2af8f9',
                     '9a6e23818d914e844849fbc5c811e0bcf1ec429e98b4198008d1b121b217803a',
                     '536a7cd4e0dd20e08e86f27fdf53baa002f6c16a3ffb21d8b2e55fd33c49a70a',
                     'U;B:1;D;L;G;E;'),
}
FIND_FIBER = r'''
dec $cc_suspended_node(pstate, pnode) : nat?
def $cc_suspended_node(S, HOBJECT n) = (n)
  -- if $fiber_at(S, n) = (pfiber)
  -- if pfiber.STATUS = FIBER_SUSPENDED
def $cc_suspended_node(S, pnode) = eps -- otherwise
dec $cc_suspended(pstate, pnode*) : nat?
def $cc_suspended(S, eps) = eps
def $cc_suspended(S, pnode :: pnode_tail*) = (n)
  -- if $cc_suspended_node(S, pnode) = (n)
def $cc_suspended(S, pnode :: pnode_tail*) = $cc_suspended(S, pnode_tail*)
  -- if $cc_suspended_node(S, pnode) = eps
'''


def retired(state, cell=False):
    checks = [f'{state}.CURRENT = eps', f'{state}.FRAMES = eps',
              f'{state}.HELD = eps', f'{state}.RETIREDOWNERS = eps',
              f'{state}.ACTIVEFIBER = eps', f'{state}.FIBERCALLERS = eps',
              f'{state}.FIBERCLOSERS = eps', f'{state}.DESTRUCTION.CALLS = eps',
              f'{state}.DESTRUCTION.RELEASES = eps', f'{state}.DESTRUCTION.OPERATIONS = eps',
              f'{state}.DESTRUCTION.FRAMES = eps', f'{state}.DESTRUCTION.CLEANUPS = eps',
              f'{state}.GC.ACTIVE = eps', f'{state}.GC.PLAN = eps',
              f'$lookup({state}.ENV, $ptascii("w")) = eps',
              f'$fiber_at({state}, n_fiber) = eps',
              f'{state}.OBJECTS[n_fiber] = FIBER pfiber_closed',
              'pfiber_closed.STATUS = FIBER_TERMINATED', 'pfiber_closed.VM = eps',
              '~pfiber_closed.RETURNED', '~pfiber_closed.FAILED', 'pfiber_closed.GRACEFUL',
              f'~((HOBJECT n_fiber) <- {state}.ALLOCATIONS)',
              f'~((HOBJECT n_object) <- {state}.ALLOCATIONS)']
    if cell:
        checks += [f'~((HCELL n_cell) <- {state}.ALLOCATIONS)',
                   f'~((HCELL n_cell) <- $heap_graph({state}).ROOTS)']
    return checks + public(state)


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
    catalogue_path = ROOT / 'tests/semantics/reference_cycle_carrier_cases.json'
    assert sha(catalogue_path) == CATALOGUE_SHA
    catalogue = {row['id']: row for row in json.loads(catalogue_path.read_text())}
    rows = {row['id']: row for row in report['results']}
    assert rows.keys() == INPUTS.keys() == catalogue.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for case, (source_sha, checked_sha, request_sha, expected) in INPUTS.items():
        directory = args.raw / case
        checked_path, request_path = directory / 'checked.json', directory / 'request.json'
        assert sha(checked_path) == checked_sha and sha(request_path) == request_sha
        checked, facts = json.loads(checked_path.read_text()), json.loads(request_path.read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert sha(source) == rows[case]['source_sha256'] == source_sha
        assert source.read_bytes() == catalogue[case]['source'].encode()
        for engine in ('native', 'model'):
            assert base64.b64decode(rows[case][engine]['stdout']) == expected.encode()
            assert base64.b64decode(rows[case][engine]['stderr']) == b''
            assert rows[case][engine]['exit_status'] == 0
        assert checked['ok'] and checked['fixture']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET']
        if case == 'cycle':
            stages = {
                1: ['$af_outputs(S.EVENTS) = $ptascii("U;B:1;L;G;")', 'S.CURRENT = eps',
                    'S.TODO = (AT (PORIGIN n_unit ([PCINDEX 9])) (STMT statement_gc)) :: ptask_tail*'],
                2: ['$af_outputs(S.EVENTS) = $ptascii("U;B:1;L;G;")', 'S.CURRENT = eps',
                    'S.TODO = (AT (PORIGIN n_unit ([PCINDEX 10])) (STMT statement_e)) :: ptask_tail*'],
                3: ['$af_outputs(S.EVENTS) = $ptascii("U;B:1;L;G;E;")',
                    'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = METHOD_TARGET n_object porigin_destructor'],
                4: [f'$af_outputs(S.EVENTS) = $ptascii("{expected}")',
                    'S.CURRENT = eps', 'S.ACTIVEFIBER = eps', 'S.FIBERCLOSERS = eps',
                    'S.TODO = [DESTRUCTOR_STORE]'],
            }
            assertions += [
                'S_g = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
                'S_g.COMPLETION = NORMAL', '$af_stage(S_g, 1)',
                'S_g.TODO = (AT (PORIGIN n_unit ([PCINDEX 9])) (STMT statement_gc)) :: ptask_g*',
                'porigin_gc = PORIGIN n_unit ([PCINDEX 9])',
                '$origin_node(S_g.SOURCES, porigin_gc) = (statement_gc)',
                'statement_gc = NStmtExpression (NExprFuncCall (NName (BYTES text_gc) metadata_gc_name) (SEQUENCE eps) metadata_gc_call) metadata_gc_statement',
                '$base64(text_gc) = $ptascii("gc_collect_cycles")',
                '$cc_suspended(S_g, S_g.ALLOCATIONS) = (n_fiber)',
                '$fiber_at(S_g, n_fiber) = (pfiber_g)', 'pfiber_g.VM = (pfibervm_g)',
                'pfibervm_g.TABLE.ENV = eps', 'pfibervm_g.CURRENT = (pcallcontext_f)',
                'pcallcontext_f.FUNCTION = PORIGIN n_unit ([PCINDEX 1])',
                '$function_at($all_functions(S_g), pcallcontext_f.FUNCTION) = (pfunction_f)',
                'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
                'pfunction_f.SIGNATURE.RETURNS = eps',
                '$af_pending(pfibervm_g.TODO) = (FINALLY_REF_RETURN porigin_final porigin_return (REFERENCE n_cell) 3)',
                '$origin_node(S_g.SOURCES, porigin_return) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return)',
                '$base64(text_x) = $ptascii("x")',
                'S_g.STORE[n_cell] = DEFINED (POBJECT n_object)',
                'n_cell <- S_g.REFCELLS', '(HCELL n_cell) <- S_g.ALLOCATIONS',
                'S_g.OBJECTS[n_object] = INSTANCE (PORIGIN n_unit ([PCINDEX 0]))',
                '$objectprops_at(S_g.OBJECTPROPS, n_object) = (ppropertyslot*)',
                '$property_slot_at(ppropertyslot*, $ptascii("back")) = (ppropertyslot_back)',
                'ppropertyslot_back.STATE = PROP_VALUE (DIRECT (POBJECT n_fiber))',
                '(HCELL n_cell) <- $node_children(S_g, HOBJECT n_fiber)',
                '~((HCELL n_cell) <- $heap_graph(S_g).ROOTS)',
                '(HCELL n_cell) <- $gc_graph(S_g).ROOTS',
                'S_g.GC.ACTIVE = eps', 'S_g.GC.PLAN = eps', 'n_gc_next = S_g.GC.NEXT',
                'n_fiber_handle = S_g.DESTRUCTION.HANDLES[n_fiber]',
            ] + public('S_g')
            assertions += [
                'S_e = $af_find($drive_steps(S_g, 1), 2000, 2)',
                'S_e.COMPLETION = NORMAL', '$af_stage(S_e, 2)',
                'S_e.TODO = (AT (PORIGIN n_unit ([PCINDEX 10])) (STMT statement_e)) :: ptask_e*',
                '$origin_node(S_e.SOURCES, PORIGIN n_unit ([PCINDEX 10])) = (statement_e)',
                'statement_e = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_e) metadata_e])) metadata_e_statement',
                '$base64(text_e) = $ptascii("E;")',
                'S_e.GC.NEXT = $(n_gc_next + 1)', 'S_e.GC.ACTIVE = eps', 'S_e.GC.PLAN = eps',
                '$fiber_at(S_e, n_fiber) = (pfiber_e)', 'pfiber_e.STATUS = FIBER_SUSPENDED',
                'pfiber_e.VM = (pfibervm_e)', 'pfibervm_e.TABLE.ENV = eps',
                '$af_pending(pfibervm_e.TODO) = $af_pending(pfibervm_g.TODO)',
                'S_e.STORE[n_cell] = S_g.STORE[n_cell]', '(HCELL n_cell) <- S_e.ALLOCATIONS',
                '(HOBJECT n_object) <- S_e.ALLOCATIONS',
                '(HCELL n_cell) <- $node_children(S_e, HOBJECT n_fiber)',
                '(HCELL n_cell) <- $gc_graph(S_e).ROOTS',
            ] + public('S_e')
            assertions += [
                'S_d = $af_find($drive_steps(S_e, 1), 2000, 3)',
                'S_d.COMPLETION = NORMAL', '$af_stage(S_d, 3)',
                'S_d.CURRENT = (pcallcontext_d)',
                'pcallcontext_d.TARGET = METHOD_TARGET n_object porigin_destructor',
                'S_d.ACTIVEFIBER = (n_fiber)',
                'S_d.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S_d.DESTRUCTION.PHASE = DESTRUCTION_STORE',
                'S_d.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*',
                'pfiberclose.OBJECT = n_fiber', 'pfiberclose.PREVIOUS = eps',
                '~pfiberclose.RELEASE.USER', 'pfiberclose.VM.CURRENT = eps',
                'DESTRUCTOR_STORE <- pfiberclose.VM.TODO',
                'S_d.DESTRUCTION.INDEX = $(n_fiber_handle + 1)',
                'S_caller = $af_find($drive_steps(S_d, 1), 2000, 4)',
                'S_caller.COMPLETION = NORMAL', '$af_stage(S_caller, 4)',
                'S_caller.DESTRUCTION.PHASE = DESTRUCTION_STORE',
                'S_caller.DESTRUCTION.INDEX = $(n_fiber_handle + 1)',
            ] + public('S_d') + retired('S_caller', cell=True)
        else:
            stages = {
                1: ['$af_outputs(S.EVENTS) = $ptascii("U;B:1;")',
                    'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = METHOD_TARGET n_object porigin_destructor'],
                2: ['$af_outputs(S.EVENTS) = $ptascii("U;B:1;D;")', 'S.CURRENT = eps',
                    'S.TODO = (AT (PORIGIN n_unit ([PCINDEX 6])) (STMT statement_l)) :: ptask_tail*'],
            }
            assertions += [
                'S_d = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
                'S_d.COMPLETION = NORMAL', '$af_stage(S_d, 1)',
                'S_d.CURRENT = (pcallcontext_d)',
                'pcallcontext_d.TARGET = METHOD_TARGET n_object porigin_destructor',
                'pcallcontext_d.LEXICAL_CLASS = (PORIGIN n_unit ([PCINDEX 0]))',
                'S_d.OBJECTS[n_object] = INSTANCE (PORIGIN n_unit ([PCINDEX 0]))',
                '$objectprops_at(S_d.OBJECTPROPS, n_object) = (ppropertyslot*)',
                '$property_slot_at(ppropertyslot*, $ptascii("back")) = (ppropertyslot_back)',
                'ppropertyslot_back.STATE = PROP_VALUE (DIRECT PNULL)',
                'S_d.ACTIVEFIBER = (n_fiber)',
                'S_d.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*',
                'pfiberclose.OBJECT = n_fiber', 'pfiberclose.RELEASE.USER',
                'S_caller = $af_find($drive_steps(S_d, 1), 2000, 2)',
                'S_caller.COMPLETION = NORMAL', '$af_stage(S_caller, 2)',
                'S_caller.TODO = (AT (PORIGIN n_unit ([PCINDEX 6])) (STMT statement_l)) :: ptask_caller*',
                '$origin_node(S_caller.SOURCES, PORIGIN n_unit ([PCINDEX 6])) = (statement_l)',
                'statement_l = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_l) metadata_l])) metadata_l_statement',
                '$base64(text_l) = $ptascii("L;")',
            ] + public('S_d') + retired('S_caller')
        assertions += [
            '$origin_child((porigin_destructor), [PCFIELD 6, PCINDEX 0]) = (porigin_d)',
            '$origin_node(S_d.SOURCES, porigin_d) = (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_d) metadata_d])) metadata_d_statement)',
            '$base64(text_d) = $ptascii("D;")',
            'S_zero = $drive(S_caller, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero.TODO = S_caller.TODO', 'S_zero.ALLOCATIONS = S_caller.ALLOCATIONS',
            'S_zero.FIBERCLOSERS = S_caller.FIBERCLOSERS',
            'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 1000)',
            'S_whole = $drive(S_caller, 1001)', 'S_adjacent = S_whole',
            'S_whole.COMPLETION = NORMAL', 'S_whole.TODO = eps',
            f'$af_outputs(S_whole.EVENTS) = $ptascii("{expected}")',
            'S_whole.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S_whole.DESTRUCTION.INDEX = S_whole.DESTRUCTION.NEXT',
            'n_fiber <- S_whole.DESTRUCTION.CALLED', 'n_object <- S_whole.DESTRUCTION.CALLED',
        ] + retired('S_whole', cell=(case == 'cycle'))
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-retention-close.watsup'
        path.write_text(PREFIX + QUIET + FIND_FIBER + '\n' + stage_text +
                        '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case + '-retention-close', 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD, 'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
