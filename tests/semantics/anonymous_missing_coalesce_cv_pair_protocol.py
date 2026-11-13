#!/usr/bin/env python3
"""Reach missing-property coalesce CV-name decisions and the separate ??= refusal."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_coalesce_cv_pair_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'no_get': 'anonymous-missing-coalesce-cv-no-get-booleans',
    'pair': 'anonymous-missing-coalesce-cv-pair-booleans',
}
ASSIGN_SOURCE = '''<?php
function missing_rhs(): int { return 9; }
$name = "missing";
$o = new class {
    public function __isset(string $name): bool { return true; }
    public function __get($name) { return 0; }
};
$o->{$name} ??= missing_rhs();
'''
PREFIX = r'''
syntax pamccvstage = AMCCV_NAME ptbytes | AMCCV_RESULT ptbytes bool | AMCCV_ASSIGN
dec $amccv_output(pevent*) : ptbytes
def $amccv_output(eps) = eps
def $amccv_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $amccv_output(pevent*)
dec $amccv_valid(pstate) : bool
def $amccv_valid(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $amccv_stage(pstate,pamccvstage) : bool
def $amccv_stage(S,AMCCV_NAME ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_NAME (POBJECT n) z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $property_magic_cv_name(S,porigin,z) = (ptbytes)
def $amccv_stage(S,AMCCV_RESULT ptbytes b_get) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce b_get) :: ptask_tail*
  -- if ppropertycoalesce.NAME = ptbytes
def $amccv_stage(S,AMCCV_ASSIGN) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $property_magic_coalesce_assign_pending(S[.COMPLETION = NORMAL])
def $amccv_stage(S,pamccvstage) = false -- otherwise
dec $amccv_seek(pstate,pamccvstage,nat) : pstate
def $amccv_seek(S,pamccvstage,n) = S -- if $amccv_stage(S,pamccvstage) \/ n = 0
def $amccv_seek(S,pamccvstage,n) = $amccv_seek($drive_steps(S[.COMPLETION = NORMAL],1),pamccvstage,$nabs($(n - 1)))
  -- if ~$amccv_stage(S,pamccvstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amccv_seek(S,pamccvstage,n) = S -- otherwise
'''


def seek(target, source, stage):
    return [target + '_raw = $amccv_seek(' + source + ',' + stage + ',2048)',
            target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
            target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
            '$amccv_stage(' + target + ',' + stage + ')']


def normal(case):
    checks = []
    previous = 'S_initial'
    for name, boolean, before in [('no', 'false', ''), ('yes', 'true', 'I:no;FALL;')]:
        state = 'S_' + name
        receipt = 'ppropertycoalesce_' + name
        line = 'z_' + name
        origin = 'porigin_' + name
        parent = 'porigin_parent_' + name
        right = 'expression_' + name + '_right'
        left_line, right_line = 'z_' + name + '_left', 'z_' + name + '_right'
        tail = 'ptask_' + name + '_tail*'
        quiet_tail = '(ORIGIN_RETURN (' + parent + ')) :: (COALESCE_QUIET ' + right + ' ' + left_line + ' ' + right_line + ') :: ' + tail
        delivery = '(ORIGIN_RETURN (' + parent + ')) :: (COALESCE_RESULT ' + right + ' ' + left_line + ' ' + right_line + ') :: ' + tail
        selector = '$ptascii("' + name + '")'
        checks += seek(state, previous, 'AMCCV_NAME (' + selector + ')') + [
            state + '.TODO = (PROPERTY_NAME (POBJECT n_' + name + ') ' + line + ') :: ' + quiet_tail,
            state + '.ORIGIN = (' + origin + ')',
            state + '.OBJECTS[n_' + name + '] = INSTANCE porigin_class_' + name,
            '$property_isset_method(' + state + ',n_' + name + ') = (pmethoddesc_' + name + ')',
            receipt + ' = {SITE ' + origin + ', NAME ' + selector + ', LINE ' + line + ', OBJECT n_' + name + ', CLASS porigin_class_' + name + ', ISSET pmethoddesc_' + name + '.FUNCTION.ORIGIN, GET $property_coalesce_get_origin(' + state + ',n_' + name + '), PROPERTY eps, OWNER (|' + state + '.FRAMES|), CALLER ' + state + '.CURRENT, TAIL (' + quiet_tail + ')}',
            '$property_coalesce_plan(' + state + ') = (' + receipt + ')',
            receipt + '.GET = ' + ('(porigin_get_' + name + ')' if case == 'pair' else 'eps'),
            'S_marker_' + name + ' = ' + state + '[.TODO = (PROPERTY_COALESCE_RESULT ' + receipt + ' false) :: ' + receipt + '.TAIL]',
            '$property_coalesce_descriptor(S_marker_' + name + ',' + receipt + ')',
            '$property_coalesce_valid(S_marker_' + name + ',' + receipt + ') /\\ $property_coalesce_capture(S_marker_' + name + ',' + receipt + ')',
            '$property_coalesce_storage_capture(S_marker_' + name + ',' + receipt + ')',
            '~$property_coalesce_capture(S_marker_' + name + ',' + receipt + '[.NAME = $ptascii("forged")])',
            '~$property_coalesce_descriptor(S_marker_' + name + ',' + receipt + '[.TAIL = eps])',
            '$amccv_output(' + state + '.EVENTS) = $ptascii("' + before + '")',
            '$amccv_valid(' + state + ')',
        ]
        if name == 'no':
            checks += [
                '$origin_node(' + state + '.SOURCES,' + origin + ') = (NExprPropertyFetch expression_receiver (NExprVariable (BYTES text_selector) metadata_selector) metadata)',
                '$lookup(' + state + '.ENV,$base64(text_selector)) = (n_selector)',
                'S_renamed = ' + state + '[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("renamed")))]',
                '$property_coalesce_plan(S_renamed) = (' + receipt + '[.NAME = $ptascii("renamed")])',
                '~$property_coalesce_capture(S_marker_' + name + '[.STORE = S_renamed.STORE],' + receipt + ')',
                'ppropertycoalesce_renamed = ' + receipt + '[.NAME = $ptascii("renamed")]',
                '$property_coalesce_capture(S_renamed[.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce_renamed false) :: ppropertycoalesce_renamed.TAIL],ppropertycoalesce_renamed)',
                '$property_coalesce_plan(' + state + '[.STORE[n_selector] = DEFINED (PINT 9)]) = eps',
                '$property_coalesce_plan(' + state + '[.SOURCES = eps]) = eps',
            ]
        checks += seek(state + '_result', state, 'AMCCV_RESULT (' + selector + ') false') + [
            state + '_result.TODO = (PROPERTY_COALESCE_RESULT ' + receipt + ' false) :: ' + receipt + '.TAIL',
            state + '_result.RESULT = KNOWN (PBOOL ' + boolean + ')',
            '$property_coalesce_valid(' + state + '_result,' + receipt + ')',
            '~$property_isset_guard(' + state + '_result,' + state + '_result.CURRENT,' + state + '_result.FRAMES,n_' + name + ',' + receipt + '.NAME)',
            '~$property_empty_get_active(' + state + '_result,n_' + name + ',' + receipt + '.NAME)',
            '$heap_owners($heap_graph(' + state + '_result),HOBJECT n_' + name + ') = 2',
            '$amccv_output(' + state + '_result.EVENTS) = $ptascii("' + before + 'I:' + name + ';")',
            'PhpStep: ' + state + '_result ~> ' + state + '_step',
        ]
        if case == 'pair' and name == 'yes':
            checks += [
                state + '_step.TODO = (CALL_ARGS (PROPERTY_COALESCE_TARGET ' + receipt + ' true) eps 1 ([KNOWN (PSTRING ' + receipt + '.NAME)]) (' + origin + ') ' + line + ') :: (PROPERTY_COALESCE_RESULT ' + receipt + ' true) :: ' + receipt + '.TAIL',
                '$property_coalesce_pending_call(' + state + '_step,' + receipt + ',true)',
                '$heap_owners($heap_graph(' + state + '_step),HOBJECT n_' + name + ') = 2',
            ] + seek('S_get', state + '_step', 'AMCCV_RESULT (' + selector + ') true') + [
                'S_get.RESULT = KNOWN (PINT 0)',
                '$amccv_output(S_get.EVENTS) = $ptascii("I:no;FALL;I:yes;GET:yes;")',
                '$property_coalesce_valid(S_get,' + receipt + ')',
                '$property_magic_cv_result_supported(S_get,' + origin + ',' + line + ',true,KNOWN (PINT 0))',
                '$property_magic_cv_result_supported(S_get,' + origin + ',' + line + ',true,KNOWN PNULL)',
                'PhpStep: S_get ~> S_get_delivery',
                'S_get_delivery = S_get[.TODO = ' + delivery + '][.BASE = BASE_VALUE (KNOWN PNULL)]',
                '$heap_owners($heap_graph(S_get_delivery),HOBJECT n_' + name + ') = 1',
            ]
        else:
            checks += [
                state + '_step = ' + state + '_result[.TODO = ' + delivery + '][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                '$heap_owners($heap_graph(' + state + '_step),HOBJECT n_' + name + ') = 1',
            ]
        previous = state + '_result'
    expected = '$base64(' + json.dumps(ROWS[CASES[case]]['stdout_template_base64']) + ')'
    return checks + [
        'S_zero = $drive_steps(S_no_result,0)',
        'S_zero = S_no_result[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(S_no_result,4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps /\\ S_full.CURRENT = eps /\\ S_full.FRAMES = eps /\\ S_full.HELD = eps',
        '$amccv_output(S_full.EVENTS) = ' + expected,
        '$amccv_valid(S_full)',
    ]


def assignment():
    return seek('S', 'S_initial', 'AMCCV_ASSIGN') + [
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
        '$property_magic_cv_source(S_marker,porigin_site,z_property)',
        '$property_effective_desc(S,n_receiver,ptbytes_name) = eps',
        '~$property_coalesce_descriptor(S_marker,ppropertycoalesce)',
        '~$property_coalesce_valid(S_marker,ppropertycoalesce)',
        '~$property_coalesce_capture(S_marker,ppropertycoalesce)',
        '$property_coalesce_assign_plan(S) = eps',
        '$amccv_valid(S)',
        'PhpStep: S ~> S_refused',
        'S_refused = S[.COMPLETION = UNSUPPORTED "magic coalesce assignment source or methods"]',
    ]


def render(case, fixture, filename):
    clauses = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
               'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']
    clauses += assignment() if case['id'] == 'assignment' else normal(case['id'])
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- ' + ('' if clause.startswith('PhpStep:') else 'if ') + clause + '\n'
                    for clause in clauses), len(clauses))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted([*CASES, 'assignment']))
    args = parser.parse_args()
    sources = {}
    for name, row_id in CASES.items():
        row = ROWS[row_id]
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
        sources[name] = {'id': name, 'source': row['source']}
    sources['assignment'] = {'id': 'assignment', 'source': ASSIGN_SOURCE}
    protocol.run({name: sources[name] for name in args.case or sources},
                 (Path(__file__), CATALOGUE), fixture_renderer=render)
