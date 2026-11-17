#!/usr/bin/env python3
"""Ground builtin iterable-union receives, caller aliases and private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import cv_fqn_stdclass_iterable_return_producer_reference_notice_review_state as prior
import cv_primitive_fqn_stdclass_producer_reference_notice_review_state as mixed

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_union_iterable_formal_producer_reference_notice_review_cases.json')
single, multi, floating = prior.single, prior.multi, prior.floating
PREFIX = prior.PREFIX + mixed.PREFIX.replace('ReviewFqnPrimitive81', 'ReviewMixedBuiltinIterableFormal114') + r'''
dec $fr_ready(pstate) : bool
def $fr_ready(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- NAMES_MAKE
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: eps
def $fr_ready(S) = false -- otherwise
dec $fr_seek(pstate, nat) : pstate
def $fr_seek(S, n) = S -- if $fr_ready(S) \/ n = 0 \/ S.TODO = eps
def $fr_seek(S, n) = $fr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$fr_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fr_seek(S, n) = S -- otherwise
'''


def formal_proof(field, variable, members, name, byref, primary=None):
    atoms, facts = [], []
    for index, kind in enumerate(members):
        text = 'text_' + field + '_member_' + str(index)
        metadata = 'metadata_' + field + '_member_' + str(index)
        atoms.append(('NNameFullyQualified' if kind == 'class' else 'NIdentifier') + ' (BYTES ' + text + ') ' + metadata)
        facts.append('$base64(' + text + ') = $ptascii(' + json.dumps(name) + ')' if kind == 'class' else
            '$ptlc($base64(' + text + ')) = $ptascii(' + json.dumps(kind) + ')')
        if kind == 'class' or kind == primary:
            alias = 'class' if kind == 'class' else 'type'
            facts += ['text_' + field + '_' + alias + ' = ' + text,
                'metadata_' + field + '_' + alias + ' = ' + metadata]
    return [variable + ' = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([' + ', '.join(atoms) +
        '])) metadata_' + field + '_union) (BOOLEAN ' + str(byref).lower() +
        ') (BOOLEAN false) phpType10_' + field + ' ABSENT (SEQUENCE eps) metadata_' + field + '_parameter'] + facts


def receive(case):
    signature = 'pfunction_producer.SIGNATURE'
    normalized = prior.branches(case['formal_members'], case.get('class_formal', ''))
    original = '(POBJECT n_old)' if case['role'] == 'object' else 'pvalue_original'
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_receive = $fr_seek(S_initial, 5000)[.COMPLETION = NORMAL]', '$fr_ready(S_receive)',
        'S_receive.CURRENT = (pcallcontext_receive)',
        '$function_at($all_functions(S_receive), pcallcontext_receive.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii(' + json.dumps(case['namespace'] + '\\make') + ')',
        signature + '.PARAMETERS = [psparam]', 'psparam.NAME = $ptascii("saved")',
        'psparam.TYPE = ' + normalized, 'psparam.BYREF = ' + str(case['formal_byref']).lower(),
        r'psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE',
        '$typed_receive_valid(S_receive, pfunction_producer.ORIGIN, 0)',
        ('$typed_caller_strict(S_receive)' if case.get('caller_strict') else '~$typed_caller_strict(S_receive)'),
        '$lookup(S_receive.ENV, $ptascii("saved")) = (n_receive)',
        'S_receive.STORE[n_receive] = DEFINED ' + original,
        'S_receive.GLOBALTABLE = (psymboltable_receive)',
        '$lookup(psymboltable_receive.ENV, $ptascii("x")) = (n_caller_receive)',
        '$lookup(psymboltable_receive.ENV, $ptascii("alias")) = (n_caller_receive)',
        'S_receive.STORE[n_caller_receive] = DEFINED ' + original,
        'n_receive ' + ('=' if case['formal_byref'] else '=/=') + ' n_caller_receive',
        '$origin_node(S_receive.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)']
    lines += formal_proof('one', 'phpType17', case['formal_members'], case.get('class_formal', ''), case['formal_byref'])
    if case['role'] == 'object':
        return lines + ['$typed_parameter_conversion(S_receive, psparam, POBJECT n_old) = TYPEVALUE (POBJECT n_old)',
            'S_received_budget = $drive_steps(S_receive, 1)', 'S_received_budget.COMPLETION = BUDGET',
            'S_received = S_received_budget[.COMPLETION = NORMAL]',
            'S_received.STORE[n_receive] = DEFINED (POBJECT n_old)',
            'S_received.STORE[n_caller_receive] = DEFINED (POBJECT n_old)']
    return lines + ['$string_bytes(pvalue_original) = ($ptascii("17"))', '$string_carrier_valid(S_receive, pvalue_original)',
        '$typed_parameter_conversion(S_receive, psparam, pvalue_original) = TYPEREJECT',
        'S_checked_receive = $typed_parameter_value(S_receive, pfunction_producer, 0, pvalue_original)',
        'S_checked_receive.COMPLETION = THROWN "TypeError" ptbytes_receive_error z_receive_error',
        'S_full = $drive(S_receive, 10000)',
        r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
        '$sr_quiet(S_full.EVENTS)', '$sr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
        '$lookup(S_full.ENV, $ptascii("x")) = eps', '$lookup(S_full.ENV, $ptascii("alias")) = eps',
        '$lookup(S_full.ENV, $ptascii("r")) = eps',
        r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']


def formal_controls(case):
    if case['role'] != 'object':
        return []
    signature = 'pfunction_producer.SIGNATURE[.RETURNS = eps]'
    args = '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE (['
    fold = '$reference_notice_producer_iterable_return_union_members('
    def proof(members, normalized=None, tag='NIdentifier', patch=''):
        normalized = prior.branches(members, '') if normalized is None else normalized
        raw = prior.raw(members, '', builtin_tag=tag)
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_one ABSENT (SEQUENCE eps) metadata_one_parameter'
        return args + parameter + ']), ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + normalized + ']' + patch + ']])'
    valid = [['iterable', kind] for kind in ('object', 'callable', 'int', 'float', 'string', 'null', 'bool', 'false', 'true')]
    valid += [members[::-1] for members in valid]
    valid += [['callable', 'object', 'iterable', 'float', 'int', boolean, 'string', 'null'] for boolean in ('bool', 'false', 'true')]
    lines = [proof(members) for members in valid]
    for members in (['iterable', 'array'], ['iterable', 'object', 'array'], ['iterable', 'iterable'],
            ['iterable', 'int', 'int'], ['iterable', 'bool', 'false'], ['iterable', 'false', 'true'],
            ['iterable', 'mixed'], ['iterable', 'void'], ['iterable', 'never']):
        lines.append('~' + proof(members))
    members = case['formal_members']
    for wrong in (prior.branches(members[::-1], ''), prior.branches(members[:-1], ''), prior.branches(members + ['null'], '')):
        lines.append('~' + proof(members, wrong))
    for tag in ('NName', 'NNameRelative', 'NNameFullyQualified'):
        lines.append('~' + proof(members, tag=tag))
    for update in ('.BYREF = true', '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged builtin iterable formal default"'):
        lines.append('~' + proof(members, patch='[' + update + ']'))
    normal = proof(members)
    for before, after in (('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_one_parameter]))'),
            ('NParam (SEQUENCE eps) (INTEGER 0)', 'NParam (SEQUENCE eps) (INTEGER 1)'),
            ('(BOOLEAN false) (BOOLEAN false) phpType10_one', '(BOOLEAN true) (BOOLEAN false) phpType10_one'),
            ('(BOOLEAN false) (BOOLEAN false) phpType10_one', '(BOOLEAN false) (BOOLEAN true) phpType10_one')):
        lines.append('~' + normal.replace(before, after, 1))
    for class_tag in ('NNameFullyQualified', 'NName', 'NNameRelative'):
        lines.append('~' + fold + prior.nodes(['class', 'iterable'], 'stdClass', class_tag=class_tag) + ', ' + prior.branches(['class', 'iterable'], 'stdClass') + ', eps)')
    lines += ['~$typed_receive_valid(S_receive, pfunction_producer.ORIGIN, 1)',
        'S_zero_receive = $drive(S_receive, 0)',
        r'S_zero_receive.COMPLETION = BUDGET /\ S_zero_receive[.COMPLETION = NORMAL] = S_receive']
    return lines


def conditions(initial, case, index, front):
    if case['role'] == 'receive':
        return [initial] + receive(case), []
    if case['role'] == 'mixed':
        reached, derived = mixed.normal(initial, case, 0, front)
        result = []
        for line in reached:
            if line in ('$base64(text_first_class) = $ptascii("sTdClAsS")', '$base64(text_last_class) = $ptascii("sTdClAsS")'):
                continue
            field = next((field for field in ('first', 'last') if line.startswith('phpType17_' + field + ' = NParam ')), None)
            if field is None:
                result.append(line)
            else:
                i = 0 if field == 'first' else 1
                result += formal_proof(field, 'phpType17_' + field, case['formal_members'][i], case.get('class_formal', ''), i == 1, case['formal_kinds'][i])
        return result, derived
    result = [initial] + receive(case)
    for line in prior.reached(case, front):
        if line.startswith('S_return = $sr_seek(S_initial, '):
            line = line.replace('$sr_seek(S_initial, ', '$sr_seek(S_received, ')
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + prior.branches(case['formal_members'], case.get('class_formal', ''))
        if front and line.startswith('$reference_notice_producer_arguments('):
            line = '~' + line
        result.append(line)
    if not front:
        result += prior.completed(case)
    if front:
        return result, []
    derived = []
    for line in prior.controls(case):
        if line.startswith('phpType17 = NParam '):
            continue
        if line.startswith('~$reference_notice_producer_arguments(') and 'metadata_parameter' in line and 'PTCLASS' in line:
            line = line.removeprefix('~')
        line = line.replace('phpType10 ABSENT', 'phpType10_one ABSENT').replace('metadata_parameter', 'metadata_one_parameter')
        derived.append(line)
    return result, derived + formal_controls(case)

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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(mixed.__file__), Path(mixed.prior.__file__), Path(mixed.prior.prior.__file__), Path(single.__file__), Path(multi.__file__), Path(single.base.__file__), Path(floating.__file__), CATALOGUE, provenance]
    specs, reached_lines, derived_lines = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current, extra = conditions(initial, case, index, args.front)
            specs.append('dec $sr_case' + str(index) + '() : bool\ndef $sr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived_lines += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    prefix = PREFIX
    for marker, name in (('NAMES_MAKE', 'make'), ('NAMES_TAKE', 'take')):
        prefix = prefix.replace(marker, '[' + ', '.join('$ptascii(' + json.dumps(case['namespace'] + '\\' + name) + ')' for case in cases) + ']')
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $sr_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-builtin-union-iterable-formal-front' if args.front else 'cv-builtin-union-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
