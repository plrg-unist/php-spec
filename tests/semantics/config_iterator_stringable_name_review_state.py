#!/usr/bin/env python3
"""Independent real-source copied option, cast and normal retirement guards."""
from pathlib import Path

import config_iterator_stringable_name_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public

HELPERS = shared.HELPERS + r'''
dec $a98_review_echo(pstate, ptbytes) : bool
def $a98_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a98_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1900) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if pconfigiterator.ITEMS = eps
def $list_warning_frontier(S, 1901) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if pconfigiterator.ITEMS = eps
def $list_warning_frontier(S, 1902) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 1903) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n porigin_child z_child z_call) :: ptask*
def $list_warning_frontier(S, 1904) = $a98_review_echo(S, $ptascii("O:"))
def $list_warning_frontier(S, 1905) = $a98_review_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 1906) = true
  -- if S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n pvalue) :: ptask*
'''


def seek(start, stage, state):
    return [f'{state}_found = $list_warning_seek({start}, {stage}, 4000)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$list_warning_frontier({state}, {stage})']


def cell(state, name, value):
    return [f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{name})',
            f'{state}.STORE[n_{name}] = DEFINED {value}']


def conditions(name, program, path, stdout):
    retained = name.endswith('retained-named')
    reference = name.endswith('reference-key')
    value, rebound, before, old = ((13, 47, 17, 17) if retained else
                                  (9, 33, 21, 27) if reference else
                                  (7, 31, 19, 23))
    checks = initial(program, path) + seek('S_initial', 1900, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_iterator',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
    ] + cell('S_cache', 'optionWatch', '(POBJECT n_option_watch)') + [
        '$weakref_get(S_cache, n_option_watch) = POBJECT n_option',
        '$stringable_instance(S_cache, n_option)',
        '~$config_iterator_argument(S_cache, POBJECT n_option)',
        '$config_iterator_send_argument(S_cache, POBJECT n_option)',
        '~$config_iterator_send_argument(S_cache[.ALLOCATIONS = eps], POBJECT n_option)',
    ]
    if reference:
        checks += cell('S_cache', 'name', 'pvalue_initial') + [
            '$string_bytes(pvalue_initial) = ($ptascii("initial"))',
            'pconfigiterator_cache.CURRENT = REFERENCE n_name',
            '$config_iterator_current_value(S_cache, pconfigiterator_cache, REFERENCE n_name) = (pvalue_initial)',
            owners('S_cache', 'HCELL n_name', 2),
        ]
    else:
        checks += ['pconfigiterator_cache.CURRENT = KNOWN (POBJECT n_option)',
                   '$config_iterator_current_value(S_cache, pconfigiterator_cache, KNOWN (POBJECT n_option)) = (POBJECT n_option)']
    checks += public('S_cache') + seek('S_cache', 1901, 'S_send') + [
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
        '$config_iterator_valid(S_send, pconfigiterator_send, "send")',
        '$config_iterator_current_value(S_send, pconfigiterator_send, pconfigiterator_send.CURRENT) = (POBJECT n_option)',
        '$config_iterator_current_argument(S_send, pconfigiterator_send)',
        'PhpStep: S_send ~> S_sent',
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_send*',
        'pconfigiterator_sent.CURRENT = KNOWN PNULL',
        'pconfigiterator_sent.KEY = KNOWN PNULL',
        '$config_iterator_argument_nodes(pconfigiterator_sent) = [HOBJECT n_option]',
    ]
    if reference:
        checks += ['pconfigiterator_send.CURRENT = REFERENCE n_name',
                   'S_send.STORE[n_name] = DEFINED (POBJECT n_option)',
                   'S_sent.STORE[n_name] = DEFINED (POBJECT n_option)',
                   owners('S_send', 'HCELL n_name', 2),
                   owners('S_sent', 'HCELL n_name', 1),
                   owners('S_send', 'HOBJECT n_option', 1),
                   owners('S_sent', 'HOBJECT n_option', 2)]
    checks += public('S_sent') + budget('S_sent', 'S_send_budget')
    checks += seek('S_sent', 1902, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        'pconfigiterator_ready.OBJECT = n_iterator',
        'pconfigiterator_ready.CURRENT = KNOWN PNULL',
        'pconfigiterator_ready.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '~$config_iterator_valid(S_ready[.CODE = eps], pconfigiterator_ready, "ready")',
        '~$config_iterator_valid(S_ready[.SOURCES = eps], pconfigiterator_ready, "ready")',
        '~$config_iterator_valid(S_ready, pconfigiterator_ready[.CURRENT = KNOWN (POBJECT n_option)], "ready")',
        '$config_pack_prefix(pconfigiterator_ready.CALL, pconfigiterator_ready.ITEMS, false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        f'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_option)), NAMED_SENT (KNOWN (PINT {value}))]',
        '$config_iterator_copied_call(S_ready, pconfigcall)',
        '$config_invoke_valid(S_ready, pconfigcall)',
        '~$config_iterator_copied_call(S_ready, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
        '~$config_iterator_copied_call(S_ready, pconfigcall[.OWNER = (n_option_watch)])',
        '$config_string_source(S_ready, pconfigcall) = ((porigin_child, z_child))',
        '$intrinsic_argument(S_ready, pconfigcall.SITE, 0) = ((expression, true, eps, porigin_child, z_child))',
        '$config_string_site_valid(S_ready, pconfigcall, n_option, porigin_child, z_child, pconfigcall.LINE)',
        '~$config_string_site_valid(S_ready, pconfigcall, n_option, porigin_child, z_child, $(pconfigcall.LINE + 1))',
        '~$config_string_site_valid(S_ready[.CODE = eps], pconfigcall, n_option, porigin_child, z_child, pconfigcall.LINE)',
        'S_ready.ITERATORS = eps',
        'S_ready.PRECISIONINI = $ptascii("' + ('14' if retained else str(before)) + '")',
        owners('S_ready', 'HOBJECT n_option', 2 if retained else 1),
    ] + cell('S_ready', 'casts', '(PINT 0)') + cell('S_ready', 'value', f'(PINT {rebound})')
    if not retained:
        checks += ['~((HOBJECT n_iterator) <- S_ready.ALLOCATIONS)']
    checks += public('S_ready') + seek('S_ready', 1903, 'S_converted') + [
        'S_converted.TODO = (CONFIG_STRING_RESULT pconfigcall n_option porigin_child z_child pconfigcall.LINE) :: ptask_converted*',
        'S_converted.RESULT = KNOWN pvalue_converted',
        '$string_bytes(pvalue_converted) = ($ptascii("precision"))',
        '$string_carrier_valid(S_converted, pvalue_converted)',
        '$config_string_site_valid(S_converted, pconfigcall, n_option, porigin_child, z_child, pconfigcall.LINE)',
        owners('S_converted', 'HOBJECT n_option', 3 if retained else 2),
        'S_converted.PRECISIONINI = $ptascii("' + str(before) + '")',
    ] + cell('S_converted', 'casts', '(PINT 1)') + public('S_converted')
    if not retained:
        checks += seek('S_converted', 1904, 'S_option_dtor') + [
            'S_option_dtor.CURRENT = (pcallcontext_dtor)',
            '$destructor_context_call(pcallcontext_dtor, S_option_dtor.CURRENT, S_option_dtor.FRAMES) = (pdestructorcall)',
            'pdestructorcall.OBJECT = n_option', 'pdestructorcall.PENDING = eps',
            '$destructor_call_live(S_option_dtor, pdestructorcall)',
            'S_option_dtor.PRECISIONINI = $ptascii("' + str(before) + '")',
            '~((HOBJECT n_iterator) <- S_option_dtor.ALLOCATIONS)',
        ] + public('S_option_dtor')
    checks += seek('S_converted' if retained else 'S_option_dtor', 1906, 'S_receipt') + [
        'S_receipt.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_option pvalue_converted) :: ptask_receipt*',
        '$task_nodes(CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_option pvalue_converted) = eps',
        '$config_iterator_string_receive_valid(S_receipt, pconfigcall, n_option, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt, pconfigcall[.LINE = $(pconfigcall.LINE + 1)], n_option, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt, pconfigcall[.OWNER = (n_option_watch)], n_option, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt, pconfigcall[.INDEX = 0], n_option, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt, pconfigcall, n_iterator, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt, pconfigcall, n_option, PNULL)',
        '~$config_iterator_string_receive_valid(S_receipt[.CODE = eps], pconfigcall, n_option, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt[.SOURCES = eps], pconfigcall, n_option, pvalue_converted)',
        '~$config_iterator_string_receive_valid(S_receipt[.OBJECTS[n_option] = STDINSTANCE], pconfigcall, n_option, pvalue_converted)',
        'S_receipt.PRECISIONINI = $ptascii("' + str(old) + '")',
        owners('S_receipt', 'HOBJECT n_option', 1 if retained else 0),
        'PhpStep: S_receipt ~> S_body_done',
        'S_body_done.PRECISIONINI = $ptascii("' + str(value) + '")',
        'S_body_done.RESULT = KNOWN pvalue_return',
        '$string_bytes(pvalue_return) = ($ptascii("' + str(old) + '"))',
    ] + public('S_receipt') + public('S_body_done') + budget('S_receipt', 'S_receive_budget')
    if not retained:
        checks += ['~((HOBJECT n_option) <- S_receipt.ALLOCATIONS)',
                   '~$stringable_instance(S_receipt, n_option)']
    checks += seek('S_body_done', 1905, 'S_after') + [
        'S_after.PRECISIONINI = $ptascii("' + str(value) + '")',
        '$weakref_get(S_after, n_option_watch) = ' + ('POBJECT n_option' if retained else 'PNULL'),
    ] + cell('S_after', 'result', 'pvalue_result') + [
        '$string_bytes(pvalue_result) = ($ptascii("' + str(old) + '"))',
    ] + cell('S_after', 'casts', '(PINT 1)') + public('S_after')
    return checks + finish('S_after', stdout, ['HOBJECT n_option', 'HOBJECT n_iterator', 'HOBJECT n_option_watch'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, model_timeout=360,
        extra_inputs=(Path(__file__), Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
