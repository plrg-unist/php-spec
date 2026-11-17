#!/usr/bin/env python3
"""Check exact double NOT of authenticated quiet scalar NOT leaves."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_not_string_concat_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_double_not_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_not_string_tree(',
                     '$property_magic_cv_raw_double_not_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_not_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_not_string_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    leaves = ((('class', (0, 1, 1, 0), 'integer', 0),
               ('method', (1, 1, 1, 1, 1), 'fqn', 'true')) if index == 0 else
              (('class', (0, 1, 0, 1), 'integer', 9223372036854775807),
               ('method', (1, 0, 1), 'simple', 'null')))
    for number, (side, parts, kind, expected) in enumerate(leaves):
        suffix = str(number)
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin, inner_origin, raw_origin = ('porigin_not_' + suffix,
                                          'porigin_inner_' + suffix, 'porigin_raw_' + suffix)
        metadata, inner_metadata, raw_metadata = ('metadata_not_' + suffix,
                                                 'metadata_inner_' + suffix, 'metadata_raw_' + suffix)
        expression, value, inner_bytes = ('expression_not_' + suffix,
                                          'pvalue_raw_' + suffix, 'ptbytes_inner_' + suffix)
        scalar = f'NScalarInt (INTEGER i_raw_{suffix}) {raw_metadata}' if kind == 'integer' else (
            f'NExprConstFetch (NName' + ('FullyQualified' if kind == 'fqn' else '') +
            f' (BYTES text_raw_{suffix}) metadata_name_{suffix}) {raw_metadata}')
        inner = f'NExprBooleanNot ({scalar}) {inner_metadata}'
        node = f'NExprBooleanNot ({inner}) {metadata}'
        truth = 'true' if expected not in (0, 'null') else 'false'
        inner_truth = 'false' if truth == 'true' else 'true'
        result += [f'$origin_child((porigin_site),{source_tree.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   rf'{metadata} =/= eps /\ {inner_metadata} =/= eps /\ {raw_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({inner_origin})',
                   f'$origin_node(S.SOURCES,{inner_origin}) = ({inner})',
                   f'$origin_child(({inner_origin}),[PCFIELD 0]) = ({raw_origin})',
                   f'$origin_node(S.SOURCES,{raw_origin}) = ({scalar})']
        if kind == 'integer':
            result += [f'i_raw_{suffix} = {expected}', f'$long_range(i_raw_{suffix})',
                       f'{value} = PINT i_raw_{suffix}']
        else:
            result += [f'$origin_child(({raw_origin}),[PCFIELD 0]) = (porigin_name_{suffix})',
                       f'$origin_node(S.SOURCES,porigin_name_{suffix}) = (NName' +
                       ('FullyQualified' if kind == 'fqn' else '') +
                       f' (BYTES text_raw_{suffix}) metadata_name_{suffix})',
                       f'metadata_name_{suffix} =/= eps',
                       f'$special_constant($base64(text_raw_{suffix})) = ({value})',
                       f'{value} = ' + ('PBOOL true' if expected == 'true' else 'PNULL')]
        result += [f'$truth_value(S,{value},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'{inner_bytes} = $echo_value(PBOOL {inner_truth})',
                   f'$property_magic_cv_raw_not_string_tree(S.SOURCES,{inner_origin},{inner}) = ({inner_bytes})',
                   rf'{inner_bytes} = eps \/ {inner_bytes} = [49]',
                   f'$truth_value(S,PBOOL {inner_truth},0) = S[.RESULT = KNOWN (PBOOL {inner_truth})]',
                   f'$echo_value(PBOOL ({inner_bytes} = eps)) = $echo_value(PBOOL {truth})',
                   f'$property_magic_cv_raw_double_not_tree(S.SOURCES,{origin},{expression}) = ($echo_value(PBOOL {truth}))',
                   f'$property_magic_cv_raw_not_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   rf'$compiled_read(S_trim,{origin}) = eps /\ $compiled_read(S_trim,{inner_origin}) = eps /\ $compiled_read(S_trim,{raw_origin}) = eps']
        for label, changed_parts, forged in (
            ('outer_metadata', parts, f'NExprBooleanNot ({inner}) eps'),
            ('outer_kind', parts, f'NExprUnaryPlus ({inner}) {metadata}'),
            ('inner_metadata', parts + (0,), f'NExprBooleanNot ({scalar}) eps'),
            ('inner_kind', parts + (0,), f'NExprUnaryPlus ({scalar}) {inner_metadata}'),
            ('raw_metadata', parts + (0, 0), scalar.rsplit(' ', 1)[0] + ' eps'),
            ('raw_kind', parts + (0, 0), f'NScalarString (BYTES "MA==") {raw_metadata}'),
            ('outer_missing', parts, None), ('inner_missing', parts + (0,), None),
            ('raw_missing', parts + (0, 0), None),
        ):
            state = f'S_not_{number}_{label}'
            path = 'pcpath_site ++ ' + source_tree.path(changed_parts)
            occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                       f'$property_magic_cv_raw_double_not_tree({state}.SOURCES,{root},expression_{side}) = eps',
                       '~' + source_tree.selector(side, state)]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_double_root_{side}_{label}'
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
               prior.prior.prior.prior.prior, prior.prior.prior.prior.prior.prior,
               renderer, source_tree, source_tree.prior, source_tree.prior.prior,
               base, base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior,
               renderer.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
