"""Ground finite primitive RETURN members, ARRAY COW and strict triple rejection."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_distinct_builtin_union_return_producer_reference_notice_review_state as prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_primitive_union_return_producer_reference_notice_review_cases.json')
KINDS = prior.prior.KINDS
PREFIX = prior.PREFIX.replace('ReviewNotice64', 'ReviewNotice65')

PRIORITY = []
for line in prior.PRIORITY:
    line = line.replace('pfunction_producer.SIGNATURE.RETURNS = ' + prior.prior.normalized(('array', 'float')),
        'pfunction_producer.SIGNATURE.RETURNS = ' + prior.prior.normalized(('array', 'bool', 'float')))
    if line.startswith('phpType18 = NUnionType'):
        line = line.replace('NIdentifier (BYTES text_last) metadata_last', 'NIdentifier (BYTES text_return_bool) metadata_return_bool, NIdentifier (BYTES text_last) metadata_last')
    PRIORITY.append(line)
PRIORITY += ['$ptlc($base64(text_return_bool)) = $ptascii("bool")']


def normal(initial, case, front):
    conditions, derived = prior.normal(initial, case, front)
    old = 'pfunction_producer.SIGNATURE.RETURNS = ' + prior.prior.normalized(('array', 'string'))
    assert conditions.count(old) == 1
    conditions = [line.replace(old, 'pfunction_producer.SIGNATURE.RETURNS = ' + prior.prior.normalized(KINDS)) for line in conditions]
    old_raw = 'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES text_return_string) metadata_return_string])) metadata_return_union'
    nodes = ['NIdentifier (BYTES text_return) metadata_return'] + ['NIdentifier (BYTES text_return_' + kind + ') metadata_return_' + kind for kind in KINDS[1:]]
    new_raw = 'phpType18 = NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union'
    assert conditions.count(old_raw) == 1
    conditions = [line.replace(old_raw, new_raw) for line in conditions]
    conditions += ['$ptlc($base64(text_return_' + kind + ')) = $ptascii("' + kind + '")' for kind in ('int', 'float', 'bool', 'null')]
    if not front:
        # REF65 admits this exact former raw3/normalized3 refusal; raw2/count mismatches stay negative.
        arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
        inherited_positive = '$reference_notice_producer_header(' + arguments + 'phpType18_bad_array_string_bool, pfunction_producer.SIGNATURE[.RETURNS = ' + prior.prior.normalized(('array', 'string', 'bool')) + '])'
        assert derived.count(inherited_positive) == 1
        for kinds in (KINDS[:4], tuple(reversed(KINDS[:4])), KINDS[:5], tuple(reversed(KINDS[:5])), tuple(reversed(KINDS)), ('array', 'string', 'bool'), ('int', 'null', 'bool')):
            name = 'phpType18_members_' + '_'.join(kinds)
            derived += [name + ' = ' + prior.prior.raw_union(kinds),
                '$reference_notice_producer_header(' + arguments + name + ', pfunction_producer.SIGNATURE[.RETURNS = ' + prior.prior.normalized(kinds) + '])']
        for kinds in (('array', 'int', 'array'), KINDS + ('array',), ('array', 'int', 'object'), ('array', 'int', 'mixed')):
            name = 'phpType18_bad_members_' + '_'.join(kinds)
            derived += [name + ' = ' + prior.prior.raw_union(kinds),
                '~$reference_notice_producer_header(' + arguments + name + ', pfunction_producer.SIGNATURE[.RETURNS = ' + prior.prior.normalized(kinds) + '])']
        header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
        derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + prior.prior.normalized(tuple(reversed(KINDS))) + '])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + prior.prior.normalized(KINDS[:-1]) + '])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTCLASS ($ptascii("array"))]))] ++ ' + prior.prior.normalized(KINDS[1:]) + '])')]
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
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(prior.return_prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__)]
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-primitive-union-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
