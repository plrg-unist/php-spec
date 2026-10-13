"""Emit delivered finally-override references in resumed and direct Fiber workers."""
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

HEAD = 'cbc57fdbaed8ca59c8e66e429587d9fb449df822'
REPORT_SHA = 'cba92c23fe5b6756b035df8c6fe24aee37850d5398961984be13374b90f42e14'
INPUTS = {
    'suspended': ('b3c9e0e56d7e2f90c026841d981d450f2522004700d9b724c825593bd6162778',
                  '800f8913d9002104d214c49ac58524b69776469284ac0b4ce5de0f9a80d96b3f',
                  '0967c4bb3fdca3e0adab8e79057a3116ab825a0fb6efab726dc974b0379282cf',
                  'U;B:1;P;', 'U;B:1;P;D;R:override;A:changed;E;', 5),
    'direct': ('a7a260a25ef1c22a0fd54ad8b763f0f61d8aa656625663471d95db2a93408197',
               'c6fd7dafff64c89b683eda2bd782f72ffb73a01ce97ce8a51019b6102521c7b6',
               '1d0e7828cbfe4b59c3b4e15b5e7bcac38564c12700f7ff1a6a353ec761766872',
               'U;P;', 'U;P;D;R:override;A:changed;B:0;E;', 4),
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
    for case, (source_sha, checked_sha, request_sha, prefix, expected, index_return) in INPUTS.items():
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
                'S.FRAMES = pframe_f :: pframe_rest*', 'pframe_f.LOCALS = (psymboltable_f)',
                '$lookup(psymboltable_f.ENV, $ptascii("y")) = (n_y)'],
            2: ['S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                'S.RESULT = REFERENCE n_returned', f'$af_outputs(S.EVENTS) = $ptascii("{prefix}D;")',
                '$lookup(S.ENV, $ptascii("r")) = eps'],
            3: ['S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("a")) = (n_a)',
                f'$af_outputs(S.EVENTS) = $ptascii("{prefix}D;")'],
            4: ['S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_worker',
                '$lookup(S.ENV, $ptascii("r")) = (n_r)', 'S.STORE[n_r] = DEFINED pvalue_written',
                '$string_bytes(pvalue_written) = ($ptascii("changed"))',
                f'$af_outputs(S.EVENTS) = $ptascii("{prefix}D;R:override;")'],
        }
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]']
        assertions += ['S_active = $af_find(S_start, 2000, 1)',
            'S_active.COMPLETION = NORMAL', '$af_stage(S_active, 1)',
            'S_active.CURRENT = (pcallcontext_destructor)',
            'pcallcontext_destructor.TARGET = METHOD_TARGET n_object porigin_destructor',
            'S_active.ACTIVEFIBER = (n_fiber)',
            'S_active.FRAMES = pframe_f :: pframe_worker :: pframe_rest*',
            'pframe_f.LOCALS = (psymboltable_f)', 'pframe_f.CONTEXT = (pcallcontext_f)',
            'pframe_worker.CONTEXT = (pcallcontext_worker)',
            'pcallcontext_worker.TARGET = CLOSURE_TARGET n_worker',
            '$fiber_at(S_active, n_fiber) = (pfiber_running)', 'pfiber_running.STATUS = FIBER_RUNNING',
            'pfiber_running.TARGET = (pcallcontext_worker.TARGET)',
            '$function_at($all_functions(S_active), pcallcontext_f.FUNCTION) = (pfunction_f)',
            'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
            'pfunction_f.SIGNATURE.RETURNS = eps',
            '$lookup(psymboltable_f.ENV, $ptascii("y")) = (n_cell)',
            '$lookup(psymboltable_f.ENV, $ptascii("x")) = eps',
            '$origin_child((pcallcontext_f.FUNCTION), [PCFIELD 5, PCINDEX 1, PCFIELD 2]) = (porigin_finally)',
            f'$origin_child((porigin_finally), [PCFIELD 0, PCINDEX {index_return}]) = (porigin_return_y)',
            '$origin_node(S_active.SOURCES, porigin_return_y) = (NStmtReturn (NExprVariable (BYTES text_y) metadata_y) metadata_return)',
            '$base64(text_y) = $ptascii("y")',
            '(RETURN_REF_UNWIND (REFERENCE n_cell) 3 true porigin_return_y) <- pframe_f.TODO',
            'pcallcontext_f.CALLSITE = (porigin_call)',
            '$origin_child((pcallcontext_worker.FUNCTION), [PCFIELD 6, PCINDEX 0, PCFIELD 0, PCFIELD 1]) = (porigin_call)',
            '$origin_node(S_active.SOURCES, porigin_call) = (NExprFuncCall (NName (BYTES text_f) metadata_f) (SEQUENCE eps) metadata_call)',
            '$base64(text_f) = $ptascii("f")', 'n_cell <- S_active.REFCELLS',
            '(HCELL n_cell) <- S_active.ALLOCATIONS',
            'S_active.STORE[n_cell] = DEFINED pvalue_selected',
            '$string_bytes(pvalue_selected) = ($ptascii("override"))',
        ]
        for label, stage, checks in [
            ('returned', 2, ['S_returned.RESULT = REFERENCE n_cell', '$lookup(S_returned.ENV, $ptascii("r")) = eps']),
            ('alias', 3, ['$lookup(S_alias.ENV, $ptascii("r")) = (n_cell)', '$lookup(S_alias.ENV, $ptascii("a")) = (n_cell)']),
            ('written', 4, ['$lookup(S_written.ENV, $ptascii("r")) = (n_cell)', '$lookup(S_written.ENV, $ptascii("a")) = (n_cell)']),
        ]:
            previous = {'returned': 'active', 'alias': 'returned', 'written': 'alias'}[label]
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
