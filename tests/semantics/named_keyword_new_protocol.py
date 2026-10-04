#!/usr/bin/env python3
"""Reached named NEW callers, service scope and cold history."""
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
import named_keyword_new_sources as sources
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r"""
dec $keyword_new_output(pevent*) : ptbytes
def $keyword_new_output(eps) = eps
def $keyword_new_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $keyword_new_output(pevent*)
dec $keyword_new_is_output(pevent) : bool
def $keyword_new_is_output(OUTPUT ptbytes) = true
def $keyword_new_is_output(pevent) = false -- otherwise
def $keyword_new_output(pevent :: pevent_tail*) = $keyword_new_output(pevent_tail*)
  -- if ~$keyword_new_is_output(pevent)
dec $fixture_keyword_new(ptask*) : pdynamicnew?
def $fixture_keyword_new((DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*) = (pdynamicnew)
def $fixture_keyword_new(ptask :: ptask_tail*) = $fixture_keyword_new(ptask_tail*)
  -- if ~$dynamic_new_marker(ptask)
def $fixture_keyword_new(eps) = eps
dec $fixture_keyword_event(pclassconstantevent, pdynamicnew, pdynamicnew) : pclassconstantevent
def $fixture_keyword_event(CCUPDATENEW porigin pdynamicnew_event n, pdynamicnew, pdynamicnew_wrong) = CCUPDATENEW porigin pdynamicnew_wrong n
  -- if pdynamicnew_event = pdynamicnew
def $fixture_keyword_event(pclassconstantevent, pdynamicnew, pdynamicnew_wrong) = pclassconstantevent -- otherwise
dec $fixture_keyword_task(ptask, pdynamicnew, pdynamicnew) : ptask
def $fixture_keyword_task(DYNAMIC_NEW_FINISH pdynamicnew, pdynamicnew, pdynamicnew_wrong) = DYNAMIC_NEW_FINISH pdynamicnew_wrong
def $fixture_keyword_task(ptask, pdynamicnew, pdynamicnew_wrong) = ptask -- otherwise
dec $fixture_keyword_line(pcodeexpr, pcpath, int) : pcodeexpr
def $fixture_keyword_line(CODEEXPR pcpath z b, pcpath, z_wrong) = CODEEXPR pcpath z_wrong b
def $fixture_keyword_line(CODECALL_INIT pcpath z, pcpath, z_wrong) = CODECALL_INIT pcpath z_wrong
def $fixture_keyword_line(pcodeexpr, pcpath, z_wrong) = pcodeexpr -- otherwise
dec $fixture_keyword_code(pcode, nat, pcpath, int) : pcode
def $fixture_keyword_code(pcode, n, pcpath, z_wrong) = pcode[.EXPRESSIONS = ($fixture_keyword_line(pcodeexpr, pcpath, z_wrong))*]
  -- if pcode.UNIT = n
  -- if pcodeexpr* = pcode.EXPRESSIONS
def $fixture_keyword_code(pcode, n, pcpath, z_wrong) = pcode -- otherwise
dec $fixture_keyword_eval(pevalbinding, nat, porigin) : pevalbinding
def $fixture_keyword_eval(pevalbinding, n, porigin_wrong) = pevalbinding[.CLASS = (porigin_wrong)]
  -- if pevalbinding.UNIT = n
def $fixture_keyword_eval(pevalbinding, n, porigin_wrong) = pevalbinding -- otherwise
dec $keyword_new_phase(pstate,nat) : bool
def $keyword_new_phase(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $fixture_keyword_new(pframe.TODO) = (pdynamicnew)
  -- if pdynamicnew.CLOSURE = (pclosureevidence)
  -- if pdynamicnew.CLASS = $ptascii("B")
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("bound")) = (n_cell)
  -- if S_global.STORE[n_cell] = DEFINED PNULL
def $keyword_new_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_b porigin_method
  -- if $object_name(S,n_b) = $ptascii("B")
  -- if S.FRAMES = pframe_b :: pframe_outer :: pframe_a :: pframe_tail*
  -- if pframe_b.TODO = (CTOR_RESULT n_b) :: (DYNAMIC_NEW_FINISH pdynamicnew_b) :: ptask_b_tail*
  -- if pframe_a.TODO = (CTOR_RESULT n_a) :: (DYNAMIC_NEW_FINISH pdynamicnew_a) :: ptask_a_tail*
  -- if pdynamicnew_b.SITE = pdynamicnew_a.SITE
  -- if pdynamicnew_b.CLASS = $ptascii("B") /\ pdynamicnew_a.CLASS = $ptascii("A")
def $keyword_new_phase(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_a porigin_method
  -- if pcallcontext.CALLSITE = (PORIGIN n_unit pcpath)
  -- if $(n_unit > 0)
  -- if $eval_binding_at(S.EVALBINDINGS,n_unit) = (pevalbinding)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CTOR_RESULT n_a) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*
  -- if pdynamicnew.SOURCE = PSTRING $ptascii("self")
def $keyword_new_phase(S,n) = false -- otherwise
dec $keyword_new_seek(pstate,nat,nat) : pstate
def $keyword_new_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $keyword_new_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $keyword_new_phase(S,n_phase)
def $keyword_new_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$keyword_new_phase(S,n_phase)
def $keyword_new_seek(S,n_phase,n) = $keyword_new_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$keyword_new_phase(S,n_phase) /\ $(n > 0)
"""


PREFIX += '\ndec $fixture_const_keyword_ctor(pstate) : bool\ndef $fixture_const_keyword_ctor(S) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method\n  -- if $object_name(S,n) = $ptascii("ConstantNewB")\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (CTOR_RESULT n) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*\n  -- if pdynamicnew.SOURCE = PSTRING $ptascii("static")\n  -- if pdynamicnew.CLOSURE = (CLOSURE_SCOPE pclosurescope)\ndef $fixture_const_keyword_ctor(S) = false -- otherwise\ndec $fixture_const_keyword_seek(pstate,nat) : pstate\ndef $fixture_const_keyword_seek(S,n) = S\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $fixture_const_keyword_seek(S,n) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $fixture_const_keyword_ctor(S)\ndef $fixture_const_keyword_seek(S,0) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$fixture_const_keyword_ctor(S)\ndef $fixture_const_keyword_seek(S,n) = $fixture_const_keyword_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$fixture_const_keyword_ctor(S) /\\ $(n > 0)\n'

def valid(state):
    return [f'$call_descriptors_valid({state})',f'$heap_valid($heap_graph({state}))']


def seek(parent,state,phase):
    return [f'{state}_found = $keyword_new_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$keyword_new_phase({state},{phase})',*valid(state)]


def reject(name,expression,predicate):
    state='S_bad_'+name
    return [f'{state} = {expression}',f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})','~'+predicate.replace('STATE',state)]


def completed(state,expected):
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$keyword_new_output(S_done.EVENTS) = '+cross.invoke.byte_expr(expected),*valid('S_done')]


def cold(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',*seek('S_initial','S_handler',0),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_handler) :: ptask_handler_tail*',
        '$fixture_keyword_new(pframe_handler.TODO) = (pdynamicnew)',
        'pdynamicnew.SITE = PORIGIN n_unit pcpath',
        'pdynamicnew.SOURCE = PSTRING $ptascii("self")',
        'pdynamicnew.CLOSURE = (pclosureevidence)',
        'n_closure = $closure_evidence_object(pclosureevidence)',
        '$heap_owners($heap_graph(S_handler),HOBJECT n_closure) = 1',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        'S_emitter = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
        '$dynamic_new_valid(S_emitter,pdynamicnew)',
        '$ordinary_keyword_new_site(S_emitter,pdynamicnew.SITE)',
        '$new_source_name(S_emitter,pdynamicnew.SITE) = ($ptascii("B"))',
        '$task_nodes(DYNAMIC_NEW_FINISH pdynamicnew) = eps',*valid('S_emitter'),
        'ptask_emitter* = S_emitter.TODO',
        'pdynamicnew_wrong = pdynamicnew[.SOURCE = PSTRING $ptascii("static")]']
    checks+=reject('source','S_emitter[.TODO = ($fixture_keyword_task(ptask_emitter,pdynamicnew,pdynamicnew_wrong))*]',
                   '$dynamic_new_record_valid(STATE,pdynamicnew_wrong)')
    checks+=['pcode* = S_emitter.CODE','pdynamicnew_line = pdynamicnew[.LINE = $(pdynamicnew.LINE + 1)][.FETCHLINE = $(pdynamicnew.FETCHLINE + 1)]']
    checks+=reject('paired_line','S_emitter[.CODE = ($fixture_keyword_code(pcode,n_unit,pcpath,$(pdynamicnew.LINE + 1)))*][.TODO = ($fixture_keyword_task(ptask_emitter,pdynamicnew,pdynamicnew_line))*]',
                   '$ordinary_keyword_new_site(STATE,pdynamicnew.SITE)')
    checks+=completed('S_handler',expected)
    checks+=['$dynamic_new_record_valid(S_done,pdynamicnew)',
        '$class_constant_history_valid(S_done)',
        '$closure_evidence_valid(S_done,pclosureevidence)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '$closure_binding_at(S_done.CLOSUREBINDINGS,n_closure) = eps',
        '$closure_scope_at(S_done.CLOSURESCOPES,n_closure) = eps',
        '$class_named(S_done.CLASSNAMES,$ptascii("b")) = (porigin_b)',
        'n_prefix = |S_done.DECLARATIONS|',
        '(CCUPDATENEW porigin_b pdynamicnew n_prefix) <- S_done.CLASSCONSTANTHISTORY',
        'pclassconstantevent* = S_done.CLASSCONSTANTHISTORY']
    checks+=reject('history_source','S_done[.CLASSCONSTANTHISTORY = ($fixture_keyword_event(pclassconstantevent,pdynamicnew,pdynamicnew_wrong))*]',
                   '$class_constant_history_valid(STATE)')
    return checks


def recursive(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',*seek('S_initial','S_nested',1),
        'S_nested.CURRENT = (pcallcontext_b)',
        'pcallcontext_b.TARGET = METHOD_TARGET n_b porigin_method',
        'pcallcontext_b.CALLSITE = (porigin)',
        'S_nested.FRAMES = pframe_b :: pframe_outer :: pframe_a :: pframe_tail*',
        'pframe_b.TODO = (CTOR_RESULT n_b) :: (DYNAMIC_NEW_FINISH pdynamicnew_b) :: ptask_b_tail*',
        'pframe_a.TODO = (CTOR_RESULT n_a) :: (DYNAMIC_NEW_FINISH pdynamicnew_a) :: ptask_a_tail*',
        r'pdynamicnew_b.SITE = porigin /\ pdynamicnew_a.SITE = porigin',
        r'pdynamicnew_b.SOURCE = PSTRING $ptascii("static") /\ pdynamicnew_a.SOURCE = PSTRING $ptascii("static")',
        'n_b =/= n_a',
        '$object_name(S_nested,n_a) = $ptascii("A")',
        '$constructor_source_name(S_nested,pcallcontext_b.TARGET,porigin) = ($ptascii("B"))',
        '$call_current_valid(S_nested)',
        'S_b = $constant_frame_scope(S_nested,pframe_b,pframe_outer :: pframe_a :: pframe_tail*)',
        'S_a = $constant_frame_scope(S_nested,pframe_a,pframe_tail*)',
        '$dynamic_new_valid(S_b,pdynamicnew_b)',
        '$dynamic_new_valid(S_a,pdynamicnew_a)',*valid('S_b'),*valid('S_a')]
    checks+=reject('caller_receiver','S_nested[.FRAMES = pframe_b[.TODO = (CTOR_RESULT n_a) :: (DYNAMIC_NEW_FINISH pdynamicnew_b) :: ptask_b_tail*] :: pframe_outer :: pframe_a :: pframe_tail*]',
                   '($constructor_source_name(STATE,pcallcontext_b.TARGET,porigin) = ($ptascii("B")))')
    checks+=reject('older_marker','S_nested[.FRAMES = pframe_b[.TODO = (CTOR_RESULT n_b) :: (DYNAMIC_NEW_FINISH pdynamicnew_a) :: ptask_b_tail*] :: pframe_outer :: pframe_a :: pframe_tail*]',
                   '$call_current_valid(STATE)')
    checks+=completed('S_nested',expected)
    checks+=['~((HOBJECT n_a) <- S_done.ALLOCATIONS)','~((HOBJECT n_b) <- S_done.ALLOCATIONS)']
    return checks


def eval_scope(initial,expected):
    checks=['S_initial = '+initial,'~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],2048)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*',
        'pevalcontext.BYTES = '+cross.invoke.byte_expr(b'return [new self, new parent, new static];'),
        '$eval_response_valid(S_wait,SOURCE_ACCEPT pevalcontext.UNIT pevalcontext.BYTES program_eval)',
        *valid('S_wait'),
        'S_eval = $eval_resume(S_wait,SOURCE_ACCEPT pevalcontext.UNIT pevalcontext.BYTES program_eval)',
        'S_eval.COMPLETION = NORMAL',*valid('S_eval'),*seek('S_eval','S_ctor',2),
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'pcallcontext_ctor.TARGET = METHOD_TARGET n_a porigin_method',
        'pcallcontext_ctor.CALLSITE = (PORIGIN n_unit pcpath)',
        'S_ctor.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (CTOR_RESULT n_a) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*',
        '$eval_binding_at(S_ctor.EVALBINDINGS,n_unit) = (pevalbinding)',
        '$goto_source_owner($all_functions(S_ctor),n_unit,pcpath) = eps',
        '$class_named(S_ctor.CLASSNAMES,$ptascii("a")) = (porigin_a)',
        '$class_named(S_ctor.CLASSNAMES,$ptascii("b")) = (porigin_b)',
        r'pdynamicnew.SCOPE = (porigin_a) /\ pdynamicnew.CALLED = (porigin_b)',
        'pevalbinding.CLASS = (porigin_a)',
        '$dynamic_new_scope_source(S_ctor,pdynamicnew) = pevalbinding.SITE',
        '$dynamic_new_record_valid(S_ctor,pdynamicnew)',
        '$constructor_source_name(S_ctor,pcallcontext_ctor.TARGET,pdynamicnew.SITE) = ($ptascii("A"))',
        'S_caller = $constant_frame_scope(S_ctor,pframe,pframe_tail*)',
        '$dynamic_new_valid(S_caller,pdynamicnew)',*valid('S_caller'),
        'pevalbinding_item* = S_ctor.EVALBINDINGS']
    checks+=reject('entry_scope','S_ctor[.EVALBINDINGS = ($fixture_keyword_eval(pevalbinding_item,n_unit,porigin_b))*]',
                   '$dynamic_new_record_valid(STATE,pdynamicnew)')
    checks+=completed('S_ctor',expected)
    checks+=['$eval_state_valid(S_done)',
        '$dynamic_new_record_valid(S_done,pdynamicnew)',
        '$keyword_new_entry_source(S_done,pdynamicnew.SITE,pdynamicnew.SCOPE) = pevalbinding.SITE',
        '~((HOBJECT n_a) <- S_done.ALLOCATIONS)']
    return checks

def constant_method(initial, expected, valid, completed):
    return [
        'S_initial = ' + initial, '~S_initial.COMPILESTOP',
        'S_found = $fixture_const_keyword_seek(S_initial,2048)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_ctor = S_found[.COMPLETION = NORMAL]',
        '$fixture_const_keyword_ctor(S_ctor)', *valid('S_ctor'),
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'S_ctor.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (CTOR_RESULT n_ctor) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*',
        'pdynamicnew.CLOSURE = (CLOSURE_SCOPE pclosurescope)',
        '$class_named(S_ctor.CLASSNAMES,$ptascii("constantnewa")) = (porigin_a)',
        '$class_named(S_ctor.CLASSNAMES,$ptascii("constantnewb")) = (porigin_b)',
        'pdynamicnew.SCOPE = (porigin_a)', 'pdynamicnew.CALLED = (porigin_b)',
        '~$class_constant_parent_chain(S_ctor,porigin_b,porigin_a,|S_ctor.CLASSES|)',
        'pframe.CONTEXT = (pcallcontext_maker)',
        'pcallcontext_maker.TARGET = CLOSURE_TARGET pclosurescope.OBJECT',
        '$object_body(S_ctor.OBJECTS[pclosurescope.OBJECT]) = METHODCLOSURE porigin_method porigin_site porigin_requested pmethodcapture?',
        'S_maker = $constant_frame_scope(S_ctor,pframe,pframe_tail*)',
        '$dynamic_new_valid(S_maker,pdynamicnew)',
        '$class_static_selection_scope_method(S_maker,pdynamicnew.SITE,pclosurescope.LEXICAL) = (pmethoddesc)',
        '$class_constant_callable_method_history_owner(S_maker,pmethoddesc,porigin_site,porigin_requested,pclosurescope) =/= eps',
        '$constructor_source_name(S_ctor,pcallcontext_ctor.TARGET,pdynamicnew.SITE) = ($ptascii("ConstantNewB"))',
        *completed('S_ctor', expected),
        '~((HOBJECT pclosurescope.OBJECT) <- S_done.ALLOCATIONS)',
        '$closure_scope_at(S_done.CLOSURESCOPES,pclosurescope.OBJECT) = eps',
        '$dynamic_new_record_valid(S_done,pdynamicnew)',
        '$class_constant_callable_method_history_owner(S_done,pmethoddesc,porigin_site,porigin_requested,pclosurescope) =/= eps',
        'pclosurescope_wrong = pclosurescope[.CALLED = porigin_a]',
        'pdynamicnew_wrong = pdynamicnew[.CALLED = (porigin_a)][.CLASS = $ptascii("ConstantNewA")][.CLOSURE = (CLOSURE_SCOPE pclosurescope_wrong)]',
        '~$dynamic_new_record_valid(S_done,pdynamicnew_wrong)',
    ]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['cold','recursive','eval','constant'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    name = {'cold':'named-keyword-cold-maker-retirement',
            'recursive':'named-keyword-recursive-factory',
            'eval':'named-keyword-eval-inherited-scope',
            'constant':'named-keyword-constant-method-cold-retirement'}[args.group]
    expected = sources.EXPECTED[name]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='keyword-new-protocol-' + args.group + '-', dir=OWN))
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
        clauses = ['program_source = ' + checked['fixture']]
        if args.group == 'eval':
            eval_parsed = frontend.request({'op':'parse-eval','id':'1','mode':'eval',
                'profile':'cli-raw-85','source':base64.b64encode(b'return [new self, new parent, new static];').decode()})
            assert eval_parsed['accepted'] is True
            eval_checked = adapter.request({'op':'check','ast':eval_parsed['ast'],'fixture':True})
            assert eval_checked['ok'] is True
            clauses += ['program_eval = '+eval_checked['fixture']]
        body = constant_method(initial,expected,valid,completed) if args.group == 'constant' else {'cold':cold,'recursive':recursive,'eval':eval_scope}[args.group](initial,expected)
        clauses += body
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
