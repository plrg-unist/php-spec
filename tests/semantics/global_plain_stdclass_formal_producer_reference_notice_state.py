#!/usr/bin/env python3
"""Ground bare global stdClass FORMAL authority before private Notice admission."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_fqn_stdclass_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_stdclass_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('SingletonFqnStdClass77\\\\make', 'make').replace('MultiFqnStdClass77\\\\make', 'make').replace('SingletonFqnStdClass77\\\\take', 'take').replace('MultiFqnStdClass77\\\\take', 'take')
PREFIX += r'''
dec $pfn_receive_ready(pstate, nat) : bool
def $pfn_receive_ready(S, n) = true
  -- if S.TODO = [TYPE_RECEIVE porigin n]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("make")
def $pfn_receive_ready(S, n) = false -- otherwise
dec $pfn_receive_seek(pstate, nat, nat) : pstate
def $pfn_receive_seek(S, n_stage, n) = S
  -- if $pfn_receive_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $pfn_receive_seek(S, n_stage, n) = $pfn_receive_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$pfn_receive_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $pfn_receive_seek(S, n_stage, n) = S -- otherwise
'''


def front_lines(index, case):
    formal, caller = ('saved', 'x') if index == 0 else ('right', 'y')
    parameter = 'psparam' if index == 0 else 'psparam_last'
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_receive = $pfn_receive_seek(S_initial, ' + str(index) + ', 5000)[.COMPLETION = NORMAL]',
        '$pfn_receive_ready(S_receive, ' + str(index) + ')',
        'S_receive.TODO = [TYPE_RECEIVE porigin_receive ' + str(index) + ']',
        '$receiving_function(S_receive, porigin_receive) = (pfunction_producer)',
        '$typed_receive_valid(S_receive, porigin_receive, ' + str(index) + ')',
        ('' if index == 0 else '~') + '$typed_caller_strict(S_receive)',
        '$lookup(S_receive.ENV, $ptascii(' + json.dumps(formal) + ')) = (n_receive)',
        'S_receive.GLOBALTABLE = (psymboltable_receive)',
        '$lookup(psymboltable_receive.ENV, $ptascii(' + json.dumps(caller) + ')) = (n_caller_receive)',
        '$lookup(psymboltable_receive.ENV, $ptascii("alias")) = (n_caller_receive)',
        'S_receive.STORE[n_receive] = DEFINED (POBJECT n_object_receive)',
        'S_receive.STORE[n_caller_receive] = DEFINED (POBJECT n_object_receive)',
        'n_receive ' + ('=/=' if index == 0 else '=') + ' n_caller_receive',
        'pfunction_producer.SIGNATURE.PARAMETERS = ' + ('[psparam]' if index == 0 else '[psparam, psparam_last]'),
        parameter + '.TYPE = ' + prior.class_type('sTdClAsS'),
        '~$typed_parameter_source(S_receive, ' + parameter + ')',
        '$typed_parameter_conversion(S_receive, ' + parameter + ', POBJECT n_object_receive) = TYPEVALUE (POBJECT n_object_receive)',
        '$parameter_backing_at(S_receive.PARAMETERBACKINGS, n_receive) = eps',
        r'$propref_at(S_receive.PROPREFS, n_receive) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_receive) = eps',
        r'$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)',
        'S_received = $drive(S_receive, 1)[.COMPLETION = NORMAL]',
        r'S_received.STORE = S_receive.STORE /\ S_received.OBJECTPROPS = S_receive.OBJECTPROPS']
    for line in prior.front_lines(index, case):
        if line == 'S_initial.COMPLETION = BUDGET':
            continue
        line = line.replace('$objn_seek(S_initial,', '$objn_seek(S_received,')
        line = line.replace('= ((8, b_last))', '= ((' + str(case['notice_line']) + ', b_last))')
        if line.startswith('$reference_notice_producer_line('):
            line = line.removesuffix('= 8') + '= ' + str(case['notice_line'])
        line = line.replace('SingletonFqnStdClass77\\\\make', 'make').replace('MultiFqnStdClass77\\\\make', 'make')
        if line.startswith('~$reference_notice_producer_header(') or line.startswith('~$reference_notice_producer_arguments('):
            line = '~(' + line[1:] + ')'
        lines.append(line)
    lines += ['pfunction_producer.ENV.NAMESPACE = eps', 'pfunction_producer.ENV.CLASSES = eps',
        'phpType18 = NNameFullyQualified (BYTES text_return) metadata_return',
        '$base64(text_return) = $ptascii(' + json.dumps(case['class_return']) + ')']
    if index == 0:
        lines += ['phpType18_parameter = NName (BYTES text_formal) metadata_formal']
    else:
        lines += ['phpType18_parameter = ABSENT',
            'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NName (BYTES text_formal) metadata_formal) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_parameter_last']
    lines += ['$base64(text_formal) = $ptascii("sTdClAsS")',
        '~($reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE))']
    return lines


def full_lines(index, case):
    return ['$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)'] + [line.replace('perrorcall.LINE = 8', 'perrorcall.LINE = ' + str(case['notice_line'])) for line in prior.full_lines(index, case)]


def controls(index, case):
    raw = 'phpType17' if index == 0 else 'phpType17_last'
    byref = 'false' if index == 0 else 'true'
    variable = 'phpType10' if index == 0 else 'phpType10_last'
    metadata = 'metadata_parameter' if index == 0 else 'metadata_parameter_last'
    parameter = 'psparam' if index == 0 else 'psparam_last'
    shape = 'NParam (SEQUENCE eps) (INTEGER 0) (NName (BYTES text_formal) metadata_formal) (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    view = shape.replace('NName ', 'NNameFullyQualified ', 1)
    sequence = 'SEQUENCE ([phpType17])' if index == 0 else 'SEQUENCE ([phpType17, phpType17_last])'
    signature = 'pfunction_producer.SIGNATURE'
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, ' + sequence + ', phpType18, ' + signature + ')'
    proof = lambda changed: scoped.replace(sequence, sequence.replace(raw, '(' + changed + ')'), 1)
    lines = ['$reference_notice_producer_global_parameter_view(' + raw + ') = (' + view + ')',
        '$reference_notice_producer_global_parameter_view(' + view + ') = (' + view + ')',
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]],', 1),
        scoped.replace('phpType6_producer,', 'SEQUENCE eps,', 1),
        proof(view),
        scoped.replace('phpType18,', 'NName (BYTES text_return) metadata_return,', 1)]
    for class_first in (True, False):
        members = ['NName (BYTES text_return) metadata_return', 'NIdentifier (BYTES "bnVsbA==") metadata_return']
        branches = ['(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(case['class_return']) + '))]))', '(PTBRANCH ([PTBUILTIN "null"]))']
        if not class_first:
            members.reverse()
            branches.reverse()
        changed = scoped.replace('phpType18,', 'NUnionType (SEQUENCE ([' + ', '.join(members) + '])) metadata_return,', 1)
        lines.append(changed.replace(signature + ')', signature + '[.RETURNS = [' + ', '.join(branches) + ']])'))
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        encoded = json.dumps(base64.b64encode(spelling.encode()).decode())
        changed = shape.replace('BYTES text_formal', 'BYTES ' + encoded)
        parameters = '[' + parameter + '[.TYPE = ' + prior.class_type(spelling) + ']]'
        if index == 1:
            parameters = '[psparam, ' + parameter + '[.TYPE = ' + prior.class_type(spelling) + ']]'
        valid = proof(changed).replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])')
        lines += [valid, '~' + valid.replace(prior.class_type(spelling), prior.class_type(spelling.swapcase()))]
    for tag in ('NNameRelative', 'NIdentifier'):
        changed = shape.replace('NName ', tag + ' ', 1)
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + proof(changed)]
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00'):
        changed = shape.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()))
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + proof(changed)]
    for typename in ('NNullableType (NName (BYTES text_formal) metadata_formal) metadata_formal',
                     'NUnionType (SEQUENCE ([NName (BYTES text_formal) metadata_formal, NIdentifier (BYTES "bnVsbA==") metadata_formal])) metadata_formal'):
        changed = shape.replace('NName (BYTES text_formal) metadata_formal', typename, 1)
        expected = changed.replace('NName ', 'NNameFullyQualified ', 1)
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + expected + ')', '~' + proof(changed)]
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
                          ('(BOOLEAN ' + byref + ') (BOOLEAN false)', '(BOOLEAN ' + byref + ') (BOOLEAN true)'),
                          (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) '),
                          ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
        changed = shape.replace(before, after, 1)
        changed_view = view.replace(before, after, 1)
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed_view + ')', '~' + proof(changed)]
    for update in ('.BYREF = ' + ('true' if index == 0 else 'false'), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged bare class formal default"'):
        parameters = '[' + parameter + '[' + update + ']]' if index == 0 else '[psparam, ' + parameter + '[' + update + ']]'
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    for strict in ('true', 'false'):
        lines.append('$typed_conversion_at(S_receive, ' + prior.class_type('sTdClAsS') + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)')
        for value in ('PNULL', 'PINT 19', 'PBOOL false', 'PSTRING ($ptascii("17"))'):
            lines.append('$typed_conversion_at(S_receive, ' + prior.class_type('sTdClAsS') + ', ' + value + ', ' + strict + ') = TYPEREJECT')
    for stage in ('receive', 'return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    sources = {}
    for i, case in enumerate(cases):
        row = records[case['id']]
        sources[i] = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in sources:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources[i].read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    reached, derived, specs = [], [], []
    for i, case in enumerate(cases):
        initial = 'S_initial = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
        conditions = [initial] + front_lines(i, case)
        extra = []
        if not args.front:
            conditions = [line for line in conditions if not line.startswith('~($reference_notice_producer_scoped_header(')]
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, case)
            extra = controls(i, case)
        specs.append('dec $scnr_case' + str(i) + '() : bool\ndef $scnr_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scnr_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, fixture, native_path,
        ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / path for path in ('tests/semantics/error_handler_run.py', 'tests/semantics/profile.json',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/validate.py',
        'tests/corpus.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for case in cases:
        row = records[case['id']]
        paths += [Path(row['command'][-1]), Path(row['stdout']), Path(row['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'module_count': len(modules), 'mode': 'fixture-SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-stdclass-formal-front' if args.front else 'global-plain-stdclass-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
