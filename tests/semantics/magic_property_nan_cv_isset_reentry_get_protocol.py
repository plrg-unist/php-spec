#!/usr/bin/env python3
"""Check NaN Empty guards at authentic CV-name Isset entry."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_nan_cv_isset_reentry_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''
dec $nan_cv_name_stage(pstate,ptbytes) : bool
def $nan_cv_name_stage(S,ptbytes) = true
  -- if S.TODO = (PROPERTY_NAME (POBJECT n) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail*
  -- if $property_magic_cv_name(S,porigin,z) = (ptbytes)
def $nan_cv_name_stage(S,ptbytes) = false -- otherwise
dec $nan_cv_seek_name(pstate,ptbytes,nat) : pstate
def $nan_cv_seek_name(S,ptbytes,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_cv_seek_name(S,ptbytes,n) = S -- if $nan_cv_name_stage(S,ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_seek_name(S,ptbytes,0) = S -- if ~$nan_cv_name_stage(S,ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_seek_name(S,ptbytes,n) = $nan_cv_seek_name($drive_steps(S[.COMPLETION = NORMAL],1),ptbytes,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nan_cv_name_stage(S,ptbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $nan_cv_live_stage(pstate) : bool
def $nan_cv_live_stage(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps
  -- if $lookup(S.ENV,$ptascii("destination")) = (n)
  -- if S.STORE[n] = DEFINED (PBOOL false)
def $nan_cv_live_stage(S) = false -- otherwise
dec $nan_cv_seek_live(pstate,nat) : pstate
def $nan_cv_seek_live(S,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_cv_seek_live(S,n) = S -- if $nan_cv_live_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_seek_live(S,0) = S -- if ~$nan_cv_live_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_seek_live(S,n) = $nan_cv_seek_live($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nan_cv_live_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $nan_cv_after(pstate,pstate) : pstate
def $nan_cv_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))
'''

CASES = {
    'named-nan-empty-cv-isset-guard-name-and-resume': {
        'source': ROW['source'],
        'stage': ('S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z_first) :: '
                  '(ORIGIN_RETURN (porigin_first)) :: (ISSET_RESULT false z_first) :: ptask_first* '
                  '-- if $property_magic_cv_name(S,porigin_first,z_first) = (eps)'),
        'checks': [
            r'z_first = 12 /\ S.ORIGIN = (porigin_first)',
            r'S.RESULT = VARIABLE $ptascii("selector") z_first /\ S.BASE = BASE_VALUE (KNOWN PNULL)',
            r'S.CURRENT = (pcallcontext_handler)',
            r'S.FRAMES = [pframe_handler]',
            r'S.HELD = eps',
            r'pcallcontext_handler.TARGET = API_BORROWED_TARGET pshutdownproducer',
            r'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_outer*',
            r'perrorcall.RESUME = PROPERTY_EMPTY_NAN ppropertyemptynan',
            r'ppropertyempty = ppropertyemptynan.EMPTY',
            r'ppropertyempty.NAME = eps /\ ppropertyempty.OBJECT = n_receiver /\ ppropertyempty.LINE = 19',
            r'ppropertyemptynan.FLOAT = 9221120237041090560 /\ ppropertyemptynan.OWNER = 0 /\ ppropertyemptynan.CALLER = eps',
            r'S_caller = $constant_frame_scope(S,pframe_handler,eps)',
            r'$property_empty_nan_valid(S_caller,ppropertyemptynan) /\ $property_empty_valid(S_caller,ppropertyempty)',
            r'$property_empty_nan_guard(S,n_receiver,eps) /\ ~$property_empty_nan_guard(S,n_receiver,$ptascii("other"))',
            r'$property_isset_plan(S) = (ppropertyisset)',
            r'ppropertyisset.SITE = porigin_first /\ ppropertyisset.LINE = z_first /\ ppropertyisset.NAME = eps /\ ppropertyisset.OBJECT = n_receiver /\ ppropertyisset.PROPERTY = eps',
            r'$property_isset_source(S,ppropertyisset) /\ $property_isset_capture(S,ppropertyisset)',
            r'~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,eps)',
            r'$property_magic_cv_source(S,porigin_first,z_first)',
            r'$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
            r'$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
            r'$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
            r'$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            r'$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'S.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\ S.STORE[n_destination] = DEFINED (PINT 42)',
            r'$string_bytes(pvalue_selector) = (eps)',
            r'n_reader <- S.REFCELLS /\ n_selector <- S.REFCELLS',
            r'(HOBJECT n_receiver) <- S.ALLOCATIONS /\ ~$instance_storage_freeing(S,n_receiver)',
            r'$task_nodes(PROPERTY_NAME (POBJECT n_receiver) z_first) = [HOBJECT n_receiver]',
            r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 3',
            r'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;"),OUTPUT $ptascii("WARN;")]',
            r'$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))',
            r'$property_isset_plan(S[.SOURCES = eps]) = eps /\ ~$property_empty_nan_guard(S[.SOURCES = eps],n_receiver,eps)',
            r'$property_isset_plan(S[.ORIGIN = eps]) = eps',
            r'$property_isset_plan(S[.TODO = (PROPERTY_NAME (POBJECT n_receiver) 13) :: (ORIGIN_RETURN (porigin_first)) :: (ISSET_RESULT false 13) :: ptask_first*]) = eps',
            r'$property_isset_plan(S[.TODO = (PROPERTY_NAME (POBJECT n_receiver) z_first) :: (ORIGIN_RETURN (porigin_first)) :: (ISSET_RESULT true z_first) :: ptask_first*]) = eps',
            r'~$property_isset_capture(S,ppropertyisset[.NAME = $ptascii("other")])',
            r'PhpStep: S ~> S_guarded',
            r'S_guarded = S[.TODO = ptask_first*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            r'$heap_owners($heap_graph(S_guarded),HOBJECT n_receiver) = 2',
            r'$property_empty_nan_guard(S_guarded,n_receiver,eps)',
            r'$call_descriptors_valid(S_guarded) /\ $heap_valid($heap_graph(S_guarded))',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            r'S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $nan_cv_after(S,S_guarded)',
            r'S_other_found = $nan_cv_seek_name(S_one[.COMPLETION = NORMAL],$ptascii("other"),2000)',
            r'S_other_found.COMPLETION = NORMAL \/ S_other_found.COMPLETION = BUDGET',
            r'S_other = S_other_found[.COMPLETION = NORMAL]',
            r'S_other.TODO = (PROPERTY_NAME (POBJECT n_receiver) 14) :: (ORIGIN_RETURN (porigin_other)) :: (ISSET_RESULT false 14) :: ptask_other*',
            r'$property_isset_plan(S_other) = (ppropertyisset_other)',
            r'ppropertyisset_other.NAME = $ptascii("other") /\ ppropertyisset_other.OBJECT = n_receiver /\ ppropertyisset_other.SITE = porigin_other',
            r'$property_empty_nan_guard(S_other,n_receiver,eps) /\ ~$property_empty_nan_guard(S_other,n_receiver,ppropertyisset_other.NAME)',
            r'S_other.STORE[n_selector] = DEFINED pvalue_other',
            r'$string_bytes(pvalue_other) = ($ptascii("other"))',
            r'S_other.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("EMPTY_GUARD;")]',
            r'PhpStep: S_other ~> S_other_call',
            r'S_other_call.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset_other) eps 1 ([KNOWN (PSTRING $ptascii("other"))]) (porigin_other) 14) :: (PROPERTY_ISSET_RESULT ppropertyisset_other) :: ptask_other*',
            r'S_other_call.EVENTS = S_other.EVENTS /\ S_other_call.STORE = S_other.STORE',
            r'$heap_owners($heap_graph(S_other_call),HOBJECT n_receiver) = 3',
            r'$property_empty_nan_guard(S_other_call,n_receiver,eps)',
            r'S_again_found = $nan_cv_seek_name($nan_cv_after(S_other,S_other_call),eps,2000)',
            r'S_again_found.COMPLETION = NORMAL \/ S_again_found.COMPLETION = BUDGET',
            r'S_again = S_again_found[.COMPLETION = NORMAL]',
            r'S_again.TODO = (PROPERTY_NAME (POBJECT n_receiver) 16) :: (ORIGIN_RETURN (porigin_again)) :: (ISSET_RESULT false 16) :: ptask_again*',
            r'$property_isset_plan(S_again) = (ppropertyisset_again)',
            r'ppropertyisset_again.NAME = eps',
            r'$property_empty_nan_guard(S_again,n_receiver,eps) /\ $property_isset_capture(S_again,ppropertyisset_again)',
            r'S_again.EVENTS = S_other.EVENTS ++ [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("OTHER;")]',
            r'PhpStep: S_again ~> S_again_guarded',
            r'S_again_guarded = S_again[.TODO = ptask_again*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            r'$heap_owners($heap_graph(S_again_guarded),HOBJECT n_receiver) = 2',
            r'S_live_found = $nan_cv_seek_live($nan_cv_after(S_again,S_again_guarded),2000)',
            r'S_live_found.COMPLETION = NORMAL \/ S_live_found.COMPLETION = BUDGET',
            r'S_live = S_live_found[.COMPLETION = NORMAL]',
            r'S_live.STORE[n_destination] = DEFINED (PBOOL false) /\ S_live.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
            r'S_live.STORE[n_selector] = DEFINED pvalue_live',
            r'$string_bytes(pvalue_live) = (eps)',
            r'S_live.TODO =/= eps /\ S_live.CURRENT = eps /\ S_live.FRAMES = eps /\ S_live.HELD = eps',
            r'S_live.EVENTS = S_again.EVENTS ++ [OUTPUT $ptascii("EMPTY_GUARD_AGAIN;")]',
            r'~$property_empty_nan_guard(S_live,n_receiver,eps) /\ ~$property_empty_guard(S_live,n_receiver,eps)',
            r'$heap_owners($heap_graph(S_live),HOBJECT n_receiver) = 1',
            r'$call_descriptors_valid(S_live) /\ $property_state_valid(S_live) /\ $heap_valid($heap_graph(S_live))',
            r'S_done = $drive_steps(S_live,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.EVENTS = S_live.EVENTS ++ [OUTPUT $ptascii("FALSE;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("DONE;")]',
            r'~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            r'$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
            r'$drive_steps(S,4096) = S_done',
        ],
    },
}


def render(case, fixture, filename):
    stage = case['stage']
    text = (HELPERS + '\ndec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + stage + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate,nat) : pstate\n'
            'def $seek(S,n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'def $seek(S,n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) '
            '-- if $(n > 0) /\\ ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found = $seek(S_initial,2000)\n'
            '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            '  -- if S = S_found[.COMPLETION = NORMAL]\n'
            '  -- if ' + stage + '\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__), CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=render)
