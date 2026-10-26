"""Reached mixed-table snapshots and direct dynamic last-owner retirement."""
import base64
import json
from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $class_instanceof(S, POBJECT n, $ptascii("MixedDynamicVictim126"))
  -- if $np_output(S.EVENTS) = $ptascii("B|H:1|K|")
def $np_stage(S, 4) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.RESULT = KNOWN (PINT $(-1))
'''


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def checks(program, path, name):
    assert name in ('right-copy-live-declared-slot','dynamic-direct-last-owner')
    death = name == 'dynamic-direct-last-owner'
    box = 'MixedReleaseBox126' if death else 'MixedCopyBox126'
    label = 'MixedReleaseNumber126' if death else 'MixedNumber126'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S','S_initial',0),
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(28 if death else 27),
        'perrorcall.MESSAGE = ' + text('Object of class ' + label + ' could not be converted to int'),
        '$error_call_valid(S,perrorcall)', '$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare)',
        'pnumbercompare.TARGET = PINT 1 /\\ pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.SOURCE.OP = SPACESHIP',
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_STD_HASH n_oldleft n_oldright',
        'paggregatecursor.LEFT = HOBJECT n_left',
        'paggregatecursor.RIGHT = HOBJECT n_right',
        'paggregatecursor.INDEX = 1 /\\ paggregatecursor.WIDTH = 3',
        'paggregatecursor.KEY = KSTRING ptbytes_front',
        'ptbytes_front = [0] ++ ' + text(box) + ' ++ [0] ++ $ptascii("front")',
        'ptbytes_tail = [0] ++ ' + text(box) + ' ++ [0] ++ $ptascii("tail")',
        'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number)',
        'paggregatecursor.RIGHTITEM = DIRECT (PINT 1)',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_ARRAY n_oldright (KSTRING ptbytes_front))',
        '$lookup(S.ENV,$ptascii("left")) = (n_leftcv)',
        'S.STORE[n_leftcv] = DEFINED (POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("right")) = (n_rightcv)',
        'S.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_oldleft)',
        '$object_table_at(S.OBJECTTABLES,n_right) = (n_oldright)',
        '$objectprops_at(S.OBJECTPROPS,n_right) = ([ppropertyslot_front,ppropertyslot_tail,ppropertyslot_dynamic])',
        'ppropertyslot_front.NAME = ptbytes_front /\\ ppropertyslot_front.DECL =/= eps',
        'ppropertyslot_tail.NAME = ptbytes_tail /\\ ppropertyslot_tail.DECL =/= eps',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (PINT 7))',
        'ppropertyslot_dynamic.NAME = $ptascii("dynamic") /\\ ppropertyslot_dynamic.DECL = eps',
        '$aggregate_std_pair(S,n_left,n_right)', '~$aggregate_decl_pair(S,n_left,n_right)',
        '$aggregate_cursor_valid(S,paggregatecursor)',
        '$aggregate_hash_image(S,n_left,n_oldleft) /\\ $aggregate_hash_image(S,n_right,n_oldright)',
        owners('S','HARRAY n_oldleft',2), owners('S','HARRAY n_oldright',2),
        '$number_compare_other(S,pnumbercompare) = (PINT 1)', '$np_guard(S)',
        '$np_output(S.EVENTS) = $ptascii("B|")',
    ]
    old = 'POBJECT n_victim' if death else 'PINT 0'
    values += [
        'ppropertyslot_dynamic.STATE = PROP_VALUE (DIRECT (' + old + '))',
        'S.ARRAYS[n_oldright].ITEMS = [ENTRY (KSTRING ptbytes_front) (INDIRECT n_right ptbytes_front),ENTRY (KSTRING ptbytes_tail) (INDIRECT n_right ptbytes_tail),ENTRY (KSTRING ($ptascii("dynamic"))) (DIRECT (' + old + '))]',
    ]
    if death:
        values += [owners('S','HOBJECT n_victim',1),
            '$class_instanceof(S,POBJECT n_victim,$ptascii("MixedDynamicVictim126"))']
    values += [
        *seek('S_return','S',1),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.RESULT = KNOWN (PBOOL true)', '$np_guard(S_return)',
        *seek('S_resume','S_return',2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        'S_resume.DESTRUCTION.OPERATIONS = eps /\\ S_resume.DESTRUCTION.RELEASES = eps',
        '$aggregate_cursor_valid(S_resume,paggregatecursor)',
        '$object_table_at(S_resume.OBJECTTABLES,n_left) = (n_oldleft)',
        '$object_table_at(S_resume.OBJECTTABLES,n_right) = (n_newright)',
        'n_newright =/= n_oldright',
        'S_resume.ARRAYS[n_oldleft] = S.ARRAYS[n_oldleft]',
        'S_resume.ARRAYS[n_oldright] = S.ARRAYS[n_oldright]',
        'S_resume.ARRAYS[n_newright].ITEMS = [ENTRY (KSTRING ptbytes_front) (DIRECT (PINT 1)),ENTRY (KSTRING ptbytes_tail) (DIRECT (PINT 7))' + (']' if death else ',ENTRY (KSTRING ($ptascii("dynamic"))) (DIRECT (PINT 9))]'),
        '$object_table_item(S_resume,INDIRECT n_right ptbytes_tail) = DIRECT (PINT 0)',
        '$objectprops_at(S_resume.OBJECTPROPS,n_right) = ([ppropertyslot_front,ppropertyslot_tail[.STATE = PROP_VALUE (DIRECT (PINT 0))],ppropertyslot_dynamic[.STATE = ' + ('PROP_UNSET' if death else 'PROP_VALUE (DIRECT (PINT 9))') + ']])',
        '$object_table_dynamic_history($object_table_slots_at(S_resume,n_right))',
        '$object_table_ordinary(S_resume,n_right)',
        '$aggregate_hash_image(S_resume,n_right,n_oldright) /\\ $aggregate_hash_image(S_resume,n_right,n_newright)',
        '~$object_table_current_entries($object_table_slots_at(S_resume,n_right),S_resume.ARRAYS[n_oldright].ITEMS)',
        owners('S_resume','HARRAY n_oldright',1), owners('S_resume','HARRAY n_newright',1),
        owners('S_resume','HARRAY n_oldleft',2),
        '$number_compare_other(S_resume,pnumbercompare) = (PINT 1)',
        '$np_output(S_resume.EVENTS) = ' + text('B|H:1|K|' if death else 'B|H:1|'), '$np_guard(S_resume)',
    ]
    if death: values += [owners('S_resume','HOBJECT n_victim',1)]
    result = 'PINT $(-1)' if death else 'PINT 0'
    values += [
        'PhpStep: S_resume ~> S_raw', 'S_raw.RESULT = KNOWN (' + result + ')',
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
    ]
    if death:
        values += [
            '(HOBJECT n_victim) <- S_raw.ALLOCATIONS', owners('S_raw','HOBJECT n_victim',0),
            'S_after.RESULT = KNOWN PNULL',
            'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
            'pdestructionoperation.VALUE = KNOWN (PINT $(-1))',
            'pdestructionoperation.SOURCE = NUMBER_COMPARE_RESULT pnumbercompare',
            'pdestructionoperation.PENDING = eps', '$np_guard(S_after)',
            *seek('S_destructor','S_after',3),
            'S_destructor.CURRENT = (pcallcontext_destructor)',
            'pcallcontext_destructor.TARGET = METHOD_TARGET n_victim porigin_destructor',
            '$destructor_selected_pending(S_destructor,$destructor_selected_frame(S_destructor)) = eps',
            '$np_guard(S_destructor)',
            *seek('S_retired','S_destructor',4),
            'S_retired.TODO = pnumbercompare.SOURCE.TAIL',
            '~$heap_member(HOBJECT n_victim,S_retired.ALLOCATIONS)',
            '$np_output(S_retired.EVENTS) = $ptascii("B|H:1|K|D|")', '$np_guard(S_retired)',
            'S_done = $drive_steps(S_retired,4000)',
        ]
    else:
        values += [
            'S_after.RESULT = KNOWN (PINT 0)', 'S_after.TODO = pnumbercompare.SOURCE.TAIL',
            '~$heap_member(HARRAY n_oldright,S_after.ALLOCATIONS)',
            '$object_table_at(S_after.OBJECTTABLES,n_right) = (n_newright)',
            owners('S_after','HARRAY n_newright',1), owners('S_after','HARRAY n_oldleft',1),
            '$np_guard(S_after)',
            'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],4000)',
        ]
    values += [
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text('B|H:1|K|D|R:1:1:1|A|' if death else 'B|H:1|R:1:1:1:1|A|'),
        '$np_guard(S_done)',
    ]
    if death: values += ['~$heap_member(HOBJECT n_victim,S_done.ALLOCATIONS)']
    return values
