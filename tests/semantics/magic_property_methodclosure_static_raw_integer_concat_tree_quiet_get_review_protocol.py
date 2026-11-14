#!/usr/bin/env python3
"""Check mixed raw String/Integer trees and exact quiet Empty authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_literal_selector_quiet_get_review_protocol as literal

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_integer_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PREFIX = r'''
dec $rawtree_review_without(pcoccurrence*,pcpath) : pcoccurrence*
def $rawtree_review_without(eps,pcpath) = eps
def $rawtree_review_without((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*,pcpath) = $rawtree_review_without(pcoccurrence*,pcpath)
def $rawtree_review_without((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*,pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $rawtree_review_without(pcoccurrence*,pcpath)
  -- if pcpath_other =/= pcpath
'''


def path(parts):
    return '[' + ','.join('PCFIELD ' + str(part) for part in parts) + ']'


def tree_nodes(shape, parts=()):
    yield parts, shape
    if isinstance(shape, tuple):
        for index, child in enumerate(shape):
            yield from tree_nodes(child, parts + (index,))


def selector(side, state='S', expression=None):
    expression = expression or 'expression_' + side
    if side == 'class':
        return f'$property_magic_cv_static_method_site_selector({state},porigin_site,{expression},porigin_requested,pclassdesc_requested.NAME)'
    return f'$property_magic_cv_static_method_site_name({state},porigin_site,{expression},pmethoddesc_method.NAME)'


def source_state(occurrences):
    return 'S[.SOURCES = [pcunit[.OCCURRENCES = ' + occurrences + ']]]'


def root_pools(side, value=None, extra=()):
    constants = ['PCONSTANT (pcpath_site ++ ' + path((1 if side == 'class' else 0,)) + ') (PSTRING ptbytes_' + ('method' if side == 'class' else 'class') + ')']
    if value is not None:
        constants.append('PCONSTANT (pcpath_site ++ ' + path((0 if side == 'class' else 1,)) + ') (' + value + ')')
    constants.extend(extra)
    return '[{UNIT n_unit,CONSTANTS ([' + ','.join(constants) + '])}]'


def nested_name(side, raw):
    """A complete five-node counterfactual, separate from the original tree."""
    field = 0 if side == 'class' else 1
    text = 'text_requested' if side == 'class' else 'text_selected'
    inner = f'NExprBinaryOpConcat (NScalarString (BYTES {text}) metadata_requested) (NScalarString (BYTES "") metadata_requested) metadata_requested'
    expression = f'NExprBinaryOpConcat (NScalarString (BYTES text_prefix) metadata_requested) ({inner}) metadata_requested'
    nodes = [((), expression),
             ((0,), 'NScalarString (BYTES text_prefix) metadata_requested'),
             ((1,), inner),
             ((1, 0), f'NScalarString (BYTES {text}) metadata_requested'),
             ((1, 1), 'NScalarString (BYTES "") metadata_requested')]
    occurrences = 'pcunit.OCCURRENCES'
    for parts, node in nodes:
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {path((field,) + parts)}) ({node})) :: ({occurrences})'
    site_class = expression if side == 'class' else 'expression_class'
    site_method = expression if side == 'method' else 'expression_method'
    site = f'NExprStaticCall ({site_class}) ({site_method}) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site'
    occurrences = f'(PCOCCURRENCE pcpath_site ({site})) :: ({occurrences})'
    return expression, source_state(occurrences) + '[.POOLS = ' + root_pools(side, 'PSTRING (' + raw + ')') + ']'


def checks(old, index):
    requested = ('\\qUIETmETHODsTATICiNHERITEDcvtARGET12' if index == 0
                 else 'qUIETmETHODsTATICiNHERITEDlITERALtARGET0')
    selected = 'CoUnTeR0' if index == 0 else 'cOunter12'
    result = [f'text_requested = "{base64.b64encode(requested.encode()).decode()}"',
              f'text_selected = "{base64.b64encode(selected.encode()).decode()}"']
    inherited = old[:old.index(literal.SELECTOR[0])]
    for check in inherited:
        if check.startswith('$origin_node(S.SOURCES,porigin_site) = '):
            check = check.replace('NScalarString (BYTES text_requested) metadata_requested',
                                  'NExprBinaryOpConcat expression_class_left expression_class_right metadata_requested')
            check = check.replace('NIdentifier (BYTES text_selected) metadata_selected',
                                  'NExprBinaryOpConcat expression_method_left expression_method_right metadata_selected')
            result += [check,
                       'expression_class = NExprBinaryOpConcat expression_class_left expression_class_right metadata_requested',
                       'expression_method = NExprBinaryOpConcat expression_method_left expression_method_right metadata_selected']
            continue
        if check.startswith('$scoped_requested_site(S,porigin_site,'):
            check = check.replace('NScalarString (BYTES text_requested) metadata_requested', 'expression_class')
        if index == 1:
            check = check.replace('"COUNTER"', '"COUNTER12"').replace('"Q09VTlRFUg=="', '"Q09VTlRFUjEy"')
            check = check.replace('"counter"', '"counter12"').replace('"Y291bnRlcg=="', '"Y291bnRlcjEy"')
        target = 'QuietMethodStaticInheritedCVTarget' if index == 0 else 'QuietMethodStaticInheritedLiteralTarget'
        result.append(check.replace(target, target + ('12' if index == 0 else '0')))
    result += ['$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)',
               'ptbytes_class = $base64(text_requested)', 'ptbytes_method = $base64(text_selected)',
               'S_roots = S[.POOLS = ' + root_pools('class', 'PSTRING ptbytes_class') + ']',
               '$property_magic_cv_static_methodclosure(S_roots,n_closure)',
               '$property_empty_rv_kind(S_roots,S_roots.OBJECTS[n_closure])']
    shapes = (((('s', 's'), ('s', ('s', 'i'))), (('s', 's'), ('s', ('s', 'i')))) if index == 0
              else ((('s', 'i'), ('s', ('s', 's'))), ('s', ('s', ('s', ('s', ('s', 'i')))))))
    for field, (side, shape) in enumerate(zip(('class', 'method'), shapes, strict=True)):
        root = 'porigin_tree_root_' + side
        raw = 'ptbytes_' + side
        result += [f'$origin_child((porigin_site),{path((field,))}) = ({root})',
                   f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{root},expression_{side}) = ({raw})',
                   f'$property_magic_cv_raw_string_tree(S.SOURCES,{root},expression_{side}) = eps',
                   selector(side), selector(side, 'S_roots'),
                   f'$property_magic_cv_raw_integer_string_tree(eps,{root},expression_{side}) = eps']
        for parts, node_shape in tree_nodes(shape):
            suffix = side + ('_' + ''.join(map(str, parts)) if parts else '')
            expression = 'expression_' + side if not parts else 'expression_tree_' + suffix
            metadata = 'metadata_tree_' + suffix
            origin = 'porigin_tree_' + suffix
            node_path = path((field,) + parts)
            if parts:
                result += [f'$origin_child((porigin_site),{node_path}) = ({origin})']
            else:
                result += [f'{origin} = {root}']
            if node_shape == 's':
                node = f'NScalarString (BYTES text_tree_{suffix}) {metadata}'
            elif node_shape == 'i':
                node = f'NScalarInt (INTEGER i_tree_{suffix}) {metadata}'
            else:
                children = ['expression_tree_' + side + '_' + ''.join(map(str, parts + (child,))) for child in range(2)]
                node = 'NExprBinaryOpConcat ' + ' '.join(children) + ' ' + metadata
            result += [f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                       f'{metadata} =/= eps']
            if node_shape == 'i':
                expected = 12 if (side == 'class') == (index == 0) else 0
                result += [f'i_tree_{suffix} = {expected}', f'$long_range(i_tree_{suffix})',
                           f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{origin},{expression}) = ($ptascii("{expected}"))',
                           f'$property_magic_cv_raw_string_tree(S.SOURCES,{origin},{expression}) = eps']
            if parts:
                result.append(f'$compiled_read(S_roots,{origin}) = eps')
            for label, occurrences in (
                ('metadata', f'(PCOCCURRENCE (pcpath_site ++ {node_path}) ({node.removesuffix(metadata)}eps)) :: pcunit.OCCURRENCES'),
                ('missing', f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {node_path})'),
            ):
                state = f'S_tree_{suffix}_{label}'
                result += [f'{state} = ' + source_state(occurrences),
                           f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                           '~' + selector(side, state),
                           f'~$property_magic_cv_static_methodclosure({state},n_closure)']
            if not isinstance(node_shape, tuple):
                state = 'S_tree_' + suffix + '_value'
                forged = (f'NScalarString (BYTES "V1JPTkc=") {metadata}' if node_shape == 's'
                          else f'NScalarInt (INTEGER $(i_tree_{suffix} + 1)) {metadata}')
                result += [f'{state} = ' + source_state(f'(PCOCCURRENCE (pcpath_site ++ {node_path}) ({forged})) :: pcunit.OCCURRENCES'),
                           f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                           '~' + selector(side, state)]
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PINT 17', ()), ('case', 'PSTRING $ptlc(' + raw + ')', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {path((field, 2))}) (PSTRING {raw})',)),
        ):
            state = f'S_root_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + root_pools(side, value, extra) + ']',
                       f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,{root},expression_{side}) = ({raw})',
                       '~' + selector(side, state),
                       selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    empty_path = (1, 0, 1) if index == 0 else (0, 1, 0)
    result += [f'$origin_child((porigin_site),{path(empty_path)}) = (porigin_empty)',
               '$origin_node(S.SOURCES,porigin_empty) = (NScalarString (BYTES "") metadata_empty)',
               'expression_empty = NScalarString (BYTES "") metadata_empty',
               '$property_magic_cv_raw_integer_string_tree(S.SOURCES,porigin_empty,expression_empty) = (eps)',
               '$property_magic_cv_raw_integer_string_tree(eps,porigin_empty,expression_empty) = eps']
    for label, node in (('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_empty'),
                        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_empty'),
                        ('keyword', 'NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_empty) metadata_empty'),
                        ('computed', 'NExprUnaryPlus (NScalarInt (INTEGER 0) metadata_empty) metadata_empty')):
        result += [f'expression_{label} = {node}',
                   f'S_leaf_{label} = ' + source_state(f'(PCOCCURRENCE (pcpath_site ++ {path(empty_path)}) ({node})) :: pcunit.OCCURRENCES'),
                   f'$origin_node(S_leaf_{label}.SOURCES,porigin_empty) = (expression_{label})',
                   f'~$property_magic_cv_raw_string_leaf(expression_{label})',
                   f'$property_magic_cv_raw_integer_string_tree(S_leaf_{label}.SOURCES,porigin_empty,expression_{label}) = eps']
    for label, value, rendered in (('zero', 0, '0'),
                                    ('min', -(2**63), '-9223372036854775808'),
                                    ('max', 2**63 - 1, '9223372036854775807'),
                                    ('below', -(2**63) - 1, None),
                                    ('above', 2**63, None)):
        node = f'NScalarInt (INTEGER $({value})) metadata_empty'
        state = 'S_range_' + label
        result += [f'expression_range_{label} = {node}',
                   f'{state} = ' + source_state(f'(PCOCCURRENCE (pcpath_site ++ {path(empty_path)}) ({node})) :: pcunit.OCCURRENCES'),
                   f'$origin_node({state}.SOURCES,porigin_empty) = (expression_range_{label})',
                   ('' if rendered is not None else '~') + f'$long_range($({value}))',
                   f'$property_magic_cv_raw_string_tree({state}.SOURCES,porigin_empty,expression_range_{label}) = eps',
                   f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,porigin_empty,expression_range_{label}) = ' + (f'($ptascii("{rendered}"))' if rendered is not None else 'eps')]
    for field, side in enumerate(('class', 'method')):
        result += [f'S_bare_{side} = ' + source_state(f'(PCOCCURRENCE (pcpath_site ++ {path((field,))}) (expression_range_zero)) :: pcunit.OCCURRENCES'),
                   '~' + selector(side, 'S_bare_' + side, 'expression_range_zero')]
    if index == 1:
        result += ['$origin_child((porigin_site),[PCFIELD 0,PCFIELD 1]) = (porigin_empty_tree)',
                   '$origin_node(S.SOURCES,porigin_empty_tree) = (expression_empty_tree)',
                   '$property_magic_cv_raw_integer_string_tree(S.SOURCES,porigin_empty_tree,expression_empty_tree) = (eps)']
    result.append('text_prefix = "XA=="')
    expression, state = nested_name('class', '92 :: ptbytes_class')
    result += ['expression_class_slash = ' + expression, 'S_class_slash = ' + state,
               '$property_magic_cv_raw_integer_string_tree(S_class_slash.SOURCES,porigin_tree_root_class,expression_class_slash) = (92 :: ptbytes_class)',
               '$property_magic_cv_raw_string_tree(S_class_slash.SOURCES,porigin_tree_root_class,expression_class_slash) = (92 :: ptbytes_class)',
               ('~' if index == 0 else '') + selector('class', 'S_class_slash', 'expression_class_slash')]
    expression, state = nested_name('method', '92 :: ptbytes_method')
    result += ['expression_method_slash = ' + expression, 'S_method_slash = ' + state,
               '$property_magic_cv_raw_integer_string_tree(S_method_slash.SOURCES,porigin_tree_root_method,expression_method_slash) = (92 :: ptbytes_method)',
               '$property_magic_cv_raw_string_tree(S_method_slash.SOURCES,porigin_tree_root_method,expression_method_slash) = (92 :: ptbytes_method)',
               '~' + selector('method', 'S_method_slash', 'expression_method_slash')]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, literal.CASES.values(), strict=True))}


def render(case, fixture, filename):
    text, assertions = literal.own.prior.prior.literal.render(case, fixture, filename)
    return PREFIX + text, assertions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (literal, literal.own, literal.own.prior, literal.own.prior.prior,
               literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
               literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
               literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=render)
