#!/usr/bin/env python3
"""Source-derived ordinary string-constant publication fronts."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

import const_string_sources as sources
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = sources.family.sha

PREFIX = r'''
dec $test_string_bind_front(pstate, preqbytes) : bool
def $test_string_bind_front(S, preqbytes) = true
  -- if S.TODO = (CONSTANT_BIND porigin) :: ptask_tail*
  -- if $constant_declaration(S,porigin) = ((preqbytes,z))
def $test_string_bind_front(S,preqbytes) = false -- otherwise
dec $test_string_bind_seek(pstate, preqbytes, nat) : pstate
def $test_string_bind_seek(S,preqbytes,0) = S
def $test_string_bind_seek(S,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_string_bind_front(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_string_bind_seek(S,preqbytes,n) = $test_string_bind_seek($drive_steps(S[.COMPLETION = NORMAL],1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_string_bind_front(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def fingerprint():
    return dict(sources.family.fingerprint(), **{name: sha(ROOT / name) for name in (
        'tests/semantics/const_string_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py', 'tests/semantics/_build/default/numeric_runner.exe')})


def initial(program, path):
    return '$php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')'


def decision(program, path):
    return PREFIX + r'''
dec $main() : (pvalue, pvalueclass, bool, bool, bool, bool, pcompletion)
def $main() = (pvalue,pvalueclass,$constant_value_class_valid(S,pvalue,pvalueclass),$global_constant_transfer_valid(S,porigin,pvalueclass,S.USERCONSTANTS),$call_descriptors_valid(S),$constant_facts_valid(S,porigin,pconstantcontext.FACTS),S_found.COMPLETION)
  -- if S_initial = ''' + initial(program, path) + r'''
  -- if S_found = $test_string_bind_seek(S_initial,$ptascii("ConstString22\\Literal"),256)
  -- if S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
  -- if S = S_found[.COMPLETION = NORMAL]
  -- if $test_string_bind_front(S,$ptascii("ConstString22\\Literal"))
  -- if S.TODO = (CONSTANT_BIND porigin) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if pvalueclass = $constant_received_class(S,porigin)
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def checks(program, path, name):
    stages = [('ConstString22\\' + key, value, True) for key, value in (
        ('Literal', 'literal'), ('EmptyValue', ''), ('Folded', 'folded'), ('AliasValue', 'literal'))]
    if name == 'request-string-alias':
        stages = [('RequestAlias22', 'request-value', False)]
    values = ['S_initial = ' + initial(program, path), 'S_initial.COMPLETION = BUDGET']
    start = 'S_initial'
    for i, (key, value, interned) in enumerate(stages):
        tag = str(i)
        state, after = 'S_' + tag, 'S_after_' + tag
        origin, context, fact = 'porigin_' + tag, 'pconstantcontext_' + tag, 'pconstantfact_' + tag
        result, row = 'pvalue_' + tag, 'puserconstant_' + tag
        text = '$ptascii(' + json.dumps(value) + ')'
        name_text = '$ptascii(' + json.dumps(key) + ')'
        flag = 'true' if interned else 'false'
        values += [state + '_found = $test_string_bind_seek(' + start + ',' + name_text + ',256)',
            state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$test_string_bind_front(' + state + ',' + name_text + ')',
            state + '.TODO = (CONSTANT_BIND ' + origin + ') :: ptask_' + tag + '*',
            state + '.CONSTCONTEXT = (' + context + ')', state + '.RESULT = KNOWN ' + result,
            '$string_bytes(' + result + ') = (' + text + ')',
            '$string_carrier_valid(' + state + ',' + result + ')',
            '$constant_received_class(' + state + ',' + origin + ') = PVSTRING ' + flag,
            '$constant_value_class_valid(' + state + ',' + result + ',PVSTRING ' + flag + ')',
            '$global_constant_transfer_valid(' + state + ',' + origin + ',PVSTRING ' + flag + ',' + state + '.USERCONSTANTS)',
            '$constant_fact_at(' + context + '.FACTS,$constant_child(' + origin + ',[PCFIELD 1])) = (' + fact + ')',
            fact + '.VALUE = (' + result + ')',
            fact + '.CLASS = PVSTRING ' + ('false' if key.endswith('\\Folded') else flag),
            '$constant_facts_valid(' + state + ',' + origin + ',' + context + '.FACTS)', *public(state)]
        if interned:
            values += [result + ' = PSTRING_CARRIER INTERNED_STRING ' + text]
        else:
            values += [result + ' = PSTRING_CARRIER (REQUEST_STRING n_string) ' + text,
                '$(n_string < |' + state + '.STRINGDATA|)', state + '.STRINGDATA[n_string] = ' + text,
                '$user_constant_at(' + state + '.USERCONSTANTS,$ptascii("RequestSource22")) = (puserconstant_source)',
                'puserconstant_source.VALUE = ' + result, 'puserconstant_source.CLASS = PVSTRING false']
        values += [state + '_zero = $drive_steps(' + state + ',0)',
            state + '_zero = ' + state + '[.COMPLETION = BUDGET]',
            state + '_one = $drive_steps(' + state + ',1)',
            state + '_one = $drive_steps(' + state + '_zero[.COMPLETION = NORMAL],1)',
            state + r'_one.COMPLETION = NORMAL \/ ' + state + '_one.COMPLETION = BUDGET',
            after + ' = ' + state + '_one[.COMPLETION = NORMAL]',
            after + '.USERCONSTANTS = ' + state + '.USERCONSTANTS ++ [' + row + ']',
            row + '.NAME = $user_constant_key(' + name_text + ')', row + '.ORIGIN = ' + origin,
            row + '.VALUE = ' + result, row + '.CLASS = PVSTRING ' + flag,
            after + '.CONSTCONTEXT = eps', after + '.TODO = ptask_' + tag + '*',
            after + '.RESULT = KNOWN PNULL',
            '$dynamic_global_constant_value(' + after + ',' + name_text + ') = (' + result + ')', *public(after)]
        values += [after + '.' + field + ' = ' + state + '.' + field for field in (
            'STRINGDATA', 'STORE', 'ARRAYS', 'ALLOCATIONS', 'EVENTS', 'POOLS', 'SOURCES', 'FILES')]
        if i == 0:
            values += ['pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text,
                '~$constant_value_class_valid(' + state + ',pvalue_bad,PVSTRING ' + flag + ')',
                '$constant_value_class_valid(' + state + ',' + result + ',PVSTRING ' + ('false' if interned else 'true') + ')',
                state + '_bad_fact = ' + state + '[.CONSTCONTEXT = (' + context + '[.FACTS = [' + fact + '[.VALUE = (pvalue_bad)]]])]',
                '~$call_descriptors_valid(' + state + '_bad_fact)',
                state + '_bad_fact_out = $drive(' + state + '_bad_fact,0)',
                state + '_bad_fact_out.COMPLETION = UNSUPPORTED text_bad_fact',
                '~$constant_facts_valid(' + state + ',' + origin + ',[' + fact + '[.CLASS = PVSCALAR]])',
                '~$constant_facts_valid(' + state + ',' + origin + ',[' + fact + '[.ORIGIN = PORIGIN 0 eps]])',
                after + '_bad_value = ' + after + '[.USERCONSTANTS = ' + state + '.USERCONSTANTS ++ [' + row + '[.VALUE = pvalue_bad]]]',
                '~$call_descriptors_valid(' + after + '_bad_value)',
                after + '_bad_out = $drive(' + after + '_bad_value,0)',
                after + '_bad_out.COMPLETION = UNSUPPORTED text_bad_value',
                '~$call_descriptors_valid(' + after + '[.USERCONSTANTS = ' + state + '.USERCONSTANTS ++ [' + row + '[.CLASS = PVSCALAR]]])']
            if not interned:
                values += ['~$constant_value_class_valid(' + state + '[.STRINGDATA[n_string] = $ptascii("different")],' + result + ',PVSTRING false)',
                    '~$constant_facts_valid(' + state + '[.STRINGDATA[n_string] = $ptascii("different")],' + origin + ',' + context + '.FACTS)']
        start = after
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'decision', 'prepare-states', 'check-states'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '-report.json')
    assert not report_path.exists()
    native = json.loads((args.sources / 'native-report.json').read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    states = args.phase.endswith('states')
    names = ['literal-folded-and-alias', 'request-string-alias'] if states else ['literal-folded-and-alias']
    paths = {name: args.sources.resolve() / name / 'main.php' for name in names}
    for name, path in paths.items():
        assert path.read_bytes() == sources.family.CASES[name]
        native_row, = [row for row in native['records'] if row['id'] == name]
        assert native_row['source_sha256'] == sha(path)
    watched = [*paths.values(), args.sources.resolve() / 'native-report.json']
    if args.phase == 'check-states':
        watched += [out / name / item for name in names for item in ('protocol.watsup', 'assertions.json')]
    if args.phase == 'decision':
        watched += [out / 'decision.watsup']
    inputs = lambda: dict(fingerprint(), **{str(p): sha(p) for p in watched})
    before = inputs()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'phase': args.phase, 'revision': head, 'inputs': before,
        'native_report_sha256': sha(args.sources / 'native-report.json'),
        'records': [], 'passed': False}
    try:
        if args.phase.startswith('prepare'):
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                try:
                    for name, path in paths.items():
                        directory = out / name if states else out
                        directory.mkdir(exist_ok=True)
                        parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
                        assert parsed['accepted']
                        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                        (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
                        fixture = directory / ('protocol.watsup' if states else 'decision.watsup')
                        values = checks(checked['fixture'], path, name) if states else []
                        if states:
                            (directory / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
                            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + value + '\n' for value in values))
                        else:
                            fixture.write_text(decision(checked['fixture'], path))
                        report['records'].append({'id': name, 'source': str(path), 'source_sha256': sha(path),
                            'fixture': str(fixture), 'fixture_sha256': sha(fixture), 'assertions': len(values)})
                finally:
                    adapter.close()
            finally:
                frontend.close()
        else:
            preparation = json.loads((out / ('prepare-states-report.json' if states else 'prepare-report.json')).read_bytes())
            assert preparation['passed'] and preparation['inputs_stable'] and preparation['head_stable']
            assert all(before[key] == value for key, value in preparation['inputs'].items())
            assert [row['id'] for row in preparation['records']] == names
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())
            for row in preparation['records']:
                fixture = Path(row['fixture']); assert row['fixture_sha256'] == sha(fixture)
                directory = fixture.parent
                command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / name) for name in modules], str(fixture)]
                record = dict(row); report['records'].append(record)
                record['process'] = recorder.recorded(command, directory / args.phase, 90 if states else 60)
                assert record['process']['exit'] == 0 and not record['process']['timeout']
                assert not record['process']['group_after'] and row['fixture_sha256'] == sha(fixture)
                assert (directory / (args.phase + '.stderr')).read_bytes() == b''
                record['stdout'] = (directory / (args.phase + '.stdout')).read_text()
                if states:
                    assert record['stdout'] == 'true\n'
        report['passed'] = True
    finally:
        report['inputs_stable'] = before == inputs()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']
    print(report_path, flush=True)


if __name__ == '__main__':
    main()
