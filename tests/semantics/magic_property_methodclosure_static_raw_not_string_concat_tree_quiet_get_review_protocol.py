#!/usr/bin/env python3
"""Check decoded String truth and exact raw BooleanNot source authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_not_integer_concat_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_string_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def string_not(sources, origin, expression):
    return f'$property_magic_cv_raw_not_string_tree({sources},{origin},{expression})'


def checks(index):
    inherited = prior.prior.prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_positive_string_tree(',
                           '$property_magic_cv_raw_not_string_tree(')
              for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_not_integer_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    leaves = ((('class', (0, 1, 1, 1, 0, 0), '0'),
               ('class', (0, 1, 1, 1, 0, 1), ''),
               ('method', (1, 1, 1, 1, 1), '00')) if index == 0 else
              (('class', (0, 0, 1, 1), ' 0'),
               ('method', (1, 1, 1, 1, 1, 1, 1, 0), '0'),
               ('method', (1, 1, 1, 1, 1, 1, 1, 1), '')))
    for number, (side, parts, expected) in enumerate(leaves):
        suffix = str(number)
        origin, child_origin = 'porigin_strnot_' + suffix, 'porigin_strnot_child_' + suffix
        metadata, child_metadata = 'metadata_strnot_' + suffix, 'metadata_strnot_child_' + suffix
        text, data, expression = 'text_strnot_' + suffix, 'ptbytes_strnot_' + suffix, 'expression_strnot_' + suffix
        child = f'NScalarString (BYTES {text}) {child_metadata}'
        node = f'NExprBooleanNot ({child}) {metadata}'
        falsey = expected in ('', '0')
        truth, complement = ('false', 'true') if falsey else ('true', 'false')
        output = '1' if falsey else ''
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{child_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
                   f'{data} = $base64({text})', f'{data} = $ptascii("{expected}")',
                   f'~(0 <- {data})',
                   f'$property_magic_cv_raw_string_tree(S.SOURCES,{child_origin},{child}) = ({data})',
                   f'$truth_value(S,PSTRING {data},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$echo_value(PBOOL ({data} = eps \\/ {data} = [48])) = $ptascii("{output}")',
                   f'$echo_value(PBOOL {complement}) = $ptascii("{output}")',
                   string_not('S.SOURCES', origin, expression) + f' = ($ptascii("{output}"))',
                   string_not('eps', origin, expression) + ' = eps',
                   f'$property_magic_cv_raw_not_integer_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{child_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        same_truth = '0' if expected == '' else '' if expected == '0' else 'other'
        forged_text = base64.b64encode(same_truth.encode()).decode()
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprBooleanNot ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryPlus ({child}) {metadata}'),
            ('parent_value', parts, f'NExprBooleanNot (NScalarString (BYTES "{forged_text}") {child_metadata}) {metadata}'),
            ('parent_missing', parts, None),
            ('child_metadata', parts + (0,), f'NScalarString (BYTES {text}) eps'),
            ('child_kind', parts + (0,), 'NScalarInt (INTEGER 0) ' + child_metadata),
            ('child_same_truth', parts + (0,), f'NScalarString (BYTES "{forged_text}") {child_metadata}'),
            ('child_missing', parts + (0,), None),
        ):
            state = f'S_strnot_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       string_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        state = 'S_strnot_wrong_child_' + suffix
        missing = f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(parts + (0,))})'
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(parts + (1,))}) ({child})) :: ({missing})'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   string_not(state + '.SOURCES', origin, expression) + ' = eps',
                   '~' + raw.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_strnot_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       string_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    for number, data in enumerate((b'', b'0', b'00', b'-0', b' 0', b'0.0', b'false', b'foo', b'\xff', b'\0', b'a\0b')):
        encoded = base64.b64encode(data).decode()
        child = f'NScalarString (BYTES "{encoded}") metadata_class'
        node = f'NExprBooleanNot ({child}) metadata_class'
        state, expression = 'S_strnot_truth_' + str(number), 'expression_strnot_truth_' + str(number)
        occurrences = (f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({node})) :: '
                       f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) ({child})) :: pcunit.OCCURRENCES')
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences)]
        result.append(string_not(state + '.SOURCES', 'porigin_tree_root_class', expression) +
                      (' = eps' if b'\0' in data else f' = ($ptascii("{"1" if data in (b"", b"0") else ""}"))'))
        if b'\0' not in data:
            truth = 'false' if data in (b'', b'0') else 'true'
            result.append(f'$truth_value(S,PSTRING $base64("{encoded}"),0) = S[.RESULT = KNOWN (PBOOL {truth})]')
    for label, child, descendants in (
        ('float', 'NScalarFloat (FLOAT "0000000000000000") metadata_class', ()),
        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_class', ()),
        ('nested_not', 'NExprBooleanNot (NScalarString (BYTES "MA==") metadata_class) metadata_class',
         (((0, 0), 'NScalarString (BYTES "MA==") metadata_class'),)),
        ('positive_child', 'NExprUnaryPlus (NScalarString (BYTES "MA==") metadata_class) metadata_class',
         (((0, 0), 'NScalarString (BYTES "MA==") metadata_class'),)),
        ('negative_child', 'NExprUnaryMinus (NScalarString (BYTES "MA==") metadata_class) metadata_class',
         (((0, 0), 'NScalarString (BYTES "MA==") metadata_class'),)),
    ):
        node = f'NExprBooleanNot ({child}) metadata_class'
        state, expression = 'S_control_strnot_' + label, 'expression_control_strnot_' + label
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child), *descendants):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   string_not(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    previous = prior.prior.prior
    literal = previous.prior.prior.prior.prior.literal
    parents = (prior, prior.prior, previous, previous.prior, previous.prior.prior, previous.prior.prior.prior,
               previous.prior.prior.prior.prior, raw, literal, literal.own,
               literal.own.prior, literal.own.prior.prior, literal.inherited,
               literal.inherited.prior, literal.inherited.prior.prior, literal.inherited.prior.prior.prior,
               literal.own.prior.prior.owning, literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=previous.prior.prior.prior.prior.render)
