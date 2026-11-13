#!/usr/bin/env python3
"""Ground ordered scalar/null union verification, strict FLOAT promotion and childless NULL lifetime."""
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
import multi_cv_scalar_return_producer_reference_notice_state as scalar
import multi_cv_nullable_array_return_producer_reference_notice_state as nullable

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_union_scalar_return_producer_reference_notice_cases.json')
PREFIX = scalar.PREFIX.replace('MultiCvFloatReturn51', 'MultiCvUnionFloat55').replace('MultiCvStringReturn51', 'MultiCvUnionString55').replace('A;M:17:23:0;H:8', 'A;M:17:23:0;H:9') + nullable.PREFIX.replace('MultiCvNullableNull52', 'MultiCvUnionNull55')


def scalar_lines(lines, index, cases):
    kind = cases[index]['return_kind']
    line = cases[index]['observed_notice_line']
    order = cases[index]['union_order']
    ordered = '[(PTBRANCH ([PTBUILTIN "' + order[0] + '"])), (PTBRANCH ([PTBUILTIN "' + order[1] + '"]))]'
    result = []
    for original in lines:
        if index == 0 and original.startswith('$string_carrier_valid('):
            continue
        current = original.replace('RETURN_KIND', kind)
        current = current.replace('pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]', 'pfunction_producer.SIGNATURE.RETURNS = ' + ordered)
        if current == 'phpType18_return = NIdentifier (BYTES text_return) metadata_return':
            result += ['phpType18_return = NUnionType (SEQUENCE ([NIdentifier (BYTES text_return_first) metadata_type, NIdentifier (BYTES text_return_last) metadata_last_type])) metadata_return',
                'text_return = ' + ('text_return_last' if order[0] == 'null' else 'text_return_first'),
                '$ptlc($base64(text_return_first)) = $ptascii(' + json.dumps(order[0]) + ') /\\ $ptlc($base64(text_return_last)) = $ptascii(' + json.dumps(order[1]) + ')']
            continue
        if index == 0:
            current = current.replace('pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))', 'pvalue_original = PINT 17')
            current = current.replace('~pfunction_producer.CODE.STRICT', 'pfunction_producer.CODE.STRICT')
        current = current.replace('pvalue_original, false)', 'pvalue_original, pfunction_producer.CODE.STRICT)')
        current = current.replace('$source_line(metadata_first) = 8 /\\ $source_line(metadata_last) = 9', '$source_line(metadata_first) = ' + str(line) + ' /\\ $source_line(metadata_last) = ' + str(line + 1))
        if current.startswith('$runtime_line('):
            current = current.removesuffix(' = 8') + ' = ' + str(line)
        current = current.replace('perrorcall.LINE = 8', 'perrorcall.LINE = ' + str(line))
        for old, new in {'ARG_OWNERS': '3', 'RETURN_OWNERS': '2', 'PRE_OWNERS': '1'}.items():
            current = current.replace(old, new)
        result.append(current)
    return result


def null_lines(lines):
    result = []
    for line in lines:
        if line == 'phpType18_return = NNullableType (NIdentifier (BYTES text_return) metadata_type) metadata_return':
            result += ['phpType18_return = NUnionType (SEQUENCE ([NIdentifier (BYTES text_return_first) metadata_type, NIdentifier (BYTES text_return_last) metadata_last_type])) metadata_return',
                'text_return = text_return_first',
                '$ptlc($base64(text_return_first)) = $ptascii("string") /\\ $ptlc($base64(text_return_last)) = $ptascii("null")']
        else:
            result.append(line.replace('PTBUILTIN "array"', 'PTBUILTIN "string"').replace('$ptlc($base64(text_return)) = $ptascii("array")', '$ptlc($base64(text_return)) = $ptascii("string")'))
    return result


CONTROLS = r"""
~$typed_return_task_valid(S_return, $(z_return + 1))
~$error_call_valid(S_notice, perrorcall[.LINE = BAD_LINE])
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
$reference_notice_producer_line(S_pre, (porigin_producer), expression_producer) = NOTICE_LINE
$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_return) metadata_type, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "RETURN_KIND"]))]])
$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NNullableType (NIdentifier (BYTES "YXJyYXk=") metadata_type) metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ABSENT, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "RETURN_KIND"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE[.RETURNS = OTHER_ORDER])
$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NNullableType (NIdentifier (BYTES text_return) metadata_type) metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "RETURN_KIND"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NNullableType (NIdentifier (BYTES "b2JqZWN0") metadata_type) metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "object"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_retired, 2)
""".strip().splitlines()

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
    selected = [0, 1, 2]
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
        conditions = [initial('S_initial', i)]
        if i < 2:
            conditions += scalar_lines(scalar.BASE + scalar.VERIFY + scalar.CONTINUE + scalar.COPY, i, cases)
            conditions += ['pvalue_checked = PFLOAT 4625478292286210048' if i == 0 else 'pvalue_checked = pvalue_original']
            output = '$mcsr_output'
        else:
            conditions += null_lines(nullable.NULL_BASE + nullable.NULL_VERIFY + nullable.NULL_CONTINUE)
            conditions += ['~pfunction_producer.CODE.STRICT', '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PNULL, false) = TYPEVALUE PNULL']
            output = '$mcn_output'
        if not args.front:
            conditions = [x.removeprefix('~') if x.startswith('~$reference_notice_producer_header(') or x == '~$positional_reference_notice_pending(S_pre)' else x for x in conditions]
        conditions += [output + '(S_pre.EVENTS) = $ptascii(' + json.dumps(('A;M:17:23:0;' if i == 0 else 'S;M:17:23:0;' if i == 1 else 'N;M:1:23:0;')) + ')']
        current_derived = []
        if not args.front:
            conditions += ['~((HCELL n_original_x) <- S_pre.ALLOCATIONS)', '$heap_owners($heap_graph(S_pre), HCELL n_original_x) = 0']
            if i < 2:
                conditions += scalar_lines(scalar.PRIVATE + scalar.NORMAL, i, cases)
                conditions += ['pvalue_written = PSTRING_CARRIER INTERNED_STRING ($ptascii("float"))' if i == 0 else 'pvalue_written = PSTRING ($ptascii("X7"))']
                conditions += [('$named_reference_notice_operand(S_written, REFERENCE n_private)' if i == 0 else '~$named_reference_notice_operand(S_written, REFERENCE n_private)')]
            else:
                conditions += nullable.NULL_PRIVATE + nullable.NULL_NORMAL
                conditions += ['$named_reference_notice_operand(S_written, REFERENCE n_private)']
            conditions += [output + '(S_full.EVENTS) = $ptascii(' + json.dumps(cases[i]['native_stdout']) + ')']
            order = list(reversed(cases[i]['union_order']))
            other_order = '[(PTBRANCH ([PTBUILTIN "' + order[0] + '"])), (PTBRANCH ([PTBUILTIN "' + order[1] + '"]))]'
            current_derived = [line.replace('OTHER_ORDER', other_order).replace('RETURN_KIND', cases[i]['return_kind']).replace('NOTICE_LINE', str(cases[i]['observed_notice_line'])).replace('BAD_LINE', str(cases[i]['observed_notice_line'] + 1)) for line in CONTROLS]
        case_specs.append('dec $mcns_case' + str(i) + '() : bool\ndef $mcns_case' + str(i) + '() = true\n' + ''.join('  -- if ' + x + '\n' for x in conditions + current_derived))
        reached += conditions
        derived += current_derived
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $mcns_case' + str(i) + '()\n' for i in selected))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(scalar.__file__), Path(nullable.__file__), CATALOGUE, fixture, *native_paths, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'multi-cv-union-scalar-return-producer-front' if args.front else 'multi-cv-union-scalar-return-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
