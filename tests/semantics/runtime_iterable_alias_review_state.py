#!/usr/bin/env python3
"""Independently distinguish iterable array copies, Generator unions and inherited Iterators."""
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
CATALOGUE = Path(__file__).with_name('runtime_iterable_alias_review_cases.json')
ITERABLE = '[(PTBRANCH ([PTBUILTIN "iterable"]))]'
PREFIX = r"""
dec $ir_output(pevent*) : ptbytes
def $ir_output(eps) = eps
def $ir_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ir_output(pevent*)
dec $ir_ready(pstate, nat) : bool
def $ir_ready(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("RuntimeIterableArrayPeer94\\keep"), $ptascii("RuntimeIterableGeneratorUnionPeer94\\keep"), $ptascii("RuntimeIterableInheritedPeer94\\keep")]
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
def $ir_ready(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("RuntimeIterableArrayPeer94\\keep"), $ptascii("RuntimeIterableGeneratorUnionPeer94\\keep"), $ptascii("RuntimeIterableInheritedPeer94\\keep")]
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
def $ir_ready(S, n_stage) = false -- otherwise
dec $ir_seek(pstate, nat, nat) : pstate
def $ir_seek(S, n_stage, n) = S -- if $ir_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $ir_seek(S, n_stage, n) = $ir_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ir_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ir_seek(S, n_stage, n) = S -- otherwise
"""


def branches(*kinds):
    return '[' + ', '.join('PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + '])' for kind in kinds) + ']'


def formal(case):
    return branches('iterable', 'false') if case['role'] == 'generator_union' else ITERABLE


def returns(case):
    return branches('false', 'iterable') if case['role'] == 'generator_union' else ITERABLE


def reached(case, front):
    accepted = not front or case['value_kind'] == 'array'
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_value = $ir_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]',
        '$ir_ready(S_value, 0)',
        'S_value.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S_value), pcallcontext.FUNCTION) = (pfunction)',
        'pfunction.NAME = $ptascii(' + json.dumps(case['namespace'] + '\\keep') + ')',
        'pfunction.SIGNATURE.PARAMETERS = [psparam]',
        r'psparam.NAME = $ptascii("saved") /\ ~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE',
        'psparam.TYPE = ' + formal(case),
        'pfunction.SIGNATURE.RETURNS = ' + returns(case),
        ('pfunction.CODE.STRICT' if case['caller_strict'] else '~pfunction.CODE.STRICT'),
        '$ppsupported_signature(pfunction.SIGNATURE)',
        '$lookup(S_value.ENV, $ptascii("saved")) = (n_saved)',
        'S_value.STORE[n_saved] = DEFINED pvalue_original',
        'S_value.GLOBALTABLE = (psymboltable_caller)',
        '$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)',
        r'S_value.STORE[n_x] = DEFINED pvalue_original /\ S_value.STORE[n_copy] = DEFINED pvalue_original',
        r'n_saved =/= n_x /\ n_saved =/= n_copy',
        '~(n_saved <- S_value.REFCELLS)',
        r'S_value.PROPREFS = eps /\ S_value.REFCOERCIONS = eps /\ S_value.PARAMETERBACKINGS = eps',
        r'$heap_valid($heap_graph(S_value)) /\ $call_descriptors_valid(S_value)',
        'S_value.TODO = (TYPE_RECEIVE porigin_receive 0) :: ptask_tail*',
        '$typed_receive_valid(S_value, porigin_receive, 0)',
        '$typed_parameter_conversion(S_value, psparam, pvalue_original) = ' + ('TYPEVALUE pvalue_original' if accepted else 'TYPEREJECT')]
    if case['value_kind'] == 'array':
        lines += ['pvalue_original = PARRAY n_array',
            '$typed_exact(' + ITERABLE + ', pvalue_original)',
            '~$typed_object_exact(S_value, ' + ITERABLE + ', pvalue_original)']
    else:
        lines += ['pvalue_original = POBJECT n_object',
            '~$typed_exact(' + ITERABLE + ', pvalue_original)',
            ('~' if front else '') + '$typed_object_exact(S_value, ' + ITERABLE + ', pvalue_original)']
        if case['value_kind'] == 'generator':
            lines += ['$generator_object(S_value, n_object)']
        else:
            lines += ['$object_class_origin(S_value, n_object) = (porigin_class)',
                '$class_link_at(S_value.LINKEDPARENTS, porigin_class) = (SOURCE_PARENT porigin_parent)',
                '$class_origin_matches(S_value, porigin_class, $ptascii("Traversable"), |S_value.CLASSES|)',
                '$typed_class_branch_match(S_value, PTBRANCH ([PTCLASS ($ptascii("Traversable"))]), porigin_class, |S_value.CLASSES|)',
                ('~' if front else '') + '$typed_class_branch_match(S_value, PTBRANCH ([PTBUILTIN "iterable"]), porigin_class, |S_value.CLASSES|)']
    if front:
        output = case['native_stdout'] if accepted else ('N;T;M;F:1;U;Q;N:1;Z;' if case['role'] == 'generator_union' else 'N;T;Z;')
        lines += ['S_pre_full = $drive(S_value, 10000)',
            r'S_pre_full.COMPLETION = NORMAL /\ S_pre_full.TODO = eps /\ S_pre_full.CURRENT = eps /\ S_pre_full.FRAMES = eps',
            '$ir_output(S_pre_full.EVENTS) = $ptascii(' + json.dumps(output) + ')']
    return lines


def completed(case):
    lines = ['S_return = $ir_seek($drive(S_value, 1)[.COMPLETION = NORMAL], 1, 5000)[.COMPLETION = NORMAL]',
        '$ir_ready(S_return, 1)',
        'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        '$typed_return_task_valid(S_return, z_return)',
        '$typed_conversion_at(S_return, ' + returns(case) + ', pvalue_original, pfunction.CODE.STRICT) = TYPEVALUE pvalue_original',
        'S_full = $drive(S_return, 10000)',
        r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
        '$ir_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
        r'S_full.STORE[n_x] = DEFINED pvalue_original /\ S_full.STORE[n_copy] = DEFINED pvalue_original',
        '~((HCELL n_saved) <- S_full.ALLOCATIONS)',
        r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']
    if case['value_kind'] == 'array':
        lines += ['$lookup(S_full.ENV, $ptascii("r")) = (n_r)',
            'S_full.STORE[n_r] = DEFINED (PARRAY n_changed)',
            'n_changed =/= n_array',
            '$entry_lookup(S_full.ARRAYS[n_array].ITEMS, KINT 0) = (DIRECT (PINT 17))',
            '$entry_lookup(S_full.ARRAYS[n_changed].ITEMS, KINT 0) = (DIRECT (PINT 23))']
    return lines


def controls(case):
    lines = ['$ptclassview(PTBRANCH ([PTBUILTIN "iterable"])) = PTBRANCH ([PTCLASS ($ptascii("Traversable"))])',
        '$ptmasks(' + ITERABLE + ') = ["array"]',
        '~$typed_class_branch(PTBRANCH ([PTBUILTIN "iterable"]), $ptascii("Iterator"))',
        '~$typed_class_branch(PTBRANCH ([PTBUILTIN "iterable"]), $ptascii("stdClass"))',
        '~$typed_class_branch(PTBRANCH ([PTCLASS ($ptascii("Traversable")), PTCLASS ($ptascii("Countable"))]), $ptascii("Traversable"))',
        '~$ppsupported_types([PTBRANCH ([PTBUILTIN "iterable", PTCLASS ($ptascii("Traversable"))])])']
    for spelling in ('Traversable', 'TRAVERSABLE', 'traversable'):
        lines += ['$typed_class_branch(PTBRANCH ([PTBUILTIN "iterable"]), $ptascii(' + json.dumps(spelling) + '))']
    for kind in ('bool', 'array', 'callable', 'object', 'mixed'):
        branch = 'PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + '])'
        lines += ['$ptclassview(' + branch + ') = ' + branch,
            '~$typed_class_branch(' + branch + ', $ptascii("Traversable"))']
    for name in ('Iterator', 'stdClass'):
        branch = 'PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))])'
        lines += ['$ptclassview(' + branch + ') = ' + branch,
            '$typed_class_branch(' + branch + ', $ptascii(' + json.dumps(name) + '))']
    for strict in ('false', 'true'):
        for value in ('PNULL', 'PBOOL false', 'PINT 17', 'PSTRING ($ptascii("17"))'):
            lines += ['$typed_conversion_at(S_value, ' + ITERABLE + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        lines += ['$typed_conversion_at(S_value, ' + branches('iterable', 'null') + ', PNULL, ' + strict + ') = TYPEVALUE PNULL',
            '$typed_conversion_at(S_value, ' + branches('iterable', 'false') + ', PBOOL false, ' + strict + ') = TYPEVALUE (PBOOL false)']
    lines += ['~$typed_receive_valid(S_value, porigin_receive, 1)',
        'S_zero = $drive(S_value, 0)',
        r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_value',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_value, 2)']
    if case['value_kind'] == 'user_iterator':
        lines += ['~$typed_class_branch_match(S_value, PTBRANCH ([PTCLASS ($ptascii("stdClass"))]), porigin_class, |S_value.CLASSES|)',
            '~$typed_class_branch_match(S_value, PTBRANCH ([PTCLASS ($ptascii("Traversable")), PTCLASS ($ptascii("stdClass"))]), porigin_class, |S_value.CLASSES|)',
            '$typed_class_branch_match(S_value, PTBRANCH ([PTCLASS ($ptascii("Traversable")), PTCLASS ($ptascii("Iterator"))]), porigin_class, |S_value.CLASSES|)']
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
    print('runtime-iterable-alias-review-front' if args.front else 'runtime-iterable-alias-review-state', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
