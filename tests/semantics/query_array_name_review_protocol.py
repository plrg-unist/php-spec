#!/usr/bin/env python3
"""A real query TypeError keeps array COW distinct from a shared reference leaf."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_array_name_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_array_review_front(pstate) : bool
def $test_query_array_review_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_query_array_review_front(S) = false -- otherwise
dec $test_query_array_review_seek(pstate, nat) : pstate
def $test_query_array_review_seek(S, 0) = S
def $test_query_array_review_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_query_array_review_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_array_review_seek(S, n) = $test_query_array_review_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_array_review_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_query_array_review_cell(pstate, nat, int) : bool
def $test_query_array_review_cell(S, n_cell, i) = true
  -- if $(n_cell < |S.STORE|)
  -- if S.STORE[n_cell] = DEFINED (PINT i)
def $test_query_array_review_cell(S, n_cell, i) = false -- otherwise
dec $test_query_array_review_until(pstate, nat, int, nat) : pstate
def $test_query_array_review_until(S, n_cell, i, 0) = S
def $test_query_array_review_until(S, n_cell, i, n) = S
  -- if $(n > 0)
  -- if $test_query_array_review_cell(S,n_cell,i) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_array_review_until(S, n_cell, i, n) = $test_query_array_review_until($drive_steps($test_running(S),1),n_cell,i,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_array_review_cell(S,n_cell,i)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reached(state, expression):
    return [state + '_found = ' + expression,
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', *common.public(state)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def trace_argument(state, label):
    return ['$lookup(' + state + '.ENV,' + text('trace') + ') = (n_trace_cell_' + label + ')',
        state + '.STORE[n_trace_cell_' + label + '] = DEFINED (PARRAY n_trace_' + label + ')',
        state + '.ARRAYS[n_trace_' + label + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + label + ')),ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + label + '))]',
        '$trace_array_field(' + state + ',n_api_' + label + ',' + text('args') + ') = PARRAY n_args_' + label,
        state + '.ARRAYS[n_args_' + label + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_argument_' + label + '))]',
        state + '.ARRAYS[n_argument_' + label + '].ITEMS = [ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_leaf)]']


def checks(program, path, name):
    assert name == 'selected-array-query-trace-shares-scalar-reference-after-cow'
    raw_items = '[ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_leaf)]'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reached('S', '$test_query_array_review_seek(S_initial,3000)'),
        '$test_query_array_review_front(S)',
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.KIND = INTRINSIC_DEFINED', 'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (PARRAY n_input))]',
        'pconfigcall_S.INDEX = 1', 'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        '$config_invoke_valid(S,pconfigcall_S)', '$dynamic_query_array_call(pconfigcall_S)',
        '$dynamic_query_array_valid(S,pconfigcall_S)', '~$dynamic_query_arity_call(pconfigcall_S)',
        '~$config_strict(S,pconfigcall_S)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression,false,eps,porigin_argument,z_argument))',
        '$compiled_read(S,porigin_argument) = eps',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINED',
        'S.ARRAYS[n_input] = parray_input', 'parray_input.ITEMS = ' + raw_items,
        'n_cell <- S.REFCELLS', '(HCELL n_cell) <- S.ALLOCATIONS', 'S.STORE[n_cell] = DEFINED (PINT 1237)',
        '$lookup(S.ENV,' + text('cell') + ') = (n_cell)',
        'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_leaf) preqbytes_leaf',
        'preqbytes_leaf = ' + text('captured-plain51'), '$string_carrier_valid(S,pvalue_leaf)',
        '$dynamic_query_array_entries(S,parray_input.ITEMS)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (PARRAY n_input)',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = (' + text('constant') + ')',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$test_outputs(S.EVENTS) = ' + text('B|A|'), 'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps',
        *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('defined(): Argument #1 ($constant_name) must be of type string, array given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('defined'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_input))]',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('queryArrayReviewCaller51'),
        'S_error.ARRAYS[n_input] = parray_input']
    values += ['S_error.' + field + ' = S.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS', 'REFCELLS',
        'ERRORHANDLER', 'AUTOLOAD', 'SOURCES', 'POOLS', 'FILES', 'STATICS', 'CLASSNAMES', 'CLASSCONSTANTCACHE')]
    values += [*common.public('S_error'),
        *reached('S_cow', '$test_query_array_review_until(S_error,n_cell,1249,3000)'),
        'S_cow.STORE[n_cell] = DEFINED (PINT 1249)', 'S_cow.ARRAYS[n_input].ITEMS = ' + raw_items,
        'S_cow.STORE[n_name] = DEFINED (PARRAY n_live)', 'n_live =/= n_input',
        'S_cow.ARRAYS[n_live].ITEMS = [ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_live_plain)]',
        '$string_bytes(pvalue_live_plain) = (' + text('live-plain51') + ')',
        *trace_argument('S_cow', 'cow'), 'n_argument_cow = n_input',
        'S_cow.STORE[n_result] = DEFINED (PINT 99)',
        *reached('S_alias', '$test_query_array_review_until(S_cow,n_cell,1277,3000)'),
        'S_alias.STORE[n_cell] = DEFINED (PINT 1277)',
        'S_alias.STORE[n_name] = DEFINED (PARRAY n_live)', 'S_alias.ARRAYS[n_live] = S_cow.ARRAYS[n_live]',
        'S_alias.ARRAYS[n_input].ITEMS = ' + raw_items, *trace_argument('S_alias', 'alias'),
        'S_alias.STORE[n_result] = DEFINED (PINT 99)', 'S_alias.STORE[n_effects] = DEFINED (PINT 1)',
        'S_alias.USERCONSTANTS = eps', 'S_alias.AUTOLOAD = S.AUTOLOAD',
        *budget('S'), *budget('S_cow')]
    for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.INDEX = 0'):
        values += ['~$dynamic_query_array_valid(S,pconfigcall_S[' + change + '])']
    for change in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINE',
            '.SENT = eps', '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]',
            '.SENT = [NAMED_SENT (KNOWN (PSTRING ' + text('TRUE') + '))]'):
        values += ['~$dynamic_query_array_call(pconfigcall_S[' + change + '])']
    values += ['~$dynamic_query_array_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (PARRAY (|S.ARRAYS|)))]] )',
        '~$dynamic_query_array_entries(S,[ENTRY (KINT 0) (ALIAS (|S.STORE|))])',
        '~$dynamic_query_array_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_input))])',
        '~$dynamic_query_array_entries(S,[ENTRY (KINT 0) (DIRECT (POBJECT 0))])',
        'S_no_ref = S[.REFCELLS = eps]', '~$dynamic_query_array_valid(S_no_ref,pconfigcall_S)',
        'pvalue_bad_leaf = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_leaf',
        '~$string_carrier_valid(S,pvalue_bad_leaf)',
        'parray_bad_leaf = parray_input[.ITEMS = [ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_bad_leaf)]]',
        'S_bad_leaf = S[.ARRAYS = $array_replace(S.ARRAYS,n_input,parray_bad_leaf)]',
        '~$dynamic_query_array_valid(S_bad_leaf,pconfigcall_S)']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
