#!/usr/bin/env python3
"""Check exact mixed Get returns and the existing private NULL handoff."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_nullable_union_quiet_get_protocol as shared

CATALOGUE = Path(__file__).with_name('magic_property_mixed_quiet_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

CASES = {
    'mixed-quiet-get-exact-string-and-private-null': {
        'source': ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))'),
        'checks': [
            r'S.FRAMES = [pframe]',
            r'S.HELD = eps',
            r'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
            r'ppropertyempty.PROPERTY = eps /\ ppropertyempty.NAME = $ptascii("zero")',
            r'n_receiver = ppropertyempty.OBJECT',
            r'$property_get_method(S,n_receiver) = (pmethoddesc)',
            r'pfunction = pmethoddesc.FUNCTION',
            r'pfunction.ORIGIN = pcallcontext.FUNCTION /\ pfunction.ORIGIN = ppropertyempty.GET',
            r'pfunction.ENDLINE = 5 /\ ~pfunction.SIGNATURE.BYREF /\ ~pfunction.CODE.STRICT',
            r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]',
            r'$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
            r'pclassdesc.NAME = $ptascii("QuietMixedRead") /\ pclassdesc.PARENT = eps',
            r'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
            r'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            r'$ptlc($base64(text_return)) = $ptascii("mixed")',
            r'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
            r'$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            r'$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
            r'~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
            r'$property_quiet_get_source(S,pmethoddesc) /\ ~$property_empty_get_source(S,pmethoddesc)',
            r'$property_empty_method_source(S,pmethoddesc,true) /\ $property_coalesce_method_source(S,pmethoddesc,true)',
            r'~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
            r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
            r'$property_empty_context(S,pcallcontext) /\ $property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
            r'$typed_return_task_valid(S,z_return) /\ ~$typed_return_task_valid(S,$(z_return + 1))',
            r'pvalue_exact = PSTRING_CARRIER INTERNED_STRING ([48])',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_exact,false,false) = TYPEVALUE pvalue_exact',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_exact,true,false) = TYPEVALUE pvalue_exact',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,true,false) = TYPEVALUE PNULL',
            r'$property_empty_truth(S,pvalue_exact) = (true)',
            r'$value_nodes(pvalue_exact) = eps /\ $value_nodes(PNULL) = eps',
            r'S_caller = $constant_frame_scope(S,pframe,eps)',
            r'$property_magic_cv_source(S_caller,ppropertyempty.SITE,ppropertyempty.LINE)',
            r'$property_magic_cv_result_supported(S_caller,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN pvalue_exact)',
            r'~$property_magic_cv_result_supported(S_caller,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN pvalue_exact)',
            r'~$property_magic_cv_result_supported(S_caller,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_receiver))',
            r'$lookup(S_caller.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            r'$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            r'$lookup(S_caller.ENV,$ptascii("written")) = (n_written)',
            r'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S.STORE[n_written] = DEFINED (PINT 42)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'$string_bytes(pvalue_selector) = ($ptascii("zero"))',
            r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2 /\ $call_receiver_roots(pcallcontext) = eps',
            r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            r'S.ORIGIN = (porigin_return)',
            r'PhpStep: S ~> S_unwind',
            r'S_unwind.TODO = (RETURN_UNWIND (KNOWN pvalue_exact) (porigin_return)) :: ptask_return*',
            r'S_unwind.STORE = S.STORE /\ S_unwind.EVENTS = S.EVENTS /\ S_unwind.ALLOCATIONS = S.ALLOCATIONS',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            r'S_one.COMPLETION = BUDGET /\ S_one.TODO = S_unwind.TODO /\ S_one.RESULT = S_unwind.RESULT',
            r'S_private_found = $quiet_composite_seek(S_one[.COMPLETION = NORMAL],1,4000)',
            r'S_private_found.COMPLETION = NORMAL \/ S_private_found.COMPLETION = BUDGET',
            r'S_private = S_private_found[.COMPLETION = NORMAL]',
            r'S_private.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'ppropertycoalesce.OBJECT = n_receiver /\ ppropertycoalesce.NAME = $ptascii("value")',
            r'S_private.RESULT = KNOWN PNULL /\ S_private.STORE[n_written] = DEFINED (PINT 42)',
            r'$property_coalesce_valid(S_private,ppropertycoalesce) /\ $call_task_valid(S_private,PROPERTY_COALESCE_RESULT ppropertycoalesce true)',
            r'$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver] /\ $base_nodes(pbase_pending) = eps',
            r'$heap_owners($heap_graph(S_private),HOBJECT n_receiver) = 2',
            r'PhpStep: S_private ~> S_release',
            r'S_release.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'S_release.RESULT = KNOWN PNULL /\ S_release.BASE = BASE_VALUE (KNOWN PNULL)',
            r'$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 1 /\ S_release.EVENTS = S_private.EVENTS',
            r'S_done = $drive_steps(S_private,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S_done.STORE[n_written] = DEFINED (PINT 9)',
            r'S_done.STORE[n_selector] = DEFINED pvalue_selector_none',
            r'$string_bytes(pvalue_selector_none) = ($ptascii("none"))',
            r'S_done.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("STRING;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("FALSE;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALL;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("S;"),OUTPUT $ptascii("ASSIGN;"),OUTPUT $ptascii("SET;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("SKIP;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
            r'$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
            r'$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S,4096) = S_done /\ $drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
        ],
    },
}

if __name__ == '__main__':
    # Reuse only the unchanged source-stage renderer and private NULL seeker.
    protocol.run(CASES,(Path(__file__),CATALOGUE,Path(shared.__file__),shared.CATALOGUE),
                 fixture_renderer=shared.render,runner_flags=('--sl',))
