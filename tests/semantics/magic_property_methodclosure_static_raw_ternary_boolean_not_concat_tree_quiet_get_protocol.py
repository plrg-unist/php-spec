#!/usr/bin/env python3
"""Check quiet ternary selection, optional arms and exact scalar-text source authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_boolean_not_concat_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_ternary_boolean_not_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_boolean_not_concat_tree(',
                     '$property_magic_cv_raw_ternary_boolean_not_concat_tree(')
        for line in prior.TREE[:28]]
TREE[15] = '$property_magic_cv_emitted_ternary_concat_value(S,porigin_class,expression_class) = (PSTRING ptbytes_class)'
TREE[16] = '$property_magic_cv_emitted_ternary_concat_value(S,porigin_name,expression_method) = (PSTRING ptbytes_method)'
TREE += ['$compiled_read(S,porigin_class) = eps', '$compiled_read(S,porigin_name) = eps',
         '$pool_value(S.POOLS,porigin_class) = eps', '$pool_value(S.POOLS,porigin_name) = eps',
         '$code_at(S.CODE,n_site) = (pcode_selectors)',
         '$code_expression(pcode_selectors.EXPRESSIONS,pcpath_site ++ [PCFIELD 0]) = ((z_class,false))',
         '$code_expression(pcode_selectors.EXPRESSIONS,pcpath_site ++ [PCFIELD 1]) = ((z_method,false))',
         '$property_magic_cv_raw_ternary_boolean_not_concat_tree(eps,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_ternary_boolean_not_concat_tree(eps,porigin_name,expression_method) = eps',
         '$property_magic_cv_raw_boolean_not_concat_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_boolean_not_concat_tree(S.SOURCES,porigin_name,expression_method) = eps',
         'S_trim = S[.POOLS = [{UNIT n_site,CONSTANTS eps}]]',
         '$property_magic_cv_static_method_site_selector(S_trim,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)',
         '$property_magic_cv_static_method_site_name(S_trim,porigin_site,phpType20_method,pmethoddesc_method.NAME)']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)'] + TREE
    false, true, null = (('keyword', 'false', False), ('keyword', 'true', False),
                         ('keyword', 'null', False))
    inherited_class = b'\\qUIETlITERALsELECTORiNHERITEDaSSIGNtARGET'
    leaves = ((('class', (0, 1, 1, 0),
                ('full', ('string', b'00'), null, true), b''),
               ('method', (1, 1, 1, 1, 1),
                ('full', ('string', b'0'), false,
                 ('plus', ('string', b'+0001'), 1)), b'1'))
              if index == 0 else
              (('class', (0, 0), ('short', ('string', inherited_class), false), inherited_class),
               ('method', (1, 0, 1),
                ('short', ('not', true), ('full', true, false, null)), b'')))
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
            elif kind in ('full', 'short'):
                condition, bindings = raw(value[1], suffix + '0', relative + (0,))
                data += bindings
                if kind == 'full':
                    selected, bindings = raw(value[2], suffix + '1', relative + (1,))
                    data += bindings
                    fallback_value = value[3]
                else:
                    selected, fallback_value = 'ABSENT', value[2]
                fallback, bindings = raw(fallback_value, suffix + '2', relative + (2,))
                data += bindings
                present = f'({selected})' if kind == 'full' else selected
                node = f'NExprTernary ({condition}) {present} ({fallback}) {metadata}'
                forged_if = ('ABSENT' if kind == 'full' else
                             f'(NExprConstFetch (NName (BYTES "bnVsbA==") {metadata}) {metadata})')
                changed = f'NExprTernary ({condition}) {forged_if} ({fallback}) {metadata}'
            else:
                left, bindings = raw(value[1], suffix + '0', relative + (0,))
                data += bindings
                if kind in ('concat', 'and', 'land', 'or', 'lor', 'xor'):
                    right, bindings = raw(value[2], suffix + '1', relative + (1,))
                    data += bindings
                    constructor = {'concat': 'NExprBinaryOpConcat', 'and': 'NExprBinaryOpBooleanAnd',
                                   'land': 'NExprBinaryOpLogicalAnd', 'or': 'NExprBinaryOpBooleanOr',
                                   'lor': 'NExprBinaryOpLogicalOr', 'xor': 'NExprBinaryOpLogicalXor'}[kind]
                    node = f'{constructor} ({left}) ({right}) {metadata}'
                    changed = f'NExprBinaryOpPlus ({left}) ({right}) {metadata}'
                    if kind != 'concat':
                        boolean = 'true' if value[3] else 'false'
                        data += [f'$property_magic_cv_raw_ternary_boolean_not_concat_tree(S.SOURCES,porigin_text_{suffix},{node}) = ($echo_value(PBOOL {boolean}))']
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

        node, bindings = raw(tree, str(number), ())
        truth = 'false' if joined in (b'', b'0') else 'true'
        result += [f'$origin_child((porigin_site),{source_tree.path(parts)}) = (porigin_not_{number})',
                   f'$origin_node(S.SOURCES,porigin_not_{number}) = ({node})',
                   f'expression_not_{number} = {node}'] + bindings
        result += [f'ptbytes_joined_{number} = $base64("{base64.b64encode(joined).decode()}")',
                   f'$truth_value(S,PBOOL {truth},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$truth_value(S,PSTRING ptbytes_joined_{number},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$property_magic_cv_raw_ternary_boolean_not_concat_tree(S.SOURCES,porigin_not_{number},expression_not_{number}) = (ptbytes_joined_{number})',
                   f'$property_magic_cv_raw_boolean_not_concat_tree(S.SOURCES,porigin_not_{number},expression_not_{number}) = eps',
                   f'$compiled_read(S_trim,porigin_not_{number}) = eps']
        for position, (relative, origin, actual, changed, empty_metadata) in enumerate(nodes):
            for label, forged in (('shape_or_value', changed), ('metadata', empty_metadata), ('missing', None)):
                state = f'S_text_not_{number}_{position}_{label}'
                path = 'pcpath_site ++ ' + source_tree.path(parts + relative)
                occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{path})' if forged is None else
                               f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
                result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                           f'$property_magic_cv_raw_ternary_boolean_not_concat_tree({state}.SOURCES,{root},expression_{side}) = eps',
                           '~' + source_tree.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        origin = 'porigin_class' if side == 'class' else 'porigin_name'
        expression = 'expression_' + side
        for label, value in (('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})'),
                             ('unexpected_exact_pool', f'PSTRING ptbytes_{side}')):
            state = f'S_text_root_{side}_{label}'
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({value})])}}]]',
                       f'$property_magic_cv_emitted_ternary_concat_value({state},{origin},{expression}) = eps',
                       '~' + source_tree.selector(side, state),
                       source_tree.selector('method' if side == 'class' else 'class', state)]
        path = f'pcpath_site ++ [PCFIELD {field}]'
        mutations = (
            ('constant', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) z_{side} true) :: pcode_selectors.EXPRESSIONS]'),
            ('zero_line', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) 0 false) :: pcode_selectors.EXPRESSIONS]'),
            ('negative_line', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) $(-1) false) :: pcode_selectors.EXPRESSIONS]'),
            ('redirect_child', f'pcode_selectors[.REDIRECTS = (CODEREDIRECT ({path}) ({path} ++ [PCFIELD 0]) false) :: pcode_selectors.REDIRECTS]'),
            ('redirect_dangling', f'pcode_selectors[.REDIRECTS = (CODEREDIRECT ({path}) (pcpath_site ++ [PCFIELD 99]) false) :: pcode_selectors.REDIRECTS]'),
            ('effect', f'pcode_selectors[.EXPRESSIONS = (CODEEFFECT ({path})) :: pcode_selectors.EXPRESSIONS]'))
        for label, code in mutations:
            state = f'S_text_code_{side}_{label}'
            result += [f'{state} = S[.CODE = [{code}]]',
                       f'$property_magic_cv_emitted_ternary_concat_value({state},{origin},{expression}) = eps',
                       '~' + source_tree.selector(side, state),
                       source_tree.selector('method' if side == 'class' else 'class', state)]
    result += ['S_text_code_missing = S[.CODE = eps]',
               '$property_magic_cv_emitted_ternary_concat_value(S_text_code_missing,porigin_class,expression_class) = eps',
               '$property_magic_cv_emitted_ternary_concat_value(S_text_code_missing,porigin_name,expression_method) = eps',
               '~' + source_tree.selector('class', 'S_text_code_missing'),
               '~' + source_tree.selector('method', 'S_text_code_missing')]
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
    parents = []
    parent = prior
    while hasattr(parent, 'prior'):
        parents.append(parent)
        parent = parent.prior
    parents.append(parent)
    parents += [renderer, source_tree, source_tree.prior, source_tree.prior.prior,
                base, base.original, base.inherited, base.inherited.prior,
                base.inherited.prior.prior, base.inherited.prior.prior.prior,
                renderer.renderer]
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
