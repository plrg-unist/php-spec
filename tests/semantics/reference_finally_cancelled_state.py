"""Emit source-reached cancelled and delivered carrier/caller checks."""
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

HEAD = '43df347e6414b0d37cbe237487f64b297cc153c7'
REPORT_SHA = 'f907284e8e986acd6940a248db333ba772337a4b3ae4517f062bfe5c7df7a146'
INPUTS = {
    'cancelled': ('d2068353ca394bc4284bb2dd54526fc63176a5526145673c42e53a1785c3d9a6',
                  'ad878c8897227abea1994e6fc27a773ff6ca81a8b1b156b09dfe0fed96948c5d',
                  'c847ba2ed6fe78a4d77b9680b2f7e0f9fb2ab70962d6d77546aa0fe8866bf66d',
                  'U;P;D;', 'U;P;D;R;', 'U;P;D;R;A:changed;'),
    'delivered': ('bb093031fb8b84d9069fbd67135d01b83d69d26cb4985f2549a2b5834460450e',
                  'bcdc1b3d9c46e1f61850a025a91b95e869d03f6c9023bb7ab88fffa91dfd498e',
                  '5fdfb07076915e1c6a4d3e2213d6e0458f60d252c89cc798253379450f175f6c',
                  'U;P;', 'U;P;R;D;', 'U;P;R;D;A:changed;'),
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
    for case, (source_sha, checked_sha, request_sha, returned_prefix, written_prefix, expected) in INPUTS.items():
        directory = args.raw / case
        checked_path, request_path = directory / 'checked.json', directory / 'request.json'
        assert sha(checked_path) == checked_sha and sha(request_path) == request_sha
        checked, facts = json.loads(checked_path.read_text()), json.loads(request_path.read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert sha(source) == rows[case]['source_sha256'] == source_sha
        assert rows[case]['source_agreement'] and rows[case]['model']['status'] == 'normal'
        for engine in ('native', 'model'):
            assert base64.b64decode(rows[case][engine]['stdout']) == expected.encode()
            assert base64.b64decode(rows[case][engine]['stderr']) == b''
            assert rows[case][engine]['exit_status'] == 0
        assert checked['ok'] and checked['fixture']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stages = {
            0: ['$af_outputs(S.EVENTS) = $ptascii("U;")', '$af_function(S, $ptascii("ping"))'],
            1: ['$af_function(S, $ptascii("f"))', '$af_outputs(S.EVENTS) = $ptascii("U;P;")',
                '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED pvalue_y',
                '$string_bytes(pvalue_y) = ($ptascii("override"))'],
            2: ['S.CURRENT = eps', 'S.FRAMES = eps', 'S.RESULT = REFERENCE n_returned',
                f'$af_outputs(S.EVENTS) = $ptascii("{returned_prefix}")', '$lookup(S.ENV, $ptascii("r")) = eps'],
            3: ['S.CURRENT = eps', 'S.FRAMES = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                '$lookup(S.ENV, $ptascii("a")) = (n_a)', f'$af_outputs(S.EVENTS) = $ptascii("{returned_prefix}")'],
            4: ['S.CURRENT = eps', 'S.FRAMES = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_written', '$string_bytes(pvalue_written) = ($ptascii("changed"))',
                f'$af_outputs(S.EVENTS) = $ptascii("{written_prefix}")'],
        }
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
            'S_start = S_initial[.COMPLETION = NORMAL]', 'S = $af_find(S_start, 2000, 0)',
            'S.COMPLETION = NORMAL', '$af_stage(S, 0)',
            'S.FRAMES = pframe_f :: pframe_main :: eps', 'pframe_f.LOCALS = (psymboltable_f)',
            'pframe_f.CONTEXT = (pcallcontext_f)',
            '$function_at($all_functions(S), pcallcontext_f.FUNCTION) = (pfunction_f)',
            'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
            'pfunction_f.SIGNATURE.RETURNS = eps',
            '$af_pending(pframe_f.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_x) z)',
            'z = 3', '$origin_child((pcallcontext_f.FUNCTION), [PCFIELD 5, PCINDEX 1]) = (porigin_owner)',
            '$origin_child((porigin_owner), [PCFIELD 0, PCINDEX 0]) = (porigin_source)',
            '$origin_node(S.SOURCES, porigin_source) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return)',
            '$base64(text_x) = $ptascii("x")',
            '$task_nodes(FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_x) z) = [HCELL n_x]',
            'n_x <- S.REFCELLS', '(HCELL n_x) <- S.ALLOCATIONS',
            'S.STORE[n_x] = DEFINED (POBJECT n_object)', '(HOBJECT n_object) <- S.ALLOCATIONS',
            '$lookup(psymboltable_f.ENV, $ptascii("x")) = eps',
        ] + public('S') + [
            'S_y = $af_find($drive_steps(S, 1), 2000, 1)', 'S_y.COMPLETION = NORMAL', '$af_stage(S_y, 1)',
            '$lookup(S_y.ENV, $ptascii("y")) = (n_y)', 'n_y =/= n_x',
            '$lookup(S_y.ENV, $ptascii("x")) = eps',
            'S_y.STORE[n_y] = DEFINED pvalue_override', '$string_bytes(pvalue_override) = ($ptascii("override"))',
            '$af_pending(S_y.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_x) z)',
            'S_y.STORE[n_x] = DEFINED (POBJECT n_object)',
            '$origin_child((porigin_owner), [PCFIELD 2]) = (porigin_final)',
            '$origin_node(S_y.SOURCES, porigin_final) = (NStmtFinally (SEQUENCE statement_final*) metadata_final)',
            f'|statement_final*| = {5 if case == "cancelled" else 4}',
            '$origin_child((porigin_final), [PCFIELD 0, PCINDEX 3]) = (porigin_y)',
            '$origin_node(S_y.SOURCES, porigin_y) = (NStmtExpression (NExprAssign (NExprVariable (BYTES text_y) metadata_y) (NScalarString (BYTES text_override) metadata_override) metadata_assign) metadata_statement)',
            '$base64(text_y) = $ptascii("y")', '$base64(text_override) = $ptascii("override")',
        ] + public('S_y')
        if case == 'cancelled':
            assertions += ['$origin_child((porigin_final), [PCFIELD 0, PCINDEX 4]) = (porigin_return_y)',
                '$origin_node(S_y.SOURCES, porigin_return_y) = (NStmtReturn (NExprVariable (BYTES text_return_y) metadata_return_y_variable) metadata_return_y)',
                '$base64(text_return_y) = $ptascii("y")', 'n_selected = n_y', 'pvalue_selected = pvalue_override']
        else:
            assertions += ['n_selected = n_x', 'pvalue_selected = POBJECT n_object']
        assertions += [
            'S_returned = $af_find($drive_steps(S_y, 1), 2000, 2)', 'S_returned.COMPLETION = NORMAL',
            '$af_stage(S_returned, 2)', 'S_returned.RESULT = REFERENCE n_selected',
            'S_returned.GLOBALTABLE = eps', 'S_returned.STORE[n_selected] = DEFINED pvalue_selected',
            'n_selected <- S_returned.REFCELLS', '(HCELL n_selected) <- S_returned.ALLOCATIONS',
        ] + (['(HOBJECT n_object) <- S_returned.ALLOCATIONS'] if case == 'delivered' else []) + public('S_returned') + [
            'S_alias = $af_find($drive_steps(S_returned, 1), 2000, 3)', 'S_alias.COMPLETION = NORMAL',
            '$af_stage(S_alias, 3)', '$lookup(S_alias.ENV, $ptascii("r")) = (n_selected)',
            '$lookup(S_alias.ENV, $ptascii("a")) = (n_selected)', '$lookup(S_alias.ENV, $ptascii("x")) = eps',
            '$lookup(S_alias.ENV, $ptascii("y")) = eps', 'S_alias.STORE[n_selected] = DEFINED pvalue_selected',
            'n_selected <- S_alias.REFCELLS', '(HCELL n_selected) <- S_alias.ALLOCATIONS',
        ] + public('S_alias') + [
            'S_written = $af_find($drive_steps(S_alias, 1), 2000, 4)', 'S_written.COMPLETION = NORMAL',
            '$af_stage(S_written, 4)', '$lookup(S_written.ENV, $ptascii("r")) = (n_selected)',
            '$lookup(S_written.ENV, $ptascii("a")) = (n_selected)',
            'S_written.STORE[n_selected] = DEFINED pvalue_changed',
            '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
            'n_selected <- S_written.REFCELLS', '(HCELL n_selected) <- S_written.ALLOCATIONS',
        ] + public('S_written') + [
            # Budget equality starts at the genuine main r/a alias cut.
            'S_zero = $drive(S_alias, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 1000)',
            'S_whole = $drive(S_alias, 1001)', 'S_adjacent = S_whole',
            'S_whole.COMPLETION = NORMAL', f'$af_outputs(S_whole.EVENTS) = $ptascii("{expected}")',
            'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
            'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps', 'S_whole.GLOBALTABLE = eps',
            'S_whole.DESTRUCTION.CALLS = eps', 'S_whole.DESTRUCTION.RELEASES = eps',
            'S_whole.DESTRUCTION.OPERATIONS = eps',
            '$lookup(S_whole.ENV, $ptascii("r")) = (n_selected)', '$lookup(S_whole.ENV, $ptascii("a")) = (n_selected)',
            '$lookup(S_whole.ENV, $ptascii("x")) = eps', '$lookup(S_whole.ENV, $ptascii("y")) = eps',
            'S_whole.STORE[n_selected] = DEFINED pvalue_changed',
            'n_selected <- S_whole.REFCELLS', '(HCELL n_selected) <- S_whole.ALLOCATIONS',
        ] + public('S_whole')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-carrier-caller.watsup'
        path.write_text(PREFIX + QUIET + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case + '-carrier-caller', 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD, 'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
