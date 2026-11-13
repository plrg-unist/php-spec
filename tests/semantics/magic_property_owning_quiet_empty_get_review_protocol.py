#!/usr/bin/env python3
"""Check owning Empty return disposal, exception replacement and receiver aliases."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_owning_quiet_empty_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''
syntax powningreviewstage = OW_DTOR nat | OW_RV_THROW | OW_CATCH

dec $owning_review_stage(pstate,powningreviewstage) : bool
def $owning_review_stage(S,OW_DTOR n_object) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_object
def $owning_review_stage(S,OW_RV_THROW) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
def $owning_review_stage(S,OW_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $owning_review_stage(S,powningreviewstage) = false -- otherwise

dec $owning_review_seek(pstate,powningreviewstage,nat) : pstate
def $owning_review_seek(S,powningreviewstage,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $owning_review_seek(S,powningreviewstage,n) = S
  -- if $owning_review_stage(S,powningreviewstage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $owning_review_seek(S,powningreviewstage,0) = S
  -- if ~$owning_review_stage(S,powningreviewstage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $owning_review_seek(S,powningreviewstage,n) = $owning_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),powningreviewstage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$owning_review_stage(S,powningreviewstage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $owning_review_after(pstate,pstate) : pstate
def $owning_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))

dec $owning_review_output(pevent*) : ptbytes
def $owning_review_output(eps) = eps
def $owning_review_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $owning_review_output(pevent*)
'''

COMMON = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
n_receiver = ppropertyempty.OBJECT
$property_get_method(S,n_receiver) = (pmethoddesc)
pfunction = pmethoddesc.FUNCTION
pfunction.ORIGIN = ppropertyempty.GET /\ ~pfunction.SIGNATURE.BYREF
pfunction.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ ~psparam.VARIADIC
$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)
$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\ pclassdesc.PARENT = eps
pfunction.ORIGIN = PORIGIN n_unit pcpath_method
$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)
ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}
$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps
$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
~$property_empty_get_source(S,pmethoddesc)
~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)
~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])
$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)
$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_empty_source(S[.SOURCES = eps],ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_empty_source(S,ppropertyempty.SITE,$(ppropertyempty.LINE + 1))
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
$property_empty_rv_ready(S,ppropertyempty)
$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)
~$property_empty_capture(S,ppropertyempty)
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_reader] = DEFINED PNULL
S.STORE[n_selector] = DEFINED pvalue_selector
S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

ARRAY = COMMON + r'''
ppropertyempty.NAME = $ptascii("items")
$ptlc($base64(text_return)) = $ptascii("array") /\ pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
~pfunction.CODE.STRICT /\ pfunction.ENDLINE = 7
"string" <- $ptmasks(psparam.TYPE) /\ "null" <- $ptmasks(psparam.TYPE)
$string_bytes(pvalue_selector) = ($ptascii("items"))
$lookup(S.ENV,$ptascii("destination")) = (n_destination)
S.STORE[n_destination] = DEFINED (PINT 42)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]
S.OBJECTS[n_payload] = INSTANCE porigin_payload
n_payload =/= n_receiver
~$array_immutable(S,n_array) /\ $property_empty_truth(S,PARRAY n_array) = eps
$heap_owners($heap_graph(S),HARRAY n_array) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_array)],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PARRAY (|S.ARRAYS|)))
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_cached_raw),HARRAY n_array) = 0 /\ $heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_one.EVENTS = S.EVENTS /\ S_one.STORE[n_destination] = DEFINED (PINT 42)
S_payload_found = $owning_review_seek(S_one[.COMPLETION = NORMAL],OW_DTOR n_payload,2000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
S_payload.CURRENT = (pcallcontext_payload)
$destructor_context_call(pcallcontext_payload,S_payload.CURRENT,S_payload.FRAMES) = (pdestructorcall_payload)
pdestructorcall_payload.OPERATION = (pdestructionoperation_payload)
pdestructionoperation_payload.SOURCE = PROPERTY_EMPTY_RESULT ppropertyempty true
pdestructionoperation_payload.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation_payload.PENDING = eps
~((HARRAY n_array) <- S_payload.ALLOCATIONS) /\ (HOBJECT n_payload) <- S_payload.ALLOCATIONS
$heap_owners($heap_graph(S_payload),HOBJECT n_receiver) = 1
$property_empty_guard(S_payload,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S_payload,n_receiver,ppropertyempty.NAME)
S_payload.EVENTS = S.EVENTS /\ S_payload.STORE[n_destination] = DEFINED (PINT 42)
S_throw_found = $owning_review_seek(S_payload,OW_RV_THROW,2000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_payload_error) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps
$throwable_live(S_throw,n_payload_error)
$string_bytes($throwable_field(S_throw,n_payload_error,"message")) = ($ptascii("payload-array"))
$throwable_field(S_throw,n_payload_error,"line") = PINT 3 /\ $throwable_field(S_throw,n_payload_error,"previous") = PNULL
~((HARRAY n_array) <- S_throw.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_throw.ALLOCATIONS)
$heap_owners($heap_graph(S_throw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_throw,ppropertyemptyrv) /\ $property_empty_guard(S_throw,n_receiver,ppropertyempty.NAME)
S_throw.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("PAYLOAD;")]
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_payload_error) :: ptask_tail*
S_release_raw.COMPLETION = NORMAL /\ S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_release_raw.EVENTS = S_throw.EVENTS /\ S_release_raw.STORE = S_throw.STORE
$heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 0
~$property_empty_guard(S_release_raw,n_receiver,ppropertyempty.NAME)
S_release = $owning_review_after(S_throw,S_release_raw)
S_receiver_found = $owning_review_seek(S_release,OW_DTOR n_receiver,2000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_payload_error
pdestructionoperation_receiver.PENDING = (n_payload_error) /\ pdestructionoperation_receiver.VALUE = KNOWN PNULL
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
S_receiver.EVENTS = S_throw.EVENTS /\ S_receiver.STORE[n_destination] = DEFINED (PINT 42)
$throwable_field(S_receiver,n_payload_error,"previous") = PNULL
S_catch_found = $owning_review_seek(S_receiver,OW_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*
S_catch.CURRENT = eps /\ S_catch.FRAMES = eps
$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)
$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_payload_error
$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("receiver-array"))
$throwable_field(S_catch,n_receiver_error,"line") = PINT 8 /\ $throwable_field(S_catch,n_payload_error,"previous") = PNULL
$owning_review_output(S_catch.EVENTS) = $ptascii("I;G;PAYLOAD;RECEIVER;")
PhpStep: S_catch ~> S_bound_raw
S_bound = $owning_review_after(S_catch,S_bound_raw)
$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)
S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)
(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\ (HOBJECT n_payload_error) <- S_bound.ALLOCATIONS
~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)
S_done = $drive_steps(S_bound,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;RECEIVER;receiver-array;payload-array;ROOT;KEEP;CLEARED;NAME_KEEP;DONE;")
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_destination] = DEFINED (PINT 42) /\ S_done.STORE[n_selector] = DEFINED pvalue_selector
S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\ S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps
$lookup(S_done.ENV,$ptascii("failure")) = eps
~((HARRAY n_array) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_payload_error) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S,4096) = S_done
'''.strip().splitlines()

OBJECT = COMMON + r'''
ppropertyempty.NAME = $ptascii("self")
$ptlc($base64(text_return)) = $ptascii("object") /\ pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
pfunction.CODE.STRICT /\ pfunction.ENDLINE = 5 /\ psparam.TYPE = eps
S.RESULT = KNOWN (POBJECT n_receiver)
$string_bytes(pvalue_selector) = ($ptascii("changed"))
~$property_magic_name_capture(S,ppropertyempty.SITE,ppropertyempty.LINE,ppropertyempty.NAME)
$eager_property_class_valid(S,S.OBJECTS[n_receiver]) /\ ~$instance_storage_freeing(S,n_receiver)
$property_empty_truth(S,POBJECT n_receiver) = eps
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))
~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_receiver)],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_receiver] = WEAKMAP eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_cached_raw.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]
pdestructionoperation.SOURCE = PROPERTY_EMPTY_RESULT ppropertyempty true
pdestructionoperation.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation.PENDING = eps
$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2 /\ S_one.EVENTS = S.EVENTS
S_ready_found = $drive_steps(S_one[.COMPLETION = NORMAL],3)
S_ready_found.COMPLETION = BUDGET
S_ready = S_ready_found[.COMPLETION = NORMAL]
S_ready.TODO = S_cached_raw.TODO /\ S_ready.RESULT = KNOWN (PBOOL false)
$heap_owners($heap_graph(S_ready),HOBJECT n_receiver) = 1 /\ S_ready.EVENTS = S.EVENTS
$property_empty_rv_valid(S_ready,ppropertyemptyrv) /\ $property_empty_guard(S_ready,n_receiver,ppropertyempty.NAME)
~$property_empty_guard(S_ready,n_receiver,$ptascii("changed"))
PhpStep: S_ready ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL false) /\ S_release_raw.EVENTS = S.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 0
~$property_empty_guard(S_release_raw,n_receiver,ppropertyempty.NAME)
S_release = $owning_review_after(S_ready,S_release_raw)
S_receiver_found = $owning_review_seek(S_release,OW_DTOR n_receiver,2000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
pdestructionoperation_receiver.SOURCE = PROPERTY_EMPTY_RV ppropertyemptyrv
pdestructionoperation_receiver.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation_receiver.PENDING = eps
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
S_receiver.EVENTS = S.EVENTS /\ S_receiver.STORE[n_reader] = DEFINED PNULL /\ S_receiver.STORE[n_selector] = DEFINED pvalue_selector
S_done = $drive_steps(S_receiver,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
$owning_review_output(S_done.EVENTS) = $ptascii("I;G;RECEIVER;OBJECT;CLEARED;NAME_CHANGED;DONE;")
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_selector
S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\ S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S,4096) = S_done
'''.strip().splitlines()

CASES = {
    'array-empty-cached-false-payload-and-receiver-replacement': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* -- if S.RESULT = KNOWN (PARRAY n_array)',
        'checks': ARRAY,
    },
    'object-empty-self-alias-and-saved-name-release': {
        'source': ROWS[1]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_receiver)',
        'checks': OBJECT,
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
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), runner_flags=('--sl',), fixture_renderer=render)
