#!/usr/bin/env python3
"""Source-reached release-string carriers and isolated missing-authority controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import startup_float_constants_compiler as runner
import startup_release_string_constants_cases as cases
import static_types as types

ordinary_conditions = runner.conditions


def conditions(program, checked, name, source, baseline):
    assert not baseline
    checks = ordinary_conditions(program, checked, name, source, False)
    checks += ['S = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 91 (' +
               types.byte_expr(str(source)) + ')]], P)', 'S.COMPLETION = NORMAL']
    selected = set()
    for index, statement in enumerate(program['program']):
        for path, node in occurrences.expected(statement, [('INDEX', index)]):
            if node['node'] != 'Expr_ConstFetch':
                continue
            raw_name = node['fields'][0]
            spelling = base64.b64decode(raw_name['fields'][0]['bytes']).decode()
            resolved = cases.ALIASES.get(spelling, spelling)
            if resolved not in cases.VALUES:
                continue
            folded = (name != 'names' or raw_name['node'] == 'Name_FullyQualified'
                      or spelling in cases.ALIASES)
            if name == 'names' and not folded and path[0] == ('INDEX', 0):
                continue
            if name == 'values' and len(path) != 3:
                continue
            if name == 'names' and folded and spelling not in cases.ALIASES:
                continue
            if name == 'boundaries' and statement['node'] != 'Stmt_Const':
                continue
            key = (resolved, 'import' if spelling in cases.ALIASES else folded)
            if key in selected:
                continue
            selected.add(key)
            origin = 'PORIGIN 91 ' + occurrences.path_term(path)
            value = cases.VALUES[resolved]
            carrier = value.replace('PSTRING ', 'PSTRING_CARRIER INTERNED_STRING ', 1)
            checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' +
                       occurrences.node_term(node) + ')']
            if folded:
                checks.append('$pool_value(S.POOLS, ' + origin + ') = (' + value + ')')
                if name == 'boundaries':
                    checks += ['$pfclass_at(P.FOLD.CLASSFACTS, ' +
                               occurrences.path_term(path) + ') = (PVSTRING true)',
                               '$pool_class(S.POOLS, ' + origin + ') = (PVSTRING true)',
                               '$constant_result_class(S, ' + origin + ') = PVSTRING true']
                else:
                    checks.append('$pool_class(S.POOLS, ' + origin + ') = eps')
                if name == 'values':
                    checks += [
                        '$compiled_read(S, ' + origin + ') = (' + value + ')',
                        '$compiled_string_value(S, ' + origin + ', ' + value + ') = ' + carrier,
                        '$compiled_string_value(S[.SOURCES = eps], ' + origin + ', ' + value + ') = ' + value,
                        '$compiled_read(S[.CODE = eps], ' + origin + ') = eps',
                        '$compiled_string_value(S[.CODE = eps], ' + origin + ', ' + value + ') = ' + value,
                        '$compiled_precision(S[.DECLARATIONS = eps], (' + origin + ')) = eps',
                        '$compiled_string_value(S[.DECLARATIONS = eps], ' + origin + ', ' + value + ') = ' + value,
                        '$compiled_string_value(S, ' + origin + ', PSTRING ([88])) = PSTRING ([88])',
                    ]
            else:
                checks += ['$compiled_read(S, ' + origin + ') = eps',
                           '$compiled_name(S, ' + origin + ') = (VALUE (' + carrier + '))',
                           '$constant_result_class(S, ' + origin + ') = PVSTRING true']
            if name == 'values':
                argument = types.byte_expr(resolved)
                checks += ['$constant_lookup_bytes(' + argument + ') = (VALUE (' + carrier + '))',
                           '$constant_name_class(S, ' + argument + ', eps) = PVSTRING true',
                           '$dynamic_global_constant_value(S, ' + argument + ') = (' + carrier + ')',
                           '$string_carrier_valid(S, ' + carrier + ')']
    return checks


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.cases, runner.VALUES, runner.conditions = cases, cases.VALUES, conditions
    passed = runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    report['scope'] = ('Actual source/compiler output supplies raw string pools; constant initializers '
                       'retain PVSTRING true while ordinary/imported pools have no class record. '
                       'Compiled and fallback reads plus runtime APIs retain INTERNED carriers. '
                       'Missing source, read or precision authority and mismatched argument bytes '
                       'do not normalize. Internal pools retain the existing trusted-compiler-output '
                       'boundary; these controls do not authenticate arbitrary forged pool values. '
                       'No native execution or source agreement is added.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
