#!/usr/bin/env python3
"""Check raw Integer UnaryPlus source, identity and quiet Empty authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_fqn_keyword_concat_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_positive_integer_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def positive(sources, origin, expression):
    return f'$property_magic_cv_raw_positive_integer_string_tree({sources},{origin},{expression})'


def checks(index):
    inherited = prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_fqn_keyword_string_tree(',
                           '$property_magic_cv_raw_positive_integer_string_tree(')
              for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    leaves = ((('class', (0, 1, 1, 1, 1), 12), ('method', (1, 1, 1, 1, 0), 0)) if index == 0 else
              (('class', (0, 0, 1, 0), 0), ('method', (1, 1, 1, 1, 1, 1, 0), 12)))
    for number, (side, parts, expected) in enumerate(leaves):
        suffix = str(number)
        origin, child_origin = 'porigin_positive_' + suffix, 'porigin_positive_child_' + suffix
        metadata, child_metadata = 'metadata_positive_' + suffix, 'metadata_positive_child_' + suffix
        integer, expression = 'i_positive_' + suffix, 'expression_positive_' + suffix
        child = f'NScalarInt (INTEGER {integer}) {child_metadata}'
        node = f'NExprUnaryPlus ({child}) {metadata}'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{child_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
                   f'{integer} = {expected}', f'$long_range({integer})',
                   f'$coerce_number(PINT {integer}) = COERCED (NINT {integer}) false',
                   f'$unary_apply(S,POSITIVE,PINT {integer},0) = S[.RESULT = KNOWN (PINT {integer})]',
                   positive('S.SOURCES', origin, expression) + f' = ($ntsigned({integer}))',
                   f'$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{child_origin},{child}) = ($ntsigned({integer}))',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{child_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprUnaryPlus ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryMinus ({child}) {metadata}'),
            ('parent_value', parts, f'NExprUnaryPlus (NScalarInt (INTEGER $({integer} + 1)) {child_metadata}) {metadata}'),
            ('parent_missing', parts, None),
            ('child_metadata', parts + (0,), f'NScalarInt (INTEGER {integer}) eps'),
            ('child_value', parts + (0,), f'NScalarInt (INTEGER $({integer} + 1)) {child_metadata}'),
            ('child_kind', parts + (0,), f'NScalarFloat (FLOAT "0000000000000000") {child_metadata}'),
            ('child_missing', parts + (0,), None),
        ):
            state = f'S_positive_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       positive(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        state = 'S_positive_wrong_child_' + suffix
        missing = f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(parts + (0,))})'
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(parts + (1,))}) ({child})) :: ({missing})'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   positive(state + '.SOURCES', origin, expression) + ' = eps',
                   '~' + raw.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_positive_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       positive(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    for number, value in enumerate((-9223372036854775809, -9223372036854775808, -1,
                                    0, 1, 9223372036854775807, 9223372036854775808)):
        integer = f'$({value})'
        child = f'NScalarInt (INTEGER {integer}) metadata_class'
        node = f'NExprUnaryPlus ({child}) metadata_class'
        state, expression = 'S_bound_' + str(number), 'expression_bound_' + str(number)
        occurrences = (f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({node})) :: '
                       f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) ({child})) :: pcunit.OCCURRENCES')
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences)]
        fitting = -9223372036854775808 <= value <= 9223372036854775807
        result.append(positive(state + '.SOURCES', 'porigin_tree_root_class', expression) +
                      (f' = ($ntsigned({integer}))' if fitting else ' = eps'))
        if fitting:
            result += [f'$coerce_number(PINT {integer}) = COERCED (NINT {integer}) false',
                       f'$unary_apply(S,POSITIVE,PINT {integer},0) = S[.RESULT = KNOWN (PINT {integer})]']
    for label, child, descendants in (
        ('string', 'NScalarString (BYTES "MTI=") metadata_class', ()),
        ('float', 'NScalarFloat (FLOAT "0000000000000000") metadata_class', ()),
        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_class', ()),
        ('true', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_class) metadata_class',
         (((0, 0), 'NName (BYTES "dHJ1ZQ==") metadata_class'),)),
        ('null', 'NExprConstFetch (NNameFullyQualified (BYTES "bnVsbA==") metadata_class) metadata_class',
         (((0, 0), 'NNameFullyQualified (BYTES "bnVsbA==") metadata_class'),)),
        ('nested', 'NExprUnaryPlus (NScalarInt (INTEGER 12) metadata_class) metadata_class',
         (((0, 0), 'NScalarInt (INTEGER 12) metadata_class'),)),
        ('negative_child', 'NExprUnaryMinus (NScalarInt (INTEGER 12) metadata_class) metadata_class',
         (((0, 0), 'NScalarInt (INTEGER 12) metadata_class'),)),
    ):
        node = f'NExprUnaryPlus ({child}) metadata_class'
        state, expression = 'S_control_positive_' + label, 'expression_control_positive_' + label
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child), *descendants):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   positive(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    literal = prior.prior.literal
    parents = (prior, prior.prior, raw, literal, literal.own, literal.own.prior, literal.own.prior.prior,
               literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
               literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
               literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.render)
