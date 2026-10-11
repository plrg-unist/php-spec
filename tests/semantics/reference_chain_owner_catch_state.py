"""Emit checked-source caught-owner CV chain frontiers."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_multiple_active_cv_state import PREFIX, sha
from request_environment_state import request_fixture

PREFIX += r'''
dec $tc_marker(ptask) : bool
def $tc_marker(REF_RETURN_CHAIN_PENDING prefreturncursor_done* prefreturncursor_live* porigin z) = true
def $tc_marker(REF_RETURN_CHAIN prefreturncursor_chain* porigin z) = true
def $tc_marker(REF_RETURN_CHAIN_CLEARED prefreturncursor_chain*) = true
def $tc_marker(REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* prefowner*) = true
def $tc_marker(REF_REPLAY_CHAIN porigin poperand z prefowner* prefreturncursor_chain*) = true
def $tc_marker(FINALLY_REF_CHAIN prefreturncursor_chain*) = true
def $tc_marker(ptask) = false -- otherwise
dec $tc_markers(ptask*) : nat
def $tc_markers(eps) = 0
def $tc_markers(ptask :: ptask_tail*) = $(1 + $tc_markers(ptask_tail*)) -- if $tc_marker(ptask)
def $tc_markers(ptask :: ptask_tail*) = $tc_markers(ptask_tail*) -- if ~$tc_marker(ptask)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_chain_owner_catch_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['passed'] and report['workers_closed']
    assert report['pins'] == report['pins_after']
    assert report['module_stats'] == report['module_stats_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    rows = {row['id']: row for row in report['results']}
    assert rows.keys() == cases.keys()
    for row in rows.values():
        assert row['source_agreement'] and row['model']['status'] == 'normal'
        assert all(row['native'][key] == row['model'][key]
                   for key in ('stdout', 'stderr', 'exit_status'))
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, case_id, stages, checks, bad=(), finish=None, budget=False, terminal=()):
        row, case = rows[case_id], cases[case_id]
        directory = args.raw / case_id
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert source.read_bytes() == case['source'].encode()
        assert sha(source) == row['source_sha256']
        assert base64.b64decode(row['native']['stdout']) == case['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == case['stderr'].encode() == b''
        assert row['native']['exit_status'] == case['exit'] == 0
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        executed = json.loads((directory / 'state.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture'] and executed['ok']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]',
                      'S = $af_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL',
                      '$af_stage(S, 0)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
        assertions += checks
        for index, mutation in enumerate(bad):
            assertions += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                           f'~$call_descriptors_valid(S_bad{index})',
                           f'S_rejected{index} = $drive(S_bad{index}, 0)',
                           f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
        if finish is not None:
            assertions += [f'S_continue = {finish}[.COMPLETION = NORMAL]']
            if budget:
                assertions += ['S_zero = $drive(S_continue, 0)', 'S_zero.COMPLETION = BUDGET',
                               'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
                               'S_whole = $drive(S_continue, 10001)', 'S_adjacent = S_whole']
            else:
                assertions += ['S_whole = $drive(S_continue, 10001)']
            assertions += ['S_whole.COMPLETION = NORMAL',
                           '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(case['stdout']) + ')',
                           '$ma_diagnostics(S_whole.EVENTS) = 0', '$reference_notice_count(S_whole.TODO) = 0',
                           'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                           'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                           '$tc_markers(S_whole.TODO) = 0',
                           '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case_id, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions),
                        'public_refusals': len(bad)})

    def public(state, tag):
        admitted = 'S_admitted_' + tag
        return [f'{admitted} = $drive({state}[.COMPLETION = NORMAL], 0)',
                f'{admitted}.COMPLETION = BUDGET', f'{admitted}.TODO = {state}.TODO',
                f'$call_descriptors_valid({admitted})', f'$heap_valid($heap_graph({admitted}))']

    def roots(state, live=()):
        return [('' if name in live else '~') + f'((HCELL n_{name}) <- $tasks_nodes({state}.TODO))'
                for name in ('x', 'w', 'z')]

    primary = 'third-cv-y-owner-catch'
    rethrow = 'third-cv-y-owner-catch-rethrow'
    chain = '[prefreturncursor_z, prefreturncursor_w, prefreturncursor_x]'
    wx = '[prefreturncursor_w, prefreturncursor_x]'
    globals = ['S.GLOBALTABLE = (psymboltable)']
    for name in ('x', 'w', 'z', 'y'):
        globals += [f'$lookup(psymboltable.ENV, $ptascii("{name}")) = (n_{name})']
    globals += [r'n_x =/= n_w /\ n_x =/= n_z /\ n_x =/= n_y /\ n_w =/= n_z /\ n_w =/= n_y /\ n_z =/= n_y']
    for name, value in (('x', 'old'), ('w', 'extra'), ('z', 'mid')):
        globals += [f'S.STORE[n_{name}] = DEFINED pvalue_{name}',
                    f'$string_bytes(pvalue_{name}) = ($ptascii("{value}"))']
    pre = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: '
           '(FINALLY_REF_RETURN porigin_z_owner porigin_z (REFERENCE n_z) z_z) :: (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: '
           '(FINALLY_REF_RETURN porigin_w_owner porigin_w (REFERENCE n_w) z_w) :: (FINALLY_PHASE porigin_w_owner 3) :: (ORIGIN_RETURN porigin_w_restore?) :: '
           '(FINALLY_REF_RETURN porigin_x_owner porigin_x (REFERENCE n_x) z_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: '
           '(TYPE_FALLTHROUGH porigin_function) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps']
    sites = ['$af_function(S, $ptascii("f"))']
    for name in ('z', 'w', 'x'):
        sites += [f'prefreturncursor_{name} = {{ OWNER porigin_{name}_owner, SOURCE porigin_{name}, LINE z_{name}, OUTER porigin_{name}_restore? }}']
    for name in ('z', 'w', 'x', 'y'):
        sites += [f'$origin_node(S.SOURCES, porigin_{name}) = (NStmtReturn (NExprVariable (BYTES text_{name}) metadata_{name}) metadata_return_{name})',
                  f'$base64(text_{name}) = $ptascii("{name}")', f'z_{name} = 4',
                  f'$lookup(S.ENV, $ptascii("{name}")) = (n_{name})']
    sites += ['porigin_z_restore? = $origin_child((porigin_w_owner), [PCFIELD 2])',
              'porigin_w_restore? = $origin_child((porigin_x_owner), [PCFIELD 2])',
              'porigin_x_restore? = (porigin_function)',
              f'prefreturncursor_chain* = {chain}', '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
              '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0']
    catch_site = [
        '$ref_replay_owners(S, porigin_y) = porigin_first :: eps',
        '$origin_node(S.SOURCES, porigin_first) = (NStmtTryCatch phpType23_body (SEQUENCE ([NStmtCatch (SEQUENCE ([NName (BYTES text_type) metadata_type])) (NExprVariable (BYTES text_e) metadata_e) (SEQUENCE ([NStmtEcho (SEQUENCE ([NScalarString (BYTES text_c) metadata_c])) metadata_echo])) metadata_catch])) phpType67_final metadata_try)',
        '$base64(text_type) = $ptascii("TypeError")',
        '$base64(text_e) = $ptascii("e")', '$base64(text_c) = $ptascii("C;")',
        '$ref_chain_selected_owner(S, porigin_first)',
    ]
    sites += catch_site
    complete = ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
                f'prefreturncursor_chain* = {chain}']
    capture = pre + globals + sites + ['$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;")',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)', 'S.ORIGIN = $origin_child((porigin_z_owner), [PCFIELD 2])']
    for name in ('x', 'w', 'z'):
        capture += [f'$heap_owners($heap_graph(S), HCELL n_{name}) = 3']
    pending1 = 'REF_RETURN_CHAIN_PENDING ([prefreturncursor_z]) ([prefreturncursor_w, prefreturncursor_x]) porigin_y z_y'
    pending2 = 'REF_RETURN_CHAIN_PENDING ([prefreturncursor_z, prefreturncursor_w]) ([prefreturncursor_x]) porigin_y z_y'
    capture += ['S_p1 = $drive_steps(S, 1)', 'S_p1.COMPLETION = BUDGET',
        'S_p1.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, FINALLY_REF_RETURN porigin_w_owner porigin_w (REFERENCE n_w) z_w, FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_RETURN porigin_x_owner porigin_x (REFERENCE n_x) z_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?, TYPE_FALLTHROUGH porigin_function, ' + pending1 + ', REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_p1.ORIGIN = porigin_z_restore?', f'$task_nodes({pending1}) = eps']
    capture += roots('S_p1', ('w', 'x')) + public('S_p1', 'p1')
    capture += ['S_p2 = $drive_steps(S_p1[.COMPLETION = NORMAL], 1)', 'S_p2.COMPLETION = BUDGET',
        'S_p2.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, FINALLY_REF_RETURN porigin_x_owner porigin_x (REFERENCE n_x) z_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?, TYPE_FALLTHROUGH porigin_function, ' + pending2 + ', REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_p2.ORIGIN = porigin_w_restore?', f'$task_nodes({pending2}) = eps']
    capture += roots('S_p2', ('x',)) + public('S_p2', 'p2')
    capture += ['S_full = $drive_steps(S_p2[.COMPLETION = NORMAL], 1)', 'S_full.COMPLETION = BUDGET',
        'S_full.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH porigin_function, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_full.ORIGIN = (porigin_function)', '$task_nodes(REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y) = eps']
    capture += roots('S_full') + public('S_full', 'full')
    for state, retired in (('S_p1', ('z',)), ('S_p2', ('z', 'w')), ('S_full', ('z', 'w', 'x'))):
        for name in ('x', 'w', 'z'):
            capture += [f'$heap_owners($heap_graph({state}), HCELL n_{name}) = ' + ('2' if name in retired else '3')]
        capture += [f'{state}.STORE = S.STORE', f'{state}.FRAMES = S.FRAMES', f'{state}.HELD = S.HELD',
                    f'{state}.EVENTS = S.EVENTS', f'$reference_notice_count({state}.TODO) = 0',
                    f'$heap_owners($heap_graph({state}), HCELL n_y) = $heap_owners($heap_graph(S), HCELL n_y)']
    fixture('ordered-chain-capture', primary, {0: pre}, capture, bad=[
        f'S_p1[.TODO = $af_replace(S_p1.TODO, {pending1}, [{pending1}, {pending1}])]',
        f'S_full[.TODO = $af_replace(S_full.TODO, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, [REF_RETURN_CHAIN ({wx}) porigin_y z_y])]',
        'S_full[.TODO = $af_replace(S_full.TODO, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y, eps)]',
    ])

    cursor_fields = []
    for name in ('z', 'w', 'x'):
        cursor_fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER', f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                          f'z_{name} = prefreturncursor_{name}.LINE', f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    replay = complete + globals + cursor_fields + catch_site + ['$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
        '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;")',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)', '$ref_replay_contexts(S, porigin_y) = prefowner*',
        'prefowner* = [REPLAY_TRY porigin_first]',
        'S_error = $drive_steps(S, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*]',
        '$throwable_live(S_error, n_error)', '$throwable_previous_id(S_error, n_error) = eps',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        '$throwable_field(S_error, n_error, "line") = PINT z_y',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$task_nodes(REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*) = [HCELL n_y]']
    replay += roots('S_error') + public('S_error', 'error')
    replay += ['S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
        'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_chain_consumed_tasks(prefreturncursor_chain*))',
        'S_expanded.ORIGIN = (porigin_first)',
        '$ref_chain_consumed_tail(S_expanded.TODO) = $ref_chain_consumed_body(prefreturncursor_chain*)']
    replay += roots('S_expanded') + public('S_expanded', 'expanded')
    fixture('chain-y-error-and-replay', primary, {0: complete}, replay, bad=[
        'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* ([prefreturncursor_w, prefreturncursor_z, prefreturncursor_x])]]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, ORIGIN_RETURN porigin_z_restore?, [ORIGIN_RETURN porigin_x_restore?])]',
    ])

    prefix_caught = 'O;P;W;P;M;P;I1;P;C;I2;P;'
    prefix_middle = prefix_caught + 'M;P;'
    prefix_selected = prefix_middle + 'I3;P;'
    body = '[FINALLY_REF_CHAIN prefreturncursor_chain*, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CHAIN ([prefreturncursor_w, prefreturncursor_x]), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_CHAIN ([prefreturncursor_x]), FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]'
    before = ['$af_function(S, $ptascii("f"))', 'S.TODO = ' + body,
              f'prefreturncursor_chain* = {chain}',
              '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix_caught) + ')']

    def old_error(state, object_name='n_old'):
        return [f'$lookup({state}.ENV, $ptascii("e")) = (n_e)',
                f'{state}.STORE[n_e] = DEFINED (POBJECT {object_name})',
                f'$throwable_live({state}, {object_name})',
                f'$throwable_previous_id({state}, {object_name}) = eps',
                f'$throwable_field({state}, {object_name}, "line") = PINT 4',
                f'$string_bytes($throwable_field({state}, {object_name}, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))']

    def cursor_sources(state):
        conditions = []
        for name in ('z', 'w', 'x'):
            conditions += [f'$origin_node({state}.SOURCES, porigin_{name}) = (NStmtReturn (NExprVariable (BYTES text_{name}) metadata_{name}) metadata_return_{name})',
                           f'$base64(text_{name}) = $ptascii("{name}")', f'z_{name} = 4',
                           f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{name})']
        return conditions

    common = before + globals + cursor_fields + cursor_sources('S') + old_error('S') + [
        'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        '$ref_chain_links(S, prefreturncursor_chain*)', '$ref_chain_cleared_site(S, prefreturncursor_chain*)',
        '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0',
        'S.ORIGIN = $origin_child((porigin_z_owner), [PCFIELD 2])']
    for name in ('x', 'w', 'z'):
        common += [f'$heap_owners($heap_graph(S), HCELL n_{name}) = 2']
    cleared = ['S_cleared = $drive_steps(S, 1)', 'S_cleared.COMPLETION = BUDGET',
        'S_cleared.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z, REF_RETURN_CHAIN_CLEARED prefreturncursor_chain*, REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z]',
        'S_cleared.ORIGIN = porigin_x_restore?', '$ref_chain_cleared_valid(S_cleared, prefreturncursor_chain*)',
        '$task_nodes(REF_RETURN_CHAIN_CLEARED prefreturncursor_chain*) = eps', '$tasks_nodes(S_cleared.TODO) = eps',
        'S_cleared.RESULT = KNOWN PNULL', 'S_cleared.BASE = BASE_VALUE (KNOWN PNULL)']
    for field in ('STORE', 'OBJECTS', 'EVENTS', 'FRAMES', 'CURRENT', 'HELD', 'RETIREDOWNERS'):
        cleared += [f'S_cleared.{field} = S.{field}']
    cleared += public('S_cleared', 'cleared')
    fresh = ['S_error = $drive_steps(S_cleared[.COMPLETION = NORMAL], 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_new, REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* prefowner*]',
        'prefowner* = [REPLAY_TRY porigin_z_owner]', 'n_new =/= n_old', '$throwable_live(S_error, n_new)',
        '$throwable_previous_id(S_error, n_new) = eps', '$throwable_field(S_error, n_new, "line") = PINT z_z',
        '$string_bytes($throwable_field(S_error, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        'S_error.STORE[n_e] = DEFINED (POBJECT n_old)', '$throwable_live(S_error, n_old)',
        '$ref_chain_cleared_replay_valid(S_error, prefreturncursor_chain*, prefowner*)',
        '$task_nodes(REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* prefowner*) = eps',
        'S_error.STORE = S.STORE', 'S_error.EVENTS = S.EVENTS']
    fresh += roots('S_error') + public('S_error', 'fresh')
    fresh += ['S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
        f'S_expanded.TODO = (THROW_SEARCH n_new) :: ($ref_replay_tasks(porigin_z, z_z, prefowner*) ++ $ref_chain_consumed_tasks({wx}))',
        f'$ref_chain_consumed_tail(S_expanded.TODO) = $ref_chain_consumed_body({wx})',
        'S_expanded.ORIGIN = (porigin_z_owner)', 'S_expanded.STORE[n_e] = DEFINED (POBJECT n_old)',
        '$reference_notice_count(S_expanded.TODO) = 0'] + public('S_expanded', 'expanded')
    internal = ['S_internal = $finally_leave_ref_return(S, porigin_z_owner, porigin_z, KNOWN PNULL, z_z, true, (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: $ref_chain_consumed_body(' + wx + '))',
        f'S_internal.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z] ++ $ref_chain_consumed_body({wx}) ++ [REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z]',
        'S_internal.ORIGIN = porigin_z_restore?', 'S_internal.STORE = S.STORE', 'S_internal.EVENTS = S.EVENTS',
        '$tasks_nodes(S_internal.TODO) = eps', '~$call_descriptors_valid(S_internal)',
        '~$ref_chain_cleared_valid(S_internal, prefreturncursor_chain*)']
    fixture('caught-chain-cleared-null-and-fresh-z-replay', primary, {0: before}, common + cleared + fresh + internal, bad=[
        'S_error[.TODO = [THROW_SEARCH n_new, REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* ([REPLAY_TRY porigin_w_owner])]]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, ORIGIN_RETURN porigin_w_restore?, [ORIGIN_RETURN porigin_x_restore?])]',
    ])

    saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix_middle) + ')',
        '$ref_chain_consumed_tail(pframe.TODO) = (FINALLY_REF_CHAIN prefreturncursor_tail*) :: ptask_chain_tail*',
        f'prefreturncursor_tail* = {wx}']
    restored = ['$af_function(S, $ptascii("f"))',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix_middle) + ')',
        '$ref_chain_consumed_tail(S.TODO) =/= eps']
    saved_fields = []
    for name in ('w', 'x'):
        saved_fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER', f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                         f'z_{name} = prefreturncursor_{name}.LINE', f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    saved_checks = saved + globals + saved_fields + ['S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
        '$af_function(S_scope, $ptascii("f"))', f'$ref_chain_links(S_scope, {wx})',
        f'$ref_chain_consumed_tail(pframe.TODO) = $ref_chain_consumed_body({wx})',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_z_owner (n_new))'] + old_error('S_scope') + [
        'n_old =/= n_new', '$throwable_live(S_scope, n_new)', '$throwable_previous_id(S_scope, n_new) = eps',
        '$throwable_field(S_scope, n_new, "line") = PINT 4',
        '$string_bytes($throwable_field(S_scope, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        '$ref_consumed_pair_tail(pframe.TODO) = eps', '$reference_notice_count(pframe.TODO) = 0',
        '$call_tasks_valid(S_scope, pframe.TODO)', '$tc_markers(pframe.TODO) = 2',
        'S.CURRENT = (pcallcontext_ping)', 'pframe.ORIGIN = (porigin_ping)',
        'pcallcontext_ping.CALLSITE = pframe.ORIGIN',
        'porigin_z_final? = $origin_child((porigin_z_owner), [PCFIELD 2])',
        'porigin_ping_statement? = $origin_child(porigin_z_final?, [PCFIELD 0, PCINDEX 1])',
        'pframe.ORIGIN = $origin_child(porigin_ping_statement?, [PCFIELD 0])',
        '$origin_node(S.SOURCES, porigin_ping) = (NExprFuncCall (NName (BYTES text_ping) metadata_ping_name) (SEQUENCE eps) metadata_ping_call)',
        '$base64(text_ping) = $ptascii("ping")',
        '(ORIGIN_RETURN porigin_ping_statement?) <- pframe.TODO',
        '(ORIGIN_RETURN porigin_z_final?) <- pframe.TODO']
    for name in ('x', 'w', 'z', 'y'):
        saved_checks += [f'$lookup(S_scope.ENV, $ptascii("{name}")) = (n_{name})']
    for name in ('x', 'w', 'z'):
        saved_checks += [f'~((HCELL n_{name}) <- $tasks_nodes(pframe.TODO))', f'$heap_owners($heap_graph(S), HCELL n_{name}) = 2']
    saved_checks += public('S', 'saved') + ['S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN', 'S_restored.CURRENT = pframe.CONTEXT',
        'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS', '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))']
    fixture('saved-z-null-error-and-w-x-history', primary, {0: saved, 1: restored}, saved_checks, bad=[
        f'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CHAIN ({wx}), [FINALLY_REF_CHAIN ([prefreturncursor_w[.LINE = $(z_w + 1)], prefreturncursor_x])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_RESUME porigin_z_owner (n_new), [FINALLY_RESUME porigin_z_owner eps])] :: pframe_tail*]',
    ])

    success = ['$af_function(S, $ptascii("f"))',
        'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix_selected) + ')']
    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
               'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    selected = success + globals + old_error('S') + ['$lookup(S.ENV, $ptascii("y")) = (n_y)',
        'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        '$origin_node(S.SOURCES, porigin_y) = (NStmtReturn (NExprVariable (BYTES text_y) metadata_y) metadata_return)',
        '$base64(text_y) = $ptascii("y")', 'z_y = 4', '$tc_markers(S.TODO) = 0',
        '$af_error_finally(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0'] + roots('S')
    selected += ['S_returned = $drive_steps(S, 1)', 'S_returned.COMPLETION = BUDGET',
        'S_returned.RESULT = REFERENCE n_y', 'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        '$tc_markers(S_returned.TODO) = 0'] + public('S_returned', 'returned')
    selected += ['S_r = $af_find(S_returned, 2000, 1)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        'S_written = $af_find($drive_steps(S_r, 1), 2000, 2)', '$lookup(S_written.ENV, $ptascii("r")) = (n_y)',
        '$lookup(S_written.ENV, $ptascii("y")) = (n_y)', '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))']
    fixture('caught-chain-selected-y-alias-and-cleanup', primary, {0: success, 1: assigned, 2: written}, selected,
        finish='S_written', budget=True,
        terminal=[f'S_whole.STORE[n_{name}] = DEFINED pvalue_{name}' for name in ('x', 'w', 'z')] +
        ['S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    escaping = ['$af_function(S, $ptascii("f"))', 'S.TODO = [THROW_SEARCH n_error, ' + body[1:-1] + ']',
        f'prefreturncursor_chain* = {chain}', '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix_caught) + ')']
    caller = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("e")) = (n_caller_e)',
              'S.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
              '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))']
    escape = escaping + globals + cursor_fields + old_error('S', 'n_error') + [
        '$ref_chain_links(S, prefreturncursor_chain*)', '$call_task_valid(S, FINALLY_REF_CHAIN prefreturncursor_chain*)',
        'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))'] + roots('S')
    escape += ['S_wx = $drive_steps(S, 1)', 'S_wx.COMPLETION = BUDGET',
        f'S_wx.TODO = [THROW_SEARCH n_error] ++ $ref_chain_consumed_body({wx})',
        'S_wx.ORIGIN = porigin_z_restore?'] + public('S_wx', 'wx')
    escape += ['S_x = $drive_steps(S_wx[.COMPLETION = NORMAL], 1)', 'S_x.COMPLETION = BUDGET',
        'S_x.TODO = [THROW_SEARCH n_error] ++ $ref_chain_consumed_body([prefreturncursor_x])',
        'S_x.ORIGIN = porigin_w_restore?'] + public('S_x', 'x')
    escape += ['S_exit = $drive_steps(S_x[.COMPLETION = NORMAL], 1)', 'S_exit.COMPLETION = BUDGET',
        'S_exit.TODO = [THROW_SEARCH n_error]', 'S_exit.ORIGIN = porigin_x_restore?',
        '$tc_markers(S_exit.TODO) = 0', 'S_exit.STORE = S.STORE', 'S_exit.EVENTS = S.EVENTS',
        '$throwable_live(S_exit, n_error)'] + public('S_exit', 'exit')
    escape += ['S_caller = $af_find(S_exit, 2000, 1)', '$lookup(S_caller.ENV, $ptascii("e")) = (n_caller_e)',
        'S_caller.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
        '$throwable_live(S_caller, n_error)', '$throwable_previous_id(S_caller, n_error) = eps',
        '$throwable_field(S_caller, n_error, "line") = PINT 4', '$tc_markers(S_caller.TODO) = 0']
    fixture('same-owner-rethrow-keeps-original-y-error', rethrow, {0: escaping, 1: caller}, escape,
        finish='S_caller', terminal=['$lookup(S_whole.ENV, $ptascii("r")) = eps',
        'S_whole.STORE[n_caller_e] = DEFINED (POBJECT n_error)'] +
        [f'S_whole.STORE[n_{name}] = DEFINED pvalue_{name}' for name in ('x', 'w', 'z')])

    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'public_refusals': sum(row['public_refusals'] for row in records), 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
