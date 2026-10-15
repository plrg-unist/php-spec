#!/usr/bin/env python3
"""Genuine class-name rejection fronts preserve captures and skip flag warnings."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_class_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_class_define_front(pstate, preqbytes) : bool
def $test_class_define_front(S, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_class_define_call(pconfigcall)
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_class_define_front(S, preqbytes) = false -- otherwise
dec $test_class_define_seek(pstate, preqbytes, nat) : pstate
def $test_class_define_seek(S, preqbytes, 0) = S
def $test_class_define_seek(S, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_class_define_front(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_class_define_seek(S, preqbytes, n) = $test_class_define_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_class_define_front(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, name, value, flag):
    call = 'pconfigcall_' + state
    args = '[NAMED_SENT (KNOWN pvalue_name_' + state + '),NAMED_SENT (KNOWN (' + value + '))'
    args += '' if flag is None else ',NAMED_SENT (KNOWN (PBOOL ' + flag + '))'
    return [state + '_found = $test_class_define_seek(' + start + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_class_define_front(' + state + ',' + text(name) + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*', call + '.SENT = ' + args + ']',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_class_define_valid(' + state + ',' + call + ')',
        '$error_handler_eligible(' + state + ',2)', state + '.USERCONSTANTS = eps', *common.public(state)]


def error(after, before, arguments):
    call = 'pconfigcall_' + before
    return [*common.step(after, before), after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "ValueError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$throwable_live(' + after + ',n_error_' + after + ')',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text('define(): Argument #1 ($constant_name) cannot be a class constant') + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after,
        '$(|'+ after + '.ARRAYS[n_trace_' + after + '].ITEMS| >= 1)',
        after + '.ARRAYS[n_trace_' + after + '].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + after + '))',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [' + ','.join('ENTRY (KINT ' + str(i) + ') (DIRECT (' + v + '))' for i, v in enumerate(arguments)) + ']',
        *[after + '.' + field + ' = ' + before + '.' + field for field in 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS EVENTS SOURCES POOLS FILES STATICS'.split()],
        *common.public(after)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-class-names-omitted-and-bool-flags':
        values += [*front('S', 'S_initial', 'A::B36', 'PINT 211', None), '~$config_strict(S,pconfigcall_S)',
            'pconfigcall_S.SELECTION = eps', 'pconfigcall_S.LINE = 6',
            *error('S_error', 'S', ['pvalue_name_S', 'PINT 211']),
            *front('S_false', 'S_error', 'C::D36', 'PINT 212', 'false'),
            *error('S_false_error', 'S_false', ['pvalue_name_S_false', 'PINT 212', 'PBOOL false']),
            *front('S_true', 'S_false_error', 'E::F36', 'PINT 213', 'true'),
            '~$dynamic_constant_case_valid(S_true,pconfigcall_S_true)',
            *error('S_true_error', 'S_true', ['pvalue_name_S_true', 'PINT 213', 'PBOOL true']),
            'pconfigcall_bad_name = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('Other::Name36') + '))]',
            '$dynamic_class_define_call(pconfigcall_bad_name)', '$config_invoke_valid(S,pconfigcall_bad_name)',
            '~$dynamic_class_define_valid(S,pconfigcall_bad_name)',
            'S_bad = $drive_steps(S[.TODO = (CONFIG_INVOKE pconfigcall_bad_name) :: ptask_S*],1)',
            'S_bad.COMPLETION = UNSUPPORTED "class-qualified define capture"',
            'pconfigcall_bad_flag = pconfigcall_S_true[.SENT = $named_slot_set(pconfigcall_S_true.SENT,2,KNOWN (PBOOL false))]',
            '$dynamic_class_define_call(pconfigcall_bad_flag)', '~$dynamic_class_define_valid(S_true,pconfigcall_bad_flag)',
            *budget('S'), *budget('S_true')]
        for flag in ('PNULL', 'PINT 1', 'PFLOAT 9221120237041090560'):
            values += ['~$dynamic_class_define_call(pconfigcall_S_true[.SENT = $named_slot_set(pconfigcall_S_true.SENT,2,KNOWN (' + flag + '))])']
    else:
        strict = name == 'strict-class-name-after-all-argument-effects'
        assert strict or name == 'captured-class-name-before-ignored-true-warning'
        actual_name, value, flag = ('Strict::Bad36', 'PINT 229', 'false') if strict else ('Captured::Flag36', 'PINT 223', 'true')
        values += [*front('S', 'S_initial', actual_name, value, flag),
            ('$config_strict' if strict else '~$config_strict') + '(S,pconfigcall_S)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL ' + ('true' if strict else 'false') + ')',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('defined') + ')',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *error('S_error', 'S', ['pvalue_name_S', value, 'PBOOL ' + flag]),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *budget('S')]
        for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_class_define_valid(S,pconfigcall_S[' + field + '])']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
