#!/usr/bin/env python3
"""Independent whole-tree receipts, copied bucket aliases and query owners."""
from pathlib import Path

import global_constant_stdclass_array_protocol as protocol
import global_constant_stdclass_array_review_sources as sources

common, text = protocol.common, protocol.text


def delivery(state, start, query):
    after = state + '_value'
    checks = [*common.reach(state,start,0,query), *common.public(state),
              f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{state}) :: ptask_{state}*',
              f'$dynamic_global_constant_valid({state},pconfigcall_{state})',
              f'$dynamic_global_constant_value({state},{text(query)}) = (PARRAY n_root)',
              f'H_{state} = $heap_graph({state})',
              f'n_rootowners_{state} = $heap_owners(H_{state},HARRAY n_root)',
              f'n_objectowners_{state} = $heap_owners(H_{state},HOBJECT n_object)',
              *common.step(after,state,'PARRAY n_root'),
              f'{after}.TODO = ptask_{state}*',
              f'H_{after} = $heap_graph({after})',
              f'H_{after}.NODES = H_{state}.NODES', f'H_{after}.EDGES = H_{state}.EDGES',
              f'$heap_owners(H_{after},HARRAY n_root) = $(n_rootowners_{state} + 1)',
              f'$heap_owners(H_{after},HOBJECT n_object) = n_objectowners_{state}']
    checks += [f'{after}.{field} = {state}.{field}' for field in
               ['ARRAYS','OBJECTS','OBJECTPROPS','OBJECTTABLES','USERCONSTANTS',
                'CONSTANTSTDOBJECTS','STORE','REFCELLS','ALLOCATIONS']]
    return checks


def checks(initial, query_unused, leaf_unused, stdout, selected_unused):
    tree, alias = 'V60_REVIEW_TREE', 'V60_REVIEW_ALIAS'
    values = [*initial, f'S_bind_found = $test_array_bind_seek(S_initial,{text(alias)},3000)',
              'S_bind = $test_running(S_bind_found)', f'$test_array_bind(S_bind,{text(alias)})',
              'S_bind.TODO = (CONSTANT_BIND porigin_alias) :: ptask_bind*',
              'S_bind.USERCONSTANTS = [puserconstant_leaf,puserconstant_tree]',
              'puserconstant_leaf.NAME = $ptascii("V60_REVIEW_LEAF")',
              f'puserconstant_tree.NAME = {text(tree)}',
              'puserconstant_leaf.VALUE = POBJECT n_object',
              'puserconstant_leaf.CLASS = PVSTDCLASS n_object porigin_birth',
              'puserconstant_tree.VALUE = PARRAY n_root',
              'puserconstant_tree.CLASS = pvalueclass_tree',
              '$pvclass_get(pvalueclass_tree,KINT 1) = (pvalueclass_child)',
              '$pvclass_get(pvalueclass_child,KINT 0) = (PVSTDCLASS n_object porigin_birth)',
              'S_bind.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
              'S_bind.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)),ENTRY (KINT 1) (DIRECT (PARRAY n_empty))]',
              'S_bind.CONSTCONTEXT = (pconstantcontext)',
              'pconstantcontext.FACTS = [pconstantfact_alias]',
              'pconstantfact_alias.CLASS = pvalueclass_tree', 'pconstantfact_alias.VALUE = eps',
              'pconstantfact_alias.LOOKUP = (pconstantlookup_alias)',
              'pconstantlookup_alias.ORIGIN = porigin_alias',
              'pconstantlookup_alias.DECL = puserconstant_tree.ORIGIN', 'pconstantlookup_alias.PREFIX = 2',
              '$constant_class_tree_valid(pvalueclass_tree)', '$constant_fact_value_valid(pconstantfact_alias)',
              '$global_constant_lookup_valid(S_bind,porigin_alias,pconstantfact_alias,S_bind.USERCONSTANTS)',
              '$global_constant_transfer_valid(S_bind,porigin_alias,pvalueclass_tree,S_bind.USERCONSTANTS)',
              '~$global_constant_lookup_valid(S_bind,porigin_alias,pconstantfact_alias[.LOOKUP = (pconstantlookup_alias[.PREFIX = 0])],S_bind.USERCONSTANTS)',
              *common.public('S_bind'), *common.step('S_bound','S_bind','PNULL'),
              *delivery('S_first','S_bound',alias),
              'S_first.USERCONSTANTS = [puserconstant_leaf,puserconstant_tree,puserconstant_alias]',
              'puserconstant_alias.NAME = $ptascii("V60_REVIEW_ALIAS")',
              'puserconstant_alias.VALUE = PARRAY n_root', 'puserconstant_alias.CLASS = pvalueclass_tree',
              'puserconstant_alias.READS = [pconstantfact_alias]',
              '$global_constant_user_valid(S_first,puserconstant_alias)',
              'n_rootowners_S_first = 2', 'n_objectowners_S_first = 3',
              '$global_std_record(S_first.CONSTANTSTDOBJECTS,n_object) = (pconstantstdobject)',
              '$global_std_completed(S_first,pconstantstdobject)', 'S_first.OBJECTS[n_object] = STDINSTANCE',
              '~$constant_callable_foldable(pvalueclass_tree)', '~$default_cacheable(pvalueclass_tree)',
              '~$dynamic_global_constant_array_tree(S_first,POBJECT n_object,PVOBJECT)',
              *delivery('S_peer','S_first_value',tree),
              'n_rootowners_S_peer = 3', 'n_objectowners_S_peer = 3',
              *delivery('S_during','S_peer_value',alias),
              'n_rootowners_S_during = 3', 'n_objectowners_S_during = 4',
              '$lookup(S_during.ENV,$ptascii("copy")) = (n_copy_cell)',
              'S_during.STORE[n_copy_cell] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
              'S_during.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_copy_child))]',
              'n_copy_child =/= n_child', '$lookup(S_during.ENV,$ptascii("slot")) = (n_slot)',
              'n_slot <- S_during.REFCELLS', 'S_during.STORE[n_slot] = DEFINED (PINT 41)',
              'S_during.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (ALIAS n_slot),ENTRY (KINT 1) (DIRECT (PARRAY n_empty))]',
              'S_during.ARRAYS[n_child].ITEMS = S_bind.ARRAYS[n_child].ITEMS',
              '$heap_edge_owners(HOBJECT n_object,H_S_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 1',
              '$heap_edge_owners(HCELL n_slot,H_S_during.EDGES,[HARRAY n_copy_child]) = 1',
              '$lookup(S_during.ENV,$ptascii("receipt")) = (n_receipt)',
              'S_during.STORE[n_receipt] = DEFINED (POBJECT n_object)',
              '$property_slot_at($object_table_slots_at(S_during,n_object),$ptascii("value")) = (ppropertyslot)',
              'ppropertyslot.STATE = PROP_VALUE pitem', '$entry_value(S_during,pitem) = PINT 7',
              'S_during.USERCONSTANTS = S_first.USERCONSTANTS',
              'S_during.CONSTANTSTDOBJECTS = S_first.CONSTANTSTDOBJECTS']
    # Pure projections separate generic value validity from canonical DIRECT trees.
    values += ['S_bad_alias = S_during[.ARRAYS[n_child].ITEMS[0] = ENTRY (KINT 0) (ALIAS n_receipt)]',
               '$constant_value_class_valid(S_bad_alias,PARRAY n_root,pvalueclass_tree)',
               f'$dynamic_global_constant_value(S_bad_alias,{text(alias)}) = eps',
               'S_bad_birth = S_during[.CONSTANTSTDOBJECTS = eps]',
               f'$dynamic_global_constant_value(S_bad_birth,{text(alias)}) = eps',
               'pvalueclass_bad = $pvclass_put(pvalueclass_tree,KINT 1,$pvclass_put(pvalueclass_child,KINT 0,PVOBJECT))',
               'S_bad_tag = S_during[.USERCONSTANTS[2].CLASS = pvalueclass_bad]',
               f'$dynamic_global_constant_value(S_bad_tag,{text(alias)}) = eps',
               *delivery('S_last','S_during_value',tree),
               'n_rootowners_S_last = 2', 'n_objectowners_S_last = 2',
               '~((HARRAY n_copy_root) <- S_last.ALLOCATIONS)',
               '~((HARRAY n_copy_child) <- S_last.ALLOCATIONS)', '~((HCELL n_slot) <- S_last.ALLOCATIONS)',
               'S_final = $drive_steps(S_last_value,5000)', 'S_final.COMPLETION = NORMAL',
               'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps',
               '$test_outputs(S_final.EVENTS) = ' + protocol.term(stdout), *common.public('S_final'),
               '$heap_owners($heap_graph(S_final),HARRAY n_root) = 3',
               '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2']
    return values


protocol.sources, protocol.checks = sources, checks
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(protocol.ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if protocol.main() else 1)
