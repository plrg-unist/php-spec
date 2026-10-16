#!/usr/bin/env python3
"""Reached ignored stdClass arguments, donor owners and abrupt eval retry."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import global_constant_stdclass_new_protocol as previous
import global_constant_stdclass_arguments_sources as sources

packet, std, common = previous.packet, previous.std, previous.common
ROOT, text, term = previous.ROOT, previous.text, previous.term
PREFIX = previous.PREFIX + r'''
dec $test_stdargs_front(pstate, nat) : bool
def $test_stdargs_front(S,0) = true
  -- if S.TODO = (EVAL (NExprNew name (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if phpType7* =/= eps
  -- if $global_std_ready(S,$ptascii("stdClass"))
def $test_stdargs_front(S,1) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = |pdefaultnew.ARGUMENTS|
  -- if $global_std_pending(S,pdefaultnew)
def $test_stdargs_front(S,2) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = 2
  -- if $global_std_pending(S,pdefaultnew)
def $test_stdargs_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (DEFAULT_NEW_SEND pdefaultnew) :: ptask_tail*
def $test_stdargs_front(S,n) = false -- otherwise
dec $test_stdargs_seek(pstate, nat, nat) : pstate
def $test_stdargs_seek(S,n_phase,0) = S
def $test_stdargs_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_stdargs_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_stdargs_seek(S,n_phase,n) = $test_stdargs_seek($test_std_running($drive_steps(S,1)),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_stdargs_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, public=True):
    return [f'{state}_found = $test_stdargs_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_std_running({state}_found)', f'$test_stdargs_front({state},{phase})',
        *(common.public(state) if public else [])]


def birth(label, start, unit, argc, budget=False):
    before, born = 'S_'+label, 'S_'+label+'_born'
    values = [*reach(before,start,0), f'{before}.ORIGIN = (porigin_{label})',
        f'porigin_{label} = PORIGIN {unit} pcpath_{label}',
        f'{before}.CONSTCONTEXT = (pconstantcontext_{label})',
        f'porigin_decl_{label} = pconstantcontext_{label}.ORIGIN',
        f'$origin_node({before}.SOURCES,porigin_{label}) = (NExprNew name_{label} (SEQUENCE phpType7_{label}*) metadata_{label})',
        f'|phpType7_{label}*| = {argc}', f'$parameter_new_prefix(phpType7_{label}*)',
        f'$default_new_unique(phpType7_{label}*)',
        f'$global_std_source({before},porigin_{label},porigin_decl_{label},|{before}.DECLARATIONS|)',
        f'$constant_context_valid({before})',
        f'$user_constant_at({before}.USERCONSTANTS,$ptascii("V63_DONOR")) = (puserconstant_donor)',
        'puserconstant_donor.VALUE = POBJECT n_donor']
    if budget:
        values += [f'S_pause = $drive_steps({before},0)',
            f'S_pause = {before}[.COMPLETION = BUDGET]',
            'S_resume = $test_std_running(S_pause)', f'S_resume = {before}']
    values += [*std.step(born,before), f'{born}.TODO = (DEFAULT_NEW_ARGS pdefaultnew_{label}) :: ptask_{label}*',
        f'n_{label} = |{before}.OBJECTS|', f'pdefaultnew_{label}.OBJECT = n_{label}',
        f'pdefaultnew_{label}.SITE = porigin_{label}', f'pdefaultnew_{label}.ARGUMENTS = phpType7_{label}*',
        f'pdefaultnew_{label}.INDEX = 0', f'pdefaultnew_{label}.VALUES = eps',
        f'{born}.OBJECTS = {before}.OBJECTS ++ [STDINSTANCE]',
        f'{born}.ALLOCATIONS = {before}.ALLOCATIONS ++ [HOBJECT n_{label}]',
        f'n_prefix_{label} = |{before}.DECLARATIONS|',
        f'$global_std_record({born}.CONSTANTSTDOBJECTS,n_{label}) = (pconstantstdobject_{label})',
        f'pconstantstdobject_{label} = {{OBJECT n_{label}, SITE porigin_{label}, DECL porigin_decl_{label}, PREFIX n_prefix_{label}, COMPLETE false}}',
        f'{born}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [pconstantstdobject_{label}]',
        f'$global_std_pending({born},pdefaultnew_{label})', f'$default_new_valid({born},pdefaultnew_{label})',
        f'~$global_std_completed({born},pconstantstdobject_{label})',
        f'$heap_owners($heap_graph({born}),HOBJECT n_{label}) = 1', f'n_{label} =/= n_donor']
    return values


def complete(label, start, argc, donated_owners):
    state, done = 'S_'+label+'_values', 'S_'+label+'_done'
    values = [*reach(state,start,1), f'{state}.TODO = (DEFAULT_NEW_ARGS pdefaultnew_{label}_values) :: ptask_{label}_values*',
        f'pdefaultnew_{label}_values.OBJECT = n_{label}', f'pdefaultnew_{label}_values.INDEX = {argc}',
        f'$default_new_valid({state},pdefaultnew_{label}_values)',
        f'$global_new_complete_phase({state},pdefaultnew_{label}_values)',
        f'~$new_has_ctor({state},pdefaultnew_{label}_values.CLASS)',
        f'$heap_owners($heap_graph({state}),HOBJECT n_{label}) = 1',
        f'$heap_owners($heap_graph({state}),HOBJECT n_donor) = {donated_owners}']
    return values


def delivered(label, state, arrays, donor_owners):
    done='S_'+label+'_done'
    values=[*std.step(done,state), f'{done}.RESULT = KNOWN (POBJECT n_{label})',
        f'$global_std_record({done}.CONSTANTSTDOBJECTS,n_{label}) = (pconstantstdobject_{label}_done)',
        f'pconstantstdobject_{label}_done = pconstantstdobject_{label}[.COMPLETE = true]',
        f'$global_std_completed({done},pconstantstdobject_{label}_done)',
        f'$constant_value_class_valid({done},POBJECT n_{label},PVSTDCLASS n_{label} porigin_{label})',
        f'$heap_owners($heap_graph({done}),HOBJECT n_{label}) = 1',
        f'$heap_owners($heap_graph({done}),HOBJECT n_donor) = {donor_owners}']
    for array in arrays:
        values += [f'~((HARRAY {array}) <- {done}.ALLOCATIONS)',
            f'$heap_owners($heap_graph({done}),HARRAY {array}) = 0']
    return values


def query(label,start,name,obj,site):
    state='S_'+label;after=state+'_value'
    values=[*common.reach(state,start,0,name), *common.public(state),
        f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{label}) :: ptask_{label}*',
        f'$user_constant_at({state}.USERCONSTANTS,{text(name)}) = (puserconstant_{label})',
        f'puserconstant_{label}.VALUE = POBJECT {obj}',
        f'puserconstant_{label}.CLASS = PVSTDCLASS {obj} {site}',
        f'$dynamic_global_constant_value({state},{text(name)}) = (POBJECT {obj})',
        f'n_owners_{label} = $heap_owners($heap_graph({state}),HOBJECT {obj})',
        *common.step(after,state,f'POBJECT {obj}'),
        f'$heap_owners($heap_graph({after}),HOBJECT {obj}) = $(n_owners_{label} + 1)']
    values += [f'{after}.{field} = {state}.{field}' for field in ['OBJECTS','OBJECTTABLES','OBJECTPROPS','ARRAYS','USERCONSTANTS','ALLOCATIONS','CONSTANTSTDOBJECTS']]
    return values


def finish(start,stdout):
    return [f'S_final = $drive_steps({start},5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.CONSTCONTEXT = eps', 'S_final.EVALCONTEXTS = eps',
        '$test_outputs(S_final.EVENTS) = '+term(stdout), *common.public('S_final')]


def checks(initial,name,stdout,responses,catch_line):
    if not name.startswith('eval-'):
        values=[*initial,*birth('outer','S_initial',0,4,True),*complete('outer','S_outer_born',4,5),
            'pdefaultnew_outer_values.VALUES = [POBJECT n_donor,PARRAY n_arg_array,POBJECT n_donor,PARRAY n_named_array]',
            'S_outer_values.ARRAYS[n_arg_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_arg_child))]',
            'S_outer_values.ARRAYS[n_arg_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_donor)),ENTRY (KINT 1) (DIRECT (PARRAY n_empty))]',
            'S_outer_values.ARRAYS[n_named_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_donor))]',
            '$heap_edge_owners(HOBJECT n_donor,$heap_graph(S_outer_values).EDGES,[HARRAY n_arg_child,HARRAY n_named_array]) = 2',
            *delivered('outer','S_outer_values',['n_arg_array','n_arg_child','n_named_array'],1),
            *query('first','S_outer_done','V63_VALUE','n_outer','porigin_outer'),
            '$object_table_slots_at(S_first,n_outer) = eps',
            *finish('S_first_value',stdout)]
        # These malformed phases are never driven.
        values += ['~$global_std_pending(S_outer_born,pdefaultnew_outer[.ARGUMENTS = eps])',
            '~$global_std_pending(S_outer_born,pdefaultnew_outer[.INDEX = 5][.VALUES = [PNULL,PNULL,PNULL,PNULL,PNULL]])',
            '~$global_std_pending(S_outer_born,pdefaultnew_outer[.VALUES = [PNULL]])',
            '~$global_std_pending(S_outer_born[.CONSTANTSTDOBJECTS = S_outer.CONSTANTSTDOBJECTS],pdefaultnew_outer)',
            '~$global_std_pending(S_outer_values[.CONSTANTSTDOBJECTS = $global_std_record_put(S_outer_values.CONSTANTSTDOBJECTS,pconstantstdobject_outer[.COMPLETE = true])],pdefaultnew_outer_values)']
        return values
    values=[*initial,*birth('failed','S_initial',1,3),*reach('S_prior','S_failed_born',2),
        'S_prior.TODO = (DEFAULT_NEW_ARGS pdefaultnew_prior) :: ptask_prior*',
        'pdefaultnew_prior.OBJECT = n_failed',
        'pdefaultnew_prior.VALUES = [POBJECT n_donor,PARRAY n_failed_array]',
        'S_prior.ARRAYS[n_failed_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_failed_child))]',
        'S_prior.ARRAYS[n_failed_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_donor))]',
        '$heap_owners($heap_graph(S_prior),HOBJECT n_donor) = 4',
        *reach('S_throw','S_prior',3,False),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (DEFAULT_NEW_SEND pdefaultnew_throw) :: ptask_throw*',
        'S_throw.CONSTCONTEXT = eps', 'pdefaultnew_throw = pdefaultnew_prior',
        '$constant_bindings(S_throw,S_throw.TODO) = [porigin_decl_failed]',
        '$global_new_argument_owned(S_throw,pdefaultnew_throw)',
        '~$global_new_argument_owned(S_throw[.TODO = eps],pdefaultnew_throw)',
        '~$global_new_argument_owned(S_throw[.CONSTANTSTDOBJECTS = $global_std_record_put(S_throw.CONSTANTSTDOBJECTS,pconstantstdobject_failed[.COMPLETE = true])],pdefaultnew_throw)',
        '~$global_new_argument_owned(S_throw,pdefaultnew_throw[.LINE = $(pdefaultnew_throw.LINE + 1)])',
        '~$global_new_argument_owned(S_throw,pdefaultnew_throw[.ARGUMENTS = eps])',
        '~$global_new_argument_owned(S_throw,pdefaultnew_throw[.VALUES = eps])',
        '~$global_new_argument_owned(S_throw[.CONSTANTSTDOBJECTS = S_failed.CONSTANTSTDOBJECTS],pdefaultnew_throw)',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ('+text('Undefined constant "V63_MISSING"')+')',
        '~(n_failed <- S_throw.DESTRUCTION.CALLED)',
        'S_discarded_found = $drive_steps(S_throw,1)',
        r'S_discarded_found.COMPLETION = NORMAL \/ S_discarded_found.COMPLETION = BUDGET',
        'S_discarded = $test_std_running(S_discarded_found)',
        'S_discarded.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_discarded.DESTRUCTION.CALLED = S_throw.DESTRUCTION.CALLED',
        'S_discarded.CONSTANTSTDOBJECTS = S_throw.CONSTANTSTDOBJECTS',
        *std.reach('S_caught','S_discarded',2,catch_line),
        'S_caught.CONSTCONTEXT = eps',
        '$user_constant_at(S_caught.USERCONSTANTS,$ptascii("V63_RETRY")) = eps',
        '$global_std_record(S_caught.CONSTANTSTDOBJECTS,n_failed) = (pconstantstdobject_failed)',
        '~$constant_value_class_valid(S_caught,POBJECT n_failed,PVSTDCLASS n_failed porigin_failed)',
        '$heap_owners($heap_graph(S_caught),HOBJECT n_donor) = 2',
        *std.property_value('S_caught','n_donor',31,'caught')]
    for node in ['HOBJECT n_failed','HARRAY n_failed_array','HARRAY n_failed_child']:
        values += [f'~(({node}) <- S_caught.ALLOCATIONS)',f'$heap_owners($heap_graph(S_caught),{node}) = 0']
    values += ['S_wait2 = $drive_steps(S_caught,5000)', 'S_wait2.COMPLETION = SOURCE_PENDING',
        *common.public('S_wait2'), '$eval_response_valid(S_wait2,'+responses[1]+')',
        'S_retry_start = $test_std_running($eval_resume(S_wait2,'+responses[1]+'))',
        *birth('retry','S_retry_start',2,3), 'n_retry =/= n_failed', 'pcpath_retry = pcpath_failed',
        'S_retry_born.CONSTANTSTDOBJECTS = S_retry.CONSTANTSTDOBJECTS ++ [pconstantstdobject_retry]',
        *complete('retry','S_retry_born',3,4),
        'pdefaultnew_retry_values.VALUES = [POBJECT n_donor,PARRAY n_retry_array,PINT 17]',
        'S_retry_values.ARRAYS[n_retry_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_retry_child))]',
        'S_retry_values.ARRAYS[n_retry_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_donor))]',
        *delivered('retry','S_retry_values',['n_retry_array','n_retry_child'],2),
        *query('retry_query','S_retry_done','V63_RETRY','n_retry','porigin_retry'),
        '$global_std_record(S_retry_query.CONSTANTSTDOBJECTS,n_failed) = (pconstantstdobject_failed)',
        '~(n_failed <- S_retry_query.DESTRUCTION.CALLED)',
        *finish('S_retry_query_value',stdout)]
    return values


def prepare(out,originals):
    native=json.loads((originals/'native-report.json').read_text());assert native['passed'] and native['inputs_stable']
    frontend=packet.Worker([str(packet.types.PHP),'-n',*packet.types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=None
    try:
        adapter=packet.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        for name in sources.family.CASES:
            path=originals/name/'main.php';row,=[r for r in native['records'] if r['id']==name]
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['source_sha256']
            assert row['process']['exit']==0 and not base64.b64decode(row['stderr'])
            parsed=frontend.request({'op':'parse','source':packet.b64(path.read_bytes())});assert parsed['accepted']
            main=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            initial=['S_initial = $php_run('+main+',0,'+json.dumps(packet.b64(str(path).encode()))+')','S_initial.COMPLETION = BUDGET']
            responses=[];catch_line=0
            if name.startswith('eval-'):
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const V63_RETRY')]
                for unit_id in [1,2]:
                    parsed_unit=frontend.request({'op':'parse-eval','id':str(unit_id),'mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert parsed_unit['accepted']
                    checked=adapter.request({'op':'check','ast':parsed_unit['ast'],'fixture':True})['fixture']
                    responses.append('SOURCE_ACCEPT '+str(unit_id)+' '+term(code)+' '+checked)
                initial=['S_wait1 = $php_run('+main+',5000,'+json.dumps(packet.b64(str(path).encode()))+')','S_wait1.COMPLETION = SOURCE_PENDING',*common.public('S_wait1'),'$eval_response_valid(S_wait1,'+responses[0]+')','S_initial = $test_std_running($eval_resume(S_wait1,'+responses[0]+'))']
                catch_line=path.read_text().splitlines().index("define('V63_MISSING', 17);")+1
            values=checks(initial,name,base64.b64decode(row['stdout']),responses,catch_line)
            target=out/name;target.mkdir()
            (target/'assertions.json').write_text(json.dumps(values,indent=2)+'\n')
            (target/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+v+'\n' for v in values))
    finally:
        try:
            if adapter:adapter.close()
        finally:frontend.close()


packet.sources,packet.prepare=sources,prepare
family_fingerprint=sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(),**{str(Path(__file__).relative_to(ROOT)):sources.family.sha(__file__)})


sources.family.fingerprint=fingerprint

if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--case',choices=sources.family.CASES)
    args,remaining=parser.parse_known_args()
    if args.case:sources.family.CASES={args.case:sources.family.CASES[args.case]}
    sys.argv=[sys.argv[0],*remaining]
    raise SystemExit(0 if packet.main() else 1)
