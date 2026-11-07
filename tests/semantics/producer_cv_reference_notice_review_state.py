"""Emit actual producer-formal, saved-cell and Notice-line checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from producer_cv_reference_notice_review_cases import CASES
from reference_send_notice_review_state import PREFIX


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['all_pass'] and report['mode'] == 'SL'
    assert report['source_agreements'] == 3
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == CASES.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def emit(case, stages, checks, derived=()):
        row = rows[case]
        source = Path(row['source'])
        assert source.read_bytes() == CASES[case]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        checked = json.loads((args.raw / case / 'checked.json').read_text())
        assert checked['ok'] and checked['fixture']
        text = ''.join(f'def $rsn_stage(S, {index}) = true\n' +
                       ''.join('  -- if ' + condition + '\n' for condition in conditions)
                       for index, conditions in stages.items())
        text += 'def $rsn_stage(S, n_stage) = false -- otherwise\n'
        filename = base64.b64encode(bytes(source)).decode()
        common = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
                  'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]']
        assertions = common + checks + list(derived)
        path = args.output / (case + '.watsup')
        path.write_text(PREFIX + text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'assertions': len(assertions),
                        'source_reached_conditions': len(assertions) - len(derived),
                        'derived_guard_conditions': len(derived), 'mode': 'AL'})

    stages = {
        0: ['S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("make")',
            'S.TODO = (RETURN_UNWIND (KNOWN (PINT 5)) porigin?) :: ptask_tail*',
            '$rsn_outputs(S.EVENTS) = $ptascii("P:4;")'],
        1: ['S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*',
            'S.RESULT = KNOWN (PINT 5)'],
        2: ['S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*',
            '$rsn_outputs(S.EVENTS) = $ptascii("P:4;H;")'],
        3: ['S.TODO = ACQUIRE_CALL :: ptask_tail*', 'S.RESULT = REFERENCE n',
            '$rsn_outputs(S.EVENTS) = $ptascii("P:4;H;F:51:105;")'],
    }
    checks = r'''
S_producer = $rsn_find(S_start, 1000, 0)
$rsn_stage(S_producer, 0)
$lookup(S_producer.ENV, $ptascii("input")) = (n_original)
S_producer.STORE[n_original] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_producer), HCELL n_original) = 4
$call_descriptors_valid(S_producer) /\ $heap_valid($heap_graph(S_producer))
S_pre = $rsn_find(S_producer, 1000, 1)
$rsn_stage(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_original)]
pnamedargs.NAMED = eps
$lookup(S_pre.ENV, $ptascii("x")) = (n_original)
$lookup(S_pre.ENV, $ptascii("hold")) = (n_original)
$lookup(S_pre.ENV, $ptascii("other")) = (n_other)
n_original =/= n_other
S_pre.STORE[n_original] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_pre), HCELL n_original) = 3
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$named_reference_notice_pending(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE phpType7_producer*) metadata_call
phpType7_producer* = [NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_arg]
expression_input = NExprVariable (BYTES text_input) metadata_input
$reference_cv(expression_input) = ($ptascii("x"))
$exit_fixed(S_pre, porigin_producer) = ((preqbytes_producer, eps))
$call_target(S_pre, preqbytes_producer, eps) = (pfunction_producer)
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16_parameters phpType18 phpType23 metadata_function)
$reference_notice_producer_arguments(SEQUENCE phpType7_producer*, phpType16_parameters, pfunction_producer.SIGNATURE)
n_private = |S_pre.STORE|
n_private =/= n_original
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_original)]
pnamedargs_after.NAMED = [($ptascii("tail"), REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_notice), HCELL n_original) = 3
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$task_nodes(perrorcall.RESUME) = [HCELL n_original, HCELL n_private]
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_resume = $rsn_find(S_notice, 1000, 2)
$rsn_stage(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("x")) = (n_other)
$lookup(S_resume.ENV, $ptascii("hold")) = eps
S_resume.STORE[n_original] = DEFINED (PINT 41)
S_resume.STORE[n_other] = DEFINED (PINT 9)
S_resume.STORE[n_private] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_resume), HCELL n_original) = 1
$heap_owners($heap_graph(S_resume), HCELL n_private) = 1
$named_reference_notice_source(S_resume, pcalltarget, 1, (porigin_call))
$error_call_valid(S_resume, perrorcall) /\ $call_descriptors_valid(S_resume)
$heap_valid($heap_graph(S_resume))
S_returned = $rsn_find(S_resume, 1000, 3)
$rsn_stage(S_returned, 3)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PINT 105)
$heap_owners($heap_graph(S_returned), HCELL n_private) = 1
$heap_owners($heap_graph(S_returned), HCELL n_original) = 0
~((HCELL n_original) <- S_returned.ALLOCATIONS)
$call_descriptors_valid(S_returned) /\ $heap_valid($heap_graph(S_returned))
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $rsn_resume(S_zero, 1)
S_one.COMPLETION = BUDGET
S_two = $rsn_resume(S_one, 1)
S_two.COMPLETION = BUDGET
S_direct = $drive(S_notice, 2)
S_two = S_direct
S_full = $drive(S_returned, 5000)
S_full.COMPLETION = NORMAL
$rsn_outputs(S_full.EVENTS) = $ptascii("P:4;H;F:51:105;R:106:9:9:1;")
$rsn_diagnostics(S_full.EVENTS) = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT 106)
$lookup(S_full.ENV, $ptascii("x")) = (n_other)
$lookup(S_full.ENV, $ptascii("other")) = (n_other)
$lookup(S_full.ENV, $ptascii("hold")) = eps
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
'''.strip().splitlines()
    derived = r'''
expression_computed = NExprVariable (NScalarString (BYTES text_input) metadata_input) metadata_input
$reference_cv(expression_computed) = ($ptascii("x"))
~$reference_notice_producer_arguments(SEQUENCE ([NArg ABSENT expression_computed (BOOLEAN false) (BOOLEAN false) metadata_arg]), phpType16_parameters, pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([NArg (NIdentifier (BYTES text_input) metadata_arg) expression_input (BOOLEAN false) (BOOLEAN false) metadata_arg]), phpType16_parameters, pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN true) metadata_arg]), phpType16_parameters, pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE (phpType7_producer* ++ phpType7_producer*), phpType16_parameters, pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([NArg ABSENT (NExprVariable (BYTES "dGhpcw==") metadata_input) (BOOLEAN false) (BOOLEAN false) metadata_arg]), phpType16_parameters, pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([NArg ABSENT (NExprVariable (BYTES "R0xPQkFMUw==") metadata_input) (BOOLEAN false) (BOOLEAN false) metadata_arg]), phpType16_parameters, pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([NArg ABSENT (NExprVariable (BYTES "aHR0cF9yZXNwb25zZV9oZWFkZXI=") metadata_input) (BOOLEAN false) (BOOLEAN false) metadata_arg]), phpType16_parameters, pfunction_producer.SIGNATURE)
$reference_notice_producer_arguments(SEQUENCE eps, phpType16_parameters, pfunction_producer.SIGNATURE)
'''.strip().splitlines()
    emit('named-producer-cv-prior-cell', stages, checks, derived)

    stages = {
        0: ['S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("make")',
            'S.TODO = (RETURN_UNWIND (KNOWN (PINT 5)) porigin?) :: ptask_tail*'],
        1: ['S.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* porigin? z) :: ptask_tail*',
            'S.RESULT = KNOWN (PINT 5)'],
        2: ['S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
            'S.RESULT = KNOWN (PBOOL false)', '$rsn_outputs(S.EVENTS) = $ptascii("P:4;H:9;")'],
        3: ['S.TODO = (CALL_ARGS pcalltarget phpType7* 1 poperand* porigin? z) :: ptask_tail*',
            '$rsn_outputs(S.EVENTS) = $ptascii("P:4;H:9;")'],
    }
    checks = r'''
S_producer = $rsn_find(S_start, 1000, 0)
$rsn_stage(S_producer, 0)
$lookup(S_producer.ENV, $ptascii("input")) = (n_local)
S_producer.STORE[n_local] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_producer), HCELL n_local) = 1
$call_descriptors_valid(S_producer) /\ $heap_valid($heap_graph(S_producer))
S_pre = $rsn_find(S_producer, 1000, 1)
$rsn_stage(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* (porigin_call) 7) :: ptask_tail*
$lookup(S_pre.ENV, $ptascii("x")) = (n_source)
n_local =/= n_source
S_pre.STORE[n_source] = DEFINED (PINT 4)
$heap_owners($heap_graph(S_pre), HCELL n_local) = 0
~((HCELL n_local) <- S_pre.ALLOCATIONS)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_pending(S_pre)
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_producer)
$call_argument_expression(S_pre, (porigin_call), 0) = expression_producer
$runtime_line(S_pre[.ORIGIN = (porigin_producer)], eps, expression_producer) = 8
$reference_notice_producer_line(S_pre, (porigin_producer), expression_producer) = 9
n_private = |S_pre.STORE|
n_private =/= n_local /\ n_private =/= n_source
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* 1 ([REFERENCE n_private]) (porigin_call) 7
perrorcall.LINE = 9
S_notice.STORE[n_private] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_false = $rsn_find(S_notice, 1000, 2)
$rsn_stage(S_false, 2)
S_false.STORE[n_source] = DEFINED (PINT 40)
S_false.STORE[n_private] = DEFINED (PINT 5)
S_false.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_false*
perrorcall_entered.RESUME = perrorcall.RESUME
perrorcall_entered.LINE = 9
$call_descriptors_valid(S_false)
S_resume = $rsn_find(S_false, 1000, 3)
$rsn_stage(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
S_resume.STORE[n_private] = DEFINED (PINT 5)
$rsn_diagnostics(S_resume.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 9]
$call_descriptors_valid(S_resume) /\ $heap_valid($heap_graph(S_resume))
S_zero = $drive(S_false, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_false
S_one = $rsn_resume(S_zero, 1)
S_one.COMPLETION = BUDGET
S_two = $rsn_resume(S_one, 1)
S_two.COMPLETION = BUDGET
S_direct = $drive(S_false, 2)
S_two = S_direct
S_full = $drive(S_resume, 5000)
S_full.COMPLETION = NORMAL
$rsn_outputs(S_full.EVENTS) = $ptascii("P:4;H:9;T;F:105:9;R:106:40;")
$rsn_diagnostics(S_full.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 9]
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT 106)
~((HCELL n_local) <- S_full.ALLOCATIONS)
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
'''.strip().splitlines()
    derived = r'''
perrorcall_wrong = perrorcall[.LINE = 8][.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE 8]
~$error_call_valid(S_notice, perrorcall_wrong)
'''.strip().splitlines()
    emit('positional-producer-cv-false-line', stages, checks, derived)
    (args.output / 'manifest.json').write_text(json.dumps({
        'source_revision': report['revision'], 'source_mode': 'SL',
        'fixture_mode': 'AL', 'records': records}, indent=2) + '\n')
    print(args.output, sum(row['assertions'] for row in records), flush=True)


if __name__ == '__main__':
    main()
