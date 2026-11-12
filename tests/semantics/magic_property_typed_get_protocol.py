#!/usr/bin/env python3
"""Check physical typed-Get authentication and missing-name entry in fixture SL."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_typed_get_cases.json')
row = json.loads(CATALOGUE.read_text())['cases'][1]
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

CASES = {
    'typed-get-cv-entry-and-source-type': {
        'source': row['source'],
        'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
                  '-- if S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin) '
                  '-- if $property_magic_cv_name(S,porigin,z) = (eps)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("name")) = (n_selector)',
            'S.STORE[n_selector] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)',
            '$property_magic_cv_source(S,porigin,z) /\\ $property_magic_name_capture(S,porigin,z,eps)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$class_at(S.CLASSES,porigin_class) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("TypedGetCV") /\\ pclassdesc.PARENT = eps',
            '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
            '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
            '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
            'pmethoddesc_get.OWNER = pmethoddesc_isset.OWNER',
            'pfunction_get = pmethoddesc_get.FUNCTION',
            'pfunction_get.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
            'psparam.NAME = $ptascii("incoming") /\\ ~psparam.BYREF /\\ ~psparam.VARIADIC /\\ psparam.REQUIRED /\\ psparam.DEFAULT = PSNONE',
            'pfunction_get.SIGNATURE.RETURNS = eps /\\ ~pfunction_get.SIGNATURE.BYREF',
            '$ppmethod_get_declaration_signature(pfunction_get.SIGNATURE)',
            '~$ppmethod_get_signature(pfunction_get.SIGNATURE)',
            'pfunction_get.ORIGIN = PORIGIN n_unit pcpath_get',
            '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_get ++ [PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_parameter_name) ABSENT (SEQUENCE eps) metadata_parameter)',
            '$ptlc($base64(text_type)) = $ptascii("string") /\\ $base64(text_parameter) = psparam.NAME',
            'phpType18 = NIdentifier (BYTES text_type) metadata_type',
            '$property_empty_get_name_type(phpType18,psparam.TYPE)',
            '$property_empty_get_source(S,pmethoddesc_get)',
            '$property_empty_get_name_type(ABSENT,eps)',
            '~$property_empty_get_name_type(phpType18,eps)',
            '~$property_empty_get_name_type(ABSENT,psparam.TYPE)',
            '~$property_empty_get_name_type(phpType18,[(PTBRANCH ([PTBUILTIN "bool"]))])',
            '~$property_empty_get_name_type(phpType18,psparam.TYPE ++ [(PTBRANCH ([PTBUILTIN "null"]))])',
            '$property_empty_get_name_type(NIdentifier (BYTES "U1RSSU5H") eps,psparam.TYPE)',
            '~$property_empty_get_name_type(NIdentifier (BYTES "Ym9vbA==") eps,psparam.TYPE)',
            '~$property_empty_get_name_type(NName (BYTES text_type) metadata_type,psparam.TYPE)',
            '~$property_empty_get_name_type(NNullableType (NIdentifier (BYTES text_type) metadata_type) eps,psparam.TYPE)',
            '~$ppmethod_get_declaration_signature(pfunction_get.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])',
            '~$ppmethod_get_declaration_signature(pfunction_get.SIGNATURE[.PARAMETERS = [psparam[.VARIADIC = true]]])',
            '~$ppmethod_get_declaration_signature(pfunction_get.SIGNATURE[.PARAMETERS = [psparam[.REQUIRED = false]]])',
            '~$ppmethod_get_declaration_signature(pfunction_get.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]])',
            '~$property_empty_get_source(S[.SOURCES = eps],pmethoddesc_get)',
            '~$property_empty_get_source(S[.CLASSES = eps],pmethoddesc_get)',
            '~$property_empty_get_source(S,pmethoddesc_get[.NAME = $ptascii("forged")])',
            '~$property_empty_get_source(S,pmethoddesc_get[.STATIC = true])',
            'ppropertyisset = {SITE porigin, NAME eps, LINE z, OBJECT n_receiver, CLASS porigin_class, METHOD pmethoddesc_isset.FUNCTION.ORIGIN, PROPERTY eps}',
            '$property_isset_source(S,ppropertyisset) /\\ ~$property_isset_empty(S,ppropertyisset)',
            '$property_isset_missing_source(S,ppropertyisset)',
            '$property_effective_desc(S,n_receiver,eps) = eps /\\ $property_isset_storage_capture(S,ppropertyisset)',
            '$property_isset_bool_pair(S,ppropertyisset) /\\ $property_isset_valid(S,ppropertyisset)',
            '$property_isset_capture(S,ppropertyisset) /\\ $property_isset_plan(S) = (ppropertyisset)',
            'S_renamed = S[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("changed")))]',
            '~$property_isset_capture(S_renamed,ppropertyisset)',
            '$property_isset_plan(S_renamed) = (ppropertyisset[.NAME = $ptascii("changed")])',
            '$property_isset_plan(S[.STORE[n_selector] = DEFINED (PINT 9)]) = eps',
            '$property_isset_plan(S[.STORE[n_selector] = DEFINED (PSTRING ([0]))]) = eps',
            '$property_magic_cv_result_supported(S,porigin,z,true,KNOWN (PINT 7))',
            '~$property_magic_cv_result_supported(S,porigin,z,true,KNOWN PNULL)',
            '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S)',
            '$heap_valid($heap_prune($heap_graph(S)))',
            'PhpStep: S ~> S_call',
            '$property_isset_pending_call(S_call,ppropertyisset)',
            '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
            '$target_nodes(PROPERTY_ISSET_TARGET ppropertyisset) = eps',
            '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S_call) /\\ $property_state_valid(S_call)',
            '$heap_valid($heap_prune($heap_graph(S_call)))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
