#!/usr/bin/env python3
"""Check original numeric String UnaryPlus and exact selector authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_positive_keyword_concat_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_positive_string_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def positive(sources, origin, expression):
    return f'$property_magic_cv_raw_positive_string_tree({sources},{origin},{expression})'


def checks(index):
    inherited = prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_positive_keyword_string_tree(',
                           '$property_magic_cv_raw_positive_string_tree(')
              for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_positive_keyword_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    leaves = ((('class', (0, 1, 1, 1, 1), '  +00012 ', 12),
               ('method', (1, 1, 1, 1, 0), '000', 0)) if index == 0 else
              (('class', (0, 0, 1, 0), ' -000 ', 0),
               ('method', (1, 1, 1, 1, 1, 1, 0), '00012', 12)))
    for number, (side, parts, original, expected) in enumerate(leaves):
        suffix = str(number)
        origin, child_origin = 'porigin_positive_' + suffix, 'porigin_string_' + suffix
        metadata, child_metadata = 'metadata_positive_' + suffix, 'metadata_string_' + suffix
        text, data, integer = 'text_string_' + suffix, 'ptbytes_string_' + suffix, 'i_string_' + suffix
        expression = 'expression_positive_' + suffix
        child = f'NScalarString (BYTES {text}) {child_metadata}'
        node = f'NExprUnaryPlus ({child}) {metadata}'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{child_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
                   f'{data} = $base64({text})', f'{data} = $ptascii("{original}")',
                   f'$coerce_number(PSTRING {data}) = COERCED (NINT {integer}) false',
                   f'{integer} = {expected}', f'$long_range({integer})',
                   f'$unary_apply(S,POSITIVE,PSTRING {data},0) = S[.RESULT = KNOWN (PINT {integer})]',
                   positive('S.SOURCES', origin, expression) + f' = ($ntsigned({integer}))',
                   positive('eps', origin, expression) + ' = eps',
                   f'$property_magic_cv_raw_positive_keyword_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$property_magic_cv_raw_positive_keyword_string_tree(S.SOURCES,{child_origin},{child}) = ({data})',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{child_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        same_number = base64.b64encode(str(expected).encode()).decode()
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprUnaryPlus ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryMinus ({child}) {metadata}'),
            ('parent_missing', parts, None),
            ('child_metadata', parts + (0,), f'NScalarString (BYTES {text}) eps'),
            ('child_value', parts + (0,), f'NScalarString (BYTES "{same_number}") {child_metadata}'),
            ('child_kind', parts + (0,), f'NScalarInt (INTEGER {integer}) {child_metadata}'),
            ('child_missing', parts + (0,), None),
        ):
            state = f'S_positive_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       positive(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state),
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
                       raw.selector('method' if side == 'class' else 'class', state)]
    for number, (payload, classification, expected) in enumerate((
        (b'-9223372036854775808', 'integer', -9223372036854775808),
        (b'9223372036854775807', 'integer', 9223372036854775807),
        (b'9223372036854775808', 'float', None),
        (b'-9223372036854775809', 'float', None),
        (b'12.0', 'float', None), (b'1.2e1', 'float', None),
        (b'12tail', 'leading', 12), (b'12\0', 'leading', 12),
        (b'word', 'invalid', None), (b'', 'invalid', None), (b' ', 'invalid', None),
    )):
        encoded = base64.b64encode(payload).decode()
        data = f'$base64("{encoded}")'
        child = f'NScalarString (BYTES "{encoded}") metadata_class'
        node = f'NExprUnaryPlus ({child}) metadata_class'
        state, expression = 'S_string_control_' + str(number), 'expression_string_control_' + str(number)
        occurrences = (f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({node})) :: '
                       f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) ({child})) :: pcunit.OCCURRENCES')
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences)]
        if classification == 'integer':
            integer = f'$({expected})'
            result += [f'$coerce_number(PSTRING {data}) = COERCED (NINT {integer}) false',
                       f'$long_range({integer})',
                       positive(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ($ntsigned({integer}))',
                       f'$unary_apply(S,POSITIVE,PSTRING {data},0) = S[.RESULT = KNOWN (PINT {integer})]']
        else:
            coerced = (f'COERCED (NFLOAT n_string_float_{number}) false' if classification == 'float' else
                       f'COERCED (NINT {expected}) true' if classification == 'leading' else 'BADNUMBER')
            result += [f'$coerce_number(PSTRING {data}) = {coerced}',
                       positive(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for label, operator, child, descendants in (
        ('variable', 'NExprUnaryPlus', 'NExprVariable (BYTES "cGFydA==") metadata_class', ()),
        ('float', 'NExprUnaryPlus', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_class', ()),
        ('nested', 'NExprUnaryPlus', 'NExprUnaryPlus (NScalarString (BYTES "MTI=") metadata_class) metadata_class',
         (((0, 0), 'NScalarString (BYTES "MTI=") metadata_class'),)),
        ('negative', 'NExprUnaryMinus', 'NScalarString (BYTES "MTI=") metadata_class', ()),
    ):
        node = f'{operator} ({child}) metadata_class'
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
    literal = prior.prior.prior.prior.literal
    parents = (prior, prior.prior, prior.prior.prior, prior.prior.prior.prior, raw, literal,
               literal.own, literal.own.prior, literal.own.prior.prior, literal.inherited,
               literal.inherited.prior, literal.inherited.prior.prior, literal.inherited.prior.prior.prior,
               literal.own.prior.prior.owning, literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.prior.render)
