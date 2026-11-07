"""Emit genuine named default-line, receipt and duplicate-priority checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from default_reference_line_review_cases import CASES
from reference_send_notice_review_state import PREFIX


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['all_pass'] and report['source_agreements'] == 2 and report['mode'] == 'SL'
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == CASES.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def emit(case, checks, derived=()):
        row = rows[case]
        source = Path(row['source'])
        assert source.read_bytes() == CASES[case]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        checked = json.loads((args.raw / case / 'checked.json').read_text())
        assert checked['ok'] and checked['fixture']
        stages = r'''
def $rsn_stage(S, 0) = true
  -- if S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 5)
  -- if $rsn_outputs(S.EVENTS) = $ptascii("P:4;")
def $rsn_stage(S, n_stage) = false -- otherwise
'''
        filename = base64.b64encode(bytes(source)).decode()
        common = [
            'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
            'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]',
            'S = $rsn_find(S_start, 1000, 0)', '$rsn_stage(S, 0)',
            'S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*',
            '~$error_handler_eligible(S, 8)', 'S.SOURCEPENDING = eps',
            r'S.CURRENT = eps /\ S.FRAMES = eps',
            '$lookup(S.ENV, $ptascii("x")) = (n_original)',
            '$lookup(S.ENV, $ptascii("hold")) = (n_original)',
            'S.STORE[n_original] = DEFINED (PINT 5)',
            '$heap_owners($heap_graph(S), HCELL n_original) = 3',
            'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_original)]',
            '$named_reference_notice_arguments(S, pnamedargs)',
            '$named_reference_notice_source(S, pcalltarget, 1, (porigin_call))',
            '$named_origin(S, (porigin_call), 1) = (porigin_producer)',
            '$named_expression($named_source(S, (porigin_call), 1)) = expression_producer',
            '$lookup(S.ENV, $ptascii("r")) = (n_target)',
            'S.STORE[n_target] = DEFINED (PINT 900)',
            r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
        ]
        conditions = common + checks + list(derived)
        path = args.output / (case + '.watsup')
        path.write_text(PREFIX + stages + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join(('  -- ' if condition.startswith('PhpStep: ') else '  -- if ') +
                                condition + '\n' for condition in conditions))
        records.append({'id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'assertions': len(conditions),
                        'source_reached_conditions': len(conditions) - len(derived),
                        'derived_guard_conditions': len(derived), 'mode': 'AL'})

    checks = r'''
z_call = 7
$runtime_line(S[.ORIGIN = (porigin_producer)], eps, expression_producer) = 9
$reference_notice_producer_line(S, (porigin_producer), expression_producer) = 10
$named_line(S, (porigin_call), 1) = 10
n_private = |S.STORE|
n_private =/= n_original
S_step = $drive(S, 1)
S_step.COMPLETION = BUDGET
S_next = S_step[.COMPLETION = NORMAL]
S_next.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs_next (porigin_call) 7) :: ptask_tail*
S_next.CURRENT = eps /\ S_next.FRAMES = eps
S_next.RESULT = KNOWN PNULL /\ S_next.BASE = BASE_VALUE (KNOWN PNULL)
pnamedargs_next.SLOTS = [NAMED_SENT (REFERENCE n_original)]
pnamedargs_next.NAMED = [($ptascii("tail"), REFERENCE n_private)]
S_next.STORE[n_private] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_next), HCELL n_private) = 1
$heap_owners($heap_graph(S_next), HCELL n_original) = 3
$task_nodes(NAMED_ARGS pcalltarget eps 2 pnamedargs_next (porigin_call) 7) = [HCELL n_original, HCELL n_private]
S_next.STORE[n_target] = DEFINED (PINT 900)
$rsn_outputs(S_next.EVENTS) = $ptascii("P:4;")
$rsn_diagnostics(S_next.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 10]
$call_descriptors_valid(S_next) /\ $heap_valid($heap_graph(S_next))
$named_line(S_next, (porigin_call), 1) = 9
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one = $rsn_resume(S_zero, 1)
S_one = S_step
S_two = $rsn_resume(S_one, 1)
S_two.COMPLETION = BUDGET
S_direct = $drive(S, 2)
S_two = S_direct
'''.strip().splitlines()
    derived = r'''
S_raw = S[.RESULT = KNOWN (PSTRING ($ptascii("raw")))]
$named_line(S_raw, (porigin_call), 1) = 9
S_ref = S[.RESULT = REFERENCE n_original]
$named_line(S_ref, (porigin_call), 1) = 9
pnamedargs_raw = pnamedargs[.SLOTS = [NAMED_SENT (KNOWN (PSTRING ($ptascii("raw"))))]]
S_prior = S[.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs_raw (porigin_call) 7) :: ptask_tail*]
$named_line(S_prior, (porigin_call), 1) = 9
$named_line(S, (porigin_call), 0) = $runtime_line(S[.ORIGIN = $named_origin(S, (porigin_call), 0)], eps, $named_expression($named_source(S, (porigin_call), 0)))
'''.strip().splitlines()
    emit('named-default-producer-cv', checks, derived)
    checks = r'''
z_call = 6
$runtime_line(S[.ORIGIN = (porigin_producer)], eps, expression_producer) = 8
$reference_notice_producer_line(S, (porigin_producer), expression_producer) = 9
$named_line(S, (porigin_call), 1) = 9
$target_function(S, pcalltarget) = (pfunction)
pnamedtarget = $named_arg_target(pfunction, $named_source(S, (porigin_call), 1), 1)
~$named_can_store(pnamedargs, pnamedtarget)
$rsn_diagnostics(S.EVENTS) = eps
n_unstored = |S.STORE|
PhpStep: S ~> S_error
S_error.COMPLETION = THROWN "Error" ($ptascii("Named parameter $head overwrites previous argument")) 9
S_error.STORE = S.STORE
S_error.OBJECTS = S.OBJECTS
S_error.ALLOCATIONS = S.ALLOCATIONS
~((HCELL n_unstored) <- S_error.ALLOCATIONS)
S_error.STORE[n_original] = DEFINED (PINT 5)
S_error.STORE[n_target] = DEFINED (PINT 900)
$rsn_outputs(S_error.EVENTS) = $ptascii("P:4;")
$rsn_diagnostics(S_error.EVENTS) = eps
$call_descriptors_valid(S_error) /\ $heap_valid($heap_graph(S_error))
'''.strip().splitlines()
    # A raw rule step observes the error before the generic throw-search driver.
    emit('named-default-producer-cv-duplicate', checks)
    (args.output / 'manifest.json').write_text(json.dumps({
        'source_revision': report['revision'], 'source_mode': 'SL',
        'fixture_mode': 'AL', 'records': records}, indent=2) + '\n')
    print(args.output, sum(row['assertions'] for row in records), flush=True)


if __name__ == '__main__':
    main()
