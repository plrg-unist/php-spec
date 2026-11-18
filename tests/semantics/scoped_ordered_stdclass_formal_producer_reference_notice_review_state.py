#!/usr/bin/env python3
"""Ground ordered declaration-scoped FORMAL authority at an actual NULL Notice frontier."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import scoped_nullable_stdclass_formal_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_ordered_stdclass_formal_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX


def branches(members):
    atoms = ['(PTBRANCH ([PTCLASS ($ptascii("stdClass"))]))' if member == 'CLASS' else '(PTBRANCH ([PTBUILTIN ' + json.dumps(member) + ']))' for member in members]
    return '[' + ', '.join(atoms) + ']'


def raw_union(members):
    atoms = ['NName (BYTES text_formal) metadata_formal' if member == 'CLASS' else 'NIdentifier (BYTES ' + json.dumps(base64.b64encode(member.encode()).decode()) + ') ' + ('metadata_null126' if member == 'null' else 'metadata_int126' if member == 'int' else 'metadata_formal') for member in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_formalnullable'


def normal(initial, case, front):
    original, inherited = prior.normal(initial, case, front)
    members = ['null', 'CLASS', 'int']
    canonical = branches(members)
    wrapper = 'NNullableType (NName (BYTES text_formal) metadata_formal) metadata_formalnullable'
    raw_type = raw_union(members)
    reached = []
    for line in original:
        if line.startswith('$ptnullable('):
            continue
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + canonical
        elif line.startswith('phpType17 = '):
            assert wrapper in line
            line = line.replace(wrapper, raw_type, 1)
        reached.append(line)
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith(('~$error_call_valid(', '~$typed_return_task_valid(', 'S_zero_', '$drive($drive(S_zero_'))]
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    view_of = lambda raw: raw.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    view = view_of(parameter)
    env = 'pfunction_producer.ENV'
    helper = lambda raw, context=env: '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + raw + ')'
    scoped = '$reference_notice_producer_scoped_header(' + env + ', SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    proof = lambda raw: scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + raw + ']),', 1)
    typed = lambda expression, signature: expression.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = ' + signature + ']]])')
    derived += [helper('phpType17') + ' = (' + view + ')', helper(view) + ' = (' + view + ')', proof(view),
        '$reference_notice_producer_global_parameter_view(phpType17) = (' + view + ')',
        scoped.replace(env + ',', env + '[.CLASSES = eps],', 1),
        '~' + scoped.replace(env + ',', env + '[.NAMESPACE = $ptascii("Other")],', 1),
        scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        '~' + scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([phpType17, phpType17]),', 1)]
    for signature in ('eps', branches(['CLASS']), branches(['CLASS', 'null']), branches(['CLASS', 'null', 'int']), branches(['null', 'int', 'CLASS']), branches(['null', 'CLASS', 'float']), branches(members + ['int']), canonical.replace('"stdClass"', '"Other"'), canonical.replace('"stdClass"', '"STDCLASS"')):
        derived.append('~' + typed(scoped, signature))
    for alias in ('Spare', 'sPaRe', 'SPARE'):
        raw = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(alias.encode()).decode()), 1)
        derived += [helper(raw) + ' = (' + view + ')', proof(raw)]
    for tag in ('NNameRelative', 'NIdentifier', 'NNameFullyQualified'):
        raw = parameter.replace('NName (BYTES text_formal)', tag + ' (BYTES text_formal)', 1)
        derived += [helper(raw) + ' = (' + raw + ')', ('' if tag == 'NNameFullyQualified' else '~') + proof(raw)]
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()), 1)
        derived += [helper(raw) + ' = (' + raw + ')', '~' + proof(raw)]
    for name in ('int', 'mixed', 'self', 'array', 'callable'):
        raw = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()), 1)
        context = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        derived += [helper(raw, context) + ' = (' + raw + ')', '~' + proof(raw).replace(env + ',', context + ',', 1)]
    for target in ('Other', 'STDCLASS', 'StDcLaSs'):
        context = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(target) + '))]]'
        expected = 'phpType17' if target == 'Other' else '(' + view.replace('"c3RkQ2xhc3M="', json.dumps(base64.b64encode(target.encode()).decode())) + ')'
        derived += [helper('phpType17', context) + ' = ' + expected, '~' + scoped.replace(env + ',', context + ',', 1)]
    for valid in (['CLASS', 'null'], ['null', 'CLASS'], ['int', 'CLASS', 'float'], ['CLASS', 'array', 'int', 'bool', 'string', 'callable', 'null'], ['iterable', 'int', 'float', 'bool', 'CLASS', 'string', 'callable', 'null'], ['false', 'CLASS', 'null'], ['CLASS', 'true', 'string']):
        raw = parameter.replace(raw_type, raw_union(valid), 1)
        derived += [helper(raw) + ' = (' + view_of(raw) + ')', typed(proof(raw), branches(valid))]
    builtin = parameter.replace(raw_type, raw_union(['int', 'null']), 1)
    derived += [helper(builtin) + ' = (' + builtin + ')', typed(proof(builtin), branches(['int', 'null']))]
    for invalid in (['CLASS', 'CLASS', 'null'], ['null', 'CLASS', 'null'], ['CLASS', 'array', 'iterable'], ['CLASS', 'bool', 'false'], ['CLASS', 'true', 'false'], ['CLASS', 'object'], ['CLASS', 'mixed'], ['CLASS', 'void'], ['CLASS', 'never']):
        raw = parameter.replace(raw_type, raw_union(invalid), 1)
        derived.append('~' + typed(proof(raw), branches(invalid)))
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN true) (BOOLEAN false)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN false) (BOOLEAN true)'),
            (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) '),
            ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
        raw = parameter.replace(before, after, 1)
        derived += [helper(raw) + ' = (' + view.replace(before, after, 1) + ')', '~' + proof(raw)]
    for before, after in (('metadata_formalnullable', 'eps'), ('metadata_formal,', 'eps,'), ('metadata_null126', 'eps'), ('metadata_int126', 'eps'), ('metadata_parameter', 'eps')):
        assert before in parameter
        raw = parameter.replace(before, after)
        derived.append(helper(raw) + ' = (' + view_of(raw) + ')')
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged scoped ordered formal default"'):
        derived.append('~' + scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[' + update + ']]])'))
    for strict in ('true', 'false'):
        derived += ['$typed_conversion_at(S_receive, psparam.TYPE, PNULL, ' + strict + ') = TYPEVALUE PNULL',
            '$typed_conversion_at(S_receive, psparam.TYPE, PINT 19, ' + strict + ') = TYPEVALUE (PINT 19)']
        for value in ('PBOOL false', 'PSTRING ($ptascii("17"))', 'PFLOAT 0'):
            derived.append('$typed_conversion_at(S_receive, psparam.TYPE, ' + value + ', ' + strict + ') = ' + ('TYPEREJECT' if strict == 'true' else 'TYPEINTEGER (' + value + ')'))
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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 2
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [Path(__file__), CATALOGUE, provenance]
    paths += sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    for case in cases:
        row = rows[case['id']]
        source = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
        paths += [source, Path(row['stdout']), Path(row['stderr'])]
    source = Path(rows[cases[0]['id']]['command'][-1])
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached, derived = normal(initial, cases[0], args.front)
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[cases[0]['id']], unchanged_reception_controls=[cases[1]['id']], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('scoped-ordered-stdclass-formal-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
