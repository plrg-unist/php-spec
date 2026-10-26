"""Reached backing-slot comparison with real setters and selected cells."""
import base64
import json
from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook
  -- if $np_output(S.EVENTS) = $ptascii("B|H:1|")
'''


def checks(program, path, name):
    assert name in ('cached-backing-skips-get-runs-set', 'backed-set-mutates-selected-cell')
    cell = name == 'backed-set-mutates-selected-cell'
    number = 'HookCellNumber127' if cell else 'HookTableNumber127'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 0),
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(28 if cell else 27),
        'perrorcall.MESSAGE = ' + text('Object of class ' + number + ' could not be converted to int'),
        '$error_call_valid(S,perrorcall)', '$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare)',
        'S.CURRENT = eps /\\ S.FRAMES = eps',
        'pnumbercompare.TARGET = PINT 1 /\\ pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.SOURCE.OP = SPACESHIP',
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_STD_HASH n_lefttable n_righttable',
        'paggregatecursor.LEFT = HOBJECT n_left', 'paggregatecursor.RIGHT = HOBJECT n_right',
        'paggregatecursor.WIDTH = 3 /\\ paggregatecursor.INDEX = 1',
        'paggregatecursor.KEY = KSTRING ($ptascii("front"))',
        'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number)',
        '$lookup(S.ENV,$ptascii("left")) = (n_leftcv)',
        'S.STORE[n_leftcv] = DEFINED (POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("right")) = (n_rightcv)',
        'S.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        'S.OBJECTS[n_left] = INSTANCE porigin_class',
        'S.OBJECTS[n_right] = INSTANCE porigin_class',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_lefttable)',
        '$object_table_at(S.OBJECTTABLES,n_right) = (n_righttable)',
        '$property_layout(S,porigin_class,|S.CLASSES|) = [ppropertydesc_front,ppropertydesc_value]',
        'ppropertydesc_value.NAME = $ptascii("value") /\\ ppropertydesc_value.KEY = $ptascii("value")',
        'ppropertydesc_value.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
        '~$property_hook_virtual(S,ppropertydesc_value)',
        '$property_hook_origin(S,ppropertydesc_value) = (porigin_get)',
        '$property_set_origin(S,ppropertydesc_value) = (porigin_set)',
        'porigin_get =/= porigin_set',
        '$objectprops_at(S.OBJECTPROPS,n_right) = ([ppropertyslot_front,ppropertyslot_value,ppropertyslot_tag])',
        'ppropertyslot_value.DECL = (ppropertydesc_value.ORIGIN)',
        'ppropertyslot_value.NAME = $ptascii("value")',
        'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
        'ppropertyslot_tag.DECL = eps /\\ ppropertyslot_tag.NAME = $ptascii("tag")',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 0))',
        '$aggregate_decl_public($property_layout(S,porigin_class,|S.CLASSES|))',
        '$aggregate_backed_hook_slot(S,n_right,ppropertyslot_value)',
        '$aggregate_backed_hook_rows(S,n_right,$object_table_slots_at(S,n_right))',
        '$aggregate_std_cast_order(S,n_right,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERUNSUPPORTED "materialized-property Stringable comparison continuation"',
        '$aggregate_std_cast_order(S,n_right,ORDERNOTICE pnumbercompare.SOURCE.CAST (PINT 1)) = ORDERNOTICE pnumbercompare.SOURCE.CAST (PINT 1)',
        '$aggregate_std_cast_order(S,n_number,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERSTRING pnumbercompare.SOURCE.CAST',
        '$object_table_ordinary(S,n_left) /\\ $object_table_ordinary(S,n_right)',
        '$aggregate_std_pair(S,n_left,n_right)', '$aggregate_cursor_valid(S,paggregatecursor)',
        '$aggregate_hash_image(S,n_right,n_righttable)',
        '$entry_lookup(S.ARRAYS[n_righttable].ITEMS,KSTRING ($ptascii("value"))) = (INDIRECT n_right ($ptascii("value")))',
        '$object_table_item(S,INDIRECT n_right ($ptascii("value"))) = DIRECT (PINT 7)',
        '$lookup(S.ENV,$ptascii("gets")) = (n_gets)', 'S.STORE[n_gets] = DEFINED (PINT 0)',
        '$lookup(S.ENV,$ptascii("sets")) = (n_sets)', 'S.STORE[n_sets] = DEFINED (PINT 0)',
        '~$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare[.SOURCE.LINE = 999])',
        '$np_output(S.EVENTS) = $ptascii("B|")', '$np_guard(S)',
    ]
    if cell:
        values += [
            '$lookup(S.ENV,$ptascii("opposite")) = (n_opposite)',
            'S.STORE[n_opposite] = DEFINED (PINT 0)',
            'paggregatecursor.RIGHTITEM = ALIAS n_opposite',
            'ppropertyslot_front.STATE = PROP_VALUE (ALIAS n_opposite)',
            'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_CELL n_opposite)',
            '$number_compare_other(S,pnumbercompare) = (PINT 0)',
        ]
    else:
        values += [
            'paggregatecursor.RIGHTITEM = DIRECT (PINT 1)',
            'ppropertyslot_front.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_ARRAY n_righttable (KSTRING ($ptascii("front"))))',
            '$number_compare_other(S,pnumbercompare) = (PINT 1)',
        ]
    values += [
        *seek('S_set', 'S', 3),
        'S_set.CURRENT = (pcallcontext_set)',
        'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_set',
        'ppropertyhook_set.OBJECT = n_right /\\ ppropertyhook_set.PROPERTY = ppropertydesc_value.ORIGIN',
        'ppropertyhook_set.HOOK = porigin_set',
        '$property_set_valid(S_set,ppropertyhook_set)',
        '$property_set_context_valid(S_set,pcallcontext_set)',
        '$property_set_entered(S_set,S_set.CURRENT,S_set.FRAMES,ppropertyhook_set)',
        '$property_set_backing(S_set,n_right,ppropertydesc_value)',
        '~$property_hook_read_needed(S_set,n_right,$ptascii("value"))',
        '$lookup(S_set.ENV,$ptascii("value")) = (n_value)',
        'S_set.STORE[n_value] = DEFINED (PINT 0)',
        'S_set.STORE[n_sets] = DEFINED (PINT 0)',
        'S_set.STORE[n_gets] = DEFINED (PINT 0)',
        '$object_table_item(S_set,INDIRECT n_right ($ptascii("value"))) = DIRECT (PINT 7)',
        '$np_guard(S_set)',
        *seek('S_return', 'S_set', 1),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.RESULT = KNOWN (PBOOL true)',
        'S_return.STORE[n_sets] = DEFINED (PINT 1)',
        'S_return.STORE[n_gets] = DEFINED (PINT 0)', '$np_guard(S_return)',
        *seek('S_resume', 'S_return', 2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        'S_resume.CURRENT = eps /\\ S_resume.FRAMES = eps',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$aggregate_cursor_valid(S_resume,paggregatecursor)',
        '$object_table_at(S_resume.OBJECTTABLES,n_right) = (n_righttable)',
        'S_resume.ARRAYS[n_righttable] = S.ARRAYS[n_righttable]',
        '$objectprops_at(S_resume.OBJECTPROPS,n_right) = ([ppropertyslot_front,ppropertyslot_value[.STATE = PROP_VALUE (DIRECT (PINT 0))],ppropertyslot_tag])',
        '$object_table_item(S_resume,INDIRECT n_right ($ptascii("value"))) = DIRECT (PINT 0)',
        '$number_compare_other(S_resume,pnumbercompare) = (PINT 1)',
        'S_resume.STORE[n_sets] = DEFINED (PINT 1)',
        'S_resume.STORE[n_gets] = DEFINED (PINT 0)',
        '$np_output(S_resume.EVENTS) = $ptascii("B|H:1|")', '$np_guard(S_resume)',
    ]
    if cell:
        values += ['S_resume.STORE[n_opposite] = DEFINED (PINT 1)',
                   '$aggregate_pointer_value(S_resume,AGGREGATE_CELL n_opposite) = (PINT 1)']
    values += [
        'PhpStep: S_resume ~> S_raw', 'S_raw.RESULT = KNOWN (PINT 0)',
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN (PINT 0)', 'S_after.TODO = pnumbercompare.SOURCE.TAIL', '$np_guard(S_after)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text('B|H:1|R:1:1:1:1:1|A|' if cell else 'B|H:1|R:1:1:1:1|V:1:1|A|'),
        'S_done.STORE[n_sets] = DEFINED (PINT 1)',
        'S_done.STORE[n_gets] = DEFINED (PINT ' + ('0' if cell else '1') + ')', '$np_guard(S_done)',
    ]
    return values
