"""Emit checked-source E-catch call continuation, selection and rethrow fixtures."""
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
    catalogue = ROOT / 'tests/semantics/reference_chain_mixed_e_call_cases.json'
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

    def fixture(name, case_id, stages, checks, finish, budget=False, terminal=()):
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
                      'S = $af_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL']
        assertions += stages[0] + ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))'] + checks
        assertions += [f'S_continue = {finish}[.COMPLETION = NORMAL]']
        if budget:
            assertions += ['S_zero = $drive(S_continue, 0)', 'S_zero.COMPLETION = BUDGET',
                           'S_zero.TODO = S_continue.TODO',
                           'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
                           'S_whole = $drive(S_continue, 10001)', 'S_adjacent = S_whole']
        else:
            assertions += ['S_whole = $drive(S_continue, 10001)']
        assertions += ['S_whole.COMPLETION = NORMAL',
                       '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(case['stdout']) + ')',
                       '$ma_diagnostics(S_whole.EVENTS) = ' + str(int(bool(case['stderr']))),
                       '$reference_notice_count(S_whole.TODO) = 0',
                       'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                       'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                       '$tc_markers(S_whole.TODO) = 0',
                       '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case_id, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': 0})

    def public(state, tag):
        admitted = 'S_admitted_' + tag
        return [f'{admitted} = $drive({state}[.COMPLETION = NORMAL], 0)',
                f'{admitted}.COMPLETION = BUDGET', f'{admitted}.TODO = {state}.TODO',
                f'$heap_valid($heap_graph({admitted}))']

    def error(state, name):
        return [f'{state}.OBJECTS[{name}] = THROWABLE pthrowable_new',
                'pthrowable_new.KIND = "TypeError"',
                f'$throwable_live({state}, {name})',
                f'$throwable_previous_id({state}, {name}) = eps',
                f'$throwable_field({state}, {name}, "line") = PINT 4',
                f'$string_bytes($throwable_field({state}, {name}, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))']

    primary, success_id, rethrow_id = 'mixed-e-call', 'mixed-e-call-y-success', 'mixed-e-call-e-rethrow'
    chain = '(prefreturncursor_z :: prefreturncursor_w :: prefreturncursor_o :: eps)'
    wo = '(prefreturncursor_w :: prefreturncursor_o :: eps)'
    body = ('(FINALLY_REF_CHAIN ' + wo + ') :: (FINALLY_PHASE porigin_w_owner 3) :: '
            '(ORIGIN_RETURN porigin_w_restore?) :: (FINALLY_REF_CHAIN (prefreturncursor_o :: eps)) :: '
            '(FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: eps')
    before_call = 'O;P;W;P;M1;P;I1;P;I2;P;C;M2;P;'
    after_call = before_call + 'P;'
    literal_prefix = after_call + 'E;B;'
    globals = ['S.GLOBALTABLE = (psymboltable)']
    for name in ('x', 'w', 'z', 'y'):
        globals += [f'$lookup(psymboltable.ENV, $ptascii("{name}")) = (n_{name})']
    globals += [r'n_x =/= n_w /\ n_x =/= n_z /\ n_x =/= n_y /\ n_w =/= n_z /\ n_w =/= n_y /\ n_z =/= n_y']
    for name, value in (('x', 'old'), ('w', 'extra')):
        globals += [f'S.STORE[n_{name}] = DEFINED pvalue_{name}',
                    f'$string_bytes(pvalue_{name}) = ($ptascii("{value}"))']
    fields = []
    for name in ('w', 'o'):
        fields += [f'porigin_{name}_owner = prefreturncursor_{name}.OWNER',
                   f'porigin_{name} = prefreturncursor_{name}.SOURCE',
                   f'z_{name} = prefreturncursor_{name}.LINE',
                   f'porigin_{name}_restore? = prefreturncursor_{name}.OUTER']
    old = ['$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
           'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
           'porigin_o_restore? = $ref_chain_function(S)', 'z_o = 4',
           '$task_nodes(FINALLY_REF_CHAIN (prefreturncursor_o :: eps)) = eps']
    live = ['S.STORE[n_z] = DEFINED PNULL',
            'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
            '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)'] + error('S', 'n_error')
    resumed_tail = ('(REF_REPLAY_ORIGIN porigin_z z_z prefowner*) :: '
                    '(REF_REPLAY_PHASE porigin_z z_z prefowner*) :: (ORIGIN_RETURN porigin_z_restore?) :: ' + body)
    call_tail = ('(ORIGIN_RETURN porigin_ping_statement?) :: DISCARD :: '
                 '(ORIGIN_RETURN porigin_e_body?) :: (AT porigin_echo_e (STMT statement_echo_e)) :: ' + resumed_tail)
    call_stage = ['$af_function(S, $ptascii("f"))',
                  '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(after_call) + ')',
                  'S.TODO = ' + call_tail,
                  'porigin_w_restore? = (porigin_e_catch)',
                  'porigin_ping_statement? = $origin_child((porigin_e_catch), [PCFIELD 1, PCINDEX 0, PCFIELD 2, PCINDEX 0])',
                  'S.ORIGIN = $origin_child(porigin_ping_statement?, [PCFIELD 0])']
    literal_stage = ['$af_function(S, $ptascii("f"))',
                     '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(literal_prefix) + ')',
                     'S.TODO = (FINALLY_REF_CHAIN (prefreturncursor_o :: eps)) :: '
                     '(FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: eps']
    normal = globals + fields + old + live + [
        'prefowner* = [REPLAY_TRY porigin_e_catch]',
        'porigin_z_restore? = $origin_child((porigin_w_owner), [PCFIELD 2])',
        'porigin_e_body? = $origin_child((porigin_e_catch), [PCFIELD 1, PCINDEX 0])',
        '$origin_child(porigin_e_body?, [PCFIELD 2, PCINDEX 1]) = (porigin_echo_e)',
        'S.ORIGIN = (porigin_ping)',
        '$origin_node(S.SOURCES, porigin_ping) = (NExprFuncCall (NName (BYTES text_ping) metadata_ping_name) (SEQUENCE eps) metadata_ping_call)',
        '$base64(text_ping) = $ptascii("ping")',
        'statement_echo_e = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_e) metadata_e])) metadata_echo_e',
        '$base64(text_e) = $ptascii("E;")',
        '$origin_node(S.SOURCES, porigin_z) = (NStmtReturn (NExprVariable (BYTES text_z) metadata_z) metadata_return_z)',
        '$base64(text_z) = $ptascii("z")', 'z_z = 4',
        '$ref_chain_catch_passage(S, ' + wo + ') = ([TRY_END porigin_e_catch, ORIGIN_RETURN porigin_e_restore?, AT porigin_echo_b (STMT statement_echo_b)])',
        'porigin_e_restore? = $origin_child((porigin_o_owner), [PCFIELD 2])',
        '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        'S_after = $drive_steps(S, 3)', 'S_after.COMPLETION = BUDGET',
        'S_after.TODO = (AT porigin_echo_e (STMT statement_echo_e)) :: ' + resumed_tail,
        'S_after.ORIGIN = porigin_e_body?',
    ]
    for field in ('STORE', 'OBJECTS', 'CURRENT', 'FRAMES', 'EVENTS'):
        normal += [f'S_after.{field} = S.{field}']
    normal += public('S_after', 'aftercall') + [
        'S_literal = $af_find(S_after, 2000, 1)', '$af_stage(S_literal, 1)',
        'S_literal.TODO = (FINALLY_REF_CHAIN (prefreturncursor_o :: eps)) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: eps',
        'S_literal.ORIGIN = $origin_child((porigin_o_owner), [PCFIELD 2])',
        'S_literal.STORE[n_e] = DEFINED (POBJECT n_error)',
        '$tasks_nodes(S_literal.TODO) = eps', '$reference_notice_count(S_literal.TODO) = 0', '$ma_diagnostics(S_literal.EVENTS) = 0',
        'S_resumed = $drive_steps(S_literal, 1)', 'S_resumed.COMPLETION = BUDGET',
        'S_resumed.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_o true porigin_o, REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE, REF_RECHECK porigin_o porigin_o_owner (KNOWN pvalue_old) z_o]',
        'S_resumed.ORIGIN = porigin_o_restore?', '$reference_notice_count(S_resumed.TODO) = 1',
        '$tc_markers(S_resumed.TODO) = 0', '$tasks_nodes(S_resumed.TODO) = eps',
        'S_resumed.STORE = S_literal.STORE', 'S_resumed.EVENTS = S_literal.EVENTS']
    fixture('e-call-return-literal-notice-and-fresh-cell', primary, {0: call_stage, 1: literal_stage}, normal,
            finish='S_resumed', budget=True, terminal=[
                '(DIAGNOSTIC "Notice" ($ptascii("Only variable references should be returned by reference")) z_o) <- S_whole.EVENTS',
                '$lookup(S_whole.ENV, $ptascii("r")) = (n_r)',
                'n_r =/= n_x', 'n_r =/= n_w', 'n_r =/= n_z', 'n_r =/= n_y',
                'S_whole.STORE[n_r] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
                'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
                'S_whole.STORE[n_z] = DEFINED PNULL', 'S_whole.STORE[n_y] = DEFINED pvalue_fixed'])

    success_stage = ['$af_function(S, $ptascii("f"))',
        'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        'prefreturncursor_chain* = ' + chain,
        '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M1;P;I1;P;")']
    assigned = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
               '$lookup(S.ENV, $ptascii("y")) = (n_r)',
               'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    success = globals + fields + old + [
        '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
        'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        '$task_nodes(REF_RETURN_CHAIN prefreturncursor_chain* porigin_y z_y) = eps',
        'S_returned = $drive_steps(S, 1)', 'S_returned.COMPLETION = BUDGET',
        'S_returned.RESULT = REFERENCE n_y', 'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        '$tc_markers(S_returned.TODO) = 0', '$reference_notice_count(S_returned.TODO) = 0',
    ] + public('S_returned', 'selected') + [
        'S_r = $af_find(S_returned, 2000, 1)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        'S_written = $af_find($drive_steps(S_r, 1), 2000, 2)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        '$tc_markers(S_written.TODO) = 0', '$reference_notice_count(S_written.TODO) = 0']
    fixture('y-success-cancels-e-call-and-keeps-alias', success_id,
            {0: success_stage, 1: assigned, 2: written}, success, finish='S_written', terminal=[
                '$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)',
                'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
                'S_whole.STORE[n_z] = DEFINED pvalue_z', 'S_whole.STORE[n_y] = DEFINED pvalue_changed',
                '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    escaping = ['$af_function(S, $ptascii("f"))', 'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(after_call + 'E;') + ')',
                '$ref_chain_consumed_tail(S.TODO) =/= eps',
                '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)']
    old_escape = ['$af_function(S, $ptascii("f"))',
        'S.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN (prefreturncursor_o :: eps), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        '$af_outputs(S.EVENTS) = $ptascii(' + json.dumps(after_call + 'E;') + ')']
    caller = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("e")) = (n_caller_e)',
              'S.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
              '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))']
    escape = globals + ['$ref_chain_consumed_tail(S.TODO) = ' + body] + fields + old + live + [
        'porigin_w_restore? = (porigin_e_catch)',
        '$ref_chain_catch_passage(S, ' + wo + ') = ([TRY_END porigin_e_catch, ORIGIN_RETURN porigin_e_restore?, AT porigin_echo_b (STMT statement_echo_b)])',
        '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0',
        'S_old = $af_find(S, 2000, 1)', '$af_stage(S_old, 1)',
        'S_old.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN (prefreturncursor_o :: eps), FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'S_old.ORIGIN = porigin_w_restore?', '$reference_notice_count(S_old.TODO) = 0',
    ] + public('S_old', 'old') + [
        'S_exit = $drive_steps(S_old, 1)', 'S_exit.COMPLETION = BUDGET',
        'S_exit.TODO = [THROW_SEARCH n_error]', 'S_exit.ORIGIN = porigin_o_restore?',
        '$tc_markers(S_exit.TODO) = 0', '$reference_notice_count(S_exit.TODO) = 0',
        'S_exit.STORE = S_old.STORE', 'S_exit.EVENTS = S_old.EVENTS',
        'S_caller = $af_find(S_exit, 2000, 2)',
        '$lookup(S_caller.ENV, $ptascii("e")) = (n_caller_e)',
        'S_caller.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
        '$throwable_live(S_caller, n_error)', '$lookup(S_caller.ENV, $ptascii("r")) = eps']
    fixture('e-call-rethrow-keeps-fresh-z-error-and-retires-history', rethrow_id,
            {0: escaping, 1: old_escape, 2: caller}, escape, finish='S_caller', terminal=[
                '$lookup(S_whole.ENV, $ptascii("r")) = eps',
                'S_whole.STORE[n_caller_e] = DEFINED (POBJECT n_error)',
                'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_w] = DEFINED pvalue_w',
                'S_whole.STORE[n_z] = DEFINED PNULL', 'S_whole.STORE[n_y] = DEFINED pvalue_fixed'])

    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path),
                                   'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'public_refusals': 0, 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
