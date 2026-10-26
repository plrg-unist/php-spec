"""Reached physical-key cursors and normal numeric Notice continuations."""
import base64
import json

PREFIX = r'''
dec $np_stage(pstate, nat) : bool
def $np_stage(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare
def $np_stage(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare
def $np_stage(S, 2) = true -- if S.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask*
def $np_stage(S, n) = false -- otherwise
dec $np_seek(pstate, nat, nat) : pstate
def $np_seek(S, n_stage, n) = S -- if $np_stage(S, n_stage) \/ n = 0
def $np_seek(S, n_stage, n) = $np_seek($drive_steps(S[.COMPLETION = NORMAL],1), n_stage, $nabs($(n - 1)))
  -- if ~$np_stage(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $np_seek(S, n_stage, n) = S -- otherwise
dec $np_guard(pstate) : bool
def $np_guard(S) = ($call_descriptors_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $np_event_output(pevent) : ptbytes
def $np_event_output(OUTPUT ptbytes) = ptbytes
def $np_event_output(pevent) = eps -- otherwise
dec $np_output(pevent*) : ptbytes
def $np_output(eps) = eps
def $np_output(pevent :: pevent_tail*) = $np_event_output(pevent) ++ $np_output(pevent_tail*)
'''


def text(value):
    return '$ptascii(' + json.dumps(value) + ')'


def seek(target, source, stage):
    return [
        target + '_found = $np_seek(' + source + ',' + str(stage) + ',4000)',
        target + '_found.COMPLETION = NORMAL \\/ ' + target + '_found.COMPLETION = BUDGET',
        target + ' = ' + target + '_found[.COMPLETION = NORMAL]',
        '$np_stage(' + target + ',' + str(stage) + ')',
    ]


def front(program, path, name):
    shadow = name == 'private-shadow-physical-key'
    line = 30 if shadow else 28
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 0),
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = ' + text('Object of class ' + ('ShadowNumber124R' if shadow else 'ReverseNumber124R') + ' could not be converted to int'),
        '$call_task_valid(S,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$number_compare_valid(S,pnumbercompare)', '$aggregate_compare_source(S,pnumbercompare.SOURCE)',
        'S.CURRENT = eps /\\ S.FRAMES = eps',
        'pnumbercompare.TARGET = PINT 1 /\\ pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.POINTER = eps',
        'pnumbercompare.SOURCE.OP = ' + ('SPACESHIP' if shadow else 'LESSEQUAL'),
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_DECL_HASH ptbytes_keys*',
        'paggregatecursor.LEFT = HOBJECT n_left /\\ paggregatecursor.RIGHT = HOBJECT n_right',
        'paggregatecursor.WIDTH = 2 /\\ paggregatecursor.INDEX = 1',
        'paggregatecursor.KEY = KSTRING ptbytes_first',
        'ptbytes_keys* = [ptbytes_first,ptbytes_second]',
        'pnumbercompare.SOURCE.ROOTLEFT = POBJECT n_left /\\ pnumbercompare.SOURCE.ROOTRIGHT = POBJECT n_right',
        'S.OBJECTS[n_left] = INSTANCE porigin_class /\\ S.OBJECTS[n_right] = INSTANCE porigin_class',
        '$lookup(S.ENV,$ptascii("left")) = (n_leftcv) /\\ S.STORE[n_leftcv] = DEFINED (POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("right")) = (n_rightcv) /\\ S.STORE[n_rightcv] = DEFINED (POBJECT n_right)',
        '$property_layout(S,porigin_class,|S.CLASSES|) = [ppropertydesc_first,ppropertydesc_second]',
        'ppropertydesc_first.KEY = ptbytes_first /\\ ppropertydesc_second.KEY = ptbytes_second',
        'ppropertydesc_first.ORIGIN =/= ppropertydesc_second.ORIGIN',
        '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_leftfirst,ppropertyslot_leftsecond])',
        '$objectprops_at(S.OBJECTPROPS,n_right) = ([ppropertyslot_rightfirst,ppropertyslot_rightsecond])',
        'ppropertyslot_leftfirst.DECL = (ppropertydesc_first.ORIGIN) /\\ ppropertyslot_rightfirst.DECL = (ppropertydesc_first.ORIGIN)',
        'ppropertyslot_leftsecond.DECL = (ppropertydesc_second.ORIGIN) /\\ ppropertyslot_rightsecond.DECL = (ppropertydesc_second.ORIGIN)',
        '$aggregate_decl_image(S,n_left,ptbytes_keys*) /\\ $aggregate_decl_image(S,n_right,ptbytes_keys*)',
        '$objectprops_materialized(S.OBJECTPROPS,n_left) /\\ $objectprops_materialized(S.OBJECTPROPS,n_right)',
        '$aggregate_decl_pair(S,n_left,n_right) /\\ $aggregate_cursor_valid(S,paggregatecursor)',
        '$aggregate_cursor_pins([paggregatecursor]) = [HOBJECT n_left,HOBJECT n_right]',
        '$aggregate_cursor_guard(paggregatecursor) = DECLARED_TABLE n_left',
        '$heap_subset([HOBJECT n_left,HOBJECT n_right],$number_compare_nodes(pnumbercompare))',
        '$np_output(S.EVENTS) = $ptascii("B|")', '$np_guard(S)',
    ]


def layout(shadow):
    if shadow:
        return [
            'ppropertydesc_first.VISIBILITY = PROPERTY_PRIVATE /\\ ppropertydesc_second.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_first.NAME = $ptascii("same") /\\ ppropertydesc_second.NAME = $ptascii("same")',
            'ptbytes_first = [0] ++ $ptascii("ShadowBase124R") ++ [0] ++ $ptascii("same")',
            'ptbytes_second = [0] ++ $ptascii("ShadowChild124R") ++ [0] ++ $ptascii("same")',
            'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number) /\\ paggregatecursor.RIGHTITEM = DIRECT (PINT 0)',
            'pnumbercompare.SOURCE.CAST.OBJECTLEFT = true',
            'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_PROPERTY n_right ptbytes_first)',
            '$number_compare_other(S,pnumbercompare) = (PINT 0)',
        ]
    return [
        'ppropertydesc_first.VISIBILITY = PROPERTY_PROTECTED /\\ ppropertydesc_second.VISIBILITY = PROPERTY_PROTECTED',
        'ppropertydesc_first.NAME = $ptascii("front") /\\ ppropertydesc_second.NAME = $ptascii("tail")',
        'ptbytes_first = [0,42,0] ++ $ptascii("front") /\\ ptbytes_second = [0,42,0] ++ $ptascii("tail")',
        'paggregatecursor.LEFTITEM = DIRECT (PINT 2) /\\ paggregatecursor.RIGHTITEM = DIRECT (POBJECT n_number)',
        'pnumbercompare.SOURCE.CAST.OBJECTLEFT = false',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_PROPERTY n_left ptbytes_first)',
        '$number_compare_other(S,pnumbercompare) = (PINT 2)',
    ]


def controls():
    return [
        '~$aggregate_cursor_valid(S,paggregatecursor[.KEY = KSTRING ($ptascii("same"))])',
        '~$aggregate_cursor_valid(S,paggregatecursor[.KIND = AGGREGATE_DECL_HASH [ptbytes_second,ptbytes_first]])',
        '~$aggregate_cursor_valid(S,paggregatecursor[.INDEX = 0])',
        '~$aggregate_cursor_valid(S,paggregatecursor[.WIDTH = 1])',
        'pnumbercompare.SOURCE.CAST.RECEIVER = n_number',
        '~$aggregate_decl_public($property_layout(S,porigin_class,|S.CLASSES|))',
        '$aggregate_decl_cast_order(S,n_left,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERUNSUPPORTED "materialized-property Stringable comparison continuation"',
        '$aggregate_decl_cast_order(S,n_left,ORDERNOTICE pnumbercompare.SOURCE.CAST (PINT 1)) = ORDERNOTICE pnumbercompare.SOURCE.CAST (PINT 1)',
        '$aggregate_decl_cast_order(S,n_left,ORDER $(-1)) = ORDER $(-1)',
        '$aggregate_decl_cast_order(S,n_number,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERSTRING pnumbercompare.SOURCE.CAST',
        '~$number_compare_valid(S,pnumbercompare[.SOURCE.LINE = 999])',
        '~$call_task_valid(S[.ORIGIN = eps],NUMBER_COMPARE_RESULT pnumbercompare)',
        'S_unset = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_right,[ppropertyslot_rightfirst[.STATE = PROP_UNSET],ppropertyslot_rightsecond])]',
        '~$aggregate_decl_image(S_unset,n_right,ptbytes_keys*) /\\ ~$number_compare_valid(S_unset,pnumbercompare)',
        'S_dynamic = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_right,[ppropertyslot_rightfirst[.DECL = eps],ppropertyslot_rightsecond])]',
        '~$aggregate_decl_image(S_dynamic,n_right,ptbytes_keys*)',
        'S_decl = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_right,[ppropertyslot_rightfirst[.DECL = (ppropertydesc_second.ORIGIN)],ppropertyslot_rightsecond])]',
        '~$aggregate_decl_image(S_decl,n_right,ptbytes_keys*)',
        'S_undef = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_right,[ppropertyslot_rightfirst[.STATE = PROP_VALUE UNINITIALIZED],ppropertyslot_rightsecond])]',
        '~$aggregate_decl_image(S_undef,n_right,ptbytes_keys*)',
        '~$aggregate_decl_image(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_right)],n_right,ptbytes_keys*)',
    ]


def resume(shadow):
    pointer_object = 'n_right' if shadow else 'n_left'
    first = '0' if shadow else '1'
    second = '1' if shadow else '7'
    result = 'PINT 1' if shadow else 'PBOOL true'
    expected = 'B|H:1|R:1:1:1:1|A|'
    return [
        *seek('S_return', 'S', 1),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.CURRENT = eps /\\ S_return.FRAMES = eps',
        'S_return.RESULT = KNOWN (PBOOL true)', '$np_guard(S_return)',
        *seek('S_resume', 'S_return', 2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$number_compare_other(S_resume,pnumbercompare) = (PINT ' + first + ')',
        '$aggregate_pointer_value(S_resume,AGGREGATE_PROPERTY ' + pointer_object + ' ptbytes_first) = (PINT ' + first + ')',
        '$aggregate_pointer_value(S_resume,AGGREGATE_PROPERTY n_right ptbytes_second) = (PINT ' + second + ')',
        '$np_output(S_resume.EVENTS) = $ptascii("B|H:1|")', '$np_guard(S_resume)',
        'PhpStep: S_resume ~> S_raw',
        'S_raw.RESULT = KNOWN (' + result + ')',
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN (' + result + ')', '$np_guard(S_after)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text(expected), '$np_guard(S_done)',
    ]


def checks(program, path, name):
    assert name in ('private-shadow-physical-key', 'protected-reversed-live-slots')
    shadow = name == 'private-shadow-physical-key'
    return front(program,path,name) + layout(shadow) + controls() + resume(shadow)
