#!/usr/bin/env python3
"""Reach missing-property Empty CV-name selection with and without Get."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_empty_cv_pair_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'no_get': 'anonymous-missing-empty-cv-no-get-booleans',
    'pair': 'anonymous-missing-empty-cv-pair-booleans',
}
PREFIX = r'''
syntax pamecvstage = AMECV_NAME ptbytes | AMECV_ISSET_RESULT ptbytes | AMECV_EMPTY_RESULT ptbytes bool
dec $amecv_output(pevent*) : ptbytes
def $amecv_output(eps) = eps
def $amecv_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $amecv_output(pevent*)
dec $amecv_valid(pstate) : bool
def $amecv_valid(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $amecv_stage(pstate,pamecvstage) : bool
def $amecv_stage(S,AMECV_NAME ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_NAME (POBJECT n) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT true z) :: ptask_tail*
  -- if $property_magic_cv_name(S,porigin,z) = (ptbytes)
def $amecv_stage(S,AMECV_ISSET_RESULT ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if ppropertyisset.NAME = ptbytes
def $amecv_stage(S,AMECV_EMPTY_RESULT ptbytes b_get) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty b_get) :: ptask_tail*
  -- if ppropertyempty.NAME = ptbytes
def $amecv_stage(S,pamecvstage) = false -- otherwise
dec $amecv_seek(pstate,pamecvstage,nat) : pstate
def $amecv_seek(S,pamecvstage,n) = S -- if $amecv_stage(S,pamecvstage) \/ n = 0
def $amecv_seek(S,pamecvstage,n) = $amecv_seek($drive_steps(S[.COMPLETION = NORMAL],1),pamecvstage,$nabs($(n - 1)))
  -- if ~$amecv_stage(S,pamecvstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amecv_seek(S,pamecvstage,n) = S -- otherwise
'''


def seek(target, source, stage):
    return [target + '_raw = $amecv_seek(' + source + ',' + stage + ',2048)',
            target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
            target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
            '$amecv_stage(' + target + ',' + stage + ')']


def checks(case):
    result = []
    previous = 'S_initial'
    with_get = case == 'pair'
    record = 'ppropertyempty' if with_get else 'ppropertyisset'
    prefix = 'property_empty' if with_get else 'property_isset'
    for name, boolean, before in [('no', 'false', ''), ('yes', 'true', 'I:no;EMPTY;')]:
        state = 'S_' + name
        receipt = record + '_' + name
        line = 'z_' + name
        origin = 'porigin_' + name
        tail = 'ptask_' + name + '_tail*'
        selector = '$ptascii("' + name + '")'
        target = 'PROPERTY_EMPTY_TARGET ' + receipt + ' true'
        marker = ('PROPERTY_EMPTY_RESULT ' + receipt + ' false' if with_get
                  else 'PROPERTY_ISSET_RESULT ' + receipt)
        result += seek(state, previous, 'AMECV_NAME (' + selector + ')') + [
            state + '.TODO = (PROPERTY_NAME (POBJECT n_' + name + ') ' + line + ') :: (ORIGIN_RETURN (' + origin + ')) :: (ISSET_RESULT true ' + line + ') :: ' + tail,
            state + '.ORIGIN = (' + origin + ')',
            state + '.OBJECTS[n_' + name + '] = INSTANCE porigin_class_' + name,
            '$property_isset_method(' + state + ',n_' + name + ') = (pmethoddesc_' + name + ')',
        ]
        fields = ('SITE ' + origin + ', NAME ' + selector + ', LINE ' + line +
                  ', OBJECT n_' + name + ', CLASS porigin_class_' + name)
        if with_get:
            result += ['$property_get_method(' + state + ',n_' + name + ') = (pmethoddesc_get_' + name + ')']
            fields += ', ISSET pmethoddesc_' + name + '.FUNCTION.ORIGIN, GET pmethoddesc_get_' + name + '.FUNCTION.ORIGIN'
        else:
            fields += ', METHOD pmethoddesc_' + name + '.FUNCTION.ORIGIN'
        result += [
            receipt + ' = {' + fields + ', PROPERTY eps}',
            '$property_magic_cv_source(' + state + ',' + origin + ',' + line + ')',
            '$' + prefix + '_plan(' + state + ') = (' + receipt + ')',
            '$' + prefix + '_valid(' + state + ',' + receipt + ') /\\ $' + prefix + '_capture(' + state + ',' + receipt + ')',
            '$' + prefix + '_storage_capture(' + state + ',' + receipt + ')',
            '$' + ('property_isset' if with_get else 'property_empty') + '_plan(' + state + ') = eps',
            '$' + prefix + '_plan(' + state + '[.TODO = (PROPERTY_NAME (POBJECT n_' + name + ') ' + line + ') :: (ORIGIN_RETURN (' + origin + ')) :: (ISSET_RESULT false ' + line + ') :: ' + tail + ']) = eps',
            '~$' + prefix + '_capture(' + state + ',' + receipt + '[.NAME = $ptascii("forged")])',
            '$amecv_output(' + state + '.EVENTS) = $ptascii("' + before + '")',
            '$amecv_valid(' + state + ')',
        ]
        if not with_get:
            result += ['$property_isset_empty(' + state + ',' + receipt + ')',
                       '$property_get_method(' + state + ',n_' + name + ') = eps']
        if name == 'no':
            result += [
                '$origin_node(' + state + '.SOURCES,' + origin + ') = (NExprPropertyFetch expression_receiver (NExprVariable (BYTES text_selector) metadata_selector) metadata)',
                '$lookup(' + state + '.ENV,$base64(text_selector)) = (n_selector)',
                'S_renamed = ' + state + '[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("renamed")))]',
                '~$' + prefix + '_capture(S_renamed,' + receipt + ')',
                '$' + prefix + '_capture(S_renamed,' + receipt + '[.NAME = $ptascii("renamed")])',
                '$' + prefix + '_plan(S_renamed) = (' + receipt + '[.NAME = $ptascii("renamed")])',
                'S_nonstring = ' + state + '[.STORE[n_selector] = DEFINED (PINT 9)]',
                '$' + prefix + '_plan(S_nonstring) = eps',
                '$' + prefix + '_plan(' + state + '[.SOURCES = eps]) = eps',
            ]
        stage = ('AMECV_EMPTY_RESULT (' + selector + ') false' if with_get
                 else 'AMECV_ISSET_RESULT (' + selector + ')')
        result += seek(state + '_result', state, stage) + [
            state + '_result.TODO = (' + marker + ') :: ' + tail,
            state + '_result.RESULT = KNOWN (PBOOL ' + boolean + ')',
            '$' + prefix + '_valid(' + state + '_result,' + receipt + ')',
            '~$property_empty_get_active(' + state + '_result,n_' + name + ',' + receipt + '.NAME)',
            '$heap_owners($heap_graph(' + state + '_result),HOBJECT n_' + name + ') = 2',
            '$amecv_output(' + state + '_result.EVENTS) = $ptascii("' + before + 'I:' + name + ';")',
            'PhpStep: ' + state + '_result ~> ' + state + '_step',
        ]
        if with_get and name == 'yes':
            result += [
                state + '_step.TODO = (CALL_ARGS (' + target + ') eps 1 ([KNOWN (PSTRING ' + receipt + '.NAME)]) (' + origin + ') ' + line + ') :: (PROPERTY_EMPTY_RESULT ' + receipt + ' true) :: ' + tail,
                '$property_empty_pending_call(' + state + '_step,' + receipt + ',true)',
                '$heap_owners($heap_graph(' + state + '_step),HOBJECT n_' + name + ') = 2',
            ] + seek('S_get_result', state + '_step', 'AMECV_EMPTY_RESULT (' + selector + ') true') + [
                'S_get_result.RESULT = KNOWN (PINT 7)',
                '$amecv_output(S_get_result.EVENTS) = $ptascii("I:no;EMPTY;I:yes;GET:yes;")',
                '$property_empty_valid(S_get_result,' + receipt + ')',
                '$property_magic_cv_result_supported(S_get_result,' + origin + ',' + line + ',true,KNOWN (PINT 7))',
                '~$property_magic_cv_result_supported(S_get_result,' + origin + ',' + line + ',true,KNOWN PNULL)',
                '~$property_magic_cv_result_supported(S_get_result,' + origin + ',' + line + ',true,KNOWN (PBOOL false))',
                'PhpStep: S_get_result ~> S_get_step',
                'S_get_step = S_get_result[.TODO = ' + tail + '][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
                '$heap_owners($heap_graph(S_get_step),HOBJECT n_' + name + ') = 1',
            ]
        else:
            result += [
                state + '_step = ' + state + '_result[.TODO = ' + tail + '][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
                '$heap_owners($heap_graph(' + state + '_step),HOBJECT n_' + name + ') = 1',
            ]
        previous = state + '_result'
    expected = '$base64(' + json.dumps(ROWS[CASES[case]]['stdout_template_base64']) + ')'
    return result + [
        'S_zero = $drive_steps(S_no_result,0)',
        'S_zero = S_no_result[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(S_no_result,4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps /\\ S_full.CURRENT = eps /\\ S_full.FRAMES = eps /\\ S_full.HELD = eps',
        '$amecv_output(S_full.EVENTS) = ' + expected,
        '$amecv_valid(S_full)',
    ]


def render(case, fixture, filename):
    clauses = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
               'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP'] + checks(case['id'])
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- ' + ('' if clause.startswith('PhpStep:') else 'if ') + clause + '\n'
                    for clause in clauses), len(clauses))


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
