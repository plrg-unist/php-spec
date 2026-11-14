#!/usr/bin/env python3
"""Reach iterable receives and returns, including real Generator and USER Iterator values."""
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

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('runtime_iterable_alias_cases.json')
ITERABLE = '[(PTBRANCH ([PTBUILTIN "iterable"]))]'
PREFIX = r"""
dec $ia_output(pevent*) : ptbytes
def $ia_output(eps) = eps
def $ia_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ia_output(pevent*)
dec $ia_ready(pstate, nat) : bool
def $ia_ready(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("RuntimeIterableGenerator94\\keep"), $ptascii("RuntimeIterableUser94\\keep"), $ptascii("RuntimeIterableNullable94\\keep")]
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
def $ia_ready(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("RuntimeIterableGenerator94\\keep"), $ptascii("RuntimeIterableUser94\\keep"), $ptascii("RuntimeIterableNullable94\\keep")]
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
def $ia_ready(S, n_stage) = false -- otherwise
dec $ia_seek(pstate, nat, nat) : pstate
def $ia_seek(S, n_stage, n) = S -- if $ia_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $ia_seek(S, n_stage, n) = $ia_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ia_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ia_seek(S, n_stage, n) = S -- otherwise
"""


def returns(case):
    return '[(PTBRANCH ([PTBUILTIN "iterable"])), (PTBRANCH ([PTBUILTIN "null"]))]' if case['nullable_return'] else ITERABLE


def reached(case, front):
    stage = 0 if case['formal_typed'] else 1
    expected = 'TYPEREJECT' if front else 'TYPEVALUE pvalue_original'
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_value = $ia_seek(S_initial, ' + str(stage) + ', 5000)[.COMPLETION = NORMAL]',
        '$ia_ready(S_value, ' + str(stage) + ')',
        'S_value.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S_value), pcallcontext.FUNCTION) = (pfunction)',
        'pfunction.NAME = $ptascii(' + json.dumps(case['namespace'] + '\\keep') + ')',
        'pfunction.SIGNATURE.PARAMETERS = [psparam]',
        r'psparam.NAME = $ptascii("saved") /\ ~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE',
        'psparam.TYPE = ' + (ITERABLE if case['formal_typed'] else 'eps'),
        'pfunction.SIGNATURE.RETURNS = ' + returns(case),
        ('pfunction.CODE.STRICT' if case['caller_strict'] else '~pfunction.CODE.STRICT'),
        '$ppsupported_signature(pfunction.SIGNATURE)',
        '$lookup(S_value.ENV, $ptascii("saved")) = (n_saved)',
        'S_value.STORE[n_saved] = DEFINED pvalue_original',
        'pvalue_original = POBJECT n_object',
        'S_value.GLOBALTABLE = (psymboltable_caller)',
        '$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)',
        r'S_value.STORE[n_x] = DEFINED pvalue_original /\ S_value.STORE[n_copy] = DEFINED pvalue_original',
        r'n_saved =/= n_x /\ n_saved =/= n_copy',
        '~(n_saved <- S_value.REFCELLS)',
        r'S_value.PROPREFS = eps /\ S_value.REFCOERCIONS = eps /\ S_value.PARAMETERBACKINGS = eps',
        r'$heap_valid($heap_graph(S_value)) /\ $call_descriptors_valid(S_value)',
        '~$typed_exact(' + ITERABLE + ', pvalue_original)',
        ('~' if front else '') + '$typed_object_exact(S_value, ' + ITERABLE + ', pvalue_original)',
        '$typed_class_type(' + ITERABLE + ', $ptascii("Traversable")) = ' + str(not front).lower()]
    if case['value_kind'] == 'generator':
        lines += ['$generator_object(S_value, n_object)']
    else:
        lines += ['$object_class_origin(S_value, n_object) = (porigin_class)',
            '$class_origin_matches(S_value, porigin_class, $ptascii("Traversable"), |S_value.CLASSES|)',
            ('~' if front else '') + '$typed_class_branch_match(S_value, PTBRANCH ([PTBUILTIN "iterable"]), porigin_class, |S_value.CLASSES|)']
    if case['formal_typed']:
        lines += ['S_value.TODO = (TYPE_RECEIVE porigin_receive 0) :: ptask_tail*',
            '$typed_receive_valid(S_value, porigin_receive, 0)',
            '$typed_parameter_conversion(S_value, psparam, pvalue_original) = ' + expected]
    else:
        lines += ['S_value.TODO = (RETURN_VALUE z_return) :: ptask_tail*',
            '$typed_return_task_valid(S_value, z_return)',
            '$typed_conversion_at(S_value, ' + returns(case) + ', pvalue_original, pfunction.CODE.STRICT) = ' + expected]
    if front:
        output = 'N;T;Z;' if case['formal_typed'] else 'B;M;T;M;N:1;Z;'
        lines += ['S_pre_full = $drive(S_value, 10000)',
            r'S_pre_full.COMPLETION = NORMAL /\ S_pre_full.TODO = eps',
            '$ia_output(S_pre_full.EVENTS) = $ptascii(' + json.dumps(output) + ')']
    return lines


def completed(case):
    lines = []
    if case['formal_typed']:
        lines += ['S_return = $ia_seek($drive(S_value, 1)[.COMPLETION = NORMAL], 1, 5000)[.COMPLETION = NORMAL]',
            '$ia_ready(S_return, 1)',
            'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
            '$typed_return_task_valid(S_return, z_return)',
            '$typed_conversion_at(S_return, ' + returns(case) + ', pvalue_original, pfunction.CODE.STRICT) = TYPEVALUE pvalue_original']
    else:
        lines += ['S_return = S_value']
    lines += ['S_full = $drive(S_return, 10000)',
        r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
        '$ia_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
        r'S_full.STORE[n_x] = DEFINED pvalue_original /\ S_full.STORE[n_copy] = DEFINED pvalue_original',
        '~((HCELL n_saved) <- S_full.ALLOCATIONS)',
        r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']
    return lines


def controls(case):
    result = ['$ptclassview(PTBRANCH ([PTBUILTIN "iterable"])) = PTBRANCH ([PTCLASS ($ptascii("Traversable"))])',
        '$ptmasks(' + ITERABLE + ') = ["array"]']
    for kind in ('null', 'true', 'false', 'bool', 'int', 'float', 'string', 'array', 'mixed', 'void', 'never', 'object', 'callable'):
        branch = 'PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + '])'
        result += ['$ptclassview(' + branch + ') = ' + branch,
            '~$typed_class_branch(' + branch + ', $ptascii("Traversable"))']
    for name in ('Traversable', 'traversable', 'TRAVERSABLE'):
        result += ['$typed_class_branch(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]), $ptascii("Traversable"))']
    for value in ('PINT 17', 'PBOOL true', 'PFLOAT $float_of_int(2)', 'PSTRING ($ptascii("17"))'):
        for strict in ('false', 'true'):
            result += ['$typed_conversion_at(S_value, ' + ITERABLE + ', ' + value + ', ' + strict + ') = TYPEREJECT']
    result += ['$typed_conversion_at(S_value, ' + returns(case) + ', PNULL, false) = ' + ('TYPEVALUE PNULL' if case['nullable_return'] else 'TYPEREJECT'),
        'S_zero = $drive(S_value, 0)',
        r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_value',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_value, 2)']
    return result


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
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $cn_case' + str(index) + '() : bool\ndef $cn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cn_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('runtime-iterable-alias-front' if args.front else 'runtime-iterable-alias-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
