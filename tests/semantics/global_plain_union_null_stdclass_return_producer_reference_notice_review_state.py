#!/usr/bin/env python3
"""Ground ordered plain class/null returns on named object and NULL frontiers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import global_plain_nullable_stdclass_return_producer_reference_notice_review_state as previous
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_union_null_stdclass_return_producer_reference_notice_review_cases.json')
prior, PREFIX = previous.prior, previous.PREFIX


def union_type(name, members):
    return '[' + ', '.join(prior.class_type(name)[1:-1] if member == 'class' else '(PTBRANCH ([PTBUILTIN "null"]))' for member in members) + ']'


def raw_union(members, class_node='NName (BYTES text_return) metadata_return'):
    return 'NUnionType (SEQUENCE ([' + ', '.join(class_node if member == 'class' else 'NIdentifier (BYTES text_return_null) metadata_return_null' for member in members) + '])) metadata_union_return'


def normal(initial, case, index, front):
    original, inherited = previous.normal(initial, case, index, front)
    reached = []
    for line in original:
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + union_type(case['class_return'], case['return_members'])
        if line.startswith('phpType18 = '):
            line = 'phpType18 = ' + raw_union(case['return_members'])
        reached.append(line)
    reached.append('$ptlc($base64(text_return_null)) = $ptascii("null")')
    if front:
        return reached, []
    derived = [line for line in inherited if '$reference_notice_producer_scoped_header(' not in line]
    def proof(raw='phpType18', members=None, name=None, env='pfunction_producer.ENV', signature=None):
        signature = signature or 'pfunction_producer.SIGNATURE'
        if members is not None:
            signature += '[.RETURNS = ' + union_type(name or case['class_return'], members) + ']'
        return '$reference_notice_producer_scoped_header(' + env + ', SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), ' + raw + ', ' + signature + ')'
    imported = '[($ptascii("stdclass"), $ptascii("stdClass"))]'
    for env in ('pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")]', 'pfunction_producer.ENV[.CLASSES = ' + imported + ']'):
        prefix = '' if case['class_return'] == 'stdClass' and '.CLASSES = ' in env else '~'
        derived += [prefix + proof(env=env), proof(env=env, raw=raw_union(case['return_members'], 'NNameFullyQualified (BYTES text_return) metadata_return'))]
    for members in (['class','null'], ['null','class']):
        for spelling in ('stdClass','sTdClAsS','STDCLASS'):
            name = 'NName (BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()) + ') metadata_return'
            derived.append(proof(raw=raw_union(members,name),members=members,name=spelling))
    derived += [proof(signature='pfunction_producer.SIGNATURE[.RETURNS = eps]'),
        '~' + proof(members=case['return_members'][::-1]), '~' + proof(members=['class']),
        '~' + proof(name='Other',members=case['return_members'])]
    for tag in ('NIdentifier','NNameRelative'):
        derived.append('~' + proof(raw=raw_union(case['return_members'],tag+' (BYTES text_return) metadata_return')))
    wrong = raw_union(case['return_members']).replace('NIdentifier (BYTES text_return_null)', 'NName (BYTES text_return_null)')
    derived += ['~' + proof(raw=wrong), '~' + proof(raw=raw_union(case['return_members']).replace('text_return_null','"aW50"')),
        '~' + proof(raw=raw_union(case['return_members'], 'NName (BYTES "T3RoZXI=") metadata_return'))]
    nullable = 'NNullableType (NName (BYTES text_return) metadata_return) metadata_union_return'
    derived.append(proof(raw=nullable,members=['class','null']))
    for update in ('.REQUIRED = false','.VARIADIC = true','.DEFAULT = PSDEFAULTUNSUPPORTED "forged ordered plain class default"'):
        derived.append('~' + proof(signature='pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[' + update + ']]]'))
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    if index == 0:
        derived.append(proof().replace('SEQUENCE ([phpType17]),','SEQUENCE ([' + parameter.replace('NNameFullyQualified','NName') + ']),'))
    return reached, derived


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
    paths = [Path(__file__), Path(previous.__file__), Path(previous.previous.__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:2]):
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
            for control_index, control in enumerate([] if args.front else case.get('scope_controls', [])):
                source_control = out / ('scope-control-' + str(control_index) + '.php')
                source_control.write_bytes(control['source'].encode())
                assert sha(source_control) == control['source_sha256'] and control['source_agreements'] == 0
                parsed_control = frontend.request({'op': 'parse', 'source': base64.b64encode(source_control.read_bytes()).decode()})
                assert parsed_control['accepted']
                checked_control = adapter.request({'op': 'check', 'ast': parsed_control['ast'], 'fixture': True})
                assert checked_control['ok'] and checked_control['fixture']
                suffix = str(control_index)
                state, function = 'S_scope' + suffix, 'pfunction_scope' + suffix
                argument, result = 'phpType17_scope' + suffix, 'phpType18_scope' + suffix
                name, body, metadata = 'phpType11_scope' + suffix, 'phpType23_scope' + suffix, 'metadata_scope' + suffix
                text, metadata_return = 'text_scope_return' + suffix, 'metadata_scope_return' + suffix
                current_derived += [state + ' = $php_run(' + checked_control['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source_control)).decode()) + ')',
                    state + '.COMPLETION = BUDGET', state + '.FUNCTIONS = [' + function + ']',
                    function + '.ENV.NAMESPACE = $ptascii(' + json.dumps(control['namespace']) + ')',
                    function + '.ENV.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]',
                    function + '.SIGNATURE.RETURNS = ' + union_type('stdClass', ['class', 'null']),
                    '$origin_node(' + state + '.SOURCES, ' + function + '.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) ' + name + ' (SEQUENCE ([' + argument + '])) ' + result + ' ' + body + ' ' + metadata + ')',
                    result + ' = NUnionType (SEQUENCE ([NName (BYTES ' + text + ') ' + metadata_return + ', NIdentifier (BYTES text_scope_null' + suffix + ') metadata_scope_null' + suffix + '])) metadata_scope_union' + suffix,
                    '$base64(' + text + ') = $ptascii("stdClass")', '$ptlc($base64(text_scope_null' + suffix + ')) = $ptascii("null")',
                    '~$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([' + argument + ']), ' + result + ', ' + function + '.SIGNATURE)']
                if not args.front:
                    tail = ', SEQUENCE ([phpType7]), SEQUENCE ([' + argument + ']), ' + result + ', ' + function + '.SIGNATURE)'
                    current_derived += ['$reference_notice_producer_scoped_header(' + function + '.ENV' + tail,
                        '$reference_notice_producer_scoped_header(' + function + '.ENV[.NAMESPACE = eps][.CLASSES = eps]' + tail]
                paths.append(source_control)
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scfr_case' + str(index) + '()\n' for index in range(2)))
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[row['id'] for row in cases[:2]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-union-null-stdclass-return-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
