"""Reached raw backing slots, inline destruction and virtual-only omission."""
import base64
import json
from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $class_instanceof(S,POBJECT n,$ptascii("InlineHookVictim127R"))
  -- if $np_output(S.EVENTS) = $ptascii("B|H:1|")
def $np_stage(S, 4) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.RESULT = KNOWN (PINT 1)
  -- if $np_output(S.EVENTS) = $ptascii("B|H:1|D|K|")
def $np_stage(S, 5) = true
  -- if S.TODO = (BINARY_RIGHT EQUAL poperand z) :: ptask_tail*
  -- if $lookup(S.ENV,$ptascii("left")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if $class_instanceof(S,POBJECT n,$ptascii("VirtualOnlyBox127R"))
  -- if $np_output(S.EVENTS) = $ptascii("B|")
'''


def start(program,path,stage):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S','S_initial',stage),
    ]


def owners(state,node,count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def inline_death(program,path):
    return start(program,path,0) + [
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = 32',
        'perrorcall.MESSAGE = $ptascii("Object of class InlineHookNumber127R could not be converted to int")',
        '$error_call_valid(S,perrorcall)', '$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare)',
        'S.CURRENT = eps /\\ S.FRAMES = eps',
        'pnumbercompare.TARGET = PINT 1 /\\ pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.SOURCE.OP = SPACESHIP',
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_STD_HASH n_lefttable n_righttable',
        'paggregatecursor.LEFT = HOBJECT n_left', 'paggregatecursor.RIGHT = HOBJECT n_right',
        'paggregatecursor.WIDTH = 4 /\\ paggregatecursor.INDEX = 1',
        'paggregatecursor.KEY = KSTRING ($ptascii("front"))',
        'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number)',
        'paggregatecursor.RIGHTITEM = DIRECT (PINT 1)',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_ARRAY n_righttable (KSTRING ($ptascii("front"))))',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_lefttable)',
        '$object_table_at(S.OBJECTTABLES,n_right) = (n_righttable)',
        'S.OBJECTS[n_right] = INSTANCE porigin_class',
        '$objectprops_at(S.OBJECTPROPS,n_right) = ([ppropertyslot_front,ppropertyslot_value,ppropertyslot_tail,ppropertyslot_tag])',
        'ppropertyslot_front.STATE = PROP_VALUE (DIRECT (PINT 1))',
        'ppropertyslot_value.NAME = $ptascii("value")',
        'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
        'ppropertyslot_tail.NAME = [0] ++ $ptascii("InlineHookBox127R") ++ [0] ++ $ptascii("tail")',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_victim))',
        'ppropertyslot_tag.NAME = $ptascii("tag") /\\ ppropertyslot_tag.DECL = eps',
        '$property_desc_at($property_layout(S,porigin_class,|S.CLASSES|),$ptascii("value")) = (ppropertydesc_value)',
        'ppropertydesc_value.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
        '~$property_hook_virtual(S,ppropertydesc_value)',
        '$property_hook_declared(S,n_right,$ptascii("value"))',
        '$aggregate_backed_hook_slot(S,n_right,ppropertyslot_value)',
        '$aggregate_backed_hook_rows(S,n_right,$object_table_slots_at(S,n_right))',
        '$object_table_ordinary(S,n_left) /\\ $object_table_ordinary(S,n_right)',
        '$aggregate_std_pair(S,n_left,n_right)', '$aggregate_cursor_valid(S,paggregatecursor)',
        '$aggregate_hash_image(S,n_right,n_righttable)',
        '$entry_lookup(S.ARRAYS[n_righttable].ITEMS,KSTRING ppropertyslot_tail.NAME) = (INDIRECT n_right ppropertyslot_tail.NAME)',
        '$object_table_item(S,INDIRECT n_right ppropertyslot_tail.NAME) = DIRECT (POBJECT n_victim)',
        owners('S','HOBJECT n_victim',1), owners('S','HARRAY n_righttable',2),
        '$np_output(S.EVENTS) = $ptascii("B|")', '$np_guard(S)',
        *seek('S_destructor','S',3),
        'S_destructor.CURRENT = (pcallcontext_destructor)',
        'pcallcontext_destructor.TARGET = METHOD_TARGET n_victim porigin_destructor',
        '$destructor_selected_pending(S_destructor,$destructor_selected_frame(S_destructor)) = eps',
        '$objectprops_at(S_destructor.OBJECTPROPS,n_right) = ([ppropertyslot_front,ppropertyslot_value,ppropertyslot_tail[.STATE = PROP_UNSET],ppropertyslot_tag])',
        '$object_table_at(S_destructor.OBJECTTABLES,n_right) = (n_righttable)',
        'S_destructor.ARRAYS[n_righttable] = S.ARRAYS[n_righttable]',
        '$object_table_item(S_destructor,INDIRECT n_right ppropertyslot_tail.NAME) = UNINITIALIZED',
        '$aggregate_hash_image(S_destructor,n_right,n_righttable)', '$np_guard(S_destructor)',
        *seek('S_return','S_destructor',1),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.RESULT = KNOWN (PBOOL true)',
        *seek('S_resume','S_return',2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        'S_resume.DESTRUCTION.OPERATIONS = eps /\\ S_resume.DESTRUCTION.RELEASES = eps',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$aggregate_cursor_valid(S_resume,paggregatecursor)',
        '$object_table_at(S_resume.OBJECTTABLES,n_right) = (n_righttable)',
        'S_resume.ARRAYS[n_righttable] = S.ARRAYS[n_righttable]',
        '$object_table_item(S_resume,INDIRECT n_right ppropertyslot_tail.NAME) = UNINITIALIZED',
        '$aggregate_table_count(S_resume.ARRAYS[n_righttable].ITEMS) = 4',
        '$number_compare_other(S_resume,pnumbercompare) = (PINT 1)',
        '~$heap_member(HOBJECT n_victim,S_resume.ALLOCATIONS)',
        '$np_output(S_resume.EVENTS) = $ptascii("B|H:1|D|K|")', '$np_guard(S_resume)',
        'PhpStep: S_resume ~> S_raw', 'S_raw.RESULT = KNOWN (PINT 1)',
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN PNULL',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.VALUE = KNOWN (PINT 1)',
        'pdestructionoperation.SOURCE = NUMBER_COMPARE_RESULT pnumbercompare',
        'pdestructionoperation.PENDING = eps', '$np_guard(S_after)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
        *seek('S_retired','S_after',4),
        'S_retired.TODO = pnumbercompare.SOURCE.TAIL', '$np_guard(S_retired)',
        'S_done = $drive_steps(S_retired,4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = $ptascii("B|H:1|D|K|R:1:1:1|A|")',
        '~$heap_member(HOBJECT n_victim,S_done.ALLOCATIONS)', '$np_guard(S_done)',
    ]


def virtual_only(program,path):
    return start(program,path,5) + [
        'S.TODO = (BINARY_RIGHT EQUAL poperand_left z_compare) :: ptask_tail*',
        'z_compare = 17', 'S.CURRENT = eps /\\ S.FRAMES = eps',
        '$lookup(S.ENV,$ptascii("left")) = (n_leftcv)',
        'S.STORE[n_leftcv] = DEFINED (POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("right")) = (n_rightcv)',
        'S.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        'S.OBJECTS[n_left] = INSTANCE porigin_class',
        'S.OBJECTS[n_right] = INSTANCE porigin_class',
        '$property_layout(S,porigin_class,|S.CLASSES|) = [ppropertydesc_plain,ppropertydesc_virtual]',
        '$property_hook_virtual(S,ppropertydesc_virtual)',
        '~$property_hook_virtual(S,ppropertydesc_plain)',
        '$property_hook_instance(S,n_left)',
        '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_plain])',
        'ppropertyslot_plain.DECL = (ppropertydesc_plain.ORIGIN)',
        'ppropertyslot_plain.NAME = $ptascii("plain")',
        'ppropertyslot_plain.STATE = PROP_VALUE (DIRECT (PINT 1))',
        '$aggregate_object_keys(S,n_left) = [$ptascii("plain")]',
        '$object_table_at(S.OBJECTTABLES,n_left) = eps',
        '~$objectprops_materialized(S.OBJECTPROPS,n_left)',
        '$object_table_ordinary(S,n_left)',
        '$aggregate_decl_public($property_layout(S,porigin_class,|S.CLASSES|))',
        '~$aggregate_backed_hook_slot(S,n_left,ppropertyslot_plain)',
        '~$aggregate_backed_hook_rows(S,n_left,$object_table_slots_at(S,n_left))',
        'paggregatecallback_probe = {LEFT (POBJECT n_left),RIGHT (PINT 1),RECEIVER n_left,OBJECTLEFT true,POINTER eps,STACK eps}',
        '$aggregate_std_cast_order(S,n_left,ORDERSTRING paggregatecallback_probe) = ORDERSTRING paggregatecallback_probe',
        'ppropertyslot_virtual = {DECL (ppropertydesc_virtual.ORIGIN),NAME ppropertydesc_virtual.KEY,STATE PROP_VALUE (DIRECT (PINT 1000))}',
        '~$aggregate_backed_hook_slot(S,n_left,ppropertyslot_virtual)',
        '~$aggregate_backed_hook_rows(S,n_left,[ppropertyslot_virtual])',
        'S_bad = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_plain,ppropertyslot_virtual])]',
        '~$object_table_ordinary(S_bad,n_left)',
        '$np_output(S.EVENTS) = $ptascii("B|")', '$np_guard(S)',
        'PhpStep: S ~> S_raw', 'S_raw.RESULT = KNOWN (PBOOL true)', 'S_raw.TODO = ptask_tail*',
        'S_after = $drive_steps(S,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN (PBOOL true)', 'S_after.TODO = ptask_tail*', '$np_guard(S_after)',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = $ptascii("B|R:1:1|A|")', '$np_guard(S_done)',
    ]


def checks(program,path,name):
    assert name in ('indirect-private-tail-inline-destructor','virtual-only-plain-equality')
    return inline_death(program,path) if name == 'indirect-private-tail-inline-destructor' else virtual_only(program,path)
