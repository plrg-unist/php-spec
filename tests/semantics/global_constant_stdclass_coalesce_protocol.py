#!/usr/bin/env python3
"""Reached coalescing newborn receipts, operand choice and shared array leaves."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import global_constant_stdclass_new_protocol as previous
import global_constant_stdclass_coalesce_sources as sources

packet, std, common = previous.packet, previous.std, previous.common
ROOT, text, term = previous.ROOT, previous.text, previous.term
PREFIX = previous.PREFIX + r'''
dec $test_coalesce_front(pstate, porigin) : bool
def $test_coalesce_front(S, porigin) = true
  -- if S.ORIGIN = (porigin)
  -- if S.TODO = (COALESCE_RESULT expression z_left z_right) :: ptask_tail*
def $test_coalesce_front(S, porigin) = false -- otherwise
dec $test_coalesce_seek(pstate, porigin, nat) : pstate
def $test_coalesce_seek(S, porigin, 0) = S
def $test_coalesce_seek(S, porigin, n) = S
  -- if $(n > 0)
  -- if $test_coalesce_front(S,porigin) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_coalesce_seek(S, porigin, n) = $test_coalesce_seek($test_std_running($drive_steps(S,1)),porigin,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_coalesce_front(S,porigin)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def flow(label, selected):
    site, choice = 'porigin_' + label, 'porigin_choice_' + label
    value = 'PVSTDCLASS n_' + label + ' ' + site
    args = lambda state, cls: f'{state},{choice},porigin_decl_{label},eps,{cls},{state}.USERCONSTANTS,$global_constant_reads({state},porigin_decl_{label}),eps'
    return [f'$reference_origin_parent({site},1) = (({choice},[PCFIELD {selected}]))',
        f'$compiled_redirect(S_{label}_done,{choice}) = eps',
        f'$origin_node(S_{label}_done.SOURCES,{choice}) = (NExprBinaryOpCoalesce expression_left_{label} expression_right_{label} metadata_{label})',
        f'~$global_constant_flow({args("S_"+label+"_born",value)})',
        f'$global_constant_flow({args("S_"+label+"_done",value)})',
        f'porigin_wrong_{label} = $constant_child({choice},[PCFIELD {1-selected}])',
        f'~$global_constant_flow({args("S_"+label+"_done","PVSTDCLASS n_"+label+" porigin_wrong_"+label)})']


def checks(initial, name, stdout):
    selected = name.startswith('eval-')
    unit, query = (1,'V62_EVAL_TREE') if selected else (0,'V62_TREE')
    values = [*initial, *previous.birth('left','S_initial',unit,not selected),
        *flow('left',1 if selected else 0)]
    if selected:
        values += ['$reference_origin_parent(porigin_choice_left,1) = ((porigin_handoff,[PCFIELD 0]))']
    else:
        values += ['porigin_handoff = porigin_choice_left']
    values += ['S_handoff_found = $test_coalesce_seek(S_left_done,porigin_handoff,1000)',
        r'S_handoff_found.COMPLETION = NORMAL \/ S_handoff_found.COMPLETION = BUDGET',
        'S_handoff = $test_std_running(S_handoff_found)', '$test_coalesce_front(S_handoff,porigin_handoff)',
        *common.public('S_handoff'), 'S_handoff.RESULT = KNOWN (POBJECT n_left)',
        'S_handoff.TODO = (COALESCE_RESULT expression_skipped z_left z_right) :: ptask_handoff*',
        'S_handoff.CONSTCONTEXT = (pconstantcontext_handoff)',
        '$constant_recorded_null(S_handoff,$constant_child(porigin_handoff,[PCFIELD 0])) = (false)',
        '$heap_owners($heap_graph(S_handoff),HOBJECT n_left) = 1',
        *std.step('S_handoff_value','S_handoff'), 'S_handoff_value.RESULT = KNOWN (POBJECT n_left)',
        'S_handoff_value.TODO = ptask_handoff*',
        'S_handoff_value.ALLOCATIONS = S_handoff.ALLOCATIONS',
        'S_handoff_value.CONSTANTSTDOBJECTS = S_handoff.CONSTANTSTDOBJECTS',
        '$heap_owners($heap_graph(S_handoff_value),HOBJECT n_left) = 1',
        'porigin_skipped = $constant_child(porigin_handoff,[PCFIELD 1])',
        'pconstantcontext_bad = pconstantcontext_handoff[.FACTS = $constant_fact_put(pconstantcontext_handoff.FACTS,{ORIGIN porigin_skipped, VALUE eps, CLASS PVOBJECT, LOOKUP eps})]',
        'S_bad_skip = S_handoff[.CONSTCONTEXT = (pconstantcontext_bad)]',
        '$constant_facts_valid(S_bad_skip,porigin_decl_left,pconstantcontext_bad.FACTS)',
        '~$constant_context_valid(S_bad_skip)',
        *previous.birth('right','S_handoff_value',unit), *flow('right',1),
        '$constant_recorded_null(S_right,$constant_child(porigin_choice_right,[PCFIELD 0])) = (true)',
        'n_left =/= n_right', 'porigin_left =/= porigin_right',
        *previous.query('S_first','S_right_done',query), 'n_rootowners_S_first = 1',
        'S_first.TODO = (CONFIG_INVOKE pconfigcall_first) :: ptask_first*']
    values += ['pconfigcall_first.SELECTION = (n_selection)' if selected else 'pconfigcall_first.SELECTION = eps']
    start = 'S_first_value'
    if selected:
        values += [*previous.query('S_peer',start,query)]
        start = 'S_peer_value'
    values += [*previous.query('S_during',start,query),
        '$lookup(S_during.ENV,$ptascii("copy")) = (n_copy)',
        'S_during.STORE[n_copy] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
        'S_during.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_copy_child))]',
        'n_copy_child =/= n_child',
        'H_during = $heap_graph(S_during)',
        '$heap_edge_owners(HOBJECT n_left,H_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 2',
        '$heap_edge_owners(HOBJECT n_right,H_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 2',
        *std.property_value('S_during','n_left',31,'left_changed'),
        *std.property_value('S_during','n_right',37,'right_changed'),
        *previous.query('S_again','S_during_value',query), 'n_rootowners_S_again = 1',
        '$heap_owners($heap_graph(S_again),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_again),HOBJECT n_right) = 1',
        'S_final = $drive_steps(S_again_value,5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps',
        'S_final.CONSTCONTEXT = eps', 'S_final.EVALCONTEXTS = eps',
        '$test_outputs(S_final.EVENTS) = '+term(stdout), *common.public('S_final')]
    return values


def prepare(out, originals):
    native = json.loads((originals/'native-report.json').read_text())
    assert native['passed'] and native['inputs_stable']
    frontend = packet.Worker([str(packet.types.PHP),'-n',*packet.types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter = None
    try:
        adapter = packet.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        for name in sources.family.CASES:
            path=originals/name/'main.php';row,=[r for r in native['records'] if r['id']==name]
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['source_sha256']
            assert row['process']['exit']==0 and not base64.b64decode(row['stderr'])
            parsed=frontend.request({'op':'parse','source':packet.b64(path.read_bytes())});assert parsed['accepted']
            main=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            initial=['S_initial = $php_run('+main+',0,'+json.dumps(packet.b64(str(path).encode()))+')','S_initial.COMPLETION = BUDGET']
            if name.startswith('eval-'):
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const V62_EVAL_NULL')]
                unit=frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert unit['accepted']
                checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
                response='SOURCE_ACCEPT 1 '+term(code)+' '+checked
                initial=['S_wait = $php_run('+main+',5000,'+json.dumps(packet.b64(str(path).encode()))+')','S_wait.COMPLETION = SOURCE_PENDING',*common.public('S_wait'),'$eval_response_valid(S_wait,'+response+')','S_initial = $test_std_running($eval_resume(S_wait,'+response+'))']
            values=checks(initial,name,base64.b64decode(row['stdout']))
            target=out/name;target.mkdir()
            (target/'assertions.json').write_text(json.dumps(values,indent=2)+'\n')
            (target/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+v+'\n' for v in values))
    finally:
        try:
            if adapter:adapter.close()
        finally:frontend.close()


packet.sources, packet.prepare = sources, prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{str(Path(__file__).relative_to(ROOT)):sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__=='__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:sources.family.CASES={args.case:sources.family.CASES[args.case]}
    sys.argv=[sys.argv[0],*remaining]
    raise SystemExit(0 if packet.main() else 1)
