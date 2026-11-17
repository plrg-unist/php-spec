#!/usr/bin/env python3
"""Check recursive quiet NOT/CONCAT truth-of-echo receipts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_text_concat_not_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_recursive_not_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_text_concat_not_tree(',
                     '$property_magic_cv_raw_recursive_not_concat_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_text_concat_not_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_text_concat_not_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    false, true, fqn_null = (('keyword', 'false', False), ('keyword', 'true', False),
                             ('keyword', 'NULL', True))
    leaves = ((('class', (0, 1, 1, 0), ('not', ('not', true)), b'1'),
               ('method', (1, 1, 1, 1, 1), ('plus', ('string', b' -000 '), 0), b'0'))
              if index == 0 else
              (('class', (0, 1, 0, 1), ('plus', false, 0), b'0'),
               ('method', (1, 0, 1), ('concat', ('not', ('concat', false, fqn_null)),
                                      ('concat', ('plus', ('integer', 12), 12), ('string', b''))), b'112')))
    for number, (side, parts, tree, joined) in enumerate(leaves):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        nodes = []

        def raw(value, suffix, relative):
            metadata = 'metadata_text_' + suffix
            kind = value[0]
            data = []
            if kind == 'integer':
                payload = 'i_text_' + suffix
                node = f'NScalarInt (INTEGER {payload}) {metadata}'
                data += [f'{payload} = {value[1]}', f'$long_range({payload})']
                changed = f'NScalarInt (INTEGER 0) {metadata}'
            elif kind == 'string':
                payload = 'text_text_' + suffix
                node = f'NScalarString (BYTES {payload}) {metadata}'
                data += [f'{payload} = "{base64.b64encode(value[1]).decode()}"']
                changed = f'NScalarString (BYTES "Y2hhbmdlZA==") {metadata}'
            elif kind == 'keyword':
                payload, name_metadata = 'text_text_' + suffix, 'metadata_name_' + suffix
                constructor = 'NNameFullyQualified' if value[2] else 'NName'
                name = f'{constructor} (BYTES {payload}) {name_metadata}'
                node = f'NExprConstFetch ({name}) {metadata}'
                data += [f'{payload} = "{base64.b64encode(value[1].encode()).decode()}"',
                         f'$special_constant($base64({payload})) = (' + ('PNULL' if value[1].lower() == 'null' else 'PBOOL ' + value[1].lower()) + ')']
                replacement = 'ZmFsc2U=' if value[1].lower() == 'true' else 'dHJ1ZQ=='
                name_origin = 'porigin_text_name_' + suffix
                data += [f'$origin_child((porigin_not_{number}),{source_tree.path(relative + (0,))}) = ({name_origin})',
                         f'$origin_node(S.SOURCES,{name_origin}) = ({name})', f'{name_metadata} =/= eps',
                         f'$compiled_read(S_trim,{name_origin}) = eps']
                nodes.append((relative + (0,), name_origin, name,
                              f'{constructor} (BYTES "{replacement}") {name_metadata}',
                              f'{constructor} (BYTES {payload}) eps'))
                changed = f'NExprConstFetch (NName (BYTES "{replacement}") {name_metadata}) {metadata}'
            else:
                left, bindings = raw(value[1], suffix + '0', relative + (0,))
                data += bindings
                if kind == 'concat':
                    right, bindings = raw(value[2], suffix + '1', relative + (1,))
                    data += bindings
                    node = f'NExprBinaryOpConcat ({left}) ({right}) {metadata}'
                    changed = f'NExprBinaryOpPlus ({left}) ({right}) {metadata}'
                else:
                    constructor = 'NExprUnaryPlus' if kind == 'plus' else 'NExprBooleanNot'
                    node = f'{constructor} ({left}) {metadata}'
                    changed = f'NExprUnaryMinus ({left}) {metadata}'
                    if kind == 'plus':
                        data += [f'$property_magic_cv_raw_positive_string_tree(S.SOURCES,porigin_text_{suffix},{node}) = ($ntsigned({value[2]}))']
            origin = 'porigin_text_' + suffix
            nodes.append((relative, origin, node, changed, node[:-len(metadata)] + 'eps'))
            return node, [f'$origin_child((porigin_not_{number}),{source_tree.path(relative)}) = ({origin})',
                          f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{metadata} =/= eps',
                          f'$compiled_read(S_trim,{origin}) = eps'] + data

        child, bindings = raw(tree, str(number), (0,))
        node = f'NExprBooleanNot ({child}) metadata_not_{number}'
        truth, complement = ('false', 'true') if joined in (b'', b'0') else ('true', 'false')
        child_value = ('PBOOL true' if index == 0 and number == 0 else
                       f'PSTRING ptbytes_joined_{number}' if index == 1 and number == 1 else 'PINT 0')
        result += [f'$origin_child((porigin_site),{source_tree.path(parts)}) = (porigin_not_{number})',
                   f'$origin_node(S.SOURCES,porigin_not_{number}) = ({node})',
                   f'expression_not_{number} = {node}', f'metadata_not_{number} =/= eps'] + bindings
        result += [f'ptbytes_joined_{number} = $base64("{base64.b64encode(joined).decode()}")',
                   f'$property_magic_cv_raw_recursive_not_concat_tree(S.SOURCES,porigin_text_{number},{child}) = (ptbytes_joined_{number})',
                   f'~(0 <- ptbytes_joined_{number})',
                   f'$echo_value({child_value}) = ptbytes_joined_{number}',
                   f'$truth_value(S,{child_value},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$truth_value(S,PSTRING ptbytes_joined_{number},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$property_magic_cv_raw_recursive_not_concat_tree(S.SOURCES,porigin_not_{number},expression_not_{number}) = ($echo_value(PBOOL {complement}))',
                   f'$property_magic_cv_raw_text_concat_not_tree(S.SOURCES,porigin_not_{number},expression_not_{number}) = eps',
                   f'$compiled_read(S_trim,porigin_not_{number}) = eps']
        nodes.append(((), f'porigin_not_{number}', node,
                      f'NExprUnaryPlus ({child}) metadata_not_{number}',
                      f'NExprBooleanNot ({child}) eps'))
        for position, (relative, origin, actual, changed, empty_metadata) in enumerate(nodes):
            for label, forged in (('value_or_kind', changed), ('metadata', empty_metadata), ('missing', None)):
                state = f'S_text_not_{number}_{position}_{label}'
                path = 'pcpath_site ++ ' + source_tree.path(parts + relative)
                occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{path})' if forged is None else
                               f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
                result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                           f'$property_magic_cv_raw_recursive_not_concat_tree({state}.SOURCES,{root},expression_{side}) = eps',
                           '~' + source_tree.selector(side, state)]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_text_root_{side}_{label}'
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


CASES = {row['id']: dict(source=row['source'], stage=prior.CASES[row['derived_from']['id']]['stage'], checks=checks(index))
         for index, row in enumerate(ROWS)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = source_tree.prior.prior.base
    parents = (prior, prior.prior, prior.prior.prior, prior.prior.prior.prior,
               prior.prior.prior.prior.prior, prior.prior.prior.prior.prior.prior,
               prior.prior.prior.prior.prior.prior.prior,
               prior.prior.prior.prior.prior.prior.prior.prior,
               prior.prior.prior.prior.prior.prior.prior.prior.prior,
               prior.prior.prior.prior.prior.prior.prior.prior.prior.prior,
               renderer, source_tree, source_tree.prior, source_tree.prior.prior,
               base, base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior,
               renderer.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
