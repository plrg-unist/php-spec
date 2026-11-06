#!/usr/bin/env python3
"""Reach conditional RHS after retirement and check both borrowed CV selectors."""
import argparse
import json

import fiber_state_review as review
import string_cv_hook_consumers_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


PREFIX = ('G', '3', ';', '', ';', 'G', '3', ';', 'X', 'Q', '1', ';',
          'G', '3', ';', 'F', ';', 'G', '3', ';', 'R', '1', ':', '5', ';',
          'G', '3', ';', 'R', 'A', 'U')
TAIL = ('C', '1', ';', 'G', '3', ';', 'R', 'S', '1', ':', 'plain', ';',
        'G', '15', ';', '1', ';', 'G', '15', ';', '1', ';',
        'G', '15', ';', '15', ';', 'B', '9', 'Z')


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


review.CASES = {
    'conditional-rhs-borrows-current-receiver-and-name-after-old-get-receiver-retires': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX),
        'checks': [
            'porigin_rhs_function = PORIGIN 0 ([PCINDEX 3])',
            'pcallcontext.FUNCTION = porigin_rhs_function',
            'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps', 'pcallcontext.ARGC = 0',
            'pcallcontext.CALLSITE = (porigin_rhs)',
            'porigin_rhs = PORIGIN 0 pcpath_rhs',
            '$(|pcpath_rhs| >= 1)',
            'pcpath_parent = pcpath_rhs[0:$nabs($( |pcpath_rhs| - 1))]',
            'pcpath_rhs = pcpath_parent ++ [PCFIELD 1]',
            'porigin_parent = PORIGIN 0 pcpath_parent',
            '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_target)',
            '$origin_node(S.SOURCES, porigin_parent) = (NExprAssignOpCoalesce expression_target expression_rhs metadata_parent)',
            '$source_line(metadata_parent) = 31',
            '$origin_node(S.SOURCES, porigin_rhs) = (expression_rhs)',
            '$origin_node(S.SOURCES, porigin_target) = (expression_target)',
            'expression_target = NExprPropertyFetch (NExprVariable (BYTES text_object) metadata_object) (NExprVariable (BYTES text_name) metadata_name) metadata_property',
            '$base64(text_object) = $ptascii("object")',
            '$base64(text_name) = $ptascii("name")',
            'S.FRAMES = [pframe_main]',
            'pframe_main.CONTEXT = eps',
            'pframe_main.ORIGIN = (porigin_rhs)',
            'pbase_object = BASE_VALUE (VARIABLE ($ptascii("object")) 31)',
            'poperand_name = VARIABLE ($ptascii("name")) 31',
            'pbase_pending = BASE_PROPERTY_PENDING pbase_object poperand_name 31',
            'ptask_write = COALESCE_ASSIGN_WRITE pbase_pending false 31',
            'ptask_write <- pframe_main.TODO',
            '$base_nodes(pbase_pending) = eps',
            '$task_nodes(ptask_write) = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = (n_object_cell)',
            '$lookup(S_global.ENV, $ptascii("other")) = (n_other_cell)',
            'n_object_cell =/= n_other_cell',
            'S.STORE[n_object_cell] = DEFINED (POBJECT n_receiver)',
            'S.STORE[n_other_cell] = DEFINED (POBJECT n_receiver)',
            '$lookup(S_global.ENV, $ptascii("name")) = (n_name_cell)',
            'S.STORE[n_name_cell] = DEFINED pvalue_name',
            '$string_bytes(pvalue_name) = ($ptascii("plain"))',
            '$lookup(S.ENV, $ptascii("object")) = eps',
            '$lookup(S.ENV, $ptascii("other")) = eps',
            '$lookup(S.ENV, $ptascii("name")) = eps',
            '$lookup(S.ENV, $ptascii("mode")) = (n_mode)',
            'S.STORE[n_mode] = DEFINED (PINT 3)',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 5)',
            '$lookup(S_global.ENV, $ptascii("result")) = (n_result)',
            'S.STORE[n_result] = DEFINED pvalue_previous',
            '$string_bytes(pvalue_previous) = ($ptascii("keep"))',
            '$class_named(S.CLASSNAMES, $ptascii("conditionalname76")) = (porigin_class)',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("ConditionalName76")',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '$(|S.DESTRUCTION.CALLED| > 0)',
            'n_old = S.DESTRUCTION.CALLED[$nabs($( |S.DESTRUCTION.CALLED| - 1))]',
            'S.OBJECTS[n_old] = INSTANCE porigin_class',
            'n_old =/= n_receiver',
            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
            '$property_desc_at(pclassdesc.PROPERTIES, $ptascii("value")) = (ppropertydesc_value)',
            '$property_desc_at(pclassdesc.PROPERTIES, $ptascii("plain")) = (ppropertydesc_plain)',
            '$property_desc_at(pclassdesc.PROPERTIES, $ptascii("tag")) = (ppropertydesc_tag)',
            '$property_hook_named_pair(S, ppropertydesc_value)',
            '$property_default_state(S, ppropertydesc_value) = (PROP_VALUE (DIRECT (PINT 3)))',
            'ppropertydesc_value.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_plain.VISIBILITY = PROPERTY_PUBLIC',
            '$property_hook_effective_origin(S, ppropertydesc_plain) = eps',
            '$property_set_origin(S, ppropertydesc_plain) = eps',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, ppropertydesc_value.KEY) = (ppropertyslot_value)',
            'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 3))',
            '$property_slot_at(ppropertyslot*, ppropertydesc_plain.KEY) = (ppropertyslot_plain)',
            'ppropertyslot_plain.STATE = PROP_VALUE (DIRECT (PINT 99))',
            '$property_slot_at(ppropertyslot*, ppropertydesc_tag.KEY) = (ppropertyslot_tag)',
            'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT pvalue_tag)',
            '$string_bytes(pvalue_tag) = ($ptascii("B"))',
            'S_write = S[.CURRENT = eps][.FRAMES = eps][.ENV = S_global.ENV][.CVS = S_global.CVS][.SYMBOLS = S_global.SYMBOLS][.ORIGIN = (porigin_parent)][.TODO = [ptask_write]]',
            '$property_pending_assign_valid(S_write, pbase_pending, 31, false)',
            '$property_hook_cv_name_site(S_write, porigin_target, 31)',
            '$property_hook_name_ready(S_write, porigin_target, poperand_name)',
            '$property_set_name_ready(S_write, poperand_name)',
            '$memoized_write_base(S_write, pbase_pending, [PCFIELD 0]) = pbase_pending',
            '$memoized_write_ready(S_write, pbase_pending, [PCFIELD 0])',
            '$property_pending_source_base(S_write[.ORIGIN = (porigin_target)], pbase_pending, expression_target)',
            'S_resolved = $property_pending_resolve(S_write, pbase_object, poperand_name, PPW, 31, 31)',
            'S_resolved.COMPLETION = NORMAL',
            'S_resolved.BASE = BASE_PROPERTY (POBJECT n_receiver) ($ptascii("plain"))',
            '$property_hook_selected_desc(S_write, n_receiver, $ptascii("plain")) = (ppropertydesc_plain)',
            '~$property_set_needed(S_write, n_receiver, $ptascii("plain"))',
            '~$property_set_pending(S_write)',
            '$property_set_plan(S_write) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S), HCELL n_object_cell) = 1',
            '$heap_owners($heap_graph(S), HCELL n_other_cell) = 1',
            '$heap_owners($heap_graph(S), HCELL n_name_cell) = 1',
            '$heap_count(HOBJECT n_old, $tasks_nodes(pframe_main.TODO)) = 0',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(pframe_main.TODO)) = 0',
            '$call_context_roots(S.CURRENT) = eps',
            '$call_context_roots(pframe_main.CONTEXT) = eps',
            *valid('S'),
            '~$property_hook_name_ready(S_write, porigin_target, KNOWN pvalue_name)',
            '~$property_set_name_ready(S_write, KNOWN pvalue_name)',
            'pbase_frozen = BASE_PROPERTY_PENDING pbase_object (KNOWN pvalue_name) 31',
            '~$property_pending_assign_valid(S_write[.TODO = [COALESCE_ASSIGN_WRITE pbase_frozen false 31]], pbase_frozen, 31, false)',
            '~$property_pending_assign_valid(S_write[.SOURCES = eps], pbase_pending, 31, false)',
            '~$property_pending_assign_valid(S_write[.TODO = [COALESCE_ASSIGN_WRITE pbase_pending false 32]], pbase_pending, 32, false)',
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S_paused[.COMPLETION = NORMAL], 4000)',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
            *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 9)',
            'S_done.STORE[n_result] = DEFINED (PINT 0)',
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
    raise SystemExit(0 if review.run(args.case, process_seconds=1800) else 1)
