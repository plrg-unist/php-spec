#!/usr/bin/env python3
"""Ground builtin object headers, real producer retirement and private Notice ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_object_producer_reference_notice_cases.json')
PREFIX = r'''
dec $objn_output(pevent*) : ptbytes
def $objn_output(eps) = eps
def $objn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $objn_output(pevent*)
dec $objn_ready(pstate, nat) : bool
def $objn_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("SingletonObject76\\make") \/ pcallcontext.NAME = $ptascii("MultiObject76\\make")
def $objn_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget eps 0 eps porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("SingletonObject76\\take") \/ pfunction.NAME = $ptascii("MultiObject76\\take")
def $objn_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("SingletonObject76\\take") \/ pfunction.NAME = $ptascii("MultiObject76\\take")
def $objn_ready(S, n) = false -- otherwise
dec $objn_seek(pstate, nat, nat) : pstate
def $objn_seek(S, n_stage, n) = S
  -- if $objn_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $objn_seek(S, n_stage, n) = $objn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$objn_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $objn_seek(S, n_stage, n) = S -- otherwise
'''


def normalized(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + member + '"]))' for member in members) + ']'


def raw_type(members):
    nodes = ['NIdentifier (BYTES "' + base64.b64encode(member.encode()).decode() + '") metadata_function' for member in members]
    if len(nodes) == 1:
        return nodes[0]
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_function'


def front_lines(index, case):
    namespace = 'SingletonObject76' if index == 0 else 'MultiObject76'
    saved, caller, value = ('saved', 'x', 11) if index == 0 else ('keep', 'y', 5)
    lines = [
        'S_initial.COMPLETION = BUDGET',
        'S_return = $objn_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]',
        '$objn_ready(S_return, 0)',
        'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        'S_return.CURRENT = (pcallcontext_return)',
        '$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii("' + namespace + r'\\make")',
        '~pfunction_producer.SIGNATURE.BYREF',
        'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members']),
        '$lookup(S_return.ENV, $ptascii("' + saved + '")) = (n_saved)',
        'S_return.STORE[n_saved] = DEFINED (POBJECT n_object)',
        '$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN (POBJECT n_object)',
        '$typed_return_task_valid(S_return, z_return)',
        '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, POBJECT n_object, pfunction_producer.CODE.STRICT) = TYPEVALUE (POBJECT n_object)',
        'S_return.FRAMES = [pframe_caller]',
        'pframe_caller.LOCALS = eps',
        r'S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps',
        'S_checked = $typed_return_value(S_return, z_return)',
        r'S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (POBJECT n_object)',
        r'S_checked.STORE = S_return.STORE /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS',
        'S_return_step = $drive(S_return, 1)',
        'S_return_step.COMPLETION = BUDGET',
        'S_after_return = S_return_step[.COMPLETION = NORMAL]',
        'S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*',
        '$task_nodes(RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) = [HOBJECT n_object]',
        r'$heap_valid($heap_graph(S_after_return)) /\ $call_descriptors_valid(S_after_return)',
        'S_pre = $objn_seek(S_after_return, 1, 1536)[.COMPLETION = NORMAL]',
        '$objn_ready(S_pre, 1)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*',
        'S_pre.RESULT = KNOWN (POBJECT n_object)',
        r'S_pre.CURRENT = eps /\ S_pre.FRAMES = eps',
        '~((HCELL n_saved) <- S_pre.ALLOCATIONS)',
        '$lookup(S_pre.ENV, $ptascii("' + saved + '")) = eps',
        '$lookup(S_pre.ENV, $ptascii("' + caller + '")) = (n_caller)',
        '$lookup(S_pre.ENV, $ptascii("alias")) = (n_caller)',
        '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)',
        r'n_copy =/= n_caller /\ n_saved =/= n_caller',
        'S_pre.STORE[n_copy] = DEFINED (POBJECT n_object)',
        'S_pre.OBJECTS[n_object] = STDINSTANCE',
        '$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_pre)',
        'pobjectprops_pre.MATERIALIZED',
        'pobjectprops_pre.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT ' + str(value) + ')))}]',
        '$node_children(S_pre, HOBJECT n_object) = eps',
        '$object_table_at(S_pre.OBJECTTABLES, n_object) = eps',
        '$named_reference_notice_object(S_pre, POBJECT n_object)',
        '$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)',
        'porigin_argument = PORIGIN n_unit pcpath_argument',
        '$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)',
        '$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
        '$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer',
        'phpType6_producer = SEQUENCE phpType7*',
        'phpType7*[' + str(index) + '] = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last',
        '$code_at(S_pre.CODE, n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS, pcpath_argument ++ [PCFIELD 1, PCINDEX ' + str(index) + ', PCFIELD 1]) = ((8, b_last))',
        '$reference_notice_producer_line(S_pre, (porigin_argument), NExprFuncCall phpType19_producer phpType6_producer metadata_producer) = 8',
        '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
        '~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])',
        '~$positional_reference_notice_pending(S_pre)',
        r'$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps',
        r'S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps',
        'H_pre = $heap_graph(S_pre)',
        '$heap_owners(H_pre, HOBJECT n_object) = ' + str(3 if index == 0 else 2),
        '$heap_owners(H_pre, HCELL n_caller) = 2',
        r'$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)']
    if index == 0:
        lines += ['pfunction_producer.CODE.STRICT', 'pfunction_producer.SIGNATURE.PARAMETERS = [psparam]',
            r'~psparam.BYREF /\ psparam.TYPE = ' + normalized(['object']),
            'S_pre.STORE[n_caller] = DEFINED (POBJECT n_object)']
    else:
        lines += ['~pfunction_producer.CODE.STRICT', 'pfunction_producer.SIGNATURE.PARAMETERS = [psparam, psparam_last]',
            r'~psparam.BYREF /\ psparam.TYPE = ' + normalized(case['formal_members'][0]),
            r'psparam_last.BYREF /\ psparam_last.TYPE = ' + normalized(case['formal_members'][1]),
            'S_pre.STORE[n_caller] = DEFINED (PINT 19)']
    lines += ['phpType7* = [phpType7_first]' if index == 0 else 'phpType7* = [phpType7_first, phpType7_last]',
        'phpType16 = SEQUENCE ([phpType17])' if index == 0 else 'phpType16 = SEQUENCE ([phpType17, phpType17_last])',
        'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter']
    return lines


def full_lines(index, case):
    lines = r'''
n_private = |S_pre.STORE|
n_private =/= n_caller /\ n_private =/= n_saved
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
n_private <- S_notice.REFCELLS
$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_valid(H_notice)
S_resume = $objn_seek(S_notice, 2, 1536)[.COMPLETION = NORMAL]
$objn_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (POBJECT n_object)
S_resume.PARAMETERBACKINGS = eps /\ S_resume.PROPREFS = eps /\ S_resume.REFCOERCIONS = eps
$error_call_valid(S_resume, perrorcall)
$heap_valid($heap_graph(S_resume))
S_full = $drive(S_resume, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.FRAMES = eps /\ S_full.CURRENT = eps
S_full.ENV = eps /\ n_private <- S_full.REFCELLS
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HOBJECT n_object) <- S_full.ALLOCATIONS)
~((HCELL n_caller) <- S_full.ALLOCATIONS) /\ ~((HCELL n_copy) <- S_full.ALLOCATIONS)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()
    lines += ['$heap_owners(H_notice, HOBJECT n_object) = ' + str(3 if index == 0 else 2),
        'S_resume.STORE[n_caller] = DEFINED (PINT ' + str(17 if index == 0 else 23) + ')',
        '$objn_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    return lines


def controls(index, case):
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    lines = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    variants = [['object'], ['object', 'null'], ['null', 'object'], ['object', 'int'], ['false', 'object'],
        ['false', 'int', 'object'], ['object', 'int', 'false'], ['true', 'int', 'object'], ['object', 'int', 'true'],
        ['object', 'array', 'int', 'float', 'string', 'null', 'bool'],
        ['null', 'string', 'float', 'int', 'array', 'true', 'object']]
    for members in variants:
        norm, raw = normalized(members), raw_type(members)
        actuals = '([phpType7_first])' if index == 0 else '([phpType7_first, phpType7_last])'
        raw_tail, tail = ('', '') if index == 0 else (', phpType17_last', ', psparam_last')
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        proof = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE ([' + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + norm + ']' + tail + ']])'
        lines += [header + raw + ', ' + signature + '[.RETURNS = ' + norm + '])', proof]
        for strict in ('true', 'false'):
            lines += ['$typed_conversion_at(S_return, ' + norm + ', POBJECT n_object, ' + strict + ') = TYPEVALUE (POBJECT n_object)']
        if len(members) > 1:
            lines += ['~' + header + raw + ', ' + signature + '[.RETURNS = ' + normalized(list(reversed(members))) + '])',
                '~' + header + raw + ', ' + signature + '[.RETURNS = ' + normalized(members[:-1]) + '])']
    for members in [['object', 'object'], ['object', 'mixed'], ['object', 'callable'], ['object', 'void'],
                    ['object', 'never'], ['object', 'false', 'true'], ['object', 'bool', 'false'],
                    ['object', 'array', 'int', 'float', 'string', 'null', 'false', 'true']]:
        lines += ['~' + header + raw_type(members) + ', ' + signature + '[.RETURNS = ' + normalized(members) + '])']
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged object default"'):
        lines += ['~$reference_notice_producer_arguments(phpType6_producer, phpType16, ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']' + ('' if index == 0 else ', psparam_last') + ']])']
    for strict in ('true', 'false'):
        for value in ('PINT 17', 'PBOOL false', 'PSTRING eps', 'PNULL'):
            lines += ['$typed_conversion_at(S_return, ' + normalized(['object']) + ', ' + value + ', ' + strict + ') = TYPEREJECT']
    for stage in ('return', 'notice'):
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
    paths = modules + [runner, Path(__file__), CATALOGUE, fixture, native_path,
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
    print('cv-object-front' if args.front else 'cv-object-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
