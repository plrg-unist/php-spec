#!/usr/bin/env python3
"""Reached nested stdClass births, earlier facts and duplicate-array release."""
import base64
import hashlib
import json
from pathlib import Path

import global_constant_stdclass_array_protocol as packet
import global_constant_stdclass_new_sources as sources
import global_constant_stdclass_protocol as std

common, ROOT, text, term = packet.common, packet.ROOT, packet.text, packet.term
PREFIX = common.PREFIX + std.PREFIX


def birth(label, start, unit, budget=False):
    before, born, done = 'S_' + label, 'S_' + label + '_born', 'S_' + label + '_done'
    obj, site, decl = 'n_' + label, 'porigin_' + label, 'porigin_decl_' + label
    values = [*std.reach(before,start,0), f'{before}.ORIGIN = ({site})',
        f'{site} = PORIGIN {unit} pcpath_{label}',
        f'{before}.CONSTCONTEXT = (pconstantcontext_{label})',
        f'{decl} = pconstantcontext_{label}.ORIGIN',
        f'pconstantcontext_{label}.FACTS =/= eps', f'$constant_context_valid({before})',
        f'$global_std_ready({before},$ptascii("stdClass"))',
        f'$global_std_source({before},{site},{decl},|{before}.DECLARATIONS|)',
        f'$constant_callable_path({before},{site},$constant_child({decl},[PCFIELD 1]))',
        f'{site} =/= $constant_child({decl},[PCFIELD 1])']
    launch = before
    if budget:
        values += ['S_pause = $drive_steps('+before+',0)',
                   'S_pause = '+before+'[.COMPLETION = BUDGET]',
                   'S_resumed = $test_std_running(S_pause)', 'S_resumed = '+before]
        launch = 'S_resumed'
    values += [*std.step(born,launch), f'{obj} = |{before}.OBJECTS|',
        f'{born}.TODO = (DEFAULT_NEW_ARGS pdefaultnew_{label}) :: ptask_{label}*',
        f'pdefaultnew_{label}.OBJECT = {obj}', f'pdefaultnew_{label}.SITE = {site}',
        f'pdefaultnew_{label}.ARGUMENTS = eps',
        f'{born}.OBJECTS = {before}.OBJECTS ++ [STDINSTANCE]',
        f'{born}.ALLOCATIONS = {before}.ALLOCATIONS ++ [HOBJECT {obj}]',
        f'n_prefix_{label} = |{before}.DECLARATIONS|',
        f'pconstantstdobject_{label} = {{OBJECT {obj}, SITE {site}, DECL {decl}, PREFIX n_prefix_{label}, COMPLETE false}}',
        f'{born}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [pconstantstdobject_{label}]',
        f'$global_std_pending({born},pdefaultnew_{label})',
        f'~$global_std_completed({born},pconstantstdobject_{label})',
        f'$heap_owners($heap_graph({born}),HOBJECT {obj}) = 1',
        *std.step(done,born), f'{done}.RESULT = KNOWN (POBJECT {obj})',
        f'$global_std_record({done}.CONSTANTSTDOBJECTS,{obj}) = (pconstantstdobject_{label}_complete)',
        f'pconstantstdobject_{label}_complete = pconstantstdobject_{label}[.COMPLETE = true]',
        f'$global_std_completed({done},pconstantstdobject_{label}_complete)',
        f'$constant_value_class_valid({done},POBJECT {obj},PVSTDCLASS {obj} {site})',
        f'{done}.OBJECTS = {born}.OBJECTS', f'{done}.ALLOCATIONS = {born}.ALLOCATIONS',
        f'$heap_owners($heap_graph({done}),HOBJECT {obj}) = 1']
    return values


def query(state, start, name):
    after = state + '_value'
    values = [*common.reach(state,start,0,name), *common.public(state),
        f'$user_constant_at({state}.USERCONSTANTS,{text(name)}) = (puserconstant)',
        'puserconstant.VALUE = PARRAY n_root',
        f'{state}.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        f'{state}.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_left)),ENTRY (KINT 1) (DIRECT (POBJECT n_right)),ENTRY (KINT 2) (DIRECT (PARRAY n_empty))]',
        f'$dynamic_global_constant_value({state},{text(name)}) = (PARRAY n_root)',
        f'n_rootowners_{state} = $heap_owners($heap_graph({state}),HARRAY n_root)',
        *common.step(after,state,'PARRAY n_root'),
        f'$heap_owners($heap_graph({after}),HARRAY n_root) = $(n_rootowners_{state} + 1)']
    values += [f'$heap_owners($heap_graph({after}),HOBJECT {obj}) = $heap_owners($heap_graph({state}),HOBJECT {obj})' for obj in ['n_left','n_right']]
    values += [f'{after}.{field} = {state}.{field}' for field in ['ARRAYS','OBJECTS','OBJECTPROPS','OBJECTTABLES','ALLOCATIONS','USERCONSTANTS','CONSTANTSTDOBJECTS']]
    return values


def checks(initial, name, stdout, responses, restore_line):
    is_eval = name.startswith('eval-')
    unit, query_name = (1,'V61_EVAL') if is_eval else (0,'V61_TREE')
    values = [*initial, *birth('left','S_initial',unit,not is_eval),
        *birth('right','S_left_done',unit), 'n_left =/= n_right',
        'porigin_left =/= porigin_right',
        '$global_std_completed(S_right,pconstantstdobject_left_complete)',
        '$constant_fact_at(pconstantcontext_right.FACTS,porigin_left) = (pconstantfact_left)',
        'pconstantfact_left.CLASS = PVSTDCLASS n_left porigin_left',
        *query('S_first','S_right_done',query_name), 'n_rootowners_S_first = 1',
        '$heap_owners($heap_graph(S_first),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_first),HOBJECT n_right) = 1']
    # Malformed context is a pure refusal; its fake fact is never driven.
    values += ['S_bad_context = S_left[.CONSTCONTEXT = (pconstantcontext_left[.FACTS = pconstantcontext_left.FACTS ++ [{ORIGIN porigin_decl_left, VALUE (PNULL), CLASS PVSCALAR, LOOKUP eps}]])]',
               '~$constant_context_valid(S_bad_context)', '~$global_std_ready(S_bad_context,$ptascii("stdClass"))']
    if not is_eval:
        values += [*query('S_during','S_first_value',query_name),
            '$lookup(S_during.ENV,$ptascii("first")) = (n_first)',
            'S_during.STORE[n_first] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
            'S_during.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_copy_child))]',
            'n_copy_child =/= n_child',
            'H_during = $heap_graph(S_during)',
            '$heap_edge_owners(HOBJECT n_left,H_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 2',
            '$heap_edge_owners(HOBJECT n_right,H_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 2',
            *std.property_value('S_during','n_left',31,'left_changed'),
            *std.property_value('S_during','n_right',37,'right_changed'),
            *query('S_again','S_during_value',query_name), 'n_rootowners_S_again = 1',
            '$heap_owners($heap_graph(S_again),HOBJECT n_left) = 1',
            '$heap_owners($heap_graph(S_again),HOBJECT n_right) = 1']
        finish = 'S_again_value'
    else:
        values += ['S_wait2 = $test_std_seek(S_first_value,4,0,5000)',
            'S_wait2.COMPLETION = SOURCE_PENDING', *common.public('S_wait2'),
            '$eval_response_valid(S_wait2,'+responses[1]+')',
            'S_retry = $test_std_running($eval_resume(S_wait2,'+responses[1]+'))',
            *birth('candidate_left','S_retry',2), *birth('candidate_right','S_candidate_left_done',2),
            'n_candidate_left =/= n_candidate_right', 'n_candidate_left =/= n_left',
            'n_candidate_right =/= n_right', 'pcpath_candidate_left = pcpath_left',
            'pcpath_candidate_right = pcpath_right',
            *std.reach('S_handler','S_candidate_right_done',3,4),
            'S_handler.CURRENT = (pcallcontext)',
            '$error_context_call(S_handler,pcallcontext) = (perrorcall)',
            'perrorcall.LEVEL = 2',
            'perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin_decl_candidate_right (PARRAY n_candidate_root) pvalueclass_candidate n_constants pconstantfact_reads* z_line',
            'S_handler.ARRAYS[n_candidate_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_candidate_child))]',
            'S_handler.ARRAYS[n_candidate_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_candidate_left)),ENTRY (KINT 1) (DIRECT (POBJECT n_candidate_right)),ENTRY (KINT 2) (DIRECT (PARRAY n_empty))]',
            '$heap_owners($heap_graph(S_handler),HARRAY n_candidate_root) = 1',
            '$heap_owners($heap_graph(S_handler),HOBJECT n_candidate_left) = 1',
            '$heap_owners($heap_graph(S_handler),HOBJECT n_candidate_right) = 1',
            *std.reach('S_discarded','S_handler',2,restore_line),
            'S_discarded.USERCONSTANTS = S_first.USERCONSTANTS',
            '$global_std_records_valid(S_discarded,S_discarded.CONSTANTSTDOBJECTS)',
            '$global_std_completed(S_discarded,pconstantstdobject_candidate_left_complete)',
            '$global_std_completed(S_discarded,pconstantstdobject_candidate_right_complete)']
        for node in ['HARRAY n_candidate_root','HARRAY n_candidate_child','HOBJECT n_candidate_left','HOBJECT n_candidate_right']:
            values += [f'~(({node}) <- S_discarded.ALLOCATIONS)',f'$heap_owners($heap_graph(S_discarded),{node}) = 0']
        values += ['~$constant_value_class_valid(S_discarded,POBJECT n_candidate_left,PVSTDCLASS n_candidate_left porigin_candidate_left)',
            '~$constant_value_class_valid(S_discarded,POBJECT n_candidate_right,PVSTDCLASS n_candidate_right porigin_candidate_right)',
            *std.property_value('S_discarded','n_left',41,'kept_left'),
            *std.property_value('S_discarded','n_right',23,'kept_right'),
            *query('S_kept','S_discarded',query_name)]
        finish = 'S_kept_value'
    values += [f'S_final = $drive_steps({finish},5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
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
            responses=[];restore_line=0
            if name.startswith('eval-'):
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const V61_EVAL')]
                for unit_id in [1,2]:
                    unit=frontend.request({'op':'parse-eval','id':str(unit_id),'mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert unit['accepted']
                    checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
                    responses.append('SOURCE_ACCEPT '+str(unit_id)+' '+term(code)+' '+checked)
                initial=['S_wait1 = $php_run('+main+',5000,'+json.dumps(packet.b64(str(path).encode()))+')','S_wait1.COMPLETION = SOURCE_PENDING',*common.public('S_wait1'),'$eval_response_valid(S_wait1,'+responses[0]+')','S_initial = $test_std_running($eval_resume(S_wait1,'+responses[0]+'))']
                restore_line=path.read_text().splitlines().index('restore_error_handler();')+1
            values=checks(initial,name,base64.b64decode(row['stdout']),responses,restore_line)
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
    raise SystemExit(0 if packet.main() else 1)
