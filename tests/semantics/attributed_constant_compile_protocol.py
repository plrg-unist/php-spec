#!/usr/bin/env python3
"""Checked compiler lines, ordered partial facts and attributed-context boundaries."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker
import source_compiler as compiler
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('attributed_constant_compile')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()
path_term = lambda path: '[' + ','.join('(' + kind + ' ' + str(index) + ')' for kind, index in path) + ']'


def nodes(value, path=()):
    if isinstance(value, dict) and 'node' in value:
        yield value, path
        for index, field in enumerate(value['fields']):
            yield from nodes(field, (*path, ('PCFIELD', index)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from nodes(child, (*path, ('PCINDEX', index)))


def prepare(out):
    cases = json.loads((SOURCE / 'cases.json').read_text())
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []; asts = {}
    selected = ('basic', 'multiline', 'last-invalid', 'first-invalid-reserved', 'reserved-first',
        'import-first', 'folded', 'static-closure', 'new', 'first-class', 'initializer-closure-invalid',
        'attribute-closure-ignored', 'cursor-last-constant', 'cursor-first-constant', 'cursor-reserved', 'cursor-closure',
        'nested-closure-before-invalid', 'nested-invalid-before-closure', 'nested-closure-before-constant',
        'nested-constant-before-closure', 'nonstatic-closure-cursor', 'closure-use-cursor',
        'new-static-cursor', 'new-unknown-before-unpack', 'new-named-then-positional',
        'new-closure-before-unpack', 'array-value-before-key', 'array-value-invalid-before-key',
        'array-value-constant-before-key-closure', 'array-value-closure-before-key-constant',
        'folded-dead-closure', 'cursor-before-nonstatic-closure')
    selected += tuple(name for name, case in cases.items()
        if name.startswith(('qualified-', 'visitor-')) and case['mode'] == 'main')
    try:
        for name in (*selected, 'ordinary-control', 'single-unsupported'):
            case = cases[name]; path = SOURCE / case['source']
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']; asts[name] = parsed['ast']
            fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            tag = name.replace('-', '_'); state = 'P_' + tag
            checks += ['U_' + tag + ' = ' + fixture, state + ' = $ppstart(91,U_' + tag + ','
                + types.byte_expr(str(path)) + ')']
            if name in selected:
                if case.get('diagnostic_class') == 'Error':
                    checks += [state + '.COMPLETION = PPCABRUPT (FATAL $ptascii('
                        + json.dumps(case['message']) + ') ' + str(case['line']) + ')', state + '.DIAGNOSTICS = eps']
                else:
                    checks += ['$pptrace(' + state + ') = [("fatal",$ptascii(' + json.dumps(case['message'])
                        + '),' + types.byte_expr(str(path)) + ',' + str(case['line']) + ')]']
                checks += [state + '.WORK = eps']
            elif name in ('ordinary-control', 'single-unsupported'):
                checks += [state + '.COMPLETION = PPCNORMAL']
            else:
                checks += [state + '.COMPLETION = PPCABRUPT (UNSUPPORTED "ordinary statement compilation")']
        for name, count in [('basic', 2), ('multiline', 2), ('last_invalid', 1), ('first_invalid_reserved', 0),
                ('reserved_first', 0), ('import_first', 0), ('folded', 2)]:
            checks += ['|P_' + name + '.NAMES| = ' + str(count)]
        declaration = 'pcpath_decl'; initializer = 'pcpath_initializer'
        checks += [declaration + ' = ' + path_term((('PCINDEX', 0), ('PCFIELD', 1), ('PCINDEX', 0))),
            initializer + ' = ' + path_term((('PCINDEX', 0), ('PCFIELD', 1), ('PCINDEX', 0), ('PCFIELD', 1))),
            'pcpath_attributes = ' + path_term((('PCINDEX', 0), ('PCFIELD', 0)))]
        for name in ('basic', 'static_closure', 'new', 'first_class'):
            unit = 'P_' + name + '.FOLD.SOURCE'
            checks += ['$ppattributed_constant_declaration_source(' + unit + ',PORIGIN 91 ' + declaration + ')',
                '$ppattributed_constant_initializer(' + unit + ',' + initializer + ')',
                '~$global_constant_declaration_source([' + unit + '],PORIGIN 91 ' + declaration + ')',
                '$global_constant_initializer_root(' + unit + ',' + initializer + ') = eps',
                '~$ppattributed_constant_declaration_source(' + unit + ',PORIGIN 92 ' + declaration + ')',
                '~$ppattributed_constant_initializer(' + unit + ',pcpath_attributes)']
        for name in ('ordinary_control', 'single_unsupported'):
            unit = 'P_' + name + '.FOLD.SOURCE'
            checks += ['~$ppattributed_constant_declaration_source(' + unit + ',PORIGIN 91 ' + declaration + ')',
                '~$ppattributed_constant_initializer(' + unit + ',' + initializer + ')']
        checks += ['$global_constant_declaration_source([P_ordinary_control.FOLD.SOURCE],PORIGIN 91 ' + declaration + ')',
            '$global_constant_declaration_source([P_single_unsupported.FOLD.SOURCE],PORIGIN 91 ' + declaration + ')']
        checks += ['$origin_node([P_visitor_fcc_class_concat.FOLD.SOURCE],PORIGIN 91 '
            + initializer + ') = (NExprStaticCall phpType19_class phpType20_class (SEQUENCE phpType7_class*) metadata_class)',
            '$ppconstant_literal_class(P_ordinary_control,phpType19_class) = $constant_callable_literal_class(phpType19_class)',
            '$ppconstant_callable_class(P_ordinary_control,phpType19_class) = $constant_callable_class_form(phpType19_class)',
            '$ppconstant_callable_invalid_class(P_ordinary_control,phpType19_class) = $constant_callable_invalid_class(phpType19_class)',
            '$origin_node([P_visitor_fcc_method_concat.FOLD.SOURCE],PORIGIN 91 '
            + initializer + ') = (NExprStaticCall phpType19_method phpType20_method (SEQUENCE phpType7_method*) metadata_method)',
            '$ppconstant_method_name(P_ordinary_control,phpType20_method) = $constant_callable_method_name(phpType20_method)']
        for name in ('static-closure', 'attribute-closure-ignored'):
            closure, closure_path = next((node, path) for node, path in nodes(asts[name]['program'])
                if node['node'] == 'Expr_Closure')
            child, child_path = next((node, path) for node, path in nodes(asts[name]['program'])
                if node['node'] in ('Stmt_Return', 'Stmt_Break'))
            unit = 'P_' + name.replace('-', '_') + '.FOLD.SOURCE'
            closure_term = 'pcpath_closure_' + name.replace('-', '_')
            child_term = 'pcpath_child_' + name.replace('-', '_')
            checks += [closure_term + ' = ' + path_term(closure_path), child_term + ' = ' + path_term(child_path),
                '$origin_node([' + unit + '],PORIGIN 91 ' + closure_term + ') = (pcnode_' + name.replace('-', '_') + ')',
                '$default_closure_node(pcnode_' + name.replace('-', '_') + ')',
                '$origin_node([' + unit + '],PORIGIN 91 ' + child_term + ') = (pcnode_child_' + name.replace('-', '_') + ')',
                '~$ppattributed_constant_initializer(' + unit + ',' + child_term + ')']
            if name == 'attribute-closure-ignored':
                checks += ['~$ppattributed_constant_initializer(' + unit + ',' + closure_term + ')',
                    'P_attribute_closure_ignored.CLOSURETEMPLATES = eps']
        for name, start, original in [('missing', None, 'basic'), ('zero', 0, 'basic'), ('negative', -1, 'basic'),
                ('missing_invalid', None, 'first-invalid-reserved')]:
            ast = copy.deepcopy(asts[original]); metadata = ast['program'][0]['fields'][1][0]['meta']
            if start is None: metadata.pop('startLine')
            else: metadata['startLine'] = {'int': str(start)}
            fixture = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture']
            checks += ['U_' + name + ' = ' + fixture,
                'P_' + name + ' = $ppstart(91,U_' + name + ',$ptascii("edited.php"))',
                'P_' + name + '.COMPLETION = PPCABRUPT (UNSUPPORTED "attributed constant declaration location")']
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\n' + compiler.PREFIX
        + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    hashes = json.loads((SOURCE / 'hashes.json').read_text())
    watched = [Path(__file__), *modules, SOURCE / 'cases.json', SOURCE / 'hashes.json', *(SOURCE / name for name in hashes),
        *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'adapter/main.ml',
            'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'bin/php-semantics',
            'vendor/php-parser/lib/PhpParser/ParserAbstract.php', 'vendor/php-parser/lib/PhpParser/Parser/Php8.php',
            '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
            'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/source_compiler.py',
            'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
            and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr']
            and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
