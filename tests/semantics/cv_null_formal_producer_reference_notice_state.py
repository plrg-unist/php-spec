#!/usr/bin/env python3
"""Ground standalone null formals, ordinary aliases and private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_mixed_formal_producer_reference_notice_review_state as single
import cv_null_return_producer_reference_notice_state as multi
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_null_formal_producer_reference_notice_cases.json')
NULL = '[(PTBRANCH ([PTBUILTIN "null"]))]'
MIXED = '[(PTBRANCH ([PTBUILTIN "mixed"]))]'
PREFIX = (single.PREFIX.replace('ReviewNotice68\\\\Null', 'NullFormalAlias69')
    + multi.multi.PREFIX.replace('MultiCvNullableNull52', 'MultiCvNullFormal69')) + r'''
dec $cnf_ready(pstate) : bool
def $cnf_ready(S) = true -- if S.TODO = [TYPE_RECEIVE porigin 0]
def $cnf_ready(S) = false -- otherwise
dec $cnf_receive(pstate, nat) : pstate
def $cnf_receive(S, n) = S
  -- if $cnf_ready(S) \/ n = 0 \/ S.TODO = eps
def $cnf_receive(S, n) = $cnf_receive($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$cnf_ready(S) /\ S.TODO =/= eps /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cnf_receive(S, n) = S -- otherwise
'''


def normal(initial, case, index, front):
    if index == 0:
        reached, derived = single.normal(initial, case, 1, front)
        replacements = {'psparam.TYPE = ' + MIXED: 'psparam.TYPE = ' + NULL,
            '$ptlc($base64(text_formal)) = $ptascii("mixed")':
                '$ptlc($base64(text_formal)) = $ptascii("null")'}
        for old, new in replacements.items():
            assert reached.count(old) == 1
            reached = [new if line == old else line for line in reached]
        # The old normalized-null mismatch is now a matching canonical formal.
        derived = [line.replace('PTBUILTIN "null"', 'PTBUILTIN "mixed"')
            if line.startswith('~$reference_notice_producer_arguments(') and '.TYPE = ' + NULL in line else line
            for line in derived]
    else:
        reached = [initial] + multi.front_lines(1, case)
        old = 'psparam_first.TYPE = eps /\\ psparam_last.TYPE = eps'
        assert reached.count(old) == 1
        reached = ['psparam_first.TYPE = ' + NULL + r' /\ psparam_last.TYPE = eps' if line == old else line for line in reached]
        offset = reached.index('S_return = $mcn_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]')
        reached[offset:offset] = [
            'phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal) metadata_formal_type) (BOOLEAN false) (BOOLEAN false) phpType10_saved ABSENT (SEQUENCE eps) metadata_formal',
            'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_changed ABSENT (SEQUENCE eps) metadata_changed',
            '$ptlc($base64(text_formal)) = $ptascii("null")',
            'S_receive = $cnf_receive(S_args, 1000)[.COMPLETION = NORMAL]',
            'S_receive.TODO = [TYPE_RECEIVE porigin_receive 0]',
            '$receiving_function(S_receive, porigin_receive) = (pfunction_producer)',
            '$typed_receive_valid(S_receive, porigin_receive, 0)',
            '~$typed_caller_strict(S_receive)',
            '$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)',
            'S_receive.STORE[n_formal] = DEFINED PNULL',
            r'n_formal =/= n_original_x /\ ~(n_formal <- S_receive.REFCELLS)',
            '~$typed_parameter_source(S_receive, psparam_first)',
            '$typed_parameter_conversion(S_receive, psparam_first, PNULL) = TYPEVALUE PNULL',
            '$parameter_backing_at(S_receive.PARAMETERBACKINGS, n_formal) = eps',
            r'$propref_at(S_receive.PROPREFS, n_formal) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_formal) = eps',
            'S_received = $drive(S_receive, 1)[.COMPLETION = NORMAL]',
            r'S_received.STORE = S_receive.STORE /\ S_received.ARRAYS = S_receive.ARRAYS',
            '$heap_valid($heap_graph(S_received))']
        reached = ['~' + line if line.startswith('$reference_notice_producer_arguments(') and '.RETURNS = eps' in line else line for line in reached]
        derived = []
        if not front:
            reached = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line == '~$positional_reference_notice_pending(S_pre)' or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) else line for line in reached]
            reached += multi.full_lines(1, case)
            derived += multi.controls(1)
    if not front:
        derived += controls(index)
    return reached, derived


def controls(index):
    actuals = '([phpType7])' if index == 0 else '([phpType7_first, phpType7_last])'
    parameters = '([phpType17])' if index == 0 else '([phpType17_first, phpType17_last])'
    slot = 'psparam' if index == 0 else 'psparam_first'
    tail = '' if index == 0 else ', psparam_last'
    raw_tail = '' if index == 0 else ', phpType17_last'
    signature = 'pfunction_producer.SIGNATURE[.RETURNS = eps]'
    proof = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE '
    byref = 'true' if index == 0 else 'false'
    metadata_type, variable, metadata_parameter = (('metadata_type', 'phpType10', 'metadata_parameter')
        if index == 0 else ('metadata_formal_type', 'phpType10_saved', 'metadata_formal'))
    raw = 'NIdentifier (BYTES "blVsTA==") ' + metadata_type
    param = 'NParam (SEQUENCE eps) (INTEGER 0) __TYPE__ (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata_parameter
    matched = proof + '([' + param.replace('__TYPE__', '(' + raw + ')') + raw_tail + ']), ' + signature + ')'
    lines = [matched]
    for kind in ('array', 'int', 'float', 'bool', 'string', 'mixed', 'object'):
        lines += ['~' + proof + parameters + ', ' + signature + '[.PARAMETERS = [' + slot + '[.TYPE = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]]' + tail + ']])']
    for raw_type, normalized in [
            ('NNullableType (' + raw + ') ' + metadata_parameter, '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + raw + ', ' + raw + '])) ' + metadata_parameter, '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NName (BYTES "bnVsbA==") ' + metadata_parameter, NULL)]:
        lines += ['~' + proof + '([' + param.replace('__TYPE__', '(' + raw_type + ')') + raw_tail + ']), ' + signature + '[.PARAMETERS = [' + slot + '[.TYPE = ' + normalized + ']' + tail + ']])']
    for update in ('.BYREF = ' + ('false' if index == 0 else 'true'), '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged null default"'):
        lines += ['~' + proof + parameters + ', ' + signature + '[.PARAMETERS = [' + slot + '[' + update + ']' + tail + ']])']
    for strict in ('false', 'true'):
        lines += ['$typed_conversion_at(S_receive, ' + NULL + ', PNULL, ' + strict + ') = TYPEVALUE PNULL']
        for value in ('PBOOL false', 'PINT 0', 'PFLOAT 0', 'PSTRING eps', 'PARRAY 0', 'POBJECT 0'):
            lines += ['$typed_conversion_at(S_receive, ' + NULL + ', ' + value + ', ' + strict + ') = TYPEREJECT']
    return lines


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
    paths = [Path(__file__), Path(single.__file__), Path(multi.__file__), Path(multi.single.__file__), Path(multi.multi.__file__), CATALOGUE, provenance]
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
            conditions, current_derived = normal(initial, case, index, args.front)
            case_specs.append('dec $cnf_case' + str(index) + '() : bool\ndef $cnf_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
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
    fixture.write_text(PREFIX + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $cnf_case0()\n  -- if $cnf_case1()\n')
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
    print('cv-null-formal-front' if args.front else 'cv-null-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
