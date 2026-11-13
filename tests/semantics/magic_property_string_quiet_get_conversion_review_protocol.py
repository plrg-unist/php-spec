#!/usr/bin/env python3
"""Check ordinary weak Get Stringable failure names and marker ownership."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_string_quiet_get_conversion_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''

dec $string_conversion_review_catch(pstate) : bool
def $string_conversion_review_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $string_conversion_review_catch(S) = false -- otherwise
dec $string_conversion_review_seek_catch(pstate,nat) : pstate
def $string_conversion_review_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $string_conversion_review_seek_catch(S,n) = S
  -- if $string_conversion_review_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $string_conversion_review_seek_catch(S,0) = S
  -- if ~$string_conversion_review_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $string_conversion_review_seek_catch(S,n) = $string_conversion_review_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$string_conversion_review_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $string_conversion_review_after(pstate,pstate) : pstate
def $string_conversion_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))
'''

CHECKS = ['z_return = 8 /\\ S.ORIGIN = (porigin_return)',
 'S.CURRENT = (pcallcontext_get)',
 'pcallcontext_get.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true',
 '$function_at($all_functions(S),pcallcontext_get.FUNCTION) = (pfunction_get)',
 '$property_get_method(S,ppropertycoalesce.OBJECT) = (pmethoddesc_get)',
 'pmethoddesc_get.FUNCTION = pfunction_get',
 'pfunction_get.ENDLINE = 8 /\\ pfunction_get.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ '
 '~pfunction_get.CODE.STRICT /\\ ~pfunction_get.SIGNATURE.BYREF',
 '$property_coalesce_method_source(S,pmethoddesc_get,true) /\\ ~$property_empty_get_source(S,pmethoddesc_get)',
 '$return_function_name(S,pfunction_get) = $ptascii("class@anonymous::__get")',
 '$c_string(pfunction_get.NAME) = $ptascii("class@anonymous") /\\ 0 <- pfunction_get.NAME',
 '$return_function_name(S,pfunction_get[.ENDLINE = 99]) = pfunction_get.NAME',
 '$typed_return_source(S,porigin_return,z_return) /\\ $typed_return_throw_pending(S)',
 '$typed_return_marker_valid(S,n_payload,porigin_return,z_return)',
 '$typed_reference_conversion(S,pfunction_get.SIGNATURE.RETURNS,POBJECT n_payload,false,false) = TYPEDEPENDENT '
 '"user object string conversion"',
 '$typed_reference_conversion(S,pfunction_get.SIGNATURE.RETURNS,POBJECT n_payload,true,false) = TYPEREJECT',
 '$task_nodes(TYPE_RETURN_THROW n_payload porigin_return z_return) = [HOBJECT n_payload]',
 '$task_nodes(STRINGIFY_RESULT n_payload porigin_return z_return) = [HOBJECT n_payload]',
 'S.OBJECTS[n_cast_error] = THROWABLE pthrowable_cast',
 'pthrowable_cast.KIND = "Exception"',
 '$string_bytes($throwable_field(S,n_cast_error,"message")) = ($ptascii("fresh-cast"))',
 '$throwable_field(S,n_cast_error,"line") = PINT 3 /\\ $throwable_field(S,n_cast_error,"previous") = PNULL',
 'S.FRAMES = [pframe_caller]',
 'pframe_caller.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_caller*',
 'S_caller = $constant_frame_scope(S,pframe_caller,eps)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("payload")) = (n_payload_cell)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 'n_receiver = ppropertycoalesce.OBJECT',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\\ S.STORE[n_payload_cell] = DEFINED (POBJECT n_payload) '
 '/\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("value"))',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
 '$heap_owners($heap_graph(S),HOBJECT n_payload) = 3',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;"),OUTPUT $ptascii("CAST;")]',
 '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
 'PhpStep: S ~> S_wrapped_raw',
 'S_wrapped_raw.TODO = (THROW_SEARCH n_type_error) :: ptask_return*',
 'S_wrapped_raw.COMPLETION = NORMAL /\\ S_wrapped_raw.RESULT = KNOWN PNULL /\\ S_wrapped_raw.BASE = BASE_VALUE '
 '(KNOWN PNULL)',
 'S_wrapped_raw.OBJECTS[n_type_error] = THROWABLE pthrowable_type',
 'pthrowable_type.KIND = "TypeError"',
 '$string_bytes($throwable_field(S_wrapped_raw,n_type_error,"message")) = ($ptascii("class@anonymous::__get(): '
 'Return value must be of type string, StringReviewThrowPayload returned"))',
 '$throwable_field(S_wrapped_raw,n_type_error,"line") = PINT 8 /\\ '
 '$throwable_field(S_wrapped_raw,n_type_error,"previous") = POBJECT n_cast_error',
 'S_wrapped_raw.STORE[n_destination] = DEFINED (PINT 42) /\\ S_wrapped_raw.EVENTS = S.EVENTS',
 '$heap_owners($heap_graph(S_wrapped_raw),HOBJECT n_payload) = 1',
 '$heap_owners($heap_graph(S_wrapped_raw),HOBJECT n_receiver) = 2',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one[.COMPLETION = NORMAL] = $string_conversion_review_after(S,S_wrapped_raw)',
 'S_catch_found = $string_conversion_review_seek_catch(S_one[.COMPLETION = NORMAL],2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_type_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_type_error)',
 '$throwable_field(S_catch,n_type_error,"previous") = POBJECT n_cast_error',
 '$throwable_field(S_catch,n_cast_error,"previous") = PNULL',
 'S_catch.STORE[n_destination] = DEFINED (PINT 42) /\\ S_catch.EVENTS = S.EVENTS',
 '$heap_owners($heap_graph(S_catch),HOBJECT n_receiver) = 1 /\\ $heap_owners($heap_graph(S_catch),HOBJECT '
 'n_payload) = 1',
 '~$property_empty_get_active(S_catch,n_receiver,ppropertycoalesce.NAME)',
 'PhpStep: S_catch ~> S_bound_raw',
 'S_bound = $string_conversion_review_after(S_catch,S_bound_raw)',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_type_error)',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("class@anonymous::__get(): Return value must be of type string, '
 'StringReviewThrowPayload returned"),OUTPUT $ptascii(";"),OUTPUT $ptascii("8"),OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("fresh-cast"),OUTPUT $ptascii(";"),OUTPUT $ptascii("3"),OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("ROOT;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\\ S_done.STORE[n_payload_cell] = DEFINED (POBJECT '
 'n_payload) /\\ S_done.STORE[n_destination] = DEFINED (PINT 42) /\\ S_done.STORE[n_selector] = DEFINED '
 'pvalue_selector',
 '$throwable_field(S_done,n_type_error,"previous") = POBJECT n_cast_error',
 '~$destructor_operational(S_done) /\\ S_done.DESTRUCTION.PHASE = DESTRUCTION_PENDING',
 '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1 /\\ $heap_owners($heap_graph(S_done),HOBJECT '
 'n_payload) = 1',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done']

CASES = {
    'anonymous-string-get-fresh-stringable-throw-name-and-resume': {
        'source': ROW['source'],
        'stage': 'S.TODO = (THROW_SEARCH n_cast_error) :: (STRINGIFY_RESULT n_payload porigin_return z_return) :: (RETURN_VALUE z_return) :: (TYPE_RETURN_THROW n_payload porigin_return z_return) :: ptask_return*',
        'checks': CHECKS,
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
                 (Path(__file__),CATALOGUE),runner_flags=('--sl',),fixture_renderer=render)
