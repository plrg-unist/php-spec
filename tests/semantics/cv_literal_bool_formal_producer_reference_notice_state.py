#!/usr/bin/env python3
"""Ground required false/true formals, exact tags and ordinary alias replacement."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_null_formal_producer_reference_notice_state as prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_literal_bool_formal_producer_reference_notice_cases.json')
single, multi = prior.single, prior.multi
MIXED = prior.MIXED
PREFIX = (prior.PREFIX.replace('NullFormalAlias69', 'FalseFormalAlias70')
    .replace('MultiCvNullFormal69', 'MultiCvLiteralBoolFormal70'))


def literal(kind):
    return '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))]'


def normal(initial, case, index, front):
    if index == 0:
        reached, _ = single.normal(initial, case, 1, front)
        replacements = {
            'psparam.TYPE = ' + MIXED: 'psparam.TYPE = ' + literal('false'),
            'pvalue_input = PNULL': 'pvalue_input = PBOOL false',
            '~pfunction_producer.SIGNATURE.BYREF /\\ pfunction_producer.CODE.STRICT = false':
                '~pfunction_producer.SIGNATURE.BYREF /\\ pfunction_producer.CODE.STRICT = true',
            '~$typed_caller_strict(S_receive)': '$typed_caller_strict(S_receive)',
            '$ptlc($base64(text_formal)) = $ptascii("mixed")':
                '$ptlc($base64(text_formal)) = $ptascii("false")'}
    else:
        reached, _ = prior.normal(initial, case, 1, front)
        reached = [line.replace('PNULL', '(PBOOL false)') for line in reached]
        replacements = {
            'S_args.STORE[n_y] = DEFINED (PINT 5)': 'S_args.STORE[n_y] = DEFINED (PBOOL true)',
            'psparam_first.TYPE = ' + prior.NULL + r' /\ psparam_last.TYPE = eps':
                'psparam_first.TYPE = ' + literal('false') + r' /\ psparam_last.TYPE = ' + literal('true'),
            'pfunction_producer.SIGNATURE.RETURNS = ' + prior.NULL + r' /\ ~pfunction_producer.SIGNATURE.BYREF':
                'pfunction_producer.SIGNATURE.RETURNS = ' + MIXED + r' /\ ~pfunction_producer.SIGNATURE.BYREF',
            '$ptlc($base64(text_return)) = $ptascii("null")': '$ptlc($base64(text_return)) = $ptascii("mixed")',
            '$ptlc($base64(text_formal)) = $ptascii("null")': '$ptlc($base64(text_formal)) = $ptascii("false")',
            'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_changed ABSENT (SEQUENCE eps) metadata_changed':
                'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal_last) metadata_changed_type) (BOOLEAN true) (BOOLEAN false) phpType10_changed ABSENT (SEQUENCE eps) metadata_changed'}
    for old, new in replacements.items():
        assert reached.count(old) == 1, old
        reached = [new if line == old else line for line in reached]
    if index == 1:
        offset = reached.index('S_return = $mcn_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]')
        reached[offset:offset] = [
            '$ptlc($base64(text_formal_last)) = $ptascii("true")',
            'S_received.TODO = [TYPE_RECEIVE porigin_receive 1]',
            '$typed_receive_valid(S_received, porigin_receive, 1)',
            '$lookup(S_received.ENV, $ptascii("changed")) = (n_y)',
            'S_received.STORE[n_y] = DEFINED (PBOOL true)',
            '~$typed_parameter_source(S_received, psparam_last)',
            '$typed_parameter_conversion(S_received, psparam_last, PBOOL true) = TYPEVALUE (PBOOL true)',
            '$parameter_backing_at(S_received.PARAMETERBACKINGS, n_y) = eps',
            r'$propref_at(S_received.PROPREFS, n_y) = eps /\ $reference_coercion_at(S_received.REFCOERCIONS, n_y) = eps',
            'S_last = $drive(S_received, 1)[.COMPLETION = NORMAL]',
            r'S_last.STORE = S_received.STORE /\ S_last.PROPREFS = S_received.PROPREFS',
            '$heap_valid($heap_graph(S_last))']
    return reached, [] if front else controls(index)


def controls(index):
    actuals = '([phpType7])' if index == 0 else '([phpType7_first, phpType7_last])'
    parameters = '([phpType17])' if index == 0 else '([phpType17_first, phpType17_last])'
    slot = 'psparam' if index == 0 else 'psparam_first'
    tail = '' if index == 0 else ', psparam_last'
    raw_tail = '' if index == 0 else ', phpType17_last'
    signature = 'pfunction_producer.SIGNATURE[.RETURNS = eps]'
    proof = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE '
    byref = 'true' if index == 0 else 'false'
    meta, variable, metadata = (('metadata_type', 'phpType10', 'metadata_parameter')
        if index == 0 else ('metadata_formal_type', 'phpType10_saved', 'metadata_formal'))
    raw = 'NIdentifier (BYTES "ZkFsU2U=") ' + meta
    param = 'NParam (SEQUENCE eps) (INTEGER 0) __TYPE__ (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    lines = [proof + parameters + ', ' + signature + ')',
        proof + '([' + param.replace('__TYPE__', '(' + raw + ')') + raw_tail + ']), ' + signature + ')',
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'mixed', 'true', 'object'):
        lines += ['~' + proof + parameters + ', ' + signature + '[.PARAMETERS = [' + slot + '[.TYPE = ' + literal(kind) + ']' + tail + ']])']
    for raw_type, normalized in [
            ('NNullableType (' + raw + ') ' + metadata, '[(PTBRANCH ([PTBUILTIN "false"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + raw + ', NIdentifier (BYTES "aW50") ' + meta + '])) ' + metadata, '[(PTBRANCH ([PTBUILTIN "false"])), (PTBRANCH ([PTBUILTIN "int"]))]'),
            ('NUnionType (SEQUENCE ([' + raw + ', ' + raw + '])) ' + metadata, '[(PTBRANCH ([PTBUILTIN "false"])), (PTBRANCH ([PTBUILTIN "false"]))]'),
            ('NName (BYTES "ZmFsc2U=") ' + metadata, literal('false'))]:
        lines += [('' if raw_type.startswith('NNullableType') or '"aW50"' in raw_type else '~') + proof + '([' + param.replace('__TYPE__', '(' + raw_type + ')') + raw_tail + ']), ' + signature + '[.PARAMETERS = [' + slot + '[.TYPE = ' + normalized + ']' + tail + ']])']
    for update in ('.BYREF = ' + ('false' if index == 0 else 'true'), '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged literal default"'):
        lines += ['~' + proof + parameters + ', ' + signature + '[.PARAMETERS = [' + slot + '[' + update + ']' + tail + ']])']
    if index == 1:
        lines += ['~' + proof + parameters + ', ' + signature + '[.PARAMETERS = [psparam_first, psparam_last[.TYPE = ' + literal('false') + ']]])',
            '~' + proof + parameters + ', ' + signature + '[.PARAMETERS = [psparam_first, psparam_last[.BYREF = false]]])']
    for kind in ('false', 'true'):
        for strict in ('false', 'true'):
            lines += ['$typed_conversion_at(S_receive, ' + literal(kind) + ', PBOOL ' + kind + ', ' + strict + ') = TYPEVALUE (PBOOL ' + kind + ')']
            for value in ('PBOOL ' + ('true' if kind == 'false' else 'false'), 'PNULL', 'PINT 0', 'PINT 1', 'PFLOAT 0', 'PSTRING eps', 'PARRAY 0', 'POBJECT 0'):
                lines += ['$typed_conversion_at(S_receive, ' + literal(kind) + ', ' + value + ', ' + strict + ') = TYPEREJECT']
    for name in ('receive', 'return', 'notice'):
        cap = 'S_' + name
        lines += ['S_zero_' + name + ' = $drive(' + cap + ', 0)', 'S_zero_' + name + '.COMPLETION = BUDGET /\\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + cap,
            '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + cap + ', 2)']
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
    paths = [Path(__file__), Path(prior.__file__), Path(single.__file__), Path(multi.__file__), Path(multi.single.__file__), Path(multi.multi.__file__), CATALOGUE, provenance]
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
            case_specs.append('dec $clbf_case' + str(index) + '() : bool\ndef $clbf_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
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
    fixture.write_text(PREFIX + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $clbf_case0()\n  -- if $clbf_case1()\n')
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
    print('cv-literal-bool-formal-front' if args.front else 'cv-literal-bool-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
