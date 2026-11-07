"""Emit source-reached owner, Notice-authenticity and budget checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from positional_reference_notice_review_cases import CASES, SOURCE_KIND_CONTROLS

PREFIX = r'''
dec $prn_stage(pstate, nat) : bool
dec $prn_find(pstate, nat, nat) : pstate
def $prn_find(S, n, n_stage) = S -- if $prn_stage(S, n_stage)
def $prn_find(S, n, n_stage) = $prn_find(S_next[.COMPLETION = NORMAL], n_next, n_stage)
  -- if ~$prn_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL
  -- if $(n > 0)
  -- if n_next = $(n - 1)
  -- if S_next = $drive_steps(S, 1)
dec $prn_resume(pstate, nat) : pstate
def $prn_resume(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $prn_resume(S, n) = $drive(S, n) -- if S.COMPLETION = NORMAL
def $prn_resume(S, n) = S -- otherwise
dec $prn_event(pevent) : preqbytes
def $prn_event(OUTPUT n*) = n*
def $prn_event(pevent) = eps -- otherwise
dec $prn_outputs(pevent*) : preqbytes
def $prn_outputs(eps) = eps
def $prn_outputs(pevent :: pevent_tail*) = $prn_event(pevent) ++ $prn_outputs(pevent_tail*)
dec $prn_diagnostic(pevent) : pevent*
def $prn_diagnostic(DIAGNOSTIC text n* z) = [DIAGNOSTIC text n* z]
def $prn_diagnostic(pevent) = eps -- otherwise
dec $prn_diagnostics(pevent*) : pevent*
def $prn_diagnostics(eps) = eps
def $prn_diagnostics(pevent :: pevent_tail*) = $prn_diagnostic(pevent) ++ $prn_diagnostics(pevent_tail*)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['all_pass'] and report['mode'] == 'SL'
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == (CASES | SOURCE_KIND_CONTROLS).keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(case, stages, checks):
        row = rows[case]
        source = Path(row['source'])
        assert source.read_bytes() == CASES[case]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        checked = json.loads((args.raw / case / 'checked.json').read_text())
        assert checked['ok'] and checked['fixture']
        stage_text = ''.join(f'def $prn_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $prn_stage(S, n_stage) = false -- otherwise\n'
        filename = base64.b64encode(bytes(source)).decode()
        common = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
                  'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]']
        assertions = common + checks
        path = args.output / (case + '.watsup')
        path.write_text(PREFIX + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'assertions': len(assertions), 'mode': 'AL'})

    alias = 'positional-prior-sent-cell-outlives-handler-rebinding'
    stages = {
        0: ['S.TODO = (CALL_SEND pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*',
            'S.RESULT = KNOWN (PINT 7)'],
        1: ['S.TODO = (RETURN_VALUE z) :: ptask_tail*', 'S.RESULT = KNOWN (PBOOL true)',
            'S.CURRENT = (pcallcontext)',
            '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
            'pfunction.NAME = $ptascii("h")', '$prn_outputs(S.EVENTS) = $ptascii("P;H;")'],
        2: ['S.TODO = (CALL_ARGS pcalltarget eps 2 poperand* porigin? z) :: ptask_tail*',
            '$prn_outputs(S.EVENTS) = $ptascii("P;H;")'],
        3: ['S.TODO = ACQUIRE_CALL :: ptask_tail*', 'S.RESULT = REFERENCE n',
            '$prn_outputs(S.EVENTS) = $ptascii("P;H;F:4:9;")'],
    }
    checks = ['S = $prn_find(S_start, 1000, 0)', '$prn_stage(S, 0)',
        'S.TODO = (CALL_SEND pcalltarget eps 1 poperand* (porigin_call) z_call) :: ptask_tail*',
        'poperand* = [REFERENCE n_kept]',
        '$lookup(S.ENV, $ptascii("x")) = (n_kept)', '$lookup(S.ENV, $ptascii("keep")) = (n_kept)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)', 'n_kept =/= n_replacement',
        'S.STORE[n_kept] = DEFINED (PINT 3)', 'S.STORE[n_replacement] = DEFINED (PINT 40)',
        '$heap_owners($heap_graph(S), HCELL n_kept) = 3',
        '$positional_reference_notice_pending(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_next = $drive_steps(S, 1)', 'S_next.COMPLETION = BUDGET',
        'S_notice = S_next[.COMPLETION = NORMAL]',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'n_warn = |S.STORE|', 'n_kept =/= n_warn',
        'perrorcall.RESUME = CALL_ARGS pcalltarget eps 2 ([REFERENCE n_kept, REFERENCE n_warn]) (porigin_call) z_call',
        'S_notice.STORE[n_warn] = DEFINED (PINT 7)', 'n_warn <- S_notice.REFCELLS',
        '(HCELL n_warn) <- S_notice.ALLOCATIONS', '$heap_owners($heap_graph(S_notice), HCELL n_warn) = 1',
        '$heap_owners($heap_graph(S_notice), HCELL n_kept) = 3',
        '$task_nodes(perrorcall.RESUME) = [HCELL n_kept, HCELL n_warn]',
        'S_notice.RESULT = KNOWN PNULL', 'S_notice.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_notice.HELD = S.HELD', '$error_call_valid(S_notice, perrorcall)',
        'S_notice.ORIGIN = (porigin_call)',
        '~$error_call_valid(S_notice[.ORIGIN = eps], perrorcall)',
        '$call_argument_origin(S_notice, (porigin_call), 1) = (porigin_argument)',
        '$exit_fixed(S_notice, porigin_argument) = ((preqbytes_producer, eps))',
        '$positional_reference_notice_source(S_notice, pcalltarget, 1, (porigin_call))',
        '~$positional_reference_notice_source(S_notice, pcalltarget, 0, (porigin_call))',
        '$call_descriptors_valid(S_notice)', '$heap_valid($heap_graph(S_notice))']
    for mutation in ['perrorcall[.LEVEL = 2]',
                     'perrorcall[.RESUME = CALL_ARGS pcalltarget eps 3 ([REFERENCE n_kept, REFERENCE n_warn]) (porigin_call) z_call]',
                     'perrorcall[.RESUME = CALL_ARGS pcalltarget eps 2 ([REFERENCE n_warn]) (porigin_call) z_call]', 'perrorcall[.LINE = $(perrorcall.LINE + 1)]',
                     'perrorcall[.MESSAGE = $ptascii("forged")]',
                     'perrorcall[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE]',
                     'perrorcall[.SITE = porigin_argument]',
                     'perrorcall[.RESUME = CALL_ARGS pcalltarget eps 0 eps (porigin_call) z_call]',
                     'perrorcall[.RESUME = CALL_ARGS pcalltarget eps 2 ([REFERENCE n_kept, KNOWN (PINT 7)]) (porigin_call) z_call]']:
        checks.append('~$error_call_valid(S_notice, ' + mutation + ')')
    checks += ['S_bad = S_notice[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.LEVEL = 2])) :: ptask_tail*]',
        '~$call_descriptors_valid(S_bad)', 'S_rejected = $drive(S_bad, 0)',
        'S_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'S_handler = $prn_find(S_notice, 1000, 1)', '$prn_stage(S_handler, 1)',
        'S_handler.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_replacement)',
        '$lookup(psymboltable.ENV, $ptascii("replacement")) = (n_replacement)',
        '$lookup(psymboltable.ENV, $ptascii("keep")) = eps', 'S_handler.STORE[n_kept] = DEFINED (PINT 3)',
        '$heap_owners($heap_graph(S_handler), HCELL n_kept) = 1',
        '$heap_owners($heap_graph(S_handler), HCELL n_warn) = 1',
        '$call_descriptors_valid(S_handler)', '$heap_valid($heap_graph(S_handler))',
        'S_resume = $prn_find(S_handler, 1000, 2)', '$prn_stage(S_resume, 2)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_tail*',
        'S_resume.STORE[n_kept] = DEFINED (PINT 3)', 'S_resume.STORE[n_warn] = DEFINED (PINT 7)',
        '$heap_owners($heap_graph(S_resume), HCELL n_kept) = 1',
        '$heap_owners($heap_graph(S_resume), HCELL n_warn) = 1',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'S_returned = $prn_find(S_resume, 1000, 3)', '$prn_stage(S_returned, 3)',
        'S_returned.RESULT = REFERENCE n_kept', 'S_returned.STORE[n_kept] = DEFINED (PINT 4)',
        '$heap_owners($heap_graph(S_returned), HCELL n_kept) = 1',
        '~((HCELL n_warn) <- S_returned.ALLOCATIONS)', '$heap_owners($heap_graph(S_returned), HCELL n_warn) = 0',
        '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
        'S_zero = $drive(S_notice, 0)', 'S_zero.COMPLETION = BUDGET', 'S_zero.TODO = S_notice.TODO',
        'S_one = $prn_resume(S_zero, 1)', 'S_split = $prn_resume(S_one, 3000)',
        'S_full = $drive(S_notice, 3001)', 'S_split = S_full', 'S_full.COMPLETION = NORMAL',
        '$prn_outputs(S_full.EVENTS) = $ptascii("P;H;F:4:9;R:11:40:40:1;")',
        '$prn_diagnostics(S_full.EVENTS) = eps', 'S_full.CURRENT = eps', 'S_full.FRAMES = eps',
        'S_full.TODO = eps', 'S_full.HELD = eps', 'S_full.RETIREDOWNERS = eps',
        '$call_descriptors_valid(S_full)', '$heap_valid($heap_graph(S_full))']
    fixture(alias, stages, checks)

    fallback = 'positional-false-handler-keeps-emitted-send-line'
    stages = {0: ['S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
                  'S.RESULT = KNOWN (PBOOL false)', '$prn_outputs(S.EVENTS) = $ptascii("P;H:8;")'],
              1: ['S.TODO = (CALL_ARGS pcalltarget phpType7* 1 poperand* porigin? z) :: ptask_tail*',
                  '$prn_outputs(S.EVENTS) = $ptascii("P;H:8;")']}
    checks = ['S = $prn_find(S_start, 1000, 0)', '$prn_stage(S, 0)',
        'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*', 'perrorcall.LINE = 8',
        'perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* 1 poperand* (porigin_call) 7',
        'poperand* = [REFERENCE n_warn]',
        'S.STORE[n_warn] = DEFINED (PINT 7)', '$heap_owners($heap_graph(S), HCELL n_warn) = 1',
        '$prn_diagnostics(S.EVENTS) = eps', '$error_call_valid(S, perrorcall)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_resume = $prn_find(S, 1000, 1)', '$prn_stage(S_resume, 1)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_tail*', 'S_resume.STORE[n_warn] = DEFINED (PINT 7)',
        '$heap_owners($heap_graph(S_resume), HCELL n_warn) = 1',
        '$prn_diagnostics(S_resume.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 8]',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET', 'S_zero.TODO = S.TODO',
        'S_one = $prn_resume(S_zero, 1)', 'S_split = $prn_resume(S_one, 3000)',
        'S_full = $drive(S, 3001)', 'S_split = S_full', 'S_full.COMPLETION = NORMAL',
        '$prn_outputs(S_full.EVENTS) = $ptascii("P;H:8;T;F:7:9;R:20;")',
        '$prn_diagnostics(S_full.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 8]',
        'S_full.CURRENT = eps', 'S_full.FRAMES = eps', 'S_full.TODO = eps',
        'S_full.HELD = eps', 'S_full.RETIREDOWNERS = eps',
        '$call_descriptors_valid(S_full)', '$heap_valid($heap_graph(S_full))']
    fixture(fallback, stages, checks)
    (args.output / 'manifest.json').write_text(json.dumps({'source_revision': report['revision'],
        'source_mode': 'SL', 'fixture_mode': 'AL', 'records': records}, indent=2) + '\n')
    print(args.output, sum(row['assertions'] for row in records), flush=True)


if __name__ == '__main__':
    main()
