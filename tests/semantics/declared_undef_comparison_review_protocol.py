"""Reached canonical UNDEF rows and a surviving selected reference cell."""
import base64
import json

from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 4) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ptbytes)) z
  -- if ptbytes = $ptascii("front")
'''


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def front(program, path, selected):
    line = 27 if selected else 25
    label = 'SelectedAliasNumber125R' if selected else 'InitialHoleNumber125R'
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 0),
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = ' + text('Object of class ' + label + ' could not be converted to int'),
        '$error_call_valid(S,perrorcall)', '$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare)',
        'S.CURRENT = eps /\\ S.FRAMES = eps', 'pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.TARGET = PINT 1', 'pnumbercompare.POINTER = eps',
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_DECL_HASH ptbytes_keys*',
        'paggregatecursor.LEFT = HOBJECT n_compareleft',
        'paggregatecursor.RIGHT = HOBJECT n_compareright',
        'paggregatecursor.INDEX = 1 /\\ paggregatecursor.WIDTH = 2',
        'paggregatecursor.KEY = KSTRING ptbytes_front',
        'ptbytes_keys* = [ptbytes_front,ptbytes_tail]',
        '$lookup(S.ENV,$ptascii("left")) = (n_leftcv)',
        'S.STORE[n_leftcv] = DEFINED (POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("right")) = (n_rightcv)',
        'S.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        'S.OBJECTS[n_left] = INSTANCE porigin_class',
        'S.OBJECTS[n_right] = INSTANCE porigin_class',
        '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_leftfront,ppropertyslot_lefttail])',
        '$objectprops_at(S.OBJECTPROPS,n_right) = ([ppropertyslot_rightfront,ppropertyslot_righttail])',
        '$aggregate_decl_image(S,n_left,ptbytes_keys*) /\\ $aggregate_decl_image(S,n_right,ptbytes_keys*)',
        '$aggregate_cursor_valid(S,paggregatecursor)',
        '$np_output(S.EVENTS) = $ptascii("B|")', '$np_guard(S)',
        '$aggregate_decl_item(PROP_INITIAL) = (UNINITIALIZED)',
        '$aggregate_decl_item(PROP_UNSET) = (UNINITIALIZED)',
        '$aggregate_decl_item(PROP_VALUE UNINITIALIZED) = eps',
        '$aggregate_item_order_effect(S,UNINITIALIZED,DIRECT (PINT 0),eps,0) = (S,ORDER $(-1))',
        '$aggregate_item_order_effect(S,DIRECT (PINT 0),UNINITIALIZED,eps,0) = (S,ORDER 1)',
        '$aggregate_item_order_effect(S,UNINITIALIZED,UNINITIALIZED,eps,0) = (S,ORDER 0)',
        '$number_compare_other_tasks([NUMBER_COMPARE_RESULT pnumbercompare],n_compareleft) = false',
        '$number_compare_other_tasks([AGGREGATE_COMPARE_RESULT pnumbercompare.SOURCE],n_compareleft)',
        '$aggregate_parked_views(S) = eps',
    ]


def selected_front():
    return [
        'n_compareleft = n_left /\\ n_compareright = n_right',
        'ptbytes_front = [0,42,0] ++ $ptascii("front")',
        'ptbytes_tail = [0] ++ $ptascii("SelectedAliasBox125R") ++ [0] ++ $ptascii("tail")',
        'pnumbercompare.SOURCE.OP = EQUAL /\\ pnumbercompare.SOURCE.CAST.OBJECTLEFT = true',
        'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number)',
        'paggregatecursor.RIGHTITEM = ALIAS n_oldcell',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_CELL n_oldcell)',
        '$lookup(S.ENV,$ptascii("opposite")) = (n_oldcell)',
        'S.STORE[n_oldcell] = DEFINED (PINT 0)',
        '$call_reference_operand_valid(S,REFERENCE n_oldcell)',
        'ppropertyslot_rightfront.STATE = PROP_VALUE (ALIAS n_oldcell)',
        'ppropertyslot_lefttail.STATE = PROP_VALUE (DIRECT (PINT 7))',
        'ppropertyslot_righttail.STATE = PROP_VALUE (DIRECT (PINT 7))',
        '$number_compare_other(S,pnumbercompare) = (PINT 0)',
        owners('S','HCELL n_oldcell',3),
        *seek('S_drop','S',4),
        'S_drop.CURRENT = (pcallcontext_drop)',
        'pcallcontext_drop.TARGET = METHOD_TARGET n_right porigin_drop',
        'S_drop.BASE = BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver',
        'S_resolved = $property_pending_resolve(S_drop,pbase_receiver,poperand_name,PPUNSET,z_receiver,$property_current_line(S_drop))',
        'S_resolved.COMPLETION = NORMAL',
        'S_resolved.BASE = BASE_PROPERTY (POBJECT n_right) ($ptascii("front"))',
        '$property_resolve(S_drop,n_right,$ptascii("front")) = PROPERTY_ACCESS ptbytes_front',
        '$aggregate_local_declared(S_drop,n_right)',
        '~$number_compare_other_local(S_drop,n_right)',
        '$aggregate_parked_views(S_drop) = eps',
        '$eager_operation_pending(S_drop) = eps',
        '$destructor_selected_pending(S_drop,$destructor_selected_frame(S_drop)) = eps',
        '$number_compare_decl_unset_allowed(S_drop,n_right,ptbytes_front)',
        '~$number_compare_decl_unset_allowed(S_drop,n_right,$ptascii("front"))',
        '~$number_compare_decl_unset_allowed(S_drop,n_right,$ptascii("missing"))',
        '$np_output(S_drop.EVENTS) = $ptascii("B|H:1|")', '$np_guard(S_drop)',
        'PhpStep: S_drop ~> S_unset_raw',
        '$objectprops_at(S_unset_raw.OBJECTPROPS,n_right) = ([ppropertyslot_rightfront[.STATE = PROP_UNSET],ppropertyslot_righttail])',
        'S_unset_raw.STORE[n_oldcell] = DEFINED (PINT 0)',
        '$aggregate_pointer_value(S_unset_raw,AGGREGATE_CELL n_oldcell) = (PINT 0)',
        '$aggregate_pointer_value(S_unset_raw,AGGREGATE_PROPERTY n_right ptbytes_front) = eps',
        'S_drop_done = $drive_steps(S_drop,1)', 'S_drop_done.COMPLETION = BUDGET',
        *seek('S_return','S_drop_done',1),
    ]


def initial_front():
    return [
        'n_compareleft = n_right /\\ n_compareright = n_left',
        'ptbytes_front = [0] ++ $ptascii("InitialHoleBox125R") ++ [0] ++ $ptascii("front")',
        'ptbytes_tail = [0] ++ $ptascii("InitialHoleBox125R") ++ [0] ++ $ptascii("tail")',
        'pnumbercompare.SOURCE.OP = GREATER /\\ pnumbercompare.SOURCE.CAST.OBJECTLEFT = false',
        'paggregatecursor.LEFTITEM = DIRECT (PINT 1)',
        'paggregatecursor.RIGHTITEM = DIRECT (POBJECT n_number)',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_PROPERTY n_right ptbytes_front)',
        'ppropertyslot_lefttail.STATE = PROP_INITIAL',
        'ppropertyslot_righttail.STATE = PROP_VALUE (DIRECT (PINT 7))',
        '$property_desc_at($property_layout(S,porigin_class,|S.CLASSES|),ptbytes_tail) = (ppropertydesc_tail)',
        'ppropertydesc_tail.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc_tail.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
        '~$aggregate_decl_initialized($object_table_slots_at(S,n_left))',
        '$aggregate_decl_initialized($object_table_slots_at(S,n_right))',
        '$object_table_item(S,INDIRECT n_left ptbytes_tail) = UNINITIALIZED',
        '$number_compare_other(S,pnumbercompare) = (PINT 1)',
        *seek('S_return','S',1),
    ]


def finish(selected):
    return [
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.CURRENT = eps /\\ S_return.FRAMES = eps',
        'S_return.RESULT = KNOWN (PBOOL true)', '$np_guard(S_return)',
        *seek('S_resume','S_return',2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$np_output(S_resume.EVENTS) = $ptascii("B|H:1|")', '$np_guard(S_resume)',
        *([
            'S_resume.STORE[n_oldcell] = DEFINED (PINT 1)',
            '$objectprops_at(S_resume.OBJECTPROPS,n_right) = ([ppropertyslot_rightfront[.STATE = PROP_UNSET],ppropertyslot_righttail])',
            '$number_compare_other(S_resume,pnumbercompare) = (PINT 1)',
            '$aggregate_pointer_value(S_resume,AGGREGATE_PROPERTY n_right ptbytes_front) = eps',
            '$call_reference_operand_valid(S_resume,REFERENCE n_oldcell)',
            owners('S_resume','HCELL n_oldcell',2),
        ] if selected else [
            '$objectprops_at(S_resume.OBJECTPROPS,n_left) = ([ppropertyslot_leftfront,ppropertyslot_lefttail[.STATE = PROP_VALUE (DIRECT (PINT 8))]])',
            '$aggregate_decl_initialized($object_table_slots_at(S_resume,n_left))',
            '$number_compare_other(S_resume,pnumbercompare) = (PINT 1)',
            '$aggregate_decl_effect(S_resume,n_right,n_left,ptbytes_keys*,1,$aggregate_cursor_lefts([paggregatecursor]),25) = (S_resume,ORDER $(-1))',
        ]),
        'PhpStep: S_resume ~> S_raw', 'S_raw.RESULT = KNOWN (PBOOL true)',
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN (PBOOL true)', '$np_guard(S_after)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text('B|H:1|R:1:1:1:1|A|' if selected else 'B|H:1|R:1:1:1|A|'),
        '$np_guard(S_done)',
    ]


def checks(program,path,name):
    assert name in ('selected-alias-property-unset','initial-typed-hole-filled')
    selected = name == 'selected-alias-property-unset'
    return front(program,path,selected) + (selected_front() if selected else initial_front()) + finish(selected)
