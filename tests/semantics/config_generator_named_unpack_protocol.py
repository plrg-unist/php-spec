#!/usr/bin/env python3
"""Reached named Generator send, history and one-step resumption checks."""
import argparse
import json
import os
from pathlib import Path
import sys

import config_generator_unpack_protocol as previous
import config_generator_named_unpack_sources as sources


driver = previous.driver
text = previous.text
PREFIX = previous.PREFIX + r"""
dec $test_named_error_front(pstate) : bool
def $test_named_error_front(S) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*
  -- if pconfiggenerator.ITEMS = [ENTRY (KSTRING preqbytes) (DIRECT pvalue)]
  -- if preqbytes = $ptascii("option")
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.KEY = (pvalue_key)
  -- if $string_bytes(pvalue_key) = ($ptascii("option"))
def $test_named_error_front(S) = false -- otherwise
dec $test_named_error_seek(pstate, nat) : pstate
def $test_named_error_seek(S, 0) = S
def $test_named_error_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_named_error_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_named_error_seek(S, n) = $test_named_error_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_named_error_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    if name == 'duplicate-named-stops-before-next':
        message = 'Named parameter $option overwrites previous argument'
        return [
            'S_initial = $php_run(' + program + ',0,' + json.dumps(previous.b64(os.fsencode(path))) + ')',
            'S_initial.COMPLETION = BUDGET',
            'S_found = $test_named_error_seek(S_initial,3000)',
            'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
            'S_front = S_found[.COMPLETION = NORMAL]',
            '$test_named_error_front(S_front)',
            'S_front.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*',
            'pconfiggenerator.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_option)]',
            'S_front.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator',
            'pgenerator.KEY = (pvalue_key)',
            '$config_generator_key(S_front,pvalue_key) = (KSTRING ' + text('option') + ')',
            '$intrinsic_argument(S_front,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
            'S_front.ORIGIN = (porigin_argument)',
            '$config_generator_send_allowed(S_front,pconfiggenerator)',
            '$config_generator_history(S_front,pconfiggenerator)',
            '$test_outputs(S_front.EVENTS) = ' + text('B|Y0|Y1|'),
            *previous.common.public('S_front'),
            'S_thrown = $test_config_generator_step(S_front)',
            'S_thrown = S_front[.COMPLETION = THROWN "Error" ' + text(message) + ' z_argument]',
            'S_thrown.TODO = S_front.TODO',
            'S_thrown.EVENTS = S_front.EVENTS',
            'S_thrown.OBJECTS = S_front.OBJECTS',
            'S_thrown.STORE = S_front.STORE',
            'S_pause = $drive_steps(S_front,0)',
            'S_pause = S_front[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S_front,1)',
            'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
        ]
    assert name == 'named-option-then-value'
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(previous.b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_config_generator_seek(S_initial,1,3000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S_first = S_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*',
        'pconfiggenerator.ITEMS = eps',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        'S_first.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator',
        'pgenerator.PHASE = GENERATOR_PAUSED',
        'pgenerator.VALUE = (pvalue_option)',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        'pgenerator.KEY = (pvalue_key)',
        '$string_bytes(pvalue_key) = (' + text('option') + ')',
        '$config_generator_key(S_first,pvalue_key) = (KSTRING ' + text('option') + ')',
        '$config_generator_send_allowed(S_first,pconfiggenerator)',
        '$config_generator_history(S_first,pconfiggenerator)',
        '$test_outputs(S_first.EVENTS) = ' + text('B|Y0|'),
        *previous.common.public('S_first'),
        'S_sent = $test_config_generator_step(S_first)',
        'S_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_sent "next") :: ptask_tail*',
        'pconfiggenerator_sent = pconfiggenerator[.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_option)]]',
        'S_sent.EVENTS = S_first.EVENTS',
        'S_sent.OBJECTS = S_first.OBJECTS',
        '$config_generator_history(S_sent,pconfiggenerator_sent)',
        *previous.common.public('S_sent'),
        '$config_generator_key(S_first,PSTRING ' + text('0') + ') = (KINT 0)',
        '$config_generator_key(S_first,PBOOL true) = eps',
        '~$config_generator_history(S_first,pconfiggenerator[.ITEMS = [ENTRY (KSTRING ' + text('0') + ') (DIRECT pvalue_option)]])',
        '~$config_generator_history(S_first,pconfiggenerator[.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_option),ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_option)]])',
        '~$config_generator_history(S_first,pconfiggenerator[.CALL = pconfiggenerator.CALL[.KIND = INTRINSIC_INI_GET]])',
        '~$config_generator_history(S_first,pconfiggenerator[.CALL = pconfiggenerator.CALL[.SITE = PORIGIN 999 eps]])',
        '~$config_generator_history(S_first[.CODE = eps],pconfiggenerator)',
        'S_pause = $drive_steps(S_first,0)',
        'S_pause = S_first[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_first,1)',
        'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources.family.CASES = {name: sources.family.CASES[name] for name in
                            ('named-option-then-value', 'duplicate-named-stops-before-next')}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output)]
    driver.main()


if __name__ == '__main__':
    main()
