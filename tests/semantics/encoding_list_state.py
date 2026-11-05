#!/usr/bin/env python3
"""Checked source compiler prefixes and reached encoding-body scheduling."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

from encoding_declare_protocol import CLI, PREFIX, public
from encoding_list_sources import HASHES, SOURCE
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
FATAL = 'Encoding declaration pragma must be the very first statement in the script'


def prepare(out):
    names = ['lists', 'body', 'nested', 'late-prefix', 'strict', 'order', 'multiline-header', 'multiline-body']
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    units, parsed_asts = {}, {}
    try:
        for name in names:
            path = SOURCE / (name + '.php')
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'], (name, parsed)
            parsed_asts[name] = parsed['ast']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            units[name.replace('-', '_')] = checked['fixture']
    finally:
        adapter.close(); frontend.close()

    lines = CLI['encoding_warning_lines']
    assert lines(parsed_asts['body']) == [2, 3, 3, 4]
    assert lines(parsed_asts['order']) == [3, 5]
    assert lines(parsed_asts['multiline-header']) == [3]
    assert lines(parsed_asts['multiline-body']) == [2]
    for name in ('multiline-header', 'multiline-body'):
        legacy = copy.deepcopy(parsed_asts[name])
        for key in ('declareHeaderCloseLine', 'declareHeaderCloseTokenPos'):
            del legacy['program'][0]['meta'][key]
        assert lines(legacy) is None
    missing = copy.deepcopy(parsed_asts['body'])
    del missing['program'][0]['fields'][0][0]['meta']['startTokenPos']
    assert lines(missing) is None
    duplicate = copy.deepcopy(parsed_asts['body'])
    duplicate['program'][1]['fields'][0][1]['meta']['startTokenPos'] = duplicate['program'][1]['fields'][0][0]['meta']['startTokenPos']
    assert lines(duplicate) is None
    (out / 'cli-controls.json').write_text(json.dumps({'passed': True, 'checks': 8}) + '\n')

    checks = []
    for name, program in units.items():
        file = b64(os.fsencode(SOURCE / (name.replace('_', '-') + '.php')))
        checks += ['U_' + name + ' = ' + program, 'P_' + name + ' = $ppstart(0,U_' + name + ',$base64(' + json.dumps(file) + '))']
    checks += [
        'P_lists.COMPLETION = PPCNORMAL', 'P_lists.ENV.STRICT',
        'P_body.COMPLETION = PPCNORMAL',
        'P_nested.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii(' + json.dumps(FATAL) + ')) 2)',
        'P_late_prefix.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii(' + json.dumps(FATAL) + ')) 4)',
        'P_order.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii(' + json.dumps(FATAL) + ')) 5)',
        'P_strict.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii("strict_types declaration must not use block mode")) 2)',
        'P_multiline_header.COMPLETION = PPCNORMAL',
        'P_multiline_body.COMPLETION = PPCNORMAL']
    prefixes = {
        'lists': [('encoding-disabled', 2, '[PCINDEX 0]'), ('encoding-disabled', 2, '[PCINDEX 0]'),
                  ('encoding-disabled', 3, '[PCINDEX 1]'), ('Foo', 2, '[PCINDEX 0]'), ('Bar', 2, '[PCINDEX 0]')],
        'body': [('encoding-disabled', 2, '[PCINDEX 0]'), ('encoding-disabled', 3, '[PCINDEX 1]'),
                 ('encoding-disabled', 3, '[PCINDEX 1]'), ('encoding-disabled', 4, '[PCINDEX 2]')],
        'nested': [('encoding-disabled', 2, '[PCINDEX 0]'), ('encoding-disabled', 2, '[PCINDEX 0,PCFIELD 1,PCINDEX 0]'),
                   ('Foo', 2, '[PCINDEX 0,PCFIELD 1,PCINDEX 0]')],
        'late_prefix': [('encoding-disabled', 4, '[PCINDEX 2]'), ('encoding-disabled', 4, '[PCINDEX 2]'),
                        ('Foo', 2, '[PCINDEX 0]')],
        'strict': [('encoding-disabled', 2, '[PCINDEX 0]')],
        'multiline_header': [('encoding-disabled', 3, '[PCINDEX 0]')],
        'multiline_body': [('encoding-disabled', 2, '[PCINDEX 0]')],
        'order': [('encoding-disabled', 3, '[PCINDEX 0,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1,PCFIELD 6,PCINDEX 0]'),
                  ('encoding-disabled', 5, '[PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD 5,PCINDEX 0,PCFIELD 6,PCINDEX 0]')],
    }
    for name, records in prefixes.items():
        checks.append('P_' + name + '.DIAGNOSTICS = [' + ','.join('pldiagnostic_' + name + '_' + str(i) for i in range(len(records))) + ']')
        for i, (kind, line, path) in enumerate(records):
            d = 'pldiagnostic_' + name + '_' + str(i); loc = 'pllocation_' + name + '_' + str(i)
            tag, args = ('encoding-disabled', 'eps') if kind == 'encoding-disabled' else ('unknown-declare', '([$ptascii(' + json.dumps(kind) + ')])')
            checks += [d + ' = PLDIAGNOSTIC "warning" ' + json.dumps(tag) + ' ' + args + ' ' + loc,
                loc + '.UNIT = 0', loc + '.PATH = ' + path, loc + '.LINE = ' + str(line),
                loc + '.FILE = P_' + name + '.LOCATION.FILE',
                '$compiler_warning_level(' + json.dumps(tag) + ') = 128']
    checks += [
        'P_body.FOLD.SOURCE.AST = PROGRAM (statement_body_0 :: statement_body_1 :: statement_body_2 :: statement_body_tail*)',
        '$encoding_declare_line(statement_body_0) = (2)',
        '$encoding_declare_line(statement_body_1) = (3)',
        '$encoding_declare_line(statement_body_2) = (4)',
        'P_nested.FOLD.SOURCE.AST = PROGRAM ([statement_outer])',
        'statement_outer = NStmtDeclare (SEQUENCE phpType49_outer*) (SEQUENCE ([statement_inner,statement_echo])) metadata_outer',
        'statement_inner = NStmtDeclare (SEQUENCE phpType49_inner*) ABSENT metadata_inner',
        'phpType49_inner* = [phpType49_foo,phpType49_encoding]',
        'pcpath_inner = [PCINDEX 0,PCFIELD 1,PCINDEX 0]',
        'pcpath_encoding = pcpath_inner ++ [PCFIELD 0,PCINDEX 1]',
        'P_reset = P_nested[.COMPLETION = PPCNORMAL][.DIAGNOSTICS = eps]',
        '$ppencoding_node(P_reset,pcpath_encoding,phpType49_encoding).DIAGNOSTICS = [pldiagnostic_nested_1]',
        'P_bad = P_reset[.FOLD.SOURCE.OCCURRENCES = eps]',
        '$ppencoding_node(P_bad,pcpath_encoding,phpType49_encoding).COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source shape")',
        '$ppencoding_node(P_reset,pcpath_encoding ++ [PCFIELD 1],phpType49_encoding).COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source shape")',
        '$ppencoding_node(P_reset,pcpath_inner ++ [PCFIELD 0,PCINDEX 0],phpType49_encoding).COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source shape")']
    checks += [
        'phpType49_encoding = NDeclareItem phpType11_encoding expression_encoding metadata_encoding',
        'pcnode_missing = NDeclareItem phpType11_encoding expression_encoding eps',
        '$ppencoding_collect(P_reset,[(PCOCCURRENCE pcpath_encoding pcnode_missing)],eps).COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source position")',
        '$ppencoding_collect(P_reset,[(PCOCCURRENCE pcpath_encoding phpType49_encoding),(PCOCCURRENCE pcpath_encoding phpType49_encoding)],eps).COMPLETION = PPCABRUPT (UNSUPPORTED "encoding parser warning source position")']

    file = json.dumps(b64(os.fsencode(SOURCE / 'body.php')))
    checks += ['S_start = $php_run(U_body,0,' + file + ')', 'S_start.COMPLETION = BUDGET']
    previous = 'S_start'
    for i, prefix in enumerate(['', 'B|', 'B|S|']):
        s = 'S_' + str(i); after = s + '_after'
        checks += [s + '_found = $test_encoding_seek(' + previous + ',0,2500)',
            s + '_found.COMPLETION = NORMAL \\/ ' + s + '_found.COMPLETION = BUDGET',
            s + ' = ' + s + '_found[.COMPLETION = NORMAL]',
            s + '.ORIGIN = (PORIGIN 0 ([PCINDEX ' + str(i) + ']))',
            s + '.TODO = (STMT statement_body_' + str(i) + ') :: ptask_' + str(i) + '*',
            'statement_body_' + str(i) + ' = NStmtDeclare (SEQUENCE phpType49_' + str(i) + '*) (SEQUENCE statement_' + str(i) + '*) metadata_' + str(i),
            '$encoding_declare_valid(' + s + ',statement_body_' + str(i) + ')',
            '~$unknown_declare_valid(' + s + ',statement_body_' + str(i) + ')',
            '$test_outputs(' + s + '.EVENTS) = $ptascii(' + json.dumps(prefix) + ')',
            s + '_budget = $drive_steps(' + s + ',0)', s + '_budget = ' + s + '[.COMPLETION = BUDGET]',
            after + '_found = $drive_steps(' + s + '_budget[.COMPLETION = NORMAL],1)',
            after + '_found.COMPLETION = NORMAL \\/ ' + after + '_found.COMPLETION = BUDGET',
            after + ' = ' + after + '_found[.COMPLETION = NORMAL]',
            after + '.TODO = $statement_tasks(statement_' + str(i) + '*,$origin_child(' + s + '.ORIGIN,[PCFIELD 1]),0) ++ ptask_' + str(i) + '*',
            *[after + '.' + field + ' = ' + s + '.' + field for field in
              ('RESULT', 'EVENTS', 'SOURCES', 'DECLARATIONS', 'STORE', 'ARRAYS', 'ALLOCATIONS')],
            *public(s), *public(after)]
        previous = after
    checks += [
        'S_final = $drive_steps(' + previous + ',2500)', 'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        '$test_outputs(S_final.EVENTS) = $ptascii("B|S|C|Z|")', *public('S_final'),
        '~$encoding_declare_valid(S_0[.ORIGIN = eps],statement_body_0)',
        '~$encoding_declare_valid(S_0[.SOURCES = eps],statement_body_0)',
        '~$encoding_declare_valid(S_0[.ORIGIN = (PORIGIN 0 ([PCINDEX 1]))],statement_body_0)',
        '~$encoding_declare_valid(S_0[.ORIGIN = (PORIGIN 1 ([PCINDEX 0]))],statement_body_0)']
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\n' + PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    count = prepare(out)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [Path(__file__), ROOT / 'spec/semantics/92-strict-compiler.watsup',
        ROOT / 'spec/semantics/93-strict-declarations.watsup', ROOT / 'spec/semantics/modules.json',
        ROOT / 'spec/semantics/194-compiler-preflight.watsup',
        ROOT / 'spec/php.watsup', ROOT / 'spec/schema.json',
        ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
        ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/encoding_declare_protocol.py',
        ROOT / 'tests/semantics/encoding_list_sources.py', ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/static_types.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', out / 'protocol.watsup',
        out / 'assertions.json', out / 'cli-controls.json', *(SOURCE / name for name in HASHES)]
    inputs = {str(path): sha(path) for path in watched}
    run = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
    report = {'head': head, 'module_count': len(modules), 'premises': count, 'cli_controls': 8, 'inputs': inputs,
        'process': run, 'stdout': (out / 'check.stdout').read_text(errors='replace'),
        'stderr': (out / 'check.stderr').read_text(errors='replace'),
        'head_stable': head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'inputs_stable': inputs == {str(path): sha(path) for path in watched}}
    report['passed'] = (run['exit'] == 0 and not run['timeout'] and not run['group_after']
        and report['stdout'] == 'true\n' and report['stderr'] == '' and report['head_stable'] and report['inputs_stable'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('pass' if report['passed'] else 'fail', count, flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
