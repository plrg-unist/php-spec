#!/usr/bin/env python3
"""Ground nullable bare-global FORMAL authority at an actual NULL Notice frontier."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_nullable_fqn_stdclass_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_nullable_stdclass_formal_producer_reference_notice_review_cases.json')
PREFIX = '\n'.join('  -- if pcallcontext.NAME = $ptascii("make")' if line.startswith('  -- if pcallcontext.NAME <- ') else line for line in prior.PREFIX.splitlines()) + '\n'


def normal(initial, case, front):
    original, _ = prior.normal(initial, case, 1, front)
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    reached = []
    for line in original:
        if line.startswith('phpType17 = '):
            line = line.replace('NNameFullyQualified', 'NName', 1)
        bare = line.removeprefix('~')
        if bare.startswith(('$reference_notice_producer_arguments(', '$reference_notice_producer_header(')):
            line = '~' + bare
        if bare == '$named_reference_notice_pending(S_pre)':
            reached += [r'pfunction_producer.ENV.NAMESPACE = eps /\ pfunction_producer.ENV.CLASSES = eps', ('~' if front else '') + scoped]
        reached.append(line)
    if front:
        return reached, []
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    view = parameter.replace('NName ', 'NNameFullyQualified ', 1)
    raw_proof = lambda value: scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + value + ']),', 1)
    typed_proof = lambda value: scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = ' + value + ']]])')
    derived = ['$reference_notice_producer_global_parameter_view(phpType17) = (' + view + ')',
        '$reference_notice_producer_global_parameter_view(' + view + ') = (' + view + ')',
        raw_proof(view),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]],', 1),
        scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        '~' + scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([phpType17, phpType17]),', 1),
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for normalized in ('eps', prior.class_type('sTdClAsS'), prior.nullable('Other'), prior.nullable('stdClass'),
            prior.prior.branches(['object', 'null']), prior.prior.branches(['null']),
            '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTCLASS ($ptascii("sTdClAsS"))]))]',
            prior.nullable('sTdClAsS')[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
            prior.nullable('sTdClAsS')[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]'):
        derived.append('~' + typed_proof(normalized))
    for spelling in ('stdClass', 'STDCLASS', 'sTdClAsS'):
        changed = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()))
        valid = raw_proof(changed).replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = ' + prior.nullable(spelling) + ']]])')
        derived += [valid, '~' + valid.replace(prior.nullable(spelling), prior.nullable(spelling.swapcase()))]
    for tag in ('NNameRelative', 'NIdentifier'):
        changed = parameter.replace('NName ', tag + ' ', 1)
        derived += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', ('' if tag == 'NNameRelative' else '~') + raw_proof(changed)]
    for spelling in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00'):
        changed = parameter.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()))
        derived += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + raw_proof(changed)]
    wrapper = 'NNullableType (NName (BYTES text_formal) metadata_formal) metadata_formalnullable'
    union = 'NUnionType (SEQUENCE ([NName (BYTES text_formal) metadata_formal, NIdentifier (BYTES "bnVsbA==") metadata_formal])) metadata_formalnullable'
    changed = parameter.replace(wrapper, union, 1)
    derived += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + raw_proof(changed)]
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN true) (BOOLEAN false)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN false) (BOOLEAN true)'),
            (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) '),
            ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
        changed, changed_view = parameter.replace(before, after, 1), view.replace(before, after, 1)
        derived += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed_view + ')', '~' + raw_proof(changed)]
    for before, after in (('metadata_formalnullable', 'eps'), ('metadata_formal)', 'eps)'), ('metadata_parameter', 'eps')):
        derived.append('$reference_notice_producer_global_parameter_view(' + parameter.replace(before, after) + ') = (' + view.replace(before, after) + ')')
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged nullable bare class default"'):
        derived.append('~' + scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[' + update + ']]])'))
    for strict in ('true', 'false'):
        derived.append('$typed_conversion_at(S_receive, psparam.TYPE, PNULL, ' + strict + ') = TYPEVALUE PNULL')
        for value in ('PBOOL false', 'PINT 19', 'PSTRING ($ptascii("17"))', 'PFLOAT 0'):
            derived.append('$typed_conversion_at(S_receive, psparam.TYPE, ' + value + ', ' + strict + ') = TYPEREJECT')
    for stage in ('receive', 'return', 'notice'):
        derived += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
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
    print('global-plain-nullable-stdclass-formal-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
