#!/usr/bin/env python3
"""Source-reached parameter-default lookup, caller and ownership controls."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from default_new_autoload_sources import CASES, EXPECTED

PREFIX = r'''
dec $review_default_is_output(pevent) : bool
dec $review_default_output(pevent*) : ptbytes
def $review_default_output(eps) = eps
def $review_default_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_default_output(pevent*)
def $review_default_output(pevent :: pevent_tail*) = $review_default_output(pevent_tail*)
  -- if ~$review_default_is_output(pevent)
def $review_default_is_output(OUTPUT ptbytes) = true
def $review_default_is_output(pevent) = false -- otherwise
dec $review_default_phase(pstate,nat) : bool
def $review_default_phase(S,0) = true
  -- if S.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("DefaultAutoloadTarget")
def $review_default_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("DefaultAutoloadTarget")
def $review_default_phase(S,2) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.CLASS = $ptascii("DefaultAutoloadTarget") /\ pdefaultnew.INDEX = 0
def $review_default_phase(S,3) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.CLASS = $ptascii("DefaultAutoloadTarget") /\ pdefaultnew.INDEX = 1
def $review_default_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at(S.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = $ptascii("nested_recursive_default")
  -- if S.TODO = (EVAL (NExprNew name (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $new_source_name(S, porigin) = ($ptascii("RecursiveDefaultTarget"))
def $review_default_phase(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("RetirementDefaultTarget")
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("receive")) = eps
  -- if $lookup(S_global.ENV, $ptascii("factory")) = eps
def $review_default_phase(S,n) = false -- otherwise
dec $review_default_terminal(pstate) : bool
def $review_default_terminal(S) = (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $review_default_seek(pstate,nat,nat) : pstate
def $review_default_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $review_default_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $review_default_phase(S,n_phase)
def $review_default_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$review_default_phase(S,n_phase)
  -- if n = 0 \/ $review_default_terminal(S)
def $review_default_seek(S,n_phase,n) = $review_default_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$review_default_phase(S,n_phase) /\ ~$review_default_terminal(S) /\ $(n > 0)
dec $review_default_outer_kind(pframe) : bool
def $review_default_outer_kind(pframe) = true
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("RecursiveDefaultTarget")
def $review_default_outer_kind(pframe) = false -- otherwise
dec $review_default_outer(pframe*) : (pframe,pframe*)?
def $review_default_outer(pframe :: pframe_tail*) = ((pframe,pframe_tail*)) -- if $review_default_outer_kind(pframe)
def $review_default_outer(pframe :: pframe_tail*) = $review_default_outer(pframe_tail*) -- if ~$review_default_outer_kind(pframe)
def $review_default_outer(eps) = eps
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $review_default_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$review_default_phase({state},{phase})', *valid(state)]


def reject(name, expression, predicate):
    state = 'S_bad_' + name
    return [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})', '~' + predicate.replace('STATE', state)]


def completed(state, expected):
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$review_default_output(S_done.EVENTS) = ' + cross.invoke.byte_expr(expected), *valid('S_done')]


def lookup(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_enter',0),
        'S_enter.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'pautoloadcall.RESUME = AUTO_DEFAULT_NEW ptbytes phpType7* porigin_parameter z',
        'S_enter.CONSTCONTEXT = (pconstantcontext)', 'pconstantcontext.ORIGIN = porigin_parameter',
        '$autoload_default_ready(S_enter,ptbytes,phpType7*,porigin_parameter,z)',
        '$task_nodes(pautoloadcall.RESUME) = eps',
        '$class_named(S_enter.CLASSNAMES,$ptascii("defaultargumentmarker")) = (porigin_marker)',
        '~((INSTANCE porigin_marker) <- S_enter.OBJECTS)',
        '~$autoload_ordinary_new_source(S_enter,pautoloadcall.SITE)']
    for name, resume, line in [
        ('parameter', 'AUTO_DEFAULT_NEW ptbytes phpType7* porigin_marker z', 'z'),
        ('arguments', 'AUTO_DEFAULT_NEW ptbytes eps porigin_parameter z', 'z'),
        ('line', 'AUTO_DEFAULT_NEW ptbytes phpType7* porigin_parameter $(z + 1)', '$(z + 1)'),
        ('tag', 'AUTO_NEW ptbytes phpType7* z z', 'z'),
    ]:
        wrong = 'pautoloadcall[.RESUME = ' + resume + '][.LINE = ' + line + ']'
        checks += reject(name, 'S_enter[.TODO = (AUTO_ENTER ' + wrong + ' pautoloadentry poperand) :: ptask_tail*]',
                         '$autoload_resume_valid(STATE,' + wrong + ')')
    checks += [*seek('S_enter','S_body',1), 'S_body.CURRENT = (pcallcontext)',
        'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_body_tail*',
        'S_owner = $constant_frame_scope(S_body,pframe,pframe_tail*)',
        '$autoload_resume_valid(S_owner,pautoloadcall)',
        '$autoload_context_valid(S_body,pcallcontext)',
        *seek('S_body','S_allocated',2),
        'S_allocated.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_allocated_tail*',
        'pdefaultnew.VALUES = eps', '$default_new_valid(S_allocated,pdefaultnew)',
        '$heap_owners($heap_graph(S_allocated),HOBJECT pdefaultnew.OBJECT) = 1',
        '~((INSTANCE porigin_marker) <- S_allocated.OBJECTS)',
        *seek('S_allocated','S_values',3),
        'S_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values) :: ptask_values_tail*',
        'pdefaultnew_values.OBJECT = pdefaultnew.OBJECT',
        'pdefaultnew_values.VALUES = [POBJECT n_argument]',
        'S_values.OBJECTS[n_argument] = INSTANCE porigin_marker',
        '$heap_owners($heap_graph(S_values),HOBJECT n_argument) = 1',
        *completed('S_values',expected),
        '~((HOBJECT pdefaultnew.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_argument) <- S_done.ALLOCATIONS)',
        'n_declaration = $nabs($(|S_done.DECLARATIONS| - 1))',
        'S_done.DECLARATIONS[n_declaration] = PDRCLASS porigin_published pdeclcause',
        'pdeclcause.AUTOLOAD = [(1,pautoloadcall,pautoloadentry)]',
        '$autoload_declaration_resume(S_done,pautoloadcall)', '$declaration_history_valid(S_done)',
        '|pdeclcause.CALLS| = 3',
        'pdeclcause.CALLS[2] = (porigin_receive,porigin_receive_site?,porigin_receive_lexical?,porigin_receive_called?)',
        '$function_at(S_done.FUNCTIONS,porigin_receive) = (pfunction_receive)',
        'pfunction_receive.NAME = $ptascii("receive_default")',
        '$declaration_cause_owner(S_done,pautoloadcall.SITE) = (pfunction_receive)',
        'pdeclcause.CALLS[0] = (porigin_publisher,porigin_publisher_site?,porigin_publisher_lexical?,porigin_publisher_called?)']
    wrong = 'pautoloadcall[.RESUME = AUTO_NEW ptbytes phpType7* z z]'
    checks += reject('history_tag',
        'S_done[.DECLARATIONS = S_done.DECLARATIONS[0:n_declaration] ++ [PDRCLASS porigin_published pdeclcause[.AUTOLOAD = [(1,' + wrong + ',pautoloadentry)]]]]',
        '$declaration_history_valid(STATE)')
    checks += reject('history_receiver',
        'S_done[.DECLARATIONS = S_done.DECLARATIONS[0:n_declaration] ++ [PDRCLASS porigin_published pdeclcause[.CALLS = pdeclcause.CALLS[0:2] ++ [(porigin_publisher,porigin_receive_site?,porigin_receive_lexical?,porigin_receive_called?)]]]]',
        '$declaration_history_valid(STATE)')
    return checks


def recursive(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_inner',4),
        'S_inner.CURRENT = (pcallcontext_inner)', 'S_inner.CONSTCONTEXT = (pconstantcontext_inner)',
        'S_inner.ORIGIN = (porigin_inner)',
        'S_inner.TODO = (EVAL (NExprNew name (SEQUENCE phpType7*) metadata)) :: ptask_inner_tail*',
        'phpType7* = eps',
        '$review_default_outer(S_inner.FRAMES) = ((pframe_outer,pframe_outer_tail*))',
        'pframe_outer.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_outer_tail*',
        'pautoloadcall.RESUME = AUTO_DEFAULT_NEW ptbytes phpType7_outer* porigin_parameter_outer z_outer',
        'ptbytes = $ptascii("RecursiveDefaultTarget")',
        'S_outer = $constant_frame_scope(S_inner,pframe_outer,pframe_outer_tail*)',
        'S_outer.CURRENT = (pcallcontext_outer)',
        'pcallcontext_inner.FUNCTION =/= pcallcontext_outer.FUNCTION',
        'pconstantcontext_inner.ORIGIN =/= porigin_parameter_outer',
        '$autoload_resume_valid(S_outer,pautoloadcall)',
        '$autoload_default_ready(S_inner,ptbytes,eps,pconstantcontext_inner.ORIGIN,pconstantcontext_inner.LINE)',
        '~$autoload_pending(S_inner,ptbytes)',
        '$autoload_pending(S_inner,$ptascii("UnrelatedDefaultTarget"))',
        '~$autoload_default_ready(S_inner,ptbytes,eps,porigin_parameter_outer,pconstantcontext_inner.LINE)',
        '$task_nodes(AUTO_DEFAULT_NEW ptbytes eps pconstantcontext_inner.ORIGIN pconstantcontext_inner.LINE) = eps']
    wrong = 'AUTO_DEFAULT_NEW ptbytes eps porigin_parameter_outer pconstantcontext_inner.LINE'
    checks += reject('recursive_parameter',
        'S_inner[.TODO = (' + wrong + ') :: ptask_inner_tail*]', '$call_task_valid(STATE,' + wrong + ')')
    checks += completed('S_inner',expected)
    return checks


def retirement(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_body',5),
        'S_body.CURRENT = (pcallcontext_loader)', 'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'pautoloadcall.RESUME = AUTO_DEFAULT_NEW ptbytes phpType7* porigin_parameter z',
        'S_owner = $constant_frame_scope(S_body,pframe,pframe_tail*)',
        'S_owner.CURRENT = (pcallcontext_receive)',
        'pcallcontext_receive.TARGET = CLOSURE_TARGET n_receive',
        'pcallcontext_receive.INSTANCE = (n_receive)', 'pcallcontext_receive.RECEIVER = (n_receiver)',
        '(HOBJECT n_receive) <- S_body.ALLOCATIONS', '(HOBJECT n_receiver) <- S_body.ALLOCATIONS',
        '$class_named(S_body.CLASSNAMES,$ptascii("defaultautoloadowner")) = (porigin_owner)',
        '$class_named(S_body.CLASSNAMES,$ptascii("defaultautoloadchild")) = (porigin_child)',
        'pcallcontext_receive.LEXICAL_CLASS = (porigin_owner)',
        'pcallcontext_receive.CALLED_CLASS = (porigin_child)',
        '$autoload_default_ready(S_owner,ptbytes,phpType7*,porigin_parameter,z)',
        '$autoload_context_valid(S_body,pcallcontext_loader)',
        '$closure_scope_at(S_body.CLOSURESCOPES,n_receive) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_owner', 'pclosurescope.CALLED = porigin_child']
    wrong = 'pautoloadcall[.RESUME = AUTO_NEW ptbytes phpType7* z z]'
    checks += reject('retired_tag',
        'S_body[.FRAMES = pframe[.TODO = (AUTO_RESULT ' + wrong + ' pautoloadentry poperand) :: ptask_tail*] :: pframe_tail*]',
        '$autoload_context_valid(STATE,pcallcontext_loader)')
    checks += [*completed('S_body',expected), '~((HOBJECT n_receive) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$closure_scope_at(S_done.CLOSURESCOPES,n_receive) = eps',
        '$lookup(S_done.ENV,$ptascii("receive")) = eps',
        '$lookup(S_done.ENV,$ptascii("factory")) = eps']
    return checks


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['lookup','recursive','retirement'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    case_name = {'lookup':'default-autoload-before-nested-argument',
                 'recursive':'default-autoload-same-key-recursion',
                 'retirement':'default-autoload-receiving-closure-core'}[args.group]
    original = CASES[case_name]
    expected = EXPECTED[case_name]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='default-autoload-protocol-' + args.group + '-', dir=ROOT / '.tools'))
    source = out/'source.php'; source.write_bytes(original)
    source_before = sha(source)
    report = {'passed':False,'before':before,'source':str(source),'source_sha256':source_before,
              'profile':cross.invoke.types.PROFILE,'mode':'unused' if args.elaborate_only else 'source-reached',
              'group':args.group,'runner_mode':'AL'}
    print(out,flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,'-d',
            'extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+checked['fixture'],*globals()[args.group](initial,expected)]
        (out/'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+c+'\n' for c in clauses)+'\ndec $main() : bool\ndef $main() = '+('true' if args.elaborate_only else '$body()')+'\n')
        modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
            *[str(ROOT/p) for p in modules],str(fixture)],out/'numeric',120,ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True,assertions=len(clauses),fixture_sha256=sha(fixture),
            state_assertions_evaluated=0 if args.elaborate_only else len(clauses),
            unused_body_assertions=len(clauses) if args.elaborate_only else 0)
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
