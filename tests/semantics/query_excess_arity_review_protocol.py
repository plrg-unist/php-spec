#!/usr/bin/env python3
"""Reached excess count skips class lookup, then an actual one-argument call recovers."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_excess_arity_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_excess_review_front(pstate, nat) : bool
def $test_query_excess_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_extra), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (KNOWN pvalue_last)]
def $test_query_excess_review_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name)]
  -- if $string_bytes(pvalue_name) = ($ptascii("TRUE"))
def $test_query_excess_review_front(S, n_stage) = false -- otherwise
dec $test_query_excess_review_seek(pstate, nat, nat) : pstate
def $test_query_excess_review_seek(S, n_stage, 0) = S
def $test_query_excess_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_query_excess_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_excess_review_seek(S, n_stage, n) = $test_query_excess_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_excess_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, stage):
    return [state + '_found = $test_query_excess_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_query_excess_review_front(' + state + ',' + str(stage) + ')',
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        '$config_invoke_valid(' + state + ',pconfigcall_' + state + ')', *common.public(state)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-class-like-query-count-before-lookup-and-one-arg-recovery'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', 0),
        'pconfigcall_S.KIND = INTRINSIC_CONSTANT',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue_extra),NAMED_SENT (KNOWN (PBOOL false)),NAMED_SENT (KNOWN pvalue_last)]',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        'pconfigcall_S.INDEX = 4', '$intrinsic_count(S,pconfigcall_S.SITE) = (4)',
        '$dynamic_query_arity_call(pconfigcall_S)', '$dynamic_query_arity_valid(S,pconfigcall_S)',
        '~$config_strict(S,pconfigcall_S)',
        'pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|E|')]
    for variable, spelling in (('name', 'MissingArity50::VALUE'),
            ('extra', 'captured-extra50'), ('last', 'captured-last50')):
        values += ['pvalue_' + variable + ' = PSTRING_CARRIER (REQUEST_STRING n_' + variable + ') preqbytes_' + variable,
            'preqbytes_' + variable + ' = ' + text(spelling), '$string_carrier_valid(S,pvalue_' + variable + ')']
    for variable, spelling in (('call', 'defined'), ('name', 'TRUE'),
            ('extra', 'after-extra50'), ('lastExtra', 'after-last50')):
        values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(spelling) + ')']
    values += [*common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "ArgumentCountError"', 'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('constant() expects exactly 1 argument, 4 given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('constant'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT pvalue_extra),ENTRY (KINT 2) (DIRECT (PBOOL false)),ENTRY (KINT 3) (DIRECT pvalue_last)]',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('queryExcessReviewCaller50')]
    values += ['S_error.' + field + ' = S.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS',
        'ERRORHANDLER', 'AUTOLOAD', 'SOURCES', 'POOLS', 'FILES', 'STATICS', 'CLASSNAMES', 'CLASSCONSTANTCACHE')]
    values += [*common.public('S_error'),
        '~$dynamic_query_arity_call(pconfigcall_S[.SENT = pconfigcall_S.SENT[0:1]])',
        '$dynamic_query_arity_call(pconfigcall_S[.SENT = pconfigcall_S.SENT[0:3]])',
        '~$dynamic_query_arity_valid(S,pconfigcall_S[.SENT = pconfigcall_S.SENT[0:3]])',
        '$dynamic_query_arity_call(pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]])',
        '~$dynamic_query_arity_valid(S,pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]])',
        '~$dynamic_query_arity_call(pconfigcall_S[.OWNER = (0)])',
        '~$dynamic_query_arity_call(pconfigcall_S[.NAMED = true])',
        '~$dynamic_query_arity_call(pconfigcall_S[.KIND = INTRINSIC_DEFINE])']
    for slot, variable in ((0, 'name'), (1, 'extra'), (3, 'last')):
        values += ['pvalue_bad_' + variable + ' = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_' + variable,
            '~$string_carrier_valid(S,pvalue_bad_' + variable + ')',
            'pconfigcall_bad_' + variable + ' = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,' + str(slot) + ',KNOWN pvalue_bad_' + variable + ')]',
            '$dynamic_query_arity_call(pconfigcall_bad_' + variable + ')',
            '~$dynamic_query_arity_valid(S,pconfigcall_bad_' + variable + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = eps', '.INDEX = 3'):
        values += ['~$dynamic_query_arity_valid(S,pconfigcall_S[' + field + '])']
    values += [*front('S_normal', 'S_error', 1),
        'pconfigcall_S_normal.KIND = INTRINSIC_DEFINED',
        'pconfigcall_S_normal.SENT = [NAMED_SENT (KNOWN pvalue_recovery)]',
        '$string_bytes(pvalue_recovery) = (' + text('TRUE') + ')',
        '~$dynamic_query_arity_call(pconfigcall_S_normal)',
        'pconfigcall_S_normal.SELECTION = (n_recovery_selection)',
        'S_normal.SELECTEDCALLS[n_recovery_selection].KIND = INTRINSIC_DEFINED',
        'S_normal.STORE[n_result] = DEFINED (PINT 99)',
        'S_normal.STORE[n_effects] = DEFINED (PINT 1)',
        *common.step('S_recovered', 'S_normal', 'PBOOL true'),
        'S_recovered.TODO = ptask_S_normal*',
        'S_recovered.STORE = S_normal.STORE', 'S_recovered.USERCONSTANTS = S_normal.USERCONSTANTS',
        'S_recovered.STRINGDATA = S_normal.STRINGDATA', 'S_recovered.AUTOLOAD = S_normal.AUTOLOAD',
        *budget('S'), *budget('S_normal')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
