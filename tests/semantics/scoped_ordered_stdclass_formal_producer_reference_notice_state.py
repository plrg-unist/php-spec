#!/usr/bin/env python3
"""Ground declaration-resolved ordered stdClass FORMAL unions before private Notices."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import scoped_nullable_stdclass_formal_producer_reference_notice_state as prior
import global_plain_ordered_stdclass_formal_producer_reference_notice_state as ordered
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_ordered_stdclass_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('ScopedNullableFormal125', 'ScopedOrderedFormal126')



def branches(members, name='stdClass'):
    return ordered.branches(members, name)


def raw_type(members, name=None, tag='NName', indexed=True):
    return ordered.raw_type(members, name, tag, indexed)


def front_lines(index, case):
    lines = []
    parameter = 'psparam' if index == 0 else 'psparam_last'
    raw = raw_type(case['formal_members'])
    for line in prior.front_lines(index, case):
        if parameter + '.TYPE = ' in line:
            line = line.replace(prior.nullable_type('stdClass'), branches(case['formal_members']))
        line = line.replace('ScopedNullableFormal125', 'ScopedOrderedFormal126')
        if line.startswith('phpType18_parameter = NNullableType '):
            line = 'phpType18_parameter = ' + raw
        if line.startswith('phpType17_last = '):
            line = line.replace('(NNullableType (NName (BYTES text_formal) metadata_formal) metadata_nullable_formal)', '(' + raw + ')', 1)
        lines.append(line)
    return lines


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index, case):
    env = 'pfunction_producer.ENV'
    raw = 'phpType17' if index == 0 else 'phpType17_last'
    converted = '$reference_notice_producer_scoped_parameter_view('
    lines = []
    for line in ordered.controls(index, case):
        if line.startswith('$typed_conversion_at(S_receive,'):
            continue
        line = line.replace('$ptascii("sTdClAsS")', '$ptascii("stdClass")')
        line = line.replace('NNameFullyQualified (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")')
        line = line.replace('$reference_notice_producer_global_parameter_view(', converted + env + ', ')
        if line.startswith('~$reference_notice_producer_scoped_header(' + env + '[.NAMESPACE = '):
            line = line[1:]
        lines.append(line)
    lines.append('$reference_notice_producer_global_parameter_view(' + raw + ') = ' + raw)
    byref = 'false' if index == 0 else 'true'
    variable = 'phpType10' if index == 0 else 'phpType10_last'
    metadata = 'metadata_parameter' if index == 0 else 'metadata_parameter_last'
    shape = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw_type(case['formal_members']) + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    view = shape.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    for position, kind in enumerate(case['formal_members']):
        if kind != 'class':
            token = 'metadata_formal_' + str(position)
            changed = shape.replace(token, 'eps', 1)
            lines.append(converted + env + ', ' + changed + ') = (' + view.replace(token, 'eps', 1) + ')')
    for alias in ('Box', 'bOx', 'BOX'):
        changed = shape.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(alias.encode()).decode()), 1)
        lines.append(converted + env + ', ' + changed + ') = (' + view + ')')
    for strict in ('true', 'false'):
        normalized = branches(case['formal_members'])
        lines.append('$typed_conversion_at(S_receive, ' + normalized + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)')
        if index == 0:
            answer = 'TYPEREJECT' if strict == 'true' else 'TYPESTRING (PINT 19)'
        else:
            answer = 'TYPEVALUE (PINT 19)'
            lines.append('$typed_conversion_at(S_receive, ' + normalized + ', PNULL, ' + strict + ') = TYPEVALUE PNULL')
        lines.append('$typed_conversion_at(S_receive, ' + normalized + ', PINT 19, ' + strict + ') = ' + answer)
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
        specs.append('dec $sour_case' + str(i) + '() : bool\ndef $sour_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $sour_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__), CATALOGUE, fixture, native_path,
        ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    dependencies = [prior, ordered]
    for dependency in dependencies:
        paths.append(Path(dependency.__file__))
        if hasattr(dependency, 'prior') and dependency.prior not in dependencies:
            dependencies.append(dependency.prior)
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
    print('scoped-ordered-stdclass-formal-front' if args.front else 'scoped-ordered-stdclass-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
