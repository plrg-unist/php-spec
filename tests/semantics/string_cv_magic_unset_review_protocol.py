#!/usr/bin/env python3
"""Reach a private unset receipt after its name CV and receiver binding changed."""
import argparse
import json

import fiber_state_review as review
import string_cv_magic_unset_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


PREFIX = ('X', 'secret', ';', 'H', 'secret', ':', '7', ';',
          '8', ':', '99', ':', 'plain', ';',
          'X', 'secret', ';', 'H', 'secret', ':', '8', ';', 'U')
TAIL = ('A', 'C', 'keep', ';', 'X', 'secret', ';', 'H', 'secret', ':', '7', ';',
        '8', ':', '99', ';', 'A', '3', 'Z')
assert ''.join(PREFIX + TAIL).encode() == sources.SOURCE_EXPECTED


review.CASES = {
    'private-unset-keeps-selected-name-and-one-receipt-through-helper-throw': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX),
        'checks': [
            'porigin_release = PORIGIN 0 ([PCINDEX 1])',
            'porigin_class = PORIGIN 0 ([PCINDEX 2])',
            'porigin_unset = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 2])',
            'pcallcontext.FUNCTION = porigin_release',
            'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps', 'pcallcontext.ARGC = 2',
            'S.FRAMES = [pframe_unset, pframe_main]',
            'pframe_unset.CONTEXT = (pcallcontext_unset)',
            'pframe_main.CONTEXT = eps',
            'pframe_main.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*',
            'pframe_main.ORIGIN = (ppropertyunset.SITE)',
            'ppropertyunset.LINE = 21',
            'ppropertyunset.NAME = $ptascii("secret")',
            'ppropertyunset.CLASS = porigin_class',
            'ppropertyunset.METHOD = porigin_unset',
            'n_receiver = ppropertyunset.OBJECT',
            'pcallcontext_unset.TARGET = PROPERTY_UNSET_TARGET ppropertyunset',
            'pcallcontext_unset.FUNCTION = porigin_unset',
            'pcallcontext_unset.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext_unset.CALLED_CLASS = (porigin_class)',
            'pcallcontext_unset.RECEIVER = (n_receiver)',
            'pcallcontext_unset.CALLSITE = (ppropertyunset.SITE)',
            'pcallcontext_unset.ARGC = 1',
            '$property_unset_frame(S, pcallcontext_unset, pframe_main, ppropertyunset)',
            '$property_unset_entered(S, S.CURRENT, S.FRAMES, ppropertyunset)',
            '$call_receiver_roots(pcallcontext_unset) = eps',
            '$call_receiver_roots(pcallcontext) = eps',
            '$target_nodes(pcallcontext_unset.TARGET) = eps',
            '$task_nodes(PROPERTY_UNSET_RESULT ppropertyunset) = [HOBJECT n_receiver]',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(pframe_unset.TODO)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            '$property_unset_method(S, n_receiver) = (pmethoddesc_unset)',
            'pmethoddesc_unset.FUNCTION.ORIGIN = porigin_unset',
            '$property_magic_method_source(S, pmethoddesc_unset, "__unset")',
            '$property_effective_desc(S, n_receiver, ppropertyunset.NAME) = (ppropertydesc_secret)',
            '(porigin_property_witness) = ppropertyunset.PROPERTY',
            'ppropertydesc_secret.ORIGIN = porigin_property_witness',
            'ppropertydesc_secret.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_secret.KEY = [0] ++ $ptascii("MagicUnsetName79") ++ [0] ++ $ptascii("secret")',
            '~$property_hook_unset_declared(S, n_receiver, ppropertydesc_secret.KEY)',
            '$property_effective_desc(S, n_receiver, $ptascii("plain")) = (ppropertydesc_plain)',
            'ppropertydesc_plain.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_plain.KEY = $ptascii("plain")',
            'porigin_plain = ppropertydesc_plain.ORIGIN',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc_secret.KEY) = (ppropertyslot_secret)',
            'ppropertyslot_secret.STATE = PROP_VALUE (DIRECT (PINT 8))',
            '$property_slot_at(ppropertyslot_all*, ppropertydesc_plain.KEY) = (ppropertyslot_plain)',
            'ppropertyslot_plain.STATE = PROP_VALUE (DIRECT (PINT 99))',
            '$property_unset_source(S, ppropertyunset)',
            '$origin_node(S.SOURCES, ppropertyunset.SITE) = (expression_property)',
            'expression_property = NExprPropertyFetch expression_receiver expression_name metadata_property',
            'expression_receiver = NExprVariable (BYTES text_receiver) metadata_receiver',
            '$base64(text_receiver) = $ptascii("object")',
            'expression_name = NExprVariable (BYTES text_name) metadata_name',
            '$base64(text_name) = $ptascii("name")',
            '$property_magic_cv_source(S, ppropertyunset.SITE, 21)',
            'ppropertyunset.SITE = PORIGIN 0 pcpath_property',
            'pcpath_statement = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
            '$origin_node(S.SOURCES, PORIGIN 0 pcpath_statement) = (NStmtUnset (SEQUENCE expression_targets*) metadata_statement)',
            'expression_targets* = [expression_property]',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 8)',
            '$lookup(S.ENV, $ptascii("member")) = (n_helper_member)',
            'S.STORE[n_helper_member] = DEFINED pvalue_helper_member',
            '$string_bytes(pvalue_helper_member) = ($ptascii("secret"))',
            'pframe_unset.LOCALS = (psymboltable_unset)',
            '$lookup(psymboltable_unset.ENV, $ptascii("member")) = (n_unset_member)',
            'S.STORE[n_unset_member] = DEFINED pvalue_unset_member',
            '$string_bytes(pvalue_unset_member) = ($ptascii("secret"))',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = eps',
            '$lookup(S_global.ENV, $ptascii("name")) = (n_name)',
            'S.STORE[n_name] = DEFINED pvalue_name_now',
            '$string_bytes(pvalue_name_now) = ($ptascii("plain"))',
            '$lookup(S_global.ENV, $ptascii("keep")) = (n_keep)',
            'S.STORE[n_keep] = DEFINED pvalue_keep',
            '$string_bytes(pvalue_keep) = ($ptascii("keep"))',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 2)',
            'S_saved = $constant_frame_scope(S, pframe_main, eps)',
            '$property_unset_valid(S_saved, ppropertyunset)',
            '$property_unset_tail(S_saved, ppropertyunset, S_saved.TODO)',
            '~$property_unset_capture(S_saved, ppropertyunset)',
            '$property_magic_name_capture(S_saved, ppropertyunset.SITE, 21, $ptascii("plain"))',
            '~$property_magic_name_capture(S_saved, ppropertyunset.SITE, 21, ppropertyunset.NAME)',
            '$property_hook_cv_name_operand(S_saved, VARIABLE ($ptascii("name")) 21, [PCFIELD 1])',
            '~$property_hook_cv_name_operand(S_saved, KNOWN (PSTRING ($ptascii("secret"))), [PCFIELD 1])',
            '~$property_unset_source(S[.SOURCES = eps], ppropertyunset)',
            '~$property_unset_source(S, ppropertyunset[.LINE = 22])',
            '$property_unset_source(S, ppropertyunset[.NAME = $ptascii("plain")])',
            '~$property_unset_valid(S_saved, ppropertyunset[.NAME = $ptascii("plain")])',
            '~$property_unset_valid(S_saved, ppropertyunset[.PROPERTY = (porigin_plain)])',
            '~$property_unset_frame(S, pcallcontext_unset[.LINE = 22], pframe_main, ppropertyunset)',
            *review.VALID,
            'S_paused = $drive(S, 0)',
            'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S_paused[.COMPLETION = NORMAL], 4000)',
            *review.DONE,
            'S_done.EVENTS = ' + output(*(PREFIX + TAIL)),
            '$trace_slot(S_done, S_done.ENV, $ptascii("n")) = PINT 3',
            '$trace_slot(S_done, S_done.ENV, $ptascii("keep")) = pvalue_keep',
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
