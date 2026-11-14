#!/usr/bin/env python3
"""Check reserved Boolean/null BooleanNot input and exact selector authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_positive_string_concat_tree_quiet_get_protocol as prior
import magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_protocol as source_tree
import magic_property_methodclosure_static_raw_fqn_keyword_concat_tree_quiet_get_protocol as renderer

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_keyword_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_positive_string_tree(',
                     '$property_magic_cv_raw_not_keyword_string_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_positive_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_positive_string_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    words = ((('class', (0, 1, 1, 0), 'true', 'NName'),
              ('method', (1, 1, 1, 1, 1), 'null', 'NNameFullyQualified')) if index == 0 else
             (('class', (0, 1, 0, 1), 'false', 'NNameFullyQualified'),
              ('method', (1, 0, 1), 'true', 'NNameFullyQualified')))
    for number, (side, parts, word, constructor) in enumerate(words):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin = 'porigin_not_' + str(number)
        constant_origin = 'porigin_not_constant_' + str(number)
        name_origin = 'porigin_not_name_' + str(number)
        metadata = 'metadata_not_' + str(number)
        constant_metadata = 'metadata_not_constant_' + str(number)
        name_metadata = 'metadata_not_name_' + str(number)
        text = 'text_not_' + str(number)
        value = 'pvalue_not_' + str(number)
        name = f'{constructor} (BYTES {text}) {name_metadata}'
        constant = f'NExprConstFetch ({name}) {constant_metadata}'
        node = f'NExprBooleanNot ({constant}) {metadata}'
        expression = 'expression_not_' + str(number)
        expected = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[word]
        truth = 'true' if word == 'true' else 'false'
        complement = 'false' if word == 'true' else 'true'
        other_constructor = 'NName' if constructor == 'NNameFullyQualified' else 'NNameFullyQualified'
        other_word = 'ZmFsc2U=' if word == 'null' else 'bnVsbA=='
        result += [
            f'$origin_child((porigin_site),{source_tree.path(parts)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{expression} = {node}',
            rf'{metadata} =/= eps /\ {constant_metadata} =/= eps /\ {name_metadata} =/= eps',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({constant_origin})',
            f'$origin_node(S.SOURCES,{constant_origin}) = ({constant})',
            f'$origin_child(({constant_origin}),[PCFIELD 0]) = ({name_origin})',
            f'$origin_node(S.SOURCES,{name_origin}) = ({name})',
            f'$special_constant($base64({text})) = ({value})',
            f'{value} = {expected}',
            f'$truth(S,{value}) = {truth}',
            f'$truth_value(S,{value},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
            f'({value} =/= PBOOL true) = {complement}',
            f'$echo_value(PBOOL (~$truth(S,{value}))) = $echo_value(PBOOL {complement})',
            f'$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,{constant_origin},{constant}) = ($echo_value({value}))',
            f'$property_magic_cv_raw_not_keyword_string_tree(S.SOURCES,{origin},{expression}) = ($echo_value(PBOOL {complement}))',
            f'$property_magic_cv_raw_positive_string_tree(S.SOURCES,{origin},{expression}) = eps',
            rf'$compiled_read(S_trim,{origin}) = eps /\ $compiled_read(S_trim,{constant_origin}) = eps /\ $compiled_read(S_trim,{name_origin}) = eps',
        ]
        for label, changed_parts, forged in (
            ('operator_metadata', parts, f'NExprBooleanNot ({constant}) eps'),
            ('operator_kind', parts, f'NExprUnaryPlus ({constant}) {metadata}'),
            ('constant_metadata', parts + (0,), f'NExprConstFetch ({name}) eps'),
            ('constant_kind', parts + (0,), f'NExprVariable (BYTES {text}) {constant_metadata}'),
            ('name_metadata', parts + (0, 0), f'{constructor} (BYTES {text}) eps'),
            ('name_kind', parts + (0, 0), f'{other_constructor} (BYTES {text}) {name_metadata}'),
            ('name_value', parts + (0, 0), f'{constructor} (BYTES "{other_word}") {name_metadata}'),
            ('operator_missing', parts, None),
            ('constant_missing', parts + (0,), None),
            ('name_missing', parts + (0, 0), None),
        ):
            state = f'S_not_{number}_{label}'
            node_path = 'pcpath_site ++ ' + source_tree.path(changed_parts)
            occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{node_path})' if forged is None else
                           f'(PCOCCURRENCE ({node_path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                       f'$property_magic_cv_raw_not_keyword_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                       '~' + source_tree.selector(side, state)]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_not_root_{side}_{label}'
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if selected == side else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([' + ','.join(constants) + '])}]]',
                       '~' + source_tree.selector(side, state),
                       source_tree.selector('method' if side == 'class' else 'class', state)]
    for label, constructor, text in (('named', 'NName', 'UEhQX0lOVF9NQVg='),
                                     ('relative', 'NNameRelative', 'dHJ1ZQ==')):
        name = f'{constructor} (BYTES "{text}") metadata_class'
        constant = f'NExprConstFetch ({name}) metadata_class'
        node = f'NExprBooleanNot ({constant}) metadata_class'
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), constant), ((0, 0), name)):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {source_tree.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'expression_control_{label} = {node}',
                   f'S_control_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                   f'$property_magic_cv_raw_not_keyword_string_tree(S_control_{label}.SOURCES,porigin_class,expression_control_{label}) = eps']
    result += ['~$property_magic_cv_static_method_site_selector(S,porigin_site,expression_not_0,porigin_requested,pclassdesc_requested.NAME)',
               '~$property_magic_cv_static_method_site_name(S,porigin_site,expression_not_1,pmethoddesc_method.NAME)']
    return result


CASES = {row['id']: dict(source=row['source'], stage=old['stage'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = source_tree.prior.prior.base
    parents = (prior, prior.prior, prior.prior.prior, renderer, source_tree,
               source_tree.prior, source_tree.prior.prior, base, base.original,
               base.inherited, base.inherited.prior, base.inherited.prior.prior,
               base.inherited.prior.prior.prior, renderer.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
