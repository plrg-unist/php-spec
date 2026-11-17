#!/usr/bin/env python3
"""Check raw non-NUL String BooleanNot and exact selector authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_not_integer_concat_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_string_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_not_integer_string_tree(',
                     '$property_magic_cv_raw_not_string_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_not_integer_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_not_integer_string_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    leaves = ((('class', (0, 1, 1, 0), b'00'), ('method', (1, 1, 1, 1, 1), b'')) if index == 0 else
              (('class', (0, 1, 0, 1), b'0'), ('method', (1, 0, 1), b'false')))
    for number, (side, parts, expected) in enumerate(leaves):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin, child_origin = 'porigin_not_' + str(number), 'porigin_not_child_' + str(number)
        metadata, child_metadata = 'metadata_not_' + str(number), 'metadata_not_child_' + str(number)
        text, value, expression = 'text_not_' + str(number), 'ptbytes_not_' + str(number), 'expression_not_' + str(number)
        child = f'NScalarString (BYTES {text}) {child_metadata}'
        node = f'NExprBooleanNot ({child}) {metadata}'
        truth, complement = ('false', 'true') if expected in (b'', b'0') else ('true', 'false')
        result += [f'$origin_child((porigin_site),{source_tree.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   rf'{metadata} =/= eps /\ {child_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
                   f'{text} = "{base64.b64encode(expected).decode()}"',
                   f'{value} = $base64({text})', f'~(0 <- {value})',
                   f'$property_magic_cv_raw_string_tree(S.SOURCES,{child_origin},{child}) = ({value})',
                   f'$truth(S,PSTRING {value}) = {truth}',
                   f'$truth_value(S,PSTRING {value},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   rf'$echo_value(PBOOL ({value} = eps \/ {value} = [48])) = $echo_value(PBOOL {complement})',
                   f'$echo_value(PBOOL (~$truth(S,PSTRING {value}))) = $echo_value(PBOOL {complement})',
                   f'$property_magic_cv_raw_not_string_tree(S.SOURCES,{origin},{expression}) = ($echo_value(PBOOL {complement}))',
                   f'$property_magic_cv_raw_not_integer_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   rf'$compiled_read(S_trim,{origin}) = eps /\ $compiled_read(S_trim,{child_origin}) = eps']
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprBooleanNot ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryPlus ({child}) {metadata}'),
            ('child_metadata', parts + (0,), f'NScalarString (BYTES {text}) eps'),
            ('child_kind', parts + (0,), f'NScalarInt (INTEGER 0) {child_metadata}'),
            ('child_value', parts + (0,), f'NScalarString (BYTES "b3RoZXI=") {child_metadata}'),
            ('parent_missing', parts, None), ('child_missing', parts + (0,), None),
        ):
            state = f'S_not_{number}_{label}'
            path = 'pcpath_site ++ ' + source_tree.path(changed_parts)
            occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                       f'$property_magic_cv_raw_not_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
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
    parents = (prior, prior.prior, prior.prior.prior, prior.prior.prior.prior,
               prior.prior.prior.prior.prior, renderer, source_tree, source_tree.prior,
               source_tree.prior.prior, base, base.original, base.inherited,
               base.inherited.prior, base.inherited.prior.prior,
               base.inherited.prior.prior.prior, renderer.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
