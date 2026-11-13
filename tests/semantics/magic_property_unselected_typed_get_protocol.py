#!/usr/bin/env python3
"""Check typed Get declarations which terminal quiet operations never invoke."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_unselected_typed_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

CASES = {
    'typed-array-get-private-terminal-isset-result': {
        'source': ROWS[0]['source'],
        'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
                  '-- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail* '
                  '-- if ppropertyisset.NAME = $ptascii("hidden") '
                  '-- if S.RESULT = KNOWN (PBOOL true)'),
        'checks': [
            'n_receiver = ppropertyisset.OBJECT',
            'S.OBJECTS[n_receiver] = INSTANCE ppropertyisset.CLASS',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
            '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
            'pmethoddesc_isset.FUNCTION.ORIGIN = ppropertyisset.METHOD',
            'pmethoddesc_isset.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"]))]',
            '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
            '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
            'pmethoddesc_get.OWNER = pmethoddesc_isset.OWNER',
            'pfunction = pmethoddesc_get.FUNCTION',
            'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))] /\\ ~pfunction.SIGNATURE.BYREF',
            '$class_at(S.CLASSES,pmethoddesc_get.OWNER) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("TypedArrayIsset") /\\ pclassdesc.PARENT = eps',
            'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
            '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            '$ptlc($base64(text_return)) = $ptascii("array")',
            'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc_get.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
            '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            '$property_get_method_source(S,pmethoddesc_get,true)',
            '~$property_empty_get_source(S,pmethoddesc_get) /\\ ~$property_quiet_get_source(S,pmethoddesc_get)',
            '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc_get,true)',
            '~$property_get_method_source(S,pmethoddesc_get[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
            '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 7,false,false) = TYPEREJECT',
            '$target_function(S,METHOD_TARGET n_receiver pfunction.ORIGIN) = (pfunction)',
            '$property_isset_bool_pair(S,ppropertyisset) /\\ ~$property_isset_untyped(S,ppropertyisset)',
            '$property_isset_source(S,ppropertyisset) /\\ ~$property_isset_empty(S,ppropertyisset)',
            '$property_isset_valid(S,ppropertyisset) /\\ $property_isset_tail(S,ppropertyisset,S.TODO)',
            '$call_task_valid(S,PROPERTY_ISSET_RESULT ppropertyisset)',
            '~$property_isset_valid(S[.SOURCES = eps],ppropertyisset)',
            '~$property_isset_valid(S,ppropertyisset[.LINE = $(ppropertyisset.LINE + 1)])',
            '$property_effective_desc(S,n_receiver,ppropertyisset.NAME) = (ppropertydesc)',
            'ppropertyisset.PROPERTY = (porigin_property)',
            'ppropertydesc.ORIGIN = porigin_property /\\ ppropertydesc.VISIBILITY = PROPERTY_PRIVATE',
            '$objectprops_at(S.OBJECTPROPS,n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*,ppropertydesc.KEY) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (PINT 41))',
            '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
            '~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertyisset.NAME)',
            '~$property_empty_get_active(S,n_receiver,ppropertyisset.NAME)',
            '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            '$lookup(S.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            'S.EVENTS = [OUTPUT $ptascii("I"),OUTPUT $ptascii("hidden"),OUTPUT $ptascii(";")]',
            '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
            'PhpStep: S ~> S_result',
            'S_result.TODO = ptask_tail* /\\ S_result.RESULT = KNOWN (PBOOL true)',
            'S_result.BASE = BASE_VALUE (KNOWN PNULL) /\\ S_result.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
            '~$property_isset_guard(S_result,S_result.CURRENT,S_result.FRAMES,n_receiver,ppropertyisset.NAME)',
            'S_result.STORE = S.STORE /\\ S_result.OBJECTPROPS = S.OBJECTPROPS',
            '$call_descriptors_valid(S_result) /\\ $property_state_valid(S_result) /\\ $heap_valid($heap_graph(S_result))',
            'S_zero = $drive_steps(S,0)',
            'S_zero = S[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            'S_one.COMPLETION = BUDGET /\\ S_one.RESULT = KNOWN (PBOOL true)',
            '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
            'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("PRESENT;"),OUTPUT $ptascii("I"),OUTPUT $ptascii("gone"),OUTPUT $ptascii(";"),OUTPUT $ptascii("ABSENT;"),OUTPUT $ptascii("I"),OUTPUT $ptascii("hidden"),OUTPUT $ptascii(";"),OUTPUT $ptascii("CV;"),OUTPUT $ptascii("NAME;"),OUTPUT $ptascii("DONE;")]',
            '$lookup(S_done.ENV,$ptascii("selector")) = (n_selector)',
            'S_done.STORE[n_selector] = DEFINED pvalue_selector',
            '$string_bytes(pvalue_selector) = ($ptascii("hidden"))',
            'S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            'S_done.OBJECTPROPS = S.OBJECTPROPS /\\ $heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
            '~$destructor_operational(S_done) /\\ S_done.DESTRUCTION.PHASE = DESTRUCTION_PENDING',
            '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
            '$drive_steps(S_result,4096) = S_done',
            '$drive_steps(S,4096) = S_done',
        ],
    },
    'typed-int-get-only-private-empty-borrows-cv': {
        'source': ROWS[1]['source'],
        'stage': ('S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) '
                  ':: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT true z_empty) :: ptask_tail*'),
        'checks': [
            '$base64(text_name) = $ptascii("hidden")',
            'S.ORIGIN = (porigin_site) /\\ S.CURRENT = eps /\\ S.FRAMES = eps',
            'S.BASE = BASE_VALUE (KNOWN PNULL) /\\ $operand_nodes(S.RESULT) = eps',
            'S_read = $quiet_operand(S,S.RESULT)',
            'S_read.COMPLETION = NORMAL',
            'S_read.RESULT = KNOWN (POBJECT n_receiver)',
            '$property_empty_source(S,porigin_site,$base64(text_name),z_empty)',
            '$property_empty_get_skip(S) /\\ $property_empty_prepare(S)',
            '~$property_get_pending(S) /\\ $property_get_plan(S) = eps',
            '$property_isset_method(S,n_receiver) = eps',
            '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
            'pfunction = pmethoddesc_get.FUNCTION',
            'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))] /\\ ~pfunction.SIGNATURE.BYREF',
            '$property_get_method_source(S,pmethoddesc_get,true) /\\ ~$property_empty_get_source(S,pmethoddesc_get)',
            '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,false,false) = TYPEREJECT',
            '~$property_get_method_source(S,pmethoddesc_get[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
            '~$property_empty_get_skip(S[.SOURCES = eps])',
            'S_wrongline = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) $(z_empty + 1)) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT true $(z_empty + 1)) :: ptask_tail*]',
            '~$property_empty_get_skip(S_wrongline)',
            'S_wrongflag = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT false z_empty) :: ptask_tail*]',
            '~$property_empty_get_skip(S_wrongflag)',
            'S_owning = S[.RESULT = KNOWN (POBJECT n_receiver)]',
            '$operand_nodes(S_owning.RESULT) = [HOBJECT n_receiver] /\\ ~$property_empty_get_skip(S_owning)',
            '$lookup(S.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            '$lookup(S.ENV,$ptascii("alias")) = (n_alias_cell)',
            'n_receiver_cell =/= n_alias_cell',
            'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\\ S.STORE[n_alias_cell] = DEFINED (POBJECT n_receiver)',
            '$machine_base_roots(S) = eps /\\ $heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            '$property_effective_desc(S,n_receiver,$base64(text_name)) = (ppropertydesc)',
            'ppropertydesc.VISIBILITY = PROPERTY_PRIVATE /\\ $property_declaring_class(S.CLASSES,ppropertydesc.ORIGIN) = (pmethoddesc_get.OWNER)',
            '$objectprops_at(S.OBJECTPROPS,n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*,ppropertydesc.KEY) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (PINT 41))',
            'S.EVENTS = eps',
            '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
            'PhpStep: S ~> S_skip',
            'S_skip.TODO = (ORIGIN_RETURN (porigin_site)) :: ptask_tail*',
            'S_skip.RESULT = KNOWN (PBOOL true) /\\ S_skip.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_skip.STORE = S.STORE /\\ S_skip.OBJECTPROPS = S.OBJECTPROPS /\\ S_skip.EVENTS = eps',
            '$machine_base_roots(S_skip) = eps /\\ $heap_owners($heap_graph(S_skip),HOBJECT n_receiver) = 2',
            'S_skip.CURRENT = eps /\\ S_skip.FRAMES = eps',
            '$call_descriptors_valid(S_skip) /\\ $property_state_valid(S_skip) /\\ $heap_valid($heap_graph(S_skip))',
            'S_zero = $drive_steps(S,0)',
            'S_zero = S[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            'S_one.COMPLETION = BUDGET /\\ S_one.RESULT = KNOWN (PBOOL true) /\\ S_one.TODO = S_skip.TODO',
            '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2',
            'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("DONE;")]',
            'S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\\ S_done.STORE[n_alias_cell] = DEFINED (POBJECT n_receiver)',
            'S_done.OBJECTPROPS = S.OBJECTPROPS /\\ $heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 2',
            '~$destructor_operational(S_done) /\\ S_done.DESTRUCTION.PHASE = DESTRUCTION_PENDING',
            '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
            '$drive_steps(S_skip,4096) = S_done',
            '$drive_steps(S,4096) = S_done',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__), CATALOGUE),
                 runner_flags=('--sl',))
