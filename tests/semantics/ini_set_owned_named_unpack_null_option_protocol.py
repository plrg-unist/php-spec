#!/usr/bin/env python3
"""Named unpack normalizes early array entries while retaining its intrinsic owner."""
import json
import os
from pathlib import Path

import ini_set_owned_unpack_null_option_protocol as numeric
import ini_set_owned_named_unpack_null_option_sources as sources

driver, common, text, b64 = numeric.driver, numeric.common, numeric.text, numeric.b64
MESSAGE = numeric.MESSAGE
reach, budget, unchanged, handled = numeric.reach, numeric.budget, numeric.unchanged, numeric.handled
PREFIX = numeric.PREFIX + r"""
dec $test_ini_named_array_partial(pstate) : bool
def $test_ini_named_array_partial(S) = true
  -- if S.TODO = (ARRAY_NEXT n_array phpType13*) :: ptask_tail*
  -- if |phpType13*| = 1
  -- if S.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT pvalue)]
def $test_ini_named_array_partial(S) = false -- otherwise
dec $test_ini_named_array_seek(pstate, nat) : pstate
def $test_ini_named_array_seek(S, 0) = S
def $test_ini_named_array_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_named_array_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_named_array_seek(S, n) = $test_ini_named_array_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_named_array_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def entries(candidate, order):
    option = 'ENTRY (KSTRING (' + text('option') + ')) (DIRECT PNULL)'
    value = 'ENTRY (KSTRING (' + text('value') + ')) (DIRECT (' + candidate + '))'
    if order == 'reversed':
        return '[' + value + ',' + option + ']'
    if order == 'forward':
        return '[' + option + ',' + value + ']'
    assert order == 'mixed'
    return '[ENTRY (KINT 0) (DIRECT PNULL),' + value + ']'


def front(state, start, candidate, order):
    call, owner, pack = 'pconfigcall_' + state, 'n_owner_' + state, 'pconfigpack_' + state
    return [*reach(state, start, 0),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')',
        call + '.INDEX = 1', call + '.SELECTION = eps', call + '.NAMED',
        call + '.PACKS = [' + pack + ']', pack + '.INDEX = 0',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        pack + '.ITEMS = ' + entries(candidate, order),
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
    values = numeric.refusals(state)
    old = '~$config_ini_null_valid(' + state + ',pconfigcall_' + state + '[.NAMED = true])'
    values[values.index(old)] = old.replace('.NAMED = true', '.NAMED = false')
    return values


def literal(state):
    pack = 'pconfigpack_' + state
    return ['$compiled_read(' + state + ',' + pack + '.SITE) = (PARRAY n_known_' + state + ')',
        '$($heap_count(HARRAY n_known_' + state + ',$pools_nodes(' + state + '.POOLS)) > 0)',
        '$dynamic_array_same_entries(' + state + ',' + pack + '.ITEMS,' + state + '.ARRAYS[n_known_' + state + '].ITEMS)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'owned-named-unpack-null-true-handlers-and-mixed-pack':
        values += [*front('S', 'S_initial', 'PINT 2237', 'reversed'), *literal('S'),
            '~$config_strict(S,pconfigcall_S)', '~$config_method_receiver(S,pconfigcall_S)',
            *handled('S', 'PINT 2237', 1, '14', 'true'),
            *front('S_mixed', 'S_after', 'PINT 2243', 'mixed'), *literal('S_mixed'),
            'n_owner_S_mixed = n_owner_S', '$config_method_receiver(S_mixed,pconfigcall_S_mixed)',
            '~$config_strict(S_mixed,pconfigcall_S_mixed)',
            *handled('S_mixed', 'PINT 2243', 2, '14', 'true'),
            'pconfigpack_forged = pconfigpack_S[.ITEMS = ' + entries('PINT 2238', 'reversed') + ']',
            'pconfigcall_forged = pconfigcall_S[.PACKS = [pconfigpack_forged]][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 2238))]]',
            '$config_invoke_valid(S,pconfigcall_forged)',
            '~$config_ini_pack_known(S,pconfigpack_forged.ITEMS,$compiled_read(S,pconfigpack_S.SITE))',
            '~$config_ini_null_valid(S,pconfigcall_forged)',
            *refusals('S'), *refusals('S_mixed'), *budget('S'), *budget('S_mixed_resume'),
            'S_final = $drive_steps(S_mixed_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|F|H|8192|' + MESSAGE + '|F|2|14')]
    elif name == 'captured-owned-named-unpack-before-later-array-option-effects':
        values += ['S_pre_found = $test_ini_named_array_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_named_array_partial(S_pre)',
            'S_pre.TODO = (ARRAY_NEXT n_builder phpType13_remaining*) :: ptask_pre*',
            'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING (' + text('value') + ')) (DIRECT pvalue_captured)]',
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-named-pack67'),
            '$string_carrier_valid(S_pre,pvalue_captured)', '(HARRAY n_builder) <- S_pre.ALLOCATIONS',
            '(HARRAY n_builder) <- $tasks_nodes(S_pre.TODO)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)',
            'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '(HOBJECT n_owner_pre) <- $tasks_nodes(S_pre.TODO)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)',
            'S_pre.STORE[n_call] = DEFINED (POBJECT n_replacement)', 'n_replacement =/= n_owner_pre',
            'S_pre.OBJECTS[n_replacement] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED pvalue_pre',
            '$string_bytes(pvalue_pre) = (' + text('after-value67') + ')',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 1)',
            'S_pre.PRECISIONINI = ' + text('6'), '$test_outputs(S_pre.EVENTS) = ' + text('B|V|'),
            *common.public('S_pre'), *front('S', 'S_pre', 'pvalue_captured', 'reversed'),
            'n_owner_S = n_owner_pre', 'pconfigpack_S.ARRAY = n_builder',
            '~((HARRAY n_builder) <- S.ALLOCATIONS)', '$compiled_read(S,pconfigpack_S.SITE) = eps',
            'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)', 'S.STORE[n_call] = DEFINED pvalue_call',
            '$string_bytes(pvalue_call) = (' + text('constant') + ')',
            'S.STORE[n_value] = DEFINED pvalue_live', '$string_bytes(pvalue_live) = (' + text('after-option67') + ')',
            'S.STORE[n_effects] = DEFINED (PINT 2)', 'S.PRECISIONINI = ' + text('7'),
            '$test_outputs(S.EVENTS) = ' + text('B|V|O|'),
            '~$config_strict(S,pconfigcall_S)', '~$config_method_receiver(S,pconfigcall_S)',
            *handled('S', 'pvalue_captured', 1, '8', 'false'),
            'S_after.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            *refusals('S'), *budget('S_pre'), *budget('S_resume'),
            'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
            'S_final.PRECISIONINI = ' + text('11'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|W|8192|' + MESSAGE + '|F|8|2|1|ini_get|precision|handler-named-pack67|D|Z|R|8|11')]
    else:
        assert name == 'strict-owned-named-unpack-before-weak-explicit-forward-pack'
        values += [*front('S', 'S_initial', 'PINT 2273', 'reversed'), '$config_strict(S,pconfigcall_S)',
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|O|'), 'S.PRECISIONINI = ' + text('9'),
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
            '$throwable_field(S_error,n_error,"previous") = PNULL',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2273))]',
            '$node_children(S_error,HARRAY n_args) = eps',
            '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictOwnedNamedUnpackCaller67'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *unchanged('S_error', 'S', 'STORE ENV EVENTS PRECISIONINI ERRORHANDLER'),
            *common.public('S_error'), *front('S_wrapper', 'S_error', 'PINT 2281', 'forward'),
            *literal('S_wrapper'), 'n_owner_S_wrapper = n_owner_S',
            '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)',
            '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)', '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
            *handled('S_wrapper', 'PINT 2281', 1, '8', 'true'),
            *refusals('S_wrapper'), *budget('S'), *budget('S_wrapper_resume'),
            'S_final = $drive_steps(S_wrapper_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|ini_set(): Argument #1 ($option) must be of type string, null given|99|2|0|9|E|H|8192|' + MESSAGE + '|F|8|1|2|1|Z')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(numeric.__file__), Path(numeric.retained.__file__),
                     Path(numeric.shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
