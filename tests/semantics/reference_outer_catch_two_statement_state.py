"""Emit source-reached checked catch-call passage and literal-resumption fixtures."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_multiple_active_cv_caught_state import PREFIX, sha
from request_environment_state import request_fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_outer_catch_two_statement_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['pins'] == report['pins_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == cases.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, case_id, stages, checks, bad=(), terminal=(), budget=False, finish=True, continuation="S"):
        row, case = rows[case_id], cases[case_id]
        assert row['pass'] and row['model']['status'] == 'normal'
        assert all(row['native'][key] == row['model'][key] for key in ('stdout', 'stderr', 'exit_status'))
        directory = args.raw / case_id
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode()).read_bytes()
        assert source == case['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        assert base64.b64decode(row['native']['stdout']) == case['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == case['stderr'].encode()
        assert row['native']['exit_status'] == case['exit'] == 0
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        state = json.loads((directory / 'state.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture'] and state['ok']
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
        if not finish:
            pass
        elif budget:
            assertions += ['S_continue = ' + continuation + '[.COMPLETION = NORMAL]',
                           'S_zero = $drive(S_continue, 0)', 'S_zero.COMPLETION = BUDGET',
                           'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
                           'S_frontier = $drive(S_continue, 10001)', 'S_whole = S_frontier',
                           'S_adjacent = S_frontier']
        else:
            assertions += ['S_whole = $drive(' + continuation + ', 10001)']
        if finish:
            assertions += ['S_whole.COMPLETION = NORMAL',
                       '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(case['stdout']) + ')',
                       '$ma_diagnostics(S_whole.EVENTS) = ' + str(int(bool(case['stderr']))), 'S_whole.CURRENT = eps',
                       'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.HELD = eps',
                       'S_whole.RETIREDOWNERS = eps', '$mc_count(S_whole.TODO) = 0',
                       '$reference_notice_count(S_whole.TODO) = 0',
                       '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case_id, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions),
                        'public_refusals': len(bad)})

    primary = 'outer-catch-call-literal-resumption'
    prefix = 'O;P;M1;P;I1;P;'
    pre = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (TRY_END porigin_y_catch) :: (ORIGIN_RETURN porigin_y_restore?) :: (AT porigin_set_z (STMT statement_set_z)) :: (ORIGIN_RETURN porigin_after_z?) :: (FINALLY_REF_RETURN porigin_z_owner porigin_z (REFERENCE n_z) z_z) :: (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: (TRY_END porigin_d_catch) :: (ORIGIN_RETURN porigin_d_restore?) :: (AT porigin_ping (STMT statement_ping)) :: (AT porigin_echo_b (STMT statement_echo_b)) :: (FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: (TYPE_FALLTHROUGH porigin_function) :: (REF_RECHECK porigin_y porigin_y_first (REFERENCE n_y) z_y) :: eps']
    bindings = [
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix) + ')',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', '$lookup(S.ENV, $ptascii("z")) = (n_z)', 'n_y =/= n_z',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)', 'S.STORE[n_z] = DEFINED pvalue_z',
        '$string_bytes(pvalue_z) = ($ptascii("mid"))',
        '$origin_node(S.SOURCES, porigin_y) = (NStmtReturn (NExprVariable (BYTES text_y) metadata_y) metadata_return_y)',
        '$base64(text_y) = $ptascii("y")',
        '$origin_node(S.SOURCES, porigin_z) = (NStmtReturn (NExprVariable (BYTES text_z) metadata_z) metadata_return_z)',
        '$base64(text_z) = $ptascii("z")',
        '$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_old) metadata_old) metadata_return_o)',
        '$origin_node(S.SOURCES, porigin_ping) = (NStmtExpression (NExprFuncCall (NName (BYTES text_ping) metadata_name_ping) (SEQUENCE eps) metadata_call_ping) metadata_statement_ping)',
        '$base64(text_ping) = $ptascii("ping")',
        '$base64(text_old) = $ptascii("old")', 'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
        'prefreturncursor_z = { OWNER porigin_z_owner, SOURCE porigin_z, LINE z_z, OUTER porigin_z_restore? }',
        'prefreturncursor_o = { OWNER porigin_o_owner, SOURCE porigin_o, LINE z_o, OUTER porigin_o_restore? }',
        'porigin_z_restore? = (porigin_d_catch)', 'porigin_o_restore? = (porigin_function)',
        'porigin_d_restore? = $origin_child((porigin_o_owner), [PCFIELD 2])',
        '$throwable_try_valid(S, porigin_d_catch)', '~$finally_present(S, porigin_d_catch)',
        '$throwable_try_valid(S, porigin_y_catch)', '~$finally_present(S, porigin_y_catch)',
        '$ref_return_pair_site(S, prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
        '$ref_return_pair_catch_passage(S, prefreturncursor_z, prefreturncursor_o) = ([TRY_END porigin_d_catch, ORIGIN_RETURN porigin_d_restore?, AT porigin_ping (STMT statement_ping), AT porigin_echo_b (STMT statement_echo_b)])',
        '$ref_replay_contexts(S, porigin_y) = [REPLAY_TRY porigin_y_first, REPLAY_TRY porigin_y_catch, REPLAY_TRY porigin_d_catch]',
        '$ref_replay_contexts(S, porigin_z) = [REPLAY_TRY porigin_z_owner, REPLAY_TRY porigin_d_catch]',
        '$ref_replay_owners(S, porigin_y) = porigin_y_first :: eps',
        '$ref_replay_owners(S, porigin_z) = porigin_z_owner :: eps',
        '$operand_nodes(KNOWN pvalue_old) = eps',
        '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps',
        '$reference_notice_count(S.TODO) = 0', 'z_y = 4', 'z_z = 4', 'z_o = 4',
        'S_zfront = $drive_steps(S, 4)', 'S_zfront.COMPLETION = BUDGET',
        'S_zfront.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, FINALLY_REF_RETURN porigin_z_owner porigin_z (REFERENCE n_z) z_z, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, TRY_END porigin_d_catch, ORIGIN_RETURN porigin_d_restore?, AT porigin_ping (STMT statement_ping), AT porigin_echo_b (STMT statement_echo_b), FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?, TYPE_FALLTHROUGH porigin_function, REF_RECHECK porigin_y porigin_y_first (REFERENCE n_y) z_y]',
        'S_zfront.ORIGIN = porigin_after_z?', 'S_zfront.STORE = S.STORE', 'S_zfront.EVENTS = S.EVENTS',
        '$call_descriptors_valid(S_zfront)', '$heap_valid($heap_graph(S_zfront))',
        'ptask_base* = [FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?, TYPE_FALLTHROUGH porigin_function, REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_o porigin_y z_y, REF_RECHECK porigin_y porigin_y_first (REFERENCE n_y) z_y]',
    ]
    passage = ['TRY_END porigin_d_catch', 'ORIGIN_RETURN porigin_d_restore?', 'AT porigin_ping (STMT statement_ping)', 'AT porigin_echo_b (STMT statement_echo_b)']
    last = 'S_zfront'
    for count in (4, 3, 2, 1, 0):
        current = 'S_p' + str(count)
        remaining = '[' + ', '.join(passage[4-count:]) + ']' if count else 'eps'
        bindings += [current + ' = $drive_steps(' + last + '[.COMPLETION = NORMAL], 1)',
                     current + '.COMPLETION = BUDGET',
                     current + '.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y] ++ ' + remaining + ' ++ ptask_base*',
                     current + '.ORIGIN = ' + ('(porigin_d_catch)' if count >= 3 else 'porigin_d_restore?'),
                     current + '.STORE = S.STORE', current + '.EVENTS = S.EVENTS', current + '.FRAMES = S.FRAMES',
                     '$reference_notice_count(' + current + '.TODO) = 0',
                     '$ref_return_pair_pending_valid(' + current + ', prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
                     current + '_public = $drive(' + current + '[.COMPLETION = NORMAL], 0)',
                     current + '_public.COMPLETION = BUDGET',
                     current + '_public.TODO = ' + current + '.TODO',
                     current + '_public.ORIGIN = ' + current + '.ORIGIN',
                     '$heap_valid($heap_graph(' + current + '))']
        last = current
    bindings += [
        '$task_nodes(REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_o porigin_y z_y) = eps',
        '~((HCELL n_z) <- $tasks_nodes(S_p4.TODO))',
        '$heap_owners($heap_graph(S_zfront), HCELL n_z) = $($heap_owners($heap_graph(S_p4), HCELL n_z) + 1)',
        'S_pair = $drive_steps(S_p0[.COMPLETION = NORMAL], 1)', 'S_pair.COMPLETION = BUDGET',
        'S_pair.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH porigin_function, REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y, REF_RECHECK porigin_y porigin_y_first (REFERENCE n_y) z_y]',
        '$ref_return_pair_valid(S_pair, prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
        '$call_descriptors_valid(S_pair)', '$heap_valid($heap_graph(S_pair))',
    ]
    fixture('catch-call-capture-pending-scopes', primary, {0:pre}, pre + bindings, bad=[
        'S_p4[.TODO = $af_replace(S_p4.TODO, AT porigin_ping (STMT statement_ping), eps)]',
        'S_p3[.TODO = $af_replace(S_p3.TODO, ORIGIN_RETURN porigin_d_restore?, eps)]',
        'S_p2[.TODO = $af_replace(S_p2.TODO, AT porigin_ping (STMT statement_ping), [AT porigin_echo_b (STMT statement_ping)])]',
        'S_p2[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, AT porigin_echo_b (STMT statement_echo_b), AT porigin_ping (STMT statement_ping)] ++ ptask_base*]',
        'S_p3[.ORIGIN = prefreturncursor_o.OUTER]',
    ], finish=False)
    pair = ['$af_function(S, $ptascii("f"))',
            'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y, REF_RECHECK porigin_y porigin_y_first (REFERENCE n_y) z_y]',
            '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix) + ')']
    error_bindings = pair[1:] + [
        'porigin_z = prefreturncursor_z.SOURCE',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$ref_return_pair_valid(S, prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
        '$ref_replay_contexts(S, porigin_y) = prefowner*',
        'prefowner* = [REPLAY_TRY porigin_y_first, REPLAY_TRY porigin_y_catch, REPLAY_TRY porigin_d_catch]',
        'prefreturncursor_z.OUTER = (porigin_d_catch)',
        '$reference_notice_count(S.TODO) = 0',
        'S_error = $drive_steps(S, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_TWO porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_z prefreturncursor_o]',
        'prefowner* = [REPLAY_TRY porigin_y_first, REPLAY_TRY porigin_y_catch, REPLAY_TRY porigin_d_catch]',
        '$throwable_live(S_error, n_error)', '$throwable_previous_id(S_error, n_error) = eps',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$ref_replay_two_valid(S_error, porigin_y, REFERENCE n_y, z_y, prefowner*, prefreturncursor_z, prefreturncursor_o)',
        '$reference_notice_count(S_error.TODO) = 0', '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
        'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_consumed_pair_tasks(prefreturncursor_z, prefreturncursor_o))',
        '$reference_notice_count(S_expanded.TODO) = 0', '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))',
        'S_public = $drive(S_expanded[.COMPLETION = NORMAL], 0)', 'S_public.COMPLETION = BUDGET',
        'S_public.TODO = S_expanded.TODO', '$call_descriptors_valid(S_public)', '$heap_valid($heap_graph(S_public))']
    fixture('catch-call-y-error-public-expanded', primary, {0:pair}, error_bindings, bad=[
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, ORIGIN_RETURN prefreturncursor_z.OUTER, eps)]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, FINALLY_REF_CONSUMED prefreturncursor_o, [FINALLY_REF_CONSUMED (prefreturncursor_o[.LINE = $(prefreturncursor_o.LINE + 1)])])]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, FINALLY_REF_CONSUMED prefreturncursor_o, [FINALLY_REF_CONSUMED (prefreturncursor_o[.SOURCE = porigin_z])])]',
        'S_expanded[.TODO = $af_replace(S_expanded.TODO, FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o, eps)]',
    ], finish=False)
    caught_prefix = 'O;P;M1;P;I1;P;I2;P;C;'
    literal_prefix = caught_prefix + 'M2;P;D;P;B;'
    caught = ['$af_function(S, $ptascii("f"))',
              'S.TODO = (FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o) :: ptask_tail*',
              '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(caught_prefix) + ')']
    globals = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
               '$lookup(psymboltable.ENV, $ptascii("z")) = (n_z)', '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)',
               'n_x =/= n_z', 'n_x =/= n_y', 'n_z =/= n_y',
               'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
               'S.STORE[n_z] = DEFINED PNULL', 'S.STORE[n_y] = DEFINED pvalue_y',
               '$string_bytes(pvalue_y) = ($ptascii("fixed"))']
    literal_stage = ['$af_function(S, $ptascii("f"))',
                     '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(literal_prefix) + ')',
                     'S.TODO = (FINALLY_REF_CONSUMED prefreturncursor_o) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: eps']
    cleared = caught[1:] + globals + [
        'S.TODO = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o, FINALLY_PHASE prefreturncursor_z.OWNER 3, ORIGIN_RETURN prefreturncursor_z.OUTER, FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE prefreturncursor_o.OWNER 3, ORIGIN_RETURN prefreturncursor_o.OUTER]',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_old)',
        '$throwable_live(S, n_old)', '$throwable_previous_id(S, n_old) = eps',
        '$string_bytes($throwable_field(S, n_old, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        'porigin_z_owner = prefreturncursor_z.OWNER', 'porigin_z = prefreturncursor_z.SOURCE',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o = prefreturncursor_o.SOURCE',
        'porigin_o_restore? = prefreturncursor_o.OUTER',
        'prefreturncursor_z.OUTER = (porigin_d_catch)',
        '$ref_return_pair_cleared_site(S, prefreturncursor_z, prefreturncursor_o)',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0',
        'S_cleared = $drive_steps(S, 1)', 'S_cleared.COMPLETION = BUDGET',
        'S_cleared.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) prefreturncursor_z.LINE true porigin_z, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_o, REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) prefreturncursor_z.LINE]',
        '$ref_return_pair_cleared_valid(S_cleared, prefreturncursor_z, prefreturncursor_o)',
        'S_cleared.STORE = S.STORE', 'S_cleared.EVENTS = S.EVENTS', 'S_cleared.FRAMES = S.FRAMES',
        '$tasks_nodes(S_cleared.TODO) = eps', '$reference_notice_count(S_cleared.TODO) = 0',
        '$call_descriptors_valid(S_cleared)', '$heap_valid($heap_graph(S_cleared))',
        'S_zerror = $drive_steps(S_cleared[.COMPLETION = NORMAL], 1)', 'S_zerror.COMPLETION = BUDGET',
        'S_zerror.TODO = [THROW_SEARCH n_new, REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_o prefowner*]',
        'prefowner* = [REPLAY_TRY porigin_z_owner, REPLAY_TRY porigin_d_catch]',
        '$ref_replay_contexts(S_cleared, porigin_z) = prefowner*',
        'n_new =/= n_old', '$throwable_live(S_zerror, n_new)', '$throwable_live(S_zerror, n_old)',
        '$throwable_previous_id(S_zerror, n_new) = eps',
        '$string_bytes($throwable_field(S_zerror, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        '$throwable_field(S_zerror, n_new, "line") = PINT prefreturncursor_z.LINE',
        '$ref_replay_pair_cleared_valid(S_zerror, prefreturncursor_z, prefreturncursor_o, prefowner*)',
        '$task_nodes(REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_o prefowner*) = eps',
        '$reference_notice_count(S_zerror.TODO) = 0', '$call_descriptors_valid(S_zerror)', '$heap_valid($heap_graph(S_zerror))',
        'S_zexpanded = $drive_steps(S_zerror[.COMPLETION = NORMAL], 1)', 'S_zexpanded.COMPLETION = BUDGET',
        'S_zexpanded.TODO = (THROW_SEARCH n_new) :: ($ref_replay_tasks(porigin_z, prefreturncursor_z.LINE, prefowner*) ++ $ref_consumed_tasks(prefreturncursor_o))',
        '$call_descriptors_valid(S_zexpanded)', '$heap_valid($heap_graph(S_zexpanded))',
        'S_literal = $af_find(S_zexpanded, 2000, 1)', '$af_stage(S_literal, 1)',
        'S_literal.TODO = [FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        '$reference_notice_count(S_literal.TODO) = 0', '$ma_diagnostics(S_literal.EVENTS) = 0',
        '$tasks_nodes(S_literal.TODO) = eps',
        'S_literal.STORE[n_x] = DEFINED pvalue_x', 'S_literal.STORE[n_z] = DEFINED PNULL',
        'S_literal.STORE[n_y] = DEFINED pvalue_y',
        '$lookup(S_literal.ENV, $ptascii("e")) = (n_e_d)', 'S_literal.STORE[n_e_d] = DEFINED (POBJECT n_new)',
        '$ref_return_cursor_literal(S_literal, prefreturncursor_o) = (pvalue_old)',
        'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
        'prefreturncursor_o.SOURCE = PORIGIN n_unit pcpath_old', 'n_unit = 0', 'prefreturncursor_o.LINE = 4',
        '$call_descriptors_valid(S_literal)', '$heap_valid($heap_graph(S_literal))',
        'S_resumed = $drive_steps(S_literal, 1)', 'S_resumed.COMPLETION = BUDGET',
        'S_resumed.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) prefreturncursor_o.LINE true porigin_o, REF_RETURN_NOTICE porigin_o prefreturncursor_o.LINE REF_NOTICE_VALUE, REF_RECHECK porigin_o porigin_o_owner (KNOWN pvalue_old) prefreturncursor_o.LINE]',
        '$reference_notice_count(S_resumed.TODO) = 1', '$mc_count(S_resumed.TODO) = 0',
        'S_resumed.STORE = S_literal.STORE', 'S_resumed.EVENTS = S_literal.EVENTS',
        '$tasks_nodes(S_resumed.TODO) = eps', '$call_descriptors_valid(S_resumed)', '$heap_valid($heap_graph(S_resumed))',
    ]
    fixture('catch-passage-cleared-z-literal-resumption', primary, {0:caught,1:literal_stage}, cleared, bad=[
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_o, [REF_RETURN_PAIR_CLEARED prefreturncursor_z (prefreturncursor_o[.LINE = $(prefreturncursor_o.LINE + 1)])])]',
        'S_zerror[.TODO = $af_replace(S_zerror.TODO, REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_o prefowner*, [REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_o ([REPLAY_TRY porigin_z_owner])])]',
        'S_resumed[.TODO = (REF_RETURN_NOTICE porigin_o prefreturncursor_o.LINE REF_NOTICE_VALUE) :: S_resumed.TODO]',
    ], budget=True, continuation='S_resumed', terminal=[
        '(DIAGNOSTIC "Notice" ($ptascii("Only variable references should be returned by reference")) prefreturncursor_o.LINE) <- S_whole.EVENTS',
        '$lookup(S_whole.ENV, $ptascii("r")) = (n_r)', 'n_r =/= n_x', 'n_r =/= n_z', 'n_r =/= n_y',
        'S_whole.STORE[n_r] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED PNULL', 'S_whole.STORE[n_y] = DEFINED pvalue_y'])

    saved_prefix = caught_prefix + 'M2;P;'
    saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
             '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(saved_prefix) + ')',
             '$ref_consumed_tail(pframe.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]']
    restored = ['$af_function(S, $ptascii("f"))',
                '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(saved_prefix) + ')', '$ref_consumed_tail(S.TODO) =/= eps']
    fixture('catch-passage-saved-m2-literal-history', primary, {0:saved,1:restored}, saved[1:] + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        '$ref_return_cursor_literal(S_scope, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_z_owner (n_new))',
        '$lookup(S_scope.ENV, $ptascii("e")) = (n_e)', 'S_scope.STORE[n_e] = DEFINED (POBJECT n_old)',
        'n_old =/= n_new', '$throwable_live(S_scope, n_old)', '$throwable_live(S_scope, n_new)',
        '$throwable_previous_id(S_scope, n_new) = eps',
        '$string_bytes($throwable_field(S_scope, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        '$throwable_field(S_scope, n_new, "line") = PINT 4',
        '$ref_consumed_pair_tail(pframe.TODO) = eps', '$mc_count(pframe.TODO) = 1',
        '$reference_notice_count(pframe.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor_o) = eps', '$call_tasks_valid(S_scope, pframe.TODO)',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN',
        'S_restored.SOURCES = S.SOURCES', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        '$reference_notice_count(S_restored.TODO) = 0', '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor_o, [FINALLY_REF_CONSUMED (prefreturncursor_o[.LINE = $(prefreturncursor_o.LINE + 1)])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = pframe.TODO ++ [REF_RETURN_NOTICE prefreturncursor_o.SOURCE prefreturncursor_o.LINE REF_NOTICE_VALUE]] :: pframe_tail*]',
    ])
    rethrow = 'outer-catch-rethrows'
    escape = ['$af_function(S, $ptascii("f"))', 'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
              '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(saved_prefix) + ')',
              '$ref_consumed_tail(S.TODO) =/= eps',
              '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)']
    fixture('catch-passage-d-rethrow-retires-literal', rethrow, {0:escape}, escape[1:] + globals + [
        '$ref_consumed_tail(S.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$throwable_live(S, n_error)', '$throwable_previous_id(S, n_error) = eps',
        '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
    ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED PNULL',
                 'S_whole.STORE[n_y] = DEFINED pvalue_y', '$lookup(S_whole.ENV, $ptascii("r")) = eps'])

    success = 'inner-y-succeeds'
    success_pair = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y) :: (REF_RECHECK porigin_y porigin_y_first (REFERENCE n_y) z_y) :: eps']
    success_globals = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
                       '$lookup(psymboltable.ENV, $ptascii("z")) = (n_z)', '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)',
                       'n_x =/= n_z', 'n_x =/= n_y', 'n_z =/= n_y',
                       'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
                       'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))',
                       'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))']
    fixture('catch-passage-first-y-success-retires-literal', success,
            {0:success_pair + ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(prefix) + ')']}, success_pair + success_globals + [
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        '$task_nodes(REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y) = eps',
        'S_returned = $drive_steps(S, 1)', 'S_returned.RESULT = REFERENCE n_y',
        'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps', '$mc_count(S_returned.TODO) = 0',
        '$reference_notice_count(S_returned.TODO) = 0', '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)',
                 'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])
    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue': str(catalogue.resolve()), 'catalogue_sha256': sha(catalogue),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'scope': 'Genuine extra-call source capture/pending4-0/public scopes, separate Y error/public expanded, cleared Z catch/literal Notice/fresh cell, saved M2, new-layout success/error retirement; one late Notice-frontier budget equality. Throwing/reentrant calls and broad returns remain open.',
                'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(args.output, manifest['fixtures'], manifest['assertions'])


if __name__ == '__main__':
    main()
