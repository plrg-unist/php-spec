"""No-table physical projection and its downstream inline comparison route."""
import base64
import json
from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 3) = true
  -- if S.TODO = (CAST_RESULT CASTARRAY z) :: ptask_tail*
  -- if $np_output(S.EVENTS) = $ptascii("B|")
def $np_stage(S, 4) = true
  -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask_tail*
  -- if $np_output(S.EVENTS) = $ptascii("B|C:1:1:1|")
'''


def front(program, path, order):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 3),
        'S.TODO = (CAST_RESULT CASTARRAY z) :: ptask_tail*',
        'z = ' + str(13 if order else 15),
        '$lookup(S.ENV,' + text('left' if order else 'box') + ') = (n_boxcv)',
        'S.STORE[n_boxcv] = DEFINED (POBJECT n_box)',
        'S_read = $resolve_at(S,S.RESULT,z)',
        'S_read.COMPLETION = NORMAL', 'S_read.RESULT = KNOWN (POBJECT n_box)',
        'S.OBJECTS[n_box] = INSTANCE porigin_class',
        '$class_instanceof(S,POBJECT n_box,' + text('ProjectionOrder128' if order else 'ProjectionShape128') + ')',
        '$property_hook_instance(S,n_box)', '$aggregate_projection_plain(S,n_box)',
        '~$objectprops_materialized(S.OBJECTPROPS,n_box)',
        '$object_table_at(S.OBJECTTABLES,n_box) = eps',
        '$lookup(S.ENV,$ptascii("gets")) = (n_gets)',
        'S.STORE[n_gets] = DEFINED (PINT 0)',
        '~$aggregate_projection_plain($objectprops_mark(S,n_box),n_box)', '$np_guard(S)',
    ]


def cast(entries):
    return [
        'ppropertyslot_value.NAME = $ptascii("value")',
        'ppropertyslot_value.DECL = (ppropertydesc_value.ORIGIN)',
        'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
        '$property_hook_origin(S,ppropertydesc_value) = (porigin_get)',
        '~$property_hook_virtual(S,ppropertydesc_value)',
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (PARRAY n_copy)', 'S_raw.TODO = ptask_tail*',
        'S_raw.OBJECTPROPS = S.OBJECTPROPS', 'S_raw.OBJECTTABLES = S.OBJECTTABLES',
        'S_raw.STORE = S.STORE',
        'S_raw.ARRAYS[n_copy].ITEMS = ' + entries,
        '~$objectprops_materialized(S_raw.OBJECTPROPS,n_box)',
        '$object_table_at(S_raw.OBJECTTABLES,n_box) = eps', '$np_guard(S_raw)',
        'S_after = $drive_steps(S,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN (PARRAY n_copy)',
        'S_after.OBJECTPROPS = S.OBJECTPROPS', 'S_after.STORE[n_gets] = DEFINED (PINT 0)', '$np_guard(S_after)',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
    ]


def finish(source, output, gets):
    return [
        'S_done = $drive_steps(' + source + '[.COMPLETION = NORMAL],4000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text(output),
        'S_done.STORE[n_gets] = DEFINED (PINT ' + str(gets) + ')', '$np_guard(S_done)',
    ]


def order(program, path):
    return front(program, path, True) + [
        '$property_layout(S,porigin_class,|S.CLASSES|) = [ppropertydesc_first,ppropertydesc_value]',
        '$objectprops_at(S.OBJECTPROPS,n_box) = ([ppropertyslot_first,ppropertyslot_value])',
        'ppropertydesc_first.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
        'ppropertyslot_first.DECL = (ppropertydesc_first.ORIGIN)',
        'ppropertyslot_first.NAME = $ptascii("first")', 'ppropertyslot_first.STATE = PROP_INITIAL',
        'S_duplicate = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_box,[ppropertyslot_first,ppropertyslot_first,ppropertyslot_value])]',
        '~$aggregate_projection_plain(S_duplicate,n_box)',
    ] + cast('[ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PINT 7))]') + [
        '$entry_lookup(S_raw.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("first"))) = eps',
        *seek('S_compare', 'S_after', 4),
        'S_compare.TODO = (BINARY_RIGHT SPACESHIP poperand_left z_compare) :: ptask_compare*',
        'z_compare = 15', 'S_compare.CURRENT = eps /\\ S_compare.FRAMES = eps',
        '$lookup(S_compare.ENV,$ptascii("right")) = (n_rightcv)',
        'S_compare.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        'S_leftread = $resolve_at(S_compare,poperand_left,z_compare)',
        'S_leftread.RESULT = KNOWN (POBJECT n_box)',
        'S_rightread = $resolve_at(S_compare,S_compare.RESULT,z_compare)',
        'S_rightread.RESULT = KNOWN (POBJECT n_right)',
        'S_compare.OBJECTS[n_right] = INSTANCE porigin_class',
        '$objectprops_at(S_compare.OBJECTPROPS,n_box) = ([ppropertyslot_first,ppropertyslot_value])',
        '$objectprops_at(S_compare.OBJECTPROPS,n_right) = ([ppropertyslot_first[.STATE = PROP_VALUE (DIRECT (PINT 5))],ppropertyslot_value])',
        '~$objectprops_materialized(S_compare.OBJECTPROPS,n_box)',
        '~$objectprops_materialized(S_compare.OBJECTPROPS,n_right)',
        '$object_table_at(S_compare.OBJECTTABLES,n_box) = eps',
        '$object_table_at(S_compare.OBJECTTABLES,n_right) = eps',
        '$lookup(S_compare.ENV,$ptascii("copy")) = (n_copycv)',
        'S_compare.STORE[n_copycv] = DEFINED (PARRAY n_copy)',
        '$value_order(S_compare,POBJECT n_box,POBJECT n_right,eps) = ORDER 1',
        'S_marked = $objectprops_mark(S_compare,n_box)',
        '$value_order(S_marked,POBJECT n_box,POBJECT n_right,eps) = ORDER $(-1)',
        '$np_guard(S_compare)',
        'PhpStep: S_compare ~> S_compare_raw', 'S_compare_raw.RESULT = KNOWN (PINT 1)',
        'S_compare_raw.TODO = ptask_compare*',
        'S_compared = $drive_steps(S_compare,1)', 'S_compared.COMPLETION = BUDGET',
        'S_compared.RESULT = KNOWN (PINT 1)', 'S_compared.TODO = ptask_compare*', '$np_guard(S_compared)',
        'S_compare_zero = $drive_steps(S_compare,0)',
        'S_compare_zero = S_compare[.COMPLETION = BUDGET]',
        '$drive_steps(S_compare_zero[.COMPLETION = NORMAL],1) = S_compared',
    ] + finish('S_compared', 'B|C:1:1:1|R:1:1:1|A|', 0)


def shape(program, path):
    return front(program, path, False) + [
        '$property_layout(S,porigin_class,|S.CLASSES|) = [ppropertydesc_virtual,ppropertydesc_secret,ppropertydesc_hidden,ppropertydesc_value]',
        '$property_hook_virtual(S,ppropertydesc_virtual)',
        '$objectprops_at(S.OBJECTPROPS,n_box) = ([ppropertyslot_secret,ppropertyslot_hidden,ppropertyslot_value])',
        'ppropertyslot_secret.NAME = [0] ++ $ptascii("ProjectionShape128") ++ [0] ++ $ptascii("secret")',
        'ppropertyslot_secret.DECL = (ppropertydesc_secret.ORIGIN)',
        'ppropertydesc_secret.VISIBILITY = PROPERTY_PRIVATE',
        'ppropertyslot_secret.STATE = PROP_VALUE (DIRECT (PINT 2))',
        'ppropertyslot_hidden.NAME = [0,42,0] ++ $ptascii("hidden")',
        'ppropertyslot_hidden.DECL = (ppropertydesc_hidden.ORIGIN)',
        'ppropertydesc_hidden.VISIBILITY = PROPERTY_PROTECTED',
        'ppropertyslot_hidden.STATE = PROP_VALUE (DIRECT (PINT 3))',
    ] + cast('[ENTRY (KSTRING ppropertyslot_secret.NAME) (DIRECT (PINT 2)),ENTRY (KSTRING ppropertyslot_hidden.NAME) (DIRECT (PINT 3)),ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PINT 7))]') + [
        '$entry_lookup(S_raw.ARRAYS[n_copy].ITEMS,KSTRING ppropertydesc_virtual.KEY) = eps',
    ] + finish('S_after', 'B|C:1:1:1:1:1|G:1:1|A|', 1)


def checks(program, path, name):
    assert name in ('cast-preserves-inline-undef-comparison', 'raw-nonpublic-virtual-snapshot')
    return order(program, path) if name == 'cast-preserves-inline-undef-comparison' else shape(program, path)
