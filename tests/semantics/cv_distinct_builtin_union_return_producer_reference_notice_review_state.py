"""Ground nonnull return pairs, ARRAY COW and strict RETURN-before-Notice rejection."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_primitive_union_formal_producer_reference_notice_review_state as prior
import singleton_cv_nullable_scalar_return_producer_reference_notice_review_state as return_prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_distinct_builtin_union_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice63', 'ReviewNotice64')
PREFIX = PREFIX.replace('def $scfr_ready(S, 6) = true\n  -- if S.TODO = [TYPE_RECEIVE porigin 0]',
    'def $scfr_ready(S, 6) = true\n  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*')
PREFIX = PREFIX.replace('P;C:11:2:1:1;', 'P;M:17;C:11:2:1:1;')

PRIORITY = []
for line in return_prior.PRIORITY:
    line = line.replace('PINT 17', 'pvalue_original')
    line = line.replace('pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]',
        'pfunction_producer.SIGNATURE.RETURNS = ' + prior.normalized(('array', 'float')))
    line = line.replace('$ptascii("bool") /\\ $ptlc($base64(text_last)) = $ptascii("null")',
        '$ptascii("array") /\\ $ptlc($base64(text_last)) = $ptascii("float")')
    PRIORITY.append(line)
    if line == 'S_return.STORE[n_formal] = DEFINED (pvalue_original)':
        PRIORITY += ['pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))',
            '$string_carrier_valid(S_return, pvalue_original)']
    if line == 'S_written.STORE[n_x] = DEFINED (PINT 23) /\\ S_written.STORE[n_copy] = DEFINED (pvalue_original)':
        PRIORITY.append('$string_carrier_valid(S_written, pvalue_original)')


def normal(initial, case, front):
    conditions, derived = prior.normal(initial, case, front)
    derived = [line.replace('metadata_return_nullable', 'metadata_return_union') for line in derived]
    old = 'pfunction_producer.SIGNATURE.RETURNS = ' + prior.normalized(('array', 'null'))
    assert conditions.count(old) == 1
    conditions = [line.replace(old, 'pfunction_producer.SIGNATURE.RETURNS = ' + prior.normalized(('array', 'string'))) for line in conditions]
    old_raw = 'phpType18 = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return_nullable'
    new_raw = 'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES text_return_string) metadata_return_string])) metadata_return_union'
    assert conditions.count(old_raw) == 1
    conditions = [line.replace(old_raw, new_raw) for line in conditions]
    conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_arguments(') else line for line in conditions]
    conditions += ['$ptlc($base64(text_return_string)) = $ptascii("string")']
    if not front:
        arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
        header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
        for kinds in (('string', 'array'), ('array',), ('array', 'string', 'bool')):
            derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + prior.normalized(kinds) + '])')]
        for kinds in (('float', 'int'), ('int', 'float'), ('bool', 'string'), ('string', 'bool')):
            name = 'phpType18_' + '_'.join(kinds)
            derived += [name + ' = ' + prior.raw_union(kinds),
                '$reference_notice_producer_header(' + arguments + name + ', pfunction_producer.SIGNATURE[.RETURNS = ' + prior.normalized(kinds) + '])']
        for kinds in (('array', 'array'), ('array', 'string', 'bool'), ('array', 'object'), ('array', 'mixed')):
            name = 'phpType18_bad_' + '_'.join(kinds)
            derived += [name + ' = ' + prior.raw_union(kinds),
                '~$reference_notice_producer_header(' + arguments + name + ', pfunction_producer.SIGNATURE[.RETURNS = ' + prior.normalized(kinds) + '])']
    return conditions, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native = json.loads(provenance.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 2
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(return_prior.__file__), Path(prior.prior.__file__)]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
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
            conditions, current_derived = normal(initial, case, args.front) if index == 0 else ([initial] + PRIORITY + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')'], [])
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n  -- if $scfr_case1()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-distinct-builtin-union-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
