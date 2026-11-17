#!/usr/bin/env python3
"""Check String truth at authenticated NOT(CONCAT) selector descendants."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_double_not_concat_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_concat_not_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_double_not_tree(',
                     '$property_magic_cv_raw_concat_not_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_double_not_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_double_not_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    leaves = ((('class', (0, 1, 1, 0), (b'0', b'0')),
               ('method', (1, 1, 1, 1, 1), (b'', b''))) if index == 0 else
              (('class', (0, 1, 0, 1), (b'', b'0')),
               ('method', (1, 0, 1), ((b'f', b'a'), b'lse'))))
    for number, (side, parts, tree) in enumerate(leaves):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        nodes = []

        def raw(value, suffix, relative):
            metadata = 'metadata_raw_' + suffix
            if isinstance(value, bytes):
                text = 'text_raw_' + suffix
                node = f'NScalarString (BYTES {text}) {metadata}'
                data = [f'{text} = "{base64.b64encode(value).decode()}"']
                changed = f'NScalarString (BYTES "Y2hhbmdlZA==") {metadata}'
                empty_metadata = f'NScalarString (BYTES {text}) eps'
            else:
                left, left_data = raw(value[0], suffix + '0', relative + (0,))
                right, right_data = raw(value[1], suffix + '1', relative + (1,))
                node = f'NExprBinaryOpConcat ({left}) ({right}) {metadata}'
                data = left_data + right_data
                changed = f'NExprBinaryOpPlus ({left}) ({right}) {metadata}'
                empty_metadata = f'NExprBinaryOpConcat ({left}) ({right}) eps'
            origin = 'porigin_raw_' + suffix
            nodes.append((relative, origin, node, changed, empty_metadata))
            return node, [f'$origin_child((porigin_not_{number}),{source_tree.path(relative)}) = ({origin})',
                          f'$origin_node(S.SOURCES,{origin}) = ({node})',
                          f'{metadata} =/= eps',
                          f'$compiled_read(S_trim,{origin}) = eps'] + data

        child, bindings = raw(tree, str(number), (0,))
        node = f'NExprBooleanNot ({child}) metadata_not_{number}'
        joined = b''.join(tree) if isinstance(tree[0], bytes) else b''.join(tree[0]) + tree[1]
        truth, complement = ('false', 'true') if joined in (b'', b'0') else ('true', 'false')
        result += [f'$origin_child((porigin_site),{source_tree.path(parts)}) = (porigin_not_{number})',
                   f'$origin_node(S.SOURCES,porigin_not_{number}) = ({node})',
                   f'expression_not_{number} = {node}', f'metadata_not_{number} =/= eps'] + bindings
        result += [f'ptbytes_joined_{number} = $base64("{base64.b64encode(joined).decode()}")',
                   f'$property_magic_cv_raw_string_tree(S.SOURCES,porigin_raw_{number},{child}) = (ptbytes_joined_{number})',
                   f'~(0 <- ptbytes_joined_{number})',
                   f'$truth(S,PSTRING ptbytes_joined_{number}) = {truth}',
                   f'$truth_value(S,PSTRING ptbytes_joined_{number},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$property_magic_cv_raw_concat_not_tree(S.SOURCES,porigin_not_{number},expression_not_{number}) = ($echo_value(PBOOL {complement}))',
                   f'$property_magic_cv_raw_double_not_tree(S.SOURCES,porigin_not_{number},expression_not_{number}) = eps',
                   f'$compiled_read(S_trim,porigin_not_{number}) = eps']
        nodes.append(((), f'porigin_not_{number}', node,
                      f'NExprUnaryPlus ({child}) metadata_not_{number}',
                      f'NExprBooleanNot ({child}) eps'))
        for position, (relative, origin, actual, changed, empty_metadata) in enumerate(nodes):
            for label, forged in (('value_or_kind', changed), ('metadata', empty_metadata), ('missing', None)):
                state = f'S_concat_not_{number}_{position}_{label}'
                path = 'pcpath_site ++ ' + source_tree.path(parts + relative)
                occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{path})' if forged is None else
                               f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
                result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                           f'$property_magic_cv_raw_concat_not_tree({state}.SOURCES,{root},expression_{side}) = eps',
                           '~' + source_tree.selector(side, state)]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_concat_not_root_{side}_{label}'
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
               prior.prior.prior.prior.prior.prior.prior,
               renderer, source_tree, source_tree.prior, source_tree.prior.prior,
               base, base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior,
               renderer.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
