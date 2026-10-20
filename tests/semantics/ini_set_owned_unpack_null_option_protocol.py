#!/usr/bin/env python3
"""Captured numeric unpack snapshots resume NULL INI options without rereading arrays."""
import json
import os
from pathlib import Path

import ini_set_owned_named_null_option_protocol as retained
import ini_set_owned_unpack_null_option_sources as sources

shared = retained.shared
driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE = shared.MESSAGE
PREFIX = shared.PREFIX
reach, budget, unchanged, handled = shared.reach, shared.budget, shared.unchanged, retained.handled


def front(state, start, candidate):
    call, owner, pack = 'pconfigcall_' + state, 'n_owner_' + state, 'pconfigpack_' + state
    return [*reach(state, start, 0),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')',
        call + '.INDEX = 1', call + '.SELECTION = eps', '~' + call + '.NAMED',
        call + '.PACKS = [' + pack + ']', pack + '.INDEX = 0',
        pack + '.ITEMS = [ENTRY (KINT i_option_' + state + ') (DIRECT PNULL),ENTRY (KINT i_value_' + state + ') (DIRECT (' + candidate + '))]',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS',
        '$getclass_live_object(' + state + ',' + owner + ')',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$config_pack_source_valid(' + state + ',' + call + ',' + pack + ')',
        '$config_ini_quiet_value(' + state + ',' + candidate + ')',
        '$config_ini_pack_known(' + state + ',' + pack + '.ITEMS,$compiled_read(' + state + ',' + pack + '.SITE))',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_pack_' + state + ',true,eps,' + pack + '.SITE,' + pack + '.LINE))',
        '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
        '$config_nodes(' + call + ') = [HOBJECT ' + owner + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ']',
        *common.public(state)]


def refusals(state):
    call, owner, pack = 'pconfigcall_' + state, 'n_owner_' + state, 'pconfigpack_' + state
    values = []
    for field in ('.OWNER = eps', '.OWNER = (|' + state + '.OBJECTS|)', '.NAMED = true',
            '.LINE = $(' + call + '.LINE + 1)', '.SITE = PORIGIN 0 eps', '.INDEX = 2',
            '.SELECTION = (0)', '.PACKS = eps', '.PACKS = [' + pack + ',' + pack + ']',
            '.PACKS = [' + pack + '[.INDEX = 1]]',
            '.PACKS = [' + pack + '[.LINE = $(' + pack + '.LINE + 1)]]',
            '.SENT = ' + call + '.SENT[0:1]',
            '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        '~$config_ini_null_valid(' + state + '[.ALLOCATIONS = eps],' + call + ')']
    return values


def literal(state, candidate):
    pack = 'pconfigpack_' + state
    return ['i_option_' + state + ' = 0', 'i_value_' + state + ' = 1',
        '$compiled_read(' + state + ',' + pack + '.SITE) = (PARRAY n_known_' + state + ')',
        '$($heap_count(HARRAY n_known_' + state + ',$pools_nodes(' + state + '.POOLS)) > 0)',
        '$dynamic_array_same_entries(' + state + ',' + pack + '.ITEMS,' + state + '.ARRAYS[n_known_' + state + '].ITEMS)',
        '$entry_lookup(' + pack + '.ITEMS,KINT 1) = (DIRECT (' + candidate + '))']


def literal_forgery(state):
    call, pack = 'pconfigcall_' + state, 'pconfigpack_' + state
    return ['pconfigpack_forged_' + state + ' = ' + pack + '[.ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2172))]]',
        'pconfigcall_forged_' + state + ' = ' + call + '[.PACKS = [pconfigpack_forged_' + state + ']][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 2172))]]',
        '$config_invoke_valid(' + state + ',pconfigcall_forged_' + state + ')',
        '~$config_ini_pack_known(' + state + ',pconfigpack_forged_' + state + '.ITEMS,$compiled_read(' + state + ',' + pack + '.SITE))',
        '~$config_ini_null_valid(' + state + ',pconfigcall_forged_' + state + ')']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'owned-numeric-unpack-null-default-and-true-handler':
        values += [*front('S', 'S_initial', 'PINT 2171'), *literal('S', 'PINT 2171'),
            '~$config_strict(S,pconfigcall_S)', '~$config_method_receiver(S,pconfigcall_S)',
            '$config_ini_null_valid(S,pconfigcall_S)', '~$error_handler_eligible(S,8192)',
            *common.step('S_after', 'S'), 'S_after.TODO = ptask_S*',
            'S_after.RESULT = KNOWN (PBOOL false)', 'S_after.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_after.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(pconfigcall_S) pconfigcall_S.LINE]',
            *unchanged('S_after', 'S', 'STORE ENV OBJECTS STRINGDATA USERCONSTANTS PRECISIONINI PRECISIONMODIFIED'),
            *common.public('S_after'), *front('S_handled', 'S_after', 'PINT 2183'),
            *literal('S_handled', 'PINT 2183'), 'n_owner_S_handled = n_owner_S',
            '$config_method_receiver(S_handled,pconfigcall_S_handled)',
            '~$config_strict(S_handled,pconfigcall_S_handled)',
            *handled('S_handled', 'PINT 2183', 1, '14', 'true'),
            *literal_forgery('S'), *refusals('S_handled'),
            *budget('S'), *budget('S_handled_resume'),
            'S_final = $drive_steps(S_handled_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|F|H|8192|' + MESSAGE + '|F|1|14')]
    elif name == 'captured-owned-unpack-null-before-live-pack-mutation':
        values += [*front('S', 'S_initial', 'pvalue_captured'),
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('packed-value66'),
            '$string_carrier_valid(S,pvalue_captured)', 'i_option_S = 0', 'i_value_S = 1',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            '~$config_strict(S,pconfigcall_S)', '~$config_method_receiver(S,pconfigcall_S)',
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED (POBJECT n_replacement)',
            'n_replacement =/= n_owner_S', 'S.OBJECTS[n_replacement] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$lookup(S.ENV,' + text('packKeep') + ') = (n_pack_keep)',
            'S.STORE[n_pack_keep] = DEFINED (PARRAY n_captured_array)', 'pconfigpack_S.ARRAY = n_captured_array',
            'S.ARRAYS[n_captured_array].ITEMS = pconfigpack_S.ITEMS',
            '$lookup(S.ENV,' + text('pack') + ') = (n_pack)', 'S.STORE[n_pack] = DEFINED (PARRAY n_live_array)',
            'n_live_array =/= n_captured_array',
            'S.ARRAYS[n_live_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31)),ENTRY (KINT 1) (DIRECT (PINT 37))]',
            '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED pvalue_live',
            '$string_bytes(pvalue_live) = (' + text('after-pack66') + ')',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.PRECISIONINI = ' + text('7'), '$test_outputs(S.EVENTS) = ' + text('B|P|'),
            *handled('S', 'pvalue_captured', 1, '8', 'false'),
            'S_return.STORE[n_pack_keep] = DEFINED (PARRAY n_mutated_array)',
            '$entry_lookup(S_return.ARRAYS[n_mutated_array].ITEMS,KINT 0) = (DIRECT pvalue_mutated_option)',
            '$string_bytes(pvalue_mutated_option) = (' + text('precision') + ')',
            '$entry_lookup(S_return.ARRAYS[n_mutated_array].ITEMS,KINT 1) = (DIRECT pvalue_mutated_value)',
            '$string_bytes(pvalue_mutated_value) = (' + text('handler-pack66') + ')',
            'S_return.ARRAYS[n_mutated_array].ITEMS =/= pconfigpack_S.ITEMS',
            '$config_ini_null_valid(S_return,pconfigcall_S)',
            '$config_ini_null_valid(S_return[.ARRAYS[pconfigpack_S.ARRAY].ITEMS = eps],pconfigcall_S)',
            'S_after.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            *refusals('S'), *budget('S'), *budget('S_resume'),
            'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
            'S_final.PRECISIONINI = ' + text('11'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|W|8192|' + MESSAGE + '|F|8|1|1|ini_get|handler-value66|31|37|precision|handler-pack66|D|Z|R|8|11')]
    else:
        assert name == 'strict-owned-unpack-null-before-weak-explicit-pack'
        values += [*front('S', 'S_initial', 'PINT 2213'), '$config_strict(S,pconfigcall_S)',
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$test_outputs(S.EVENTS) = ' + text('B|P|'), 'S.PRECISIONINI = ' + text('9'),
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
            '$throwable_field(S_error,n_error,"previous") = PNULL',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2213))]',
            '$node_children(S_error,HARRAY n_args) = eps',
            '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictOwnedUnpackCaller66'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *unchanged('S_error', 'S', 'STORE ENV EVENTS PRECISIONINI ERRORHANDLER'),
            *common.public('S_error'), *front('S_wrapper', 'S_error', 'PINT 2221'),
            *literal('S_wrapper', 'PINT 2221'), 'n_owner_S_wrapper = n_owner_S',
            '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)',
            '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)', '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
            *handled('S_wrapper', 'PINT 2221', 1, '8', 'true'),
            *refusals('S_wrapper'), *budget('S'), *budget('S_wrapper_resume'),
            'S_final = $drive_steps(S_wrapper_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|ini_set(): Argument #1 ($option) must be of type string, null given|99|1|0|9|E|H|8192|' + MESSAGE + '|F|8|1|1|41|43|Z')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(retained.__file__), Path(shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
