"""Ground distinct builtin union arrays, strict reception and finite raw guards."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_union_null_formal_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_distinct_builtin_union_formal_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice61', 'ReviewNotice62')
PRIORITY = []
for line in prior.PRIORITY:
    line = line.replace('psparam.TYPE = [(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]', 'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "array"]))]')
    if line.startswith('phpType17 = NParam'):
        line = line.replace('NIdentifier (BYTES "bnVsbA==") metadata_null', 'NIdentifier (BYTES text_other) metadata_other')
    line = line.replace('$ptlc($base64(text_type)) = $ptascii("bool")', '$ptlc($base64(text_type)) = $ptascii("string")')
    PRIORITY.append(line)
PRIORITY += ['$ptlc($base64(text_other)) = $ptascii("array")']


def normal(initial, case, front):
    conditions, derived = prior.normal(initial, case, front)
    old = 'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "array"]))]'
    assert conditions.count(old) == 1
    conditions = [line.replace(old, 'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "string"]))]') for line in conditions]
    old_raw = '(NUnionType (SEQUENCE ([NIdentifier (BYTES "bnVsbA==") metadata_null, NIdentifier (BYTES text_type) metadata_type])) metadata_formal_union)'
    new_raw = '(NUnionType (SEQUENCE ([NIdentifier (BYTES text_type) metadata_type, NIdentifier (BYTES text_other) metadata_other])) metadata_formal_union)'
    assert sum(old_raw in line for line in conditions) == 1
    conditions = [line.replace(old_raw, new_raw) for line in conditions]
    conditions += ['$ptlc($base64(text_other)) = $ptascii("string")']
    if not front:
        derived = [line.replace('metadata_null', 'metadata_other') for line in derived]
        wrong = 'psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]]'
        derived = [line.replace(wrong, 'psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "array"]))]]') if line.startswith('~$reference_notice_producer_arguments(') else line for line in derived]
        derived = [line.removeprefix('~') if 'SEQUENCE ([phpType17_wider])' in line else line for line in derived]
        # Match both old61 INT|FLOAT refusal instantiations without replaying them.
        derived += [
            'phpType10_suffix = NExprVariable (BYTES "Y2hhbmdlZA==") metadata_arg',
            'phpType17_int_float = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") metadata_type, NIdentifier (BYTES "ZmxvYXQ=") metadata_other])) metadata_formal_union) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
            'psparam_int_float = psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "float"]))]]']
        for first, last in (('null', 'float'), ('bool', 'null')):
            suffix = first + '_' + last
            one, two = (base64.b64encode(kind.encode()).decode() for kind in (first, last))
            normalized = '[(PTBRANCH ([PTBUILTIN "' + first + '"])), (PTBRANCH ([PTBUILTIN "' + last + '"]))]'
            derived += [
                'phpType17_' + suffix + ' = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES "' + one + '") metadata_type, NIdentifier (BYTES "' + two + '") metadata_other])) metadata_formal_union) (BOOLEAN true) (BOOLEAN false) phpType10_suffix ABSENT (SEQUENCE eps) metadata_parameter',
                'psparam_' + suffix + ' = psparam[.NAME = $ptascii("changed")][.BYREF = true][.TYPE = ' + normalized + ']',
                '$reference_notice_producer_arguments(SEQUENCE ([phpType7, phpType7]), SEQUENCE ([phpType17_int_float, phpType17_' + suffix + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_int_float, psparam_' + suffix + ']])']
        for kinds in (('array', 'array'), ('array', 'string', 'int')):
            name = 'phpType17_bad_' + '_'.join(kinds)
            raw = ['NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") metadata_type' for kind in kinds]
            normalized = '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + kind + '"]))' for kind in kinds) + ']'
            derived += [name + ' = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([' + ', '.join(raw) + '])) metadata_formal_union) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
                ('' if kinds == ('array', 'string', 'int') else '~') + '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([' + name + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
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
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(prior.prior.__file__)]
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
    print('cv-distinct-builtin-union-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
