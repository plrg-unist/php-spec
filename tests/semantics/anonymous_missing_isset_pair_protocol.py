#!/usr/bin/env python3
"""Reach missing-property isset preparation, bool delivery and saved throw."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_isset_pair_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'booleans': 'anonymous-missing-isset-pair-booleans',
    'throw': 'named-missing-isset-pair-saved-throw',
}
PREFIX = r'''
syntax pamipstage = AMIP_PREP ptbytes | AMIP_PLAN ptbytes | AMIP_RESULT ptbytes | AMIP_THROW
dec $amip_output(pevent*) : ptbytes
def $amip_output(eps) = eps
def $amip_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $amip_output(pevent*)
dec $amip_valid(pstate) : bool
def $amip_valid(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $amip_stage(pstate,pamipstage) : bool
def $amip_stage(S,AMIP_PREP ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail*
  -- if $base64(text_name) = ptbytes
def $amip_stage(S,AMIP_PLAN ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ISSET_RESULT false z) :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
def $amip_stage(S,AMIP_RESULT ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if ppropertyisset.NAME = ptbytes
def $amip_stage(S,AMIP_THROW) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
def $amip_stage(S,pamipstage) = false -- otherwise
dec $amip_seek(pstate,pamipstage,nat) : pstate
def $amip_seek(S,pamipstage,n) = S -- if $amip_stage(S,pamipstage) \/ n = 0
def $amip_seek(S,pamipstage,n) = $amip_seek($drive_steps(S[.COMPLETION = NORMAL],1),pamipstage,$nabs($(n - 1)))
  -- if ~$amip_stage(S,pamipstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amip_seek(S,pamipstage,n) = $amip_seek($drive_steps(S,1),pamipstage,$nabs($(n - 1)))
  -- if ~$amip_stage(S,pamipstage) /\ $(n > 0)
  -- if $throwable_pending(S.COMPLETION)
def $amip_seek(S,pamipstage,n) = S -- otherwise
'''


def seek(target, source, stage):
    return [target + '_raw = $amip_seek(' + source + ',' + stage + ',2048)',
            target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
            target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
            '$amip_stage(' + target + ',' + stage + ')']


def finish(source, expected):
    return [
        'S_zero = $drive_steps(' + source + ',0)',
        'S_zero = ' + source + '[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(' + source + ',4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps /\\ S_full.CURRENT = eps /\\ S_full.FRAMES = eps /\\ S_full.HELD = eps',
        '$amip_output(S_full.EVENTS) = ' + expected,
        '$amip_valid(S_full)',
    ]


def booleans():
    checks = []
    previous = 'S_initial'
    for name, boolean, before in [('no', 'false', ''), ('yes', 'true', 'I:no;SHORT;')]:
        state = 'S_' + name
        receipt = 'ppropertyisset_' + name
        line = 'z_' + name
        origin = 'porigin_' + name
        tail = 'ptask_' + name + '_tail*'
        checks += seek(state, previous, 'AMIP_PREP ($ptascii("' + name + '"))') + [
            state + '.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_' + name + ') metadata_' + name + ') ' + line + ') :: (ORIGIN_RETURN (' + origin + ')) :: (ISSET_RESULT false ' + line + ') :: ' + tail,
            state + '.ORIGIN = (' + origin + ') /\\ ' + state + '.BASE = BASE_VALUE (KNOWN PNULL)',
            '$quiet_operand(' + state + ',' + state + '.RESULT).RESULT = KNOWN (POBJECT n_' + name + ')',
            '$property_isset_method(' + state + ',n_' + name + ') = (pmethoddesc_' + name + ')',
            state + '.OBJECTS[n_' + name + '] = INSTANCE porigin_class_' + name,
            receipt + ' = {SITE ' + origin + ', NAME $ptascii("' + name + '"), LINE ' + line + ', OBJECT n_' + name + ', CLASS porigin_class_' + name + ', METHOD pmethoddesc_' + name + '.FUNCTION.ORIGIN, PROPERTY eps}',
            '$property_isset_bool_pair(' + state + ',' + receipt + ')',
            '$property_isset_valid(' + state + ',' + receipt + ') /\\ $property_isset_capture(' + state + ',' + receipt + ')',
            '~$property_isset_untyped(' + state + ',' + receipt + ')',
            '$property_empty_prepare(' + state + ')',
            '~$property_get_pending(' + state + ') /\\ $property_get_plan(' + state + ') = eps',
            'S_wrong_' + name + ' = ' + state + '[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_' + name + ') metadata_' + name + ') ' + line + ') :: (ORIGIN_RETURN (' + origin + ')) :: (ISSET_RESULT true ' + line + ') :: ' + tail + ']',
            '~$property_empty_prepare(S_wrong_' + name + ')',
            '~$property_empty_prepare(' + state + '[.SOURCES = eps])',
            '$amip_output(' + state + '.EVENTS) = $ptascii("' + before + '")',
            '$amip_valid(' + state + ')',
        ] + seek(state + '_plan', state, 'AMIP_PLAN ($ptascii("' + name + '"))') + [
            '$property_isset_plan(' + state + '_plan) = (' + receipt + ')',
            '$property_empty_plan(' + state + '_plan) = eps',
            '$property_isset_plan(' + state + '_plan[.TODO = (ISSET_RESULT true ' + line + ') :: ' + tail + ']) = eps',
        ] + seek(state + '_result', state + '_plan', 'AMIP_RESULT ($ptascii("' + name + '"))') + [
            state + '_result.TODO = (PROPERTY_ISSET_RESULT ' + receipt + ') :: ' + tail,
            state + '_result.RESULT = KNOWN (PBOOL ' + boolean + ')',
            '$property_isset_valid(' + state + '_result,' + receipt + ')',
            '~$property_empty_get_active(' + state + '_result,n_' + name + ',' + receipt + '.NAME)',
            '$heap_owners($heap_graph(' + state + '_result),HOBJECT n_' + name + ') = 2',
            '$amip_output(' + state + '_result.EVENTS) = $ptascii("' + before + 'I:' + name + ';")',
            'PhpStep: ' + state + '_result ~> ' + state + '_step',
            state + '_step = ' + state + '_result[.TODO = ' + tail + '][.RESULT = KNOWN (PBOOL ' + boolean + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$heap_owners($heap_graph(' + state + '_step),HOBJECT n_' + name + ') = 1',
        ]
        previous = state + '_result'
    expected = '$base64(' + json.dumps(ROWS[CASES['booleans']]['stdout_template_base64']) + ')'
    return checks + finish('S_no_result', expected)


def throwing():
    expected = '$base64(' + json.dumps(ROWS[CASES['throw']]['stdout_template_base64']) + ')'
    return seek('S', 'S_initial', 'AMIP_THROW') + [
        'S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*',
        'ppropertyisset.PROPERTY = eps /\\ ppropertyisset.NAME = $ptascii("missing")',
        'n_receiver = ppropertyisset.OBJECT',
        '$property_isset_bool_pair(S,ppropertyisset) /\\ $property_isset_valid(S,ppropertyisset)',
        '$property_isset_throw_tail(S,ppropertyisset) /\\ $call_task_valid(S,PROPERTY_ISSET_RESULT ppropertyisset)',
        '~$property_isset_capture(S,ppropertyisset)',
        '~$property_empty_get_active(S,n_receiver,ppropertyisset.NAME)',
        '~$property_get_guard_tasks(S.TODO,n_receiver,ppropertyisset.NAME)',
        '$lookup(S.ENV,$ptascii("o")) = (n_o)',
        'S.STORE[n_o] = DEFINED PNULL',
        '$lookup(S.ENV,$ptascii("saved")) = (n_saved)',
        'S.STORE[n_saved] = DEFINED (POBJECT n_error)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED (PINT 42)',
        '$throwable_live(S,n_error)',
        '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        '$amip_output(S.EVENTS) = $ptascii("I:missing;")',
        '$amip_valid(S)',
        'PhpStep: S ~> S_discard',
        'S_discard.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_discard.EVENTS = S.EVENTS /\\ S_discard.STORE = S.STORE',
        '$heap_owners($heap_graph(S_discard),HOBJECT n_receiver) = 0',
    ] + finish('S', expected) + [
        '~((HOBJECT n_receiver) <- S_full.ALLOCATIONS)',
        'S_full.STORE[n_result] = DEFINED (PINT 42) /\\ S_full.STORE[n_o] = DEFINED PNULL',
        '$lookup(S_full.ENV,$ptascii("caught")) = (n_caught)',
        'S_full.STORE[n_caught] = DEFINED (POBJECT n_error)',
    ]


def render(case, fixture, filename):
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']
    checks += booleans() if case['id'] == 'booleans' else throwing()
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    sources = {}
    for name in args.case or CASES:
        row = ROWS[CASES[name]]
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
        sources[name] = {'id': name, 'source': row['source']}
    protocol.run(sources, (Path(__file__), CATALOGUE), fixture_renderer=render)
