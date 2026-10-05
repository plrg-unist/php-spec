#!/usr/bin/env python3
"""Source-reached autoload cache, cursor and callback controls."""
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
import autoload_sources as sources
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $review_autoload_output(pevent*) : ptbytes
dec $review_autoload_is_output(pevent) : bool
def $review_autoload_is_output(OUTPUT ptbytes) = true
def $review_autoload_is_output(pevent) = false -- otherwise
def $review_autoload_output(eps) = eps
def $review_autoload_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_autoload_output(pevent*)
def $review_autoload_output(pevent :: pevent_tail*) = $review_autoload_output(pevent_tail*)
  -- if ~$review_autoload_is_output(pevent)
dec $review_autoload_phase(pstate,nat) : bool
def $review_autoload_phase(S,0) = true
  -- if S.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("PrivateTarget")
  -- if pautoloadentry.TARGET = AUTO_TARGET (CLOSURE_TARGET n)
def $review_autoload_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("PrivateTarget")
def $review_autoload_phase(S,2) = true
  -- if S.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("CompactedTarget")
  -- if pautoloadcall.INDEX = 2
  -- if $review_autoload_output(S.EVENTS) = $ptascii("A|B|C|")
def $review_autoload_phase(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("RecursiveTarget")
def $review_autoload_phase(S,4) = true
  -- if S.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall
  -- if pautoloadcall.NAME = $ptascii("ExplicitTarget")
def $review_autoload_phase(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("TraceTarget")
def $review_autoload_phase(S,6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("TraceExplicit")
def $review_autoload_phase(S,7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry (REFERENCE n)) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("ReferenceTarget")
  -- if S.STORE[n] = DEFINED (PSTRING $ptascii("ChangedTarget"))
def $review_autoload_phase(S,8) = true
  -- if S.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("PrivateRetiredTarget")
  -- if pautoloadentry.TARGET = AUTO_TARGET (CLOSURE_TARGET n)
def $review_autoload_phase(S,9) = true
  -- if S.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("PrivateRetiredTarget")
  -- if S.AUTOLOAD.ENTRIES = eps
def $review_autoload_phase(S,n) = false -- otherwise
dec $review_autoload_seek(pstate,nat,nat) : pstate
def $review_autoload_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $review_autoload_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $review_autoload_phase(S,n_phase)
def $review_autoload_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$review_autoload_phase(S,n_phase)
def $review_autoload_seek(S,n_phase,n) = $review_autoload_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$review_autoload_phase(S,n_phase) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $review_autoload_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$review_autoload_phase({state},{phase})', *valid(state)]


def reject(name, expression, predicate):
    state = 'S_bad_' + name
    return [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})', '~' + predicate.replace('STATE', state)]


def completed(state, expected, byte_expr):
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$review_autoload_output(S_done.EVENTS) = ' + byte_expr(expected), *valid('S_done')]


def method(initial, expected, byte_expr):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_enter',0),
        'S_enter.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'pautoloadentry.TARGET = AUTO_TARGET (CLOSURE_TARGET n_loader)',
        'pautoloadentry.SCOPE = (pclosurescope)', 'pautoloadentry.BINDING = eps',
        '$class_named(S_enter.CLASSNAMES,$ptascii("loaderowner")) = (porigin_owner)',
        '$class_named(S_enter.CLASSNAMES,$ptascii("loaderchild")) = (porigin_child)',
        'pclosurescope.OBJECT = n_loader', 'pclosurescope.LEXICAL = porigin_owner',
        'pclosurescope.CALLED = porigin_child', 'pclosurescope.RECEIVER = eps',
        '$autoload_entry_valid(S_enter,pautoloadentry)',
        '$heap_owners($heap_graph(S_enter),HOBJECT n_loader) = 2']
    checks += reject('method_scope',
        'S_enter[.TODO = (AUTO_ENTER pautoloadcall pautoloadentry[.SCOPE = (pclosurescope[.LEXICAL = porigin_child])] poperand) :: ptask_tail*]',
        '$autoload_entry_valid(STATE,pautoloadentry[.SCOPE = (pclosurescope[.LEXICAL = porigin_child])])')
    checks += reject('method_called',
        'S_enter[.TODO = (AUTO_ENTER pautoloadcall pautoloadentry[.SCOPE = (pclosurescope[.CALLED = porigin_owner])] poperand) :: ptask_tail*]',
        '$autoload_entry_valid(STATE,pautoloadentry[.SCOPE = (pclosurescope[.CALLED = porigin_owner])])')
    checks += reject('method_operand',
        'S_enter[.TODO = (AUTO_ENTER pautoloadcall pautoloadentry (KNOWN (PSTRING $ptascii("OtherTarget")))) :: ptask_tail*]',
        '$autoload_sent_valid(STATE,pautoloadcall,pautoloadentry,KNOWN (PSTRING $ptascii("OtherTarget")))')
    checks += [*seek('S_enter','S_body',1), 'S_body.CURRENT = (pcallcontext)',
        '$autoload_context_valid(S_body,pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_loader',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext.CALLED_CLASS = (porigin_child)',
        'pcallcontext.EXTRA = eps', '$heap_owners($heap_graph(S_body),HOBJECT n_loader) = 2']
    checks += reject('method_extra',
        'S_body[.CURRENT = (pcallcontext[.EXTRA = [KNOWN (PSTRING $ptascii("PrivateTarget"))]])]',
        '$autoload_context_valid(STATE,pcallcontext[.EXTRA = [KNOWN (PSTRING $ptascii("PrivateTarget"))]])')
    checks += [*completed('S_body',expected,byte_expr),
        '(HOBJECT n_loader) <- S_done.ALLOCATIONS', '$heap_owners($heap_graph(S_done),HOBJECT n_loader) = 1']
    return checks


def compaction(initial, expected, byte_expr):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_cursor',2),
        'S_cursor.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'S_cursor.AUTOLOAD.CAPACITY = 8', '|S_cursor.AUTOLOAD.ENTRIES| = 7',
        *['S_cursor.AUTOLOAD.ENTRIES[' + str(index) + '] = (pautoloadentry_' + name + ')'
          for index, name in enumerate('cdefghi')],
        'pautoloadentry = pautoloadentry_c',
        '$autoload_raw(pautoloadentry_f) = PSTRING $ptascii("load_f")',
        '$autoload_raw(pautoloadentry_i) = PSTRING $ptascii("load_i")']
    checks += reject('capacity', 'S_cursor[.AUTOLOAD.CAPACITY = 7]', '$autoload_registry_valid(STATE)')
    checks += ['S_next_found = $drive_steps(S_cursor,1)', 'S_next_found.COMPLETION = BUDGET',
        'S_next = S_next_found[.COMPLETION = NORMAL]',
        'S_next.TODO = (AUTO_NEXT pautoloadcall[.INDEX = 3]) :: ptask_tail*', *valid('S_next'),
        'S_f_found = $drive_steps(S_next,1)', 'S_f_found.COMPLETION = BUDGET',
        'S_f = S_f_found[.COMPLETION = NORMAL]',
        'S_f.TODO = (AUTO_ENTER pautoloadcall[.INDEX = 3] pautoloadentry_f poperand) :: ptask_tail*',
        *valid('S_f'), *completed('S_f',expected,byte_expr)]
    return checks



def compaction_cursor(initial, expected, byte_expr):
    return compaction(initial, expected, byte_expr)[:25]


def compaction_finish(initial, expected, byte_expr):
    checks = compaction(initial, expected, byte_expr)
    dependencies = [checks[index] for index in [0, 2, 3, 4, 5, 8, 14]]
    return dependencies + checks[25:]


def recursion(initial, expected, byte_expr):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_body',3),
        'S_body.CURRENT = (pcallcontext)', 'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.KEY = $ptascii("recursivetarget")',
        '~$autoload_pending(S_body,$ptascii("recursivetarget"))',
        '$autoload_pending(S_body,$ptascii("UnrelatedTarget"))',
        '$autoload_context_valid(S_body,pcallcontext)']
    pcall_wrong = 'pautoloadcall[.KEY = $ptascii("RecursiveTarget")]'
    pframe_wrong = 'pframe[.TODO = (AUTO_RESULT ' + pcall_wrong + ' pautoloadentry poperand) :: ptask_tail*]'
    checks += reject('key', 'S_body[.FRAMES = ' + pframe_wrong + ' :: pframe_tail*]',
                     '$autoload_context_valid(STATE,pcallcontext)')
    checks += completed('S_body',expected,byte_expr)
    return checks


def explicit(initial, expected, byte_expr):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_enter',4),
        'S_enter.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("ExplicitTarget")))]',
        '$review_autoload_output(S_enter.EVENTS) = $ptascii("T|")',
        '$autoload_explicit_name(S_enter,pconfigcall) = ($ptascii("ExplicitTarget"))',
        '$autoload_resume_valid(S_enter,pautoloadcall)']
    wrong = 'pautoloadcall[.NAME = $ptascii("OtherTarget")][.KEY = $ptascii("othertarget")]'
    checks += reject('explicit_name', 'S_enter[.TODO = (AUTO_ENTER ' + wrong + ' pautoloadentry (KNOWN (PSTRING $ptascii("OtherTarget")))) :: ptask_tail*]',
                     '$autoload_resume_valid(STATE,' + wrong + ')')
    checks += completed('S_enter',expected,byte_expr)
    return checks


def traces(initial, expected, byte_expr):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_lookup',5),
        'S_lookup.CURRENT = (pcallcontext_lookup)', 'S_lookup.FRAMES = pframe_lookup :: pframe_lookup_tail*',
        'pframe_lookup.TODO = (AUTO_RESULT pautoloadcall_lookup pautoloadentry_lookup poperand_lookup) :: ptask_lookup_tail*',
        'pautoloadcall_lookup.MODE = AUTO_LOOKUP', 'pcallcontext_lookup.CALLSITE = (pautoloadcall_lookup.SITE)',
        'pcallcontext_lookup.LINE = 4', '$autoload_context_valid(S_lookup,pcallcontext_lookup)',
        *seek('S_lookup','S_explicit',6), 'S_explicit.CURRENT = (pcallcontext_explicit)',
        'S_explicit.FRAMES = pframe_explicit :: pframe_explicit_tail*',
        'pframe_explicit.TODO = (AUTO_RESULT pautoloadcall_explicit pautoloadentry_explicit poperand_explicit) :: ptask_explicit_tail*',
        'pautoloadcall_explicit.MODE = AUTO_EXPLICIT pconfigcall',
        'pcallcontext_explicit.TARGET = pcallcontext_lookup.TARGET',
        'pcallcontext_explicit.CALLSITE = eps', 'pcallcontext_explicit.LINE = $(-1)',
        '$autoload_context_valid(S_explicit,pcallcontext_explicit)']
    checks += reject('explicit_trace_line',
        'S_explicit[.CURRENT = (pcallcontext_explicit[.LINE = 4])]',
        '$autoload_context_valid(STATE,pcallcontext_explicit[.LINE = 4])')
    checks += completed('S_explicit',expected,byte_expr)
    return checks


def reference(initial, expected, byte_expr):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_written',7),
        'S_written.CURRENT = (pcallcontext)', 'S_written.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry (REFERENCE n_argument)) :: ptask_tail*',
        'n_argument <- S_written.REFCELLS', '(HCELL n_argument) <- S_written.ALLOCATIONS',
        'S_written.STORE[n_argument] = DEFINED (PSTRING $ptascii("ChangedTarget"))',
        'pautoloadcall.NAME = $ptascii("ReferenceTarget")',
        '$autoload_context_valid(S_written,pcallcontext)',
        *completed('S_written',expected,byte_expr),
        '~((HCELL n_argument) <- S_done.ALLOCATIONS)']


def retirement(initial, expected, byte_expr):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_enter',8),
        'S_enter.TODO = (AUTO_ENTER pautoloadcall pautoloadentry poperand) :: ptask_tail*',
        'pautoloadentry.TARGET = AUTO_TARGET (CLOSURE_TARGET n_loader)',
        'pautoloadentry.SCOPE = (pclosurescope)', '$autoload_entry_valid(S_enter,pautoloadentry)',
        *seek('S_enter','S_returned',9),
        'S_returned.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_returned_tail*',
        'S_returned.AUTOLOAD.CAPACITY = 8', '$autoload_registry_valid(S_returned)',
        '~((HOBJECT n_loader) <- S_returned.ALLOCATIONS)',
        '$closure_scope_at(S_returned.CLOSURESCOPES,n_loader) = eps',
        '$autoload_entry_valid(S_returned,pautoloadentry)',
        '~$autoload_entry_live(S_returned,pautoloadentry)',
        '$call_task_valid(S_returned,AUTO_RESULT pautoloadcall pautoloadentry poperand)',
        *completed('S_returned',expected,byte_expr),
        '~((HOBJECT n_loader) <- S_done.ALLOCATIONS)',
        'n_declaration = $nabs($(|S_done.DECLARATIONS| - 1))',
        'S_done.DECLARATIONS[n_declaration] = PDRCLASS porigin_published pdeclcause',
        '$class_named(S_done.CLASSNAMES,$ptascii("privateretiredtarget")) = (porigin_published)',
        'pdeclcause.AUTOLOAD = [(1,pautoloadcall,pautoloadentry)]',
        '$declaration_history_valid(S_done)',
        'pdeclcause.CALLS[1] = (porigin_loader,porigin_site?,porigin_lexical?,porigin_called?)',
        'n_call_tail = $nabs($(|pdeclcause.CALLS| - 2))',
        '$class_named(S_done.CLASSNAMES,$ptascii("retiredowner")) = (porigin_owner)']
    for name, cause in [
        ('cause_missing', 'pdeclcause[.AUTOLOAD = eps]'),
        ('cause_index', 'pdeclcause[.AUTOLOAD = [(0,pautoloadcall,pautoloadentry)]]'),
        ('cause_line', 'pdeclcause[.AUTOLOAD = [(1,pautoloadcall[.LINE = $(pautoloadcall.LINE + 1)],pautoloadentry)]]'),
        ('cause_called', 'pdeclcause[.CALLS = pdeclcause.CALLS[0:1] ++ [(porigin_loader,porigin_site?,porigin_lexical?,porigin_called_wrong?)] ++ pdeclcause.CALLS[2:n_call_tail]]'),
    ]:
        if name == 'cause_called':
            checks += ['porigin_called_wrong? = (porigin_owner)']
        checks += reject(name,
            'S_done[.DECLARATIONS = S_done.DECLARATIONS[0:n_declaration] ++ [PDRCLASS porigin_published ' + cause + ']]',
            '$declaration_history_valid(STATE)')
    return checks

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['method', 'compaction', 'compaction_cursor', 'compaction_finish', 'recursion', 'explicit', 'traces', 'reference', 'retirement'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    case_group = 'compaction' if args.group in ['compaction_cursor','compaction_finish'] else args.group
    name = {'method': 'autoload-captured-private-method-core', 'compaction': 'autoload-live-compaction-cursor', 'recursion': 'autoload-same-name-recursion', 'explicit': 'autoload-explicit-user-stringable', 'traces': 'autoload-lookup-explicit-trace-lines', 'reference': 'autoload-required-reference-loader', 'retirement': 'autoload-private-fcc-retirement'}[case_group]
    expected = sources.EXPECTED[name]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='autoload-protocol-' + args.group + '-', dir=OWN))
    source = out / 'source.php'
    source.write_bytes(sources.CASES[name])
    source_before = sha(source)
    runner_flags = ['--sl'] if args.group in ['compaction_cursor', 'compaction_finish'] else []
    report = {'passed':False,'before':before,'source':str(source),'source_sha256':source_before,
              'profile':cross.invoke.types.PROFILE,'mode':'unused' if args.elaborate_only else 'source-reached','group':args.group,
              'runner_mode':'SL' if runner_flags else 'AL'}
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
        body = globals()[args.group](initial,expected,cross.invoke.byte_expr)
        clauses += body
        (out / 'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+c+'\n' for c in clauses)+'\ndec $main() : bool\ndef $main() = '+('true' if args.elaborate_only else '$body()')+'\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),*runner_flags,*[str(ROOT / p) for p in modules],str(fixture)],out / 'numeric',120,ROOT)
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
