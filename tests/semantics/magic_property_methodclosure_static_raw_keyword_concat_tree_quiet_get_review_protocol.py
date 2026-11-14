#!/usr/bin/env python3
"""Check keyword tree Name children and exact quiet Empty authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_integer_concat_tree_quiet_get_review_protocol as prior

literal = prior.literal
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def keyword_tree(side, state='S'):
    return (f'$property_magic_cv_raw_keyword_string_tree({state}.SOURCES,'
            f'porigin_tree_root_{side},expression_{side})')


def checks(old, index):
    requested = ('\\qUIETmETHODsTATICiNHERITEDcvtARGET12' if index == 0
                 else 'qUIETmETHODsTATICiNHERITEDlITERALtARGET01')
    selected = 'CoUnTeR01' if index == 0 else 'cOunter12'
    result = [f'text_requested = "{base64.b64encode(requested.encode()).decode()}"',
              f'text_selected = "{base64.b64encode(selected.encode()).decode()}"']
    for check in old[:old.index(literal.SELECTOR[0])]:
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
        suffix = '01' if index == 0 else '12'
        check = check.replace('"COUNTER"', '"COUNTER' + suffix + '"')
        check = check.replace('"Q09VTlRFUg=="', '"' + base64.b64encode(('COUNTER' + suffix).encode()).decode() + '"')
        check = check.replace('"counter"', '"counter' + suffix + '"')
        check = check.replace('"Y291bnRlcg=="', '"' + base64.b64encode(('counter' + suffix).encode()).decode() + '"')
        target = 'QuietMethodStaticInheritedCVTarget' if index == 0 else 'QuietMethodStaticInheritedLiteralTarget'
        result.append(check.replace(target, target + ('12' if index == 0 else '01')))
    result += ['$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)',
               'ptbytes_class = $base64(text_requested)', 'ptbytes_method = $base64(text_selected)',
               'S_roots = S[.POOLS = ' + prior.root_pools('class', 'PSTRING ptbytes_class') + ']',
               '$property_magic_cv_static_methodclosure(S_roots,n_closure)',
               '$property_empty_rv_kind(S_roots,S_roots.OBJECTS[n_closure])']
    shapes = (((('s', 's'), ('s', ('s', (('false', 'null'), 'i')))),
               (('s', 's'), ('s', ('s', ('i', 'true'))))) if index == 0 else
              ((('s', ('i', 'true')), ('s', ('s', 's'))),
               ('s', ('s', ('s', ('s', ('s', ('i', ('false', 'null')))))))))
    for field, (side, shape) in enumerate(zip(('class', 'method'), shapes, strict=True)):
        root = 'porigin_tree_root_' + side
        raw = 'ptbytes_' + side
        result += [f'$origin_child((porigin_site),{prior.path((field,))}) = ({root})',
                   keyword_tree(side) + f' = ({raw})',
                   f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{root},expression_{side}) = eps',
                   f'$property_magic_cv_raw_string_tree(S.SOURCES,{root},expression_{side}) = eps',
                   prior.selector(side), prior.selector(side, 'S_roots'),
                   f'$property_magic_cv_raw_keyword_string_tree(eps,{root},expression_{side}) = eps']
        for parts, node_shape in prior.tree_nodes(shape):
            suffix = side + ('_' + ''.join(map(str, parts)) if parts else '')
            expression = 'expression_' + side if not parts else 'expression_tree_' + suffix
            metadata = 'metadata_tree_' + suffix
            origin = 'porigin_tree_' + suffix
            node_path = prior.path((field,) + parts)
            result.append(f'$origin_child((porigin_site),{node_path}) = ({origin})' if parts else f'{origin} = {root}')
            if node_shape == 's':
                node = f'NScalarString (BYTES text_tree_{suffix}) {metadata}'
            elif node_shape == 'i':
                node = f'NScalarInt (INTEGER i_tree_{suffix}) {metadata}'
            elif node_shape in ('true', 'false', 'null'):
                name = f'NName (BYTES text_tree_{suffix}) metadata_name_{suffix}'
                node = f'NExprConstFetch ({name}) {metadata}'
            else:
                children = ['expression_tree_' + side + '_' + ''.join(map(str, parts + (child,))) for child in range(2)]
                node = 'NExprBinaryOpConcat ' + ' '.join(children) + ' ' + metadata
            result += [f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                       f'{metadata} =/= eps']
            if parts:
                result.append(f'$compiled_read(S_roots,{origin}) = eps')
            changes = [('metadata', f'(PCOCCURRENCE (pcpath_site ++ {node_path}) ({node.removesuffix(metadata)}eps)) :: pcunit.OCCURRENCES'),
                       ('missing', f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {node_path})'),
                       ('type', f'(PCOCCURRENCE (pcpath_site ++ {node_path}) (NScalarFloat (FLOAT "3ff0000000000000") {metadata})) :: pcunit.OCCURRENCES')]
            if node_shape == 's':
                forged = f'NScalarString (BYTES "V1JPTkc=") {metadata}'
                changes.append(('value', f'(PCOCCURRENCE (pcpath_site ++ {node_path}) ({forged})) :: pcunit.OCCURRENCES'))
            elif node_shape == 'i':
                expected = 12 if (side == 'class') == (index == 0) else 0
                result += [f'i_tree_{suffix} = {expected}', f'$long_range(i_tree_{suffix})']
                forged = f'NScalarInt (INTEGER $(i_tree_{suffix} + 1)) {metadata}'
                changes.append(('value', f'(PCOCCURRENCE (pcpath_site ++ {node_path}) ({forged})) :: pcunit.OCCURRENCES'))
            elif node_shape in ('true', 'false', 'null'):
                name_path = prior.path((field,) + parts + (0,))
                name_origin = 'porigin_name_' + suffix
                value = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[node_shape]
                rendered = '($ptascii("1"))' if node_shape == 'true' else '(eps)'
                result += [f'$origin_child(({origin}),[PCFIELD 0]) = ({name_origin})',
                           f'$origin_node(S.SOURCES,{name_origin}) = ({name})',
                           f'metadata_name_{suffix} =/= eps',
                           f'$special_constant($base64(text_tree_{suffix})) = ({value})',
                           f'$property_magic_cv_raw_keyword_string_tree(S.SOURCES,{origin},{expression}) = {rendered}',
                           f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{origin},{expression}) = eps',
                           '~' + prior.selector('class', expression=expression),
                           '~' + prior.selector('method', expression=expression)]
                other = 'false' if node_shape != 'false' else 'null'
                changed_text = base64.b64encode(other.encode()).decode()
                forged = f'NExprConstFetch (NName (BYTES "{changed_text}") metadata_name_{suffix}) {metadata}'
                changes.append(('value', f'(PCOCCURRENCE (pcpath_site ++ {node_path}) ({forged})) :: pcunit.OCCURRENCES'))
                for label, child in (
                    ('name_value', f'NName (BYTES "{changed_text}") metadata_name_{suffix}'),
                    ('name_type', f'NNameFullyQualified (BYTES text_tree_{suffix}) metadata_name_{suffix}'),
                    ('name_metadata', f'NName (BYTES text_tree_{suffix}) eps'),
                ):
                    changes.append((label, f'(PCOCCURRENCE (pcpath_site ++ {name_path}) ({child})) :: pcunit.OCCURRENCES'))
                changes.append(('name_missing', f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {name_path})'))
            for label, occurrences in changes:
                state = f'S_tree_{suffix}_{label}'
                result += [f'{state} = ' + prior.source_state(occurrences),
                           keyword_tree(side, state) + ' = eps',
                           '~' + prior.selector(side, state),
                           f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PINT 17', ()), ('case', 'PSTRING $ptlc(' + raw + ')', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {prior.path((field, 2))}) (PSTRING {raw})',)),
        ):
            state = f'S_root_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + prior.root_pools(side, value, extra) + ']',
                       keyword_tree(side, state) + f' = ({raw})',
                       '~' + prior.selector(side, state),
                       prior.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    leaf_path = prior.path((0, 0, 0))
    result += [f'$origin_child((porigin_site),{leaf_path}) = (porigin_control)',
               'metadata_control = metadata_requested', 'metadata_name_control = metadata_selected']
    for label, node in (
        ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_control'),
        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_control'),
        ('computed', 'NExprUnaryPlus (NScalarInt (INTEGER 0) metadata_control) metadata_control'),
        ('named', 'NExprConstFetch (NName (BYTES "UEhQX0lOVF9NQVg=") metadata_name_control) metadata_control'),
        ('fqn', 'NExprConstFetch (NNameFullyQualified (BYTES "dHJ1ZQ==") metadata_name_control) metadata_control'),
        ('relative', 'NExprConstFetch (NNameRelative (BYTES "dHJ1ZQ==") metadata_name_control) metadata_control'),
    ):
        state = 'S_control_' + label
        result += [f'expression_control_{label} = {node}',
                   f'{state} = ' + prior.source_state(f'(PCOCCURRENCE (pcpath_site ++ {leaf_path}) ({node})) :: pcunit.OCCURRENCES'),
                   f'$property_magic_cv_raw_keyword_string_tree({state}.SOURCES,porigin_control,expression_control_{label}) = eps',
                   '~' + prior.selector('class', state, 'expression_control_' + label),
                   '~' + prior.selector('method', state, 'expression_control_' + label)]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, literal.CASES.values(), strict=True))}


def render(case, fixture, filename):
    text, assertions = literal.own.prior.prior.literal.render(case, fixture, filename)
    return prior.PREFIX + text, assertions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (prior, literal, literal.own, literal.own.prior, literal.own.prior.prior,
               literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
               literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
               literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=render)
