#!/usr/bin/env python3
"""Reach undeclared-property ?? decisions and the separate ??= refusal."""
import argparse
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_coalesce_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {name: 'anonymous-missing-coalesce-' + suffix for name, suffix in (
    ('false', 'false-fallback'), ('zero', 'true-zero-lazy'),
    ('null', 'true-null-fallback'), ('no_get', 'no-get-booleans'))}
ASSIGN_SOURCE = '''<?php
function missing_rhs(): int { return 9; }
$o = new class {
    public function __isset(string $name): bool { return true; }
    public function __get($name) { return 0; }
};
$o->missing ??= missing_rhs();
'''
PREFIX = r'''
syntax pamcstage = AMC_PREP | AMC_ENTER bool | AMC_RESULT bool | AMC_ASSIGN
dec $amc_output(pevent*) : ptbytes
def $amc_output(eps) = eps
def $amc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $amc_output(pevent*)
dec $amc_stage(pstate,pamcstage) : bool
def $amc_stage(S,AMC_PREP) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $property_coalesce_plan(S[.COMPLETION = NORMAL]) =/= eps
def $amc_stage(S,AMC_ENTER b) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce b
def $amc_stage(S,AMC_RESULT b) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce b) :: ptask_tail*
def $amc_stage(S,AMC_ASSIGN) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $property_magic_coalesce_assign_pending(S[.COMPLETION = NORMAL])
def $amc_stage(S,pamcstage) = false -- otherwise
dec $amc_seek(pstate,pamcstage,nat) : pstate
def $amc_seek(S,pamcstage,n) = S -- if $amc_stage(S,pamcstage) \/ n = 0
def $amc_seek(S,pamcstage,n) = $amc_seek($drive_steps(S[.COMPLETION = NORMAL],1),pamcstage,$nabs($(n - 1)))
  -- if ~$amc_stage(S,pamcstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amc_seek(S,pamcstage,n) = S -- otherwise
dec $amc_after(pstate,pstate) : pstate
def $amc_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $amc_valid(pstate) : bool
def $amc_valid(S) = ($call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''


def seek(target, source, stage):
    return [target + '_raw = $amc_seek(' + source + ',' + stage + ',2048)',
            target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
            target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
            '$amc_stage(' + target + ',' + stage + ')']


def finish(source, name):
    return [
        'S_zero = $drive_steps(' + source + ',0)',
        'S_zero = ' + source + '[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(' + source + ',4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps',
        '$amc_output(S_full.EVENTS) = $base64(' + json.dumps(ROWS[CASES[name]]['stdout_template_base64']) + ')',
        '$amc_valid(S_full)',
    ]


def normal(name):
    no_get = name == 'no_get'
    checks = seek('S', 'S_initial', 'AMC_PREP') + [
        '$property_coalesce_plan(S) = (ppropertycoalesce)',
        'ppropertycoalesce.PROPERTY = eps',
        'n_receiver = ppropertycoalesce.OBJECT',
        '$property_effective_desc(S,n_receiver,ppropertycoalesce.NAME) = eps',
        '$property_coalesce_prepare(S) /\\ $property_empty_prepare(S)',
        'S_marker = S[.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ppropertycoalesce.TAIL]',
        '$property_coalesce_descriptor(S_marker,ppropertycoalesce)',
        '$property_coalesce_valid(S_marker,ppropertycoalesce)',
        '$property_coalesce_capture(S_marker,ppropertycoalesce)',
        '$property_coalesce_storage_capture(S_marker,ppropertycoalesce)',
        '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
        '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
        'ppropertycoalesce.SITE = PORIGIN n_unit pcpath_site',
        '~$property_coalesce_descriptor(S_marker,ppropertycoalesce[.PROPERTY = (ppropertycoalesce.SITE)])',
        '~$property_coalesce_descriptor(S_marker,ppropertycoalesce[.NAME = $ptascii("forged")])',
        '~$property_coalesce_descriptor(S_marker,ppropertycoalesce[.LINE = $(ppropertycoalesce.LINE + 1)])',
        '~$property_coalesce_descriptor(S_marker,ppropertycoalesce[.TAIL = eps])',
        '~$property_coalesce_descriptor(S_marker[.SOURCES = eps],ppropertycoalesce)',
        '$amc_valid(S)',
        'PhpStep: S ~> S_call_raw',
        'S_call = $amc_after(S,S_call_raw)',
        '$property_coalesce_pending_call(S_call,ppropertycoalesce,false)',
        '$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce false) = [HOBJECT n_receiver]',
        '$target_nodes(PROPERTY_COALESCE_TARGET ppropertycoalesce false) = eps',
        '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
        '$amc_valid(S_call)',
    ] + seek('S_enter', 'S_call', 'AMC_ENTER false') + [
        'S_enter.CURRENT = (pcallcontext_isset)',
        '$property_coalesce_context(S_enter,pcallcontext_isset)',
        '$call_receiver_roots(pcallcontext_isset) = eps',
        '$property_isset_guard(S_enter,S_enter.CURRENT,S_enter.FRAMES,n_receiver,ppropertycoalesce.NAME)',
        '~$property_empty_get_active(S_enter,n_receiver,ppropertycoalesce.NAME)',
        '$heap_owners($heap_graph(S_enter),HOBJECT n_receiver) = 2',
        '$amc_valid(S_enter)',
    ] + seek('S_isset', 'S_enter', 'AMC_RESULT false') + [
        'S_isset.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ppropertycoalesce.TAIL',
        'S_isset.RESULT = KNOWN (PBOOL ' + ('false' if name in ('false', 'no_get') else 'true') + ')',
        '$property_coalesce_valid(S_isset,ppropertycoalesce)',
        '~$property_isset_guard(S_isset,S_isset.CURRENT,S_isset.FRAMES,n_receiver,ppropertycoalesce.NAME)',
        '~$property_empty_get_active(S_isset,n_receiver,ppropertycoalesce.NAME)',
        '$heap_owners($heap_graph(S_isset),HOBJECT n_receiver) = 2',
        '$amc_valid(S_isset)',
    ]
    if name in ('false', 'no_get'):
        checks += [
            'ppropertycoalesce.GET = eps' if no_get else 'ppropertycoalesce.GET =/= eps',
            'PhpStep: S_isset ~> S_delivery_raw',
            'S_delivery_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*',
            'S_delivery_raw.RESULT = KNOWN PNULL /\\ S_delivery_raw.BASE = BASE_VALUE (KNOWN PNULL)',
        ]
    else:
        checks += [
            'ppropertycoalesce.GET = (porigin_get)',
            'PhpStep: S_isset ~> S_get_call_raw',
            'S_get_call = $amc_after(S_isset,S_get_call_raw)',
            '$property_coalesce_pending_call(S_get_call,ppropertycoalesce,true)',
        ] + seek('S_get_enter', 'S_get_call', 'AMC_ENTER true') + [
            'S_get_enter.CURRENT = (pcallcontext_get)',
            '$property_coalesce_context(S_get_enter,pcallcontext_get)',
            '~$property_isset_guard(S_get_enter,S_get_enter.CURRENT,S_get_enter.FRAMES,n_receiver,ppropertycoalesce.NAME)',
            '$property_empty_get_active(S_get_enter,n_receiver,ppropertycoalesce.NAME)',
            '$call_receiver_roots(pcallcontext_get) = eps',
            '$heap_owners($heap_graph(S_get_enter),HOBJECT n_receiver) = 2',
            '$amc_valid(S_get_enter)',
        ] + seek('S_get', 'S_get_enter', 'AMC_RESULT true') + [
            'S_get.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ppropertycoalesce.TAIL',
            'S_get.RESULT = KNOWN ' + ('(PINT 0)' if name == 'zero' else 'PNULL'),
            '~$property_isset_guard(S_get,S_get.CURRENT,S_get.FRAMES,n_receiver,ppropertycoalesce.NAME)',
            '~$property_empty_get_active(S_get,n_receiver,ppropertycoalesce.NAME)',
            '$amc_valid(S_get)',
            'PhpStep: S_get ~> S_delivery_raw',
            'S_delivery_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*',
            'S_delivery_raw.RESULT = S_get.RESULT /\\ S_delivery_raw.BASE = BASE_VALUE (KNOWN PNULL)',
        ]
    checks += [
        'S_delivery = $amc_after(' + ('S_isset' if name in ('false', 'no_get') else 'S_get') + ',S_delivery_raw)',
        '$heap_owners($heap_graph(S_delivery),HOBJECT n_receiver) = 1',
        '$amc_valid(S_delivery)',
    ]
    if no_get:
        checks += seek('S_yes', 'S_delivery', 'AMC_PREP') + [
            '$property_coalesce_plan(S_yes) = (ppropertycoalesce_yes)',
            'ppropertycoalesce_yes.PROPERTY = eps /\\ ppropertycoalesce_yes.GET = eps',
            'ppropertycoalesce_yes.NAME = $ptascii("yes")',
        ] + seek('S_yes_result', 'S_yes', 'AMC_RESULT false') + [
            'S_yes_result.RESULT = KNOWN (PBOOL true)',
            'PhpStep: S_yes_result ~> S_yes_delivery',
            'S_yes_delivery.TODO = (ORIGIN_RETURN (porigin_yes)) :: (COALESCE_RESULT expression_yes z_yes_left z_yes_right) :: ptask_yes_tail*',
            'S_yes_delivery.RESULT = KNOWN PNULL /\\ S_yes_delivery.BASE = BASE_VALUE (KNOWN PNULL)',
        ]
    return checks + finish('S_delivery', name)


def assignment():
    return seek('S', 'S_initial', 'AMC_ASSIGN') + [
        'S.TODO = (COALESCE_ASSIGN_PREP expression_target expression_rhs z) :: ptask_tail*',
        'S.ORIGIN = (porigin_parent)',
        '$property_coalesce_assign_source(S,porigin_parent)',
        '$property_coalesce_assign_base(S,porigin_parent,S.BASE)',
        '$origin_child((porigin_parent),[PCFIELD 0]) = (porigin_site)',
        'S.BASE = BASE_PROPERTY_PENDING pbase poperand z_receiver',
        'S_receiver = $property_pending_resolve(S,pbase,poperand,PPIS,z_receiver,z)',
        'S_receiver.COMPLETION = NORMAL',
        'S_receiver.BASE = BASE_PROPERTY (POBJECT n_receiver) ptbytes_name',
        'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
        '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
        'z_property = $runtime_line(S[.ORIGIN = (porigin_site)],eps,expression_target)',
        'ppropertycoalesce = {SITE porigin_site, NAME ptbytes_name, LINE z_property, OBJECT n_receiver, CLASS porigin_class, ISSET pmethoddesc_isset.FUNCTION.ORIGIN, GET $property_coalesce_get_origin(S,n_receiver), PROPERTY eps, OWNER (|S.FRAMES|), CALLER S.CURRENT, TAIL ((ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent S.BASE (|S.FRAMES|) S.CURRENT) :: ptask_tail*)}',
        'S_marker = S[.ORIGIN = (porigin_site)][.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ppropertycoalesce.TAIL][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$property_coalesce_source(S_marker,ppropertycoalesce)',
        '$property_effective_desc(S,n_receiver,ptbytes_name) = eps',
        '~$property_coalesce_descriptor(S_marker,ppropertycoalesce)',
        '~$property_coalesce_valid(S_marker,ppropertycoalesce)',
        '~$property_coalesce_capture(S_marker,ppropertycoalesce)',
        '$property_coalesce_assign_plan(S) = eps',
        '$amc_valid(S)',
        'PhpStep: S ~> S_refused',
        'S_refused = S[.COMPLETION = UNSUPPORTED "magic coalesce assignment source or methods"]',
    ]


def render(case, fixture, filename):
    name = case['id']
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']
    checks += assignment() if name == 'assignment' else normal(name)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted([*CASES, 'assignment']))
    args = parser.parse_args()
    sources = {name: {'id': name, 'source': ROWS[row]['source']} for name, row in CASES.items()}
    sources['assignment'] = {'id': 'assignment', 'source': ASSIGN_SOURCE}
    protocol.run({name: sources[name] for name in args.case or sources},
                 (Path(__file__), CATALOGUE), fixture_renderer=render)
