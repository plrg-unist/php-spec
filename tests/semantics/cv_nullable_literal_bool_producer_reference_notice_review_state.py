"""Ground nullable false/true snapshots and separate RECEIVE/RETURN priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_literal_bool_return_producer_reference_notice_review_state as prior
import cv_literal_bool_formal_producer_reference_notice_review_state as formal_prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_nullable_literal_bool_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice71', 'ReviewNotice72').replace(
    'pcallcontext.NAME = $ptascii("ReviewNotice72\\\\Named\\\\make")',
    'pcallcontext.NAME <- [$ptascii("ReviewNotice72\\\\FalseNamed\\\\make"), $ptascii("ReviewNotice72\\\\TrueNamed\\\\make")]').replace(
    'pcallcontext.NAME <- [$ptascii("ReviewNotice72\\\\FalsePriority\\\\make"), $ptascii("ReviewNotice72\\\\TruePriority\\\\make")]',
    'pcallcontext.NAME = $ptascii("ReviewNotice72\\\\ReturnPriority\\\\make")')
PREFIX = PREFIX.replace('def $scfr_ready(S, n_stage) = false -- otherwise', r'''
def $scfr_ready(S, 9) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice72\\ReceivePriority\\make")
def $scfr_ready(S, 10) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("P;C:11:2:1:1;")
def $scfr_ready(S, 11) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("P;C:11:2:1:1;D:11:31:23:1;")
def $scfr_ready(S, n_stage) = false -- otherwise
''')


def nullable(kind):
    return '[(PTBRANCH ([PTBUILTIN "' + kind + '"])), (PTBRANCH ([PTBUILTIN "null"]))]'


def normal(initial, case, front):
    reached, _ = prior.normal(initial, case, front)
    kind = case['return_kind']
    value = 'PNULL' if case['input_value'] == 'null' else '(PBOOL true)'
    result = []
    for line in reached:
        line = line.replace('psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]', 'psparam.TYPE = ' + nullable(kind))
        line = line.replace('pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "true"]))]',
                            'pfunction_producer.SIGNATURE.RETURNS = ' + nullable(kind))
        if line.startswith('phpType17 = '):
            line = line.replace('(NIdentifier (BYTES text_type) metadata_type)',
                                '(NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable)')
        if line.startswith('phpType18 = '):
            line = 'phpType18 = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_nullable_return'
        line = line.replace('$ptlc($base64(text_type)) = $ptascii("mixed")', '$ptlc($base64(text_type)) = $ptascii("' + kind + '")')
        line = line.replace('$ptlc($base64(text_return)) = $ptascii("true")', '$ptlc($base64(text_return)) = $ptascii("' + kind + '")')
        line = line.replace('DEFINED (PBOOL true)', 'DEFINED ' + value).replace('KNOWN (PBOOL true)', 'KNOWN ' + value)
        line = line.replace('psparam, PBOOL true) = TYPEVALUE (PBOOL true)', 'psparam, ' + value + ') = TYPEVALUE ' + value)
        if front and line.startswith('$reference_notice_producer_arguments('):
            line = '~' + line
        result.append(line)
    derived = []
    if not front:
        arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
        header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
        proof = '$reference_notice_producer_arguments(' + arguments + 'pfunction_producer.SIGNATURE[.RETURNS = eps])'
        for normalized in (nullable('true' if kind == 'false' else 'false'),
                '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))]',
                '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "' + kind + '"]))]',
                nullable(kind)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
            derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])'),
                '~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]]')]
        raw_identifier = 'NIdentifier (BYTES text_return) metadata_return'
        raw_union = 'NUnionType (SEQUENCE ([' + raw_identifier + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return'
        derived += ['~' + header.replace('phpType18,', raw_identifier + ','),
            '~' + header.replace('phpType18,', raw_union + ','),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            '~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
        raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw_union + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        derived += ['~$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([' + raw_parameter + ']), pfunction_producer.SIGNATURE[.RETURNS = eps])']
        for literal_kind in ('false', 'true'):
            for strict in ('false', 'true'):
                for accepted in ('PNULL', 'PBOOL ' + literal_kind):
                    derived += ['$typed_conversion_at(S_return, ' + nullable(literal_kind) + ', ' + accepted + ', ' + strict + ') = TYPEVALUE (' + accepted + ')']
                for rejected in ('PBOOL ' + ('true' if literal_kind == 'false' else 'false'), 'PINT 0', 'PINT 1', 'PSTRING eps', 'PFLOAT 0'):
                    derived += ['$typed_conversion_at(S_return, ' + nullable(literal_kind) + ', ' + rejected + ', ' + strict + ') = TYPEREJECT']
        for name in ('receive', 'return', 'notice'):
            stage = 'S_' + name
            derived += ['S_zero_' + name + ' = $drive(' + stage + ', 0)',
                'S_zero_' + name + '.COMPLETION = BUDGET /\\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + stage,
                '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + stage + ', 2)']
    return result, derived


def receive_priority(initial, case):
    reached, derived = formal_prior.priority(initial, 1)
    result = []
    for line in reached:
        line = line.replace('psparam.TYPE = [(PTBRANCH ([PTBUILTIN "false"]))]', 'psparam.TYPE = ' + nullable('false'))
        if line.startswith('phpType17 = '):
            line = line.replace('(NIdentifier (BYTES text_type) metadata_type)',
                                '(NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable)')
        for old, new in ((6, 9), (7, 10), (8, 11)):
            line = line.replace(', ' + str(old) + ',', ', ' + str(new) + ',').replace(', ' + str(old) + ')', ', ' + str(new) + ')')
        result.append(line)
    return result, derived


def return_priority(initial, case):
    reached, derived = prior.priority(initial, case)
    result = []
    for line in reached:
        line = line.replace('pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "true"]))]',
                            'pfunction_producer.SIGNATURE.RETURNS = ' + nullable('true'))
        if line.startswith('phpType18 = '):
            line = 'phpType18 = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_nullable_return'
        result.append(line)
    return result, derived


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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.return_prior.__file__), Path(formal_prior.__file__), Path(formal_prior.prior.__file__)]
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
            conditions, current_derived = normal(initial, case, args.front) if index < 2 else (receive_priority(initial, case) if index == 2 else return_priority(initial, case))
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scfr_case' + str(i) + '()\n' for i in range(4)))
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
    print('cv-nullable-literal-bool-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
