"""Emit reached global-W rebinding and retained-local retirement proofs."""
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
    catalogue = ROOT / 'tests/semantics/reference_lifecycle_rebinding_w_cases.json'
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

    def fixture(name, case_id, stages, checks, finish=None, budget=False, public_refusals=0):
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
                        'fixture_sha256': sha(path), 'assertions': len(assertions), 'public_refusals': public_refusals})

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
              'porigin_x_restore? = (porigin_function)', f'prefreturncursor_chain* = {chain}',
              '$ref_chain_site(S, prefreturncursor_chain*, porigin_y, z_y)',
              '$destructor_operational(S)', '$ref_chain_lifecycle_safe(S, prefreturncursor_chain*)',
              '$ref_chain_rebinding_class(S, prefreturncursor_chain*)',
              '$ref_chain_mutation_cursor(S, prefreturncursor_chain*) = (prefreturncursor_w)',
              '$reference_notice_count(S.TODO) = 0', '$ma_diagnostics(S.EVENTS) = 0']
    sites += ['S.CLASSES = pclassdesc :: eps', 'pclassdesc.METHODS = pmethoddesc :: eps',
        'pmethoddesc.NAME = $ptascii("__destruct")',
        '$origin_node(S.SOURCES, pmethoddesc.FUNCTION.ORIGIN) = (NStmtClassMethod phpType14 (INTEGER 1) (BOOLEAN false) (NIdentifier (BYTES text_dtor) metadata_dtor) (SEQUENCE eps) ABSENT (SEQUENCE ([NStmtExpression (NExprAssignRef (NExprArrayDimFetch (NExprVariable (BYTES text_globals_w) metadata_globals_w) (NScalarString (BYTES text_key_w) metadata_key_w) metadata_fetch_w) (NExprArrayDimFetch (NExprVariable (BYTES text_globals_x) metadata_globals_x) (NScalarString (BYTES text_key_x) metadata_key_x) metadata_fetch_x) metadata_assign_ref) metadata_statement_w, NStmtEcho (SEQUENCE ([NScalarString (BYTES text_d) metadata_d])) metadata_echo, NStmtExpression (NExprThrow (NExprNew (NName (BYTES text_type) metadata_type) (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text_message) metadata_message) (BOOLEAN false) (BOOLEAN false) metadata_arg])) metadata_new) metadata_throw) metadata_statement])) metadata_method)',
        '$base64(text_globals_w) = $ptascii("GLOBALS")', '$base64(text_globals_x) = $ptascii("GLOBALS")',
        '$base64(text_key_w) = $ptascii("w")', '$base64(text_key_x) = $ptascii("x")',
        '$ref_chain_mutation_source_cursor(S, prefreturncursor_chain*) = (prefreturncursor_w)']
    error = ['S.TODO = [THROW_SEARCH n_y_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*]']
    old_error = ['S_error = $af_find(S, 2000, 3)', 'S_error.COMPLETION = NORMAL',
        'S_error.TODO = [THROW_SEARCH n_y_error, REF_REPLAY_CHAIN porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_chain*]',
        '$ref_replay_contexts(S_error, porigin_y) = prefowner*', 'prefowner* = [REPLAY_TRY porigin_first]',
        '$throwable_live(S_error, n_y_error)', 'S_error.OBJECTS[n_y_error] = THROWABLE pthrowable_y',
        'pthrowable_y.KIND = "TypeError"', '$throwable_previous_id(S_error, n_y_error) = eps',
        '$throwable_field(S_error, n_y_error, "line") = PINT z_y',
        '$string_bytes($throwable_field(S_error, n_y_error, "message")) = ($ptascii("f(): Return value must be of type string, SelectedY returned"))',
        'S_error.STORE[n_y] = DEFINED (POBJECT n_y_object)', 'S_error.EVENTS = S.EVENTS']
    escaping = ['S.TODO = [THROW_SEARCH n_error, ' + body[1:-1] + ']',
                f'prefreturncursor_chain* = {chain}',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;I2;P;D;")']
    caught = ['$af_outputs(S.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;I2;P;D;R:destructor;")',
              '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)',
              'S.CURRENT = eps', 'S.FRAMES = eps']
    escape = pre + globals + sites + ['S.STORE[n_y] = DEFINED (POBJECT n_y_object)'] + old_error
    escape += ['S_after = $af_find(S_error, 2000, 1)', 'S_after.COMPLETION = NORMAL',
        'S_after.TODO = [THROW_SEARCH n_error, ' + body[1:-1] + ']',
        'n_error =/= n_y_error',
        '$af_outputs(S_after.EVENTS) = $ptascii("O;P;W;P;M;P;I1;P;I2;P;D;")',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        '$throwable_live(S_after, n_error)', '$throwable_field(S_after, n_error, "line") = PINT 3',
        '$string_bytes($throwable_field(S_after, n_error, "message")) = ($ptascii("destructor"))',
        '$throwable_previous_id(S_after, n_error) = (n_y_error)',
        'S_after.OBJECTS[n_y_error] = THROWABLE pthrowable_y', '$throwable_live(S_after, n_y_error)',
        '$throwable_previous_id(S_after, n_y_error) = eps',
        '$throwable_field(S_after, n_y_error, "line") = PINT z_y',
        '$string_bytes($throwable_field(S_after, n_y_error, "message")) = ($ptascii("f(): Return value must be of type string, SelectedY returned"))',
        'S_after.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        '~((HOBJECT n_y_object) <- S_after.ALLOCATIONS)', 'n_y_object <- S_after.DESTRUCTION.CALLED',
        'S_after.DESTRUCTION.CALLS = eps', 'S_after.DESTRUCTION.RELEASES = eps', 'S_after.DESTRUCTION.OPERATIONS = eps']
    escape += public('S_after', 'post_d')
    for name in ('x', 'z'):
        escape += [f'S_after.STORE[n_{name}] = DEFINED pvalue_{name}']
    escape += ['S_after.STORE[n_w] = DEFINED pvalue_w',
        '$lookup(S_after.ENV, $ptascii("w")) = (n_w)', '$lookup(S_after.ENV, $ptascii("x")) = (n_x)',
        'S_after.GLOBALTABLE = (psymboltable_after)',
        '$lookup(psymboltable_after.ENV, $ptascii("w")) = (n_x)',
        '$lookup(psymboltable_after.ENV, $ptascii("x")) = (n_x)',
        '$ref_chain_rebinding_class(S_after, prefreturncursor_chain*)',
        '$ref_chain_rebinding_cursor(S_after, prefreturncursor_w)',
        '~$ref_chain_string_cursors(S_after, [prefreturncursor_w])']
    escape += ['S_wx = $drive_steps(S_after[.COMPLETION = NORMAL], 1)', 'S_wx.COMPLETION = BUDGET',
        'S_wx.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN (' + wx + '), FINALLY_PHASE porigin_w_owner 3, ORIGIN_RETURN porigin_w_restore?, FINALLY_REF_CHAIN ([prefreturncursor_x]), FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        'S_wx.ORIGIN = porigin_z_restore?', 'S_x = $drive_steps(S_wx[.COMPLETION = NORMAL], 1)', 'S_x.COMPLETION = BUDGET',
        'S_x.TODO = [THROW_SEARCH n_error, FINALLY_REF_CHAIN ([prefreturncursor_x]), FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        'S_x.ORIGIN = porigin_w_restore?', 'S_wx.STORE = S_after.STORE', 'S_x.STORE = S_after.STORE',
        '$ref_chain_mutation_source_cursor(S_wx, ' + wx + ') = (prefreturncursor_w)',
        '$ref_chain_mutation_source_cursor(S_x, [prefreturncursor_x]) = (prefreturncursor_w)',
        '$ref_chain_rebinding_class(S_wx, ' + wx + ')',
        '$ref_chain_rebinding_class(S_x, [prefreturncursor_x])',
        'S_wx.GLOBALTABLE = S_after.GLOBALTABLE', 'S_x.GLOBALTABLE = S_after.GLOBALTABLE',
        '$lookup(S_wx.ENV, $ptascii("w")) = (n_w)', '$lookup(S_x.ENV, $ptascii("w")) = (n_w)',
        '$ref_chain_rebinding_cursor(S_wx, prefreturncursor_w)',
        '$ref_chain_rebinding_cursor(S_x, prefreturncursor_w)',
        '~$ref_chain_string_cursors(S_wx, [prefreturncursor_w])',
        '~$ref_chain_string_cursors(S_x, [prefreturncursor_w])',
        '$ref_chain_string_cursors(S_wx, [prefreturncursor_x])',
        '$ref_chain_string_cursors(S_x, [prefreturncursor_x])',
        '$ref_chain_mutation_cursor(S_wx, ' + wx + ') = eps',
        '$ref_chain_mutation_cursor(S_x, [prefreturncursor_x]) = eps', 'S_exit = $drive_steps(S_x[.COMPLETION = NORMAL], 1)', 'S_exit.COMPLETION = BUDGET',
        'S_exit.TODO = [THROW_SEARCH n_error]', 'S_exit.ORIGIN = porigin_x_restore?',
        'S_exit.EVENTS = S_after.EVENTS', 'S_exit.STORE = S_after.STORE',
        'S_exit.GLOBALTABLE = S_after.GLOBALTABLE', '$lookup(S_exit.ENV, $ptascii("w")) = (n_w)',
        '$tc_markers(S_exit.TODO) = 0',
        '$throwable_live(S_exit, n_error)', 'S_caller = $af_find(S_exit, 2000, 2)',
        '$lookup(S_caller.ENV, $ptascii("e")) = (n_e)', 'S_caller.STORE[n_e] = DEFINED (POBJECT n_error)',
        'S_caller.OBJECTS[n_error] = THROWABLE pthrowable', '$throwable_live(S_caller, n_error)',
        '$throwable_previous_id(S_caller, n_error) = (n_y_error)',
        'S_caller.OBJECTS[n_y_error] = THROWABLE pthrowable_y', '$throwable_live(S_caller, n_y_error)',
        '$throwable_previous_id(S_caller, n_y_error) = eps',
        '$lookup(S_caller.ENV, $ptascii("r")) = eps', '$ma_diagnostics(S_caller.EVENTS) = 0']
    escape += public('S_wx', 'wx') + public('S_x', 'x')
    escape += ['psymboltable_bad_x = psymboltable_after[.ENV = (BIND $ptascii("x") n_w) :: $unbind(psymboltable_after.ENV, $ptascii("x"))]',
        'S_bad_x = S_x[.GLOBALTABLE = (psymboltable_bad_x)][.COMPLETION = NORMAL]',
        'S_bad_x.STORE = S_x.STORE', 'S_bad_x.ENV = S_x.ENV', 'S_bad_x.TODO = S_x.TODO',
        '$lookup(psymboltable_bad_x.ENV, $ptascii("w")) = (n_x)',
        '$lookup(psymboltable_bad_x.ENV, $ptascii("x")) = (n_w)',
        'S_bad_x.ORIGIN = S_x.ORIGIN', '$heap_valid($heap_graph(S_bad_x))',
        'S_rejected_x = $drive(S_bad_x, 0)',
        'S_rejected_x.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
    for name in ('x', 'z'):
        escape += [f'S_caller.STORE[n_{name}] = DEFINED pvalue_{name}']
    escape += ['S_caller.GLOBALTABLE = eps',
        '$lookup(S_caller.ENV, $ptascii("w")) = (n_x)',
        '$lookup(S_caller.ENV, $ptascii("x")) = (n_x)']
    escape += public('S_caller', 'caller')
    fixture('retained-local-w-survives-global-rebinding', primary,
            {0: pre, 1: escaping, 2: caught, 3: error}, escape, finish='S_caller', budget=True, public_refusals=1)

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
        'S_returned = $af_find(S, 2000, 3)', 'S_returned.COMPLETION = NORMAL',
        'S_returned.RESULT = REFERENCE n_y', 'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        '$tc_markers(S_returned.TODO) = 0', 'S_returned.STORE[n_y] = DEFINED pvalue_y']
    alias += public('S_returned', 'selected')
    alias += ['S_r = $af_find(S_returned, 2000, 1)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        '$lookup(S_r.ENV, $ptascii("y")) = (n_y)', 'S_written = $af_find($drive_steps(S_r, 1), 2000, 2)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        'S_written.OBJECTS = eps', 'S_written.DESTRUCTION.CALLED = eps',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))']
    for name in ('x', 'w', 'z'):
        alias += [f'S_written.STORE[n_{name}] = DEFINED pvalue_{name}']
    fixture('selected-y-alias-without-global-rebinding', selected,
            {0: complete, 1: assigned, 2: written,
             3: ['S.RESULT = REFERENCE n_y', '$lookup(S.ENV, $ptascii("y")) = (n_y)',
                 'S.CURRENT = eps', 'S.FRAMES = eps', '$tc_markers(S.TODO) = 0',
                 'S.DESTRUCTION.CALLS = eps', 'S.DESTRUCTION.RELEASES = eps',
                 'S.DESTRUCTION.OPERATIONS = eps']}, alias, finish='S_written')

    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'producer_sha256': sha(Path(__file__)),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'public_refusals': sum(row['public_refusals'] for row in records), 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
