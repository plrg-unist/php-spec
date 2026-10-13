"""Emit resumed reference-return delivery to a genuine Fiber worker caller."""
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

HEAD = 'cb498f92293d2045aae60e524ec20e729fab2390'
REPORT_SHA = 'bb1629bce9610488914f8cdd8221fe03d0243010cfe07a6b88edd4ffbd584ede'
INPUTS = {
    'suspended': ('03b62396bd8397c7f2d6c162853247d80d7f2f40f0beed6d5959bede62055252',
                  'c7edc227b2f144a156d0dcaf39e315838f68be4bf52d2e1a8bd7634d569a505b',
                  '464bc35c532eb0871e3c7ff8cfd5056c38eb146cf71e4ccd76b9ac6f690e6043',
                  'U:0;B:1;', 'U:0;B:1;P;R:selected;A:changed;E;'),
    'direct': ('a069805f9521ddbf33d857bf0e4eaa85f9523b0613e3ae5bc78e891e301fdec1',
               'b8ac6a0ff091031b7a16bc64360745ce8047e30e9a7cae7d91f310202531fcf6',
               '546e5137088fb7c64fa011906514ac650f37de1bb3ea1886a9f41f7586e6804a',
               'U:0;', 'U:0;P;R:selected;A:changed;B:0;E;'),
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
    for case, (source_sha, checked_sha, request_sha, prefix, expected) in INPUTS.items():
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
            1: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")', '$af_function(S, $ptascii("ping"))'],
            2: ['S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                'S.RESULT = REFERENCE n_returned', f'$af_outputs(S.EVENTS) = $ptascii("{prefix}P;")',
                '$lookup(S.ENV, $ptascii("r")) = eps'],
            3: ['S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("a")) = (n_a)',
                f'$af_outputs(S.EVENTS) = $ptascii("{prefix}P;")'],
            4: ['S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("r")) = (n_r)', 'S.STORE[n_r] = DEFINED pvalue_written',
                '$string_bytes(pvalue_written) = ($ptascii("changed"))',
                f'$af_outputs(S.EVENTS) = $ptascii("{prefix}P;R:selected;")'],
        }
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]']
        if case == 'suspended':
            stages[0] = ['$af_outputs(S.EVENTS) = $ptascii("U:0;")',
                '$fiber_globals(S) = psymboltable', '$lookup(psymboltable.ENV, $ptascii("w")) = (n_w)',
                'S.STORE[n_w] = DEFINED (POBJECT n_fiber)', '$fiber_at(S, n_fiber) = (pfiber)',
                'pfiber.STATUS = FIBER_SUSPENDED']
            assertions += ['S_parked = $af_find(S_start, 2000, 0)', 'S_parked.COMPLETION = NORMAL',
                '$af_stage(S_parked, 0)', '$fiber_globals(S_parked) = psymboltable_parked',
                '$lookup(psymboltable_parked.ENV, $ptascii("w")) = (n_w)',
                'S_parked.STORE[n_w] = DEFINED (POBJECT n_fiber)',
                '$fiber_at(S_parked, n_fiber) = (pfiber_parked)', 'pfiber_parked.STATUS = FIBER_SUSPENDED',
                'pfiber_parked.VM = (pfibervm)',
                '$af_pending(pfibervm.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_cell) 3)',
                'pfibervm.CURRENT = (pcallcontext_parked)', 'pfibervm.FRAMES = pframe_worker :: pframe_rest*',
                'pframe_worker.CONTEXT = (pcallcontext_worker)',
                'pfibervm.TABLE.ENV = eps', 'n_cell <- S_parked.REFCELLS',
                '(HCELL n_cell) <- S_parked.ALLOCATIONS', 'S_parked.STORE[n_cell] = DEFINED pvalue_selected',
                '$string_bytes(pvalue_selected) = ($ptascii("selected"))',
                'S_ping = $af_find($drive_steps(S_parked, 1), 2000, 1)']
        else:
            assertions += ['S_ping = $af_find(S_start, 2000, 1)']
        assertions += ['S_ping.COMPLETION = NORMAL', '$af_stage(S_ping, 1)',
            'S_ping.ACTIVEFIBER = (n_fiber)',
            'S_ping.FRAMES = pframe_f :: pframe_ping_worker :: pframe_ping_rest*',
            'pframe_f.LOCALS = (psymboltable_f)', 'pframe_f.CONTEXT = (pcallcontext_f)',
            'pframe_ping_worker.CONTEXT = (pcallcontext_worker)',
            'pcallcontext_worker.TARGET = CLOSURE_TARGET n_worker',
            '$fiber_at(S_ping, n_fiber) = (pfiber_running)', 'pfiber_running.STATUS = FIBER_RUNNING',
            'pfiber_running.TARGET = (pcallcontext_worker.TARGET)',
            '$function_at($all_functions(S_ping), pcallcontext_f.FUNCTION) = (pfunction_f)',
            'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
            '$af_pending(pframe_f.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_cell) 3)',
            '$origin_child((pcallcontext_f.FUNCTION), [PCFIELD 5, PCINDEX 1]) = (porigin_owner)',
            '$origin_child((porigin_owner), [PCFIELD 0, PCINDEX 0]) = (porigin_source)',
            '$origin_node(S_ping.SOURCES, porigin_source) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return)',
            '$base64(text_x) = $ptascii("x")', '$lookup(psymboltable_f.ENV, $ptascii("x")) = eps',
            'pcallcontext_f.CALLSITE = (porigin_call)',
            '$origin_child((pcallcontext_worker.FUNCTION), [PCFIELD 6, PCINDEX 0, PCFIELD 0, PCFIELD 1]) = (porigin_call)',
            '$origin_node(S_ping.SOURCES, porigin_call) = (NExprFuncCall (NName (BYTES text_f) metadata_f) (SEQUENCE eps) metadata_call)',
            '$base64(text_f) = $ptascii("f")', 'n_cell <- S_ping.REFCELLS',
            '(HCELL n_cell) <- S_ping.ALLOCATIONS', 'S_ping.STORE[n_cell] = DEFINED pvalue_selected',
            '$string_bytes(pvalue_selected) = ($ptascii("selected"))',
        ] + public('S_ping')
        for label, stage, checks in [
            ('returned', 2, ['S_returned.RESULT = REFERENCE n_cell', '$lookup(S_returned.ENV, $ptascii("r")) = eps']),
            ('alias', 3, ['$lookup(S_alias.ENV, $ptascii("r")) = (n_cell)', '$lookup(S_alias.ENV, $ptascii("a")) = (n_cell)']),
            ('written', 4, ['$lookup(S_written.ENV, $ptascii("r")) = (n_cell)', '$lookup(S_written.ENV, $ptascii("a")) = (n_cell)']),
        ]:
            previous = {'returned': 'ping', 'alias': 'returned', 'written': 'alias'}[label]
            state = 'S_' + label
            assertions += [f'{state} = $af_find($drive_steps(S_{previous}, 1), 2000, {stage})',
                f'{state}.COMPLETION = NORMAL', f'$af_stage({state}, {stage})',
                f'{state}.CURRENT = (pcallcontext_worker)', f'{state}.ACTIVEFIBER = (n_fiber)',
                *checks, f'$lookup({state}.ENV, $ptascii("x")) = eps', f'n_cell <- {state}.REFCELLS',
                f'(HCELL n_cell) <- {state}.ALLOCATIONS']
            if label != 'written':
                assertions += [f'{state}.STORE[n_cell] = DEFINED pvalue_selected']
            else:
                assertions += [f'{state}.STORE[n_cell] = DEFINED pvalue_changed',
                               '$string_bytes(pvalue_changed) = ($ptascii("changed"))']
            assertions += public(state)
        assertions += [
            'S_zero = $drive(S_alias, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero.TODO = S_alias.TODO', 'S_zero.ENV = S_alias.ENV',
            'S_zero.ACTIVEFIBER = S_alias.ACTIVEFIBER', 'S_zero.FIBERCALLERS = S_alias.FIBERCALLERS',
            'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 1000)',
            'S_whole = $drive(S_alias, 1001)', 'S_adjacent = S_whole',
            'S_whole.COMPLETION = NORMAL', f'$af_outputs(S_whole.EVENTS) = $ptascii("{expected}")',
            'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
            'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps', 'S_whole.ACTIVEFIBER = eps',
            'S_whole.FIBERCALLERS = eps', 'S_whole.FIBERCLOSERS = eps',
            'S_whole.DESTRUCTION.CALLS = eps', 'S_whole.DESTRUCTION.RELEASES = eps',
            'S_whole.DESTRUCTION.OPERATIONS = eps',
            '$lookup(S_whole.ENV, $ptascii("r")) = eps', '$lookup(S_whole.ENV, $ptascii("a")) = eps',
        ] + public('S_whole')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-worker-caller.watsup'
        path.write_text(PREFIX + QUIET + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case + '-worker-caller', 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD, 'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
