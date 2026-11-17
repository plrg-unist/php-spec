#!/usr/bin/env python3
"""Ground ordered bare-global FORMAL unions at actual array and eight-member frontiers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import cv_fqn_stdclass_iterable_formal_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_ordered_stdclass_formal_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('NAMES_MAKE', '[$ptascii("make")]').replace('NAMES_TAKE', '[$ptascii("take")]')
PREFIX += r"""
dec $ord_receive_ready(pstate) : bool
def $ord_receive_ready(S) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("make")
def $ord_receive_ready(S) = false -- otherwise
dec $ord_receive_seek(pstate, nat) : pstate
def $ord_receive_seek(S, n) = S -- if $ord_receive_ready(S) \/ n = 0 \/ S.TODO = eps
def $ord_receive_seek(S, n) = $ord_receive_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$ord_receive_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ord_receive_seek(S, n) = S -- otherwise
"""


def reached(case, front):
    lines = []
    for line in prior.reached(case, True):
        if line.startswith('phpType17 = '):
            line = line.replace('NNameFullyQualified', 'NName', 1)
        if line.startswith('pfunction_producer.NAME = '):
            line = 'pfunction_producer.NAME = $ptascii("make")'
        if line.startswith('S_return = '):
            line = line.replace('$ir_seek(S_initial,', '$ir_seek(S_received,', 1)
        lines.append(line)
    value = 'PARRAY n_entry' if case['cv_arity'] == 1 else 'PINT 5'
    receive = ['S_receive = $ord_receive_seek(S_initial, 5000)[.COMPLETION = NORMAL]',
        '$ord_receive_ready(S_receive)', 'S_receive.TODO = [TYPE_RECEIVE porigin_receive 0]',
        '$receiving_function(S_receive, porigin_receive) = (pfunction_producer)',
        'pfunction_producer.SIGNATURE.PARAMETERS = ' + ('[psparam]' if case['cv_arity'] == 1 else '[psparam, psparam_other]'),
        '$typed_receive_valid(S_receive, porigin_receive, 0)',
        ('' if case['cv_arity'] > 1 else '~') + '$typed_caller_strict(S_receive)',
        '$lookup(S_receive.ENV, $ptascii("saved")) = (n_receive)',
        'S_receive.GLOBALTABLE = (psymboltable_caller)',
        '$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_entry_cell)',
        'n_receive =/= n_entry_cell',
        'S_receive.STORE[n_receive] = DEFINED (' + value + ')',
        'S_receive.STORE[n_entry_cell] = DEFINED (' + value + ')',
        '~$typed_parameter_source(S_receive, psparam)',
        '$typed_parameter_conversion(S_receive, psparam, ' + value + ') = TYPEVALUE (' + value + ')',
        '$parameter_backing_at(S_receive.PARAMETERBACKINGS, n_receive) = eps',
        r'$propref_at(S_receive.PROPREFS, n_receive) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_receive) = eps',
        r'$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)',
        'S_received = $drive(S_receive, 1)[.COMPLETION = NORMAL]',
        r'S_received.STORE = S_receive.STORE /\ S_received.ARRAYS = S_receive.ARRAYS']
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)'
    return lines[:1] + receive + lines[1:] + ['n_formal = n_receive', 'n_entry_cell = n_caller', r'pfunction_producer.ENV.NAMESPACE = eps /\ pfunction_producer.ENV.CLASSES = eps', ('~' if front else '') + scoped]


def completed(case):
    return prior.completed(case)


def controls(case):
    shape = prior.formal_proof(case)[0].removeprefix('phpType17 = ').replace('NNameFullyQualified', 'NName', 1)
    view = shape.replace('NName ', 'NNameFullyQualified ', 1)
    signature = 'pfunction_producer.SIGNATURE'
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, ' + signature + ')'
    raw_parameters = lambda value: 'SEQUENCE ([' + value + (', phpType17_other' if case['cv_arity'] > 1 else '') + '])'
    proof = lambda value: scoped.replace('phpType16,', raw_parameters(value) + ',', 1)
    typed = lambda value, members, name=case['class_formal']: proof(value).replace(signature + ')', signature + '[.PARAMETERS = [psparam[.TYPE = ' + prior.branches(members, name) + ']' + (', psparam_other' if case['cv_arity'] > 1 else '') + ']])')
    parameter = lambda members, name=case['class_formal'], tag='NName': 'NParam (SEQUENCE eps) (INTEGER 0) (' + prior.raw(members, name, tag) + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    lines = ['$reference_notice_producer_global_parameter_view(phpType17) = (' + view + ')',
        '$reference_notice_producer_global_parameter_view(' + view + ') = (' + view + ')', proof(view),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]],', 1),
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for members in (['class', 'null'], ['int', 'class'], ['iterable', 'class'], ['class', 'array'],
            ['callable', 'int', 'class', 'iterable', 'float', 'true', 'string', 'null']):
        lines.append(typed(parameter(members), members))
    lines.append('~' + typed(parameter(['class', 'null']), ['class']))
    for members in (['class', 'class'], ['class', 'array', 'iterable'], ['class', 'object'], ['class', 'mixed'],
            ['class', 'void'], ['class', 'int', 'int'], ['class', 'bool', 'false'], ['class', 'true', 'false']):
        lines.append('~' + typed(parameter(members), members))
    for members in (case['formal_members'][::-1], case['formal_members'][:-1], case['formal_members'] + ['null']):
        lines.append('~' + typed(shape, members))
    for tag in ('NNameRelative', 'NIdentifier'):
        changed = parameter(case['formal_members'], tag=tag)
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + typed(changed, case['formal_members'])]
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00'):
        changed = parameter(case['formal_members'], name=name)
        rejected = typed(changed, case['formal_members'], name).replace('$ptascii(' + json.dumps(name) + ')', '[' + ', '.join(map(str, name.encode())) + ']')
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + rejected]
    for before, after in (('metadata_formal_union', 'eps'), ('metadata_parameter', 'eps'), ('metadata_formal0', 'eps')):
        lines.append('$reference_notice_producer_global_parameter_view(' + shape.replace(before, after) + ') = (' + view.replace(before, after) + ')')
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN true) (BOOLEAN false)'),
            ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN false) (BOOLEAN true)'),
            (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) ')):
        changed = shape.replace(before, after, 1)
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + view.replace(before, after, 1) + ')', '~' + proof(changed)]
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged ordered bare formal default"'):
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = [psparam[' + update + ']' + (', psparam_other' if case['cv_arity'] > 1 else '') + ']])'))
    value = 'PARRAY n_entry' if case['cv_arity'] == 1 else 'PINT 5'
    for strict in ('false', 'true'):
        lines.append('$typed_conversion_at(S_receive, psparam.TYPE, ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')')
    for stage in ('receive', 'return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return lines


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
    paths = [Path(__file__), CATALOGUE, provenance]
    paths += sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    specs, reached_lines, derived_lines = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:2]):
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
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $ir_case' + str(index) + '() : bool\ndef $ir_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $ir_case' + str(index) + '()\n' for index in range(2)))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases[:2]], unchanged_reception_controls=[cases[2]['id']], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-fqn-stdclass-iterable-formal-front' if args.front else 'cv-fqn-stdclass-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
