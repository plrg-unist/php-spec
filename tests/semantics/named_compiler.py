#!/usr/bin/env python3
"""Named user-function compiler phases, fixed-name lookup and original source paths."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types
import source_compiler as compiler
import source_context as context
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/named_compiler_cases.json').read_text())


CONTEXTS = {'named-known-reference-reorder': ['$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                   '(PPW)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") metadata_name) '
                                   'expression (BOOLEAN false) (BOOLEAN false) metadata)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                   'P.FUNCTIONS = [pfunction]',
                                   '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("x")) = '
                                   '(0)',
                                   '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("y")) = '
                                   '(1)',
                                   '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("X")) = '
                                   'eps',
                                   '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("z")) = '
                                   'eps'],
 'named-deferred-reference-reorder': ['$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                      '(PPR)',
                                      '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                      '0,PCFIELD 1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") '
                                      'metadata_name) expression (BOOLEAN false) (BOOLEAN false) metadata)',
                                      '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                      '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'known-unknown-undefined-cv': ['$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = (PPR)',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                '1,PCINDEX 0]) = (NArg (NIdentifier (BYTES "eg==") metadata_name) expression '
                                '(BOOLEAN false) (BOOLEAN false) metadata)',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                '1,PCINDEX 0,PCFIELD 1]) = (expression)'],
 'deferred-unknown-undefined-cv': ['$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = '
                                   '(PPR)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 0]) = (NArg (NIdentifier (BYTES "eg==") metadata_name) '
                                   'expression (BOOLEAN false) (BOOLEAN false) metadata)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 0,PCFIELD 1]) = (expression)'],
 'known-duplicate-undefined-cv': ['$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (PPR)',
                                  '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                  '1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") metadata_name) '
                                  'expression (BOOLEAN false) (BOOLEAN false) metadata)',
                                  '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                  '1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'deferred-duplicate-undefined-cv': ['$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                     '(PPR)',
                                     '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                     '0,PCFIELD 1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") '
                                     'metadata_name) expression (BOOLEAN false) (BOOLEAN false) metadata)',
                                     '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                     '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'known-reference-duplicate-undefined-cv': ['$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD '
                                            '1]) = (PPW)',
                                            '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                            '0,PCFIELD 1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") '
                                            'metadata_name) expression (BOOLEAN false) (BOOLEAN false) '
                                            'metadata)',
                                            '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                            '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'deferred-reference-duplicate-undefined-cv': ['$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX '
                                               '1,PCFIELD 1]) = (PPR)',
                                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX '
                                               '2,PCFIELD 0,PCFIELD 1,PCINDEX 1]) = (NArg (NIdentifier '
                                               '(BYTES "eA==") metadata_name) expression (BOOLEAN false) '
                                               '(BOOLEAN false) metadata)',
                                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX '
                                               '2,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'unknown-computed-variable': ['$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = (PPF)',
                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                               '1,PCINDEX 0]) = (NArg (NIdentifier (BYTES "eg==") metadata_name) expression '
                               '(BOOLEAN false) (BOOLEAN false) metadata)',
                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                               '1,PCINDEX 0,PCFIELD 1]) = (expression)'],
 'duplicate-computed-variable': ['$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (PPR)',
                                 '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                                 '1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") metadata_name) '
                                 'expression (BOOLEAN false) (BOOLEAN false) metadata)',
                                 '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                                 '1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'duplicate-reference-computed-variable': ['$ppaccess(P, [PCINDEX 4,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD '
                                           '1]) = (PPW)',
                                           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 4,PCFIELD '
                                           '0,PCFIELD 1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") '
                                           'metadata_name) expression (BOOLEAN false) (BOOLEAN false) '
                                           'metadata)',
                                           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 4,PCFIELD '
                                           '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'named-unknown-dimension-check-first': ['$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) '
                                         '= (PPF)',
                                         '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                         '0,PCFIELD 1,PCINDEX 0]) = (NArg (NIdentifier (BYTES "eg==") '
                                         'metadata_name) expression (BOOLEAN false) (BOOLEAN false) '
                                         'metadata)',
                                         '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                         '0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = (expression)'],
 'named-duplicate-dimension-check-first': ['$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD '
                                           '1]) = (PPR)',
                                           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                           '0,PCFIELD 1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "eA==") '
                                           'metadata_name) expression (BOOLEAN false) (BOOLEAN false) '
                                           'metadata)',
                                           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                           '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)'],
 'named-variadic-reference-keys': ['$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = '
                                   '(PPR)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 0]) = (NArg (NIdentifier (BYTES "Yg==") metadata_name_0) '
                                   'expression_0 (BOOLEAN false) (BOOLEAN false) metadata_0)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 0,PCFIELD 1]) = (expression_0)',
                                   '$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                   '(PPR)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 1]) = (NArg (NIdentifier (BYTES "YQ==") metadata_name_1) '
                                   'expression_1 (BOOLEAN false) (BOOLEAN false) metadata_1)',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD 0,PCFIELD '
                                   '1,PCINDEX 1,PCFIELD 1]) = (expression_1)'],
 'named-variadic-keys': ['P.FUNCTIONS = [pfunction]',
                         '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("x")) = (0)',
                         '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("xs")) = eps',
                         '$fixed_parameter_index(pfunction.SIGNATURE.PARAMETERS, $ptascii("z")) = eps'],
 'named-multiline-fixed-type': ['$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 1,PCFIELD '
                                '0]) = ((6,false))',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD 3,PCINDEX '
                                '0]) = (NParam phpType14 phpType24 phpType18 phpType4_1 phpType4_2 phpType10 '
                                'phpType5 phpType37 metadata)',
                                '$psline(metadata) = 3',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                                '1,PCINDEX 0,PCFIELD 1]) = (expression_0)',
                                '$expression_line(expression_0) = 7',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                                '1,PCINDEX 1,PCFIELD 1]) = (expression_1)',
                                '$expression_line(expression_1) = 8'],
 'named-multiline-tail-type': ['$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 1,PCFIELD '
                               '0]) = ((6,false))',
                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD 3,PCINDEX 1]) '
                               '= (NParam phpType14 phpType24 phpType18 phpType4_1 phpType4_2 phpType10 '
                               'phpType5 phpType37 metadata)',
                               '$psline(metadata) = 4',
                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                               '1,PCINDEX 0,PCFIELD 1]) = (expression_0)',
                               '$expression_line(expression_0) = 7',
                               '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                               '1,PCINDEX 1,PCFIELD 1]) = (expression_1)',
                               '$expression_line(expression_1) = 8'],
 'named-unknown-cv-multiline': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX 1,PCFIELD '
                                '0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = ((4,false))',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 0,PCFIELD '
                                '1,PCINDEX 0,PCFIELD 1]) = (expression)',
                                '$expression_line(expression) = 5',
                                '$ppcall_list_line(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1]) = 4',
                                '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX 1,PCFIELD '
                                '0]) = ((3,false))'],
 'named-deferred-duplicate-cv-multiline': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                           '0,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = ((3,false))',
                                           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD '
                                           '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                           '$expression_line(expression) = 5',
                                           '$ppcall_list_line(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = 3',
                                           '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                           '0,PCFIELD 0]) = ((2,false))'],
 'named-known-fixed-duplicate-cv-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                          '1,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = ((6,false))',
                                          '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                          '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                          '$expression_line(expression) = 6',
                                          '$ppcall_list_line(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1]) = 4',
                                          '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                          '1,PCFIELD 0]) = ((3,false))'],
 'named-known-fixed-undefined-cv-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                          '1,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = ((5,false))',
                                          '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                          '0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = (expression)',
                                          '$expression_line(expression) = 5',
                                          '$ppcall_list_line(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1]) = 4',
                                          '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                          '1,PCFIELD 0]) = ((3,false))'],
 'named-deferred-undefined-cv-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                       '0,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = ((3,false))',
                                       '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD '
                                       '0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = (expression)',
                                       '$expression_line(expression) = 4',
                                       '$ppcall_list_line(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = 3',
                                       '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                       '0,PCFIELD 0]) = ((2,false))'],
 'named-unknown-computed-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX 2,PCFIELD '
                                  '0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = ((6,false))',
                                  '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 0,PCFIELD '
                                  '1,PCINDEX 0,PCFIELD 1]) = (expression)',
                                  '$expression_line(expression) = 6',
                                  '$ppcall_list_line(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1]) = 5',
                                  '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX 2,PCFIELD '
                                  '0]) = ((4,false))'],
 'named-deferred-parenthesized-first-argument-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), '
                                                       '[PCINDEX 0,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) '
                                                       '= ((4,false))',
                                                       '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX '
                                                       '0,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                                       '(expression)',
                                                       '$expression_line(expression) = 7',
                                                       '$ppcall_list_line(P, [PCINDEX 0,PCFIELD 0,PCFIELD '
                                                       '1]) = 4',
                                                       '$code_expression($compiled_operands(P,P.EXPRESSIONS), '
                                                       '[PCINDEX 0,PCFIELD 0]) = ((2,false))'],
 'named-leading-positional-deferred-cv-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), '
                                                '[PCINDEX 0,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                                '((3,false))',
                                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX '
                                                '0,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                                '$expression_line(expression) = 4',
                                                '$ppcall_list_line(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = 3',
                                                '$code_expression($compiled_operands(P,P.EXPRESSIONS), '
                                                '[PCINDEX 0,PCFIELD 0]) = ((2,false))'],
 'positional-deferred-cv-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX 0,PCFIELD '
                                  '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = ((3,false))',
                                  '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD 0,PCFIELD '
                                  '1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                  '$expression_line(expression) = 4',
                                  '$ppcall_list_line(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = 3',
                                  '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX 0,PCFIELD '
                                  '0]) = ((2,false))'],
 'named-known-reference-duplicate-cv-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), '
                                              '[PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = '
                                              '((7,false))',
                                              '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX '
                                              '2,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                              '$expression_line(expression) = 7',
                                              '$ppcall_list_line(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1]) = 5',
                                              '$code_expression($compiled_operands(P,P.EXPRESSIONS), '
                                              '[PCINDEX 2,PCFIELD 0]) = ((4,false))'],
 'named-deferred-header-compile-lines': ['$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                         '0,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = ((3,false))',
                                         '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD '
                                         '0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = (expression)',
                                         '$expression_line(expression) = 4',
                                         '$ppcall_list_line(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = 3',
                                         '$code_expression($compiled_operands(P,P.EXPRESSIONS), [PCINDEX '
                                         '0,PCFIELD 0]) = ((2,false))'],
 'named-deferred-cv-typed-return-line': ['P.FUNCTIONS = [pfunction_r,pfunction_f]',
                                         '$code_expression(pfunction_r.CODE.EXPRESSIONS, [PCINDEX 0,PCFIELD '
                                         '5,PCINDEX 1]) = ((5,false))',
                                         '$code_expression(pfunction_r.CODE.EXPRESSIONS, [PCINDEX 0,PCFIELD '
                                         '5,PCINDEX 1,PCFIELD 0]) = ((4,false))',
                                         '$code_expression(pfunction_r.CODE.EXPRESSIONS, [PCINDEX 0,PCFIELD '
                                         '5,PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = '
                                         '((5,false))',
                                         '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD '
                                         '5,PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) = '
                                         '(expression)',
                                         '$expression_line(expression) = 6']}

PENDING = {'unpack-then-named-mapping-dependency': 'named, unpacked or reference call argument compilation', 'reference-cv-computed-catch-cell-projection': 'ordinary statement compilation'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/named_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='named-compiler-', dir=ROOT / '.tools'))
    print(out, flush=True)

    def run(command, label):
        (out / (label + '.command.json')).write_text(json.dumps(command) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, env=types.ENV, timeout=60)
        except subprocess.TimeoutExpired as error:
            (out / (label + '.stdout')).write_bytes(error.stdout or b'')
            (out / (label + '.stderr')).write_bytes(error.stderr or b'')
            (out / (label + '.status.json')).write_text(json.dumps({'status': 'timeout'}))
            raise
        (out / (label + '.stdout')).write_bytes(result.stdout)
        (out / (label + '.stderr')).write_bytes(result.stderr)
        (out / (label + '.status.json')).write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
        return result

    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend-wire')
    adapter = Worker([str(adapter_path), str(ROOT)], out / 'adapter-wire')
    records, assertions = [], []
    try:
        for index, (name, source) in enumerate(CASES.items()):
            file = out / (name + '.php')
            file.write_bytes(source.encode())
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            native = run([str(types.PHP), '-n', *types.FLAGS, '-l', str(file)], name)
            assert native.returncode in (0, 255), native
            events = context.events(native)
            record = {'name': name, 'source_base64': base64.b64encode(source.encode()).decode(),
                      'checked': checked, 'lint_exit': native.returncode, 'events': events}
            records.append(record)
            (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
            body = f'  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
            if name in PENDING:
                body += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(PENDING[name])+')\n'
            else:
                body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if name not in PENDING and native.returncode == 0:
                body += '  -- if P.COMPLETION = PPCNORMAL\n  -- if ~P.RETURNREF\n'
                body += ''.join('  -- if '+condition+'\n' for condition in CONTEXTS.get(name, []))
            assertions.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n' + body)
            (out / (name + '.state.watsup')).write_text(f'dec $main() : ppstate\ndef $main() = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n')
        fixture = out / 'compiler.watsup'
        fixture.write_text(compiler.PREFIX + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Named user-function source compile phases, case-sensitive fixed-name lookup and source argument paths/modes; catch and unpack dependencies remain explicit; builtin compilation does not implement builtin execution. Runtime binding and native execution pairing is separate.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/named-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;', len(PENDING), 'explicit pending controls;', sum(map(len, CONTEXTS.values())), 'source projections')


if __name__ == '__main__':
    main()
