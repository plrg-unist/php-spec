#!/usr/bin/env python3
"""Permanent compiled pool installation and lifetime invariants; no source activation."""
import base64
from collections import deque
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/semantics'))
import static_types as types


def seq(items): return '([' + ', '.join(items) + '])' if items else 'eps'
def path(index): return f'([PCINDEX {index}, PCFIELD 0])'
def constant(index, value): return f'PCONSTANT {path(index)} ({value})'
def array(values):
    return '{ITEMS '+seq([f'ENTRY (KINT {i}) (DIRECT ({v}))' for i,v in enumerate(values)])+', NEXT '+str(len(values))+'}'


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(ROOT/'tests/semantics'), 'numeric_runner.exe'], cwd=ROOT, check=True, timeout=120)
    runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    def fingerprint():
        return {'closure': types.syntax_validation.implementation_fingerprint(), 'runner': hashlib.sha256(runner.read_bytes()).hexdigest()}
    before = fingerprint()
    source = b'<?php '+b'[NAN];'*12
    frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')])
    adapter = types.Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)])
    try:
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert 'ast' in checked, checked
    finally: frontend.close(); adapter.close()
    unit = '$pcsource(71, '+checked['fixture']+')'
    initial = '$initial_state(NORMAL)'
    nan = 'PFLOAT 9221120237041090560'
    arrays = [array([nan]),array([nan]),array(['PARRAY 0','PARRAY 0']),array([]),array(['PINT 9'])]
    nodes = ['HARRAY 0','HARRAY 1','HARRAY 2','HARRAY 4']
    facts = [constant(0,'PARRAY 2'),constant(1,'PARRAY 0'),constant(2,'PARRAY 1')]
    existing = (initial+'[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 0)]), NEXT 1}, $array_empty(), $array_empty()]]'
        '[.STORE = [DEFINED (PARRAY 0)]][.ENV = [BIND ([97]) 0]][.ALLOCATIONS = [HCELL 0, HARRAY 0, HARRAY 2]]'
        '[.HELD = [HARRAY 2]][.RESULT = KNOWN (PARRAY 2)][.TODO = [DISCARD]][.ORIGIN = (PORIGIN 8 eps)]')
    install = f'$install_pool(S, U, {seq(arrays)}, {seq(nodes)}, {seq(facts)})'
    prefix = [f'U = {unit}',f'S = {existing}', f'S_pool = {install}']
    cases = [prefix + [
        'S_pool.COMPLETION = NORMAL','S_pool.STORE = S.STORE','S_pool.ENV = S.ENV','S_pool.HELD = S.HELD',
        'S_pool.RESULT = S.RESULT','S_pool.TODO = S.TODO','S_pool.ORIGIN = S.ORIGIN',
        'S_pool.SOURCES = [U]','|S_pool.ARRAYS| = 8',
        'S_pool.ARRAYS[0] = S.ARRAYS[0]','S_pool.ARRAYS[1] = S.ARRAYS[1]','S_pool.ARRAYS[2] = S.ARRAYS[2]',
        'S_pool.ARRAYS[5].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY 3)), ENTRY (KINT 1) (DIRECT (PARRAY 3))]',
        'S_pool.ALLOCATIONS = [HCELL 0, HARRAY 0, HARRAY 2, HARRAY 3, HARRAY 4, HARRAY 5, HARRAY 7]',
        '$heap_valid($heap_graph(S_pool))',
        '$pools_nodes(S_pool.POOLS) = [HARRAY 5, HARRAY 3, HARRAY 4]',
        '$pool_value(S_pool.POOLS, PORIGIN 71 '+path(0)+') = (PARRAY 5)',
        '$pool_value(S_pool.POOLS, PORIGIN 72 '+path(0)+') = eps',
        '$pool_value(S_pool.POOLS, PORIGIN 71 ([PCINDEX 11, PCFIELD 0])) = eps',
        'S_done = $prune_allocations($release_temporaries(S_pool))',
        'S_done.ALLOCATIONS = [HCELL 0, HARRAY 0, HARRAY 3, HARRAY 4, HARRAY 5]',
        'S_done.POOLS = S_pool.POOLS','S_done.SOURCES = S_pool.SOURCES','S_done.HELD = eps',
        '$heap_valid($heap_graph(S_done))',
        '$identity_apply(S_done, false, PARRAY 3, PARRAY 3, 1).RESULT = KNOWN (PBOOL true)',
        '$identity_apply(S_done, false, PARRAY 3, PARRAY 4, 1).RESULT = KNOWN (PBOOL false)',
        '$allocate_array(S_done, $array_empty()).RESULT = KNOWN (PARRAY 8)']]
    cases += [prefix + [
        'S_done = $drive(S_pool, 100)', 'S_done.COMPLETION = NORMAL', 'S_done.HELD = S_pool.HELD',
        'S_done.POOLS = S_pool.POOLS', '$heap_valid($heap_graph(S_done))',
        'S_more = $drive(S_done[.TODO = [DISCARD]][.RESULT = KNOWN (PARRAY 3)], 100)',
        'S_more.POOLS = S_pool.POOLS','S_more.ALLOCATIONS = S_done.ALLOCATIONS'],
        prefix + ['S_done = $drive(S_pool, 0)', 'S_done.COMPLETION = BUDGET', 'S_done.POOLS = S_pool.POOLS',
            'S_done.HELD = S_pool.HELD', '$drive(S_done[.COMPLETION = NORMAL],100) = $drive(S_pool,100)'],
        prefix + ['S_done = $drive(S_pool[.COMPLETION = THROWN "Error" eps 1], 100)',
            'S_done.POOLS = S_pool.POOLS','S_done.HELD = eps', '$heap_valid($heap_graph(S_done))'],
        prefix + ['S_done = $drive(S_pool[.COMPLETION = UNSUPPORTED "boundary"], 100)',
            'S_done.POOLS = S_pool.POOLS','S_done.HELD = eps', '$heap_valid($heap_graph(S_done))'],
        prefix + ['S_done = $write_name($release_temporaries(S_pool), [98], PARRAY 4)',
            'S_copy = $location_array(S_done, ROOT 1, 1)',
            'S_copy.STORE[1] = DEFINED (PARRAY 8)', 'S_copy.ARRAYS[4] = S_pool.ARRAYS[4]',
            'S_copy.POOLS = S_pool.POOLS', '$heap_valid($heap_graph(S_copy))'],
        prefix + [f'S_second = $install_pool(S_pool, $pcsource(72, U.AST), {seq(arrays)}, {seq(nodes)}, {seq(facts)})',
            'S_second.COMPLETION = NORMAL','|S_second.ARRAYS| = 13',
            '$pool_value(S_second.POOLS, PORIGIN 71 '+path(0)+') = (PARRAY 5)',
            '$pool_value(S_second.POOLS, PORIGIN 72 '+path(0)+') = (PARRAY 10)',
            'S_second.ARRAYS[10].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY 8)), ENTRY (KINT 1) (DIRECT (PARRAY 8))]',
            '$identity_apply(S_second, false, PARRAY 4, PARRAY 9, 1).RESULT = KNOWN (PBOOL false)',
            '$heap_valid($heap_graph(S_second))'],
        prefix + [f'$install_pool(S_pool, U, {seq(arrays)}, {seq(nodes)}, {seq(facts)}) = S_pool[.COMPLETION = UNSUPPORTED "invalid compiled constant pool"]'],
        [f'U = {unit}',f'S = {initial}[.SOURCES = [U]]',
            f'S_pool = $install_pool(S, U, {seq(arrays)}, {seq(nodes)}, {seq(facts)})',
            'S_pool.COMPLETION = NORMAL','S_pool.SOURCES = [U]'],
    ]
    scalar_values = ['PNULL','PBOOL true','PBOOL false','PINT (-9223372036854775808)', 'PINT 9223372036854775807', nan, 'PFLOAT 9223372036854775808','PSTRING ([0,255,128])']
    cases += [[f'U = {unit}',f'S_pool = $install_pool({initial}, U, eps, eps, {seq([constant(i,v) for i,v in enumerate(scalar_values)])})',
        'S_pool.COMPLETION = NORMAL','S_pool.ALLOCATIONS = eps','$pools_nodes(S_pool.POOLS) = eps']+
        [f'$pool_value(S_pool.POOLS, PORIGIN 71 {path(i)}) = ({v})' for i,v in enumerate(scalar_values)]]
    bad = 'S[.COMPLETION = UNSUPPORTED "invalid compiled constant pool"]'
    invalid = [
        ('U[.OCCURRENCES = eps]',seq(arrays),seq(nodes),seq(facts)),
        ('U',seq(arrays),seq(nodes),seq(facts+[facts[0]])),
        ('U',seq(arrays),seq(nodes), '[PCONSTANT ([PCINDEX 99, PCFIELD 0]) (PINT 1)]'),
        ('U',seq(arrays),seq(nodes), '[PCONSTANT ([PCINDEX 0]) (PINT 1)]'),
        ('U',seq(arrays),seq(nodes), seq([constant(0,'PARRAY 3')])),
        ('U',seq(arrays),seq(nodes), seq([constant(0,'PARRAY 99')])),
        ('U',seq(arrays),seq(nodes+['HARRAY 0']),seq(facts)),
        ('U',seq(arrays),'[HCELL 0]', 'eps'),
        ('U',seq(arrays),'[HARRAY 99]', 'eps'),
        ('U',seq([array(['PARRAY 1'])]),'[HARRAY 0]',seq([constant(0,'PARRAY 0')])),
        ('U','[{ITEMS ([ENTRY (KINT 0) (ALIAS 0)]), NEXT 1}]','[HARRAY 0]',seq([constant(0,'PARRAY 0')])),
        ('U','[{ITEMS ([ENTRY (KINT 0) UNINITIALIZED]), NEXT 1}]','[HARRAY 0]',seq([constant(0,'PARRAY 0')])),
    ]
    for u,arr,ns,fs in invalid:
        cases += [[f'U = {unit}',f'S = {existing}',f'$install_pool(S, {u}, {arr}, {ns}, {fs}) = {bad}']]
    cases += [[f'U = {unit}', f'S = {initial}[.SOURCES = [$pcsource(71, PROGRAM eps)]]',f'{install} = {bad}'],
        [f'U = {unit}',f'S = {initial}[.COMPLETION = BUDGET]', f'$install_pool(S,U,eps,eps,eps) = S']]
    boundaries = len(cases)
    rng = random.Random(8501032)
    records = []
    for _ in range(100):
        offset = rng.randrange(6)
        size = rng.randrange(1,10)
        live = [i for i in range(size) if rng.randrange(4)]
        tables, edges = [], {}
        for i in range(size):
            children = [rng.choice(live) for _ in range(rng.randrange(4))] if live and i in live else []
            # Constant evaluator creates acyclic direct tables; a different BFS oracle predicts retention.
            children = [c for c in children if c < i]
            edges[i] = children
            tables.append(array([f'PARRAY {c}' for c in children]+['PINT 7']))
        roots = [rng.choice(live) for _ in range(rng.randrange(1,5))] if live else []
        retained = set(roots); work = deque(roots)
        while work:
            for child in edges[work.popleft()]:
                if child not in retained: retained.add(child); work.append(child)
        fs = seq([constant(i,f'PARRAY {r}') for i,r in enumerate(roots)])
        cases += [[f'U = {unit}',f'S = {initial}[.ARRAYS = {seq([array([])]*offset)}]',
            f'S_pool = $install_pool(S,U,{seq(tables)},{seq([f"HARRAY {i}" for i in live])},{fs})',
            'S_pool.COMPLETION = NORMAL',f'|S_pool.ARRAYS| = {offset+size}',
            f'$pools_nodes(S_pool.POOLS) = {seq([f"HARRAY {offset+i}" for i in roots])}',
            'S_done = $prune_allocations($release_temporaries(S_pool))',
            f'S_done.ALLOCATIONS = {seq([f"HARRAY {offset+i}" for i in sorted(retained)])}',
            '$heap_valid($heap_graph(S_done))','S_done.POOLS = S_pool.POOLS']+
            [f'S_pool.ARRAYS[{offset+i}] = {array([f"PARRAY {offset+c}" for c in edges[i]]+["PINT 7"])}' for i in range(size)]]
        records.append({'offset':offset,'size':size,'live':live,'edges':edges,'roots':roots,'retained':sorted(retained)})
    declarations = 'var U : pcunit\n'
    with tempfile.TemporaryDirectory(prefix='compiled-pools-',dir=ROOT/'.tools') as tmp:
        for start in range(0,len(cases),16):
            batch = cases[start:start+16]
            fixture = Path(tmp)/'cases.watsup'
            fixture.write_text(declarations+'\n'.join(f'dec $case{start+i}() : bool\ndef $case{start+i}() = true\n'+''.join(f'  -- if {a}\n' for a in assertions) for i,assertions in enumerate(batch))+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{start+i}()\n' for i in range(len(batch))))
            run = subprocess.run([str(runner),*map(str,specs),str(fixture)],cwd=ROOT,capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT/'.tools/compiled-pools-failure.watsup').write_text(fixture.read_text())
                raise AssertionError(f'pool batch {start}: {run.stdout}{run.stderr}')
    assert before == fingerprint(), 'implementation changed during compiled-pool validation'
    report = {'result':'pass','classification':'internal permanent pool installation; source facts not consumed',
        'boundary_cases':boundaries,'constructed_graph_cases':len(records),'assertions':sum(map(len,cases)),
        'seed':8501032,'source_base64':base64.b64encode(source).decode(),'checked_ast':checked['ast'],
        'graphs':records,'manifest_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),'fingerprint':before}
    output = ROOT/'coverage/semantics/compiled-pools.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print({k:report[k] for k in ('result','boundary_cases','constructed_graph_cases','assertions')})


if __name__ == '__main__': main()
