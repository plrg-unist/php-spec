#!/usr/bin/env python3
"""Reached rejected current values, real argument discard and late store calls."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import global_constant_stdclass_arguments_protocol as previous
import global_constant_stdclass_duplicate_arguments_sources as sources

packet, std, common = previous.packet, previous.std, previous.common
ROOT, text, term = previous.ROOT, previous.text, previous.term
PREFIX = previous.PREFIX + r'''
dec $test_rejected_front(pstate, nat, nat) : bool
def $test_rejected_front(S,0,n_object) = true
  -- if S.TODO = (DEFAULT_NEW_SEND pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.OBJECT = n_object
  -- if $global_std_duplicate(S,pdefaultnew)
  -- if pdefaultnew.ARGUMENTS[pdefaultnew.INDEX] = NArg (NIdentifier (BYTES text) metadata_name) expression (BOOLEAN false) (BOOLEAN false) metadata
  -- if $parameter_new_name_present(pdefaultnew.ARGUMENTS[0:pdefaultnew.INDEX],$base64(text))
def $test_rejected_front(S,1,n_object) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if S.DESTRUCTION.PHASE = DESTRUCTION_STORE
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n_object)
  -- if ~(n_object <- S.DESTRUCTION.CALLED)
  -- if $destructor_method(S,n_object) =/= eps
def $test_rejected_front(S,n_phase,n_object) = false -- otherwise
dec $test_rejected_seek(pstate, nat, nat, nat) : pstate
def $test_rejected_seek(S,n_phase,n_object,0) = S
def $test_rejected_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_rejected_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_rejected_seek(S,n_phase,n_object,n) = $test_rejected_seek($test_std_running($drive_steps(S,1)),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_rejected_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state,start,phase,obj):
    return [f'{state}_found = $test_rejected_seek({start},{phase},{obj},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_std_running({state}_found)',
        f'$test_rejected_front({state},{phase},{obj})',*common.public(state)]


def born(start):
    return [*previous.reach('S_before',start,0),
        'S_before.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN 1 pcpath_site',
        'S_before.CONSTCONTEXT = (pconstantcontext)', 'porigin_decl = pconstantcontext.ORIGIN',
        'S_before.DESTRUCTION.REJECTED = eps',
        '$origin_node(S_before.SOURCES,porigin_site) = (NExprNew name (SEQUENCE phpType7*) metadata)',
        '|phpType7*| = 3', '$parameter_new_prefix(phpType7*)', '~$default_new_unique(phpType7*)',
        *std.step('S_born','S_before'),
        'S_born.TODO = (DEFAULT_NEW_ARGS pdefaultnew_born) :: ptask_born*',
        'n_outer = |S_before.OBJECTS|', 'pdefaultnew_born.OBJECT = n_outer',
        'pdefaultnew_born.SITE = porigin_site', 'pdefaultnew_born.ARGUMENTS = phpType7*',
        'pdefaultnew_born.INDEX = 0', 'pdefaultnew_born.VALUES = eps',
        'S_born.OBJECTS = S_before.OBJECTS ++ [STDINSTANCE]',
        'S_born.ALLOCATIONS = S_before.ALLOCATIONS ++ [HOBJECT n_outer]',
        '$global_std_record(S_born.CONSTANTSTDOBJECTS,n_outer) = (pconstantstdobject)',
        '~pconstantstdobject.COMPLETE', 'pconstantstdobject.DECL = porigin_decl',
        'pconstantstdobject.SITE = porigin_site',
        'S_born.CONSTANTSTDOBJECTS = S_before.CONSTANTSTDOBJECTS ++ [pconstantstdobject]',
        '$global_std_pending(S_born,pdefaultnew_born)',
        '$heap_owners($heap_graph(S_born),HOBJECT n_outer) = 1']


def owners(state,array):
    values=[f'(HOBJECT n_current) <- {state}.ALLOCATIONS',
        f'$heap_owners($heap_graph({state}),HOBJECT n_current) = 1']
    if array:
        values += [f'(HARRAY n_root) <- {state}.ALLOCATIONS',f'(HARRAY n_child) <- {state}.ALLOCATIONS',
            f'$heap_owners($heap_graph({state}),HARRAY n_root) = 1',
            f'$heap_owners($heap_graph({state}),HARRAY n_child) = 1',
            f'$heap_edge_owners(HARRAY n_child,$heap_graph({state}).EDGES,[HARRAY n_root]) = 1',
            f'$heap_edge_owners(HOBJECT n_current,$heap_graph({state}).EDGES,[HARRAY n_child]) = 1']
    return values


def checks(initial,name,stdout,after_line):
    array=name.endswith('nested-array')
    target='V64_DUPLICATE' if array else 'V63_REVIEW_BAD'
    current='PARRAY n_root' if array else 'POBJECT n_current'
    rootnode='HARRAY n_root' if array else 'HOBJECT n_current'
    late=b'current|' if array else b'second|'
    assert stdout.endswith(late)
    shape=['S_current.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        'S_current.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current))]'] if array else []
    values=[*initial,*born('S_initial'),*reach('S_current','S_born',0,'n_outer'),
        'S_current.TODO = (DEFAULT_NEW_SEND pdefaultnew) :: ptask_current*',
        'pdefaultnew.OBJECT = n_outer', 'pdefaultnew.INDEX = 1',
        'pdefaultnew.VALUES = [POBJECT n_prior]',
        'S_current.RESULT = KNOWN ('+current+')',*shape,
        '$global_new_record(S_current.CONSTANTOBJECTS,n_prior) = (pconstantobject_prior)',
        '$global_new_record(S_current.CONSTANTOBJECTS,n_current) = (pconstantobject_current)',
        '$global_new_completed(S_current,pconstantobject_prior)',
        '$global_new_completed(S_current,pconstantobject_current)',
        'n_prior =/= n_current', 'n_outer =/= n_current',
        'S_current.DESTRUCTION.REJECTED = eps',
        '$global_std_rejected(S_current,pdefaultnew) = (pconstantargument)',
        'pconstantargument.OBJECT = n_outer', 'pconstantargument.INDEX = 1',
        'pconstantargument.VALUE = '+current,
        'pconstantargument.CONSTANTS = |S_current.USERCONSTANTS|',
        'pconstantargument.READS = eps', '$constant_argument_header(S_current,pconstantargument)',
        '$constant_arguments_valid(S_current,[pconstantargument])',
        '$constant_argument_roots([pconstantargument]) = ['+rootnode+']',
        '$heap_owners($heap_graph(S_current),HOBJECT n_outer) = 1',
        '$heap_owners($heap_graph(S_current),HOBJECT n_prior) = 1',*owners('S_current',array)]
    if array:
        values += ['pconstantargument.CLASS = PVARRAY false [(KINT 0,PVSCALAR),(KINT 1,PVARRAY false [(KINT 0,PVINSTANCE n_current pconstantobject_current.SITE)])]']
    else:
        values += ['pconstantargument.CLASS = PVINSTANCE n_current pconstantobject_current.SITE']
    # Pure projections are never driven.
    values += ['~$constant_argument_header(S_current,pconstantargument[.INDEX = 0])',
        '~$constant_argument_header(S_current,pconstantargument[.INDEX = 3])',
        '~$constant_argument_header(S_current,pconstantargument[.CONSTANTS = $(|S_current.USERCONSTANTS| + 1)])',
        '~$constant_argument_header(S_current,pconstantargument[.VALUE = POBJECT n_outer])',
        '~$constant_argument_header(S_current,pconstantargument[.CLASS = PVOBJECT])',
        '~$constant_argument_header(S_current[.ALLOCATIONS = $destruction_node_delete(S_current.ALLOCATIONS,HOBJECT n_current)],pconstantargument)',
        '~$constant_argument_header(S_current[.CONSTANTOBJECTS = $global_new_record_put(S_current.CONSTANTOBJECTS,pconstantobject_current[.COMPLETE = false])],pconstantargument)',
        '~$constant_argument_header(S_current[.CONSTANTSTDOBJECTS = S_before.CONSTANTSTDOBJECTS],pconstantargument)',
        '~$constant_argument_header(S_current[.CONSTANTSTDOBJECTS = $global_std_record_put(S_current.CONSTANTSTDOBJECTS,pconstantstdobject[.COMPLETE = true])],pconstantargument)',
        '~$constant_arguments_valid(S_current,[pconstantargument,pconstantargument])',
        '$global_std_rejected(S_current[.TODO = eps],pdefaultnew) = eps',
        'S_no_context = S_current[.CONSTCONTEXT = eps]',
        '$global_std_duplicate(S_no_context,pdefaultnew)',
        '$global_std_rejected(S_no_context,pdefaultnew) = eps',
        'S_boundary = $default_new_duplicate(S_no_context,pdefaultnew)',
        'S_boundary.COMPLETION = UNSUPPORTED "global constant duplicate argument value"',
        'S_current.CONSTCONTEXT = (pconstantcontext_current)',
        'porigin_prior = $default_new_arg_origin(pdefaultnew[.INDEX = 0])',
        '$constant_fact_at(pconstantcontext_current.FACTS,porigin_prior) = (pconstantfact_prior)',
        '~$constant_argument_header(S_current,pconstantargument[.READS = [pconstantfact_prior]])']
    launch='S_current'
    if not array:
        values += ['S_pause = $drive_steps(S_current,0)', 'S_pause = S_current[.COMPLETION = BUDGET]',
            'S_resume = $test_std_running(S_pause)', 'S_resume = S_current']
        launch='S_resume'
    values += [*common.step('S_error',launch),
        'S_error.TODO = (THROW_SEARCH n_error) :: (DEFAULT_NEW_SEND pdefaultnew) :: ptask_current*',
        'S_error.CONSTCONTEXT = eps', 'S_error.DESTRUCTION.REJECTED = [pconstantargument]',
        '$constant_argument_header(S_error,pconstantargument)', '$heap_valid($heap_graph(S_error))',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ('+text('Named parameter $keep overwrites previous argument')+')',
        '$throwable_field(S_error,n_error,"line") = PINT 1',*owners('S_error',array),
        '$global_new_argument_owned(S_error,pdefaultnew)',
        *common.step('S_discarded','S_error'),
        'S_discarded.DESTRUCTION.REJECTED = S_error.DESTRUCTION.REJECTED',
        *std.reach('S_after','S_discarded',2,after_line),
        'S_after.CONSTCONTEXT = eps',
        '$user_constant_at(S_after.USERCONSTANTS,'+text(target)+') = eps',
        'S_after.DESTRUCTION.REJECTED = [pconstantargument]',
        '$constant_argument_header(S_after,pconstantargument)',
        '$global_std_record(S_after.CONSTANTSTDOBJECTS,n_outer) = (pconstantstdobject)',
        '~((HOBJECT n_outer) <- S_after.ALLOCATIONS)',
        '~((HOBJECT n_prior) <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_outer) = 0',
        '$heap_owners($heap_graph(S_after),HOBJECT n_prior) = 0',
        '~(n_current <- S_after.DESTRUCTION.CALLED)',*owners('S_after',array),
        *reach('S_store','S_after',1,'n_current'),
        '$test_outputs(S_store.EVENTS) = '+term(stdout[:-len(late)]),
        'S_store.DESTRUCTION.REJECTED = S_after.DESTRUCTION.REJECTED',
        '$constant_argument_header(S_store,pconstantargument)',*owners('S_store',array),
        *std.step('S_selected','S_store'),
        'S_selected.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
        'pdestructorcall.OBJECT = n_current', 'pdestructorcall.STORE',
        '(n_current <- S_selected.DESTRUCTION.CALLED)',
        'S_selected.DESTRUCTION.REJECTED = S_store.DESTRUCTION.REJECTED',
        *previous.finish('S_selected',stdout),
        'S_final.DESTRUCTION.PHASE = DESTRUCTION_DONE',
        'S_final.DESTRUCTION.REJECTED = S_store.DESTRUCTION.REJECTED',
        '$constant_argument_header(S_final,pconstantargument)',*owners('S_final',array)]
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
            code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const ')]
            unit=frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert unit['accepted']
            checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
            response='SOURCE_ACCEPT 1 '+term(code)+' '+checked
            initial=['S_wait = $php_run('+main+',5000,'+json.dumps(packet.b64(str(path).encode()))+')',
                'S_wait.COMPLETION = SOURCE_PENDING',*common.public('S_wait'),
                '$eval_response_valid(S_wait,'+response+')',
                'S_initial = $test_std_running($eval_resume(S_wait,'+response+'))']
            after_line=next(i+1 for i,line in enumerate(path.read_text().splitlines()) if line.startswith("echo defined('"))
            values=checks(initial,name,base64.b64decode(row['stdout']),after_line)
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
