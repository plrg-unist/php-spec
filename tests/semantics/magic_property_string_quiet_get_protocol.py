#!/usr/bin/env python3
"""Check quiet string Get conversion, byte identity and receiver retirement."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_string_quiet_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STRINGABLE_CATALOGUE = Path(__file__).with_name('magic_property_string_quiet_get_stringable_cases.json')
STRINGABLE_ROW = json.loads(STRINGABLE_CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(STRINGABLE_ROW['source'].encode()).hexdigest() == STRINGABLE_ROW['source_sha256']

HELPERS = r'''
dec $quiet_string_result(pstate,ptbytes) : bool
def $quiet_string_result(S,ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = (ptbytes)
def $quiet_string_result(S,ptbytes) = false -- otherwise
dec $quiet_string_seek_result(pstate,ptbytes,nat) : pstate
def $quiet_string_seek_result(S,ptbytes,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_string_seek_result(S,ptbytes,n) = S -- if $quiet_string_result(S,ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_string_seek_result(S,ptbytes,0) = S -- if ~$quiet_string_result(S,ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_string_seek_result(S,ptbytes,n) = $quiet_string_seek_result($drive_steps(S[.COMPLETION = NORMAL],1),ptbytes,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$quiet_string_result(S,ptbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CASES = {
    'string-empty-get-weak-zero-and-interned-nul': {
        'source': ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  r'-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  r'-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  r'-- if S.RESULT = KNOWN (PINT 0)'),
        'checks': [
            r'S.ORIGIN = (porigin_return)',
            r'z_return = 6',
            r'n_receiver = ppropertyempty.OBJECT',
            r'ppropertyempty.PROPERTY = eps /\ ppropertyempty.NAME = $ptascii("zero")',
            r'$property_get_method(S,n_receiver) = (pmethoddesc)',
            r'pfunction = pmethoddesc.FUNCTION',
            r'pfunction.ORIGIN = pcallcontext.FUNCTION /\ pfunction.ORIGIN = ppropertyempty.GET',
            r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))] /\ ~pfunction.SIGNATURE.BYREF /\ ~pfunction.CODE.STRICT',
            r'$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
            r'pclassdesc.NAME = $ptascii("QuietStringRead") /\ pclassdesc.PARENT = eps',
            r'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
            r'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            r'$ptlc($base64(text_return)) = $ptascii("string")',
            r'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
            r'$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            r'$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
            r'~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
            r'$property_quiet_get_source(S,pmethoddesc) /\ ~$property_empty_get_source(S,pmethoddesc)',
            r'$property_empty_method_source(S,pmethoddesc,true) /\ $property_coalesce_method_source(S,pmethoddesc,true)',
            r'~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
            r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
            r'$return_function_name(S,pfunction) = $ptascii("QuietStringRead::__get")',
            r'S.FRAMES = [pframe]',
            r'pframe.CONTEXT = eps /\ pframe.ORIGIN = (ppropertyempty.SITE)',
            r'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
            r'$property_empty_context(S,pcallcontext) /\ $property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
            r'$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
            r'$call_receiver_roots(pcallcontext) = eps /\ $target_nodes(pcallcontext.TARGET) = eps',
            r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            r'S_caller = $constant_frame_scope(S,pframe,eps)',
            r'$lookup(S_caller.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            r'$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            r'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'$string_bytes(pvalue_selector) = ($ptascii("zero"))',
            r'$typed_return_task_valid(S,z_return) /\ ~$typed_return_task_valid(S,$(z_return + 1))',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,false,false) = TYPESTRING (PINT 0)',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,true,false) = TYPEREJECT',
            r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            r'PhpStep: S ~> S_unwind',
            r'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))) (porigin_return)) :: ptask_return*',
            r'S_unwind.STORE = S.STORE /\ S_unwind.EVENTS = S.EVENTS /\ S_unwind.STRINGDATA = S.STRINGDATA',
            r'$value_nodes(PSTRING_CARRIER INTERNED_STRING ([48])) = eps',
            r'$heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 2',
            r'$call_descriptors_valid(S_unwind) /\ $property_state_valid(S_unwind) /\ $heap_valid($heap_graph(S_unwind))',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            r'S_one.COMPLETION = BUDGET /\ S_one.TODO = S_unwind.TODO /\ S_one.RESULT = S_unwind.RESULT',
            r'S_result_found = $quiet_string_seek_result(S_one[.COMPLETION = NORMAL],[48],2000)',
            r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
            r'S_result = S_result_found[.COMPLETION = NORMAL]',
            r'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_result*',
            r'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48])) /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps',
            r'$call_task_valid(S_result,PROPERTY_EMPTY_RESULT ppropertyempty true)',
            r'$property_magic_cv_source(S_result,ppropertyempty.SITE,ppropertyempty.LINE)',
            r'$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,S_result.RESULT)',
            r'~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,false,S_result.RESULT)',
            r'~$property_magic_cv_source(S_result,ppropertyempty.SITE,$(ppropertyempty.LINE + 1))',
            r'~$property_empty_valid(S_result[.SOURCES = eps],ppropertyempty)',
            r'$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PSTRING ([48])))',
            r'~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PSTRING ([256])))',
            r'~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_result.STRINGDATA|)) ([48])))',
            r'$property_empty_truth(S_result,PSTRING_CARRIER INTERNED_STRING ([48])) = (true)',
            r'$property_empty_guard(S_result,n_receiver,ppropertyempty.NAME) /\ $heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2',
            r'S_result.STORE[n_selector] = DEFINED pvalue_selector /\ S_result.EVENTS = S.EVENTS',
            r'PhpStep: S_result ~> S_truth',
            r'S_truth.TODO = ptask_result* /\ S_truth.RESULT = KNOWN (PBOOL true)',
            r'$heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1 /\ ~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME)',
            r'S_truth.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S_truth.STRINGDATA = S_result.STRINGDATA',
            r'S_nul_found = $quiet_string_seek_result(S_truth,[113,0],4000)',
            r'S_nul_found.COMPLETION = NORMAL \/ S_nul_found.COMPLETION = BUDGET',
            r'S_nul = S_nul_found[.COMPLETION = NORMAL]',
            r'S_nul.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_nul true) :: ptask_nul*',
            r'ppropertyempty_nul.OBJECT = n_receiver /\ ppropertyempty_nul.NAME = [113]',
            r'S_nul.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([113,0]))',
            r'$string_carrier_valid(S_nul,PSTRING_CARRIER INTERNED_STRING ([113,0]))',
            r'$property_magic_cv_result_supported(S_nul,ppropertyempty_nul.SITE,ppropertyempty_nul.LINE,true,S_nul.RESULT)',
            r'$property_empty_truth(S_nul,PSTRING_CARRIER INTERNED_STRING ([113,0])) = (false)',
            r'$value_nodes(PSTRING_CARRIER INTERNED_STRING ([113,0])) = eps',
            r'$heap_owners($heap_graph(S_nul),HOBJECT n_receiver) = 2',
            r'S_nul.STORE[n_selector] = DEFINED pvalue_selector_nul',
            r'$string_bytes(pvalue_selector_nul) = ([113])',
            r'PhpStep: S_nul ~> S_nonempty',
            r'S_nonempty.TODO = ptask_nul* /\ S_nonempty.RESULT = KNOWN (PBOOL false)',
            r'$heap_owners($heap_graph(S_nonempty),HOBJECT n_receiver) = 1',
            r'~$property_empty_guard(S_nonempty,n_receiver,ppropertyempty_nul.NAME)',
            r'S_done = $drive_steps(S_nonempty,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY_ZERO;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("STRING_ZERO;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("NONEMPTY_NUL;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("NUL_BYTES;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALL;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
            r'S_done.STORE[n_selector] = DEFINED pvalue_selector_nul /\ S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            r'$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
            r'~$property_empty_get_active(S_done,n_receiver,ppropertyempty_nul.NAME) /\ ~$property_empty_guard(S_done,n_receiver,ppropertyempty_nul.NAME)',
            r'$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S_unwind,4096) = S_done',
            r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
        ],
    },
    'string-empty-get-stringable-normal-retirement': {
        'source': STRINGABLE_ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: (TYPE_RETURN_THROW n_payload porigin_return z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))'),
        'checks': [
            r'z_return = 14 /\ S.ORIGIN = (porigin_return)',
            r'n_receiver = ppropertyempty.OBJECT',
            r'ppropertyempty.NAME = $ptascii("zero")',
            r'$property_get_method(S,n_receiver) = (pmethoddesc)',
            r'pfunction = pmethoddesc.FUNCTION',
            r'pfunction.ORIGIN = pcallcontext.FUNCTION',
            r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))] /\ ~pfunction.CODE.STRICT',
            r'$property_quiet_get_source(S,pmethoddesc) /\ $property_empty_context(S,pcallcontext)',
            r'$typed_return_resume_pending(S,z_return) /\ $typed_return_marker_valid(S,n_payload,porigin_return,z_return)',
            r'$typed_return_callback_type(S,n_payload) /\ $typed_return_source(S,porigin_return,z_return)',
            r'$call_task_valid(S,TYPE_RETURN_THROW n_payload porigin_return z_return)',
            r'$task_nodes(TYPE_RETURN_THROW n_payload porigin_return z_return) = [HOBJECT n_payload]',
            r'~$typed_return_marker_valid(S,n_payload,porigin_return,$(z_return + 1))',
            r'~$typed_return_resume_pending(S[.TODO = (RETURN_VALUE z_return) :: ptask_return*],z_return)',
            r'~$typed_return_marker_valid(S[.RESULT = KNOWN (POBJECT n_payload)],n_payload,porigin_return,z_return)',
            r'$lookup($global_table_view(S).ENV,$ptascii("payload")) = (n_payload_cell)',
            r'$lookup($global_table_view(S).ENV,$ptascii("reader")) = (n_receiver_cell)',
            r'$lookup($global_table_view(S).ENV,$ptascii("destination")) = (n_destination)',
            r'$lookup($global_table_view(S).ENV,$ptascii("selector")) = (n_selector)',
            r'S.STORE[n_payload_cell] = DEFINED PNULL /\ S.STORE[n_receiver_cell] = DEFINED PNULL',
            r'S.STORE[n_destination] = DEFINED (PINT 42)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'$string_bytes(pvalue_selector) = ($ptascii("zero"))',
            r'(HOBJECT n_payload) <- S.ALLOCATIONS /\ (HOBJECT n_receiver) <- S.ALLOCATIONS',
            r'$heap_owners($heap_graph(S),HOBJECT n_payload) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
            r'~(n_payload <- S.DESTRUCTION.CALLED) /\ ~(n_receiver <- S.DESTRUCTION.CALLED)',
            r'$string_carrier_valid(S,PSTRING_CARRIER INTERNED_STRING ([48])) /\ $value_nodes(PSTRING_CARRIER INTERNED_STRING ([48])) = eps',
            r'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;"),OUTPUT $ptascii("CAST;")]',
            r'$call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))',
            r'PhpStep: S ~> S_unwind',
            r'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))) (porigin_return)) :: ptask_return*',
            r'S_unwind.RESULT = KNOWN PNULL /\ S_unwind.BASE = BASE_VALUE (KNOWN PNULL)',
            r'S_unwind.STORE = S.STORE /\ S_unwind.EVENTS = S.EVENTS /\ S_unwind.STRINGDATA = S.STRINGDATA',
            r'$heap_owners($heap_graph(S_unwind),HOBJECT n_payload) = 0 /\ $heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 1',
            r'~$typed_return_resume_pending(S_unwind,z_return)',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_result_found = $quiet_string_seek_result(S_zero[.COMPLETION = NORMAL],[48],2000)',
            r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
            r'S_result = S_result_found[.COMPLETION = NORMAL]',
            r'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_result*',
            r'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48])) /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps',
            r'S_result.STORE[n_payload_cell] = DEFINED PNULL /\ S_result.STORE[n_receiver_cell] = DEFINED PNULL',
            r'S_result.STORE[n_destination] = DEFINED (PINT 42) /\ S_result.STORE[n_selector] = DEFINED pvalue_selector',
            r'~((HOBJECT n_payload) <- S_result.ALLOCATIONS) /\ n_payload <- S_result.DESTRUCTION.CALLED',
            r'(HOBJECT n_receiver) <- S_result.ALLOCATIONS /\ ~(n_receiver <- S_result.DESTRUCTION.CALLED)',
            r'$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
            r'S_result.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("PAYLOAD;")]',
            r'~$property_empty_get_active(S_result,n_receiver,ppropertyempty.NAME) /\ $property_empty_guard(S_result,n_receiver,ppropertyempty.NAME)',
            r'$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,S_result.RESULT)',
            r'$call_task_valid(S_result,PROPERTY_EMPTY_RESULT ppropertyempty true) /\ $call_descriptors_valid(S_result) /\ $heap_valid($heap_graph(S_result))',
            r'S_done = $drive_steps(S_result,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.STORE[n_destination] = DEFINED (PBOOL true) /\ S_done.STORE[n_payload_cell] = DEFINED PNULL /\ S_done.STORE[n_receiver_cell] = DEFINED PNULL',
            r'S_done.STORE[n_selector] = DEFINED pvalue_selector',
            r'~((HOBJECT n_payload) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            r'n_payload <- S_done.DESTRUCTION.CALLED /\ n_receiver <- S_done.DESTRUCTION.CALLED',
            r'~$property_empty_get_active(S_done,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_guard(S_done,n_receiver,ppropertyempty.NAME)',
            r'S_done.EVENTS = S_result.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("PAYLOAD_CLEAR;"),OUTPUT $ptascii("READER_CLEAR;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
            r'S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps',
            r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S_zero[.COMPLETION = NORMAL],4096) = S_done',
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
                  if not args.case or name in args.case}, (Path(__file__), CATALOGUE, STRINGABLE_CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=render)
