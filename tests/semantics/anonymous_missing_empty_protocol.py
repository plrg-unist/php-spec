#!/usr/bin/env python3
"""Reach missing-property empty dispatch, short circuit and source-mode guards."""
import argparse
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_empty_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'false': 'anonymous-missing-empty-false-skips-get',
    'true': 'anonymous-missing-empty-true-get-nonempty',
    'isset_only': 'anonymous-missing-empty-isset-only-booleans',
}
FLAGS_SOURCE = '''<?php
$o = new class {
    public function __isset(string $name): bool { return true; }
};
$i = isset($o->missing);
$e = empty($o->missing);
echo ($i && $e) ? "OK;" : "BAD;";
'''
PREFIX = r'''
syntax pamestage = AME_PAIR_PLAN | AME_PAIR_RESULT bool | AME_ISSET_PLAN bool | AME_ISSET_RESULT
dec $ame_output(pevent*) : ptbytes
def $ame_output(eps) = eps
def $ame_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ame_output(pevent*)
dec $ame_stage(pstate,pamestage) : bool
def $ame_stage(S,AME_PAIR_PLAN) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $property_empty_plan(S[.COMPLETION = NORMAL]) =/= eps
def $ame_stage(S,AME_PAIR_RESULT b) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty b) :: ptask_tail*
def $ame_stage(S,AME_ISSET_PLAN b) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ISSET_RESULT b z) :: ptask_tail*
  -- if $property_isset_plan(S[.COMPLETION = NORMAL]) =/= eps
def $ame_stage(S,AME_ISSET_RESULT) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
def $ame_stage(S,pamestage) = false -- otherwise
dec $ame_seek(pstate,pamestage,nat) : pstate
def $ame_seek(S,pamestage,n) = S -- if $ame_stage(S,pamestage) \/ n = 0
def $ame_seek(S,pamestage,n) = $ame_seek($drive_steps(S[.COMPLETION = NORMAL],1),pamestage,$nabs($(n - 1)))
  -- if ~$ame_stage(S,pamestage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ame_seek(S,pamestage,n) = S -- otherwise
dec $ame_after(pstate,pstate) : pstate
def $ame_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ame_valid(pstate) : bool
def $ame_valid(S) = ($call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''


def seek(target, source, stage):
    return [target + '_raw = $ame_seek(' + source + ',' + stage + ',2048)',
            target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
            target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
            '$ame_stage(' + target + ',' + stage + ')']


def finish(source, expected):
    return [
        'S_zero = $drive_steps(' + source + ',0)',
        'S_zero = ' + source + '[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(' + source + ',4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps',
        '$ame_output(S_full.EVENTS) = ' + expected,
        '$ame_valid(S_full)',
    ]


def paired(name):
    checks = seek('S', 'S_initial', 'AME_PAIR_PLAN') + [
        'S.TODO = (ISSET_RESULT true z) :: ptask_tail*',
        'S.BASE = BASE_PROPERTY (POBJECT n_receiver) ptbytes_name',
        'S.RESULT = KNOWN PNULL',
        'S.ORIGIN = (porigin_site)',
        '$property_empty_plan(S) = (ppropertyempty)',
        'ppropertyempty.PROPERTY = eps /\\ ppropertyempty.OBJECT = n_receiver',
        'ppropertyempty.NAME = ptbytes_name /\\ ppropertyempty.SITE = porigin_site /\\ ppropertyempty.LINE = z',
        '$property_empty_valid(S,ppropertyempty) /\\ $property_empty_capture(S,ppropertyempty)',
        '$property_empty_storage_capture(S,ppropertyempty)',
        '$property_effective_desc(S,n_receiver,ptbytes_name) = eps',
        '$property_empty_method(S,n_receiver,false) = (pmethoddesc_isset)',
        '$property_empty_method(S,n_receiver,true) = (pmethoddesc_get)',
        '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
        '$property_empty_get_source(S,pmethoddesc_get)',
        '$property_empty_function(S,ppropertyempty,false) = (pmethoddesc_isset.FUNCTION)',
        '$property_empty_function(S,ppropertyempty,true) = (pmethoddesc_get.FUNCTION)',
        '~$property_empty_guard(S,n_receiver,ptbytes_name)',
        '$property_isset_plan(S) = eps',
        '$ame_valid(S)',
        '~$property_empty_valid(S,ppropertyempty[.PROPERTY = (porigin_site)])',
        '~$property_empty_valid(S,ppropertyempty[.NAME = $ptascii("forged")])',
        '~$property_empty_valid(S,ppropertyempty[.GET = ppropertyempty.ISSET])',
        '~$property_empty_valid(S,ppropertyempty[.ISSET = ppropertyempty.GET])',
        '~$property_empty_valid(S[.SOURCES = eps],ppropertyempty)',
        'PhpStep: S ~> S_call_raw',
        'S_call = $ame_after(S,S_call_raw)',
        'S_call.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty false) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) z) :: (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*',
        '$property_empty_pending_call(S_call,ppropertyempty,false)',
        '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty false) = [HOBJECT n_receiver]',
        '$target_nodes(PROPERTY_EMPTY_TARGET ppropertyempty false) = eps',
        '$property_empty_guard(S_call,n_receiver,ptbytes_name)',
        '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
        '$ame_valid(S_call)',
    ] + seek('S_result', 'S_call', 'AME_PAIR_RESULT false') + [
        'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*',
        'S_result.RESULT = KNOWN (PBOOL ' + ('false' if name == 'false' else 'true') + ')',
        '$property_empty_guard(S_result,n_receiver,ptbytes_name)',
        '~$property_empty_get_active(S_result,n_receiver,ptbytes_name)',
        '$ame_output(S_result.EVENTS) = $ptascii("ISSET:missing;")',
        '$ame_valid(S_result)',
        'PhpStep: S_result ~> S_step',
    ]
    if name == 'false':
        checks += [
            'S_step = S_result[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '~$property_empty_guard(S_step,n_receiver,ptbytes_name)',
            '$heap_owners($heap_graph(S_step),HOBJECT n_receiver) = 1',
        ]
    else:
        checks += [
            'S_step.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty true) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) z) :: (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*',
            'S_step.RESULT = KNOWN PNULL /\\ S_step.BASE = BASE_VALUE (KNOWN PNULL)',
            '$property_empty_pending_call(S_step,ppropertyempty,true)',
            '$property_empty_guard(S_step,n_receiver,ptbytes_name)',
            '$heap_owners($heap_graph(S_step),HOBJECT n_receiver) = 2',
        ] + seek('S_get_result', 'S_step', 'AME_PAIR_RESULT true') + [
            'S_get_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*',
            'S_get_result.RESULT = KNOWN (PINT 7)',
            '$ame_output(S_get_result.EVENTS) = $ptascii("ISSET:missing;GET:missing;")',
            '$property_empty_guard(S_get_result,n_receiver,ptbytes_name)',
            '~$property_empty_get_active(S_get_result,n_receiver,ptbytes_name)',
            '$ame_valid(S_get_result)',
            'PhpStep: S_get_result ~> S_get_step',
            'S_get_step = S_get_result[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '~$property_empty_guard(S_get_step,n_receiver,ptbytes_name)',
            '$heap_owners($heap_graph(S_get_step),HOBJECT n_receiver) = 1',
        ]
    return checks + finish('S_result', '$base64(' + json.dumps(ROWS[CASES[name]]['stdout_template_base64']) + ')')


def isset_only():
    checks = []
    previous = 'S_initial'
    for suffix, member, result in (('no', 'no', 'false'), ('yes', 'yes', 'true')):
        state = 'S_' + suffix
        receipt = 'ppropertyisset_' + suffix
        checks += seek(state, previous, 'AME_ISSET_PLAN true') + [
            state + '.TODO = (ISSET_RESULT true z_' + suffix + ') :: ptask_' + suffix + '_tail*',
            '$property_isset_plan(' + state + ') = (' + receipt + ')',
            receipt + '.PROPERTY = eps /\\ ' + receipt + '.NAME = $ptascii("' + member + '")',
            '$property_isset_empty(' + state + ',' + receipt + ')',
            '$property_empty_plan(' + state + ') = eps',
            '$property_get_method(' + state + ',' + receipt + '.OBJECT) = eps',
            '$property_isset_capture(' + state + ',' + receipt + ')',
            'S_wrong_' + suffix + ' = ' + state + '[.TODO = (ISSET_RESULT false z_' + suffix + ') :: ptask_' + suffix + '_tail*]',
            '$property_isset_plan(S_wrong_' + suffix + ') = eps',
            '$ame_valid(' + state + ')',
        ] + seek(state + '_result', state, 'AME_ISSET_RESULT') + [
            state + '_result.TODO = (PROPERTY_ISSET_RESULT ' + receipt + ') :: ptask_' + suffix + '_tail*',
            state + '_result.RESULT = KNOWN (PBOOL ' + result + ')',
            'PhpStep: ' + state + '_result ~> ' + state + '_step',
            state + '_step = ' + state + '_result[.TODO = ptask_' + suffix + '_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        ]
        previous = state + '_result'
    expected = '$base64(' + json.dumps(ROWS[CASES['isset_only']]['stdout_template_base64']) + ')'
    return checks + finish('S_no_result', expected)


def flags():
    return seek('S_isset', 'S_initial', 'AME_ISSET_PLAN false') + [
        'S_isset.TODO = (ISSET_RESULT false z_isset) :: ptask_isset_tail*',
        '$property_isset_plan(S_isset) = (ppropertyisset_isset)',
        'ppropertyisset_isset.PROPERTY = eps',
        '~$property_isset_empty(S_isset,ppropertyisset_isset)',
        'S_wrong_isset = S_isset[.TODO = (ISSET_RESULT true z_isset) :: ptask_isset_tail*]',
        '$property_isset_plan(S_wrong_isset) = eps',
        '$ame_valid(S_isset)',
    ] + seek('S_empty', 'S_isset', 'AME_ISSET_PLAN true') + [
        'S_empty.TODO = (ISSET_RESULT true z_empty) :: ptask_empty_tail*',
        '$property_isset_plan(S_empty) = (ppropertyisset_empty)',
        'ppropertyisset_empty.PROPERTY = eps',
        'ppropertyisset_empty.SITE =/= ppropertyisset_isset.SITE',
        '$property_isset_empty(S_empty,ppropertyisset_empty)',
        'S_wrong_empty = S_empty[.TODO = (ISSET_RESULT false z_empty) :: ptask_empty_tail*]',
        '$property_isset_plan(S_wrong_empty) = eps',
        '$ame_valid(S_empty)',
    ] + finish('S_empty', '$ptascii("OK;")')


def render(case, fixture, filename):
    name = case['id']
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']
    checks += paired(name) if name in ('false', 'true') else isset_only() if name == 'isset_only' else flags()
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted([*CASES, 'flags']))
    args = parser.parse_args()
    sources = {name: {'id': name, 'source': ROWS[row]['source']} for name, row in CASES.items()}
    sources['flags'] = {'id': 'flags', 'source': FLAGS_SOURCE}
    protocol.run({name: sources[name] for name in args.case or sources},
                 (Path(__file__), CATALOGUE), fixture_renderer=render)
