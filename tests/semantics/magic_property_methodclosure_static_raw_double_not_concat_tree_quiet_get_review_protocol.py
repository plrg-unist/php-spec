#!/usr/bin/env python3
"""Check actual nested BooleanNot source, Boolean results and selector authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_not_string_concat_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_double_not_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def double_not(sources, origin, expression):
    return f'$property_magic_cv_raw_double_not_tree({sources},{origin},{expression})'


def checks(index):
    inherited = prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_not_string_tree(',
                           '$property_magic_cv_raw_double_not_tree(')
              for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_not_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    leaves = ((('class', (0, 1, 1, 1, 0, 0), '00'),
               ('class', (0, 1, 1, 1, 0, 1), ' 0'),
               ('method', (1, 1, 1, 1, 1), '0')) if index == 0 else
              (('class', (0, 0, 1, 1), ''),
               ('method', (1, 1, 1, 1, 1, 1, 1, 0), 'false'),
               ('method', (1, 1, 1, 1, 1, 1, 1, 1), '00')))
    for number, (side, parts, expected) in enumerate(leaves):
        suffix = str(number)
        origin = 'porigin_not2_' + suffix
        inner_origin, leaf_origin = 'porigin_not2_inner_' + suffix, 'porigin_not2_leaf_' + suffix
        metadata = 'metadata_not2_' + suffix
        inner_metadata, leaf_metadata = 'metadata_not2_inner_' + suffix, 'metadata_not2_leaf_' + suffix
        text, data = 'text_not2_' + suffix, 'ptbytes_not2_' + suffix
        inner_data, expression = 'ptbytes_not2_inner_' + suffix, 'expression_not2_' + suffix
        leaf = f'NScalarString (BYTES {text}) {leaf_metadata}'
        inner = f'NExprBooleanNot ({leaf}) {inner_metadata}'
        node = f'NExprBooleanNot ({inner}) {metadata}'
        falsey = expected in ('', '0')
        truth, complement = ('false', 'true') if falsey else ('true', 'false')
        output, inner_output = ('', '1') if falsey else ('1', '')
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{inner_metadata} =/= eps', f'{leaf_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({inner_origin})',
                   f'$origin_node(S.SOURCES,{inner_origin}) = ({inner})',
                   f'$origin_child(({inner_origin}),[PCFIELD 0]) = ({leaf_origin})',
                   f'$origin_node(S.SOURCES,{leaf_origin}) = ({leaf})',
                   f'{data} = $base64({text})', f'{data} = $ptascii("{expected}")',
                   f'~(0 <- {data})',
                   f'$property_magic_cv_raw_string_tree(S.SOURCES,{leaf_origin},{leaf}) = ({data})',
                   f'$truth_value(S,PSTRING {data},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$property_magic_cv_raw_not_string_tree(S.SOURCES,{inner_origin},{inner}) = ({inner_data})',
                   f'{inner_data} = $ptascii("{inner_output}")',
                   rf'{inner_data} = eps \/ {inner_data} = [49]',
                   f'$truth_value(S,PBOOL {complement},0) = S[.RESULT = KNOWN (PBOOL {complement})]',
                   f'$echo_value(PBOOL ({inner_data} = eps)) = $ptascii("{output}")',
                   f'$echo_value(PBOOL {truth}) = $ptascii("{output}")',
                   double_not('S.SOURCES', origin, expression) + f' = ($ptascii("{output}"))',
                   double_not('eps', origin, expression) + ' = eps',
                   f'$property_magic_cv_raw_not_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{inner_origin}) = eps',
                   f'$compiled_read(S_roots,{leaf_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        same_truth = '0' if expected == '' else '' if expected == '0' else 'other'
        forged_text = base64.b64encode(same_truth.encode()).decode()
        forged_leaf = f'NScalarString (BYTES "{forged_text}") {leaf_metadata}'
        for label, changed_parts, forged in (
            ('outer_metadata', parts, f'NExprBooleanNot ({inner}) eps'),
            ('outer_kind', parts, f'NExprUnaryPlus ({inner}) {metadata}'),
            ('outer_value', parts, f'NExprBooleanNot (NExprBooleanNot ({forged_leaf}) {inner_metadata}) {metadata}'),
            ('outer_missing', parts, None),
            ('inner_metadata', parts + (0,), f'NExprBooleanNot ({leaf}) eps'),
            ('inner_kind', parts + (0,), f'NExprUnaryPlus ({leaf}) {inner_metadata}'),
            ('inner_value', parts + (0,), f'NExprBooleanNot ({forged_leaf}) {inner_metadata}'),
            ('inner_missing', parts + (0,), None),
            ('leaf_metadata', parts + (0, 0), f'NScalarString (BYTES {text}) eps'),
            ('leaf_kind', parts + (0, 0), 'NScalarInt (INTEGER 0) ' + leaf_metadata),
            ('leaf_same_truth', parts + (0, 0), forged_leaf),
            ('leaf_missing', parts + (0, 0), None),
        ):
            state = f'S_not2_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       double_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        for label, child_parts, child in (('inner', parts + (0,), inner), ('leaf', parts + (0, 0), leaf)):
            state = 'S_not2_wrong_' + label + '_' + suffix
            missing = f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(child_parts)})'
            wrong_parts = child_parts[:-1] + (1,)
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(wrong_parts)}) ({child})) :: ({missing})'
            result += [f'{state} = ' + raw.source_state(occurrences),
                       double_not(state + '.SOURCES', origin, expression) + ' = eps',
                       '~' + raw.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_not2_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       double_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    for number, data in enumerate((b'', b'0', b'00', b'-0', b' 0', b'0.0', b'false', b'foo', b'\xff', b'\0', b'a\0b')):
        encoded = base64.b64encode(data).decode()
        leaf = f'NScalarString (BYTES "{encoded}") metadata_class'
        inner = f'NExprBooleanNot ({leaf}) metadata_class'
        node = f'NExprBooleanNot ({inner}) metadata_class'
        state, expression = 'S_not2_truth_' + str(number), 'expression_not2_truth_' + str(number)
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), inner), ((0, 0), leaf)):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences)]
        result.append(double_not(state + '.SOURCES', 'porigin_tree_root_class', expression) +
                      (' = eps' if b'\0' in data else f' = ($ptascii("{"" if data in (b"", b"0") else "1"}"))'))
        if b'\0' not in data:
            truth = 'false' if data in (b'', b'0') else 'true'
            result.append(f'$truth_value(S,PSTRING $base64("{encoded}"),0) = S[.RESULT = KNOWN (PBOOL {truth})]')
    for label, child, descendants in (
        ('float', 'NScalarFloat (FLOAT "0000000000000000") metadata_class', ()),
        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_class', ()),
        ('triple_not', 'NExprBooleanNot (NScalarString (BYTES "MA==") metadata_class) metadata_class',
         (((0, 0, 0), 'NScalarString (BYTES "MA==") metadata_class'),)),
        ('positive_child', 'NExprUnaryPlus (NScalarString (BYTES "MA==") metadata_class) metadata_class',
         (((0, 0, 0), 'NScalarString (BYTES "MA==") metadata_class'),)),
        ('negative_child', 'NExprUnaryMinus (NScalarString (BYTES "MA==") metadata_class) metadata_class',
         (((0, 0, 0), 'NScalarString (BYTES "MA==") metadata_class'),)),
        ('concat_child', 'NExprBinaryOpConcat (NScalarString (BYTES "MA==") metadata_class) (NScalarString (BYTES "") metadata_class) metadata_class',
         (((0, 0, 0), 'NScalarString (BYTES "MA==") metadata_class'), ((0, 0, 1), 'NScalarString (BYTES "") metadata_class'))),
    ):
        inner = f'NExprBooleanNot ({child}) metadata_class'
        node = f'NExprBooleanNot ({inner}) metadata_class'
        state, expression = 'S_control_not2_' + label, 'expression_control_not2_' + label
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), inner), ((0, 0), child), *descendants):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   double_not(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for label, inner, descendants, expected in (
        ('concat', 'NExprBinaryOpConcat (NScalarString (BYTES "") metadata_class) (NScalarString (BYTES "") metadata_class) metadata_class',
         (((0, 0), 'NScalarString (BYTES "") metadata_class'), ((0, 1), 'NScalarString (BYTES "") metadata_class')), ''),
        ('positive', 'NExprUnaryPlus (NScalarInt (INTEGER 1) metadata_class) metadata_class',
         (((0, 0), 'NScalarInt (INTEGER 1) metadata_class'),), '1'),
    ):
        node = f'NExprBooleanNot ({inner}) metadata_class'
        state, expression = 'S_control_not2_inner_' + label, 'expression_control_not2_inner_' + label
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), inner), *descendants):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = (porigin_not2_control_{label})',
                   f'$property_magic_cv_raw_not_string_tree({state}.SOURCES,porigin_not2_control_{label},{inner}) = ($ptascii("{expected}"))',
                   double_not(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    previous = prior.prior.prior.prior
    literal = previous.prior.prior.prior.prior.literal
    parents = (prior, prior.prior, prior.prior.prior, previous, previous.prior, previous.prior.prior,
               previous.prior.prior.prior, previous.prior.prior.prior.prior, raw, literal, literal.own,
               literal.own.prior, literal.own.prior.prior, literal.inherited,
               literal.inherited.prior, literal.inherited.prior.prior, literal.inherited.prior.prior.prior,
               literal.own.prior.prior.owning, literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=previous.prior.prior.prior.prior.render)
