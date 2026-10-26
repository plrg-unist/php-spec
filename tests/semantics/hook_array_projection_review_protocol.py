"""Reached singleton-reference snapshots and their final object release."""
import base64
import json
from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 3) = true
  -- if S.TODO = (CAST_RESULT CASTARRAY z) :: ptask_tail*
  -- if $np_output(S.EVENTS) = $ptascii("B|")
def $np_stage(S, 4) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if $np_output(S.EVENTS) = $ptascii("B|C:1:1|K:1|U|")
def $np_stage(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $class_instanceof(S,POBJECT n,$ptascii("SnapshotVictim128R"))
  -- if $np_output(S.EVENTS) = $ptascii("B|C:1:1|K:1|U|")
'''


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def front(program, path):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 3),
        'S.TODO = (CAST_RESULT CASTARRAY z) :: ptask_tail*',
        '$lookup(S.ENV,$ptascii("box")) = (n_boxcv)',
        'S.STORE[n_boxcv] = DEFINED (POBJECT n_box)',
        'S_read = $resolve_at(S,S.RESULT,z)',
        'S_read.COMPLETION = NORMAL', 'S_read.RESULT = KNOWN (POBJECT n_box)',
        'S.OBJECTS[n_box] = INSTANCE porigin_class',
        '$objectprops_at(S.OBJECTPROPS,n_box) = ([ppropertyslot_plain,ppropertyslot_value])',
        'ppropertyslot_plain.NAME = $ptascii("plain")',
        'ppropertyslot_plain.STATE = PROP_VALUE (ALIAS n_ref)',
        'ppropertyslot_value.NAME = $ptascii("value")',
        'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
        '$property_hook_instance(S,n_box)',
        '$aggregate_projection_plain(S,n_box)',
        '~$objectprops_materialized(S.OBJECTPROPS,n_box)',
        '$object_table_at(S.OBJECTTABLES,n_box) = eps',
        '$lookup(S.ENV,$ptascii("temporary")) = eps',
        owners('S', 'HCELL n_ref', 1),
        '~$aggregate_projection_plain($objectprops_mark(S,n_box),n_box)',
        '$np_guard(S)',
    ]


def cast(plain_value):
    return [
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (PARRAY n_copy)',
        'S_raw.TODO = ptask_tail*',
        'S_raw.OBJECTPROPS = S.OBJECTPROPS',
        'S_raw.OBJECTTABLES = S.OBJECTTABLES',
        'S_raw.STORE[n_ref] = S.STORE[n_ref]',
        'S_raw.ARRAYS[n_copy].ITEMS = [ENTRY (KSTRING ($ptascii("plain"))) (DIRECT (' + plain_value + ')),ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PINT 7))]',
        '~$objectprops_materialized(S_raw.OBJECTPROPS,n_box)',
        '$object_table_at(S_raw.OBJECTTABLES,n_box) = eps',
        owners('S_raw', 'HCELL n_ref', 1), '$np_guard(S_raw)',
        'S_after = $drive_steps(S,1)', 'S_after.COMPLETION = BUDGET',
        '$np_guard(S_after)',
        'S_zero = $drive_steps(S,0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
    ]


def finish(source, output):
    return [
        'S_done = $drive_steps(' + source + '[.COMPLETION = NORMAL],4000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text(output), '$np_guard(S_done)',
    ]


def scalar(program, path):
    return front(program, path) + [
        'S.STORE[n_ref] = DEFINED (PINT 2)',
        '$property_layout(S,porigin_class,|S.CLASSES|) = [ppropertydesc_virtual,ppropertydesc_plain,ppropertydesc_value]',
        'ppropertydesc_virtual.KEY = $ptascii("virtual")',
        '$property_hook_virtual(S,ppropertydesc_virtual)',
    ] + cast('PINT 2') + finish('S_after', 'B|C:1:1:1|R:1:1|A|') + [
        '~$heap_member(HCELL n_ref,S_done.ALLOCATIONS)',
    ]


def lifetime(program, path):
    return front(program, path) + [
        'S.STORE[n_ref] = DEFINED (POBJECT n_victim)',
        '$class_instanceof(S,POBJECT n_victim,$ptascii("SnapshotVictim128R"))',
        owners('S', 'HOBJECT n_victim', 1),
    ] + cast('POBJECT n_victim') + [
        owners('S_raw', 'HOBJECT n_victim', 2),
        *seek('S_drop', 'S_after', 4),
        '$lookup(S_drop.ENV,$ptascii("copy")) = (n_copycv)',
        'S_drop.STORE[n_copycv] = DEFINED (PARRAY n_copy)',
        '$entry_lookup(S_drop.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("plain"))) = (DIRECT (POBJECT n_victim))',
        '$lookup(S_drop.ENV,$ptascii("box")) = eps',
        '~$heap_member(HCELL n_ref,S_drop.ALLOCATIONS)',
        owners('S_drop', 'HOBJECT n_victim', 1), '$np_guard(S_drop)',
        *seek('S_destructor', 'S_drop', 5),
        'S_destructor.CURRENT = (pcallcontext_destructor)',
        'pcallcontext_destructor.TARGET = METHOD_TARGET n_victim porigin_destructor',
        '$destructor_selected_pending(S_destructor,$destructor_selected_frame(S_destructor)) = eps',
        '$entry_lookup(S_destructor.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("plain"))) = eps',
        '$np_guard(S_destructor)',
    ] + finish('S_destructor', 'B|C:1:1|K:1|U|D|A|') + [
        '~$heap_member(HOBJECT n_victim,S_done.ALLOCATIONS)',
    ]


def checks(program, path, name):
    return (scalar if name == 'singleton-scalar-snapshot' else lifetime)(program, path)
