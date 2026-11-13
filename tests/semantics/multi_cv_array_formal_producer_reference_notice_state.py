#!/usr/bin/env python3
"""Ground mixed ARRAY formals, exact receive, frame retirement and Notice cancellation."""
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
import multi_cv_array_return_producer_reference_notice_state as array

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_array_formal_producer_reference_notice_cases.json')
PREFIX = array.PREFIX.replace('MultiCvArrayReturn50', 'MultiCvArrayFormal56').replace('MultiCvArrayThrow50', 'MultiCvArrayFormalThrow56')
PREFIX = PREFIX.replace('def $mcar_ready(S, n_stage) = false -- otherwise', r"""
def $mcar_ready(S, 7) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("MultiCvArrayFormal56\\make")
def $mcar_ready(S, 8) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 1) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("MultiCvArrayFormalThrow56\\make")
def $mcar_ready(S, n_stage) = false -- otherwise
""")


def base_lines(index):
    lines = []
    for old in array.BASE:
        if old == 'psparam_first.TYPE = eps /\\ psparam_last.TYPE = eps':
            lines.append('psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\\ psparam_last.TYPE = eps' if index == 0 else 'psparam_first.TYPE = eps /\\ psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]')
        elif old.startswith('$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN)'):
            lines.append(old)
            for which, ref, typed in [('first', False, index == 0), ('last', True, index == 1)]:
                raw_type = '(NIdentifier (BYTES text_parameter_type) metadata_parameter_type)' if typed else 'ABSENT'
                lines.append('phpType17_' + which + ' = NParam (SEQUENCE eps) (INTEGER 0) ' + raw_type + ' (BOOLEAN ' + str(ref).lower() + ') (BOOLEAN false) phpType10_' + which + ' ABSENT (SEQUENCE eps) metadata_parameter_' + which)
            lines.append('$ptlc($base64(text_parameter_type)) = $ptascii("array")')
        elif old == 'S_args.STORE[n_y] = DEFINED (PINT 5)' and index == 1:
            lines += ['S_args.STORE[n_y] = DEFINED (PARRAY n_y_root)', '$lookup(S_args.ENV, $ptascii("yCopy")) = (n_y_copy)', 'S_args.STORE[n_y_copy] = DEFINED (PARRAY n_y_root)', 'S_args.ARRAYS[n_y_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]']
        elif old.startswith('S_return = '):
            stage, parameter, name, value = (7, 0, 'saved', 'n_root') if index == 0 else (8, 1, 'changed', 'n_y_root')
            lines += ['S_receive = $mcar_seek(S_args, ' + str(stage) + ', 5000)[.COMPLETION = NORMAL]', '$mcar_ready(S_receive, ' + str(stage) + ')',
                '$typed_receive_valid(S_receive, pfunction_producer.ORIGIN, ' + str(parameter) + ')', '$lookup(S_receive.ENV, $ptascii(' + json.dumps(name) + ')) = (n_received)',
                'S_receive.STORE[n_received] = DEFINED (PARRAY ' + value + ')', '$typed_parameter_conversion(S_receive, pfunction_producer.SIGNATURE.PARAMETERS[' + str(parameter) + '], PARRAY ' + value + ') = TYPEVALUE (PARRAY ' + value + ')',
                '$mcar_output(S_receive.EVENTS) = $ptascii(' + json.dumps('A;' if index == 0 else 'T;') + ')',
                'S_received_budget = $drive_steps(S_receive, 1)', 'S_received_budget.COMPLETION = BUDGET', 'S_received = S_received_budget[.COMPLETION = NORMAL]', 'S_received.STORE[n_received] = DEFINED (PARRAY ' + value + ')',
                'S_received.ARRAYS = S_receive.ARRAYS', '$heap_valid($heap_graph(S_received)) /\\ $call_descriptors_valid(S_received)',
                old.replace('$mcar_seek(S_args, 1,', '$mcar_seek(S_received, 1,')]
        else:
            lines.append(old)
    return lines


def continue_lines(index):
    return ['~' + line if line.startswith('$reference_notice_producer_arguments(') and '.RETURNS = eps' in line else line for line in array.CONTINUE]


YCOPY = r"""
$heap_owners(H_args, HARRAY n_y_root) = 2
S_pre.STORE[n_y_copy] = DEFINED (PARRAY n_y_root)
S_pre.ARRAYS[n_y_root].ITEMS = S_args.ARRAYS[n_y_root].ITEMS
$heap_owners(H_pre, HARRAY n_y_root) = 1
$node_children(S_pre, HCELL n_y) = eps
""".strip().splitlines()

CONTROLS = r"""
~$typed_return_task_valid(S_return, $(z_return + 1))
~$error_call_valid(S_notice, perrorcall[.LINE = 9])
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
$reference_notice_producer_line(S_pre, (porigin_producer), expression_producer) = 8
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
""".strip().splitlines()

def formal_controls(index):
    which = 'first' if index == 0 else 'last'
    other = 'phpType17_last' if index == 0 else 'phpType17_first'
    ref = 'false' if index == 0 else 'true'
    lines = ['phpType17_scalar = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "aW50") metadata_parameter_type) (BOOLEAN ' + ref + ') (BOOLEAN false) phpType10_' + which + ' ABSENT (SEQUENCE eps) metadata_parameter_' + which]
    raw = '[phpType17_scalar, ' + other + ']' if index == 0 else '[' + other + ', phpType17_scalar]'
    kinds = '[psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]], psparam_last]' if index == 0 else '[psparam_first, psparam_last[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]'
    empty = '[psparam_first[.TYPE = eps], psparam_last]' if index == 0 else '[psparam_first, psparam_last[.TYPE = eps]]'
    lines += ['$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE (' + raw + '), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = ' + kinds + '])',
        '~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = ' + empty + '])']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_paths = [path.resolve() for path in args.native_report]
    natives = [json.loads(path.read_bytes()) for path in native_paths]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {}
    for native in natives:
        for row in native['records']:
            assert row['id'] not in records
            records[row['id']] = row
    selected = [0, 1]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for native in natives:
        assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
        assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
        assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    for i in selected:
        case, record = cases[i], records[cases[i]['id']]
        assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == record['source_sha256']
        assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in selected:
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
    def initial(name, i):
        return name + ' = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
    case_specs = []
    reached = []
    derived = []
    for i in selected:
        conditions = [initial('S_initial', i)] + base_lines(i)
        conditions += array.VERIFY + continue_lines(i) + (array.COPY if i == 0 else array.SOLE)
        conditions += ['$parameter_backing_at(S_pre.PARAMETERBACKINGS, n_y) = eps', '$propref_at(S_pre.PROPREFS, n_y) = eps', '$reference_coercion_at(S_pre.REFCOERCIONS, n_y) = eps']
        if i == 1:
            conditions += YCOPY
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line == '~$positional_reference_notice_pending(S_pre)' or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) else line for line in conditions]
        conditions += ['$mcar_output(S_pre.EVENTS) = $ptascii(' + json.dumps('A;M:17:23:0;' if i == 0 else 'T;M:17:23:0;') + ')']
        current_derived = []
        if not args.front:
            conditions += ['~((HCELL n_original_x) <- S_pre.ALLOCATIONS)', '$heap_owners($heap_graph(S_pre), HCELL n_original_x) = 0']
            conditions += array.PRIVATE
            if i == 0:
                conditions += array.NORMAL
                conditions += ['~$named_reference_notice_array(S_written, PARRAY n_current)']
            else:
                conditions += [line.replace('DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))', 'DEFINED (PINT 11)').replace('S_full.STORE[n_y] = DEFINED (PINT 31)', 'S_full.STORE[n_y] = DEFINED (PINT 43)') for line in array.CANCEL]
                conditions += ['$lookup(S_full.ENV, $ptascii("y")) = eps', '$lookup(S_full.ENV, $ptascii("yCopy")) = eps', '~((HARRAY n_y_root) <- S_full.ALLOCATIONS)', '$heap_owners($heap_graph(S_full), HCELL n_y) = 1']
            conditions += ['$mcar_output(S_full.EVENTS) = $ptascii(' + json.dumps(cases[i]['native_stdout']) + ')']
            current_derived = CONTROLS[:] + formal_controls(i)
        replacements = {'ARG_OWNERS': '3' if i == 0 else '2', 'FORMAL_OWNERS': '2' if i == 0 else '1', 'RETURN_OWNERS': '3' if i == 0 else '2', 'PRE_OWNERS': '2' if i == 0 else '1'}
        for old, new in replacements.items():
            conditions = [line.replace(old, new) for line in conditions]
        case_specs.append('dec $mcaf_case' + str(i) + '() : bool\ndef $mcaf_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
        reached += conditions
        derived += current_derived
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $mcaf_case' + str(i) + '()\n' for i in selected))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(array.__file__), CATALOGUE, fixture, *native_paths, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
    paths += [ROOT / path for path in ('tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for i in selected:
        paths += [sources[i], Path(records[cases[i]['id']]['stdout']), Path(records[cases[i]['id']]['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'multi-cv-array-formal-producer-front' if args.front else 'multi-cv-array-formal-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
