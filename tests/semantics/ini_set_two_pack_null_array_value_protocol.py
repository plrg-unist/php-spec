#!/usr/bin/env python3
"""Two completed unpack snapshots preserve NULL and the earlier owning array."""
import json
import os
from pathlib import Path

import ini_set_owned_unpack_null_array_value_protocol as shared
import ini_set_unpack_null_array_value_protocol as ownerless
import ini_set_null_array_value_protocol as arrays
import ini_set_two_pack_null_array_value_sources as sources

common, driver, text, b64 = shared.common, shared.driver, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, unchanged = shared.reach, shared.returned, shared.budget, shared.unchanged
PREFIX = shared.PREFIX + r"""
dec $test_ini_two_pack_front(pstate, nat) : bool
def $test_ini_two_pack_front(S, 0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.SENT = eps
def $test_ini_two_pack_front(S, 1) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_outer)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
def $test_ini_two_pack_front(S, 2) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_outer)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1
def $test_ini_two_pack_front(S, n_stage) = false -- otherwise
dec $test_ini_two_pack_seek(pstate, nat, nat) : pstate
def $test_ini_two_pack_seek(S, n_stage, 0) = S
def $test_ini_two_pack_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_two_pack_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_two_pack_seek(S, n_stage, n) = $test_ini_two_pack_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_two_pack_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def partial(state, start, stage):
    return [state + '_found = $test_ini_two_pack_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_two_pack_front(' + state + ',' + str(stage) + ')']


def front(state, start, mode, owned=False, selected=False):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    packs = ['pconfigpack_first_' + state, 'pconfigpack_second_' + state]
    if mode == 'reversed':
        entries = ['ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY ' + array + '))',
            'ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)']
    else:
        first = 'KSTRING ' + text('option') if mode == 'named_then_numeric' else 'KINT i_option_' + state
        second = 'KSTRING ' + text('value') if mode == 'mixed' else 'KINT i_value_' + state
        entries = ['ENTRY (' + first + ') (DIRECT PNULL)', 'ENTRY (' + second + ') (DIRECT (PARRAY ' + array + '))']
    roots = ('HOBJECT n_owner_' + state + ',' if owned else '') + 'HARRAY ' + array
    values = [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.INDEX = 2',
        call + '.PACKS = [' + ','.join(packs) + ']', ('' if mode != 'numeric' else '~') + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
        '$intrinsic_count(' + state + ',' + call + '.SITE) = (2)',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_array(' + state + ',' + array + ')', '(HARRAY ' + array + ') <- ' + state + '.ALLOCATIONS',
        '~$config_ini_quiet_value(' + state + ',PARRAY ' + array + ')',
        '$node_children(' + state + ',HARRAY ' + array + ') = eps',
        '$config_nodes(' + call + ') = [' + roots + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [' + roots + ']',
        state + '.CURRENT = eps', state + '.FRAMES = eps']
    for index, (pack, entry) in enumerate(zip(packs, entries)):
        values += [pack + '.INDEX = ' + str(index), pack + '.ARRAY = n_outer_' + str(index) + '_' + state,
            pack + '.ITEMS = [' + entry + ']',
            '$intrinsic_argument(' + state + ',' + call + '.SITE,' + str(index) + ') = ((expression_pack_' + str(index) + '_' + state + ',true,eps,' + pack + '.SITE,' + pack + '.LINE))',
            '$config_pack_source_valid(' + state + ',' + call + ',' + pack + ')',
            '$config_ini_pack_known(' + state + ',' + pack + '.ITEMS,$compiled_read(' + state + ',' + pack + '.SITE))',
            '~((HARRAY n_outer_' + str(index) + '_' + state + ') <- $config_nodes(' + call + '))']
    if owned:
        values += [call + '.OWNER = (n_owner_' + state + ')', call + '.SELECTION = eps',
            state + '.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '(HOBJECT n_owner_' + state + ') <- ' + state + '.ALLOCATIONS']
    else:
        values += [call + '.OWNER = eps', '~$config_method_receiver(' + state + ',' + call + ')']
        if selected:
            values += [call + '.SELECTION = (n_selection_' + state + ')',
                state + '.SELECTEDCALLS[n_selection_' + state + '].KIND = INTRINSIC_INI_SET',
                state + '.SELECTEDCALLS[n_selection_' + state + '].SITE = ' + call + '.SITE',
                state + '.SELECTEDCALLS[n_selection_' + state + '].LINE = ' + call + '.LINE']
        else:
            values += [call + '.SELECTION = eps']
    return values + common.public(state)


def literal(state, index, key, inner=False):
    pack, known = ('pconfigpack_' + ('first_' if index == 0 else 'second_') + state,
        'n_known_pack_' + str(index) + '_' + state)
    values = ['$compiled_read(' + state + ',' + pack + '.SITE) = (PARRAY ' + known + ')',
        '$($heap_count(HARRAY ' + known + ',$pools_nodes(' + state + '.POOLS)) > 0)',
        '$dynamic_array_same_entries(' + state + ',' + pack + '.ITEMS,' + state + '.ARRAYS[' + known + '].ITEMS)']
    if inner:
        values += ['$entry_lookup(' + state + '.ARRAYS[' + known + '].ITEMS,' + key + ') = (DIRECT (PARRAY n_known_inner_' + state + '))',
            '$dynamic_array_same(' + state + ',PARRAY n_array_' + state + ',PARRAY n_known_inner_' + state + ')',
            '$array_immutable(' + state + ',n_array_' + state + ') = $array_immutable(' + state + ',n_known_inner_' + state + ')']
    return values


def error(state, start, owned=False, explicit=False, strict=False, default=False):
    return (shared.error(state, start, explicit, strict, default) if owned else
        ownerless.error(state, start, strict, default))


def refusals(state, owned=False):
    call, first, second = 'pconfigcall_' + state, 'pconfigpack_first_' + state, 'pconfigpack_second_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 1',
            '.KIND = INTRINSIC_INI_GET', '.SELECTION = (|' + state + '.SELECTEDCALLS|)',
            '.SENT = ' + call + '.SENT[0:1]', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]',
            '.OWNER = (|' + state + '.OBJECTS|)'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    for packs in ('eps', '[' + first + ']', '[' + second + ']', '[' + first + ',' + first + ']', '[' + second + ',' + first + ']'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[.PACKS = ' + packs + '])']
    for index, pack in enumerate((first, second)):
        for field in ('.INDEX = ' + str(1-index), '.SITE = PORIGIN 0 eps', '.LINE = $(' + pack + '.LINE + 1)',
                '.ARRAY = |' + state + '.ARRAYS|', '.ITEMS = eps'):
            packs = [first, second]
            packs[index] = pack + '[' + field + ']'
            values += ['~$config_ini_null_valid(' + state + ',' + call + '[.PACKS = [' + ','.join(packs) + ']])']
    values += ['~$config_ini_null_valid(' + state + '[.CODE = eps],' + call + ')',
        '~$config_ini_null_valid(' + state + '[.ALLOCATIONS = eps],' + call + ')']
    if owned:
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = eps])',
            '~$config_ini_null_valid(' + state + '[.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')']
    return values


def first_group(owned, key):
    roots = '[HOBJECT n_owner_pre]' if owned else 'eps'
    active = '[HOBJECT n_owner_pre,HARRAY n_outer_first]' if owned else '[HARRAY n_outer_first]'
    values = [*partial('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.KIND = INTRINSIC_INI_SET',
        'pconfigcall_pre.INDEX = 0', 'pconfigcall_pre.SENT = eps', 'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED',
        '$config_pending_valid(S_pre,pconfigcall_pre,true)', '$config_nodes(pconfigcall_pre) = ' + roots,
        '$lookup(S_pre.ENV,' + text('optionPack') + ') = (n_option_pack)',
        'S_pre.STORE[n_option_pack] = DEFINED (PARRAY n_outer_first)',
        'S_pre.ARRAYS[n_outer_first].ITEMS = [ENTRY (KINT ' + str(key) + ') (DIRECT PNULL)]',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)', 'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]
    if owned:
        values += ['pconfigcall_pre.OWNER = (n_owner_pre)', 'pconfigcall_pre.SELECTION = eps',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement)',
            'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_live)', 'n_live =/= n_owner_pre',
            'S_pre.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET']
    else:
        values += ['pconfigcall_pre.OWNER = eps', 'pconfigcall_pre.SELECTION = (n_selection)',
            'S_pre.STORE[n_call] = DEFINED pvalue_original_call', 'S_pre.STORE[n_keep] = DEFINED pvalue_original_call',
            '$string_bytes(pvalue_original_call) = (' + text('InI_SeT') + ')']
    values += [*partial('S_capture','S_pre',1),
        'S_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer_first)) 0) :: ptask_pre*',
        'pconfigcall_capture.PACKS = [pconfigpack_option]',
        'pconfigcall_capture = pconfigcall_pre[.PACKS = [pconfigpack_option]]',
        'pconfigpack_option.INDEX = 0', 'pconfigpack_option.ARRAY = n_outer_first',
        'pconfigpack_option.ITEMS = [ENTRY (KINT ' + str(key) + ') (DIRECT PNULL)]',
        '$config_pack_source_valid(S_capture,pconfigcall_capture,pconfigpack_option)',
        '$config_unpack_valid(S_capture,pconfigcall_capture,KNOWN (PARRAY n_outer_first),0)',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer_first)) 0) = ' + active,
        *unchanged('S_capture','S_pre','STORE ENV EVENTS'), *common.public('S_capture'), *common.step('S_first','S_capture'),
        'pconfigcall_first = pconfigcall_capture[.SENT = [NAMED_SENT (KNOWN PNULL)]]',
        'S_first.TODO = (CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer_first)) 1) :: ptask_pre*',
        '$config_unpack_valid(S_first,pconfigcall_first,KNOWN (PARRAY n_outer_first),1)',
        *common.public('S_first'), *common.step('S_between','S_first'),
        'pconfigcall_between = pconfigcall_first[.INDEX = 1]',
        'S_between.TODO = (CONFIG_ARGS pconfigcall_between) :: ptask_pre*',
        '$config_pending_valid(S_between,pconfigcall_between,true)',
        '$task_nodes(CONFIG_ARGS pconfigcall_between) = ' + roots,
        '$test_outputs(S_between.EVENTS) = ' + text('B|'), *common.public('S_between'),
        *partial('S_second_capture','S_between',2),
        'S_second_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_outer_second)) 0) :: ptask_pre*',
        'pconfigcall_second.PACKS = [pconfigpack_option,pconfigpack_value]',
        'pconfigcall_second = pconfigcall_between[.PACKS = [pconfigpack_option,pconfigpack_value]]',
        'pconfigpack_value.INDEX = 1', 'pconfigpack_value.ARRAY = n_outer_second',
        'pconfigpack_value.ITEMS = [ENTRY (KINT ' + ('9' if owned else '7') + ') (DIRECT (PARRAY n_captured))]',
        'S_second_capture.ARRAYS[n_outer_second].ITEMS = pconfigpack_value.ITEMS',
        '$config_unpack_valid(S_second_capture,pconfigcall_second,KNOWN (PARRAY n_outer_second),0)',
        '$node_children(S_second_capture,HARRAY n_outer_second) = [HARRAY n_captured]',
        '~((HARRAY n_outer_first) <- S_second_capture.ALLOCATIONS)',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_outer_second)) 0) = ' +
            ('[HOBJECT n_owner_pre,HARRAY n_outer_second]' if owned else '[HARRAY n_outer_second]'),
        'S_second_capture.STORE[n_effects] = DEFINED (PINT 1)', 'S_second_capture.STORE[n_value] = DEFINED (PINT 0)',
        'S_second_capture.STORE[n_result] = DEFINED (PINT 99)', 'S_second_capture.STORE[n_warnings] = DEFINED (PINT 0)',
        '$test_outputs(S_second_capture.EVENTS) = ' + text('B|P|'), *common.public('S_second_capture'),
        *common.step('S_second_sent','S_second_capture'),
        'pconfigcall_second_sent = pconfigcall_second[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
        'S_second_sent.TODO = (CONFIG_UNPACK_NEXT pconfigcall_second_sent (KNOWN (PARRAY n_outer_second)) 1) :: ptask_pre*',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_second_sent (KNOWN (PARRAY n_outer_second)) 1) = ' +
            ('[HOBJECT n_owner_pre,HARRAY n_captured,HARRAY n_outer_second]' if owned else '[HARRAY n_captured,HARRAY n_outer_second]'),
        *common.public('S_second_sent'), *common.step('S_done','S_second_sent'),
        'pconfigcall_done = pconfigcall_second_sent[.INDEX = 2]', 'S_done.TODO = (CONFIG_ARGS pconfigcall_done) :: ptask_pre*',
        '$config_nodes(pconfigcall_done) = ' + ('[HOBJECT n_owner_pre,HARRAY n_captured]' if owned else '[HARRAY n_captured]'),
        *common.public('S_done')]
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'two-pack-null-array-default-and-explicit-reversed-returned-trace':
        values += [*front('S_default','S_initial','numeric'), 'i_option_S_default = 3', 'i_value_S_default = 7',
            'S_default.ARRAYS[n_array_S_default].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3433))]',
            *literal('S_default',0,'KINT 3'), *literal('S_default',1,'KINT 7',inner=True),
            '~$config_strict(S_default,pconfigcall_S_default)', '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', *error('S_default','S_default',default=True),
            *front('S_true','S_default_error','reversed',owned=True),
            'S_true.ARRAYS[n_array_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3449))]',
            *literal('S_true',0,'KSTRING ' + text('value'),inner=True), *literal('S_true',1,'KSTRING ' + text('option')),
            '$config_method_receiver(S_true,pconfigcall_S_true)', '~$config_strict(S_true,pconfigcall_S_true)',
            *returned('S_true',1,'14','true'), *error('S_true','S_true_resume',owned=True,explicit=True),
            'S_forged = $allocate_array(S_true,$array_insert($array_empty(),KINT 0,DIRECT (PINT 3450)))',
            'S_forged.RESULT = KNOWN (PARRAY n_forged)',
            'pconfigpack_forged = pconfigpack_first_S_true[.ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_forged))]]',
            'pconfigcall_forged = pconfigcall_S_true[.PACKS = [pconfigpack_forged,pconfigpack_second_S_true]][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_forged))]]',
            '$config_invoke_valid(S_forged,pconfigcall_forged)', '$config_ini_rejected_array(S_forged,n_forged)',
            '~$config_ini_pack_known(S_forged,pconfigpack_forged.ITEMS,$compiled_read(S_forged,pconfigpack_forged.SITE))',
            '$config_ini_pack_known(S_forged,pconfigpack_second_S_true.ITEMS,$compiled_read(S_forged,pconfigpack_second_S_true.SITE))',
            '~$config_ini_null_valid(S_forged,pconfigcall_forged)',
            '~$config_ini_pack_known(S_true,[ENTRY (KSTRING ' + text('option') + ') (DIRECT (PBOOL false))],$compiled_read(S_true,pconfigpack_second_S_true.SITE))',
            *refusals('S_true',owned=True), *partial('S_cross_capture','S_true_error',2),
            'S_cross_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_cross_capture (KNOWN (PARRAY n_cross_outer)) 0) :: ptask_S_cross*',
            'pconfigcall_cross_capture.NAMED', 'pconfigcall_cross_capture.SENT = [NAMED_SENT (KNOWN PNULL)]',
            'pconfigcall_cross_capture.PACKS = [pconfigpack_cross_option,pconfigpack_cross_value]',
            'pconfigpack_cross_option.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]',
            'pconfigpack_cross_value.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_cross_array))]',
            '$config_unpack_valid(S_cross_capture,pconfigcall_cross_capture,KNOWN (PARRAY n_cross_outer),0)',
            *common.step('S_cross_sent','S_cross_capture'),
            'pconfigcall_cross_sent = pconfigcall_cross_capture[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_cross_array))]]',
            'S_cross_sent.TODO = (CONFIG_UNPACK_NEXT pconfigcall_cross_sent (KNOWN (PARRAY n_cross_outer)) 1) :: ptask_S_cross*',
            'S_cross_sent.EVENTS = S_cross_capture.EVENTS', *common.public('S_cross_sent'),
            *front('S_cross','S_cross_sent','named_then_numeric'), 'i_value_S_cross = 0', 'n_array_S_cross = n_cross_array',
            'pconfigcall_S_cross = pconfigcall_cross_sent[.INDEX = 2]',
            'S_cross.ARRAYS[n_array_S_cross].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0))]',
            *literal('S_cross',0,'KSTRING ' + text('option')), *literal('S_cross',1,'KINT 0',inner=True),
            *returned('S_cross',2,'14','true'), *error('S_cross','S_cross_resume'),
            *budget('S_default'), *budget('S_true_resume'), *budget('S_cross_capture'),
            *shared.recovery('S_cross_error','n_owner_S_true','14'),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|3449|3449|99|1|O|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|2|Z|R|14|11')]
    else:
        strict = name == 'strict-two-pack-option-priority-before-same-owner-explicit-mixed-reception'
        assert strict or name == 'two-pack-null-and-array-captures-survive-later-group-effects'
        values += [*first_group(strict,5 if strict else 3),
            *front('S','S_done','numeric',owned=strict,selected=not strict),
            'i_option_S = ' + ('5' if strict else '3'), 'i_value_S = ' + ('9' if strict else '7'),
            'pconfigcall_S = pconfigcall_done', 'n_array_S = n_captured',
            'pconfigpack_first_S = pconfigpack_option', 'pconfigpack_second_S = pconfigpack_value',
            '~((HARRAY n_outer_first) <- S.ALLOCATIONS)', '~((HARRAY n_outer_second) <- S.ALLOCATIONS)',
            '$compiled_read(S,pconfigpack_option.SITE) = eps', '$compiled_read(S,pconfigpack_value.SITE) = eps',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S.TODO)) = 1',
            'S.PRECISIONINI = ' + text('14'), '$test_outputs(S.EVENTS) = ' + text('B|P|'),
            'S.STORE[n_option_pack] = DEFINED (PARRAY n_live_pack)', 'n_live_pack =/= n_outer_first',
            'S.ARRAYS[n_live_pack].ITEMS = [ENTRY (KINT ' + ('5' if strict else '3') + ') (DIRECT pvalue_live_option)]',
            '$string_bytes(pvalue_live_option) = (' + text('precision') + ')',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_array_keep] = DEFINED (PARRAY n_mutated)', 'n_mutated =/= n_captured']
        if strict:
            values += ['n_owner_S = n_owner_pre', 'S.STORE[n_call] = DEFINED (POBJECT n_live)',
                'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
                'S_pre.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3461))]',
                'S.ARRAYS[n_captured].ITEMS = S_pre.ARRAYS[n_captured].ITEMS',
                'S.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0))]',
                '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)',
                '~$config_method_receiver(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                *error('S','S',owned=True,strict=True),
                *front('S_wrapper','S_error','mixed',owned=True), 'i_option_S_wrapper = 3',
                'n_owner_S_wrapper = n_owner_pre', 'S_wrapper.ARRAYS[n_array_S_wrapper].ITEMS = eps',
                *literal('S_wrapper',0,'KINT 3'), *literal('S_wrapper',1,'KSTRING ' + text('value'),inner=True),
                '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)', '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)',
                '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
                *returned('S_wrapper',1,'8','true'), *error('S_wrapper','S_wrapper_resume',owned=True,explicit=True),
                *refusals('S_wrapper',owned=True), *budget('S_between'), *budget('S_second_capture'), *budget('S_wrapper_resume'),
                *shared.recovery('S_wrapper_error','n_owner_pre','8'),
                'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|P|' + OPTION_ERROR + '|99|1|0|precision|0|0|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|Z|R|8|11')]
        else:
            values += ['S_pre.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured)]',
                'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-two-pack-array86'),
                'S.ARRAYS[n_captured].ITEMS = S_pre.ARRAYS[n_captured].ITEMS', '$string_carrier_valid(S,pvalue_captured)',
                'n_selection_S = n_selection', 'S.SELECTEDCALLS[n_selection] = S_pre.SELECTEDCALLS[n_selection]',
                'S.STORE[n_call] = DEFINED pvalue_live_call', '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
                'S.STORE[n_keep] = DEFINED pvalue_original_call',
                'S.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_mutated)]',
                '$string_bytes(pvalue_mutated) = (' + text('pack-array86') + ')',
                '~$config_strict(S,pconfigcall_S)',
                *returned('S',1,'8','false'),
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                'S_return.STORE[n_keep] = DEFINED pvalue_original_call',
                'S_return.STORE[n_array_keep] = DEFINED (PARRAY n_handler_array)', 'n_handler_array =/= n_captured',
                'S_return.ARRAYS[n_handler_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_handler)]',
                '$string_bytes(pvalue_handler) = (' + text('handler-array86') + ')',
                'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
                'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value86') + ')',
                *error('S','S_resume'), *refusals('S'),
                *[v for v in arrays.refusals('S') if v not in refusals('S')], *budget('S_pre'), *budget('S_between'), *budget('S_second_capture'), *budget('S_resume'),
                *ownerless.recovery('S_error','8'),
                'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|P|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|precision|handler-array86|constant|handler-value86|8|Z|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(ownerless.__file__), Path(shared.shared.__file__),
            Path(shared.shared.shared.__file__), Path(arrays.__file__), Path(shared.base.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
