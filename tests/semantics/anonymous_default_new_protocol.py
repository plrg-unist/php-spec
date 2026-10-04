#!/usr/bin/env python3
"""Live receiving Closure scopes survive callback retirement and nested defaults."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from anonymous_default_new_sources import CASES, ROOT
OWN = ROOT / ".tools"
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $anonymous_scope_output(pevent*) : ptbytes
def $anonymous_scope_output(eps) = eps
def $anonymous_scope_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $anonymous_scope_output(pevent*)
dec $anonymous_scope_is_output(pevent) : bool
def $anonymous_scope_is_output(OUTPUT ptbytes) = true
def $anonymous_scope_is_output(pevent) = false -- otherwise
def $anonymous_scope_output(pevent :: pevent_tail*) = $anonymous_scope_output(pevent_tail*)
  -- if ~$anonymous_scope_is_output(pevent)
dec $anonymous_scope_phase(pstate,nat) : bool
def $anonymous_scope_phase(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE =/= eps
  -- if S.CONSTCONTEXT =/= eps
  -- if S.TODO = (EVAL (NExprNew (NName (BYTES text) metadata_name) phpType6 metadata)) :: ptask_tail*
  -- if $ptlc($base64(text)) = $ptascii("self")
def $anonymous_scope_phase(S,1) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = 0
  -- if pdefaultnew.CLASS = $ptascii("A")
def $anonymous_scope_phase(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("bound")) = eps
def $anonymous_scope_phase(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_tail*
  -- if pdefaultctor.NEW.CLASS = $ptascii("A")
  -- if pcallcontext.TARGET = METHOD_TARGET pdefaultctor.NEW.OBJECT pdefaultctor.FUNCTION
def $anonymous_scope_phase(S,4) = true
  -- if $anonymous_scope_phase(S,0)
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS = (porigin_class)
  -- if $class_at(S.CLASSES,porigin_class) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("B")
def $anonymous_scope_phase(S,5) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = 0
  -- if pdefaultnew.CLASS = $ptascii("B")
def $anonymous_scope_phase(S,n) = false -- otherwise
dec $anonymous_scope_seek(pstate,nat,nat) : pstate
def $anonymous_scope_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $anonymous_scope_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $anonymous_scope_phase(S,n_phase)
def $anonymous_scope_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$anonymous_scope_phase(S,n_phase)
def $anonymous_scope_seek(S,n_phase,n) = $anonymous_scope_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$anonymous_scope_phase(S,n_phase) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $anonymous_scope_seek({parent},{phase},4096)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$anonymous_scope_phase({state},{phase})', *valid(state)]


def reject(name, expression, predicate=None):
    state = 'S_bad_' + name
    clauses = [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
               f'~$call_descriptors_valid({state})']
    if predicate:
        clauses.append('~' + predicate.replace('STATE', state))
    return clauses


def owner(initial):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_eval',0)]
    checks += [
        'S_eval.CURRENT = (pcallcontext_bound)',
        'pcallcontext_bound.INSTANCE = (n_bound)',
        'pcallcontext_bound.TARGET = CLOSURE_TARGET n_bound',
        'pcallcontext_bound.LEXICAL_CLASS = (porigin_a)',
        'pcallcontext_bound.CALLED_CLASS = (porigin_b)',
        'pcallcontext_bound.RECEIVER = (n_receiver)',
        'porigin_a =/= porigin_b',
        'S_eval.OBJECTS[n_receiver] = INSTANCE porigin_b',
        '$class_at(S_eval.CLASSES,porigin_a) = (pclassdesc_a)',
        'pclassdesc_a.NAME = $ptascii("A")',
        '$class_at(S_eval.CLASSES,porigin_b) = (pclassdesc_b)',
        'pclassdesc_b.NAME = $ptascii("B")',
        'S_eval.ORIGIN = (porigin_new)',
        'S_eval.TODO = (EVAL (NExprNew (NName (BYTES text_new) metadata_new_name) (SEQUENCE phpType7_new*) metadata_new)) :: ptask_eval_tail*',
        'porigin_new = PORIGIN n_unit pcpath_new',
        'S_eval.CONSTCONTEXT = (pconstantcontext)',
        '$default_parameter_origin(S_eval,pcallcontext_bound.FUNCTION,0) = pconstantcontext.ORIGIN',
        '$function_at(S_eval.CLOSURETEMPLATES,pcallcontext_bound.FUNCTION) = (pfunction_template)',
        '$code_at(S_eval.CODE,n_unit) = (pcode)',
        '$code_name(pcode.NAMES,pcpath_new) = eps',
        'S_eval.CLOSUREBINDINGS = [pclosurebinding]',
        'pclosurebinding.OBJECT = n_bound',
        'pclosurebinding.LEXICAL = (porigin_a)',
        'pclosurebinding.CALLED = (porigin_b)',
        'pclosurebinding.RECEIVER = (n_receiver)',
        '~((HOBJECT pclosurebinding.SOURCE) <- S_eval.ALLOCATIONS)',
        '$anonymous_default_new_object_valid(S_eval,n_bound)',
        '$anonymous_default_new_site(S_eval,porigin_new)',
        '$new_source_name(S_eval,porigin_new) = ($ptascii("A"))',
    ]
    for name, field, value in [
        ('lexical','LEXICAL_CLASS','(porigin_b)'),
        ('called','CALLED_CLASS','(porigin_a)'),
        ('receiver','RECEIVER','eps'),
        ('instance','INSTANCE','(n_receiver)'),
        ('target','TARGET','CLOSURE_TARGET n_receiver'),
        ('function','FUNCTION','pclosurebinding.SITE')]:
        checks += reject(name,'S_eval[.CURRENT = (pcallcontext_bound[.'+field+' = '+value+'])]',
                         '$anonymous_default_new_site(STATE,porigin_new)')
    checks += reject('parameter','S_eval[.CONSTCONTEXT = (pconstantcontext[.ORIGIN = porigin_new])]',
                     '$anonymous_default_new_site(STATE,porigin_new)')
    checks += reject('compiled_line','S_eval[.CONSTCONTEXT = (pconstantcontext[.LINE = $(pconstantcontext.LINE + 1)])]',
                     '$anonymous_default_new_site(STATE,porigin_new)')
    checks += reject('origin','S_eval[.ORIGIN = (pconstantcontext.ORIGIN)]',
                     '$anonymous_default_new_site(STATE,porigin_new)')
    checks += reject('task_source','S_eval[.TODO = (EVAL (NExprNew (NName (BYTES "cGFyZW50") metadata_new_name) (SEQUENCE phpType7_new*) metadata_new)) :: ptask_eval_tail*]',
                     '$anonymous_default_new_task_valid(STATE,NExprNew (NName (BYTES "cGFyZW50") metadata_new_name) (SEQUENCE phpType7_new*) metadata_new)')
    checks += ['$anonymous_default_new_site(S_bad_task_source,porigin_new)']
    checks += reject('template','S_eval[.CLOSURETEMPLATES = [pfunction_template[.ORIGIN = pclosurebinding.SITE]]]',
                     '$anonymous_default_new_site(STATE,porigin_new)')
    checks += reject('missing_binding','S_eval[.CLOSUREBINDINGS = eps]',
                     '$anonymous_default_new_object_valid(STATE,n_bound)')
    checks += reject('binding_source','S_eval[.CLOSUREBINDINGS = [pclosurebinding[.SOURCE = n_bound]]]',
                     '$anonymous_default_new_object_valid(STATE,n_bound)')
    checks += reject('binding_lexical','S_eval[.CLOSUREBINDINGS = [pclosurebinding[.LEXICAL = (pconstantcontext.ORIGIN)]]]',
                     '$anonymous_default_new_object_valid(STATE,n_bound)')
    checks += [
        *seek('S_eval','S_allocated',1),
        'S_allocated.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_new_tail*',
        'pdefaultnew.SITE = porigin_new',
        'pdefaultnew.LINE = pconstantcontext.LINE',
        'S_allocated.OBJECTS[pdefaultnew.OBJECT] = INSTANCE porigin_a',
        '$default_new_valid(S_allocated,pdefaultnew)',
        *seek('S_allocated','S_handler',2),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'pcallcontext_handler.LEXICAL_CLASS = eps',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.CONTEXT = (pcallcontext_bound)',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler_tail*',
        'S_emitter = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
        'S_default = S_emitter[.ORIGIN = (porigin_new)]',
        '$anonymous_default_new_site(S_default,porigin_new)',
        '$default_new_valid(S_default,pdefaultnew)',
        '$new_source_name(S_default,porigin_new) = ($ptascii("A"))',
        'S_global = $global_table_view(S_handler)',
        '$lookup(S_global.ENV,$ptascii("bound")) = eps',
        '$(0 < $heap_owners($heap_graph(S_handler),HOBJECT n_bound))',
        '(HOBJECT n_receiver) <- S_handler.ALLOCATIONS',
        '$anonymous_scope_output(S_handler.EVENTS) = $ptascii("H|")',
    ]
    checks += reject('saved_lexical','S_handler[.FRAMES = pframe_handler[.CONTEXT = (pcallcontext_bound[.LEXICAL_CLASS = (porigin_b)])] :: pframe_handler_tail*]')
    checks += [
        *seek('S_handler','S_ctor',3),
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'S_ctor.FRAMES = pframe_ctor :: pframe_ctor_tail*',
        'pframe_ctor.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_ctor_tail*',
        'pdefaultctor.NEW.SITE = porigin_new',
        'pdefaultctor.NEW.OBJECT = pdefaultnew.OBJECT',
        'pdefaultctor.NEW.VALUES = [PINT 2048]',
        '$default_ctor_context_valid(S_ctor,pcallcontext_ctor)',
        'S_ctor_owner = $constant_frame_scope(S_ctor,pframe_ctor,pframe_ctor_tail*)',
        'S_ctor_owner.CURRENT = (pcallcontext_bound)',
        '$anonymous_default_new_site(S_ctor_owner,porigin_new)',
        '$default_ctor_valid(S_ctor_owner,pdefaultctor)',
        '$new_source_name(S_ctor_owner,porigin_new) = ($ptascii("A"))',
        '~$anonymous_default_new_site(S_ctor,porigin_new)',
    ]
    checks += reject('ctor_scope','S_ctor[.FRAMES = pframe_ctor[.CONTEXT = (pcallcontext_bound[.LEXICAL_CLASS = (porigin_b)])] :: pframe_ctor_tail*]',
                     '$default_ctor_context_valid(STATE,pcallcontext_ctor)')
    checks += reject('ctor_class','S_ctor[.FRAMES = pframe_ctor[.TODO = (DEFAULT_CTOR_RESULT pdefaultctor[.NEW = pdefaultctor.NEW[.CLASS = $ptascii("B")]]) :: ptask_ctor_tail*] :: pframe_ctor_tail*]',
                     '$default_ctor_context_valid(STATE,pcallcontext_ctor)')
    checks += reject('ctor_owner','S_ctor[.FRAMES = pframe_ctor[.TODO = ptask_ctor_tail*] :: pframe_ctor_tail*]',
                     '$default_ctor_context_valid(STATE,pcallcontext_ctor)')
    checks += [
        '$heap_owners($heap_graph(S_ctor),HOBJECT pdefaultnew.OBJECT) = $($heap_owners($heap_graph(S_bad_ctor_owner),HOBJECT pdefaultnew.OBJECT) + 1)',
        'S_done = $drive_steps(S_ctor,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$anonymous_scope_output(S_done.EVENTS) = $ptascii("H|C2048|T|B/a")',
        '~((HOBJECT n_bound) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pdefaultnew.OBJECT) <- S_done.ALLOCATIONS)',
        r'S_done.CONSTCONTEXT = eps /\ S_done.PARAMETERBACKINGS = eps /\ S_done.CLOSUREBINDINGS = eps',
        *valid('S_done')]
    return checks


def recursive(initial):
    return [
        'S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial','S_outer',0),
        'S_outer.CURRENT = (pcallcontext_outer)',
        'pcallcontext_outer.INSTANCE = (n_outer)',
        'pcallcontext_outer.TARGET = CLOSURE_TARGET n_outer',
        'pcallcontext_outer.LEXICAL_CLASS = (porigin_a)',
        'pcallcontext_outer.CALLED_CLASS = (porigin_a)',
        'pcallcontext_outer.RECEIVER = eps',
        'S_outer.ORIGIN = (porigin_new)',
        '$new_source_name(S_outer,porigin_new) = ($ptascii("A"))',
        '$closure_binding_at(S_outer.CLOSUREBINDINGS,n_outer) = (pclosurebinding_outer)',
        '~((HOBJECT pclosurebinding_outer.SOURCE) <- S_outer.ALLOCATIONS)',
        *seek('S_outer','S_ctor',3),
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'S_ctor.FRAMES = pframe_outer :: pframe_outer_tail*',
        'pframe_outer.TODO = (DEFAULT_CTOR_RESULT pdefaultctor_outer) :: ptask_outer_tail*',
        'pdefaultctor_outer.NEW.CLASS = $ptascii("A")',
        'pdefaultctor_outer.NEW.SITE = porigin_new',
        '$default_ctor_context_valid(S_ctor,pcallcontext_ctor)',
        *seek('S_ctor','S_inner',4),
        'S_inner.CURRENT = (pcallcontext_inner)',
        'pcallcontext_inner.INSTANCE = (n_inner)',
        'n_inner =/= n_outer',
        'pcallcontext_inner.TARGET = CLOSURE_TARGET n_inner',
        'pcallcontext_inner.FUNCTION = pcallcontext_outer.FUNCTION',
        'pcallcontext_inner.LEXICAL_CLASS = (porigin_b)',
        'porigin_a =/= porigin_b',
        'pcallcontext_inner.CALLED_CLASS = (porigin_b)',
        'pcallcontext_inner.RECEIVER = eps',
        'S_inner.ORIGIN = (porigin_new)',
        '$anonymous_default_new_site(S_inner,porigin_new)',
        '$new_source_name(S_inner,porigin_new) = ($ptascii("B"))',
        '$closure_binding_at(S_inner.CLOSUREBINDINGS,n_inner) = (pclosurebinding_inner)',
        'pclosurebinding_inner.SOURCE = pclosurebinding_outer.SOURCE',
        'S_inner.FRAMES = pframe_actor :: pframe_outer :: pframe_outer_tail*',
        'pframe_actor.CONTEXT = (pcallcontext_ctor)',
        'S_saved = $constant_frame_scope(S_inner,pframe_outer,pframe_outer_tail*)',
        'S_saved.CURRENT = (pcallcontext_outer)',
        '$anonymous_default_new_site(S_saved,porigin_new)',
        '$new_source_name(S_saved,porigin_new) = ($ptascii("A"))',
        '$default_ctor_valid(S_saved,pdefaultctor_outer)',
        'S_actor = $constant_frame_scope(S_inner,pframe_actor,pframe_outer :: pframe_outer_tail*)',
        '$default_ctor_context_valid(S_actor,pcallcontext_ctor)',
        *reject('recursive_instance','S_inner[.CURRENT = (pcallcontext_inner[.INSTANCE = (n_outer)])]',
                '$anonymous_default_new_site(STATE,porigin_new)'),
        *reject('recursive_lexical','S_inner[.CURRENT = (pcallcontext_inner[.LEXICAL_CLASS = (porigin_a)])]',
                '$anonymous_default_new_site(STATE,porigin_new)'),
        'pframe_swapped = pframe_outer[.CONTEXT = (pcallcontext_inner)]',
        *reject('recursive_owner','S_inner[.FRAMES = pframe_actor :: pframe_swapped :: pframe_outer_tail*]'),
        'S_actor_swapped = $constant_frame_scope(S_bad_recursive_owner,pframe_actor,pframe_swapped :: pframe_outer_tail*)',
        '~$default_ctor_context_valid(S_actor_swapped,pcallcontext_ctor)',
        *seek('S_inner','S_inner_allocated',5),
        'S_inner_allocated.TODO = (DEFAULT_NEW_ARGS pdefaultnew_inner) :: ptask_inner_tail*',
        'pdefaultnew_inner.CLASS = $ptascii("B")',
        'pdefaultnew_inner.SITE = porigin_new',
        'pdefaultnew_inner.OBJECT =/= pdefaultctor_outer.NEW.OBJECT',
        'S_inner_allocated.OBJECTS[pdefaultnew_inner.OBJECT] = INSTANCE porigin_b',
        '$default_new_valid(S_inner_allocated,pdefaultnew_inner)',
        'S_done = $drive_steps(S_inner_allocated,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$anonymous_scope_output(S_done.EVENTS) = $ptascii("B|TB|Fb|A|TA|Fa|")',
        '~((HOBJECT pdefaultnew_inner.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pdefaultctor_outer.NEW.OBJECT) <- S_done.ALLOCATIONS)',
        '(HOBJECT n_inner) <- S_done.ALLOCATIONS',
        '(HOBJECT n_outer) <- S_done.ALLOCATIONS',
        '~((HOBJECT pclosurebinding_outer.SOURCE) <- S_done.ALLOCATIONS)',
        r'S_done.CONSTCONTEXT = eps /\ S_done.PARAMETERBACKINGS = eps',
        *valid('S_done')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['owner','recursive'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    name = {'owner':'anonymous-default-callback-owner-retirement', 'recursive':'anonymous-default-recursive-template-scopes'}[args.group]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='anonymous-default-scope-' + args.group + '-', dir=OWN))
    source = out / 'source.php'; source.write_bytes(CASES[name])
    source_before = sha(source)
    report = {'passed':False, 'head':before['identity']['head'], 'before':before,
              'source':str(source), 'source_sha256':source_before, 'profile':cross.invoke.types.PROFILE,
              'mode':'unused' if args.elaborate_only else 'source-reached', 'group':args.group}
    print(out, flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,
            '-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        clauses = ['program_source = ' + checked['fixture'], *(owner(initial) if args.group == 'owner' else recursive(initial))]
        (out / 'assertions.json').write_text(json.dumps(clauses,indent=2) + '\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + c + '\n' for c in clauses) + '\ndec $main() : bool\ndef $main() = ' + ('true' if args.elaborate_only else '$body()') + '\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),*[str(ROOT / p) for p in modules],str(fixture)],out / 'numeric',120,ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True,assertions=len(clauses),fixture_sha256=sha(fixture),state_assertions_evaluated=0 if args.elaborate_only else len(clauses),unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        if adapter:adapter.close()
        if frontend:frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['source_unchanged'] = source_before == sha(source)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
        print(out / 'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
