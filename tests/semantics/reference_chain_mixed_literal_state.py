"""Emit checked-source state proofs for ordinary inner CV and terminal literal history chains."""
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
    catalogue = ROOT / 'tests/semantics/reference_chain_mixed_literal_cases.json'
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

    primary, normal = 'mixed-chain-literal-primary', 'mixed-chain-literal-selected'
    chain = '[prefreturncursor_z, prefreturncursor_w, prefreturncursor_o]'
    wx = '[prefreturncursor_w, prefreturncursor_o]'
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
           '(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: '
           '(TYPE_FALLTHROUGH porigin_function) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps']
    sites = ['$af_function(S, $ptascii("f"))']
    for name in ('z', 'w', 'o'):
        sites += [f'prefreturncursor_{name} = {{ OWNER porigin_{name}_owner, SOURCE porigin_{name}, LINE z_{name}, OUTER porigin_{name}_restore? }}']
    for name in ('z', 'w', 'y'):
        sites += [f'$origin_node(S.SOURCES, porigin_{name}) = (NStmtReturn (NExprVariable (BYTES text_{name}) metadata_{name}) metadata_return_{name})',
                  f'$base64(text_{name}) = $ptascii("{name}")', f'z_{name} = 4',
                  f'$lookup(S.ENV, $ptascii("{name}")) = (n_{name})']
    sites += ['$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_old) metadata_old) metadata_return_o)',
              '$base64(text_old) = $ptascii("old")', 'z_o = 4',
              'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
              '$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
              '$ref_chain_outer_literal(S, prefreturncursor_o)',
              '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps',
              'porigin_z_restore? = $origin_child((porigin_w_owner), [PCFIELD 2])',
              'porigin_w_restore? = $origin_child((porigin_o_owner), [PCFIELD 2])',
              'porigin_o_restore? = (porigin_function)',
              f'prefreturncursor_chain* = {chain}', '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
              '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0']
    complete = ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
                f'prefreturncursor_chain* = {chain}']
    capture = pre + globals + sites + ['$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;")',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)', 'S.ORIGIN = $origin_child((porigin_z_owner), [PCFIELD 2])']
    for name in ('w', 'z'):
        capture += [f'$heap_owners($heap_graph(S), HCELL n_{name}) = 3']
    pending1 = 'REF_RETURN_CHAIN_PENDING ([prefreturncursor_z]) ([prefreturncursor_w, prefreturncursor_o]) porigin_y z_y'
    pending2 = 'REF_RETURN_CHAIN_PENDING ([prefreturncursor_z, prefreturncursor_w]) ([prefreturncursor_o]) porigin_y z_y'
    capture += ['S_p1 = $drive_steps(S, 1)', 'S_p1.COMPLETION = BUDGET',
        'S_p1.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, FINALLY_REF_RETURN porigin_w_owner porigin_w (REFERENCE n_w) z_w, FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?, TYPE_FALLTHROUGH porigin_function, ' + pending1 + ', REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_p1.ORIGIN = porigin_z_restore?', f'$task_nodes({pending1}) = eps']
    capture += roots('S_p1', ('w',)) + public('S_p1', 'p1')
    capture += ['S_p2 = $drive_steps(S_p1[.COMPLETION = NORMAL], 1)', 'S_p2.COMPLETION = BUDGET',
        'S_p2.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?, TYPE_FALLTHROUGH porigin_function, ' + pending2 + ', REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_p2.ORIGIN = porigin_w_restore?', f'$task_nodes({pending2}) = eps']
    capture += roots('S_p2') + public('S_p2', 'p2')
    capture += ['S_full = $drive_steps(S_p2[.COMPLETION = NORMAL], 1)', 'S_full.COMPLETION = BUDGET',
        'S_full.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH porigin_function, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_full.ORIGIN = (porigin_function)', '$task_nodes(REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y) = eps']
    capture += roots('S_full') + public('S_full', 'full')
    capture += ['$heap_owners($heap_graph(S), HCELL n_x) = 2',
                '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps']
    for state, retired in (('S_p1', ('z',)), ('S_p2', ('z', 'w')), ('S_full', ('z', 'w'))):
        for name in ('w', 'z'):
            capture += [f'$heap_owners($heap_graph({state}), HCELL n_{name}) = ' + ('2' if name in retired else '3')]
        capture += [f'$heap_owners($heap_graph({state}), HCELL n_x) = 2', f'{state}.STORE = S.STORE', f'{state}.FRAMES = S.FRAMES', f'{state}.HELD = S.HELD',
                    f'{state}.EVENTS = S.EVENTS', f'$reference_notice_count({state}.TODO) = 0',
                    f'$heap_owners($heap_graph({state}), HCELL n_y) = $heap_owners($heap_graph(S), HCELL n_y)']
    literal_start = ['$af_function(S, $ptascii("f"))',
                     'S.TODO = (RETURN_REF_VALUE z_o) :: ptask_literal_tail*',
                     'S.ORIGIN = (porigin_o)',
                     '$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_old) metadata_old) metadata_return_o)']
    literal_checks = literal_start + [
        '$base64(text_old) = $ptascii("old")', 'z_o = 4',
        'S.RESULT = KNOWN pvalue_old', 'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
        '$reference_return_value_valid(S, z_o)', '$reference_notice_count(S.TODO) = 0',
        '$af_outputs(S.EVENTS) = eps', '$ma_diagnostics(S.EVENTS) = 0',
        'S_literal = $drive_steps(S, 1)', 'S_literal.COMPLETION = BUDGET',
        'S_literal.TODO = (RETURN_REF_UNWIND (KNOWN pvalue_old) z_o false porigin_o) :: ptask_notice_tail*',
        '$reference_notice_count(S_literal.TODO) = 1',
        '$reference_notice_end(S_literal.TODO, porigin_o, z_o, REF_NOTICE_VALUE)',
        '$task_nodes(REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) = eps',
        'S_literal.STORE = S.STORE', 'S_literal.REFCELLS = S.REFCELLS',
        '$call_descriptors_valid(S_literal)', '$heap_valid($heap_graph(S_literal))',
        'S_capture = $af_find(S_literal, 2000, 1)', 'S_capture.COMPLETION = NORMAL', '$af_stage(S_capture, 1)',
    ]
    import re
    literal_checks += [re.sub(r'\bS\b', 'S_capture', condition) for condition in capture]
    fixture('literal-value-notice-and-chain-capture', primary, {0: literal_start, 1: pre}, literal_checks, bad=[
        f'S_p1[.TODO = $af_replace(S_p1.TODO, {pending1}, [{pending1}, {pending1}])]',
        f'S_full[.TODO = $af_replace(S_full.TODO, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, [REF_RETURN_CHAIN ({wx}) porigin_y z_y])]',
        'S_full[.TODO = $af_replace(S_full.TODO, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y, eps)]',
        'S_p2[.TODO = S_p2.TODO ++ [REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE]]',
    ])

    cursor_fields = []
    for name in ('z', 'w', 'o'):
        cursor_fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER', f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                          f'z_{name} = prefreturncursor_{name}.LINE', f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    replay = complete + globals + cursor_fields + ['$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
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
        'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* ([prefreturncursor_w, prefreturncursor_z, prefreturncursor_o])]]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, ORIGIN_RETURN porigin_z_restore?, [ORIGIN_RETURN porigin_o_restore?])]',
    ])

    body = '[FINALLY_REF_CHAIN prefreturncursor_chain*, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CHAIN ([prefreturncursor_w, prefreturncursor_o]), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]'
    saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
        '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;I2;P;")',
        '$ref_chain_consumed_tail(pframe.TODO) = (FINALLY_REF_CHAIN prefreturncursor_chain*) :: ptask_chain_tail*',
        f'prefreturncursor_chain* = {chain}']
    restored = ['$af_function(S, $ptascii("f"))',
        '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;I2;P;")', '$ref_chain_consumed_tail(S.TODO) =/= eps']
    saved_checks = saved + globals + cursor_fields + ['S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
        '$af_function(S_scope, $ptascii("f"))', f'$ref_chain_consumed_tail(pframe.TODO) = {body}',
        '$ref_chain_links(S_scope, prefreturncursor_chain*)',
        '$ref_return_cursor_literal(S_scope, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '~$ref_chain_cleared_site(S_scope, prefreturncursor_chain*)',
        '~((HCELL n_x) <- $tasks_nodes(pframe.TODO))', '$heap_owners($heap_graph(S), HCELL n_x) = 2', '$call_tasks_valid(S_scope, pframe.TODO)',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_y_owner (n_error))',
        '$throwable_live(S_scope, n_error)', '$throwable_previous_id(S_scope, n_error) = eps',
        '$throwable_field(S_scope, n_error, "line") = PINT 4',
        '$string_bytes($throwable_field(S_scope, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$reference_notice_count(pframe.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        '$task_nodes(FINALLY_REF_CHAIN prefreturncursor_chain*) = eps']
    for name in ('w', 'z'):
        saved_checks += [f'~((HCELL n_{name}) <- $tasks_nodes(pframe.TODO))', f'$heap_owners($heap_graph(S), HCELL n_{name}) = 2']
    saved_checks += public('S', 'saved') + ['S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN', 'S_restored.CURRENT = pframe.CONTEXT',
        'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS', '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))']
    fixture('saved-chain-in-replayed-ping', primary, {0: saved, 1: restored}, saved_checks, bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CHAIN prefreturncursor_chain*, [FINALLY_REF_CHAIN ([prefreturncursor_z[.LINE = $(z_z + 1)], prefreturncursor_w, prefreturncursor_o])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, ORIGIN_RETURN porigin_w_restore?, [ORIGIN_RETURN porigin_o_restore?])] :: pframe_tail*]',
    ])

    escaping = ['S.TODO = [THROW_SEARCH n_error, ' + body[1:-1] + ']', f'prefreturncursor_chain* = {chain}',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;I2;P;")']
    escape = escaping + globals + cursor_fields + ['$throwable_live(S, n_error)', '$throwable_previous_id(S, n_error) = eps',
        'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        '$call_task_valid(S, FINALLY_REF_CHAIN prefreturncursor_chain*)'] + roots('S')
    escape += ['S_wx = $drive_steps(S, 1)', 'S_wx.COMPLETION = BUDGET',
        f'S_wx.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ({wx}), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'S_wx.ORIGIN = porigin_z_restore?', '$throwable_live(S_wx, n_error)'] + public('S_wx', 'wx')
    escape += ['S_x = $drive_steps(S_wx[.COMPLETION = NORMAL], 1)', 'S_x.COMPLETION = BUDGET',
        'S_x.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'S_x.ORIGIN = porigin_w_restore?', '$throwable_live(S_x, n_error)'] + public('S_x', 'x')
    escape += ['S_exit = $drive_steps(S_x[.COMPLETION = NORMAL], 1)', 'S_exit.COMPLETION = BUDGET',
        'S_exit.TODO = [THROW_SEARCH n_error]', 'S_exit.ORIGIN = porigin_o_restore?', '$tc_markers(S_exit.TODO) = 0',
        '$throwable_live(S_exit, n_error)', 'S_exit.STORE = S.STORE', 'S_exit.EVENTS = S.EVENTS'] + public('S_exit', 'exit')
    fixture('z-w-literal-error-retirement-and-caller-catch', primary, {0: escaping}, escape, finish='S_exit', budget=True,
            terminal=['$lookup(S_whole.ENV, $ptascii("r")) = eps',
                      '$lookup(S_whole.ENV, $ptascii("e")) = (n_caller_e)',
                      'S_whole.STORE[n_caller_e] = DEFINED (POBJECT n_error)'] +
                     [f'S_whole.STORE[n_{name}] = DEFINED pvalue_{name}' for name in ('x', 'w', 'z')])

    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
               'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    selected = complete + globals + cursor_fields + ['$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
        '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I2;P;")', 'S.STORE[n_y] = DEFINED pvalue_y',
        '$string_bytes(pvalue_y) = ($ptascii("fixed"))', '$reference_notice_count(S.TODO) = 0',
        'S.ORIGIN = porigin_o_restore?'] + roots('S')
    selected += ['S_returned = $drive_steps(S, 1)', 'S_returned.COMPLETION = BUDGET',
        'S_returned.RESULT = REFERENCE n_y', 'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        '$tc_markers(S_returned.TODO) = 0', 'S_returned.STORE[n_y] = DEFINED pvalue_y'] + public('S_returned', 'returned')
    selected += ['S_r = $af_find(S_returned, 2000, 1)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        '$lookup(S_r.ENV, $ptascii("y")) = (n_y)', 'S_written = $af_find($drive_steps(S_r, 1), 2000, 2)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))']
    fixture('selected-y-chain-retirement-and-caller-alias', normal, {0: complete, 1: assigned, 2: written}, selected,
            finish='S_written', terminal=[f'S_whole.STORE[n_{name}] = DEFINED pvalue_{name}' for name in ('x', 'w', 'z')] +
            ['S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'public_refusals': sum(row['public_refusals'] for row in records), 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
