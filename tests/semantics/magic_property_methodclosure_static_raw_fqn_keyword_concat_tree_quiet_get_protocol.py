#!/usr/bin/env python3
"""Check FQN keyword source children and exact folded selector roots."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_protocol as prior
import magic_property_owning_quiet_empty_get_review_protocol as renderer

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_fqn_keyword_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PREFIX = r'''
dec $fqn_keyword_without(pcoccurrence*,pcpath) : pcoccurrence*
def $fqn_keyword_without(eps,pcpath) = eps
def $fqn_keyword_without((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*,pcpath) = $fqn_keyword_without(pcoccurrence*,pcpath)
def $fqn_keyword_without((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*,pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $fqn_keyword_without(pcoccurrence*,pcpath)
  -- if pcpath_other =/= pcpath
'''

TREE = [line.replace('$property_magic_cv_raw_keyword_string_tree(',
                     '$property_magic_cv_raw_fqn_keyword_string_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_keyword_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_keyword_string_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    keywords = ((('class', (0, 1, 1, 1), 'true'),
                 ('method', (1, 1, 0), 'false'),
                 ('method', (1, 1, 1, 1, 1), 'null')) if index == 0 else
                (('class', (0, 1, 0, 0), 'null'),
                 ('class', (0, 1, 0, 1), 'false'),
                 ('method', (1, 1), 'true')))
    for number, (side, parts, word) in enumerate(keywords):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin = 'porigin_fqn_' + str(number)
        name_origin = 'porigin_fqn_name_' + str(number)
        metadata = 'metadata_fqn_' + str(number)
        name_metadata = 'metadata_fqn_name_' + str(number)
        text = 'text_fqn_' + str(number)
        node = f'NExprConstFetch (NNameFullyQualified (BYTES {text}) {name_metadata}) {metadata}'
        expression = 'expression_fqn_' + str(number)
        value = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[word]
        rendered = '$ptascii("1")' if word == 'true' else 'eps'
        result += [
            f'$origin_child((porigin_site),{prior.path(parts)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{expression} = {node}',
            rf'{metadata} =/= eps /\ {name_metadata} =/= eps',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({name_origin})',
            f'$origin_node(S.SOURCES,{name_origin}) = (NNameFullyQualified (BYTES {text}) {name_metadata})',
            f'$special_constant($base64({text})) = ({value})',
            f'$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,{origin},{expression}) = ({rendered})',
            f'$property_magic_cv_raw_keyword_string_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$parser_literal({expression}) = eps',
            rf'$compiled_read(S_trim,{origin}) = eps /\ $compiled_read(S_trim,{name_origin}) = eps',
        ]
        for label, changed_parts, forged in (
            ('expression_metadata', parts, f'NExprConstFetch (NNameFullyQualified (BYTES {text}) {name_metadata}) eps'),
            ('expression_kind', parts, f'NExprVariable (BYTES {text}) {metadata}'),
            ('name_metadata', parts + (0,), f'NNameFullyQualified (BYTES {text}) eps'),
            ('name_value', parts + (0,), f'NNameFullyQualified (BYTES "d3Jvbmc=") {name_metadata}'),
            ('name_simple', parts + (0,), f'NName (BYTES {text}) {name_metadata}'),
            ('name_relative', parts + (0,), f'NNameRelative (BYTES {text}) {name_metadata}'),
            ('expression_missing', parts, None),
            ('name_missing', parts + (0,), None),
        ):
            state = f'S_fqn_{number}_{label}'
            node_path = 'pcpath_site ++ ' + prior.path(changed_parts)
            occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{node_path})' if forged is None else
                           f'(PCOCCURRENCE ({node_path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [
                f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                f'$property_magic_cv_raw_fqn_keyword_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                '~' + prior.selector(side, state),
            ]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_fqn_root_{side}_{label}'
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if selected == side else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [
                f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([' + ','.join(constants) + '])}]]',
                '~' + prior.selector(side, state),
                prior.selector('method' if side == 'class' else 'class', state),
            ]
    result += [
        '~$property_magic_cv_static_method_site_selector(S,porigin_site,expression_fqn_0,porigin_requested,pclassdesc_requested.NAME)',
        '~$property_magic_cv_static_method_site_name(S,porigin_site,expression_fqn_2,pmethoddesc_method.NAME)',
    ]
    return result


CASES = {row['id']: dict(source=row['source'], stage=old['stage'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


def render(case, fixture, filename):
    text, assertions = renderer.render(case, fixture, filename)
    return PREFIX + text, assertions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = prior.prior.prior.base
    parents = (prior, prior.prior, prior.prior.prior, base, base.original, base.inherited,
               base.inherited.prior, base.inherited.prior.prior,
               base.inherited.prior.prior.prior, renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=render)
