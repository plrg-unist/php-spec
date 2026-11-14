#!/usr/bin/env python3
"""Ground required nullable formals, weak reception, NULL and private-cell lifetimes."""
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
import multi_cv_scalar_formal_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_nullable_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('MultiCvScalarFormalString57', 'MultiCvNullableFormalString58').replace('MultiCvScalarFormal57', 'MultiCvNullableFormal58')
PREFIX = PREFIX.replace('I;M:1:1:1:1;H:8:0:body;F:29:17:1;R:41:31:37:1:1;P:43:1:1;', 'A;M:17:1:1:1;H:8:0:body;F:29:17:1;R:41:17:31:37:1:1;P:43:17;')
PREFIX = PREFIX.replace('I;M:1:1:1:1;H:8:0:body;F:29:17:1;R:41:31:37:1:1;', 'A;M:17:1:1:1;H:8:0:body;F:29:17:1;R:41:17:31:37:1:1;')


def front_lines(index, case):
    lines = []
    for line in prior.front_lines(index, case):
        if line.startswith('phpType17_first = NParam') or line.startswith('phpType17_last = NParam'):
            for which in ['first', 'last']:
                line = line.replace('(NIdentifier (BYTES text_' + which + '_type) metadata_' + which + '_type)', '(NNullableType (NIdentifier (BYTES text_' + which + '_type) metadata_' + which + '_type) metadata_' + which + '_nullable)')
        if line.startswith('psparam_first.TYPE =') or line.startswith('psparam_last.TYPE ='):
            line = line[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
        if index == 0:
            line = line.replace('STORE[n_snapshot] = DEFINED pvalue_original', 'STORE[n_snapshot] = DEFINED pvalue_snapshot')
            if line == 'pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_original_string) ($ptascii("17"))':
                lines += ['pvalue_original = PARRAY n_root', 'pvalue_snapshot = PSTRING_CARRIER (REQUEST_STRING n_original_string) ($ptascii("17"))']
                continue
            line = line.replace('$string_carrier_valid(S_args, pvalue_original)', '$string_carrier_valid(S_args, pvalue_snapshot)').replace('$string_carrier_valid(S_pre, pvalue_original)', '$string_carrier_valid(S_pre, pvalue_snapshot)')
            line = line.replace('pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', 'pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii("5"))')
            line = line.replace('pvalue_saved = PINT 17', 'pvalue_saved = pvalue_original').replace('pvalue_received_last = PBOOL false', 'pvalue_received_last = PINT 5')
            line = line.replace('psparam_first, pvalue_original) = TYPEINTEGER pvalue_original', 'psparam_first, pvalue_original) = TYPEVALUE pvalue_original').replace('psparam_last, pvalue_y_original) = TYPEBOOL pvalue_y_original', 'psparam_last, pvalue_y_original) = TYPEINTEGER pvalue_y_original')
            line = line.replace('I;M:1:1:1:1;', 'A;M:17:1:1:1;')
        else:
            line = line.replace('pvalue_y_original = PINT 17', 'pvalue_y_original = PNULL').replace('pvalue_received_last = PFLOAT 4625478292286210048', 'pvalue_received_last = PNULL')
            line = line.replace('psparam_last, pvalue_y_original) = TYPEVALUE (PFLOAT 4625478292286210048)', 'psparam_last, pvalue_y_original) = TYPEVALUE PNULL')
        lines.append(line)
    if index == 0:
        lines += ['$lookup(S_args.ENV, $ptascii("copy")) = (n_copy)', 'S_args.STORE[n_copy] = DEFINED (PARRAY n_root)', 'S_args.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_snapshot)]', '$heap_owners(H_args, HARRAY n_root) = 3', '$heap_owners($heap_graph(S_return), HARRAY n_root) = 2', 'S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)', 'S_pre.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS', '$heap_owners($heap_graph(S_pre), HARRAY n_root) = 1']
    return lines


def full_lines(index, case):
    lines = prior.full_lines(index, case)
    if index == 0:
        lines = [line.replace('STORE[n_snapshot] = DEFINED pvalue_original', 'STORE[n_snapshot] = DEFINED pvalue_snapshot').replace('$string_carrier_valid(S_full, pvalue_original)', '$string_carrier_valid(S_full, pvalue_snapshot)') for line in lines]
        lines += ['S_written.STORE[n_copy] = DEFINED (PARRAY n_root)', 'S_written.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS', 'n_written =/= n_root', '$heap_owners($heap_graph(S_written), HARRAY n_root) = 1', 'S_retired.STORE[n_copy] = DEFINED (PARRAY n_root)', '$heap_owners($heap_graph(S_retired), HARRAY n_root) = 1', '$lookup(S_full.ENV, $ptascii("copy")) = eps', '~((HCELL n_copy) <- S_full.ALLOCATIONS)', '~((HARRAY n_root) <- S_full.ALLOCATIONS)']
    return lines


def controls(index):
    lines = [line for line in prior.controls(index) if not line.startswith('phpType17_nullable = ') and not ('SEQUENCE ([phpType17_nullable, phpType17_last])' in line)]
    lines += [
        'phpType17_union = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_first_type) metadata_first_type, NIdentifier (BYTES "bnVsbA==") metadata_first_type])) metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_union, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])',
        '~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), psparam_first.TYPE[0]]], psparam_last]])',
        'phpType17_nullable_int = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES "aW50") metadata_first_type) metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_nullable_int, phpType17_int_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]], psparam_last[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]])']
    lines += [
        'phpType17_nullable_string = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES "c3RyaW5n") metadata_first_type) metadata_first_nullable) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
        'phpType17_bool_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "Ym9vbA==") metadata_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter',
        'phpType17_float_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "ZmxvYXQ=") metadata_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_nullable_int, phpType17_bool_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]], psparam_last[.TYPE = [(PTBRANCH ([PTBUILTIN "bool"]))]]]])',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_nullable_string, phpType17_float_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "null"]))]], psparam_last[.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]]]])']
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
        conditions = [initial('S_initial', i)] + front_lines(i, cases[i])
        current_derived = []
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line.startswith('~$reference_notice_producer_arguments(') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, cases[i])
            current_derived = controls(i)
        case_specs.append('dec $mcsf_case' + str(i) + '() : bool\ndef $mcsf_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
        reached += conditions
        derived += current_derived
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $mcsf_case' + str(i) + '()\n' for i in selected))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), CATALOGUE, fixture, *native_paths, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'multi-cv-nullable-formal-producer-front' if args.front else 'multi-cv-nullable-formal-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
