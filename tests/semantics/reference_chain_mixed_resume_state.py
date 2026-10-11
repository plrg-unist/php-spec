"""Emit checked-source caught mixed-history literal-resumption frontiers."""
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
    catalogue = ROOT / 'tests/semantics/reference_chain_mixed_resume_cases.json'
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
        assert base64.b64decode(row['native']['stderr']) == case['stderr'].encode()
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
                           '$ma_diagnostics(S_whole.EVENTS) = ' + str(int(bool(case['stderr']))), '$reference_notice_count(S_whole.TODO) = 0',
                           'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                           'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                           '$tc_markers(S_whole.TODO) = 0',
                           '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))'] + list(terminal)
        if name == 'first-y-capture-and-authenticated-e-passage':
            # Public drive already checks descriptor admission or refusal.
            assertions = [condition for condition in assertions
                          if not condition.startswith(('$call_descriptors_valid(S_admitted_',
                                                       '~$call_descriptors_valid(S_bad'))]
        if name == 'e-rethrow-preserves-fresh-z-error-and-retires-literal':
            assertions = [condition for condition in assertions
                          if not condition.startswith('~$call_descriptors_valid(S_bad')]
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

    primary = 'mixed-literal-resume'
    success_id = 'mixed-literal-resume-y-success'
    rethrow_id = 'mixed-literal-resume-e-rethrow'
    chain = '[prefreturncursor_z, prefreturncursor_w, prefreturncursor_o]'
    wo = '[prefreturncursor_w, prefreturncursor_o]'
    prefix = 'O;P;W;P;M1;P;I1;P;'
    caught_prefix = prefix + 'I2;P;C;'
    saved_prefix = caught_prefix + 'M2;P;'
    literal_prefix = saved_prefix + 'E;B;'
    globals = ['S.GLOBALTABLE = (psymboltable)']
    for name in ('x', 'w', 'z', 'y'):
        globals += [f'$lookup(psymboltable.ENV, $ptascii("{name}")) = (n_{name})']
    globals += [r'n_x =/= n_w /\ n_x =/= n_z /\ n_x =/= n_y /\ n_w =/= n_z /\ n_w =/= n_y /\ n_z =/= n_y']
    for name, value in (('x', 'old'), ('w', 'extra')):
        globals += [f'S.STORE[n_{name}] = DEFINED pvalue_{name}',
                    f'$string_bytes(pvalue_{name}) = ($ptascii("{value}"))']
    cursor_fields = []
    for name in ('z', 'w', 'o'):
        cursor_fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER',
                          f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                          f'z_{name} = prefreturncursor_{name}.LINE',
                          f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    old_literal = [
        '$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_old) metadata_old) metadata_return_o)',
        '$base64(text_old) = $ptascii("old")', 'z_o = 4',
        'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
        '$ref_chain_outer_literal(S, prefreturncursor_o)',
        'porigin_o_restore? = (porigin_function)',
    ]
    pre_tail = ('(FINALLY_REF_RETURN porigin_z_owner porigin_z (REFERENCE n_z) z_z) :: '
        '(FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: '
        '(FINALLY_REF_RETURN porigin_w_owner porigin_w (REFERENCE n_w) z_w) :: '
        '(FINALLY_PHASE porigin_w_owner 3) :: (ORIGIN_RETURN porigin_w_restore?) :: '
        '(TRY_END porigin_e_catch) :: (ORIGIN_RETURN porigin_e_restore?) :: '
        '(AT porigin_echo_b (STMT statement_echo_b)) :: '
        '(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) :: '
        '(FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: '
        '(TYPE_FALLTHROUGH porigin_function) :: '
        '(REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps')
    pre = ['$af_function(S, $ptascii("f"))',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix) + ')',
        'S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: '
        '(TRY_END porigin_y_catch) :: (ORIGIN_RETURN porigin_y_restore?) :: '
        '(AT porigin_set_z (STMT statement_set_z)) :: (ORIGIN_RETURN porigin_after_z?) :: ' + pre_tail]
    sites = []
    for name in ('z', 'w', 'o'):
        sites += [f'prefreturncursor_{name} = {{ OWNER porigin_{name}_owner, SOURCE porigin_{name}, LINE z_{name}, OUTER porigin_{name}_restore? }}']
    for name in ('z', 'w', 'y'):
        sites += [f'$origin_node(S.SOURCES, porigin_{name}) = (NStmtReturn (NExprVariable (BYTES text_{name}) metadata_{name}) metadata_return_{name})',
                  f'$base64(text_{name}) = $ptascii("{name}")', f'z_{name} = 4',
                  f'$lookup(S.ENV, $ptascii("{name}")) = (n_{name})']
    sites += old_literal + [
        'porigin_z_restore? = $origin_child((porigin_w_owner), [PCFIELD 2])',
        'porigin_w_restore? = (porigin_e_catch)',
        'porigin_e_restore? = $origin_child((porigin_o_owner), [PCFIELD 2])',
        'porigin_y_restore? = $origin_child((porigin_z_owner), [PCFIELD 2, PCFIELD 0, PCINDEX 3])',
        'porigin_after_z? = $origin_child((porigin_z_owner), [PCFIELD 2])',
        '$origin_child(porigin_y_restore?, [PCFIELD 1, PCINDEX 1]) = (porigin_set_z)',
        '$origin_node(S.SOURCES, porigin_set_z) = (NStmtExpression (NExprAssign (NExprVariable (BYTES text_z) metadata_set_z) (NExprConstFetch (NName (BYTES text_null) metadata_null) metadata_const) metadata_assign_z) metadata_statement_z)',
        '$base64(text_null) = $ptascii("null")',
        '$origin_node(S.SOURCES, porigin_echo_b) = (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_b) metadata_b])) metadata_echo_b)',
        '$base64(text_b) = $ptascii("B;")',
        f'prefreturncursor_chain* = {chain}',
        '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
        '$ref_replay_contexts(S, porigin_y) = [REPLAY_TRY porigin_first, REPLAY_TRY porigin_y_catch, REPLAY_TRY porigin_e_catch]',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps',
    ]
    capture = pre + globals + sites + [
        'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        'S_zfront = $drive_steps(S, 4)', 'S_zfront.COMPLETION = BUDGET',
        'S_zfront.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: ' + pre_tail,
        'S_zfront.ORIGIN = porigin_after_z?', 'S_zfront.EVENTS = S.EVENTS',
        'S_zfront.STORE = S.STORE', '$reference_notice_count(S_zfront.TODO) = 0',
    ]
    pending1 = 'REF_RETURN_CHAIN_PENDING ([prefreturncursor_z]) ([prefreturncursor_w, prefreturncursor_o]) porigin_y z_y'
    pending2 = 'REF_RETURN_CHAIN_PENDING ([prefreturncursor_z, prefreturncursor_w]) ([prefreturncursor_o]) porigin_y z_y'
    p1 = ('[RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, '
        'FINALLY_REF_RETURN porigin_w_owner porigin_w (REFERENCE n_w) z_w, '
        'FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, '
        'TRY_END porigin_e_catch, ORIGIN_RETURN porigin_e_restore?, AT porigin_echo_b (STMT statement_echo_b), '
        'FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, '
        'FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?, TYPE_FALLTHROUGH porigin_function, '
        + pending1 + ', REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]')
    capture += ['S_p1 = $drive_steps(S_zfront[.COMPLETION = NORMAL], 1)',
                'S_p1.COMPLETION = BUDGET', 'S_p1.TODO = ' + p1,
                'S_p1.ORIGIN = porigin_z_restore?', f'$task_nodes({pending1}) = eps']
    capture += roots('S_p1', ('w',)) + public('S_p1', 'p1')
    passage = ['TRY_END porigin_e_catch', 'ORIGIN_RETURN porigin_e_restore?', 'AT porigin_echo_b (STMT statement_echo_b)']
    base = ('[FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, '
        'FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?, TYPE_FALLTHROUGH porigin_function, '
        + pending2 + ', REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]')
    previous = 'S_p1'
    for count in (3, 2, 1, 0):
        state = 'S_p' + str(count) + '_e'
        suffix = '[' + ', '.join(passage[3-count:]) + ']' if count else 'eps'
        capture += [state + ' = $drive_steps(' + previous + '[.COMPLETION = NORMAL], 1)',
            state + '.COMPLETION = BUDGET',
            state + '.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y] ++ ' + suffix + ' ++ ' + base,
            state + '.ORIGIN = ' + ('(porigin_e_catch)' if count >= 2 else 'porigin_e_restore?'),
            '$ref_chain_pending_valid(' + state + ', [prefreturncursor_z, prefreturncursor_w], [prefreturncursor_o], porigin_y, z_y)',
            '$reference_notice_count(' + state + '.TODO) = 0',
            state + '.STORE = S.STORE', state + '.EVENTS = S.EVENTS']
        capture += public(state, 'e' + str(count))
        previous = state
    capture += ['S_full = $drive_steps(S_p0_e[.COMPLETION = NORMAL], 1)',
        'S_full.COMPLETION = BUDGET',
        'S_full.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH porigin_function, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'S_full.ORIGIN = (porigin_function)', '$task_nodes(REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y) = eps']
    capture += roots('S_full') + public('S_full', 'full')
    for state, retired in (('S_zfront', ()), ('S_p1', ('z',)), ('S_p3_e', ('z', 'w')), ('S_full', ('z', 'w'))):
        for name in ('w', 'z'):
            capture += [f'$heap_owners($heap_graph({state}), HCELL n_{name}) = ' + ('2' if name in retired else '3')]
        capture += [f'$heap_owners($heap_graph({state}), HCELL n_x) = 2',
                    f'$reference_notice_count({state}.TODO) = 0']
    literal_start = ['$af_function(S, $ptascii("f"))',
        'S.TODO = (RETURN_REF_VALUE z_o) :: ptask_literal_tail*', 'S.ORIGIN = (porigin_o)',
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
        'S_capture = $af_find(S_literal, 2000, 1)', '$af_stage(S_capture, 1)',
    ]
    import re
    literal_checks += [re.sub(r'\bS\b', 'S_capture', condition) for condition in pre]
    literal_checks += ['$reference_notice_count(S_capture.TODO) = 0',
                       '$ma_diagnostics(S_capture.EVENTS) = 0',
                       '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps']
    fixture('initial-literal-value-notice-and-cancellation', primary,
            {0: literal_start, 1: pre}, literal_checks)
    fixture('first-y-capture-and-authenticated-e-passage', primary, {0: pre}, capture, bad=[
        f'S_p1[.TODO = $af_replace(S_p1.TODO, {pending1}, [{pending1}, {pending1}])]',
        'S_p3_e[.TODO = $af_replace(S_p3_e.TODO, TRY_END porigin_e_catch, [TRY_END porigin_y_catch])]',
        'S_p2_e[.TODO = $af_replace(S_p2_e.TODO, ORIGIN_RETURN porigin_e_restore?, eps)]',
        'S_p2_e[.ORIGIN = (porigin_function)]',
        'S_full[.TODO = S_full.TODO ++ [REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE]]',
    ])

    complete = ['$af_function(S, $ptascii("f"))',
        'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        f'prefreturncursor_chain* = {chain}']
    replay = complete + globals + cursor_fields + old_literal + [
        '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix) + ')',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        '$ref_replay_contexts(S, porigin_y) = prefowner*',
        'prefowner* = [REPLAY_TRY porigin_first, REPLAY_TRY porigin_y_catch, REPLAY_TRY porigin_e_catch]',
        'S_error = $drive_steps(S, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*]',
        '$throwable_live(S_error, n_error)', '$throwable_previous_id(S_error, n_error) = eps',
        '$throwable_field(S_error, n_error, "line") = PINT z_y',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$task_nodes(REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*) = [HCELL n_y]',
        '$reference_notice_count(S_error.TODO) = 0',
    ] + roots('S_error') + public('S_error', 'yerror')
    replay += ['S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)',
        'S_expanded.COMPLETION = BUDGET',
        'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_chain_consumed_tasks(prefreturncursor_chain*))',
        'S_expanded.ORIGIN = (porigin_first)',
        '$ref_chain_consumed_tail(S_expanded.TODO) = $ref_chain_consumed_body(prefreturncursor_chain*)',
        '$reference_notice_count(S_expanded.TODO) = 0',
    ] + roots('S_expanded') + public('S_expanded', 'yexpanded')
    fixture('y-error-expanded-mixed-history', primary, {0: complete}, replay, bad=[
        'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y ([REPLAY_TRY porigin_first]) prefreturncursor_chain*]]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, ORIGIN_RETURN porigin_w_restore?, eps)]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, FINALLY_REF_CHAIN ([prefreturncursor_o]), [FINALLY_REF_CHAIN ([prefreturncursor_o[.SOURCE = porigin_z]])])]',
    ])

    body = ('[FINALLY_REF_CHAIN prefreturncursor_chain*, FINALLY_PHASE porigin_z_owner 3, '
        'ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CHAIN ([prefreturncursor_w, prefreturncursor_o]), '
        'FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, '
        'FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]')
    caught = ['$af_function(S, $ptascii("f"))', 'S.TODO = ' + body,
        f'prefreturncursor_chain* = {chain}',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(caught_prefix) + ')']

    def error(state, object_name, message, line='4'):
        return [f'$throwable_live({state}, {object_name})',
            f'$throwable_previous_id({state}, {object_name}) = eps',
            f'$throwable_field({state}, {object_name}, "line") = PINT {line}',
            f'$string_bytes($throwable_field({state}, {object_name}, "message")) = ($ptascii(' + json.dumps(message) + '))']

    def caught_store(state):
        return [f'{state}.STORE[n_z] = DEFINED PNULL',
            f'{state}.STORE[n_y] = DEFINED pvalue_fixed',
            '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
            f'$lookup({state}.ENV, $ptascii("e")) = (n_e)',
            f'{state}.STORE[n_e] = DEFINED (POBJECT n_old)'] + error(state, 'n_old', 'f(): Return value must be of type string, stdClass returned')

    before_clear = caught + globals + cursor_fields + old_literal + caught_store('S') + [
        '$ref_chain_links(S, prefreturncursor_chain*)', '$ref_chain_cleared_site(S, prefreturncursor_chain*)',
        '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0',
        'S.ORIGIN = $origin_child((porigin_z_owner), [PCFIELD 2])',
        'porigin_w_restore? = (porigin_e_catch)',
    ]
    cleared = ['S_cleared = $drive_steps(S, 1)', 'S_cleared.COMPLETION = BUDGET',
        'S_cleared.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z, REF_RETURN_CHAIN_CLEARED prefreturncursor_chain*, REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z]',
        'S_cleared.ORIGIN = porigin_o_restore?', '$ref_chain_cleared_valid(S_cleared, prefreturncursor_chain*)',
        '$tasks_nodes(S_cleared.TODO) = eps', '$reference_notice_count(S_cleared.TODO) = 0',
        'S_cleared.RESULT = KNOWN PNULL', 'S_cleared.BASE = BASE_VALUE (KNOWN PNULL)']
    for field in ('STORE', 'OBJECTS', 'EVENTS', 'FRAMES', 'CURRENT', 'HELD', 'RETIREDOWNERS'):
        cleared += [f'S_cleared.{field} = S.{field}']
    cleared += public('S_cleared', 'cleared')
    fresh = ['S_error = $drive_steps(S_cleared[.COMPLETION = NORMAL], 1)',
        'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_new, REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* prefowner*]',
        'prefowner* = [REPLAY_TRY porigin_z_owner, REPLAY_TRY porigin_e_catch]',
        'n_new =/= n_old', 'S_error.STORE[n_e] = DEFINED (POBJECT n_old)',
        '$throwable_live(S_error, n_old)',
        '$ref_chain_cleared_replay_valid(S_error, prefreturncursor_chain*, prefowner*)',
        '$task_nodes(REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* prefowner*) = eps',
        'S_error.STORE = S.STORE', 'S_error.EVENTS = S.EVENTS',
    ] + error('S_error', 'n_new', 'f(): Return value must be of type string, null returned', 'z_z')
    fresh += roots('S_error') + public('S_error', 'zerror')
    fresh += ['S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)',
        'S_expanded.COMPLETION = BUDGET',
        f'S_expanded.TODO = (THROW_SEARCH n_new) :: ($ref_replay_tasks(porigin_z, z_z, prefowner*) ++ $ref_chain_consumed_tasks({wo}))',
        f'$ref_chain_consumed_tail(S_expanded.TODO) = $ref_chain_consumed_body({wo})',
        'S_expanded.ORIGIN = (porigin_z_owner)',
        'S_expanded.STORE[n_e] = DEFINED (POBJECT n_old)',
        '$reference_notice_count(S_expanded.TODO) = 0',
    ] + public('S_expanded', 'zexpanded')
    internal = ['S_internal = $finally_leave_ref_return(S, porigin_z_owner, porigin_z, KNOWN PNULL, z_z, true, (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: $ref_chain_consumed_body(' + wo + '))',
        f'S_internal.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z] ++ $ref_chain_consumed_body({wo}) ++ [REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z]',
        'S_internal.ORIGIN = porigin_z_restore?', 'S_internal.STORE = S.STORE', 'S_internal.EVENTS = S.EVENTS',
        '$tasks_nodes(S_internal.TODO) = eps', '~$call_descriptors_valid(S_internal)',
        '~$ref_chain_cleared_valid(S_internal, prefreturncursor_chain*)']
    fixture('caught-c-cleared-null-and-fresh-z', primary, {0: caught}, before_clear + cleared + fresh + internal, bad=[
        'S_error[.TODO = [THROW_SEARCH n_new, REF_REPLAY_CHAIN_CLEARED prefreturncursor_chain* ([REPLAY_TRY porigin_z_owner])]]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, ORIGIN_RETURN porigin_w_restore?, [ORIGIN_RETURN porigin_o_restore?])]',
    ])

    saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(saved_prefix) + ')',
        '$ref_chain_consumed_tail(pframe.TODO) = (FINALLY_REF_CHAIN prefreturncursor_tail*) :: ptask_chain_tail*',
        f'prefreturncursor_tail* = {wo}']
    restored = ['$af_function(S, $ptascii("f"))',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(saved_prefix) + ')',
        '$ref_chain_consumed_tail(S.TODO) =/= eps']
    saved_fields = []
    for name in ('w', 'o'):
        saved_fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER',
                        f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                        f'z_{name} = prefreturncursor_{name}.LINE',
                        f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    saved_checks = saved + globals + saved_fields + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
        '$af_function(S_scope, $ptascii("f"))', f'$ref_chain_links(S_scope, {wo})',
        f'$ref_chain_consumed_tail(pframe.TODO) = $ref_chain_consumed_body({wo})',
        '$ref_return_cursor_literal(S_scope, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_z_owner (n_new))',
        '$lookup(S_scope.ENV, $ptascii("e")) = (n_e)',
        'S_scope.STORE[n_e] = DEFINED (POBJECT n_old)', 'n_old =/= n_new',
    ] + error('S_scope', 'n_old', 'f(): Return value must be of type string, stdClass returned')
    saved_checks += error('S_scope', 'n_new', 'f(): Return value must be of type string, null returned') + [
        '$ref_consumed_pair_tail(pframe.TODO) = eps', '$reference_notice_count(pframe.TODO) = 0',
        '$call_tasks_valid(S_scope, pframe.TODO)', '$tc_markers(pframe.TODO) = 2',
        'S.CURRENT = (pcallcontext_ping)', 'pframe.ORIGIN = (porigin_ping)',
        'pcallcontext_ping.CALLSITE = pframe.ORIGIN',
        'porigin_z_final? = $origin_child((porigin_z_owner), [PCFIELD 2])',
        'porigin_ping_statement? = $origin_child(porigin_z_final?, [PCFIELD 0, PCINDEX 2])',
        'pframe.ORIGIN = $origin_child(porigin_ping_statement?, [PCFIELD 0])',
        '$origin_node(S.SOURCES, porigin_ping) = (NExprFuncCall (NName (BYTES text_ping) metadata_ping_name) (SEQUENCE eps) metadata_ping_call)',
        '$base64(text_ping) = $ptascii("ping")',
        '(ORIGIN_RETURN porigin_ping_statement?) <- pframe.TODO',
        '(ORIGIN_RETURN porigin_z_final?) <- pframe.TODO',
    ]
    for name in ('x', 'w', 'z', 'y'):
        saved_checks += [f'$lookup(S_scope.ENV, $ptascii("{name}")) = (n_{name})']
    for name in ('x', 'w', 'z'):
        saved_checks += [f'~((HCELL n_{name}) <- $tasks_nodes(pframe.TODO))',
                        f'$heap_owners($heap_graph(S), HCELL n_{name}) = 2']
    saved_checks += public('S', 'saved') + [
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN',
        'S_restored.CURRENT = pframe.CONTEXT', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))']
    fixture('saved-m2-fresh-z-and-w-literal-history', primary, {0: saved, 1: restored}, saved_checks, bad=[
        f'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CHAIN ({wo}), [FINALLY_REF_CHAIN ([prefreturncursor_w, prefreturncursor_o[.LINE = $(z_o + 1)]])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_RESUME porigin_z_owner (n_new), [FINALLY_RESUME porigin_z_owner eps])] :: pframe_tail*]',
    ])

    literal_stage = ['$af_function(S, $ptascii("f"))',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(literal_prefix) + ')',
        'S.TODO = [FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]']
    literal = literal_stage + globals + [
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o = prefreturncursor_o.SOURCE',
        'z_o = prefreturncursor_o.LINE', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        'porigin_o_restore? = (porigin_function)',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
        'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
        'porigin_o = PORIGIN n_unit pcpath_old', 'n_unit = 0', 'z_o = 4',
        '$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_old) metadata_old) metadata_return_o)',
        '$base64(text_old) = $ptascii("old")',
        'S.ORIGIN = $origin_child((porigin_o_owner), [PCFIELD 2])',
        'S.STORE[n_z] = DEFINED PNULL', 'S.STORE[n_y] = DEFINED pvalue_fixed',
        '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_new)',
        '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0',
        '$ma_diagnostics(S.EVENTS) = 0', '$tc_markers(S.TODO) = 1',
    ] + error('S', 'n_new', 'f(): Return value must be of type string, null returned')
    literal += ['S_resumed = $drive_steps(S, 1)', 'S_resumed.COMPLETION = BUDGET',
        'S_resumed.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_o true porigin_o, REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE, REF_RECHECK porigin_o porigin_o_owner (KNOWN pvalue_old) z_o]',
        'S_resumed.ORIGIN = porigin_o_restore?', '$reference_notice_count(S_resumed.TODO) = 1',
        '$tc_markers(S_resumed.TODO) = 0', '$tasks_nodes(S_resumed.TODO) = eps',
        'S_resumed.STORE = S.STORE', 'S_resumed.EVENTS = S.EVENTS',
    ] + public('S_resumed', 'literal')
    fixture('e-b-literal-resumption-notice-and-fresh-cell', primary, {0: literal_stage}, literal,
        bad=['S_resumed[.TODO = (REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) :: S_resumed.TODO]'],
        finish='S_resumed', budget=True, terminal=[
            '(DIAGNOSTIC "Notice" ($ptascii("Only variable references should be returned by reference")) z_o) <- S_whole.EVENTS',
            '$lookup(S_whole.ENV, $ptascii("r")) = (n_r)',
            'n_r =/= n_x', 'n_r =/= n_w', 'n_r =/= n_z', 'n_r =/= n_y',
            'S_whole.STORE[n_r] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
            'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
            'S_whole.STORE[n_z] = DEFINED PNULL', 'S_whole.STORE[n_y] = DEFINED pvalue_fixed'])

    success_stage = complete + ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix) + ')']
    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)',
        '$lookup(S.ENV, $ptascii("y")) = (n_r)',
        'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['$lookup(S.ENV, $ptascii("r")) = (n_r)',
        '$lookup(S.ENV, $ptascii("y")) = (n_r)',
        'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    success = success_stage + globals + cursor_fields + old_literal + [
        '$lookup(S.ENV, $ptascii("y")) = (n_y)',
        'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        '$task_nodes(REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y) = eps',
        'S_returned = $drive_steps(S, 1)', 'S_returned.COMPLETION = BUDGET',
        'S_returned.RESULT = REFERENCE n_y', 'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        '$tc_markers(S_returned.TODO) = 0', '$reference_notice_count(S_returned.TODO) = 0',
    ] + public('S_returned', 'selected')
    success += ['S_r = $af_find(S_returned, 2000, 1)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        'S_written = $af_find($drive_steps(S_r, 1), 2000, 2)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        '$tc_markers(S_written.TODO) = 0', '$reference_notice_count(S_written.TODO) = 0',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))']
    fixture('first-y-success-alias-and-history-retirement', success_id,
        {0: success_stage, 1: assigned, 2: written}, success, finish='S_written', terminal=[
            '$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)',
            'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
            'S_whole.STORE[n_z] = DEFINED pvalue_z', 'S_whole.STORE[n_y] = DEFINED pvalue_changed',
            '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    escape_prefix = saved_prefix + 'E;'
    escaping = ['$af_function(S, $ptascii("f"))',
        'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(escape_prefix) + ')',
        '$ref_chain_consumed_tail(S.TODO) =/= eps',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)']
    old_escape = ['$af_function(S, $ptascii("f"))',
        'S.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(escape_prefix) + ')']
    caller = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("e")) = (n_caller_e)',
        'S.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
        '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))']
    escape = escaping + globals + [
        '$ref_chain_consumed_tail(S.TODO) = [FINALLY_REF_CHAIN ([prefreturncursor_w, prefreturncursor_o]), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'porigin_w_owner = prefreturncursor_w.OWNER', 'porigin_w = prefreturncursor_w.SOURCE',
        'z_w = prefreturncursor_w.LINE', 'porigin_w_restore? = prefreturncursor_w.OUTER',
        '$origin_node(S.SOURCES, porigin_w) = (NStmtReturn (NExprVariable (BYTES text_w) metadata_w) metadata_return_w)',
        '$base64(text_w) = $ptascii("w")', 'z_w = 4',
        '$lookup(S.ENV, $ptascii("w")) = (n_w)',
        '$ref_chain_catch_passage(S, [prefreturncursor_w, prefreturncursor_o]) = ([TRY_END porigin_e_catch, ORIGIN_RETURN porigin_e_restore?, AT porigin_echo_b (STMT statement_echo_b)])',
        'porigin_w_restore? = (porigin_e_catch)',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o = prefreturncursor_o.SOURCE',
        'z_o = prefreturncursor_o.LINE', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        'porigin_o_restore? = $ref_chain_function(S)',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        'S.STORE[n_z] = DEFINED PNULL', 'S.STORE[n_y] = DEFINED pvalue_fixed',
        '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
    ] + error('S', 'n_error', 'f(): Return value must be of type string, null returned')
    escape += ['S_old = $af_find(S, 2000, 1)', '$af_stage(S_old, 1)',
        'S_old.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'S_old.ORIGIN = porigin_w_restore?',
        '$reference_notice_count(S_old.TODO) = 0',
        'S_admitted_old = $drive(S_old[.COMPLETION = NORMAL], 0)',
        'S_admitted_old.COMPLETION = BUDGET', 'S_admitted_old.TODO = S_old.TODO',
        '$heap_valid($heap_graph(S_admitted_old))',
        'S_exit = $drive_steps(S_old, 1)', 'S_exit.COMPLETION = BUDGET',
        'S_exit.TODO = [THROW_SEARCH n_error]', 'S_exit.ORIGIN = porigin_o_restore?',
        '$tc_markers(S_exit.TODO) = 0', '$reference_notice_count(S_exit.TODO) = 0',
        'S_exit.STORE = S_old.STORE', 'S_exit.EVENTS = S_old.EVENTS',
    ] + public('S_exit', 'escaped')
    escape += ['S_caller = $af_find(S_exit, 2000, 2)',
        '$lookup(S_caller.ENV, $ptascii("e")) = (n_caller_e)',
        'S_caller.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
        '$throwable_live(S_caller, n_error)', '$lookup(S_caller.ENV, $ptascii("r")) = eps']
    fixture('e-rethrow-preserves-fresh-z-error-and-retires-literal', rethrow_id,
        {0: escaping, 1: old_escape, 2: caller}, escape, bad=[
            'S_old[.ORIGIN = porigin_o_restore?]',
            'S_old[.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ([prefreturncursor_o]), FINALLY_PHASE porigin_o_owner 3]]',
            'S_old[.TODO = $ref_chain_consumed_body([prefreturncursor_o])]',
        ], finish='S_caller', terminal=[
            '$lookup(S_whole.ENV, $ptascii("r")) = eps',
            'S_whole.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
            'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
            'S_whole.STORE[n_z] = DEFINED PNULL', 'S_whole.STORE[n_y] = DEFINED pvalue_fixed'])

    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path),
                                   'revision': report['revision']}],
        'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)),
        'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
        'public_refusals': sum(row['public_refusals'] for row in records), 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
