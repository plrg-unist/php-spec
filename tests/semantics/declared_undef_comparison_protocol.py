"""Source-reached declared UNDEF ordering and physical reference ownership."""
import base64
import json

from nonpublic_numeric_comparison_review_protocol import PREFIX as COMMON, seek, text

PREFIX = COMMON + r'''
def $np_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $class_instanceof(S, POBJECT n, $ptascii("UnsetVictim125"))
  -- if $np_output(S.EVENTS) = $ptascii("B|H:1|")
def $np_stage(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.RESULT = KNOWN (PINT 1)
def $np_stage(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.RESULT = KNOWN (PINT $(-1))

def $np_stage(S, 4) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if $np_output(S.EVENTS) = $ptascii("B|H:1|K|R:1:1:1:1|U|")
  -- if $lookup(S.ENV, $ptascii("held")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if $class_instanceof(S, POBJECT n, $ptascii("SharedUnsetVictim125"))
'''


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def checks(program, path, name):
    assert name in ('future-unset-inline-last-owner','both-unset-retained-reference-tail')
    shared = name == 'both-unset-retained-reference-tail'
    box = 'SharedUnsetBox125' if shared else 'FutureUnsetBox125'
    width = 3 if shared else 2
    line = 31 if shared else 28
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 0),
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(line),
        '$number_compare_valid(S,pnumbercompare)', '$np_guard(S)',
        'pnumbercompare.TARGET = PINT 1 /\\ pnumbercompare.PHASE = NUMBER_PRIMARY',
        'pnumbercompare.SOURCE.OP = SPACESHIP',
        'pnumbercompare.SOURCE.CAST.STACK = [paggregatecursor]',
        'paggregatecursor.KIND = AGGREGATE_DECL_HASH ptbytes_keys*',
        'paggregatecursor.LEFT = HOBJECT n_left',
        'paggregatecursor.RIGHT = HOBJECT n_right',
        'paggregatecursor.KEY = KSTRING ptbytes_front',
        'paggregatecursor.WIDTH = ' + str(width) + ' /\\ paggregatecursor.INDEX = 1',
        'ptbytes_keys* = [ptbytes_front,ptbytes_tail' + (',ptbytes_later' if shared else '') + ']',
        'ptbytes_front = [0] ++ ' + text(box) + ' ++ [0] ++ $ptascii("front")',
        'ptbytes_tail = [0] ++ ' + text(box) + ' ++ [0] ++ $ptascii("tail")',
        'paggregatecursor.LEFTITEM = DIRECT (POBJECT n_number)',
        'paggregatecursor.RIGHTITEM = DIRECT (PINT 1)',
        'pnumbercompare.SOURCE.CAST.POINTER = (AGGREGATE_PROPERTY n_right ptbytes_front)',
        '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_lfront,ppropertyslot_ltail' + (',ppropertyslot_llater' if shared else '') + '])',
        '$objectprops_at(S.OBJECTPROPS,n_right) = ([ppropertyslot_rfront,ppropertyslot_rtail' + (',ppropertyslot_rlater' if shared else '') + '])',
        'ppropertyslot_ltail.NAME = ptbytes_tail /\\ ppropertyslot_rtail.NAME = ptbytes_tail',
        '$aggregate_decl_image(S,n_left,ptbytes_keys*) /\\ $aggregate_decl_image(S,n_right,ptbytes_keys*)',
        '$number_compare_decl_unset_allowed(S,n_right,ptbytes_tail)',
        '~$number_compare_decl_unset_allowed(S,n_right,$ptascii("absent"))',
        '~$number_compare_decl_unset_allowed(S,n_right,$ptascii("tail"))',
        '$aggregate_decl_item(PROP_INITIAL) = (UNINITIALIZED)',
        '$aggregate_decl_item(PROP_UNSET) = (UNINITIALIZED)',
        '$aggregate_decl_item(PROP_VALUE UNINITIALIZED) = eps',
        '$np_output(S.EVENTS) = $ptascii("B|")',
    ]
    if shared:
        values += [
            'ptbytes_later = [0] ++ ' + text(box) + ' ++ [0] ++ $ptascii("later")',
            'ppropertyslot_ltail.STATE = PROP_VALUE (ALIAS n_cell)',
            'ppropertyslot_rtail.STATE = PROP_VALUE (ALIAS n_cell)',
            '$lookup(S.ENV,$ptascii("held")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_victim)',
            owners('S','HCELL n_cell',3), owners('S','HOBJECT n_victim',1),
            'ppropertyslot_llater.STATE = PROP_VALUE (DIRECT (PINT 3))',
            'ppropertyslot_rlater.STATE = PROP_VALUE (DIRECT (PINT 4))',
        ]
    else:
        values += [
            'ppropertyslot_ltail.STATE = PROP_VALUE (DIRECT (PINT 7))',
            'ppropertyslot_rtail.STATE = PROP_VALUE (DIRECT (POBJECT n_victim))',
            owners('S','HOBJECT n_victim',1),
            *seek('S_destructor','S',3),
            'S_destructor.CURRENT = (pcallcontext_destructor)',
            'pcallcontext_destructor.TARGET = METHOD_TARGET n_victim porigin_destructor',
            '$objectprops_at(S_destructor.OBJECTPROPS,n_right) = ([ppropertyslot_rfront,ppropertyslot_rtail[.STATE = PROP_UNSET]])',
            '$aggregate_decl_image(S_destructor,n_right,ptbytes_keys*)',
            '$np_output(S_destructor.EVENTS) = $ptascii("B|H:1|")',
            '$np_guard(S_destructor)',
        ]
    values += [
        *seek('S_return','S' if shared else 'S_destructor',1),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = NUMBER_COMPARE_RESULT pnumbercompare',
        'S_return.RESULT = KNOWN (PBOOL true)',
        *seek('S_resume','S_return',2),
        'S_resume.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: ptask_tail*',
        '$call_task_valid(S_resume,NUMBER_COMPARE_RESULT pnumbercompare)',
        '$objectprops_at(S_resume.OBJECTPROPS,n_right) = ([ppropertyslot_rfront,ppropertyslot_rtail[.STATE = PROP_UNSET]' + (',ppropertyslot_rlater' if shared else '') + '])',
        '$aggregate_decl_image(S_resume,n_right,ptbytes_keys*)',
        '~$aggregate_decl_initialized($object_table_slots_at(S_resume,n_right))',
        '$aggregate_decl_cast_order(S_resume,n_right,ORDERSTRING pnumbercompare.SOURCE.CAST) = ORDERUNSUPPORTED "materialized-property Stringable comparison continuation"',
        '$number_compare_other(S_resume,pnumbercompare) = (PINT 1)',
        '$np_output(S_resume.EVENTS) = ' + text('B|H:1|K|' if shared else 'B|H:1|D|K|'),
        '$np_guard(S_resume)',
    ]
    if shared:
        values += [
            '$objectprops_at(S_resume.OBJECTPROPS,n_left) = ([ppropertyslot_lfront,ppropertyslot_ltail[.STATE = PROP_UNSET],ppropertyslot_llater])',
            owners('S_resume','HCELL n_cell',1), owners('S_resume','HOBJECT n_victim',1),
        ]
    else:
        values += ['~$heap_member(HOBJECT n_victim,S_resume.ALLOCATIONS)']
    result = 'PINT $(-1)' if shared else 'PINT 1'
    values += [
        'PhpStep: S_resume ~> S_raw', 'S_raw.RESULT = KNOWN (' + result + ')',
        'S_raw.TODO = pnumbercompare.SOURCE.TAIL',
        'S_after = $drive_steps(S_resume,1)', 'S_after.COMPLETION = BUDGET',
        'S_after.RESULT = KNOWN PNULL',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.VALUE = KNOWN (' + result + ')',
        'pdestructionoperation.SOURCE = NUMBER_COMPARE_RESULT pnumbercompare',
        'pdestructionoperation.PENDING = eps',
        'S_after.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_retirement_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_left),DESTRUCTION_VALUE (HOBJECT n_right)]',
        '$np_guard(S_after)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],1) = S_after',
    ]
    values += [*seek('S_retired','S_after',6 if shared else 5),
        'S_retired.RESULT = KNOWN (' + result + ')',
        'S_retired.TODO = pnumbercompare.SOURCE.TAIL', '$np_guard(S_retired)']
    if shared:
        values += [*seek('S_outside','S_retired',4),
            owners('S_outside','HCELL n_cell',1), owners('S_outside','HOBJECT n_victim',1),
            '$np_guard(S_outside)',
            'S_done = $drive_steps(S_outside,4000)',
        ]
    else:
        values += ['S_done = $drive_steps(S_retired,4000)']
    values += [
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$np_output(S_done.EVENTS) = ' + text('B|H:1|K|R:1:1:1:1|U|D|A|' if shared else 'B|H:1|D|K|R:1:1:1|A|'),
        '~$heap_member(HOBJECT n_victim,S_done.ALLOCATIONS)', '$np_guard(S_done)',
    ]
    return values
