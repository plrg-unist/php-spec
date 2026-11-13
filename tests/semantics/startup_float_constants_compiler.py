#!/usr/bin/env python3
"""Actual source occurrences distinguish folded primitives from namespace lookup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker
import source_occurrences as occurrences
import startup_float_constants_cases as cases
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
VALUES = {'PHP_FLOAT_DIG': 'PINT 15', 'PHP_FLOAT_EPSILON': 'PFLOAT 4372995238176751616',
          'PHP_FLOAT_MAX': 'PFLOAT 9218868437227405311', 'PHP_FLOAT_MIN': 'PFLOAT 4503599627370496'}


def conditions(program, checked, name, source, baseline):
    aliases = getattr(cases, 'ALIASES', {'EPS': 'PHP_FLOAT_EPSILON'})
    undefined = getattr(cases, 'UNDEFINED', ('php_float_DIG',))
    checks = ['P = $ppstart(91, ' + checked['fixture'] + ', ' + types.byte_expr(str(source)) + ')',
              'P.COMPLETION = PPCNORMAL', '$ppconstants(P) = PPCCONSTANTS (pcpath_value, pvalue)*']
    for index, statement in enumerate(program['program']):
        for path, node in occurrences.expected(statement, [('INDEX', index)]):
            if node['node'] != 'Expr_ConstFetch':
                continue
            raw = node['fields'][0]
            spelling = base64.b64decode(raw['fields'][0]['bytes']).decode()
            if spelling not in VALUES and spelling not in aliases and spelling not in undefined:
                continue
            resolved, fallback = spelling, None
            folded = name != 'names' or raw['node'] == 'Name_FullyQualified'
            if name == 'names' and raw['node'] != 'Name_FullyQualified':
                if spelling in aliases:
                    resolved, folded = aliases[spelling], True
                else:
                    namespace = 'Startup\\Shadow' if path[0] == ('INDEX', 0) else 'Startup\\Fallback'
                    resolved = namespace + '\\' + spelling
                    if raw['node'] != 'Name_Relative':
                        fallback = spelling
                    folded = False
            term = occurrences.path_term(path)
            checks.append('$origin_node([P.FOLD.SOURCE], PORIGIN 91 ' + term + ') = (' + occurrences.node_term(node) + ')')
            if folded and not baseline:
                checks += ['$ppconstant_at((pcpath_value, pvalue)*, ' + term + ') = (' + VALUES[resolved] + ')',
                           '$code_name($compiled_names(P.NAMES), ' + term + ') = eps']
            else:
                checks.append('$ppconstant_at((pcpath_value, pvalue)*, ' + term + ') = eps')
                lookup = '$code_name($compiled_names(P.NAMES), ' + term + ')'
                if fallback is None:
                    checks.append(lookup + ' = ((' + types.byte_expr(resolved) + ', eps))')
                else:
                    suffix = str(len(checks))
                    checks += [lookup + ' = ((preqbytes_resolved_' + suffix + ', preqbytes_fallback_' + suffix + '?))',
                               'preqbytes_resolved_' + suffix + ' = $ptascii(' + json.dumps(resolved) + ')',
                               'preqbytes_fallback_' + suffix + '? = ($ptascii(' + json.dumps(fallback) + '))']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--native-baseline', required=True, type=Path)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = [Path(__file__), Path(cases.__file__), Path(occurrences.__file__), Path(types.__file__),
             ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'spec/semantics/20-machine.watsup',
             ROOT / 'spec/semantics/23-named-constants.watsup', ROOT / 'spec/semantics/46-source-compiler.watsup',
             ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', runner]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(ROOT)): digest(path) for path in paths}
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], args.output / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], args.output / 'adapter')
    functions, counts = [], {}
    try:
        for name in ('values', 'names', 'boundaries'):
            source = args.native_baseline / name / 'source.php'
            assert source.read_bytes() == cases.CASES[name]
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            checks = conditions(parsed['ast'], checked, name, source, args.baseline)
            counts[name] = len(checks)
            functions.append('dec $' + name + '() : bool\ndef $' + name + '() = true\n' +
                             ''.join('  -- if ' + check + '\n' for check in checks))
    finally:
        frontend.close()
        adapter.close()
    fixture = args.output / 'compiler.watsup'
    fixture.write_text('\n'.join(functions) + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if $' + name + '()\n' for name in counts))
    result = recorded([str(runner), *(['--sl'] if args.sl else []), *modules, str(fixture)], args.output / 'compiler', 90)
    passed = (result['exit'] == 0 and not result['timeout'] and result['interruption'] is None
              and (args.output / 'compiler.stdout').read_bytes() == b'true\n'
              and not (args.output / 'compiler.stderr').read_bytes())
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in paths}
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'inputs': before, 'mode': 'fixture-SL' if args.sl else 'AL', 'source_credit': 0,
              'baseline': args.baseline, 'assertions': counts, 'run': result, 'passed': passed}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['mode'], counts, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
