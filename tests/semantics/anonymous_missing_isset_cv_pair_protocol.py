#!/usr/bin/env python3
"""Reach missing-property Isset CV-name selection with and without Get."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_isset_cv_pair_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'no_get': 'anonymous-missing-isset-cv-no-get-booleans',
    'pair': 'anonymous-missing-isset-cv-pair-booleans',
}
PREFIX = r'''
syntax pamcvpstage = AMCVP_NAME ptbytes | AMCVP_RESULT ptbytes
dec $amcvp_output(pevent*) : ptbytes
def $amcvp_output(eps) = eps
def $amcvp_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $amcvp_output(pevent*)
dec $amcvp_valid(pstate) : bool
def $amcvp_valid(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $amcvp_stage(pstate,pamcvpstage) : bool
def $amcvp_stage(S,AMCVP_NAME ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_NAME (POBJECT n) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail*
  -- if $property_magic_cv_name(S,porigin,z) = (ptbytes)
def $amcvp_stage(S,AMCVP_RESULT ptbytes) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if ppropertyisset.NAME = ptbytes
def $amcvp_stage(S,pamcvpstage) = false -- otherwise
dec $amcvp_seek(pstate,pamcvpstage,nat) : pstate
def $amcvp_seek(S,pamcvpstage,n) = S -- if $amcvp_stage(S,pamcvpstage) \/ n = 0
def $amcvp_seek(S,pamcvpstage,n) = $amcvp_seek($drive_steps(S[.COMPLETION = NORMAL],1),pamcvpstage,$nabs($(n - 1)))
  -- if ~$amcvp_stage(S,pamcvpstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amcvp_seek(S,pamcvpstage,n) = S -- otherwise
'''


def seek(target, source, stage):
    return [target + '_raw = $amcvp_seek(' + source + ',' + stage + ',2048)',
            target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
            target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
            '$amcvp_stage(' + target + ',' + stage + ')']


def checks(case):
    result = []
    previous = 'S_initial'
    with_get = case == 'pair'
    for name, boolean, before in [('no', 'false', ''),
                                  ('yes', 'true', 'I:no;' + ('SHORT;' if with_get else 'NO;'))]:
        state = 'S_' + name
        receipt = 'ppropertyisset_' + name
        line = 'z_' + name
        origin = 'porigin_' + name
        tail = 'ptask_' + name + '_tail*'
        result += seek(state, previous, 'AMCVP_NAME ($ptascii("' + name + '"))') + [
            state + '.TODO = (PROPERTY_NAME (POBJECT n_' + name + ') ' + line + ') :: (ORIGIN_RETURN (' + origin + ')) :: (ISSET_RESULT false ' + line + ') :: ' + tail,
            state + '.ORIGIN = (' + origin + ')',
            state + '.OBJECTS[n_' + name + '] = INSTANCE porigin_class_' + name,
            '$property_isset_method(' + state + ',n_' + name + ') = (pmethoddesc_' + name + ')',
            receipt + ' = {SITE ' + origin + ', NAME $ptascii("' + name + '"), LINE ' + line + ', OBJECT n_' + name + ', CLASS porigin_class_' + name + ', METHOD pmethoddesc_' + name + '.FUNCTION.ORIGIN, PROPERTY eps}',
            '$property_magic_cv_source(' + state + ',' + origin + ',' + line + ')',
            '$property_isset_missing_source(' + state + ',' + receipt + ')',
            '$property_isset_plan(' + state + ') = (' + receipt + ')',
            '$property_isset_valid(' + state + ',' + receipt + ') /\\ $property_isset_capture(' + state + ',' + receipt + ')',
            '$property_isset_bool_pair(' + state + ',' + receipt + ') = ' + str(with_get).lower(),
            '~$property_isset_untyped(' + state + ',' + receipt + ')',
            '$property_empty_plan(' + state + ') = eps',
            '$property_isset_plan(' + state + '[.TODO = (PROPERTY_NAME (POBJECT n_' + name + ') ' + line + ') :: (ORIGIN_RETURN (' + origin + ')) :: (ISSET_RESULT true ' + line + ') :: ' + tail + ']) = eps',
            '~$property_isset_capture(' + state + ',' + receipt + '[.NAME = $ptascii("forged")])',
            '$amcvp_output(' + state + '.EVENTS) = $ptascii("' + before + '")',
            '$amcvp_valid(' + state + ')',
        ]
        if name == 'no':
            result += [
                '$origin_node(' + state + '.SOURCES,' + origin + ') = (NExprPropertyFetch expression_receiver (NExprVariable (BYTES text_selector) metadata_selector) metadata)',
                '$lookup(' + state + '.ENV,$base64(text_selector)) = (n_selector)',
                'S_renamed = ' + state + '[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("renamed")))]',
                '~$property_isset_capture(S_renamed,' + receipt + ')',
                '$property_isset_capture(S_renamed,' + receipt + '[.NAME = $ptascii("renamed")])',
                '$property_isset_plan(S_renamed) = (' + receipt + '[.NAME = $ptascii("renamed")])',
                'S_nonstring = ' + state + '[.STORE[n_selector] = DEFINED (PINT 9)]',
                '~$property_isset_capture(S_nonstring,' + receipt + ')',
                '$property_isset_plan(S_nonstring) = eps',
                '$property_isset_plan(' + state + '[.SOURCES = eps]) = eps',
            ]
        result += seek(state + '_result', state, 'AMCVP_RESULT ($ptascii("' + name + '"))') + [
            state + '_result.TODO = (PROPERTY_ISSET_RESULT ' + receipt + ') :: ' + tail,
            state + '_result.RESULT = KNOWN (PBOOL ' + boolean + ')',
            '$property_isset_valid(' + state + '_result,' + receipt + ')',
            '~$property_empty_get_active(' + state + '_result,n_' + name + ',' + receipt + '.NAME)',
            '$heap_owners($heap_graph(' + state + '_result),HOBJECT n_' + name + ') = 2',
            '$amcvp_output(' + state + '_result.EVENTS) = $ptascii("' + before + 'I:' + name + ';")',
            'PhpStep: ' + state + '_result ~> ' + state + '_step',
            state + '_step = ' + state + '_result[.TODO = ' + tail + '][.RESULT = KNOWN (PBOOL ' + boolean + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
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
        '$amcvp_output(S_full.EVENTS) = ' + expected,
        '$amcvp_valid(S_full)',
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
