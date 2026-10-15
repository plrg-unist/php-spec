#!/usr/bin/env python3
"""Reached scalar flag reception fixes class-name error priority and raw traces."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_class_scalar_flag_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_class_scalar_front(pstate, preqbytes) : bool
def $test_class_scalar_front(S, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_class_define_scalar_call(pconfigcall)
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_class_scalar_front(S, preqbytes) = false -- otherwise
dec $test_class_scalar_seek(pstate, preqbytes, nat) : pstate
def $test_class_scalar_seek(S, preqbytes, 0) = S
def $test_class_scalar_seek(S, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_class_scalar_front(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_class_scalar_seek(S, preqbytes, n) = $test_class_scalar_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_class_scalar_front(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, name, value):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_class_scalar_seek(' + start + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_class_scalar_front(' + state + ',' + text(name) + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_name_' + state + '),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN pvalue_flag_' + state + ')]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_class_define_scalar_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_flag_call(' + call + ')', '~$dynamic_scalar_define_flag_valid(' + state + ',' + call + ')',
        '~$dynamic_class_define_call(' + call + ')', '$error_handler_eligible(' + state + ',2)',
        state + '.USERCONSTANTS = eps', *common.public(state)]


def error(after, before, value, given=None, caller=None):
    call = 'pconfigcall_' + before
    message = 'define(): Argument #1 ($constant_name) cannot be a class constant' if given is None else (
        'define(): Argument #3 ($case_insensitive) must be of type bool, ' + given + ' given')
    frames = ['ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + after + '))']
    if caller:
        frames += ['ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + after + '))']
    values = [*common.step(after, before), after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = ' + json.dumps('ValueError' if given is None else 'TypeError'),
        'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)', '$throwable_live(' + after + ',n_error_' + after + ')',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [' + ','.join(frames) + ']',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name_' + before + '),ENTRY (KINT 1) (DIRECT (' + value + ')),ENTRY (KINT 2) (DIRECT pvalue_flag_' + before + ')]',
        *[after + '.' + field + ' = ' + before + '.' + field for field in 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS EVENTS SOURCES POOLS FILES STATICS ERRORHANDLER ERRORHANDLERS'.split()],
        *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + after + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-class-names-with-quiet-scalar-flags':
        values += [*front('S', 'S_initial', 'Int::Bad37', 'PINT 317'), '~$config_strict(S,pconfigcall_S)',
            'pvalue_flag_S = PINT 2', 'pconfigcall_S.SELECTION = eps', 'pconfigcall_S.LINE = 6',
            *error('S_error', 'S', 'PINT 317'),
            *front('S_string', 'S_error', 'String::Bad37', 'PINT 318'),
            '$string_bytes(pvalue_flag_S_string) = (' + text('false') + ')', '$truth(S_string,pvalue_flag_S_string)',
            *error('S_string_error', 'S_string', 'PINT 318'),
            *front('S_float', 'S_string_error', 'Float::Bad37', 'PINT 319'),
            'pvalue_flag_S_float = PFLOAT 4612811918334230528', *error('S_float_error', 'S_float', 'PINT 319'),
            'pconfigcall_bad_name = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('Other::Name37') + '))]',
            '$dynamic_class_define_scalar_call(pconfigcall_bad_name)', '$config_invoke_valid(S,pconfigcall_bad_name)',
            '~$dynamic_class_define_scalar_valid(S,pconfigcall_bad_name)',
            'S_bad = $drive_steps(S[.TODO = (CONFIG_INVOKE pconfigcall_bad_name) :: ptask_S*],1)',
            'S_bad.COMPLETION = UNSUPPORTED "class-qualified scalar define flag capture"',
            '~$dynamic_class_define_scalar_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PINT 0))])',
            *budget('S'), *budget('S_float')]
        for flag in ('PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 9221120237041090560', 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_class_define_scalar_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
        for value in ('PSTRING ' + text('Ordinary37'), 'PSTRING (' + text('::') + ' ++ [0])', 'PINT 3'):
            values += ['~$dynamic_class_define_scalar_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + value + '))])']
    else:
        strict = name == 'strict-scalar-flag-precedes-class-name-error'
        assert strict or name == 'captured-scalar-flag-before-class-name-error'
        actual_name, value = ('Strict::Bad37', 'PINT 329') if strict else ('Captured::Scalar37', 'PINT 323')
        values += [*front('S', 'S_initial', actual_name, value),
            ('$config_strict' if strict else '~$config_strict') + '(S,pconfigcall_S)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (' + ('PBOOL true' if strict else 'PINT 0') + ')',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('defined') + ')',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)']
        if strict:
            values += ['pvalue_flag_S = PINT 2', *error('S_error', 'S', value, 'int'),
                *front('S_string', 'S_error', 'Strict::String37', 'PINT 330'),
                '$config_strict(S_string,pconfigcall_S_string)', '$string_bytes(pvalue_flag_S_string) = (' + text('false') + ')',
                *error('S_string_error', 'S_string', 'PINT 330', 'string'),
                *front('S_float', 'S_string_error', 'Strict::Float37', 'PINT 331'),
                '$config_strict(S_float,pconfigcall_S_float)', 'pvalue_flag_S_float = PFLOAT 4612811918334230528',
                *error('S_float_error', 'S_float', 'PINT 331', 'float')]
        else:
            values += ['pvalue_flag_S = PSTRING_CARRIER (REQUEST_STRING n_flag_string) preqbytes_flag',
                'preqbytes_flag = ' + text('false'), '$string_carrier_valid(S,pvalue_flag_S)', '$truth(S,pvalue_flag_S)',
                *error('S_error', 'S', value, caller='classScalarCaller37'),
                'n_bad_string = |S.STRINGDATA|', 'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_flag',
                '~$string_carrier_valid(S,pvalue_bad_flag)',
                '~$dynamic_class_define_scalar_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])']
        values += ['S_error.STORE[n_result] = DEFINED (PINT 99)', *budget('S')]
        for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT', '.OWNER = (0)'):
            values += ['~$dynamic_class_define_scalar_valid(S,pconfigcall_S[' + field + '])']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
