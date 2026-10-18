#!/usr/bin/env python3
"""Reached defined() count error precedes raw-null conversion and preserves effects."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_query_arity_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_arity_review_front(pstate) : bool
def $test_query_arity_review_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN pvalue_extra)]
def $test_query_arity_review_front(S) = false -- otherwise
dec $test_query_arity_review_seek(pstate, nat) : pstate
def $test_query_arity_review_seek(S, 0) = S
def $test_query_arity_review_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_query_arity_review_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_arity_review_seek(S, n) = $test_query_arity_review_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_arity_review_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'selected-mixed-case-defined-count-before-null-conversion'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_query_arity_review_seek(S_initial,3000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_query_arity_review_front(S)',
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.KIND = INTRINSIC_DEFINED',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_extra)]',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        'pconfigcall_S.INDEX = 2', '$intrinsic_count(S,pconfigcall_S.SITE) = (2)',
        '$config_invoke_valid(S,pconfigcall_S)', '$dynamic_query_arity_call(pconfigcall_S)',
        '$dynamic_query_arity_valid(S,pconfigcall_S)', '~$config_strict(S,pconfigcall_S)',
        'pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINED',
        'pvalue_extra = PSTRING_CARRIER (REQUEST_STRING n_extra) preqbytes_extra',
        'preqbytes_extra = ' + text('request-extra'), '$string_carrier_valid(S,pvalue_extra)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
        'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|E|'), *common.public('S')]
    for variable, expected in (('call', 'constant'), ('name', 'TRUE'), ('extra', 'after-extra')):
        values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    values += [*common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "ArgumentCountError"', 'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('defined() expects exactly 1 argument, 2 given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('defined'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('file') + ') = PSTRING ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_api_args',
        'S_error.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT pvalue_extra)]',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('queryArityReviewCaller48')]
    values += ['S_error.' + field + ' = S.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS',
        'ERRORHANDLER', 'SOURCES', 'POOLS', 'FILES', 'CLASSCONSTANTCACHE', 'CLASSNAMES')]
    values += ['S_error.STORE[n_result] = DEFINED (PINT 99)',
        'S_error.STORE[n_effects] = DEFINED (PINT 1)', *common.public('S_error'),
        '~$dynamic_query_arity_call(pconfigcall_S[.SENT = [NAMED_SENT (KNOWN PNULL)]])',
        '$dynamic_query_arity_call(pconfigcall_S[.SENT = eps])',
        '~$dynamic_query_arity_valid(S,pconfigcall_S[.SENT = eps])',
        '$dynamic_query_arity_call(pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN (PINT 3))]])',
        '~$dynamic_query_arity_valid(S,pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN (PINT 3))]])',
        '~$dynamic_query_arity_arguments(S,[NAMED_HOLE,NAMED_SENT (KNOWN pvalue_extra)])',
        '~$dynamic_query_arity_call(pconfigcall_S[.OWNER = (0)])',
        '~$dynamic_query_arity_call(pconfigcall_S[.NAMED = true])',
        '~$dynamic_query_arity_call(pconfigcall_S[.KIND = INTRINSIC_DEFINE])',
        'pvalue_bad_extra = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_extra',
        '~$string_carrier_valid(S,pvalue_bad_extra)',
        'pconfigcall_bad_extra = pconfigcall_S[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_bad_extra)]]',
        '$dynamic_query_arity_call(pconfigcall_bad_extra)', '~$dynamic_query_arity_valid(S,pconfigcall_bad_extra)']
    for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT', '.INDEX = 1'):
        values += ['~$dynamic_query_arity_valid(S,pconfigcall_S[' + change + '])']
    for value in ('PARRAY 0', 'POBJECT 0'):
        values += ['~$dynamic_query_arity_arguments(S,[NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN pvalue_extra)])']
    values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
