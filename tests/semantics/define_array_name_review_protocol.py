#!/usr/bin/env python3
"""Actual define array-name rejection follows effects but precedes flag handling."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_array_name_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_define_array_review_front(pstate, nat) : bool
def $test_define_array_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_array)),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN (PBOOL true))]
def $test_define_array_review_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("Array"))
def $test_define_array_review_front(S, n_stage) = false -- otherwise
dec $test_define_array_review_seek(pstate, nat, nat) : pstate
def $test_define_array_review_seek(S, n_stage, 0) = S
def $test_define_array_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_define_array_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_array_review_seek(S, n_stage, n) = $test_define_array_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_array_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, stage):
    return [state + '_found = $test_define_array_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_define_array_review_front(' + state + ',' + str(stage) + ')',
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        '$config_invoke_valid(' + state + ',pconfigcall_' + state + ')', *common.public(state)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'captured-define-array-name-before-reference-and-true-flag-effects'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', 0),
        'pconfigcall_S.KIND = INTRINSIC_DEFINE',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN pvalue_candidate),NAMED_SENT (KNOWN (PBOOL true))]',
        'pconfigcall_S.INDEX = 3', '$intrinsic_count(S,pconfigcall_S.SITE) = (3)',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        '$dynamic_define_array_name_call(pconfigcall_S)', '$dynamic_define_array_name_valid(S,pconfigcall_S)',
        '~$dynamic_define_arity_call(pconfigcall_S)', '~$dynamic_query_array_call(pconfigcall_S)',
        '$dynamic_constant_case_flag(pconfigcall_S)', '~$dynamic_constant_case_valid(S,pconfigcall_S)',
        '~$config_strict(S,pconfigcall_S)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression,false,eps,porigin_argument,z_argument))',
        '$compiled_read(S,porigin_argument) = eps',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'S.ARRAYS[n_input] = parray_input',
        'parray_input.ITEMS = [ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_leaf)]',
        'n_cell <- S.REFCELLS', '(HCELL n_cell) <- S.ALLOCATIONS', 'S.STORE[n_cell] = DEFINED (PINT 1361)',
        '$lookup(S.ENV,' + text('cell') + ') = (n_cell)',
        'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_leaf) preqbytes_leaf',
        'preqbytes_leaf = ' + text('captured-name52'), '$string_carrier_valid(S,pvalue_leaf)',
        'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate',
        'preqbytes_candidate = ' + text('captured-value52'), '$string_carrier_valid(S,pvalue_candidate)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (PARRAY n_live)',
        'n_live =/= n_input',
        'S.ARRAYS[n_live].ITEMS = [ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_live_plain)]',
        '$string_bytes(pvalue_live_plain) = (' + text('flag-live52') + ')',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = (' + text('defined') + ')',
        '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED (PINT 997)',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$test_outputs(S.EVENTS) = ' + text('B|V|F|'), 'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps',
        *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, array given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_input)),ENTRY (KINT 1) (DIRECT pvalue_candidate),ENTRY (KINT 2) (DIRECT (PBOOL true))]',
        '$node_children(S_error,HARRAY n_args) = [HARRAY n_input]',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('defineArrayReviewCaller52'),
        'S_error.ARRAYS[n_input] = parray_input', 'S_error.ARRAYS[n_live] = S.ARRAYS[n_live]']
    values += ['S_error.' + field + ' = S.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS', 'REFCELLS',
        'ERRORHANDLER', 'AUTOLOAD', 'SOURCES', 'POOLS', 'FILES', 'STATICS', 'CLASSNAMES', 'CLASSCONSTANTCACHE')]
    values += [*common.public('S_error'), *budget('S')]
    for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.INDEX = 2'):
        values += ['~$dynamic_define_array_name_valid(S,pconfigcall_S[' + change + '])']
    for change in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_CONSTANT', '.SENT = eps',
            '.SENT = pconfigcall_S.SENT[0:1]', '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$dynamic_define_array_name_call(pconfigcall_S[' + change + '])']
    values += ['pconfigcall_two = pconfigcall_S[.SENT = pconfigcall_S.SENT[0:2]][.INDEX = 2]',
        '$dynamic_define_array_name_call(pconfigcall_two)', '~$dynamic_define_array_name_valid(S,pconfigcall_two)',
        '~$dynamic_define_array_name_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PARRAY (|S.ARRAYS|)))])',
        '~$dynamic_define_array_name_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PARRAY n_input))])',
        '~$dynamic_define_array_name_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (POBJECT 0))])',
        'S_no_ref = S[.REFCELLS = eps]', '~$dynamic_define_array_name_valid(S_no_ref,pconfigcall_S)',
        'pvalue_bad_leaf = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_leaf',
        'parray_bad_leaf = parray_input[.ITEMS = [ENTRY (KSTRING ' + text('alias') + ') (ALIAS n_cell),ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_bad_leaf)]]',
        'S_bad_leaf = S[.ARRAYS = $array_replace(S.ARRAYS,n_input,parray_bad_leaf)]',
        '~$dynamic_define_array_name_valid(S_bad_leaf,pconfigcall_S)']
    for slot, variable, spelling in ((1, 'candidate', 'captured-value52'), (2, 'flag', 'flag52')):
        values += ['pvalue_bad_' + variable + ' = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text(spelling),
            '~$string_carrier_valid(S,pvalue_bad_' + variable + ')',
            '~$dynamic_define_array_name_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,' + str(slot) + ',KNOWN pvalue_bad_' + variable + ')])']
    values += [*front('S_absent', 'S_error', 1),
        'S_absent.USERCONSTANTS = eps', 'S_absent.STORE[n_result] = DEFINED (PINT 99)',
        'S_absent.STORE[n_effects] = DEFINED (PINT 2)',
        '~$dynamic_define_array_name_call(pconfigcall_S_absent)',
        *common.step('S_checked', 'S_absent', 'PBOOL false'),
        'S_checked.TODO = ptask_S_absent*', 'S_checked.STORE = S_absent.STORE',
        'S_checked.USERCONSTANTS = eps', 'S_checked.STRINGDATA = S_absent.STRINGDATA', *budget('S_absent')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
