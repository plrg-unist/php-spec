#!/usr/bin/env python3
"""Reach pure GET and intrinsically backed short SET source, slot and owners before RHS throw."""
import argparse
import json

import fiber_state_review as review
import pure_get_short_set_pair_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


PREFIX = ('S', '4', ';', '1', 'G', '700',
          'S', '9', ';', 'C', 'G', '700',
          'S', '2', ';', '1', 'G', '700',
          'S', '8', ';', 'U')
TAIL = ('D', 'C', 'S', '1', ';', '1', 'G', '700', 'D', '5', 'Z')


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


review.CASES = {
    'pure-get-and-inherent-short-set-retain-real-slot-and-source-owners-through-abort': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX),
        'checks': [
            'porigin_rewrite = PORIGIN 0 ([PCINDEX 1])',
            'porigin_class = PORIGIN 0 ([PCINDEX 2])',
            'porigin_property = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 0])',
            'porigin_get = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 0, PCFIELD 4, PCINDEX 0])',
            'porigin_hook = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 0, PCFIELD 4, PCINDEX 1])',
            'pcallcontext.FUNCTION = porigin_rewrite',
            'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps', 'pcallcontext.ARGC = 1',
            '$lookup(S.ENV, $ptascii("supplied")) = (n_value)',
            'S.STORE[n_value] = DEFINED pvalue_input',
            '$string_bytes(pvalue_input) = ($ptascii("8"))',
            '$lookup(S.ENV, $ptascii("value")) = eps',
            'S.FRAMES = [pframe_set, pframe_main]',
            'pframe_set.CONTEXT = (pcallcontext_set)', 'pframe_main.CONTEXT = eps',
            'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook',
            'pcallcontext_set.FUNCTION = porigin_hook',
            'pcallcontext_set.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext_set.CALLED_CLASS = (porigin_class)',
            'pcallcontext_set.RECEIVER = (n_receiver)',
            'ppropertyhook.OBJECT = n_receiver', 'ppropertyhook.PROPERTY = porigin_property',
            'ppropertyhook.HOOK = porigin_hook', 'ppropertyhook.LINE = 25',
            'pframe_main.TODO = (PROPERTY_SET_RESULT ppropertyhook pvalue_input) :: ptask_tail*',
            'pframe_set.LOCALS = (psymboltable_set)',
            '$lookup(psymboltable_set.ENV, $ptascii("supplied")) = (n_set_value)',
            'S.STORE[n_set_value] = DEFINED pvalue_input',
            'n_value =/= n_set_value',
            '$lookup(psymboltable_set.ENV, $ptascii("value")) = eps',
            'S.CLASSES = [pclassdesc]', 'pclassdesc.ORIGIN = porigin_class',
            'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps',
            '$hook_property_at(pclassdesc.PROPERTIES, porigin_property) = (ppropertydesc)',
            'ppropertydesc.NAME = $ptascii("value")', 'ppropertydesc.KEY = ppropertydesc.NAME',
            'ppropertydesc.VISIBILITY = PROPERTY_PUBLIC', 'ppropertydesc.SETVISIBILITY = eps',
            'ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            '$property_default_state(S, ppropertydesc) = (PROP_VALUE (DIRECT (PINT 0)))',
            '$origin_node(S.SOURCES, porigin_property) = (NPropertyItem phpType40_name phpType5_initializer metadata_item)',
            'phpType5_initializer =/= ABSENT',
            '$property_set_origin(S, ppropertydesc) = (porigin_hook)',
            '$property_hook_origin(S, ppropertydesc) = (porigin_get)',
            '$property_hook_pair_origins(S, ppropertydesc) = [porigin_get, porigin_hook]',
            '$property_hook_pair_declared(S, ppropertydesc)',
            '$function_at(S.FUNCTIONS, porigin_get) = (pfunction_get)',
            'pfunction_get.NAME = $ptascii("ShortGetSetPair57::$value::get")',
            'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF false}',
            'pfunction_get.DEFAULTS = eps', '~pfunction_get.EARLY',
            'pfunction_get.BODY = [PCINDEX 2, PCFIELD 5, PCINDEX 0, PCFIELD 4, PCINDEX 0, PCFIELD 5]',
            '$origin_node(S.SOURCES, porigin_get) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES text_get) metadata_get) (SEQUENCE eps) (SEQUENCE statement_get*) metadata_get_hook)',
            '$base64(text_get) = $ptascii("get")',
            '~$hook_body_backed(SEQUENCE statement_get*, ppropertydesc.NAME)',
            '$hook_body_supported(SEQUENCE statement_get*)',
            '~$property_hook_virtual(S, ppropertydesc)',
            '$property_set_function(S, ppropertyhook) = (pfunction_set)',
            '$property_set_signature_at(S, ppropertydesc) = (pssignature_set)',
            'pfunction_set.SIGNATURE = pssignature_set',
            'pssignature_set.PARAMETERS = [psparam_set]',
            'pssignature_set.RETURNS = ([(PTBRANCH ([PTBUILTIN "void"]))])',
            '~pssignature_set.BYREF',
            'psparam_set.NAME = $ptascii("supplied")',
            '~psparam_set.BYREF', '~psparam_set.VARIADIC',
            'psparam_set.REQUIRED', 'psparam_set.DEFAULT = PSNONE',
            '|psparam_set.TYPE| = 2',
            '"int" <- $ptmasks(psparam_set.TYPE)',
            '"string" <- $ptmasks(psparam_set.TYPE)',
            '$ptascii("supplied") <- pfunction_set.CVS',
            '~($ptascii("value") <- pfunction_set.CVS)',
            'pfunction_set.NAME = $ptascii("ShortGetSetPair57::$value::set")',
            'pfunction_set.BODY = [PCINDEX 2, PCFIELD 5, PCINDEX 0, PCFIELD 4, PCINDEX 1, PCFIELD 5]',
            '$origin_node(S.SOURCES, PORIGIN 0 pfunction_set.BODY) = (expression)',
            '$origin_node(S.SOURCES, porigin_hook) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES text_set) metadata_set) (SEQUENCE ([phpType17_parameter])) expression metadata_hook)',
            '$base64(text_set) = $ptascii("set")',
            '~$hook_body_backed(expression, ppropertydesc.NAME)',
            '$hook_body_supported(expression)',
            '$origin_node(S.SOURCES, porigin_get) = (phpType38_get)',
            '$origin_node(S.SOURCES, porigin_hook) = (phpType38_set)',
            '$hook_pair_short_set_headers(phpType38_get, phpType38_set, ppropertydesc.NAME, phpType5_initializer)',
            '~$hook_pair_short_set_headers(phpType38_get, phpType38_set, ppropertydesc.NAME, ABSENT)',
            '~$hook_pair_short_set_headers(phpType38_set, phpType38_get, ppropertydesc.NAME, phpType5_initializer)',
            '$origin_child((porigin_hook), [PCFIELD 4, PCINDEX 0]) = (porigin_parameter)',
            '$origin_node(S.SOURCES, porigin_parameter) = (phpType17_parameter)',
            'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) phpType18 (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_parameter_var) ABSENT (SEQUENCE eps) metadata_parameter',
            '$base64(text_parameter) = $ptascii("supplied")',
            '$property_set_expression(S, porigin_hook) = ((ppropertydesc, expression, 16))',
            '$property_set_expression(S, porigin_get) = eps',
            'ptask_implicit = AT porigin_hook (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n_receiver) ppropertydesc.KEY) 16 false)',
            'ptask_implicit <- pframe_set.TODO',
            '$task_nodes(ptask_implicit) = [HOBJECT n_receiver]',
            '$origin_node(S.SOURCES, ppropertyhook.SITE) = (NExprAssign expression_target (NScalarString (BYTES text_input) metadata_input) metadata_assign)',
            '$base64(text_input) = $ptascii("8")',
            '$property_set_context_valid(S, pcallcontext_set)',
            '$property_set_valid(S, ppropertyhook)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("value")) = (ppropertyslot_value)',
            'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 12))',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = eps',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            '$lookup(S_global.ENV, $ptascii("result")) = (n_result)',
            'S.STORE[n_count] = DEFINED (PINT 4)',
            'S.STORE[n_result] = DEFINED pvalue_previous',
            '$string_bytes(pvalue_previous) = ($ptascii("2"))',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(pframe_set.TODO)) = 1',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(pframe_main.TODO)) = 1',
            '$call_context_roots(S.CURRENT) = eps',
            '$call_context_roots(pframe_set.CONTEXT) = eps',
            *valid('S'),
            '$property_set_function(S[.FUNCTIONS = eps], ppropertyhook) = eps',
            '$property_hook_pair_origins(S[.SOURCES = eps], ppropertydesc) = eps',
            '$property_hook_pair_origins(S, ppropertydesc[.TYPE = eps]) = eps',
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
            *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 5)',
            'S_done.STORE[n_result] = DEFINED pvalue_final',
            '$string_bytes(pvalue_final) = ($ptascii("1"))',
            'n_receiver <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = ' + output(*(PREFIX + TAIL)),
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
