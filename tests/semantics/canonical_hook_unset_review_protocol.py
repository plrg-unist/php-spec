#!/usr/bin/env python3
"""Reach a canonical-key UNSET with only its saved method retaining the object."""
import argparse
import json

import fiber_state_review as review
import canonical_hook_unset_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


PREFIX = ('V', 'Cannot access private property PrivateUnsetA74::$value', ';',
          'S', '1', ';', 'E', 'Cannot unset hooked property PrivateUnsetA74::$value',
          '|', '1', ';', 'G', '110', ';',
          'X', 'Cannot access private property PrivateUnsetB74::$value',
          '|', '1', ';', 'G', '107', ';', 'U')
TAIL = ('A', 'L', 'Cannot unset hooked property PrivateUnsetA74::$value',
        '|', '1', ';', 'B', 'Z')


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


review.CASES = {
    'private-canonical-unset-preserves-slot-and-last-method-owner-through-error': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output(*PREFIX),
        'checks': [
            'porigin_release = PORIGIN 0 ([PCINDEX 0])',
            'porigin_trait = PORIGIN 0 ([PCINDEX 1])',
            'porigin_wrapper = PORIGIN 0 ([PCINDEX 2])',
            'porigin_a = PORIGIN 0 ([PCINDEX 3])',
            'porigin_b = PORIGIN 0 ([PCINDEX 4])',
            'porigin_property = PORIGIN 0 ([PCINDEX 1, PCFIELD 2, PCINDEX 0, PCFIELD 3, PCINDEX 0])',
            'porigin_get = PORIGIN 0 ([PCINDEX 1, PCFIELD 2, PCINDEX 0, PCFIELD 4, PCINDEX 0])',
            'porigin_set = PORIGIN 0 ([PCINDEX 1, PCFIELD 2, PCINDEX 0, PCFIELD 4, PCINDEX 1])',
            'porigin_erase = PORIGIN 0 ([PCINDEX 3, PCFIELD 5, PCINDEX 4])',
            'porigin_call_release = PORIGIN 0 ([PCINDEX 3, PCFIELD 5, PCINDEX 4, PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 0])',
            'porigin_unset = PORIGIN 0 ([PCINDEX 3, PCFIELD 5, PCINDEX 4, PCFIELD 6, PCINDEX 1])',
            '$origin_child((porigin_unset), [PCFIELD 0, PCINDEX 0]) = (porigin_target)',
            'porigin_get_a = TRAIT_ORIGIN porigin_a porigin_get ($hook_name($ptascii("value")))',
            'porigin_set_a = TRAIT_ORIGIN porigin_a porigin_set ($property_set_name($ptascii("value")))',
            'pcallcontext.FUNCTION = porigin_release',
            'pcallcontext.CALLSITE = (porigin_call_release)',
            'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.RECEIVER = eps', 'pcallcontext.ARGC = 0',
            'S.FRAMES = [pframe_erase, pframe_main]',
            'pframe_erase.CONTEXT = (pcallcontext_erase)', 'pframe_main.CONTEXT = eps',
            'pcallcontext_erase.FUNCTION = porigin_erase',
            'pcallcontext_erase.TARGET = METHOD_TARGET n_receiver porigin_erase',
            'pcallcontext_erase.LEXICAL_CLASS = (porigin_a)',
            'pcallcontext_erase.CALLED_CLASS = (porigin_a)',
            'pcallcontext_erase.RECEIVER = (n_receiver)',
            'pcallcontext_erase.ARGC = 1', 'pcallcontext_erase.LINE = 30',
            'pframe_erase.ORIGIN = (porigin_call_release)',
            'pframe_erase.LOCALS = (psymboltable_erase)',
            '$lookup(psymboltable_erase.ENV, $ptascii("drop")) = (n_drop)',
            'S.STORE[n_drop] = DEFINED (PBOOL true)',
            '$origin_node(S.SOURCES, porigin_unset) = (statement_unset)',
            'statement_unset = NStmtUnset (SEQUENCE ([expression_unset])) metadata_unset',
            '$source_line(metadata_unset) = 15',
            '$origin_node(S.SOURCES, porigin_target) = (expression_unset)',
            'expression_unset = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_value) metadata_value) metadata_property',
            '$base64(text_this) = $ptascii("this")',
            '$base64(text_value) = $ptascii("value")',
            'ptask_unset = AT porigin_unset (STMT statement_unset)',
            'ptask_unset <- pframe_erase.TODO',
            '$task_nodes(ptask_unset) = eps',
            '$origin_accepts(S.SOURCES, porigin_unset, STMT statement_unset)',
            'S.CLASSES = [pclassdesc_trait, pclassdesc_wrapper, pclassdesc_a, pclassdesc_b]',
            'pclassdesc_trait.ORIGIN = porigin_trait',
            'pclassdesc_wrapper.ORIGIN = porigin_wrapper',
            'pclassdesc_a.ORIGIN = porigin_a', 'pclassdesc_b.ORIGIN = porigin_b',
            'pclassdesc_a.PARENT = eps', 'pclassdesc_b.PARENT = eps',
            '$hook_property_at(pclassdesc_trait.PROPERTIES, porigin_property) = (ppropertydesc_raw)',
            '$hook_property_at(pclassdesc_a.PROPERTIES, TRAIT_MEMBER_ORIGIN porigin_a porigin_property) = (ppropertydesc_a)',
            '$hook_property_at(pclassdesc_b.PROPERTIES, TRAIT_MEMBER_ORIGIN porigin_b porigin_property) = (ppropertydesc_b)',
            'ppropertydesc_a = $trait_data_property(pclassdesc_a, ppropertydesc_raw)',
            'ppropertydesc_b = $trait_data_property(pclassdesc_b, ppropertydesc_raw)',
            'ppropertydesc_a.NAME = $ptascii("value")',
            'ppropertydesc_a.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_a.SETVISIBILITY = eps', '~ppropertydesc_a.FINAL',
            'ppropertydesc_a.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            'ppropertydesc_a.KEY = [0] ++ $ptascii("PrivateUnsetA74") ++ [0] ++ $ptascii("value")',
            'ppropertydesc_b.KEY = [0] ++ $ptascii("PrivateUnsetB74") ++ [0] ++ $ptascii("value")',
            'ppropertydesc_a.KEY =/= ppropertydesc_b.KEY',
            '$property_hook_pair_origins(S, ppropertydesc_raw) = [porigin_get, porigin_set]',
            '$property_hook_pair_backed(S, ppropertydesc_raw)',
            '$property_hook_trait_selected(S, ppropertydesc_a, porigin_get_a) = (pfunction_get)',
            '$property_hook_trait_selected(S, ppropertydesc_a, porigin_set_a) = (pfunction_set)',
            '$property_default_state(S, ppropertydesc_a) = (PROP_VALUE (DIRECT (PINT 7)))',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = eps',
            '$lookup(S_global.ENV, $ptascii("other")) = (n_other_cell)',
            'S.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
            'n_receiver =/= n_other',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_a',
            'S.OBJECTS[n_other] = INSTANCE porigin_b',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS', '(HOBJECT n_other) <- S.ALLOCATIONS',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_a*)',
            '$property_slot_at(ppropertyslot_a*, ppropertydesc_a.KEY) = (ppropertyslot_value_a)',
            'ppropertyslot_value_a.STATE = PROP_VALUE (DIRECT (PINT 10))',
            '$objectprops_at(S.OBJECTPROPS, n_other) = (ppropertyslot_b*)',
            '$property_slot_at(ppropertyslot_b*, ppropertydesc_b.KEY) = (ppropertyslot_value_b)',
            'ppropertyslot_value_b.STATE = PROP_VALUE (DIRECT (PINT 7))',
            '$property_desc_at($property_layout(S, porigin_a, |S.CLASSES|), ppropertydesc_a.KEY) = (ppropertydesc_a)',
            '$property_effective_desc(S, n_receiver, ppropertydesc_a.KEY) = eps',
            '$property_hook_declared(S, n_receiver, ppropertydesc_a.NAME)',
            '~$property_hook_declared(S, n_receiver, ppropertydesc_a.KEY)',
            '$property_hook_unset_declared(S, n_receiver, ppropertydesc_a.KEY)',
            '$property_hook_unset_declared(S, n_other, ppropertydesc_b.KEY)',
            'S_erase = S[.CURRENT = (pcallcontext_erase)][.FRAMES = [pframe_main]][.ENV = psymboltable_erase.ENV][.CVS = psymboltable_erase.CVS][.SYMBOLS = psymboltable_erase.SYMBOLS]',
            '$property_resolve(S_erase, n_receiver, ppropertydesc_a.NAME) = PROPERTY_ACCESS ppropertydesc_a.KEY',
            '$property_hook_selected_desc(S_erase, n_receiver, ppropertydesc_a.NAME) = (ppropertydesc_a)',
            '$property_resolve(S_erase, n_other, ppropertydesc_b.NAME) = PROPERTY_DENIED ppropertydesc_b',
            '$property_hook_selected_desc(S_erase, n_other, ppropertydesc_b.NAME) = eps',
            '$lookup(S_global.ENV, $ptascii("input")) = (n_input)',
            'S.STORE[n_input] = DEFINED pvalue_input',
            '$string_bytes(pvalue_input) = ($ptascii("5"))',
            '$lookup(S_global.ENV, $ptascii("result")) = (n_result)',
            'S.STORE[n_result] = DEFINED pvalue_previous',
            '$string_bytes(pvalue_previous) = ($ptascii("keep"))',
            'S.BASE = BASE_VALUE (KNOWN PNULL)',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_other) = 1',
            '$call_context_roots(pframe_erase.CONTEXT) = [HOBJECT n_receiver]',
            '$call_context_roots(S.CURRENT) = eps',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(pframe_erase.TODO)) = 0',
            '$heap_count(HOBJECT n_receiver, $tasks_nodes(pframe_main.TODO)) = 0',
            '$heap_count(HOBJECT n_receiver, $base_nodes(S.BASE)) = 0',
            '$heap_count(HOBJECT n_receiver, S.HELD) = 0',
            *valid('S'),
            '~$property_hook_unset_declared(S, n_receiver, ppropertydesc_a.NAME)',
            '~$property_hook_unset_declared(S, n_receiver, ppropertydesc_b.KEY)',
            '~$property_hook_unset_declared(S[.SOURCES = eps], n_receiver, ppropertydesc_a.KEY)',
            'S_indirect = $property_unset_indirect_check(S, n_receiver, ppropertydesc_a.KEY, 15)',
            'S_indirect.COMPLETION = UNSUPPORTED "hooked property unset"',
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S_paused[.COMPLETION = NORMAL], 4000)',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
            *valid('S_done'),
            'S_done.STORE[n_result] = DEFINED pvalue_previous',
            'n_receiver <- S_done.DESTRUCTION.CALLED',
            'n_other <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_other) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = ' + output(*(PREFIX + TAIL)),
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=1800) else 1)
