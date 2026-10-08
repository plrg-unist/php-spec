#!/usr/bin/env python3
"""Reached identical caches authenticate each Generator object separately."""
import os

import generator_force_close_protocol as driver
import yield_key_warning_protocol as key
import yield_key_identity_review as source

CASES = {
    'nested-key-cache-identity': source.CASES['nested-key-warnings-have-distinct-generator-cache-owners'],
}
PREFIX = key.PREFIX + r'''
dec $key_identity_phase(pstate) : bool
def $key_identity_phase(S) = true
  -- if S.TODO = (GENERATOR_YIELD_KEY n porigin z) :: ptask*
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $trace_slot(S,psymboltable.ENV,$ptascii("other")) = POBJECT n
def $key_identity_phase(S) = false -- otherwise
dec $key_identity_seek(pstate,nat) : pstate
def $key_identity_seek(S,n) = S -- if $key_identity_phase(S)
def $key_identity_seek(S,n) = S
  -- if ~$key_identity_phase(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $key_identity_seek(S,0) = S -- if ~$key_identity_phase(S)
def $key_identity_seek(S,n) = $key_identity_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$key_identity_phase(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $key_identity_without_outer(pframe*,nat) : pframe*
def $key_identity_without_outer(eps,n) = eps
def $key_identity_without_outer(pframe :: pframe*,n) = pframe[.TODO = ptask*] :: pframe*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = GENERATOR_YIELD_KEY n porigin z
def $key_identity_without_outer(pframe :: pframe*,n) = pframe :: $key_identity_without_outer(pframe*,n) -- otherwise
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              'S_both_found = $key_identity_seek(S_initial,4096)',
              r'S_both_found.COMPLETION = NORMAL \/ S_both_found.COMPLETION = BUDGET',
              'S_both = S_both_found[.COMPLETION = NORMAL]',
              '$key_identity_phase(S_both)'] + key.valid('S_both')
    checks += r'''
S_both.TODO = (GENERATOR_YIELD_KEY n_inner porigin z) :: ptask*
S_both.GLOBALTABLE = (psymboltable)
$trace_slot(S_both,psymboltable.ENV,$ptascii("other")) = POBJECT n_inner
$trace_slot(S_both,psymboltable.ENV,$ptascii("generator")) = POBJECT n_outer
n_outer =/= n_inner
S_both.OBJECTS[n_outer] = GENERATOR pgenerator_outer
S_both.OBJECTS[n_inner] = GENERATOR pgenerator_inner
pgenerator_outer = pgenerator_inner
pgenerator_inner.PHASE = GENERATOR_RUNNING
pgenerator_inner.VALUE = (PINT 11) /\ pgenerator_inner.KEY = eps
$generator_yield_key_node_valid(S_both,n_outer)
$generator_yield_key_node_valid(S_both,n_inner)
$generator_id_count($generator_yield_key_tasks_ids(S_both.TODO) ++ $generator_yield_key_frames_ids(S_both.FRAMES),n_outer) = 1
$generator_id_count($generator_yield_key_tasks_ids(S_both.TODO) ++ $generator_yield_key_frames_ids(S_both.FRAMES),n_inner) = 1
S_lost = S_both[.FRAMES = $key_identity_without_outer(S_both.FRAMES,n_outer)]
S_lost.FRAMES =/= S_both.FRAMES
$heap_graph(S_lost) = $heap_graph(S_both)
$heap_valid($heap_graph(S_lost))
$generator_id_count($generator_yield_key_tasks_ids(S_lost.TODO) ++ $generator_yield_key_frames_ids(S_lost.FRAMES),n_outer) = 0
$generator_id_count($generator_yield_key_tasks_ids(S_lost.TODO) ++ $generator_yield_key_frames_ids(S_lost.FRAMES),n_inner) = 1
$generator_yield_key_cache_pending(S_lost,pgenerator_outer)
~$generator_yield_key_node_valid(S_lost,n_outer)
$generator_yield_key_node_valid(S_lost,n_inner)
~$call_descriptors_valid(S_lost)
$call_entry_check(S_lost).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
S_zero = $drive_steps(S_both,0)
S_zero = S_both[.COMPLETION = BUDGET]
S_resumed = $drive(S_zero[.COMPLETION = NORMAL],4096)
S_direct = $drive(S_both,4096)
S_resumed = S_direct
S_resumed.COMPLETION = NORMAL /\ S_resumed.TODO = eps /\ S_resumed.FRAMES = eps
'''.strip().splitlines()
    checks += ['$yield_key_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += key.valid('S_resumed')
    return checks


def main():
    driver.CASES = CASES
    driver.source.WATCHED = key.WATCHED + [
        'tests/semantics/yield_key_identity_review.py',
        'tests/semantics/yield_key_identity_protocol.py',
    ]
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
