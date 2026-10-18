#!/usr/bin/env python3
"""Named intrinsic owners retain written captures and normalized NULL arguments."""
import json
import os
from pathlib import Path

import ini_set_owned_null_option_protocol as shared
import ini_set_owned_named_null_option_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE = shared.MESSAGE
reach, budget, unchanged = shared.reach, shared.budget, shared.unchanged
PREFIX = shared.PREFIX + r"""
dec $test_ini_owned_named_partial(pstate) : bool
def $test_ini_owned_named_partial(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN pvalue)]
def $test_ini_owned_named_partial(S) = false -- otherwise
dec $test_ini_owned_named_partial_seek(pstate, nat) : pstate
def $test_ini_owned_named_partial_seek(S, 0) = S
def $test_ini_owned_named_partial_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_named_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_named_partial_seek(S, n) = $test_ini_owned_named_partial_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_named_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def handled(state, candidate, warnings, precision, result):
    values = shared.handled(state, candidate, warnings, precision, result)
    finish = state + '_after = ' + state + '_resume[.TODO = ptask_' + state + '*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]'
    # Consuming the marker decrements its still-retained Closure owner.
    values[values.index(finish)] = finish + '[.GC = $gc_buffer_add(' + state + '_resume.GC,HOBJECT n_owner_' + state + ')]'
    return values


def front(state, start, candidate):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')',
        call + '.INDEX = 2', call + '.SELECTION = eps', call + '.PACKS = eps', call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS', '$getclass_live_object(' + state + ',' + owner + ')',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)',
        '$config_nodes(' + call + ') = [HOBJECT ' + owner + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ']', *common.public(state)]


def refusals(state):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    values = []
    for field in ('.OWNER = eps', '.OWNER = (|' + state + '.OBJECTS|)', '.NAMED = false',
            '.LINE = $(' + call + '.LINE + 1)', '.SITE = PORIGIN 0 eps', '.INDEX = 1',
            '.SELECTION = (0)', '.SENT = ' + call + '.SENT[0:1]',
            '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        'pvalue_bad_' + state + ' = PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('bad65'),
        '~$config_ini_null_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN pvalue_bad_' + state + ')])']
    return values


def written_reversed(state, call):
    return ['$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_value_' + state + ',false,preqbytes_value_' + state + '?,porigin_value_' + state + ',z_value_' + state + '))',
        'preqbytes_value_' + state + '? = (' + text('value') + ')',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,1) = ((expression_option_' + state + ',false,preqbytes_option_' + state + '?,porigin_option_' + state + ',z_option_' + state + '))',
        'preqbytes_option_' + state + '? = (' + text('option') + ')',
        '$config_destination(INTRINSIC_INI_SET,preqbytes_value_' + state + '?,0) = (1)',
        '$config_destination(INTRINSIC_INI_SET,preqbytes_option_' + state + '?,1) = (0)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'owned-named-null-true-handlers-and-mixed-prefix':
        candidate = 'PSTRING_CARRIER INTERNED_STRING ' + text('literal-owned65')
        values += [*front('S', 'S_initial', candidate), '~$config_strict(S,pconfigcall_S)',
            '~$config_method_receiver(S,pconfigcall_S)', *written_reversed('S', 'pconfigcall_S'),
            '$compiled_read(S,porigin_value_S) = (PSTRING ' + text('literal-owned65') + ')',
            '$compiled_read(S,porigin_option_S) = (PNULL)',
            '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PSTRING_CARRIER INTERNED_STRING ' + text('wrong65') + '))])',
            *handled('S', candidate, 1, '14', 'true'),
            *front('S_mixed', 'S_after', 'PINT 2111'), 'n_owner_S_mixed = n_owner_S',
            '$config_method_receiver(S_mixed,pconfigcall_S_mixed)',
            '$intrinsic_argument(S_mixed,pconfigcall_S_mixed.SITE,0) = ((expression_mixed,false,eps,porigin_mixed,z_mixed))',
            '$intrinsic_argument(S_mixed,pconfigcall_S_mixed.SITE,1) = ((expression_mixed_value,false,preqbytes_mixed_value?,porigin_mixed_value,z_mixed_value))',
            'preqbytes_mixed_value? = (' + text('value') + ')',
            '$compiled_read(S_mixed,porigin_mixed_value) = (PINT 2111)',
            *handled('S_mixed', 'PINT 2111', 2, '14', 'true'), *refusals('S'), *refusals('S_mixed'),
            *budget('S'), *budget('S_mixed_resume'),
            'S_final = $drive_steps(S_mixed_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|F|H|8192|' + MESSAGE + '|F|2|14')]
    elif name == 'captured-owned-named-null-before-live-owner-and-option-writes':
        values += ['S_pre_found = $test_ini_owned_named_partial_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_named_partial(S_pre)',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
            'pconfigcall_pre.OWNER = (n_owner_pre)', 'pconfigcall_pre.INDEX = 1', 'pconfigcall_pre.NAMED',
            'pconfigcall_pre.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN pvalue_captured)]',
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-owned-value65'),
            '$string_carrier_valid(S_pre,pvalue_captured)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
            *written_reversed('S_pre', 'pconfigcall_pre'),
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_replacement)',
            'n_replacement =/= n_owner_pre', 'S_pre.OBJECTS[n_replacement] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)',
            'S_pre.STORE[n_value] = DEFINED pvalue_live_pre',
            '$string_bytes(pvalue_live_pre) = (' + text('after-value65') + ')',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 1)',
            'S_pre.PRECISIONINI = ' + text('6'), '$test_outputs(S_pre.EVENTS) = ' + text('B|V|'),
            *common.public('S_pre'), *front('S', 'S_pre', 'pvalue_captured'),
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_captured)]]',
            'n_owner_S = n_owner_pre', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            'S.STORE[n_call] = DEFINED (POBJECT n_replacement)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
            'S.PRECISIONINI = ' + text('7'), '$test_outputs(S.EVENTS) = ' + text('B|V|O|'),
            '~$config_method_receiver(S,pconfigcall_S)', *handled('S', 'pvalue_captured', 1, '8', 'false'),
            'S_after.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            *refusals('S'), *budget('S_pre'), *budget('S_resume'),
            'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
            'S_final.PRECISIONINI = ' + text('11'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|W|8192|' + MESSAGE + '|F|8|2|1|ini_get|precision|handler-owned65|D|Z|R|8|11')]
    else:
        assert name == 'strict-owned-named-call-before-weak-explicit-mixed-null'
        values += [*front('S', 'S_initial', 'PINT 2129'), '$config_strict(S,pconfigcall_S)',
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            *written_reversed('S', 'pconfigcall_S'),
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|O|'), 'S.PRECISIONINI = ' + text('9'),
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2129))]',
            '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictOwnedNamedCaller65'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *unchanged('S_error', 'S', 'STORE ENV EVENTS PRECISIONINI ERRORHANDLER'),
            *common.public('S_error'), *front('S_wrapper', 'S_error', 'PINT 2137'),
            'n_owner_S_wrapper = n_owner_S', '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)',
            '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)', '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
            *handled('S_wrapper', 'PINT 2137', 1, '8', 'true'),
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
        for path in (Path(__file__), Path(shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
