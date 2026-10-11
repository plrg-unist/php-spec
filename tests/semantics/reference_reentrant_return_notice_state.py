"""Emit genuine nested/outer Notice delivery and escaped-return cancellation."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_chain_mixed_resume_state import PREFIX, sha
from request_environment_state import request_fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_reentrant_return_notice_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['passed'] and report['workers_closed']
    assert report['pins'] == report['pins_after'] and report['module_stats'] == report['module_stats_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    rows = {row['id']: row for row in report['results']}
    assert rows.keys() == cases.keys()
    assert all(row['source_agreement'] and row['model']['status'] == 'normal' for row in rows.values())
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    message = '$ptascii("Only variable references should be returned by reference")'
    nested = 'O;P;W;P;M1;P;I1;P;I2;P;C;M2;P;Q;O;P;W;P;M3;P;Q;E;B;'
    escaping = nested[:-2]
    outer = nested + 'T;E;B;'
    legacy = ('(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) :: '
              '(FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_f_restore?) :: '
              '(TYPE_FALLTHROUGH porigin_f) :: (REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) :: eps')

    def fixture(name, case_id, stages, checks):
        case, row = cases[case_id], rows[case_id]
        directory = args.raw / case_id
        checked = json.loads((directory / 'checked.json').read_text())
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert source.read_bytes() == case['source'].encode() and sha(source) == row['source_sha256']
        assert base64.b64decode(row['native']['stdout']) == case['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == case['stderr'].encode()
        assert row['native']['exit_status'] == case['exit'] == 0
        assert checked['ok'] and checked['fixture']
        start = '$php_request_run(' + checked['fixture'] + ', 0, ' + json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')'
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]', 'S = $af_find(S_start, 2000, 0)',
                      'S.COMPLETION = NORMAL'] + stages[0] + checks
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case_id, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})

    def public(state, tag):
        target = 'S_admitted_' + tag
        return [f'{target} = $drive({state}[.COMPLETION = NORMAL], 0)', f'{target}.COMPLETION = BUDGET',
                f'{target}.TODO = {state}.TODO', f'$heap_valid($heap_graph({target}))']

    function = ['S.CURRENT = (pcallcontext_f)',
                '$function_at($all_functions(S), pcallcontext_f.FUNCTION) = (pfunction_f)',
                'pfunction_f.NAME = $ptascii("f")', 'porigin_f = pfunction_f.ORIGIN']
    source = ['porigin_f_restore? = (porigin_f)', 'z_o = 4',
              '$finally_ref_source_valid(S, porigin_o_owner, porigin_o, z_o)',
              '$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_old) metadata_old) metadata_return_old)',
              '$base64(text_old) = $ptascii("old")',
              'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
              'S.ORIGIN = $origin_child((porigin_o_owner), [PCFIELD 2])',
              '$reference_notice_source(S, porigin_o, KNOWN pvalue_old, z_o, REF_NOTICE_VALUE)',
              '~$reference_return_null_valid(S[.ORIGIN = (porigin_o)], z_o)',
              '$reference_notice_presence(S)', '$reference_notice_count(S.TODO) = 1',
              '$task_nodes(REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) = eps',
              '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps',
              '$heap_valid($heap_graph(S))']
    globals = ['S.GLOBALTABLE = (psymboltable)']
    for name in ('x', 'w', 'z', 'y'):
        globals += [f'$lookup(psymboltable.ENV, $ptascii("{name}")) = (n_{name})']
    globals += [r'n_x =/= n_w /\ n_x =/= n_z /\ n_x =/= n_y /\ n_w =/= n_z /\ n_w =/= n_y /\ n_z =/= n_y',
                'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
                'S.STORE[n_w] = DEFINED pvalue_w', '$string_bytes(pvalue_w) = ($ptascii("extra"))',
                'S.STORE[n_z] = DEFINED PNULL', 'S.STORE[n_y] = DEFINED pvalue_fixed',
                '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))']
    nested_context = ['pcallcontext_f.CALLSITE = (porigin_nested_call)',
                      'S.FRAMES = pframe_post :: pframe_outer_f :: pframe_rest*',
                      'pframe_post.CONTEXT = (pcallcontext_post)',
                      '$function_at($all_functions(S), pcallcontext_post.FUNCTION) = (pfunction_post)',
                      'pfunction_post.NAME = $ptascii("post")',
                      'pframe_post.ORIGIN = (porigin_nested_call)',
                      '$origin_child((pfunction_post.ORIGIN), [PCFIELD 5, PCINDEX 2, PCFIELD 1, PCINDEX 1, PCFIELD 0]) = (porigin_nested_call)',
                      '$origin_node(S.SOURCES, porigin_nested_call) = (NExprFuncCall (NName (BYTES text_f) metadata_f) (SEQUENCE eps) metadata_call_f)',
                      '$base64(text_f) = $ptascii("f")',
                      'pframe_outer_f.CONTEXT = (pcallcontext_outer_f)',
                      'pcallcontext_outer_f.FUNCTION = pcallcontext_f.FUNCTION',
                      '$ref_chain_consumed_tail(pframe_outer_f.TODO) = (FINALLY_REF_CHAIN (prefreturncursor_w :: prefreturncursor_o :: eps)) :: ptask_outer_tail*',
                      '~$reference_return_used(S)']
    literal_stage = function + ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(nested) + ')', 'S.TODO = ' + legacy]
    returned_stage = ['$af_function(S, $ptascii("post"))', '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(nested) + ')']
    checks = source + globals + nested_context + ['$ma_diagnostics(S.EVENTS) = 0'] + public('S', 'nested') + [
        'S_resumed = $drive_steps(S, 1)', 'S_resumed.COMPLETION = BUDGET',
        'S_resumed.TODO = (RETURN_REF_UNWIND (KNOWN pvalue_old) z_o true porigin_o) :: (TYPE_FALLTHROUGH porigin_f) :: (REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) :: (REF_RECHECK porigin_o porigin_o_owner (KNOWN pvalue_old) z_o) :: eps',
        'S_resumed.ORIGIN = porigin_f_restore?', 'S_resumed.EVENTS = S.EVENTS',
        'S_resumed.STORE = S.STORE', '$reference_notice_count(S_resumed.TODO) = 1'] + public('S_resumed', 'resumed') + [
        'S_return = $af_find(S_resumed[.COMPLETION = NORMAL], 2000, 1)', '$af_stage(S_return, 1)',
        'S_return.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Notice" (' + message + ') z_o]',
        '$ma_diagnostics(S_return.EVENTS) = 1', 'S_return.CURRENT = pframe_post.CONTEXT',
        'S_return.FRAMES = pframe_outer_f :: pframe_rest*', 'S_return.ORIGIN = (porigin_nested_call)',
        'porigin_nested_statement? = $origin_child((pfunction_post.ORIGIN), [PCFIELD 5, PCINDEX 2, PCFIELD 1, PCINDEX 1])',
        'porigin_guard? = $origin_child((pfunction_post.ORIGIN), [PCFIELD 5, PCINDEX 2])',
        'porigin_t? = $origin_child((pfunction_post.ORIGIN), [PCFIELD 5, PCINDEX 2, PCFIELD 1, PCINDEX 2])',
        'porigin_t? = (porigin_t_statement)', '$origin_node(S_return.SOURCES, porigin_t_statement) = (statement_t)',
        'S_return.TODO = (ORIGIN_RETURN porigin_nested_statement?) :: DISCARD :: (ORIGIN_RETURN porigin_guard?) :: (AT porigin_t_statement (STMT statement_t)) :: (ORIGIN_RETURN (pfunction_post.ORIGIN)) :: RETURN_NULL :: eps',
        '$reference_notice_count(S_return.TODO) = 0', '$heap_valid($heap_graph(S_return))'] + public('S_return', 'returned')
    fixture('nested-live-value-notice-before-t', 'reentrant-e-call', {0: literal_stage, 1: returned_stage}, checks)

    outer_stage = function + ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(outer) + ')',
                  'S.TODO = (FINALLY_REF_CHAIN (prefreturncursor_o :: eps)) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_f_restore?) :: eps']
    checks = globals + ['prefreturncursor_o.OWNER = porigin_o_owner', 'prefreturncursor_o.OUTER = porigin_f_restore?',
              'porigin_f_restore? = (porigin_f)', 'porigin_o = prefreturncursor_o.SOURCE', 'z_o = prefreturncursor_o.LINE', 'z_o = 4',
              '$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
              'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
              'S.ORIGIN = $origin_child((porigin_o_owner), [PCFIELD 2])', '$reference_return_used(S)',
              '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 1'] + public('S', 'outer') + [
              'S_resumed = $drive_steps(S, 1)', 'S_resumed.COMPLETION = BUDGET',
              'S_resumed.TODO = (RETURN_REF_UNWIND (KNOWN pvalue_old) z_o true porigin_o) :: (REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) :: (REF_RECHECK porigin_o porigin_o_owner (KNOWN pvalue_old) z_o) :: eps',
              'S_resumed.EVENTS = S.EVENTS', 'S_resumed.STORE = S.STORE', '$reference_notice_count(S_resumed.TODO) = 1'] + public('S_resumed', 'outerresumed') + [
              'S_continue = S_resumed[.COMPLETION = NORMAL]', 'S_zero = $drive(S_continue, 0)', 'S_zero.COMPLETION = BUDGET',
              'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
              'S_whole = $drive(S_continue, 10001)', 'S_adjacent = S_whole',
              'S_whole.COMPLETION = NORMAL', '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(cases['reentrant-e-call']['stdout']) + ')',
              '$ma_diagnostics(S_whole.EVENTS) = 2',
              'S_delivered = $af_find(S_continue, 2000, 1)',
              'S_delivered.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Notice" (' + message + ') z_o]',
              '$lookup(S_whole.ENV, $ptascii("r")) = (n_r)', 'n_r =/= n_x', 'n_r =/= n_w', 'n_r =/= n_z', 'n_r =/= n_y',
              'S_whole.STORE[n_r] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
              'n_r <- S_whole.REFCELLS',
              'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
              'S_whole.STORE[n_z] = DEFINED PNULL', 'S_whole.STORE[n_y] = DEFINED pvalue_fixed']
    delivered_stage = ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(outer) + ')', '$ma_diagnostics(S.EVENTS) = 2']
    clean = ['S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.HELD = eps',
             'S_whole.RETIREDOWNERS = eps', '$reference_notice_count(S_whole.TODO) = 0',
             '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))']
    fixture('outer-additional-notice-and-fresh-caller-cell', 'reentrant-e-call', {0: outer_stage, 1: delivered_stage}, checks + clean)

    escape_stage = function + ['$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(escaping) + ')',
                   'S.TODO = (THROW_SEARCH n_error) :: ' + legacy]
    checks = source + globals + nested_context + [
              '$ma_diagnostics(S.EVENTS) = 0', '$throwable_live(S, n_error)',
              'S.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
              '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)',
              '$throwable_field(S, n_error, "line") = PINT 4',
              '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))'] + public('S', 'escape') + [
              'S_left = $drive_steps(S, 1)', 'S_left.COMPLETION = BUDGET',
              'S_left.TODO = (THROW_SEARCH n_error) :: (TYPE_FALLTHROUGH porigin_f) :: (REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE) :: eps',
              'S_left.ORIGIN = porigin_f_restore?', 'S_left.EVENTS = S.EVENTS', 'S_left.STORE = S.STORE',
              '$reference_notice_count(S_left.TODO) = 1', '$reference_notice_discarding(S_left)',
              'S_whole = $drive(S_left[.COMPLETION = NORMAL], 10001)', 'S_whole.COMPLETION = NORMAL',
              '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(cases['e-rethrow']['stdout']) + ')',
              '$ma_diagnostics(S_whole.EVENTS) = 0', '$lookup(S_whole.ENV, $ptascii("r")) = eps',
              '$lookup(S_whole.ENV, $ptascii("e")) = (n_caller_e)', 'S_whole.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
              '$throwable_live(S_whole, n_error)', 'S_whole.STORE[n_x] = DEFINED pvalue_x',
              'S_whole.STORE[n_w] = DEFINED pvalue_w', 'S_whole.STORE[n_z] = DEFINED PNULL',
              'S_whole.STORE[n_y] = DEFINED pvalue_fixed']
    fixture('nested-e-rethrow-cancels-restored-notice', 'e-rethrow', {0: escape_stage}, checks + clean)
    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')})


if __name__ == '__main__':
    main()
