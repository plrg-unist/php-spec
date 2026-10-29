#!/usr/bin/env python3
"""Source-reached physical and traced property-table collection checks."""
import argparse

import gc_materialized_table_sources as sources
import shutdown_state_review as runner


CASES = {
    'mixed-physical-and-traced-edges': {
        'source': sources.family.CASES['mixed-components'].decode(),
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT -- if S.GC.NEXT = 0',
        'checks': [
            '$object_table_gc_boundary(S)', '$gc_materialized_quiet(S)',
            '$object_tables_valid(S)',
            '$gc_indirect_arrays_valid(S, S.ALLOCATIONS)',
            '$gc_materialized_locators(S, S.OBJECTTABLES)',
            '$lookup(S.ENV, $ptascii("wa")) = (n_wa_cell)',
            'S.STORE[n_wa_cell] = DEFINED (POBJECT n_wa)',
            'S.OBJECTS[n_wa] = WEAKREFERENCE (n_a)',
            '$lookup(S.ENV, $ptascii("wb")) = (n_wb_cell)',
            'S.STORE[n_wb_cell] = DEFINED (POBJECT n_wb)',
            'S.OBJECTS[n_wb] = WEAKREFERENCE (n_b)',
            '$lookup(S.ENV, $ptascii("wc")) = (n_wc_cell)',
            'S.STORE[n_wc_cell] = DEFINED (POBJECT n_wc)',
            'S.OBJECTS[n_wc] = WEAKREFERENCE (n_c)',
            '$object_table_at(S.OBJECTTABLES, n_a) = (n_table)',
            '$objectprops_at(S.OBJECTPROPS, n_a) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("rows")) = (ppropertyslot_rows)',
            'ppropertyslot_rows.STATE = PROP_VALUE (DIRECT (PARRAY n_rows))',
            'H = $heap_graph(S)',
            '$heap_children(HOBJECT n_a, H.EDGES) = [HARRAY n_table, HOBJECT n_b, HOBJECT n_b, HARRAY n_rows]',
            '$heap_children(HARRAY n_table, H.EDGES) = [HOBJECT n_c]',
            '$heap_children(HOBJECT n_a, $gc_graph(S).EDGES) = [HARRAY n_table]',
            '$heap_children(HARRAY n_table, $gc_graph(S).EDGES) = [HOBJECT n_b, HOBJECT n_b, HARRAY n_rows, HOBJECT n_c]',
            '$heap_valid(H)', '$heap_valid($gc_graph(S))',
            'S_started = $gc_begin(S, pconfigcall)',
            'S_started.TODO = (GC_TRACE pgccall) :: ptask_tail*',
            'S_started.GC.ACTIVE = (pgccall)',
            '$gc_trace_valid(S_started, pgccall)',
            'pgcplan = $gc_plan(S_started, pgccall)',
            'pgcplan.DTORS = eps',
            '|pgcplan.COUNTED| = 5', '$gc_pass_count(pgcplan) = 5',
            '(HARRAY n_table) <- pgcplan.FREESET',
            '~((HARRAY n_table) <- pgcplan.COUNTED)',
            'S_marked = S[.GC.BUFFER = $gc_mark_dtors(S.GC.BUFFER, [HOBJECT n_a])]',
            'S_marked.GC.BUFFER =/= S.GC.BUFFER',
            '~$gc_materialized_quiet(S_marked)',
            '$gc_begin(S_marked, pconfigcall).COMPLETION = UNSUPPORTED "cached ordinary property-table collection"',
            'S_direct = S[.ARRAYS = $array_replace(S.ARRAYS, n_table, $array_insert(S.ARRAYS[n_table], KSTRING $ptascii("left"), DIRECT (POBJECT n_b)))]',
            '~$gc_materialized_locators(S_direct, S_direct.OBJECTTABLES)',
            '$gc_begin(S_direct, pconfigcall).COMPLETION = UNSUPPORTED "cached ordinary property-table collection"',
            'S_wrong_target = S[.ARRAYS = $array_replace(S.ARRAYS, n_table, $array_insert(S.ARRAYS[n_table], KSTRING $ptascii("left"), INDIRECT n_b $ptascii("left")))]',
            '~$object_tables_valid(S_wrong_target)',
            '$gc_begin(S_wrong_target, pconfigcall).COMPLETION = UNSUPPORTED "cached ordinary property-table collection"',
            'S_wrong_key = S[.ARRAYS = $array_replace(S.ARRAYS, n_table, $array_insert(S.ARRAYS[n_table], KSTRING $ptascii("left"), INDIRECT n_a $ptascii("right")))]',
            '~$gc_indirect_arrays_valid(S_wrong_key, S_wrong_key.ALLOCATIONS)',
            '$gc_begin(S_wrong_key, pconfigcall).COMPLETION = UNSUPPORTED "cached ordinary property-table collection"',
        ],
        'timeout': 180,
    },
    'typed-outside-cell-detaches': {
        'source': sources.family.CASES['typed-cell-detachment'].decode(),
        'stage': 'S.TODO = (GC_FREE pgcplan) :: ptask_tail* '
                 '-- if pgcplan.CALL.PASS = 0 -- if S.GC.NEXT = 1',
        'checks': [
            'pgcplan.DTORS = eps',
            '$call_task_valid(S, GC_FREE pgcplan)',
            '$lookup(S.ENV, $ptascii("watch")) = (n_watch_cell)',
            'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
            'S.OBJECTS[n_watch] = WEAKREFERENCE (n_node)',
            '$lookup(S.ENV, $ptascii("alias")) = (n_alias)',
            'S.STORE[n_alias] = DEFINED (PINT 7)',
            '(HCELL n_alias) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HCELL n_alias) = 2',
            '$propref_at(S.PROPREFS, n_alias) = (ppropref)',
            '(HOBJECT n_node) <- pgcplan.FREESET',
            '~((HCELL n_alias) <- pgcplan.FREESET)',
            '$heap_valid($heap_graph(S))',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.STORE[n_alias] = DEFINED (PINT 7)',
            '(HCELL n_alias) <- S_step.ALLOCATIONS',
            '$heap_owners($heap_graph(S_step), HCELL n_alias) = 1',
            '~((HOBJECT n_node) <- S_step.ALLOCATIONS)',
            '$propref_at(S_step.PROPREFS, n_alias) = eps',
            '$heap_valid($heap_graph(S_step))',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
        ],
        'timeout': 180,
    },
    'destructor-plan-stays-outside-slice': {
        'source': '<?php gc_disable(); #[AllowDynamicProperties] class PhysicalGcDtor01 {'
                  ' public $link; function __destruct() {} } $x = new PhysicalGcDtor01;'
                  ' $x->link = $x; $x->extra = 7; unset($x); gc_collect_cycles();',
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT -- if S.GC.NEXT = 0',
        'checks': [
            '$object_table_gc_boundary(S)', '$gc_materialized_quiet(S)',
            'pgccall = {NONCE S.GC.NEXT, CALL pconfigcall, CALLER S.CURRENT, ORIGIN S.ORIGIN, CONSTCONTEXT S.CONSTCONTEXT, PASS 0, TOTAL 0, PENDING eps, COUNT_SOURCE eps}',
            'S_started = S[.GC.NEXT = $(S.GC.NEXT + 1)][.GC.ACTIVE = (pgccall)][.TODO = (GC_TRACE pgccall) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            'pgcplan = $gc_plan(S_started, pgccall)',
            'pgcplan.DTORS =/= eps',
            '$gc_begin(S, pconfigcall).COMPLETION = UNSUPPORTED "cached ordinary property-table collection"',
        ],
        'timeout': 180,
    },
}

runner.CASES = CASES
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
