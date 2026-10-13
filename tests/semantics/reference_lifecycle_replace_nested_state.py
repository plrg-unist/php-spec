"""Emit fresh caught-error replacement identity, trace and late cleanup proofs."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_three_active_cv_state import PREFIX, sha
from request_environment_state import request_fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_lifecycle_replace_nested_cases.json'
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

    def fixture(name, case_id, stages, checks, finish=None, budget=False):
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
                      '$af_stage(S, 0)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))'] + checks
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
                           'S_whole.DESTRUCTION.PHASE = DESTRUCTION_DONE',
                           'S_whole.DESTRUCTION.CALLS = eps', 'S_whole.DESTRUCTION.RELEASES = eps',
                           'S_whole.DESTRUCTION.OPERATIONS = eps',
                           '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))']
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case_id, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': int(case_id == 'destructor-y-replay')})

    def public(state, tag):
        admitted = 'S_admitted_' + tag
        return [f'{admitted} = $drive({state}[.COMPLETION = NORMAL], 0)',
                f'{admitted}.COMPLETION = BUDGET', f'{admitted}.TODO = {state}.TODO',
                f'$heap_valid($heap_graph({admitted}))']

    primary, selected = 'destructor-y-replay', 'destructor-y-selected'
    chain = '[prefreturncursor_z, prefreturncursor_w, prefreturncursor_x]'
    wx = '[prefreturncursor_w, prefreturncursor_x]'
    body = ('[FINALLY_REF_CHAIN prefreturncursor_chain*, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, '
            'FINALLY_REF_CHAIN (' + wx + '), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, '
            'FINALLY_REF_CHAIN ([prefreturncursor_x]), FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]')
    globals = ['S.GLOBALTABLE = (psymboltable)']
    for name in ('x', 'w', 'z', 'y', 'n'):
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
              'porigin_x_restore? = (porigin_function)', f'prefreturncursor_chain* = {chain}',
              '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
              '$destructor_operational(S)', '$ref_chain_lifecycle_safe(S, prefreturncursor_chain*)',
              '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
              '$lookup(S.ENV, $ptascii("n")) = (n_n)',
              '$ref_chain_reentrant_replace_class(S, prefreturncursor_chain*)']

    sites += ['S.CLASSES = pclassdesc :: eps', 'pclassdesc.METHODS = pmethoddesc :: eps',
        'pmethoddesc.NAME = $ptascii("__destruct")',
        '$origin_node(S.SOURCES, pmethoddesc.FUNCTION.ORIGIN) = (NStmtClassMethod phpType14 (INTEGER 1) (BOOLEAN false) (NIdentifier (BYTES text_method) metadata_method_name) (SEQUENCE eps) ABSENT (SEQUENCE ([statement_guard, statement_d])) metadata_method)',
        'statement_guard = NStmtIf (NExprBinaryOpIdentical (NExprArrayDimFetch (NExprVariable (BYTES text_globals_n) metadata_globals_n) (NScalarString (BYTES text_key_n) metadata_key_n) metadata_fetch_n) (NScalarInt (INTEGER 2) metadata_two) metadata_identical) (SEQUENCE ([statement_q, statement_try, statement_t])) (SEQUENCE eps) ABSENT metadata_guard',
        'statement_try = NStmtTryCatch (SEQUENCE ([statement_ref, statement_probe])) (SEQUENCE ([NStmtCatch (SEQUENCE ([NName (BYTES text_catch_type) metadata_catch_type])) (NExprVariable (BYTES text_catch_name) metadata_catch_name) (SEQUENCE ([statement_c, statement_replace])) metadata_catch])) ABSENT metadata_try',
        '$base64(text_catch_type) = $ptascii("TypeError")',
        '$base64(text_catch_name) = $ptascii("nested")', '~$environment_name($base64(text_catch_name))',
        'statement_c = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_prefix) metadata_prefix, NExprMethodCall (NExprVariable (BYTES text_receiver) metadata_receiver) (NIdentifier (BYTES text_getter) metadata_getter) (SEQUENCE eps) metadata_message_call, NScalarString (BYTES text_suffix) metadata_suffix])) metadata_catch_echo',
        '$base64(text_receiver) = $base64(text_catch_name)', '$base64(text_getter) = $ptascii("getMessage")',
        '$base64(text_prefix) = $ptascii("C:")', '$base64(text_suffix) = $ptascii(";")',
        'statement_replace = NStmtExpression (NExprThrow (NExprNew (NName (BYTES text_replace_type) metadata_replace_type) (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text_replace_message) metadata_replace_message) (BOOLEAN false) (BOOLEAN false) metadata_replace_arg])) metadata_replace_new) metadata_replace_throw) metadata_replace_statement',
        '$base64(text_replace_type) = $ptascii("TypeError")', '$base64(text_replace_message) = $ptascii("replacement")',
        '$origin_child((pmethoddesc.FUNCTION.ORIGIN), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 1, PCFIELD 1, PCINDEX 0, PCFIELD 2, PCINDEX 1, PCFIELD 0, PCFIELD 0]) = (porigin_replace_new)',
        'statement_ref = NStmtExpression (NExprAssignRef (NExprVariable (BYTES text_inner_ref) metadata_inner_ref) (NExprFuncCall (NName (BYTES text_call) metadata_call_name) (SEQUENCE eps) metadata_call) metadata_assign_ref) metadata_ref_statement',
        'statement_probe = NStmtExpression (NExprAssign (NExprVariable (BYTES text_inner_write) metadata_inner_write) (NScalarString (BYTES text_probe) metadata_probe) metadata_assign_write) metadata_write_statement',
        '$base64(text_inner_ref) = $ptascii("inner")', '$base64(text_inner_write) = $base64(text_inner_ref)',
        '~$environment_name($base64(text_inner_ref))', '$base64(text_probe) = $ptascii("probe")',
        '$base64(text_globals_n) = $ptascii("GLOBALS")', '$base64(text_key_n) = $ptascii("n")',
        '$base64(text_call) = $ptascii("f")',
        '$origin_child((pmethoddesc.FUNCTION.ORIGIN), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 1, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 1]) = (porigin_call)',
        '$call_selected_valid(S, porigin_function, (porigin_call))',
        '$origin_child((pmethoddesc.FUNCTION.ORIGIN), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 2]) = (porigin_t)',
        '$origin_node(S.SOURCES, porigin_t) = (statement_t)',
        'statement_t = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_t) metadata_t])) metadata_echo_t',
        '$base64(text_t) = $ptascii("T;")',
        '$origin_child((pmethoddesc.FUNCTION.ORIGIN), [PCFIELD 6, PCINDEX 1]) = (porigin_d)',
        '$origin_node(S.SOURCES, porigin_d) = (statement_d)',
        'statement_d = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_d) metadata_d])) metadata_echo_d',
        '$base64(text_d) = $ptascii("D;")']
    nested_output = 'O;P;W;P;M;P;I1;P;I2;P;Q;O;P;W;P;M;P;I3;P;'
    completed_catch_output = nested_output + 'C:nested;'
    caller_prefix = completed_catch_output + 'R:replacement;'
    replacing = ['S.CURRENT = (pcallcontext_dtor)',
        'pcallcontext_dtor.TARGET = METHOD_TARGET n_y_object porigin_method',
        '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc_dtor)',
        'pmethoddesc_dtor.NAME = $ptascii("__destruct")',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(completed_catch_output) + ')',
        'S.TODO = (THROW_SEARCH n_pending_error) :: ptask_tail*',
        '$lookup(S.ENV, $ptascii("inner")) = eps',
        '$lookup(S.ENV, $ptascii("nested")) = (n_caught_cell)',
        'S.STORE[n_caught_cell] = DEFINED (POBJECT n_caught_error)',
        'S.GLOBALTABLE = (psymboltable_catch)',
        '$lookup(psymboltable_catch.ENV, $ptascii("y")) = (n_y)',
        'S.STORE[n_y] = DEFINED pvalue_fixed',
        '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))']
    escaping = ['S.TODO = [THROW_SEARCH n_error, ' + body[1:-1] + ']',
        f'prefreturncursor_chain* = {chain}',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(completed_catch_output) + ')']
    caught = ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(caller_prefix) + ')',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)',
        'S.CURRENT = eps', 'S.FRAMES = eps']
    error = ['S.TODO = [THROW_SEARCH n_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*]']
    reentry = pre + globals + sites + [
        'S.STORE[n_n] = DEFINED (PINT 1)', 'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        '~$ref_chain_reentrant_caught_class(S, prefreturncursor_chain*)',
        'S_old = $af_find(S, 2000, 3)', 'S_old.COMPLETION = NORMAL',
        '$ref_replay_contexts(S_old, porigin_y) = prefowner*', 'prefowner* = [REPLAY_TRY porigin_first]',
        'S_old.TODO = [THROW_SEARCH n_old, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*]',
        '$throwable_live(S_old, n_old)', 'S_old.OBJECTS[n_old] = THROWABLE pthrowable_old',
        'pthrowable_old.KIND = "TypeError"', '$throwable_previous_id(S_old, n_old) = eps',
        '$throwable_field(S_old, n_old, "line") = PINT z_y',
        '$string_bytes($throwable_field(S_old, n_old, "message")) = ($ptascii("f(): Return value must be of type string, SelectedY returned"))',
        'S_old.STORE[n_y] = DEFINED (POBJECT n_y_object)', 'S_old.EVENTS = S.EVENTS',
        'S_replace = $af_find(S_old, 2000, 4)', 'S_replace.COMPLETION = NORMAL',
        'S_replace.CURRENT = (pcallcontext_dtor)',
        'pcallcontext_dtor.TARGET = METHOD_TARGET n_y_object pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_dtor.RECEIVER = (n_y_object)',
        'S_replace.FRAMES = pframe_f :: pframe_main :: eps',
        'pframe_f.CONTEXT = (pcallcontext_f)', 'pcallcontext_f.FUNCTION = porigin_function',
        '(FINALLY_RESUME porigin_first (n_old)) <- pframe_f.TODO',
        'S_replace.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        '$lookup(S_replace.ENV, $ptascii("inner")) = eps',
        '$lookup(S_replace.ENV, $ptascii("nested")) = (n_caught_cell)',
        'S_replace.STORE[n_caught_cell] = DEFINED (POBJECT n_nested_error)',
        r'n_error =/= n_old /\ n_error =/= n_nested_error /\ n_nested_error =/= n_old',
        'S_replace.OBJECTS[n_nested_error] = THROWABLE pthrowable_nested', '$throwable_live(S_replace, n_nested_error)',
        'pthrowable_nested.KIND = "TypeError"', '$throwable_previous_id(S_replace, n_nested_error) = eps',
        '$throwable_field(S_replace, n_nested_error, "line") = PINT 4',
        '$string_bytes($throwable_field(S_replace, n_nested_error, "message")) = ($ptascii("nested"))',
        'pthrowable_nested.ORIGIN = (porigin_nested_new)',
        '$origin_node(S_replace.SOURCES, porigin_nested_new) = (NExprNew (NName (BYTES text_nested_type) metadata_nested_type) (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text_nested_message) metadata_nested_message) (BOOLEAN false) (BOOLEAN false) metadata_nested_arg])) metadata_nested_new)',
        '$base64(text_nested_type) = $ptascii("TypeError")', '$base64(text_nested_message) = $ptascii("nested")',
        '$throwable_field(S_replace, n_nested_error, "trace") = PARRAY n_nested_trace', '$trace_graph_valid(S_replace, n_nested_trace)',
        'S_replace.GLOBALTABLE = (psymboltable_replace)',
        '$lookup(psymboltable_replace.ENV, $ptascii("n")) = (n_n)',
        '$lookup(psymboltable_replace.ENV, $ptascii("y")) = (n_y)',
        'S_replace.STORE[n_n] = DEFINED (PINT 3)',
        'S_replace.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        'S_replace.OBJECTS[n_old] = THROWABLE pthrowable_old', '$throwable_live(S_replace, n_old)',
        'S_replace.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "TypeError"', '$throwable_live(S_replace, n_error)',
        '$throwable_previous_id(S_replace, n_error) = eps',
        '$throwable_field(S_replace, n_error, "line") = PINT 3',
        '$string_bytes($throwable_field(S_replace, n_error, "message")) = ($ptascii("replacement"))',
        'pthrowable_error.ORIGIN = (porigin_replace_new)',
        '$origin_node(S_replace.SOURCES, porigin_replace_new) = (NExprNew (NName (BYTES text_replace_type) metadata_replace_type) (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text_replace_message) metadata_replace_message) (BOOLEAN false) (BOOLEAN false) metadata_replace_arg])) metadata_replace_new)',
        '$throwable_previous_id(S_replace, n_old) = eps',
        '$throwable_field(S_replace, n_error, "trace") = PARRAY n_trace',
        'n_trace =/= n_nested_trace',
        '$trace_graph_valid(S_replace, n_trace)',
        'pnode_trace* = $heap_reach([HARRAY n_trace], eps, $heap_graph(S_replace).EDGES)',
        'pnode_trace* = (HARRAY n_trace_part)*',
        'n_y_object <- S_replace.DESTRUCTION.CALLED', '(HOBJECT n_y_object) <- S_replace.ALLOCATIONS',
        '$reference_notice_count(S_replace.TODO) = 0', '$ma_diagnostics(S_replace.EVENTS) = 0']
    for name in ('x', 'w', 'z'):
        reentry += [f'S_replace.STORE[n_{name}] = DEFINED pvalue_{name}']
    reentry += ['S_after = $af_find(S_replace, 2000, 1)', 'S_after.COMPLETION = NORMAL',
        'S_after.TODO = [THROW_SEARCH n_error, ' + body[1:-1] + ']',
        '$af_outputs(S_after.EVENTS) = $ptascii(' + json.dumps(completed_catch_output) + ')',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable_error', '$throwable_live(S_after, n_error)',
        'S_after.OBJECTS[n_old] = THROWABLE pthrowable_old', '$throwable_live(S_after, n_old)',
        '$throwable_previous_id(S_after, n_error) = (n_old)', '$throwable_previous_id(S_after, n_old) = eps',
        '~$throwable_live(S_after, n_nested_error)',
        '$throwable_field(S_after, n_error, "line") = PINT 3',
        '$string_bytes($throwable_field(S_after, n_error, "message")) = ($ptascii("replacement"))',
        '$throwable_field(S_after, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_after, n_trace)',
        '$heap_reach([HARRAY n_trace], eps, $heap_graph(S_after).EDGES) = pnode_trace*',
        '(S_after.ARRAYS[n_trace_part] = S_replace.ARRAYS[n_trace_part])*',
        'S_after.STORE[n_y] = DEFINED pvalue_y', 'S_after.STORE[n_n] = DEFINED (PINT 3)',
        '~((HOBJECT n_y_object) <- S_after.ALLOCATIONS)', 'n_y_object <- S_after.DESTRUCTION.CALLED',
        'S_after.DESTRUCTION.CALLS = eps', 'S_after.DESTRUCTION.RELEASES = eps', 'S_after.DESTRUCTION.OPERATIONS = eps',
        '$ref_chain_reentrant_replace_class(S_after, prefreturncursor_chain*)',
        '~$ref_chain_reentrant_caught_class(S_after, prefreturncursor_chain*)']
    reentry += public('S_after', 'after_replace')
    for name in ('x', 'w', 'z'):
        reentry += [f'S_after.STORE[n_{name}] = DEFINED pvalue_{name}']
    reentry += ['S_wx = $drive_steps(S_after[.COMPLETION = NORMAL], 1)', 'S_wx.COMPLETION = BUDGET',
        'S_wx.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN (' + wx + '), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_CHAIN ([prefreturncursor_x]), FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        'S_wx.ORIGIN = porigin_z_restore?', 'S_x = $drive_steps(S_wx[.COMPLETION = NORMAL], 1)', 'S_x.COMPLETION = BUDGET',
        'S_x.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ([prefreturncursor_x]), FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        'S_x.ORIGIN = porigin_w_restore?',
        '$ref_chain_reentrant_replace_class(S_wx, ' + wx + ')', '$ref_chain_reentrant_replace_class(S_x, [prefreturncursor_x])',
        '~$ref_chain_reentrant_caught_class(S_wx, ' + wx + ')', '~$ref_chain_reentrant_caught_class(S_x, [prefreturncursor_x])',
        'S_wx.STORE = S_after.STORE', 'S_x.STORE = S_after.STORE',
        'S_exit = $drive_steps(S_x[.COMPLETION = NORMAL], 1)', 'S_exit.COMPLETION = BUDGET',
        'S_exit.TODO = [THROW_SEARCH n_error]', 'S_exit.ORIGIN = porigin_x_restore?',
        'S_exit.EVENTS = S_after.EVENTS', 'S_exit.STORE = S_after.STORE', '$tc_markers(S_exit.TODO) = 0',
        '$throwable_live(S_exit, n_error)', 'S_caller = $af_find(S_exit, 2000, 2)',
        '$lookup(S_caller.ENV, $ptascii("e")) = (n_e)', 'S_caller.STORE[n_e] = DEFINED (POBJECT n_error)',
        'S_caller.OBJECTS[n_error] = THROWABLE pthrowable_error', '$throwable_live(S_caller, n_error)',
        'S_caller.OBJECTS[n_old] = THROWABLE pthrowable_old', '$throwable_live(S_caller, n_old)',
        '$throwable_previous_id(S_caller, n_error) = (n_old)', '$throwable_previous_id(S_caller, n_old) = eps',
        '~$throwable_live(S_caller, n_nested_error)',
        '$throwable_field(S_caller, n_error, "line") = PINT 3',
        '$throwable_field(S_caller, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_caller, n_trace)',
        '$heap_reach([HARRAY n_trace], eps, $heap_graph(S_caller).EDGES) = pnode_trace*',
        '(S_caller.ARRAYS[n_trace_part] = S_replace.ARRAYS[n_trace_part])*',
        'S_caller.GLOBALTABLE = eps',
        '$lookup(S_caller.ENV, $ptascii("n")) = (n_n)', 'S_caller.STORE[n_n] = DEFINED (PINT 3)',
        '$lookup(S_caller.ENV, $ptascii("y")) = (n_y)', 'S_caller.STORE[n_y] = DEFINED pvalue_y',
        '$lookup(S_caller.ENV, $ptascii("r")) = eps', '$ma_diagnostics(S_caller.EVENTS) = 0']
    reentry += public('S_wx', 'wx') + public('S_x', 'x') + public('S_caller', 'caller')
    reentry += ['S_bad_counter = S_x[.STORE[n_n] = DEFINED (PBOOL false)][.COMPLETION = NORMAL]',
        'S_bad_counter.TODO = S_x.TODO', 'S_bad_counter.ENV = S_x.ENV',
        'S_bad_counter.GLOBALTABLE = S_x.GLOBALTABLE', '$heap_valid($heap_graph(S_bad_counter))',
        'S_rejected_counter = $drive(S_bad_counter, 0)',
        'S_rejected_counter.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
    for name in ('x', 'w', 'z'):
        reentry += [f'S_caller.STORE[n_{name}] = DEFINED pvalue_{name}']
    fixture('destructor-fresh-replacement-keeps-creation-trace', primary,
        {0: pre, 1: escaping, 2: caught, 3: error, 4: replacing},
        reentry, finish='S_replace', budget=True)

    complete = ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
                f'prefreturncursor_chain* = {chain}']
    fields = []
    for name in ('z', 'w', 'x'):
        fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER', f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                   f'z_{name} = prefreturncursor_{name}.LINE', f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
               'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    alias = complete + globals + fields + ['$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
        '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I2;P;")', 'S.STORE[n_y] = DEFINED pvalue_y',
        '$string_bytes(pvalue_y) = ($ptascii("fixed"))', 'S.OBJECTS = eps', 'S.DESTRUCTION.CALLED = eps',
        'S.ORIGIN = porigin_x_restore?', '$reference_notice_count(S.TODO) = 0',
        '$lookup(S.ENV, $ptascii("n")) = (n_n)', 'S.STORE[n_n] = DEFINED (PINT 2)',
        'S_probed = $af_find(S, 2000, 3)', 'S_probed.COMPLETION = NORMAL',
        'S_probed.RESULT = REFERENCE n_y', 'S_probed.CURRENT = eps', 'S_probed.FRAMES = eps',
        '$tc_markers(S_probed.TODO) = 0', 'S_probed.STORE[n_y] = DEFINED pvalue_y']
    alias += public('S_probed', 'selected')
    alias += ['S_r = $af_find(S_probed, 2000, 1)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        '$lookup(S_r.ENV, $ptascii("y")) = (n_y)', 'S_written = $af_find($drive_steps(S_r, 1), 2000, 2)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        'S_written.OBJECTS = eps', 'S_written.DESTRUCTION.CALLED = eps',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))']
    for name in ('x', 'w', 'z'):
        alias += [f'S_written.STORE[n_{name}] = DEFINED pvalue_{name}']
    fixture('selected-y-alias-without-destructor-replacement', selected,
            {0: complete, 1: assigned, 2: written,
             3: ['S.RESULT = REFERENCE n_y', '$lookup(S.ENV, $ptascii("y")) = (n_y)',
                 'S.CURRENT = eps', 'S.FRAMES = eps', '$tc_markers(S.TODO) = 0',
                 'S.DESTRUCTION.CALLS = eps', 'S.DESTRUCTION.RELEASES = eps',
                 'S.DESTRUCTION.OPERATIONS = eps']}, alias, finish='S_written')

    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'public_refusals': 1, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
