#!/usr/bin/env python3
"""Reach a scalar magic getter whose name CV changed after selection."""
import argparse
import json

import fiber_state_review as review
import string_cv_magic_properties_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


PREFIX = ('G', 'secret', ';', 'H', '7', ':', 'secret', ';',
          '107', ':', 'plain', ':', '99', ';',
          'G', 'secret', ';', 'H', '7', ':', 'secret', ';', 'U')
TAIL = ('A', 'C', '1', ';', 'G', 'secret', ';', 'H', '7', ':', 'secret', ';',
        '107', ';', 'A', '3', 'Z')


review.CASES = {
    'magic-get-receipt-keeps-selected-name-after-cv-and-receiver-removal': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX),
        'checks': [
            'porigin_read = PORIGIN 0 ([PCINDEX 1])',
            'porigin_class = PORIGIN 0 ([PCINDEX 2])',
            'porigin_get = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 2])',
            'pcallcontext.FUNCTION = porigin_read',
            'pcallcontext.LEXICAL_CLASS = eps',
            'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps', 'pcallcontext.ARGC = 2',
            'S.FRAMES = [pframe_get, pframe_main]',
            'pframe_get.CONTEXT = (pcallcontext_get)',
            'pframe_main.CONTEXT = eps',
            'pframe_main.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*',
            'pframe_main.ORIGIN = (ppropertyget.SITE)',
            'ppropertyget.LINE = 17',
            'ppropertyget.CLASS = porigin_class',
            'ppropertyget.METHOD = porigin_get',
            'ppropertyget.NAME = $ptascii("secret")',
            'ppropertyget.DECL = eps',
            'n_receiver = ppropertyget.OBJECT',
            'pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_receiver porigin_get',
            'pcallcontext_get.FUNCTION = porigin_get',
            'pcallcontext_get.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext_get.CALLED_CLASS = (porigin_class)',
            'pcallcontext_get.RECEIVER = (n_receiver)',
            'pcallcontext_get.ARGC = 1',
            'pcallcontext_get.CALLSITE = (ppropertyget.SITE)',
            '$property_get_frame(S, pcallcontext_get, pframe_main)',
            '$property_get_context(S, pcallcontext_get)',
            '$call_receiver_roots(pcallcontext_get) = eps',
            '$call_receiver_roots(pcallcontext) = eps',
            '$target_nodes(pcallcontext_get.TARGET) = eps',
            '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
            '$property_get_carriers(pframe_main.TODO, n_receiver, ppropertyget.SITE) = 1',
            '$property_get_base_count(pframe_main.TODO, n_receiver, ppropertyget.SITE) = 0',
            '$property_get_input_count(pframe_main.TODO, n_receiver, ppropertyget.SITE) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            '$property_get_method(S, n_receiver) = (pmethoddesc_get)',
            'pmethoddesc_get.FUNCTION.ORIGIN = porigin_get',
            '~pmethoddesc_get.FUNCTION.SIGNATURE.BYREF',
            '$property_effective_desc(S, n_receiver, $ptascii("secret")) = (ppropertydesc_secret)',
            'ppropertydesc_secret.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_secret.KEY = [0] ++ $ptascii("MagicNameGet77") ++ [0] ++ $ptascii("secret")',
            '$property_effective_desc(S, n_receiver, $ptascii("plain")) = (ppropertydesc_plain)',
            'ppropertydesc_plain.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_plain.KEY = $ptascii("plain")',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc_secret.KEY) = (ppropertyslot_secret)',
            'ppropertyslot_secret.STATE = PROP_VALUE (DIRECT (PINT 7))',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc_plain.KEY) = (ppropertyslot_plain)',
            'ppropertyslot_plain.STATE = PROP_VALUE (DIRECT (PINT 99))',
            '$property_get_lookup(S, ppropertyget) = PROPERTY_DENIED ppropertydesc_secret',
            '$property_resolve_scope(S, n_receiver, ppropertyget.NAME, (porigin_class)) = PROPERTY_ACCESS ppropertydesc_secret.KEY',
            '$property_get_source(S, ppropertyget)',
            '$property_get_cv_name_source(S, ppropertyget)',
            '$property_get_history(S, ppropertyget)',
            '$property_get_valid(S, ppropertyget, true)',
            '~$property_get_owned_source(S, ppropertyget)',
            '~$property_get_reference_source(S, ppropertyget)',
            '~$property_get_this_source(S, ppropertyget)',
            '$origin_node(S.SOURCES, ppropertyget.SITE) = (NExprPropertyFetch expression_receiver expression_name metadata_property)',
            'expression_receiver = NExprVariable (BYTES text_receiver) metadata_receiver',
            '$base64(text_receiver) = $ptascii("object")',
            'expression_name = NExprVariable (BYTES text_name) metadata_name',
            '$base64(text_name) = $ptascii("name")',
            '$property_hook_cv_name_site(S, ppropertyget.SITE, 17)',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 7)',
            '$lookup(S.ENV, $ptascii("member")) = (n_helper_member)',
            'S.STORE[n_helper_member] = DEFINED pvalue_helper_member',
            '$string_bytes(pvalue_helper_member) = ($ptascii("secret"))',
            'pframe_get.LOCALS = (psymboltable_get)',
            '$lookup(psymboltable_get.ENV, $ptascii("member")) = (n_get_member)',
            'S.STORE[n_get_member] = DEFINED pvalue_get_member',
            '$string_bytes(pvalue_get_member) = ($ptascii("secret"))',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = eps',
            '$lookup(S_global.ENV, $ptascii("name")) = (n_name)',
            'S.STORE[n_name] = DEFINED pvalue_name_now',
            '$string_bytes(pvalue_name_now) = ($ptascii("plain"))',
            '$lookup(S_global.ENV, $ptascii("result")) = (n_result)',
            'S.STORE[n_result] = DEFINED pvalue_result',
            '$string_bytes(pvalue_result) = ($ptascii("keep"))',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 2)',
            'S_source = S_global[.ORIGIN = (ppropertyget.SITE)]',
            '$property_hook_cv_name_operand(S_source, VARIABLE ($ptascii("name")) 17, [PCFIELD 1])',
            'S_entry = S_source[.CURRENT = eps][.FRAMES = eps][.RESULT = VARIABLE ($ptascii("name")) 17][.BASE = BASE_VALUE (KNOWN PNULL)][.TODO = [PROPERTY_NAME (POBJECT n_receiver) 17, DIM_FETCH 17]]',
            '~$property_get_pending(S_entry)',
            '$property_get_plan(S_entry) = eps',
            '~$property_hook_cv_name_operand(S_source, KNOWN (PSTRING ($ptascii("secret"))), [PCFIELD 1])',
            '~$property_get_source(S[.SOURCES = eps], ppropertyget)',
            '~$property_hook_cv_name_site(S, ppropertyget.SITE, 18)',
            '~$property_get_valid(S, ppropertyget[.NAME = $ptascii("plain")], true)',
            '~$property_get_frame(S, pcallcontext_get[.LINE = 18], pframe_main)',
            '$property_get_verify_desc(S, ppropertyget) = eps',
            '$property_get_name_result_supported(S, ppropertyget, KNOWN (PINT 107))',
            '~$property_get_name_result_supported(S, ppropertyget, KNOWN (PSTRING ($ptascii("bad"))))',
            'S_result = S_source[.CURRENT = eps][.FRAMES = eps][.TODO = pframe_main.TODO][.RESULT = KNOWN (PSTRING ($ptascii("bad")))][.BASE = BASE_VALUE (KNOWN PNULL)]',
            'S_boundary = $property_get_complete(S_result, ppropertyget, S_result.RESULT)',
            'S_boundary.COMPLETION = UNSUPPORTED "CV-name magic getter result or conversion"',
            *review.VALID,
            'S_paused = $drive(S, 0)',
            'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S_paused[.COMPLETION = NORMAL], 4000)',
            *review.DONE,
            'S_done.EVENTS = ' + output(*(PREFIX + TAIL)),
            '$trace_slot(S_done, S_done.ENV, $ptascii("n")) = PINT 3',
            '$trace_slot(S_done, S_done.ENV, $ptascii("result")) = pvalue_result',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'n_receiver <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    parser.add_argument('--process-seconds', type=int, default=1800)
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=args.process_seconds) else 1)
