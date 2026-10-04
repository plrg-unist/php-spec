#!/usr/bin/env python3
"""Reached class-name operands and captured missing-read continuations."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / '.tools'
import dynamic_new_sources as sources
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r"""
dec $dynamic_new_output(pevent*) : ptbytes
def $dynamic_new_output(eps) = eps
def $dynamic_new_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dynamic_new_output(pevent*)
dec $dynamic_new_is_output(pevent) : bool
def $dynamic_new_is_output(OUTPUT ptbytes) = true
def $dynamic_new_is_output(pevent) = false -- otherwise
def $dynamic_new_output(pevent :: pevent_tail*) = $dynamic_new_output(pevent_tail*)
  -- if ~$dynamic_new_is_output(pevent)
dec $fixture_dynamic_new(ptask*) : pdynamicnew?
def $fixture_dynamic_new((DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*) = (pdynamicnew)
def $fixture_dynamic_new(ptask :: ptask_tail*) = $fixture_dynamic_new(ptask_tail*)
  -- if ~$dynamic_new_marker(ptask)
def $fixture_dynamic_new(eps) = eps
dec $fixture_dynamic_new_event(pclassconstantevent, pdynamicnew, pdynamicnew) : pclassconstantevent
def $fixture_dynamic_new_event(CCUPDATENEW porigin pdynamicnew_event n, pdynamicnew, pdynamicnew_wrong) = CCUPDATENEW porigin pdynamicnew_wrong n
  -- if pdynamicnew_event = pdynamicnew
def $fixture_dynamic_new_event(pclassconstantevent, pdynamicnew, pdynamicnew_wrong) = pclassconstantevent -- otherwise
dec $dynamic_new_phase(pstate,nat) : bool
def $dynamic_new_phase(S,0) = true
  -- if S.TODO = (DYNAMIC_NEW_CLASS z z_fetch) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
def $dynamic_new_phase(S,1) = true
  -- if S.ORIGIN = (porigin)
  -- if $dynamic_new_find(S,S.TODO,porigin) = (pdynamicnew)
  -- if pdynamicnew.SOURCE = POBJECT n_old
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) phpType7* 0 eps (porigin) z) :: (CTOR_RESULT n) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*
def $dynamic_new_phase(S,2) = true
  -- if S.TODO = (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*
  -- if pdynamicnew.SOURCE = POBJECT n_old
  -- if S.RESULT = KNOWN (POBJECT n)
def $dynamic_new_phase(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_outer porigin_method
  -- if $object_name(S,n_outer) = $ptascii("B")
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_inner porigin_method) phpType7* 0 eps (porigin) z) :: (CTOR_RESULT n_inner) :: (DYNAMIC_NEW_FINISH pdynamicnew_inner) :: ptask_tail*
  -- if pdynamicnew_inner.CLASS = $ptascii("A")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CTOR_RESULT n_outer) :: (DYNAMIC_NEW_FINISH pdynamicnew_outer) :: ptask_saved_tail*
  -- if pdynamicnew_outer.SITE = porigin
  -- if pdynamicnew_outer.CLASS = $ptascii("B")
def $dynamic_new_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $fixture_dynamic_new(pframe.TODO) = (pdynamicnew)
  -- if pdynamicnew.CLASS = $ptascii("A")
def $dynamic_new_phase(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext.CALLSITE = (porigin)
  -- if $dynamic_new_keyword(S,porigin) = (NName (BYTES "c2VsZg==") metadata)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CTOR_RESULT n) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*
def $dynamic_new_phase(S,6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $fixture_dynamic_new(pframe.TODO) = (pdynamicnew)
  -- if pdynamicnew.CLOSURE = (pclosureevidence)
  -- if pdynamicnew.CLASS = $ptascii("B")
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("bound")) = (n_cell)
  -- if S_global.STORE[n_cell] = DEFINED PNULL
def $dynamic_new_phase(S,n) = false -- otherwise
dec $dynamic_new_seek(pstate,nat,nat) : pstate
def $dynamic_new_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $dynamic_new_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $dynamic_new_phase(S,n_phase)
def $dynamic_new_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dynamic_new_phase(S,n_phase)
def $dynamic_new_seek(S,n_phase,n) = $dynamic_new_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dynamic_new_phase(S,n_phase) /\ $(n > 0)
"""

PREFIX += '\ndec $fixture_cached_dynamic_ctor(pstate) : bool\ndef $fixture_cached_dynamic_ctor(S) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method\n  -- if $object_name(S,n) = $ptascii("HostB")\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (CTOR_RESULT n) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*\n  -- if pdynamicnew.SOURCE = PSTRING $ptascii("static")\n  -- if pdynamicnew.CLOSURE = (CLOSURE_SCOPE pclosurescope)\ndef $fixture_cached_dynamic_ctor(S) = false -- otherwise\ndec $fixture_cached_dynamic_seek(pstate,nat) : pstate\ndef $fixture_cached_dynamic_seek(S,n) = S\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $fixture_cached_dynamic_seek(S,n) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $fixture_cached_dynamic_ctor(S)\ndef $fixture_cached_dynamic_seek(S,0) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$fixture_cached_dynamic_ctor(S)\ndef $fixture_cached_dynamic_seek(S,n) = $fixture_cached_dynamic_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$fixture_cached_dynamic_ctor(S) /\\ $(n > 0)\n'


def valid(state):
    return [f'$call_descriptors_valid({state})',f'$heap_valid($heap_graph({state}))']


def seek(parent,state,phase):
    return [f'{state}_found = $dynamic_new_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$dynamic_new_phase({state},{phase})',*valid(state)]


def reject(name,expression,predicate):
    state='S_bad_'+name
    return [f'{state} = {expression}',f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})','~'+predicate.replace('STATE',state)]


def completed(state,expected):
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$dynamic_new_output(S_done.EVENTS) = '+cross.invoke.byte_expr(expected),*valid('S_done')]


def retired(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',*seek('S_initial','S_class',0),
        'S_class.TODO = (DYNAMIC_NEW_CLASS z z_fetch) :: ptask_class_tail*',
        'S_class.RESULT = KNOWN (POBJECT n_old)','S_class.ORIGIN = (porigin)',
        '$heap_owners($heap_graph(S_class),HOBJECT n_old) = 1',
        'S_without_result = S_class[.RESULT = KNOWN PNULL]',
        '$heap_owners($heap_graph(S_without_result),HOBJECT n_old) = 0',
        '$dynamic_new_output(S_class.EVENTS) = $ptascii("S|")']
    for name,task in [('line','DYNAMIC_NEW_CLASS $(z + 1) z_fetch'),
                      ('fetch','DYNAMIC_NEW_CLASS z $(z_fetch + 1)')]:
        checks+=reject(name,'S_class[.TODO = ('+task+') :: ptask_class_tail*]','$call_task_valid(STATE,'+task+')')
    checks+=reject('origin','S_class[.ORIGIN = $origin_child(S_class.ORIGIN,[PCFIELD 0])]','$dynamic_new_class_valid(STATE,z,z_fetch)')
    checks+=[*seek('S_class','S_selected',1),
        'S_selected.TODO = (CALL_ARGS (METHOD_TARGET n_new porigin_method) phpType7* 0 eps (porigin) z) :: (CTOR_RESULT n_new) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_selected_tail*',
        'pdynamicnew.SOURCE = POBJECT n_old','pdynamicnew.CLASS = $ptascii("Selected")',
        '~((HOBJECT n_old) <- S_selected.ALLOCATIONS)',
        '$dynamic_new_valid(S_selected,pdynamicnew)',
        '$task_nodes(DYNAMIC_NEW_FINISH pdynamicnew) = eps',
        '$getclass_live_object(S_selected,n_new)',
        'ptask_args = CALL_ARGS (METHOD_TARGET n_new porigin_method) phpType7* 0 eps (porigin) z']
    for name,record in [('selected_line','pdynamicnew[.LINE = $(z + 1)]'),
                        ('selected_fetch','pdynamicnew[.FETCHLINE = $(z_fetch + 1)]'),
                        ('selected_source','pdynamicnew[.SOURCE = PINT 7]'),
                        ('selected_class','pdynamicnew[.CLASS = $ptascii("stdClass")]')]:
        checks+=reject(name,'S_selected[.TODO = [ptask_args,CTOR_RESULT n_new,DYNAMIC_NEW_FINISH '+record+'] ++ ptask_selected_tail*]','$dynamic_new_valid(STATE,'+record+')')
    checks+=reject('missing_marker','S_selected[.TODO = [ptask_args,CTOR_RESULT n_new] ++ ptask_selected_tail*]','$call_task_valid(STATE,ptask_args)')
    checks+=[*seek('S_selected','S_finish',2),
        'S_finish.TODO = (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_finish_tail*',
        'S_finish.RESULT = KNOWN (POBJECT n_new)',
        '$dynamic_new_finish_result(S_finish,pdynamicnew)',
        'pdynamicnew_other = pdynamicnew[.SOURCE = PSTRING $ptascii("stdClass")][.CLASS = $ptascii("stdClass")]',
        '$dynamic_new_valid(S_finish,pdynamicnew_other)']
    checks+=reject('finish_class','S_finish[.TODO = (DYNAMIC_NEW_FINISH pdynamicnew_other) :: ptask_finish_tail*]','$dynamic_new_finish_result(STATE,pdynamicnew_other)')
    checks+=completed('S_finish',expected)
    checks+=['~((HOBJECT n_old) <- S_done.ALLOCATIONS)']
    return checks


def recursive(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',*seek('S_initial','S_nested',3),
        'S_nested.CURRENT = (pcallcontext_outer)',
        'pcallcontext_outer.TARGET = METHOD_TARGET n_outer porigin_method',
        'S_nested.TODO = (CALL_ARGS (METHOD_TARGET n_inner porigin_method) phpType7* 0 eps (porigin) z) :: (CTOR_RESULT n_inner) :: (DYNAMIC_NEW_FINISH pdynamicnew_inner) :: ptask_nested_tail*',
        'S_nested.FRAMES = pframe_outer :: pframe_outer_tail*',
        'pframe_outer.TODO = (CTOR_RESULT n_outer) :: (DYNAMIC_NEW_FINISH pdynamicnew_outer) :: ptask_saved_tail*',
        'pdynamicnew_inner.SITE = porigin','pdynamicnew_outer.SITE = porigin',
        'pdynamicnew_inner.SOURCE = PSTRING $ptascii("A")',
        'pdynamicnew_outer.SOURCE = PSTRING $ptascii("B")',
        '$object_name(S_nested,n_outer) = $ptascii("B")',
        '$object_name(S_nested,n_inner) = $ptascii("A")','n_inner =/= n_outer',
        '$new_source_name(S_nested,porigin) = ($ptascii("A"))',
        '$constructor_source_name(S_nested,pcallcontext_outer.TARGET,porigin) = ($ptascii("B"))',
        '$call_current_valid(S_nested)',
        'S_saved = $constant_frame_scope(S_nested,pframe_outer,pframe_outer_tail*)',
        '$dynamic_new_valid(S_saved,pdynamicnew_outer)',*valid('S_saved')]
    checks+=reject('saved_receiver','S_nested[.FRAMES = pframe_outer[.TODO = (CTOR_RESULT n_inner) :: (DYNAMIC_NEW_FINISH pdynamicnew_outer) :: ptask_saved_tail*] :: pframe_outer_tail*]',
                   '($constructor_source_name(STATE,pcallcontext_outer.TARGET,porigin) = ($ptascii("B")))')
    checks+=reject('saved_missing','S_nested[.FRAMES = pframe_outer[.TODO = (CTOR_RESULT n_outer) :: ptask_saved_tail*] :: pframe_outer_tail*]',
                   '($constructor_source_name(STATE,pcallcontext_outer.TARGET,porigin) = ($ptascii("B")))')
    wrong='pdynamicnew_outer[.SOURCE = PSTRING $ptascii("A")][.CLASS = $ptascii("A")]'
    checks+=reject('saved_class','S_nested[.FRAMES = pframe_outer[.TODO = (CTOR_RESULT n_outer) :: (DYNAMIC_NEW_FINISH '+wrong+') :: ptask_saved_tail*] :: pframe_outer_tail*]',
                   '$call_current_valid(STATE)')
    checks+=completed('S_nested',expected)
    checks+=['~((HOBJECT n_inner) <- S_done.ALLOCATIONS)']
    return checks


def contexts(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',*seek('S_initial','S_handler',4),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_handler) :: ptask_handler_tail*',
        '$fixture_dynamic_new(pframe_handler.TODO) = (pdynamicnew)',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        'S_emitter = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
        '$dynamic_new_valid(S_emitter,pdynamicnew)',
        '$new_source_name(S_emitter,pdynamicnew.SITE) = ($ptascii("A"))',*valid('S_emitter'),
        *completed('S_handler',expected)]
    return checks


def keyword(initial,expected):
    return ['S_keyword_initial = '+initial,'~S_keyword_initial.COMPILESTOP',*seek('S_keyword_initial','S_keyword',5),
        'S_keyword.CURRENT = (pcallcontext_keyword)',
        'pcallcontext_keyword.TARGET = METHOD_TARGET n_keyword porigin_method_keyword',
        'pcallcontext_keyword.CALLSITE = (porigin_keyword)',
        'S_keyword.FRAMES = pframe_keyword :: pframe_keyword_tail*',
        'pframe_keyword.TODO = (CTOR_RESULT n_keyword) :: (DYNAMIC_NEW_FINISH pdynamicnew_keyword) :: ptask_keyword_tail*',
        'pdynamicnew_keyword.SOURCE = PSTRING $ptascii("self")',
        'pdynamicnew_keyword.CLASS = $ptascii("A")',
        'pframe_keyword.CONTEXT = (pcallcontext_caller)',
        '$origin_node(S_keyword.SOURCES,porigin_keyword) = (NExprNew expression_keyword phpType6_keyword metadata_keyword)',
        'pdeclcalls = [(pcallcontext_caller.FUNCTION,pcallcontext_caller.CALLSITE,pcallcontext_caller.LEXICAL_CLASS,pcallcontext_caller.CALLED_CLASS)]',
        '$class_named(S_keyword.CLASSNAMES,$ptascii("a")) = (porigin_a)',
        '$declaration_new_selection(S_keyword,porigin_keyword,expression_keyword,porigin_a,pdeclcalls)',
        '$constructor_source_name(S_keyword,pcallcontext_keyword.TARGET,porigin_keyword) = ($ptascii("A"))',
        'S_keyword_done = $drive_steps(S_keyword,2048)',
        r'S_keyword_done.COMPLETION = NORMAL /\ S_keyword_done.TODO = eps /\ S_keyword_done.CURRENT = eps /\ S_keyword_done.FRAMES = eps',
        '$dynamic_new_output(S_keyword_done.EVENTS) = '+cross.invoke.byte_expr(expected),*valid('S_keyword_done')]


def rebound(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',*seek('S_initial','S_handler',6),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_handler) :: ptask_handler_tail*',
        '$fixture_dynamic_new(pframe_handler.TODO) = (pdynamicnew)',
        'pdynamicnew.CLOSURE = (pclosureevidence)',
        '$class_named(S_handler.CLASSNAMES,$ptascii("b")) = (porigin_b)',
        'pdynamicnew.SCOPE = (porigin_b)', 'pdynamicnew.CALLED = (porigin_b)',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        'S_emitter = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
        '$dynamic_new_valid(S_emitter,pdynamicnew)',
        'n_closure = $closure_evidence_object(pclosureevidence)',
        '$getclass_live_object(S_emitter,n_closure)',
        '$class_named(S_handler.CLASSNAMES,$ptascii("a")) = (porigin_a)',
        'pdynamicnew_wrong = pdynamicnew[.SCOPE = (porigin_a)]',
        '~$dynamic_new_record_valid(S_emitter,pdynamicnew_wrong)',
        *valid('S_emitter'),*completed('S_handler',expected),
        '$class_constant_history_valid(S_done)',
        '$dynamic_new_record_valid(S_done,pdynamicnew)',
        '$closure_evidence_valid(S_done,pclosureevidence)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '$closure_binding_at(S_done.CLOSUREBINDINGS,n_closure) = eps',
        '$closure_scope_at(S_done.CLOSURESCOPES,n_closure) = eps',
        'n_prefix = |S_done.DECLARATIONS|',
        '(CCUPDATENEW porigin_b pdynamicnew n_prefix) <- S_done.CLASSCONSTANTHISTORY',
        'pclassconstantevent* = S_done.CLASSCONSTANTHISTORY']
    checks+=reject('history_scope','S_done[.CLASSCONSTANTHISTORY = ($fixture_dynamic_new_event(pclassconstantevent,pdynamicnew,pdynamicnew_wrong))*]',
                   '$class_constant_history_valid(STATE)')
    return checks


def cached_method(initial,expected,valid,completed):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',
        'S_found = $fixture_cached_dynamic_seek(S_initial,2048)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_ctor = S_found[.COMPLETION = NORMAL]', '$fixture_cached_dynamic_ctor(S_ctor)', *valid('S_ctor'),
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'S_ctor.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (CTOR_RESULT n_ctor) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*',
        'pdynamicnew.CLOSURE = (CLOSURE_SCOPE pclosurescope)',
        '$class_named(S_ctor.CLASSNAMES,$ptascii("hosta")) = (porigin_a)',
        '$class_named(S_ctor.CLASSNAMES,$ptascii("hostb")) = (porigin_b)',
        'pdynamicnew.SCOPE = (porigin_a)', 'pdynamicnew.CALLED = (porigin_b)',
        'pframe.CONTEXT = (pcallcontext_maker)',
        'pcallcontext_maker.TARGET = CLOSURE_TARGET pclosurescope.OBJECT',
        '$object_body(S_ctor.OBJECTS[pclosurescope.OBJECT]) = METHODCLOSURE porigin_method porigin_site porigin_requested pmethodcapture?',
        'S_maker = $constant_frame_scope(S_ctor,pframe,pframe_tail*)',
        '$dynamic_new_valid(S_maker,pdynamicnew)',
        '$constructor_source_name(S_ctor,pcallcontext_ctor.TARGET,pdynamicnew.SITE) = ($ptascii("HostB"))',
        *completed('S_ctor',expected),
        '~((HOBJECT pclosurescope.OBJECT) <- S_done.ALLOCATIONS)',
        '$closure_scope_at(S_done.CLOSURESCOPES,pclosurescope.OBJECT) = eps',
        '$dynamic_new_record_valid(S_done,pdynamicnew)',
        'pclosurescope_wrong = pclosurescope[.CALLED = porigin_a]',
        'pdynamicnew_wrong = pdynamicnew[.CALLED = (porigin_a)][.CLASS = $ptascii("HostA")][.CLOSURE = (CLOSURE_SCOPE pclosurescope_wrong)]',
        '~$dynamic_new_record_valid(S_done,pdynamicnew_wrong)']
    return checks

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['retired','recursive','contexts','rebound','cached'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    name = {'retired':'dynamic-new-selector-retirement-source',
            'recursive':'dynamic-new-recursive-inherited-constructor',
            'contexts':'dynamic-new-recursive-cold-selection',
            'rebound':'dynamic-new-rebound-keyword-cold-retirement','cached':'dynamic-new-cached-method-composition'}[args.group]
    expected = sources.EXPECTED[name]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='dynamic-new-protocol-' + args.group + '-', dir=OWN))
    source = out / 'source.php'
    source.write_bytes(sources.CASES[name])
    source_before = sha(source)
    report = {'passed':False,'before':before,'source':str(source),'source_sha256':source_before,
              'profile':cross.invoke.types.PROFILE,'mode':'unused' if args.elaborate_only else 'source-reached','group':args.group}
    print(out, flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,'-d',
            'extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        body = retired(initial,expected) if args.group == 'retired' else recursive(initial,expected) if args.group == 'recursive' else contexts(initial,expected) if args.group == 'contexts' else rebound(initial,expected) if args.group == 'rebound' else cached_method(initial,expected,valid,completed)
        if args.group == 'contexts':
            keyword_name = 'dynamic-new-binary-keyword-inherited-constructor'
            keyword_source = out / 'keyword.php'
            keyword_source.write_bytes(sources.CASES[keyword_name])
            keyword_parsed = frontend.request({'op':'parse','source':base64.b64encode(keyword_source.read_bytes()).decode()})
            assert keyword_parsed['accepted'] is True
            keyword_checked = adapter.request({'op':'check','ast':keyword_parsed['ast'],'fixture':True})
            assert keyword_checked['ok'] is True
            body += ['program_keyword = '+keyword_checked['fixture'],*keyword('$php_run(program_keyword,0,'+json.dumps(base64.b64encode(os.fsencode(keyword_source)).decode())+')',sources.EXPECTED[keyword_name])]
        clauses = ['program_source = ' + checked['fixture'], *body]
        (out / 'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+c+'\n' for c in clauses)+'\ndec $main() : bool\ndef $main() = '+('true' if args.elaborate_only else '$body()')+'\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),*[str(ROOT / p) for p in modules],str(fixture)],out / 'numeric',120,ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True,assertions=len(clauses),fixture_sha256=sha(fixture),state_assertions_evaluated=0 if args.elaborate_only else len(clauses),unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['source_unchanged'] = source_before == sha(source)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(out/'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
