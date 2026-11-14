"""Ground exact array/callable headers, finite-table owners and private Notice cells."""
import argparse
import base64
import hashlib
import importlib
import json
import os
import subprocess
from pathlib import Path

import cv_int_callable_producer_reference_notice_review_state as prior
import cv_union_callable_producer_reference_notice_review_state as raw_types
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_array_callable_producer_reference_notice_review_cases.json')
FORWARD = raw_types.union(('callable', 'array'))[1]
REVERSE = raw_types.union(('array', 'callable'))[1]


def prefix(case):
    return prior.prefix(case).replace('ReviewCallableInt86', 'ReviewCallableArray90')


def controls(case):
    args = 'SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    signature = 'pfunction_producer.SIGNATURE'
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])',
        '~$positional_reference_notice_pending(S_pre[.ARRAYS = eps])',
        '~$positional_reference_notice_pending(S_pre[.ALLOCATIONS = eps])',
        '~$error_call_valid(S_notice[.REFCELLS = eps], perrorcall)']
    for normalized in (FORWARD, REVERSE):
        for strict in ('false', 'true'):
            lines += ['$typed_exact(' + normalized + ', pvalue_original)',
                '$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
                '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps][.CLASSES = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
                '$typed_conversion_at(S_return, ' + normalized + ', pvalue_y_original, ' + strict + ') = TYPEVALUE pvalue_y_original']
            for field in ('CALLABLES', 'FUNCTIONS'):
                lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', pvalue_y_original, ' + strict + ') = TYPEREJECT']
            for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'PINT 17', 'PFLOAT $float_of_int(0)', 'PFLOAT $float_of_int(17)', 'PSTRING eps', 'PSTRING ($ptascii("17"))', 'PSTRING ($ptascii("missingArray90"))'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEREJECT']
    raw_array, _ = raw_types.union(('array', 'callable'))
    for family in ('string', 'int', 'float', 'bool', 'literal_bool'):
        donor = importlib.import_module('cv_' + family + '_callable_producer_reference_notice_review_state')
        promoted = [line.removeprefix('~') for line in donor.controls(case) if raw_array in line and line.startswith(('~$reference_notice_producer_header(', '$reference_notice_producer_header(', '~$reference_notice_producer_arguments(', '$reference_notice_producer_arguments('))]
        assert len(promoted) == 2, family
        lines += promoted
    for kinds in (('callable', 'array'), ('array', 'callable'), ('callable', 'object'), ('callable', 'array', 'null'), ('callable', 'callable')):
        raw, normalized = raw_types.union(kinds)
        refusal = '' if len(kinds) == 2 and 'array' in kinds else '~'
        lines += [refusal + '$reference_notice_producer_header(' + args + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
        raw_param = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter'
        lines += [refusal + '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([' + raw_param + ', phpType17_last]), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '], psparam_last]])']
    for wrong in (FORWARD, '[(PTBRANCH ([PTBUILTIN "array"]))]', REVERSE[:-1] + ', (PTBRANCH ([PTBUILTIN "array"]))]'):
        lines += ['~$reference_notice_producer_header(' + args + 'phpType18_return, ' + signature + '[.RETURNS = ' + wrong + '])']
    for update in ('.BYREF = true', '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged array callable default"'):
        lines += ['~$reference_notice_producer_arguments(' + args + signature + '[.RETURNS = eps][.PARAMETERS = [psparam_first[' + update + '], psparam_last]])']
    for stage in ('notice', 'receive_last'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return lines


def normal(initial, case, index, front):
    reached, _ = prior.normal(initial, dict(case, formal_kinds=['int', 'int']), index, front)
    replacements = {
        'pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_original_string) ($ptascii("17"))': 'pvalue_original = PARRAY n_original_array',
        'pvalue_y_original = PSTRING_CARRIER (REQUEST_STRING n_y_string) ($ptascii("19"))': 'pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps('ReviewCallableArray90\\FiRsT') + '))',
        'pvalue_saved = PINT 17': 'pvalue_saved = pvalue_original',
        'pvalue_received_last = PINT 19': 'pvalue_received_last = pvalue_y_original',
        '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEINTEGER pvalue_original': '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEVALUE pvalue_original',
        '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEINTEGER pvalue_y_original': '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE pvalue_y_original',
        '$node_children(S_notice, HCELL n_private) = eps': '$node_children(S_notice, HCELL n_private) = [HARRAY n_original_array]',
    }
    result = []
    for line in reached:
        if line.startswith('$string_carrier_valid(') and 'pvalue_y_original' not in line:
            continue
        line = replacements.get(line, line)
        line = line.replace(prior.FORWARD, FORWARD).replace(prior.REVERSE, REVERSE)
        line = line.replace('$ptascii("int")', '$ptascii("array")')
        if line.startswith(('S_checked.COMPLETION =', 'S_after_return.TODO =', 'S_pre.RESULT =', 'S_notice.STORE[n_private]', 'S_resume.STORE[n_private]')):
            line = line.replace('(PINT 17)', 'pvalue_saved')
        result.append(line)
    result += ['S_args.ARRAYS[n_original_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]',
        '$node_children(S_receive_last, HCELL n_saved) = [HARRAY n_original_array]',
        '$heap_valid($heap_graph(S_pre))',
        'S_pre.ARRAYS[n_original_array].ITEMS = S_args.ARRAYS[n_original_array].ITEMS']
    if not front:
        result += ['$heap_owners($heap_graph(S_notice), HARRAY n_original_array) = 2',
            'S_resume.STORE[n_snapshot] = DEFINED pvalue_original',
            'S_full.ARRAYS[n_original_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]']
    return result, [] if front else controls(case)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native, cases = json.loads(provenance.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prefix_prior.__file__), Path(raw_types.__file__), CATALOGUE, provenance] + [ROOT / 'tests/semantics' / ('cv_' + family + '_callable_producer_reference_notice_review_state.py') for family in ('string', 'float', 'bool', 'literal_bool')]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:1]):
            row = rows[case['id']]
            source = Path(row['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            conditions, current_derived = normal(initial, case, index, args.front)
            case_specs.append('dec $scfr_case' + str(index) + '() : bool\ndef $scfr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
            reached += conditions
            derived += current_derived
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(prefix(cases[0]) + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[row['id'] for row in cases[:1]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-array-callable-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
