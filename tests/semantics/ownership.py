#!/usr/bin/env python3
"""Pure allocation-graph invariants; these are not PHP source/GC coverage."""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tests'))
import validate as syntax_validation


def seq(values):
    return '([' + ', '.join(values) + '])' if values else 'eps'


def node(n):
    return f'HARRAY {n}'


def graph(nodes, edges, roots):
    return '{NODES ' + seq([node(n) for n in nodes]) + ', EDGES ' + seq([
        f'HEDGE ({node(a)}) ({node(b)})' for a, b in edges]) + ', ROOTS ' + seq([node(n) for n in roots]) + '}'


def expected(nodes, edges, roots):
    # Incremental decrement queue is independent of the specification's repeated
    # simultaneous filtering; duplicate incoming edges are deliberately retained.
    counts = Counter(roots)
    children = {n: [] for n in nodes}
    for a, b in edges:
        counts[b] += 1
        children[a].append(b)
    queue = deque(n for n in nodes if not counts[n])
    alive = set(nodes)
    while queue:
        a = queue.popleft()
        alive.remove(a)
        for b in children[a]:
            counts[b] -= 1
            if counts[b] == 0:
                queue.append(b)
    reachable = set(roots)
    queue = deque(roots)
    while queue:
        for b in children[queue.popleft()]:
            if b not in reachable:
                reachable.add(b)
                queue.append(b)
    return [n for n in nodes if n in alive], [n for n in nodes if n in reachable]


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True, timeout=120)
    runner = HERE/'_build/default/numeric_runner.exe'
    specs = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    def fingerprint():
        return {'closure': syntax_validation.implementation_fingerprint(),
                'runner': hashlib.sha256(runner.read_bytes()).hexdigest()}
    before = fingerprint()
    graphs = [([], [], []), ([0,1,2], [(0,1),(1,2)], []),
              ([0,1,2], [(0,1),(1,0),(1,2)], []),
              ([0,1,2], [(0,1),(1,0),(1,2)], [2]),
              ([0,1,2], [(0,1),(0,1),(1,2)], [0,0])]
    # Every directed graph on three nodes, with varied root sets.
    for mask in range(512):
        edges = [(a,b) for a in range(3) for b in range(3) if mask & (1 << (a*3+b))]
        roots = [n for n in range(3) if (mask // 8) & (1 << n)]
        graphs.append(([0,1,2], edges, roots))
    rng = random.Random(8501039)
    for _ in range(100):
        nodes = list(range(rng.randrange(1,9)))
        graphs.append((nodes, [(rng.choice(nodes),rng.choice(nodes)) for _ in range(rng.randrange(25))],
                       [rng.choice(nodes) for _ in range(rng.randrange(6))]))
    cases = []
    for nodes, edges, roots in graphs:
        h = graph(nodes, edges, roots)
        retained, reachable = expected(nodes, edges, roots)
        pruned = graph(retained, [(a,b) for a,b in edges if a in retained and b in retained], roots)
        collected = graph(reachable, [(a,b) for a,b in edges if a in reachable and b in reachable], roots)
        assertions = [f'$heap_valid({h})', f'$heap_prune({h}) = {pruned}', f'$heap_collect({h}) = {collected}',
                      f'$heap_prune($heap_prune({h})) = {pruned}', f'$heap_collect($heap_prune({h})) = {collected}']
        for n in nodes:
            assertions.append(f'$heap_owners({h}, {node(n)}) = {roots.count(n)+sum(b==n for a,b in edges)}')
        cases.append(assertions)
    initial = '($initial_state(NORMAL))'
    base = (initial+'[.STORE = [DEFINED (PARRAY 0), DEFINED (PINT 1)]]'
            '[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 1), ENTRY (KINT 1) (ALIAS 1)]), NEXT 2}, '
            '{ITEMS ([ENTRY (KINT 0) (DIRECT (PARRAY 1))]), NEXT 1}]]'
            '[.ENV = [BIND ([97]) 0, BIND ([98]) 0]][.ALLOCATIONS = [HCELL 0, HCELL 1, HARRAY 0]]')
    # ARRAY1 is a historical self-cycle, never allocated in this state: neither
    # edge counting nor collection may resurrect it. Two aliases root cell0,
    # whose outgoing array ownership is expanded exactly once.
    cases += [[f'$heap_valid($heap_graph({base}))',
               f'$heap_owners($heap_graph({base}), HCELL 0) = 2',
               f'$heap_owners($heap_graph({base}), HCELL 1) = 2',
               f'$heap_owners($heap_graph({base}), HARRAY 0) = 1',
               f'$heap_owners($heap_graph({base}), HARRAY 1) = 0',
               f'$prune_allocations({base}[.ENV = eps]).ALLOCATIONS = eps']]
    cyclic = (base+'[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 1), ENTRY (KINT 1) (DIRECT (PARRAY 0))]), NEXT 2}]]'
              '[.ENV = eps]')
    cases += [[f'$prune_allocations({cyclic}).ALLOCATIONS = [HCELL 1, HARRAY 0]',
               f'$heap_owners($heap_graph($prune_allocations({cyclic})), HCELL 1) = 1',
               f'$heap_collect($heap_graph($prune_allocations({cyclic}))).NODES = eps']]
    cases += [[f'$machine_roots({initial}[.RESULT = VARIABLE ([97]) 1][.BASE = BASE_NAME (VARIABLE ([98]) 1) 1]) = eps'],
              [f'$machine_roots({initial}[.RESULT = KNOWN (PARRAY 0)][.BASE = BASE_DIM (BASE_VALUE (KNOWN (PARRAY 1))) (KNOWN (PARRAY 2)) 1][.HELD = [HCELL 3]]) = [HARRAY 0, HARRAY 1, HARRAY 2, HCELL 3]'],
              ['$tasks_nodes([ARRAY_NEXT 0 eps, ARRAY_VALUE 1 (KNOWN (PARRAY 2)) eps 1, BINARY_RIGHT ADD (KNOWN (PARRAY 3)) 1, DIM_PATH (BASE_NAME (KNOWN (PARRAY 4)) 1) 1, ASSIGN_ARRAY (BASE_APPEND (BASE_VALUE (KNOWN (PARRAY 5))) 1) 1 false]) = [HARRAY 0, HARRAY 1, HARRAY 2, HARRAY 3, HARRAY 4, HARRAY 5]'],
              ['$heap_valid({NODES ([HARRAY 0, HARRAY 0]), EDGES eps, ROOTS eps}) = false'],
              ['$heap_valid({NODES ([HARRAY 0]), EDGES ([HEDGE (HARRAY 0) (HARRAY 1)]), ROOTS eps}) = false'],
              ['$heap_valid({NODES eps, EDGES eps, ROOTS ([HCELL 0])}) = false'],
              [f'$prune_allocations($allocate_array({initial}, $array_empty())[.RESULT = KNOWN PNULL]).ALLOCATIONS = eps'],
              [f'$allocate_array({initial}, $array_empty()).ALLOCATIONS = [HARRAY 0]', f'$ensure({initial}, [97]).ALLOCATIONS = [HCELL 0]']]
    # Exercise actual task moves, not just the graph projection. One transition
    # is enough to expose accidental duplicate roots of a saved captured value.
    moves = [('BINARY_LEFT ADD (NScalarInt (INTEGER 1) eps) 1', '[HARRAY 0]'),
             ('DIM_CAPTURE', '[HARRAY 0]'), ('DIM_NAME 1', '[HARRAY 0]'),
             ('DIM_PATH (BASE_VALUE (KNOWN PNULL)) 1', '[HARRAY 0]'),
             ('DISCARD', 'eps')]
    for task, roots in moves:
        cases.append([f'S_next = $ownership_step({initial}[.RESULT = KNOWN (PARRAY 0)][.TODO = [{task}]])',
                      f'$machine_roots(S_next) = {roots}'])
    # Internal mutation entry transfers each captured input exactly once. Lookup
    # scratch may then be overwritten without losing a temporary-only RHS/path.
    held = (initial+'[.RESULT = KNOWN (PARRAY 0)][.BASE = BASE_VALUE (KNOWN (PARRAY 1))]'
            '[.TODO = [ASSIGN_ARRAY (BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN (PARRAY 2)) 1) 1 false, BINARY_RIGHT ADD (KNOWN (PARRAY 3)) 1]]'
            '[.HELD = [HCELL 4]]')
    cases += [[f'S_next = $hold_task_inputs({held})',
               'S_next.HELD = [HCELL 4, HARRAY 2, HARRAY 0, HARRAY 1]',
               'S_next.RESULT = KNOWN PNULL', 'S_next.BASE = BASE_VALUE (KNOWN PNULL)',
               '$machine_roots(S_next) = [HARRAY 3, HCELL 4, HARRAY 2, HARRAY 0, HARRAY 1]']]
    live = (initial+'[.STORE = [DEFINED (PARRAY 0)]]'
            '[.ARRAYS = [{ITEMS eps, NEXT 0}]]'
            '[.ENV = [BIND ([97]) 0]][.ALLOCATIONS = [HCELL 0, HARRAY 0]]')
    for captured in (False, True):
        operand = 'KNOWN (PARRAY 0)' if captured else 'VARIABLE ([97]) 1'
        assignment = (live+f'[.RESULT = {operand}]'
                      '[.HELD = [HCELL 0]][.TODO = [ASSIGN_ARRAY (BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN (PINT 0)) 1) 1 false]]')
        cases.append([f'S_next = $drive({assignment}, 1)',
                      'S_next.COMPLETION = NORMAL', 'S_next.HELD = [HCELL 0]',
                      '$heap_valid($heap_graph(S_next))',
                      'S_next.RESULT = KNOWN (PARRAY 0)',
                      f'|S_next.ARRAYS| = {2 if captured else 1}'])
    for completion in ('THROWN "Error" eps 1', 'UNSUPPORTED "test boundary"'):
        # Abrupt handlers may already have emptied TODO; cleanup still applies.
        abrupt = (live+f'[.COMPLETION = {completion}][.ENV = eps]'
                  '[.RESULT = KNOWN (PARRAY 0)][.HELD = [HCELL 0]]')
        cases.append([f'S_next = $drive({abrupt}, 1)',
                      'S_next.ALLOCATIONS = eps', 'S_next.HELD = eps',
                      'S_next.RESULT = KNOWN PNULL', '$heap_valid($heap_graph(S_next))'])
    for value, line in (('PINT 1', 1), ('PBOOL false', 0)):
        abrupt_write = (live+f'[.STORE = [DEFINED ({value})]][.RESULT = KNOWN (PARRAY 0)]'
                        f'[.HELD = [HCELL 0]][.TODO = [ASSIGN_ARRAY (BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN (PINT 0)) {line}) {line} false]]')
        cases.append([f'S_next = $ownership_step({abrupt_write})',
                      'S_next.COMPLETION =/= NORMAL', 'S_next.HELD = [HCELL 0]',
                      'S_next.TODO = eps'])
    for key in ('PINT 0', 'PARRAY 0'):
        unset = (live+f'[.BASE = BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN ({key})) 1]'
                 '[.HELD = [HCELL 0]][.TODO = [UNSET_ARRAY]]')
        cases.append([f'S_next = $ownership_step({unset})',
                      'S_next.HELD = [HCELL 0]', 'S_next.TODO = eps',
                      'S_next.RESULT = KNOWN PNULL', 'S_next.BASE = BASE_VALUE (KNOWN PNULL)'])
    cases += [[f'$drive({cyclic}[.COMPLETION = UNSUPPORTED "test cycle"], 1).ALLOCATIONS = [HCELL 1, HARRAY 0]'],
              [f'$drive({live}[.ENV = eps][.RESULT = KNOWN (PARRAY 0)][.TODO = [DISCARD]], 1).ALLOCATIONS = eps'],
              [f'S_next = $drive({live}[.TODO = [DISCARD]][.HELD = [HCELL 0]], 0)',
               'S_next.COMPLETION = BUDGET', 'S_next.TODO = [DISCARD]',
               'S_next.HELD = [HCELL 0]', 'S_next.ALLOCATIONS = [HCELL 0, HARRAY 0]']]
    reference = live+'[.ENV = eps][.RESULT = REFERENCE 0]'
    cases += [['$operand_nodes(REFERENCE 0) = [HCELL 0]',
               f'$heap_valid($heap_graph({reference}))',
               f'$prune_allocations({reference}).ALLOCATIONS = [HCELL 0, HARRAY 0]'],
              [f'$resolve({reference}[.STORE = [DEFINED (PINT 7)]], REFERENCE 0).RESULT = KNOWN (PINT 7)',
               f'$resolve_at({reference}[.STORE = [DEFINED (PSTRING ([55]))]], REFERENCE 0, 1).RESULT = KNOWN (PSTRING ([55]))'],
              [f'S_next = $bind_reference({live}, [98])',
               'S_next.RESULT = REFERENCE 0',
               '$machine_roots(S_next) = [HCELL 0, HCELL 0, HCELL 0]',
               '$heap_owners($heap_graph(S_next), HARRAY 0) = 1'],
              [f'S_next = $drive({reference}[.TODO = [BINARY_LEFT IDENTICAL (NScalarInt (INTEGER 1) eps) 1]], 1)',
               'S_next.COMPLETION = BUDGET', 'S_next.ALLOCATIONS = [HCELL 0, HARRAY 0]',
               '$machine_roots(S_next) = [HCELL 0]', '$heap_valid($heap_graph(S_next))'],
              [f'$drive({reference}[.TODO = [DISCARD]], 1).ALLOCATIONS = eps'],
              [f'S_next = $drive({reference}[.TODO = [WRITE_NAME ([98]) 1, DISCARD]], 2)',
               'S_next.COMPLETION = NORMAL', 'S_next.ALLOCATIONS = [HARRAY 0, HCELL 1]',
               'S_next.STORE[1] = DEFINED (PARRAY 0)', '$heap_valid($heap_graph(S_next))'],
              [f'$hold_task_inputs({reference}[.TODO = [DISCARD]]).HELD = [HCELL 0]']]
    # Separation observes surviving incoming owners, not backing vectors or the
    # number of names that alias one cell. These are helper-only embedded refs.
    copying = (initial+'[.STORE = [DEFINED (PARRAY 0), DEFINED (PARRAY 0), DEFINED (PINT 1)]]'
               '[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 2)]), NEXT 1}]]'
               '[.ENV = [BIND ([97]) 0, BIND ([98]) 1]]'
               '[.ALLOCATIONS = [HCELL 0, HCELL 1, HCELL 2, HARRAY 0]]')
    for suffix in ('', '[.RESULT = KNOWN (PARRAY 0)]', '[.ENV = [BIND ([97]) 0, BIND ([98]) 0]]'):
        unshared = copying+'[.ENV = [BIND ([97]) 0]]'+suffix
        cases.append([f'S_next = $location_array({unshared}, ROOT 0, 1)',
                      '|S_next.ARRAYS| = 1', 'S_next.RESULT = KNOWN (PARRAY 0)',
                      '$entry_lookup(S_next.ARRAYS[0].ITEMS, KINT 0) = (ALIAS 2)',
                      '$heap_valid($heap_graph(S_next))'])
    variants = [('', 'DIRECT (PINT 1)'),
                ('[.ENV = [BIND ([97]) 0, BIND ([98]) 1, BIND ([120]) 2]]', 'ALIAS 2'),
                ('[.HELD = [HCELL 2]]', 'ALIAS 2'),
                ('[.STORE = [DEFINED (PARRAY 0), DEFINED (PARRAY 0), DEFINED (PARRAY 0)]]', 'ALIAS 2'),
                ('[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 2), ENTRY (KINT 1) (ALIAS 2)]), NEXT 2}]]', 'ALIAS 2'),
                ('[.ENV = [BIND ([97]) 0]][.HELD = [HARRAY 0]]', 'DIRECT (PINT 1)')]
    for suffix, item in variants:
        cases.append([f'S_next = $location_array({copying+suffix}, ROOT 0, 1)',
                      '|S_next.ARRAYS| = 2', 'S_next.RESULT = KNOWN (PARRAY 1)',
                      f'$entry_lookup(S_next.ARRAYS[1].ITEMS, KINT 0) = ({item})',
                      '$entry_lookup(S_next.ARRAYS[0].ITEMS, KINT 0) = (ALIAS 2)',
                      '$heap_valid($heap_graph(S_next))'])
        cases.append([f'S_next = $binary_apply({copying+suffix}, ADD, PARRAY 0, PARRAY 0, 1)',
                      f'$entry_lookup(S_next.ARRAYS[1].ITEMS, KINT 0) = ({item})',
                      '$entry_lookup(S_next.ARRAYS[0].ITEMS, KINT 0) = (ALIAS 2)',
                      '$heap_valid($heap_graph(S_next))'])
    for cycle in (False, True):
        extra = ', ENTRY (KINT 1) (DIRECT (PARRAY 1))' if cycle else ''
        dead = (copying+'[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 2)]), NEXT 1}, '
                '{ITEMS ([ENTRY (KINT 0) (ALIAS 2)'+extra+']), NEXT 2}]]'
                '[.ALLOCATIONS = [HCELL 0, HCELL 1, HCELL 2, HARRAY 0, HARRAY 1]]')
        item = 'ALIAS 2' if cycle else 'DIRECT (PINT 1)'
        cases.append([f'S_next = $location_array({dead}, ROOT 0, 1)',
                      f'$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 0) = ({item})',
                      f'$heap_member(HARRAY 1, S_next.ALLOCATIONS) = {str(cycle).lower()}',
                      '$heap_valid($heap_graph(S_next))'])
        cases.append([f'S_next = $prune_allocations($binary_apply({dead}, ADD, PARRAY 0, PARRAY 0, 1))',
                      f'$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 0) = ({item})',
                      f'$heap_member(HARRAY 1, S_next.ALLOCATIONS) = {str(cycle).lower()}',
                      '$heap_valid($heap_graph(S_next))'])
        cases.append([f'S_next = $prune_allocations($binary_apply($allocate_array({dead}, $array_empty()), ADD, PARRAY 2, PARRAY 0, 1))',
                      f'$entry_lookup(S_next.ARRAYS[3].ITEMS, KINT 0) = ({item})',
                      f'$heap_member(HARRAY 1, S_next.ALLOCATIONS) = {str(cycle).lower()}',
                      '$heap_valid($heap_graph(S_next))'])
    merging = (copying+'[.STORE = [DEFINED (PARRAY 0), DEFINED (PARRAY 1), DEFINED (PINT 1)]]'
               '[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 2)]), NEXT 1}, '
               '{ITEMS ([ENTRY (KINT 2) (DIRECT (PINT 3))]), NEXT 3}]]'
               '[.ALLOCATIONS = [HCELL 0, HCELL 1, HCELL 2, HARRAY 0, HARRAY 1]]')
    cases += [[f'S_next = $binary_apply({merging}, ADD, PARRAY 1, PARRAY 0, 1)',
               '$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 0) = (DIRECT (PINT 1))',
               '$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 2) = (DIRECT (PINT 3))',
               '$heap_owners($heap_graph(S_next), HCELL 2) = 1'],
              [f'S_next = $ownership_step({merging}[.RESULT = KNOWN (PARRAY 1)][.HELD = [HCELL 2]][.TODO = [BINARY_RIGHT ADD (KNOWN (PARRAY 0)) 1]])',
               'S_next.HELD = [HCELL 2]', 'S_next.TODO = eps',
               '$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 0) = (ALIAS 2)',
               '$heap_valid($heap_graph(S_next))']]
    self_merge = merging+'[.STORE = [DEFINED (PARRAY 0), DEFINED (PARRAY 1), DEFINED (PARRAY 0)]]'
    for left, right, item, changed in ((0,1,'ALIAS 2','PINT 9'),
                                       (1,0,'DIRECT (PARRAY 0)','PARRAY 0')):
        cases.append([f'S_next = $binary_apply({self_merge}, ADD, PARRAY {left}, PARRAY {right}, 1)',
                      f'$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 0) = ({item})',
                      f'$location_write(S_next, ELEMENT 2 (KINT 0), PINT 9).STORE[2] = DEFINED ({changed})',
                      '$heap_valid($heap_graph(S_next))'])
    for suffix in ('[.HELD = [HCELL 2]]', '[.ENV = [BIND ([97]) 0, BIND ([98]) 1, BIND ([120]) 2]]'):
        cases.append([f'S_next = $binary_apply({merging+suffix}, ADD, PARRAY 1, PARRAY 0, 1)',
                      '$entry_lookup(S_next.ARRAYS[2].ITEMS, KINT 0) = (ALIAS 2)',
                      '$heap_valid($heap_graph(S_next))'])
    conflict = merging+'[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 2)]), NEXT 1}, {ITEMS ([ENTRY (KINT 0) (DIRECT (PINT 3))]), NEXT 1}]]'
    local = (merging+'[.ENV = eps]'
             '[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 2)]), NEXT 1}, {ITEMS ([ENTRY (KINT 1) (ALIAS 2)]), NEXT 2}]]')
    cases += [[f'S_next = $binary_apply({conflict}, ADD, PARRAY 1, PARRAY 0, 1)',
               'S_next.ARRAYS[2].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]',
               '$heap_owners($heap_graph(S_next), HCELL 2) = 1'],
              [f'S_next = $prune_allocations($binary_apply({local}, ADD, PARRAY 0, PARRAY 1, 1))',
               'S_next.HELD = eps', 'S_next.ALLOCATIONS = [HCELL 2, HARRAY 2]',
               'S_next.ARRAYS[2].ITEMS = [ENTRY (KINT 0) (ALIAS 2), ENTRY (KINT 1) (ALIAS 2)]',
               '$heap_valid($heap_graph(S_next))']]
    literal = (initial+'[.STORE = [DEFINED (PINT 1)]][.ENV = [BIND ([120]) 0]]'
               '[.ARRAYS = [{ITEMS eps, NEXT 0}]][.ALLOCATIONS = [HCELL 0, HARRAY 0]]'
               '[.TODO = [ARRAY_REF_VALUE 0 eps eps 1]]')
    cases += [[f'S_next = $hold_literal_reference({literal})',
               'S_next.HELD = [HARRAY 0, HCELL 0]',
               '$heap_owners($heap_graph(S_next), HCELL 0) = 2',
               '$heap_valid($heap_graph(S_next))'],
              [f'S_next = $ownership_step({literal})', 'S_next.HELD = eps',
               'S_next.ARRAYS[0].ITEMS = [ENTRY (KINT 0) (ALIAS 0)]',
               '$heap_owners($heap_graph(S_next), HCELL 0) = 2',
               '$heap_valid($heap_graph(S_next))'],
              ['$tasks_nodes([ARRAY_REF_KEY 0 (NScalarInt (INTEGER 1) eps) eps, ARRAY_REF_VALUE 1 (REFERENCE 2) eps 1]) = [HARRAY 0, HARRAY 1, HCELL 2]'],
              [f'S_next = $ownership_step({initial}[.RESULT = REFERENCE 0][.TODO = [ARRAY_REF_KEY 1 (NExprVariable (BYTES "eA==") eps) eps]])',
               '$machine_roots(S_next) = [HARRAY 1, HCELL 0]', 'S_next.RESULT = KNOWN PNULL']]
    for key, line in (('PNULL', 0), ('PARRAY 0', 1)):
        cases.append([f'S_next = $drive({literal}[.HELD = [HCELL 0]][.TODO = [ARRAY_REF_VALUE 0 (KNOWN ({key})) eps {line}]], 1)',
                      'S_next.COMPLETION =/= NORMAL', 'S_next.HELD = eps',
                      'S_next.ALLOCATIONS = [HCELL 0]', '$heap_valid($heap_graph(S_next))'])
    cases += [[f'S_next = $ownership_step({literal}[.HELD = [HCELL 0]][.TODO = [ARRAY_REF_VALUE 0 (KNOWN PNULL) eps 1]])',
               'S_next.COMPLETION = NORMAL', 'S_next.HELD = [HCELL 0]',
               '|S_next.EVENTS| = 1', 'S_next.ARRAYS[0].ITEMS = [ENTRY (KSTRING eps) (ALIAS 0)]'],
              [f'S_next = $drive({literal}[.ARRAYS = [{{ITEMS ([ENTRY (KINT 9223372036854775807) (DIRECT (PINT 0))]), NEXT 9223372036854775807}}]], 1)',
               'S_next.COMPLETION =/= NORMAL', 'S_next.ALLOCATIONS = [HCELL 0]',
               'S_next.HELD = eps', '$heap_valid($heap_graph(S_next))'],
              [f'S_next = $prune_allocations($ownership_step({literal}[.STORE = [DEFINED (PINT 1), DEFINED (PINT 2)]][.ARRAYS = [{{ITEMS ([ENTRY (KINT 0) (ALIAS 1)]), NEXT 1}}]][.ALLOCATIONS = [HCELL 0, HCELL 1, HARRAY 0]][.TODO = [ARRAY_REF_VALUE 0 (KNOWN (PINT 0)) eps 1]]))',
               'S_next.ALLOCATIONS = [HCELL 0, HARRAY 0]',
               'S_next.ARRAYS[0].ITEMS = [ENTRY (KINT 0) (ALIAS 0)]', '$heap_valid($heap_graph(S_next))']]
    cases += [[f'S_next = $ownership_step({initial}[.TODO = [REF_DYNAMIC_CV (VARIABLE ([120]) 3) ([120]) 3]])',
               'S_next.EVENTS = [WARNING ([120]) 3]',
               'S_next.STORE = [DEFINED PNULL]', 'S_next.RESULT = REFERENCE 0',
               '$heap_owners($heap_graph(S_next), HCELL 0) = 3', '$heap_valid($heap_graph(S_next))'],
              ['$task_nodes(REF_DYNAMIC_CV (REFERENCE 0) ([120]) 1) = [HCELL 0]'],
              [f'S_next = $drive({initial}[.TODO = [REF_DYNAMIC_CV (VARIABLE ([120]) 0) ([120]) 0]], 1)',
               'S_next.COMPLETION = UNSUPPORTED "missing source line"',
               'S_next.STORE = eps', 'S_next.ALLOCATIONS = eps'],
              [f'S_next = $drive({initial}[.TODO = [REF_DYNAMIC_CV (KNOWN (PSTRING ([120]))) ([95,71,69,84]) 1]], 1)',
               'S_next.COMPLETION = UNSUPPORTED "request environment variable"',
               'S_next.STORE = eps', 'S_next.ALLOCATIONS = eps'],
              [f'S_next = $drive({initial}[.STORE = [DEFINED (PSTRING ([120]))]][.ALLOCATIONS = [HCELL 0]][.TODO = [REF_DYNAMIC_CV (REFERENCE 0) ([120]) 1]], 1)',
               'S_next.COMPLETION = NORMAL', 'S_next.RESULT = REFERENCE 1',
               'S_next.ALLOCATIONS = [HCELL 1]', '$heap_valid($heap_graph(S_next))']]
    acquire = (live+'[.BASE = BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN (PINT 0)) 1]'
               '[.TODO = [ACQUIRE_ARRAY 1]]')
    cases += [[f'S_next = $ownership_step({acquire}[.HELD = [HCELL 0]])',
               'S_next.HELD = [HCELL 0]', 'S_next.RESULT = KNOWN PNULL',
               'S_next.CELL = 1', 'S_next.STORE[1] = DEFINED PNULL',
               'S_next.ARRAYS[0].ITEMS = [ENTRY (KINT 0) (ALIAS 1)]',
               '$heap_owners($heap_graph(S_next), HCELL 1) = 1', '$heap_valid($heap_graph(S_next))'],
              [f'S_next = $ownership_step({base}[.ENV = [BIND ([97]) 0]][.BASE = BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN (PINT 0)) 1][.TODO = [ACQUIRE_ARRAY 1]])',
               'S_next.CELL = 1', '|S_next.STORE| = 2', '|S_next.ARRAYS| = 2',
               '$heap_owners($heap_graph(S_next), HCELL 1) = 2'],
              [f'S_next = $ownership_step({acquire}[.STORE = [DEFINED (PARRAY 0), DEFINED (PARRAY 0)]][.ENV = [BIND ([97]) 0, BIND ([98]) 1]][.ALLOCATIONS = [HCELL 0, HCELL 1, HARRAY 0]] )',
               'S_next.CELL = 2', 'S_next.STORE[0] = DEFINED (PARRAY 1)',
               'S_next.ARRAYS[0].ITEMS = eps', 'S_next.ARRAYS[1].ITEMS = [ENTRY (KINT 0) (ALIAS 2)]',
               '$heap_valid($heap_graph(S_next))'],
              [f'S_acquired = $ownership_step({acquire})',
               'S_next = $ownership_step(S_acquired[.TODO = [REF_CAPTURE (KNOWN (PSTRING ([120]))) 1]])',
               'S_next.TODO = [REF_DYNAMIC (KNOWN (PSTRING ([120]))) 1 1]',
               '$heap_owners($heap_graph(S_next), HCELL 1) = 2', '$heap_valid($heap_graph(S_next))'],
              [f'S_acquired = $ownership_step({acquire})',
               'S_next = $ownership_step(S_acquired[.TODO = [REF_DYNAMIC (KNOWN (PSTRING ([120]))) 1 1]])',
               'S_next.RESULT = REFERENCE 1', 'S_next.TODO = eps',
               '$heap_owners($heap_graph(S_next), HCELL 1) = 3', '$heap_valid($heap_graph(S_next))'],
              ['$task_nodes(REF_DYNAMIC (REFERENCE 0) 1 1) = [HCELL 0, HCELL 1]']]
    for key, line in (('PARRAY 0', 1), ('PNULL', 0)):
        cases.append([f'S_next = $drive({acquire}[.BASE = BASE_DIM (BASE_VALUE (VARIABLE ([97]) 1)) (KNOWN ({key})) {line}][.TODO = [ACQUIRE_ARRAY {line}]][.HELD = [HCELL 0]], 1)',
                      'S_next.COMPLETION =/= NORMAL', '|S_next.STORE| = 1',
                      'S_next.HELD = eps', 'S_next.RESULT = KNOWN PNULL', '$heap_valid($heap_graph(S_next))'])
    cases += [[f'S_next = $drive({acquire}[.ARRAYS = [{{ITEMS ([ENTRY (KINT 9223372036854775807) (DIRECT PNULL)]), NEXT 9223372036854775807}}]][.BASE = BASE_APPEND (BASE_VALUE (VARIABLE ([97]) 1)) 1], 1)',
               'S_next.COMPLETION =/= NORMAL', '|S_next.STORE| = 1',
               'S_next.HELD = eps', '$heap_valid($heap_graph(S_next))'],
              [f'S_acquired = $ownership_step({acquire})',
               'S_next = $drive(S_acquired[.TODO = [REF_DYNAMIC (VARIABLE ([120]) 0) 1 0]], 1)',
               'S_next.COMPLETION = UNSUPPORTED "missing source line"',
               'S_next.HELD = eps', '$heap_owners($heap_graph(S_next), HCELL 1) = 1',
               '$heap_valid($heap_graph(S_next))']]
    declarations = ['dec $ownership_step(pstate) : pstate\ndef $ownership_step(S) = S_next\n  -- PhpStep: S ~> S_next\n']
    with tempfile.TemporaryDirectory(prefix='ownership-', dir=ROOT/'.tools') as tmp:
        for start in range(0,len(cases),64):
            batch = cases[start:start+64]
            definitions = [f'dec $case{start+i}() : bool\ndef $case{start+i}() = true\n'+''.join(f'  -- if {a}\n' for a in assertions) for i,assertions in enumerate(batch)]
            fixture = Path(tmp)/'cases.watsup'
            fixture.write_text('\n'.join(declarations+definitions)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{start+i}()\n' for i in range(len(batch))))
            run = subprocess.run([str(runner), *map(str,specs), str(fixture)],cwd=ROOT,capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT/'.tools/ownership-failure.watsup').write_text(fixture.read_text())
                raise AssertionError(f'ownership batch {start}: {run.stdout}{run.stderr}')
    assert before == fingerprint(), 'implementation changed during ownership validation'
    report = {'result':'pass','classification':'helper-only allocation graph; source element-reference targets and GC remain pending',
              'graph_cases':len(graphs),'machine_and_boundary_cases':len(cases)-len(graphs),
              'assertions':sum(map(len,cases)),'seed':8501039,'fingerprint':before,
              'manifest_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest()}
    (ROOT/'coverage/semantics/ownership.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='fingerprint'}))


if __name__ == '__main__':
    main()
