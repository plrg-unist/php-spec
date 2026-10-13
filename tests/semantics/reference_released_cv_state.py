"""Emit source-reached selected-return carrier and caller-alias checks."""
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

HEAD = 'b55942bc3764dc33d555861ae247faf26c4c1ead'
REPORT_SHA = '906a73bfa78e88d32b5d3fe0282e571b78e4366dfa90851dacfd3b62662b8e79'
INPUTS = {
    'released': ('ce6cdc9aaf21308f29c409774b46f5d556d2c82f33832b75e2c16a169ea7a274',
                 '4fbf49052a780d1df2cfbc99791bb7278b3c749e8c6830f031538f664aceea75',
                 '997664d039527dfdc33e12af8acbdb16896b412a206fdac72b4bc703bc468964', 'U:0;'),
    'retained': ('dbda81d94344b7cf65ce3711ec50222c672366f9dedd7881a336b75385a231cf',
                 'b4f83f426ee9da056ad9a87d531e0ad0fdb1af4f7f5fcc4d286d39d9779e3625',
                 'f8e4593a58db0c60ae9b8808d7ef32f9e9a57c4f85d8b346a96709e89164c3a8', 'U:1;'),
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
    for case, (source_sha, checked_sha, request_sha, prefix) in INPUTS.items():
        directory = args.raw / case
        checked_path, request_path = directory / 'checked.json', directory / 'request.json'
        assert sha(checked_path) == checked_sha and sha(request_path) == request_sha
        checked, facts = json.loads(checked_path.read_text()), json.loads(request_path.read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert sha(source) == rows[case]['source_sha256'] == source_sha
        expected = prefix + 'P;R:selected;A:changed;'
        assert rows[case]['source_agreement'] and rows[case]['model']['status'] == 'normal'
        for engine in ('native', 'model'):
            assert base64.b64decode(rows[case][engine]['stdout']) == expected.encode()
            assert base64.b64decode(rows[case][engine]['stderr']) == b''
            assert rows[case][engine]['exit_status'] == 0
        assert checked['ok'] and checked['fixture']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stages = {
            0: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")', '$af_function(S, $ptascii("ping"))'],
            1: ['S.CURRENT = eps', 'S.FRAMES = eps', 'S.RESULT = REFERENCE n_returned',
                f'$af_outputs(S.EVENTS) = $ptascii("{prefix}P;")', '$lookup(S.ENV, $ptascii("r")) = eps'],
            2: ['S.CURRENT = eps', 'S.FRAMES = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                '$lookup(S.ENV, $ptascii("a")) = (n_a)', f'$af_outputs(S.EVENTS) = $ptascii("{prefix}P;")'],
            3: ['S.CURRENT = eps', 'S.FRAMES = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_written', '$string_bytes(pvalue_written) = ($ptascii("changed"))',
                f'$af_outputs(S.EVENTS) = $ptascii("{prefix}P;R:selected;")'],
        }
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
            'S_start = S_initial[.COMPLETION = NORMAL]', 'S = $af_find(S_start, 2000, 0)',
            'S.COMPLETION = NORMAL', '$af_stage(S, 0)',
            'S.FRAMES = pframe_f :: pframe_main :: eps', 'pframe_f.LOCALS = (psymboltable_f)',
            'pframe_f.CONTEXT = (pcallcontext_f)',
            '$function_at($all_functions(S), pcallcontext_f.FUNCTION) = (pfunction_f)',
            'pfunction_f.NAME = $ptascii("f")', 'pfunction_f.SIGNATURE.BYREF',
            '$af_pending(pframe_f.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_cell) z)',
            'z = 3', '$origin_child((pcallcontext_f.FUNCTION), [PCFIELD 5, PCINDEX 1]) = (porigin_owner)',
            '$origin_child((porigin_owner), [PCFIELD 0, PCINDEX 0]) = (porigin_source)',
            '$origin_node(S.SOURCES, porigin_source) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return)',
            '$base64(text_x) = $ptascii("x")',
            '$task_nodes(FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_cell) z) = [HCELL n_cell]',
            'n_cell <- S.REFCELLS', '(HCELL n_cell) <- S.ALLOCATIONS',
            'S.STORE[n_cell] = DEFINED pvalue_selected', '$string_bytes(pvalue_selected) = ($ptascii("selected"))',
            ('$lookup(psymboltable_f.ENV, $ptascii("x")) = eps' if case == 'released' else
             '$lookup(psymboltable_f.ENV, $ptascii("x")) = (n_cell)'),
        ] + public('S') + [
            'S_returned = $af_find($drive_steps(S, 1), 2000, 1)', 'S_returned.COMPLETION = NORMAL',
            '$af_stage(S_returned, 1)', 'S_returned.RESULT = REFERENCE n_cell',
            'S_returned.GLOBALTABLE = eps', 'S_returned.STORE[n_cell] = DEFINED pvalue_selected',
            'n_cell <- S_returned.REFCELLS', '(HCELL n_cell) <- S_returned.ALLOCATIONS',
        ] + public('S_returned') + [
            'S_alias = $af_find($drive_steps(S_returned, 1), 2000, 2)', 'S_alias.COMPLETION = NORMAL',
            '$af_stage(S_alias, 2)', '$lookup(S_alias.ENV, $ptascii("r")) = (n_cell)',
            '$lookup(S_alias.ENV, $ptascii("a")) = (n_cell)', '$lookup(S_alias.ENV, $ptascii("x")) = eps',
            'S_alias.STORE[n_cell] = DEFINED pvalue_selected', 'n_cell <- S_alias.REFCELLS',
            '(HCELL n_cell) <- S_alias.ALLOCATIONS',
        ] + public('S_alias') + [
            'S_written = $af_find($drive_steps(S_alias, 1), 2000, 3)', 'S_written.COMPLETION = NORMAL',
            '$af_stage(S_written, 3)', '$lookup(S_written.ENV, $ptascii("r")) = (n_cell)',
            '$lookup(S_written.ENV, $ptascii("a")) = (n_cell)',
            'S_written.STORE[n_cell] = DEFINED pvalue_changed',
            '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
            'n_cell <- S_written.REFCELLS', '(HCELL n_cell) <- S_written.ALLOCATIONS',
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
            '$lookup(S_whole.ENV, $ptascii("r")) = (n_cell)', '$lookup(S_whole.ENV, $ptascii("a")) = (n_cell)',
            '$lookup(S_whole.ENV, $ptascii("x")) = eps', 'S_whole.STORE[n_cell] = DEFINED pvalue_changed',
            'n_cell <- S_whole.REFCELLS', '(HCELL n_cell) <- S_whole.ALLOCATIONS',
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
