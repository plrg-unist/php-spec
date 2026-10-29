#!/usr/bin/env python3
"""Reached saved-key cleanup with a final temporary INPUT and copied payload."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_input_finalizer_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import finish, initial, owners, public, seek


SOURCES = SimpleNamespace(CASES=cases.CASES, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a70_peer_echo(pstate, ptbytes) : bool
def $a70_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a70_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 970) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 971) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 972) = $a70_peer_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 973) = $a70_peer_echo(S, $ptascii("P:"))
def $list_warning_frontier(S, 974) = $a70_peer_echo(S, $ptascii("E:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def destructor(state, label, target):
    return [f'{state}.CURRENT = (pcallcontext_{label})',
            f'$destructor_context_call(pcallcontext_{label}, {state}.CURRENT, {state}.FRAMES) = (pdestructorcall_{label})',
            f'pdestructorcall_{label}.OBJECT = {target}',
            f'pdestructorcall_{label}.PENDING = (n_saved)',
            f'$destructor_call_live({state}, pdestructorcall_{label})']


def conditions(name, program, path, stdout):
    assert name == cases.NAME
    checks = initial(program, path) + seek('S_initial', 970, 'S_key_throw') + [
        'S_key_throw.TODO = (THROW_SEARCH n_saved) :: (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_key_tail*',
        'pconfigiterator_key.OBJECT = n_iterator',
        'pconfigiterator_key.INPUT = KNOWN (POBJECT n_iterator)',
        'pconfigiterator_key.PRODUCER = eps',
        'pconfigiterator_key.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]',
        '$config_iterator_argument_nodes(pconfigiterator_key) = [HOBJECT n_payload]',
        '$config_iterator_valid(S_key_throw, pconfigiterator_key, "key")',
        cell('S_key_throw', 'saved', 'n_saved_cell'),
        'S_key_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        '$throwable_live(S_key_throw, n_saved)',
        cell('S_key_throw', 'iteratorWatch', 'n_iterator_watch_cell'),
        'S_key_throw.STORE[n_iterator_watch_cell] = DEFINED (POBJECT n_iterator_watch)',
        cell('S_key_throw', 'payloadWatch', 'n_payload_watch_cell'),
        'S_key_throw.STORE[n_payload_watch_cell] = DEFINED (POBJECT n_payload_watch)',
        cell('S_key_throw', 'result', 'n_result_cell'),
        'S_key_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$weakref_get(S_key_throw, n_iterator_watch) = POBJECT n_iterator',
        '$weakref_get(S_key_throw, n_payload_watch) = POBJECT n_payload',
        owners('S_key_throw', 'HOBJECT n_iterator', 2),
        owners('S_key_throw', 'HOBJECT n_payload', 1),
    ] + public('S_key_throw') + [
        # THROW_SEARCH removed the original task; a copied CONFIG_INVOKE root
        # must keep the prefix while the last INPUT owner is reconstructed.
        'S_unwound = S_key_throw[.TODO = (THROW_SEARCH n_saved) :: ptask_key_tail*]',
        'S_hold = $config_iterator_discard_scope(S_unwound, pconfigiterator_key)',
        owners('S_hold', 'HOBJECT n_iterator', 0),
        owners('S_hold', 'HOBJECT n_payload', 1),
        '~$config_iterator_quiet_input(S_hold, pconfigiterator_key)',
        '$config_iterator_effectful_input(S_hold, pconfigiterator_key)',
        '$config_iterator_discard_allowed(S_unwound, pconfigiterator_key)',
        'pconfigiterator_empty = pconfigiterator_key[.ITEMS = eps]',
        '~$config_iterator_effectful_input(S_hold, pconfigiterator_empty)',
        '~$config_iterator_discard_allowed(S_unwound, pconfigiterator_empty)',
        'S_dead = S_hold[.ALLOCATIONS = $destruction_node_delete(S_hold.ALLOCATIONS, HOBJECT n_payload)]',
        '~$config_iterator_effectful_input(S_dead, pconfigiterator_key)',
    ] + seek('S_key_throw', 971, 'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_saved) :: (CONFIG_ITERATOR pconfigiterator_input "input-release") :: ptask_input_tail*',
        'pconfigiterator_input = pconfigiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$config_iterator_valid(S_input, pconfigiterator_input, "input-release")',
        '$config_iterator_argument_nodes(pconfigiterator_input) = [HOBJECT n_payload]',
        '$config_iterator_effectful_input(S_input, pconfigiterator_input)',
        '~$config_iterator_quiet_input(S_input, pconfigiterator_input)',
        owners('S_input', 'HOBJECT n_iterator', 1),
        owners('S_input', 'HOBJECT n_payload', 1),
        '$weakref_get(S_input, n_iterator_watch) = POBJECT n_iterator',
        '$weakref_get(S_input, n_payload_watch) = POBJECT n_payload',
        'PhpStep: S_input ~> S_release',
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release*',
        'S_release.DESTRUCTION.RELEASES = pdestructionrelease :: prelease_tail*',
    ] + public('S_input') + seek('S_release', 972, 'S_input_dtor') + destructor('S_input_dtor', 'input', 'n_iterator') + [
        '$weakref_get(S_input_dtor, n_payload_watch) = POBJECT n_payload',
        owners('S_input_dtor', 'HOBJECT n_payload', 1),
    ] + public('S_input_dtor') + seek('S_input_dtor', 973, 'S_payload_dtor') + destructor('S_payload_dtor', 'payload', 'n_payload') + [
        '$weakref_get(S_payload_dtor, n_iterator_watch) = PNULL',
        '~((HOBJECT n_iterator) <- S_payload_dtor.ALLOCATIONS)',
    ] + public('S_payload_dtor') + seek('S_payload_dtor', 974, 'S_catch') + [
        cell('S_catch', 'e', 'n_e_cell'),
        'S_catch.STORE[n_e_cell] = DEFINED (POBJECT n_saved)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$throwable_field(S_catch, n_saved, "previous") = PNULL',
        '$weakref_get(S_catch, n_iterator_watch) = PNULL',
        '$weakref_get(S_catch, n_payload_watch) = PNULL',
        '~((HOBJECT n_iterator) <- S_catch.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_catch.ALLOCATIONS)',
    ] + public('S_catch')
    return checks + finish('S_catch', stdout, ['HOBJECT n_iterator', 'HOBJECT n_payload'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
