"""Emit request-store Fiber fatal transfer and ordinary catch continuation checks."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_active_finalizer_state import PREFIX
from reference_orphaned_cv_state import QUIET, public, sha
from request_environment_state import request_fixture

HEAD = 'd16a062ba6691a0b21910ef75ac5abbcbad19235'
SOURCE_HEAD = '0ec208316a6da70dd95464ef2ce5e5344afc5a06'
REPORT_SHA = '8a3032d690d3930f0473ca10e54882773fd594c3c3e7a32d89042adfc0b51cb3'
INPUTS = {
    'cycle': ('b24d624bd0951d55d04a1499c104dae8d0b2c0f52a5f817f221c2b762b03e7ed',
              '6ddaf38ae897c131765915ff8fa8afc02ad14fb22e170be5a48d924ad5487a64',
              'eaedc9f05cffcc4536b08ae9dcd333e53a30642c89da4301319e4710fe07ff55',
              'U;B:1;L;G;E;D;', 'U;B:1;L;G;E;D;', 255),
    'null-control': ('1aaf54763787e9f525f253dfb22b07ed08d22d4e4225cb750a90aeff97be0b53',
                     'a48e50aed97c15cfe653b035bf022bd2250a001be5ac473113f0aedcddcb1db7',
                     '720d656acbdf58549634386af13c224731eacdecb600e1be478183db10c2cef4',
                     'U;B:1;D;', 'U;B:1;D;C:old;P:null;L;G;E;', 0),
}


def preserved(state):
    return [f'{state}.OBJECTS[n_error] = THROWABLE pthrowable_error',
            f'$throwable_previous_id({state}, n_error) = eps',
            f'$throwable_field({state}, n_error, "line") = PINT 2',
            f'$throwable_field({state}, n_error, "trace") = PARRAY n_trace',
            f'$trace_graph_valid({state}, n_trace)',
            f'$heap_reach([HARRAY n_trace], eps, $heap_graph({state}).EDGES) = pnode_trace*',
            f'({state}.ARRAYS[n_trace_part] = S_throw.ARRAYS[n_trace_part])*']


def drained(state):
    return [f'{state}.CURRENT = eps', f'{state}.FRAMES = eps',
            f'{state}.HELD = eps', f'{state}.RETIREDOWNERS = eps',
            f'{state}.ACTIVEFIBER = eps', f'{state}.FIBERCALLERS = eps',
            f'{state}.FIBERCLOSERS = eps', f'{state}.DESTRUCTION.CALLS = eps',
            f'{state}.DESTRUCTION.RELEASES = eps', f'{state}.DESTRUCTION.OPERATIONS = eps',
            f'{state}.DESTRUCTION.FRAMES = eps', f'{state}.DESTRUCTION.CLEANUPS = eps']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.raw / 'report.json'
    assert sha(report_path) == REPORT_SHA
    report = json.loads(report_path.read_text())
    assert report['revision'] == report['head_after'] == SOURCE_HEAD and report['status_after'] == ''
    assert report['complete'] and report['passed'] and report['workers_closed']
    assert report['pins'] == report['pins_after'] and report['module_stats'] == report['module_stats_after']
    assert report['model_evaluations'] == report['source_agreements'] == 2
    rows = {row['id']: row for row in report['results']}
    assert rows.keys() == INPUTS.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for case, (source_sha, checked_sha, request_sha, prefix, expected, exit_status) in INPUTS.items():
        directory = args.raw / case
        checked_path, request_path = directory / 'checked.json', directory / 'request.json'
        assert sha(checked_path) == checked_sha and sha(request_path) == request_sha
        checked, facts = json.loads(checked_path.read_text()), json.loads(request_path.read_text())
        source = Path(base64.b64decode(facts['file']).decode())
        assert sha(source) == rows[case]['source_sha256'] == source_sha
        for engine in ('native', 'model'):
            assert base64.b64decode(rows[case][engine]['stdout']) == expected.encode()
            assert rows[case][engine]['exit_status'] == exit_status
        assert rows[case]['native']['stderr'] == rows[case]['model']['stderr']
        assert checked['ok'] and checked['fixture']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stages = {1: [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")',
                      'S.CURRENT = (pcallcontext_stage)',
                      'pcallcontext_stage.TARGET = METHOD_TARGET n_object porigin_destructor',
                      'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*']}
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
            'S_throw = $af_find(S_initial[.COMPLETION = NORMAL], 2000, 1)',
            'S_throw.COMPLETION = NORMAL', '$af_stage(S_throw, 1)',
            'S_throw.CURRENT = (pcallcontext_destructor)',
            'pcallcontext_destructor.TARGET = METHOD_TARGET n_old_object porigin_destructor',
            'pcallcontext_destructor.FUNCTION = porigin_destructor',
            'pcallcontext_destructor.LEXICAL_CLASS = (PORIGIN n_unit ([PCINDEX 0]))',
            'pcallcontext_destructor.LINE = 3',
            '$origin_child((porigin_destructor), [PCFIELD 6, PCINDEX 1]) = (porigin_throw_statement)',
            '$origin_node(S_throw.SOURCES, porigin_throw_statement) = (NStmtExpression (NExprThrow expression_new metadata_throw) metadata_statement)',
            '$origin_child((porigin_throw_statement), [PCFIELD 0]) = (porigin_throw)',
            '$origin_child((porigin_throw), [PCFIELD 0]) = (porigin_new)',
            'S_throw.ORIGIN = (porigin_throw)',
            'expression_new = NExprNew (NName (BYTES text_exception) metadata_exception) (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text_message) metadata_message) (BOOLEAN false) (BOOLEAN false) metadata_arg])) metadata_new',
            '$base64(text_exception) = $ptascii("Exception")', '$base64(text_message) = $ptascii("old")',
            'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*', 'n_error =/= n_old_object',
            'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Exception"', 'pthrowable_error.ORIGIN = (porigin_new)',
            '$throwable_previous_id(S_throw, n_error) = eps',
            '$string_bytes($throwable_field(S_throw, n_error, "message")) = ($ptascii("old"))',
            '$throwable_field(S_throw, n_error, "line") = PINT 2',
            '$throwable_field(S_throw, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_throw, n_trace)',
            'pnode_trace* = $heap_reach([HARRAY n_trace], eps, $heap_graph(S_throw).EDGES)',
            'pnode_trace* = (HARRAY n_trace_part)*',
            'S_throw.ARRAYS[n_trace].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_first_frame))) :: pentry_trace_tail*',
            '$trace_array_field(S_throw, n_first_frame, $ptascii("line")) = PINT 3',
            '$trace_array_field(S_throw, n_first_frame, $ptascii("function")) = PSTRING $ptascii("__destruct")',
            '$trace_array_field(S_throw, n_first_frame, $ptascii("class")) = PSTRING $ptascii("O")',
            'S_throw.ACTIVEFIBER = (n_fiber)',
            'S_throw.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*',
            'pfiberclose.OBJECT = n_fiber', 'pfiberclose.EXIT =/= n_error',
            'pfiberclose.SUSPEND.LINE = 3',
        ] + public('S_throw')
        if case == 'cycle':
            stages[2] = [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")',
                         'S.TODO = (FIBER_CALLBACK_FINISH pfiberfinish) :: ptask_tail*',
                         'pfiberfinish.PENDING = (n_error)', 'S.CURRENT = eps', 'S.FRAMES = eps']
            assertions += ['~pfiberclose.RELEASE.USER',
                'S_transfer = $af_find($drive_steps(S_throw, 1), 2000, 2)',
                'S_transfer.COMPLETION = NORMAL', '$af_stage(S_transfer, 2)',
                'S_transfer.TODO = [FIBER_CALLBACK_FINISH pfiberfinish]',
                'pfiberfinish.OBJECT = n_fiber', 'pfiberfinish.PENDING = (n_error)',
                'S_transfer.FIBERCLOSERS = [pfiberclose]', '$fiber_callback_ready(S_transfer)',
            ] + preserved('S_transfer') + public('S_transfer')
            # Descriptor admission follows driver cleanup of the raw terminal step.
            assertions += ['PhpStep: S_transfer ~> S_uncaught',
                'S_uncaught.COMPLETION = UNCAUGHT n_error',
                'S_uncaught.ERRORORIGIN = pthrowable_error.FILEORIGIN',
                'S_uncaught.CURRENT = eps', 'S_uncaught.FRAMES = eps',
                'S_uncaught.ACTIVEFIBER = eps', 'S_uncaught.FIBERCLOSERS = eps',
                'S_uncaught.FIBERCALLERS = eps',
                'S_uncaught.TODO = [DESTRUCTOR_RELEASE pfiberclose.RELEASE, DESTRUCTOR_STORE]',
                'S_uncaught.DESTRUCTION.RELEASES = [pfiberclose.RELEASE]',
                '$fiber_at(S_uncaught, n_fiber) = (pfiber_closed)',
                'pfiber_closed.STATUS = FIBER_TERMINATED', 'pfiber_closed.VM = eps',
                '~pfiber_closed.RETURNED', 'pfiber_closed.FAILED', '~pfiber_closed.GRACEFUL',
            ] + preserved('S_uncaught') + ['$heap_valid($heap_graph(S_uncaught))', '$rc_quiet(S_uncaught.EVENTS)']
            budget_state = 'S_transfer'
        else:
            stages[2] = [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}")', 'S.CURRENT = eps',
                         '$lookup(S.ENV, $ptascii("e")) = (n_e)',
                         'S.STORE[n_e] = DEFINED (POBJECT n_error)']
            stages[3] = [f'$af_outputs(S.EVENTS) = $ptascii("{prefix}C:old;P:null;")',
                         'S.CURRENT = eps',
                         'S.TODO = (AT (PORIGIN n_unit ([PCINDEX 6])) (STMT statement_next)) :: ptask_tail*']
            assertions += ['pfiberclose.RELEASE.USER',
                'S_catch = $af_find($drive_steps(S_throw, 1), 2000, 2)',
                'S_catch.COMPLETION = NORMAL', '$af_stage(S_catch, 2)',
                '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
                'S_catch.STORE[n_e] = DEFINED (POBJECT n_error)',
            ] + preserved('S_catch') + public('S_catch')
            assertions += ['S_caller = $af_find($drive_steps(S_catch, 1), 2000, 3)',
                'S_caller.COMPLETION = NORMAL', '$af_stage(S_caller, 3)',
                'S_caller.TODO = (AT (PORIGIN n_unit ([PCINDEX 6])) (STMT statement_next)) :: ptask_caller*',
                '$origin_node(S_caller.SOURCES, PORIGIN n_unit ([PCINDEX 6])) = (statement_next)',
                'statement_next = NStmtEcho (SEQUENCE ([NScalarString (BYTES text_next) metadata_next])) metadata_next_statement',
                '$base64(text_next) = $ptascii("L;")',
                '$lookup(S_caller.ENV, $ptascii("e")) = (n_e)',
                'S_caller.STORE[n_e] = DEFINED (POBJECT n_error)',
                '$lookup(S_caller.ENV, $ptascii("w")) = eps',
                '$lookup(S_caller.ENV, $ptascii("r")) = eps',
                'S_caller.GLOBALTABLE = eps',
                '$fiber_at(S_caller, n_fiber) = eps',
                'S_caller.OBJECTS[n_fiber] = FIBER pfiber_closed',
                'pfiber_closed.STATUS = FIBER_TERMINATED', 'pfiber_closed.VM = eps',
                '~pfiber_closed.RETURNED', 'pfiber_closed.FAILED', '~pfiber_closed.GRACEFUL',
                '~((HOBJECT n_old_object) <- S_caller.ALLOCATIONS)',
            ] + preserved('S_caller') + drained('S_caller') + public('S_caller')
            budget_state = 'S_caller'
        assertions += [f'S_zero = $drive({budget_state}, 0)', 'S_zero.COMPLETION = BUDGET',
            f'S_zero.TODO = {budget_state}.TODO', f'S_zero.ENV = {budget_state}.ENV',
            f'S_zero.ALLOCATIONS = {budget_state}.ALLOCATIONS',
            f'S_zero.FIBERCLOSERS = {budget_state}.FIBERCLOSERS',
            'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 1000)',
            f'S_whole = $drive({budget_state}, 1001)', 'S_adjacent = S_whole',
            f'$af_outputs(S_whole.EVENTS) = $ptascii("{expected}")',
            'S_whole.TODO = eps', 'S_whole.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            '$lookup(S_whole.ENV, $ptascii("w")) = eps',
            '$lookup(S_whole.ENV, $ptascii("r")) = eps',
            '~((HOBJECT n_fiber) <- S_whole.ALLOCATIONS)',
            '~((HOBJECT n_old_object) <- S_whole.ALLOCATIONS)',
            '~((HOBJECT n_error) <- S_whole.ALLOCATIONS)',
            '(~((HARRAY n_trace_part) <- S_whole.ALLOCATIONS))*',
        ] + drained('S_whole')
        if case == 'cycle':
            stderr = '$base64(' + json.dumps(rows[case]['native']['stderr']) + ')'
            assertions += ['S_one.COMPLETION = BUDGET',
                'S_whole.COMPLETION = REQUESTFATAL ($ptascii("Exception")) ($ptascii("old")) 2', 'S_whole.EXITSTATUS = 255',
                'S_whole.EVENTS = S_throw.EVENTS ++ [STDERR (' + stderr + ')]',
                'S_whole.DESTRUCTION.CALLED = $destructor_all(0, |S_whole.OBJECTS|)',
                '$(S_whole.DESTRUCTION.INDEX < S_whole.DESTRUCTION.NEXT)',
                '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))']
        else:
            assertions += ['S_whole.COMPLETION = NORMAL', 'S_whole.EXITSTATUS = 0',
                           'S_whole.DESTRUCTION.INDEX = S_whole.DESTRUCTION.NEXT'] + public('S_whole')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / f'{case}-error-transfer.watsup'
        path.write_text(PREFIX + QUIET + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join(('  -- ' if condition.startswith('PhpStep:') else '  -- if ') + condition + '\n'
                                for condition in assertions))
        records.append({'id': case + '-error-transfer', 'source_id': case,
                        'fixture': str(path.resolve()), 'fixture_sha256': sha(path),
                        'assertions': len(assertions), 'public_refusals': 0})
    manifest = {'revision': HEAD, 'source_revision': SOURCE_HEAD,
                'source_reports': [{'path': str(report_path.resolve()), 'sha256': REPORT_SHA}],
                'producer_sha256': sha(Path(__file__)), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'public_refusals': 0,
                'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('fixtures', 'assertions', 'public_refusals')}))


if __name__ == '__main__':
    main()
