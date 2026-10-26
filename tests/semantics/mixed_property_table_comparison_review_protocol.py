"""Reached mixed buckets: old table snapshots, live slots and surviving cells."""
import base64
import json

from nonpublic_numeric_comparison_review_protocol import PREFIX, seek, text


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def front(program, path, cell):
    label = 'CellCopyNumber126R' if cell else 'LeftCopyNumber126R'
    box = 'CellCopyBox126R' if cell else 'LeftCopyBox126R'
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 0),
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(24 if cell else 26),
        'perrorcall.MESSAGE = ' + text('Object of class ' + label + ' could not be converted to int'),
        '$error_call_valid(S,perrorcall)', '$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$number_compare_valid(S,pnumbercompare)', '$aggregate_compare_source(S,pnumbercompare.SOURCE)',
        'S.CURRENT = eps /\\ S.FRAMES = eps',
        'pnumbercompare.TARGET = PINT 1 /\\ pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.POINTER = eps',
        'pnumbercompare.SOURCE.OP = ' + ('EQUAL' if cell else 'SPACESHIP'),
        'pnumbercompare.SOURCE.CAST.OBJECTLEFT = true',
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_STD_HASH n_oldleft n_oldright',
        'paggregatecursor.LEFT = HOBJECT n_left',
        'paggregatecursor.RIGHT = HOBJECT n_right',
        'paggregatecursor.INDEX = 1 /\\ paggregatecursor.WIDTH = ' + str(2 if cell else 3),
        'paggregatecursor.KEY = KSTRING ptbytes_front',
        'ptbytes_front = [0] ++ ' + text(box) + ' ++ [0] ++ $ptascii("front")',
        'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number)',
        'paggregatecursor.RIGHTITEM = DIRECT (PINT 1)',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_ARRAY n_oldright (KSTRING ptbytes_front))',
        'pnumbercompare.SOURCE.ROOTLEFT = POBJECT n_left /\\ pnumbercompare.SOURCE.ROOTRIGHT = POBJECT n_right',
        '$lookup(S.ENV,$ptascii("left")) = (n_leftcv)',
        'S.STORE[n_leftcv] = DEFINED (POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("right")) = (n_rightcv)',
        'S.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        'S.OBJECTS[n_left] = INSTANCE porigin_class',
        'S.OBJECTS[n_right] = INSTANCE porigin_class',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_oldleft)',
        '$object_table_at(S.OBJECTTABLES,n_right) = (n_oldright)',
        '$object_table_ordinary(S,n_left) /\\ $object_table_ordinary(S,n_right)',
        '$aggregate_std_pair(S,n_left,n_right)', '~$aggregate_decl_pair(S,n_left,n_right)',
        '$aggregate_cursor_valid(S,paggregatecursor)',
        '$aggregate_hash_image(S,n_left,n_oldleft) /\\ $aggregate_hash_image(S,n_right,n_oldright)',
        '$aggregate_cursor_pins([paggregatecursor]) = [HOBJECT n_left,HOBJECT n_right,HARRAY n_oldleft,HARRAY n_oldright]',
        '$aggregate_cursor_guard(paggregatecursor) = HARRAY n_oldleft',
        '$number_compare_other(S,pnumbercompare) = (PINT 1)',
        owners('S', 'HARRAY n_oldleft', 2), owners('S', 'HARRAY n_oldright', 2),
        owners('S', 'HOBJECT n_number', 1),
        '~$aggregate_decl_public($property_layout(S,porigin_class,|S.CLASSES|))',
        '$object_table_dynamic_history($object_table_slots_at(S,n_left))',
        '$aggregate_std_cast_order(S,n_left,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERUNSUPPORTED "materialized-property Stringable comparison continuation"',
        '$aggregate_std_cast_order(S,n_number,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERSTRING pnumbercompare.SOURCE.CAST',
        '$aggregate_std_cast_order(S,n_left,ORDERNOTICE pnumbercompare.SOURCE.CAST (PINT 1)) = ORDERNOTICE pnumbercompare.SOURCE.CAST (PINT 1)',
        '$aggregate_std_cast_order(S,n_left,ORDER 0) = ORDER 0',
        '$np_output(S.EVENTS) = $ptascii("B|")', '$np_guard(S)',
    ]


def copied():
    return [
        'ptbytes_sentinel = [0] ++ $ptascii("LeftCopyBox126R") ++ [0] ++ $ptascii("sentinel")',
        '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_front,ppropertyslot_sentinel,ppropertyslot_dynamic])',
        'ppropertyslot_front.NAME = ptbytes_front /\\ ppropertyslot_front.DECL =/= eps',
        'ppropertyslot_sentinel.NAME = ptbytes_sentinel /\\ ppropertyslot_sentinel.DECL =/= eps',
        'ppropertyslot_sentinel.STATE = PROP_VALUE (DIRECT (PINT 2))',
        'ppropertyslot_dynamic.DECL = eps /\\ ppropertyslot_dynamic.NAME = $ptascii("tail")',
        'ppropertyslot_dynamic.STATE = PROP_VALUE (DIRECT (PINT 2))',
        'S.ARRAYS[n_oldleft].ITEMS = [ENTRY (KSTRING ptbytes_front) (INDIRECT n_left ptbytes_front),ENTRY (KSTRING ptbytes_sentinel) (INDIRECT n_left ptbytes_sentinel),ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PINT 2))]',
        'S.ARRAYS[n_oldright].ITEMS = [ENTRY (KSTRING ptbytes_front) (INDIRECT n_right ptbytes_front),ENTRY (KSTRING ptbytes_sentinel) (INDIRECT n_right ptbytes_sentinel),ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PINT 3))]',
        'S_plain = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_front,ppropertyslot_sentinel])][.OBJECTTABLES = $object_table_remove(S.OBJECTTABLES,n_left)]',
        '~$object_table_dynamic_history($object_table_slots_at(S_plain,n_left))',
        '~$object_table_ordinary(S_plain,n_left)',
        'S_bad = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_front,ppropertyslot_sentinel,ppropertyslot_dynamic[.STATE = PROP_VALUE (INDIRECT n_left ptbytes_front)]])]',
        '~$object_table_ordinary(S_bad,n_left)',
        *seek('S_return', 'S', 1),
        *resume(),
        '$object_table_at(S_resume.OBJECTTABLES,n_left) = (n_newleft)',
        'n_newleft =/= n_oldleft', '$object_table_at(S_resume.OBJECTTABLES,n_right) = (n_oldright)',
        'S_resume.ARRAYS[n_oldleft] = S.ARRAYS[n_oldleft]',
        'S_resume.ARRAYS[n_oldright] = S.ARRAYS[n_oldright]',
        'S_resume.ARRAYS[n_newleft].ITEMS = [ENTRY (KSTRING ptbytes_front) (DIRECT (POBJECT n_number)),ENTRY (KSTRING ptbytes_sentinel) (DIRECT (PINT 2)),ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PINT 9))]',
        '$object_table_item(S_resume,INDIRECT n_left ptbytes_sentinel) = DIRECT (PINT 1)',
        '$objectprops_at(S_resume.OBJECTPROPS,n_left) = ([ppropertyslot_front,ppropertyslot_sentinel[.STATE = PROP_VALUE (DIRECT (PINT 1))],ppropertyslot_dynamic[.STATE = PROP_VALUE (DIRECT (PINT 9))]])',
        '$aggregate_hash_image(S_resume,n_left,n_oldleft) /\\ $aggregate_hash_image(S_resume,n_left,n_newleft)',
        '~$object_table_current_entries($object_table_slots_at(S_resume,n_left),S_resume.ARRAYS[n_oldleft].ITEMS)',
        owners('S_resume','HARRAY n_oldleft',1), owners('S_resume','HARRAY n_newleft',1),
        owners('S_resume','HARRAY n_oldright',2), owners('S_resume','HOBJECT n_number',2),
        *finish('KNOWN (PINT $(-1))'),
    ]


def retained_cell():
    return [
        '$lookup(S.ENV,$ptascii("outside")) = (n_outside)',
        'S.STORE[n_outside] = DEFINED (PINT 0)',
        '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_front,ppropertyslot_dynamic])',
        'ppropertyslot_front.NAME = ptbytes_front /\\ ppropertyslot_front.DECL =/= eps',
        'ppropertyslot_dynamic.DECL = eps /\\ ppropertyslot_dynamic.NAME = $ptascii("tail")',
        'ppropertyslot_dynamic.STATE = PROP_VALUE (ALIAS n_outside)',
        'S.ARRAYS[n_oldleft].ITEMS = [ENTRY (KSTRING ptbytes_front) (INDIRECT n_left ptbytes_front),ENTRY (KSTRING ($ptascii("tail"))) (ALIAS n_outside)]',
        'S.ARRAYS[n_oldright].ITEMS = [ENTRY (KSTRING ptbytes_front) (INDIRECT n_right ptbytes_front),ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PINT 9))]',
        owners('S','HCELL n_outside',3),
        *seek('S_return','S',1),
        *resume(),
        '$object_table_at(S_resume.OBJECTTABLES,n_left) = (n_newleft)',
        'n_newleft =/= n_oldleft', '$object_table_at(S_resume.OBJECTTABLES,n_right) = (n_oldright)',
        'S_resume.ARRAYS[n_oldleft] = S.ARRAYS[n_oldleft]',
        'S_resume.ARRAYS[n_newleft].ITEMS = [ENTRY (KSTRING ptbytes_front) (DIRECT (POBJECT n_number))]',
        '$objectprops_at(S_resume.OBJECTPROPS,n_left) = ([ppropertyslot_front,ppropertyslot_dynamic[.STATE = PROP_UNSET]])',
        '$object_table_dynamic_history($object_table_slots_at(S_resume,n_left))',
        '$object_table_ordinary(S_resume,n_left)',
        'S_resume.STORE[n_outside] = DEFINED (PINT 9)',
        '$call_reference_operand_valid(S_resume,REFERENCE n_outside)',
        '$aggregate_hash_image(S_resume,n_left,n_oldleft)',
        '$aggregate_pointer_value(S_resume,AGGREGATE_CELL n_outside) = (PINT 9)',
        owners('S_resume','HCELL n_outside',3),
        owners('S_resume','HARRAY n_oldleft',1), owners('S_resume','HARRAY n_newleft',1),
        *finish('KNOWN (PBOOL true)', cell=True),
    ]


def resume():
    return [
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.RESULT = KNOWN (PBOOL true)', '$np_guard(S_return)',
        *seek('S_resume','S_return',2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$aggregate_cursor_valid(S_resume,paggregatecursor)',
        '$np_output(S_resume.EVENTS) = $ptascii("B|H:1|")', '$np_guard(S_resume)',
    ]


def finish(result, cell=False):
    return [
        'PhpStep: S_resume ~> S_raw', 'S_raw.RESULT = ' + result,
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = ' + result, 'S_after.TODO = pnumbercompare.SOURCE.TAIL',
        '~((HARRAY n_oldleft) <- S_after.ALLOCATIONS)',
        '(HARRAY n_newleft) <- S_after.ALLOCATIONS',
        '$object_table_at(S_after.OBJECTTABLES,n_left) = (n_newleft)',
        owners('S_after','HARRAY n_newleft',1), owners('S_after','HARRAY n_oldright',1),
        *([owners('S_after','HCELL n_outside',2)] if cell else []),
        '$np_guard(S_after)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = $ptascii("B|H:1|R:1:1:1:1|A|")',
        '$np_guard(S_done)',
    ]


def checks(program, path, name):
    assert name in ('left-copy-live-private-slot','old-table-cell-after-dynamic-unset')
    cell = name == 'old-table-cell-after-dynamic-unset'
    return front(program,path,cell) + (retained_cell() if cell else copied())
