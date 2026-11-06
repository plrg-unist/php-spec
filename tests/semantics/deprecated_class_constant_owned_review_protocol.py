#!/usr/bin/env python3
"""Check actual class-constant binders, lookup receipts and publication cuts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_class_constant_owned_review'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTIONS = {'cleanup': 'object-alias-local-cleanup',
    'publication': 'distinct-class-cache-publication',
    'reentry': 'reentry-eval-prefix-snapshot',
    'lookup': 'object-shadow-cache-lookup',
    'heap_snapshot': 'class-owned-owning-child-cache'}

EXTRA = r'''
dec $class_owned_ready(pstate,nat,porigin) : bool
def $class_owned_ready(S,0,porigin) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask*
def $class_owned_ready(S,1,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_local)
  -- if S.OBJECTS[n_local] = INSTANCE porigin_local
  -- if $class_at(S.CLASSES,porigin_local) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Local194")
  -- if $destructor_method(S,n_local) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $class_owned_ready(S,n_mode,porigin) = false -- otherwise
dec $class_owned_pause(pstate,nat,porigin,nat) : pstate
def $class_owned_pause(S,n_mode,porigin,n) = S -- if $class_owned_ready(S,n_mode,porigin)
def $class_owned_pause(S,n_mode,porigin,n) = $class_owned_pause(S_next[.COMPLETION = NORMAL],n_mode,porigin,$nabs($(n - 1)))
  -- if ~$class_owned_ready(S,n_mode,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $class_owned_pause(S,n_mode,porigin,n) = S -- otherwise
dec $class_owned_parent_ready(pstate,pclassconstantcontext) : bool
def $class_owned_parent_ready(S,pclassconstantcontext) = true
  -- if S.TODO = (CLASS_CONST_BIND pclassconstantcontext.DECL) :: ptask*
  -- if S.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*
def $class_owned_parent_ready(S,pclassconstantcontext) = false -- otherwise
dec $class_owned_parent_pause(pstate,pclassconstantcontext,nat) : pstate
def $class_owned_parent_pause(S,pclassconstantcontext,n) = S
  -- if $class_owned_parent_ready(S,pclassconstantcontext)
def $class_owned_parent_pause(S,pclassconstantcontext,n) = $class_owned_parent_pause(S_next[.COMPLETION = NORMAL],pclassconstantcontext,$nabs($(n - 1)))
  -- if ~$class_owned_parent_ready(S,pclassconstantcontext)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $class_owned_parent_pause(S,pclassconstantcontext,n) = S -- otherwise
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.COMPLETION = NORMAL',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'pdeprecatedconstant.COPIED = eps', '$task_nodes(perrorcall.RESUME) = eps',
        'S_warn.CONSTCONTEXT = (pconstantcontext)',
        'S_warn.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.DECL = pconstantcontext.ORIGIN',
        '$class_constant_origin(S_warn.CLASSES,pclassconstantcontext.DECL) = (pclassconstantdesc)',
        '$owned_class_constant_source(S_warn,pclassconstantdesc)',
        '$owned_class_constant_scope(S_warn)',
        '$class_constant_context_valid(S_warn,pconstantcontext)',
        '$deprecated_constant_class_ast(S_warn,pdeprecatedconstant.SITE)',
        '$deprecated_constant_payload_valid(S_warn,pdeprecatedconstant)',
        '$class_constant_pending_cache(S_warn,pclassconstantcontext)',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = eps',
        '$(pclassconstantcontext.HISTORY <= |S_warn.CLASSCONSTANTHISTORY|)',
        '$owned_class_linked_before(S_warn.CLASSCONSTANTHISTORY[0:pclassconstantcontext.HISTORY],pclassconstantdesc.OWNER)',
        '~$owned_class_cache_seen(S_warn.CLASSCONSTANTHISTORY[0:pclassconstantcontext.HISTORY],pclassconstantcontext.DECL)',
        '~$owned_class_constant_scope(S_warn[.CONSTCONTEXT = eps])',
        '~$owned_class_constant_scope(S_warn[.CLASSCONSTANTINIT = eps])',
        '~$class_constant_pending_cache(S_warn,pclassconstantcontext[.HISTORY = 0])',
        '$call_descriptors_valid(S_warn)']


def bind(parent=False):
    pause = '$class_owned_parent_pause(S_warn,pclassconstantcontext,10000)' if parent else '$class_owned_pause(S_warn,0,pclassconstantcontext.DECL,10000)'
    return ['S_bind = ' + pause,
        'S_bind.COMPLETION = NORMAL', '$class_owned_ready(S_bind,0,pclassconstantcontext.DECL)',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'S_bind.CONSTCONTEXT = (pconstantcontext_bind)',
        '$class_constant_context_valid(S_bind,pconstantcontext_bind)',
        '$class_constant_pending_cache(S_bind,pclassconstantcontext)',
        '$call_descriptors_valid(S_bind)']


def published():
    return ['S_after.COMPLETION = BUDGET',
        '$default_cache_at(S_after.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache)',
        '$class_constant_history_valid(S_after)',
        '$class_constant_caches_valid(S_after,S_after.CLASSCONSTANTCACHE)',
        '$call_descriptors_valid(S_after)',
        '$owned_class_last_write(S_after.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL) = (pclassconstantevent)',
        '$constant_callable_cache_event(pclassconstantevent) = ((pclassconstantcontext.DECL,n_prefix))',
        '$constant_callable_cache_prefix(S_after.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL) = (n_prefix)',
        '$constant_callable_cache_valid(S_after,pclassconstantdesc,pdefaultcache.CLASS,n_prefix)']


def cleanup(fixture, path):
    return start(fixture, path) + [
        '$deprecated_constant_value(S_warn,pdeprecatedconstant.SITE) = POBJECT n_donor',
        '(HOBJECT n_donor) <- $user_constant_roots(S_warn.USERCONSTANTS)',
        '$class_constant_roots(S_warn.CLASSCONSTANTCACHE) = eps',
        'S_local = $class_owned_pause(S_warn,1,pclassconstantcontext.DECL,10000)',
        'S_local.COMPLETION = NORMAL', '$class_owned_ready(S_local,1,pclassconstantcontext.DECL)',
        '$lookup($global_table_view(S_local).ENV,$ptascii("alias")) = (n_alias)',
        'S_local.STORE[n_alias] = DEFINED PNULL',
        '(HOBJECT n_donor) <- S_local.ALLOCATIONS',
        '$default_cache_at(S_local.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = eps',
        '$class_constant_state_valid(S_local)',
        '$class_constant_saved_scopes_valid(S_local,S_local.FRAMES)',
        '$constant_context_valid(S_local)', '$gc_state_valid(S_local)',
        '$destruction_state_valid(S_local)', '$call_current_valid(S_local)',
        '$error_handlers_valid(S_local,S_local.ERRORHANDLER :: S_local.ERRORHANDLERS)'] + bind() + [
        'S_bind.RESULT = KNOWN (POBJECT n_donor)',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero.CLASSCONSTANTCACHE = S_bind.CLASSCONSTANTCACHE',
        'S_zero.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        'S_after = $drive_steps(S_zero[.COMPLETION = NORMAL],1)'] + published() + [
        'pdefaultcache.VALUE = POBJECT n_donor',
        '$class_constant_roots(S_after.CLASSCONSTANTCACHE) = [HOBJECT n_donor]',
        '(HOBJECT n_donor) <- $machine_roots(S_after)',
        '$owned_class_write_facts(pclassconstantevent) = (pconstantfact_read*)',
        '$global_constant_read_facts(pconstantfact_read*) =/= eps',
        'S_after.PARAMETERRECEIVES = eps',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
        'S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS',
        'S_done.CLASSCONSTANTCACHE = S_full.CLASSCONSTANTCACHE']


def publication(fixture, path):
    return start(fixture, path) + [
        '$deprecated_constant_value(S_warn,pdeprecatedconstant.SITE) = PARRAY n_array'] + bind() + [
        'S_bind.CLASSCONSTANTCACHE = [pdefaultcache_child]',
        'pdefaultcache_child.ORIGIN =/= pclassconstantcontext.DECL',
        'pdefaultcache_child.VALUE = PINT 9',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = eps',
        '$owned_class_cache_seen(S_bind.CLASSCONSTANTHISTORY,pdefaultcache_child.ORIGIN)',
        '~$owned_class_cache_seen(S_bind.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL)',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        'S_after = $drive_steps(S_bind,1)'] + published() + [
        'pdefaultcache.VALUE = PARRAY n_array',
        '$default_cache_at(S_after.CLASSCONSTANTCACHE,pdefaultcache_child.ORIGIN) = (pdefaultcache_child)',
        '$class_constant_roots(S_after.CLASSCONSTANTCACHE) = [HARRAY n_array]',
        '~$owned_class_extended_history(S_after.CLASSCONSTANTHISTORY)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)']


def reentry(fixture, path, response):
    binder = bind(True)
    binder[0] = 'S_bind = $class_owned_parent_pause(S_entered,pclassconstantcontext,10000)'
    return start(fixture, path) + [
        'S_wait = $drive_steps(S_warn,10000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        '$call_descriptors_valid(S_wait)', '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')', 'S_entered.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_entered)'] + binder + [
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_old)',
        'pdefaultcache_old.VALUE = PINT 9', '$owned_class_snapshot_available(S_bind,pdefaultcache_old)',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        'pclassconstantcontext_late = pclassconstantcontext[.HISTORY = |S_bind.CLASSCONSTANTHISTORY|]',
        '~$class_constant_pending_cache(S_bind,pclassconstantcontext_late)',
        'pclassconstantcontext_bad = pclassconstantcontext[.HISTORY = $(|S_bind.CLASSCONSTANTHISTORY| + 1)]',
        '~$class_constant_pending_cache(S_bind,pclassconstantcontext_bad)',
        'S_bad = S_bind[.CLASSCONSTANTINIT = pclassconstantcontext_late :: pclassconstantcontext_tail*]',
        '~$class_constant_state_valid(S_bad)',
        'S_after = $drive_steps(S_bind,1)'] + published() + [
        'pdefaultcache.VALUE = PARRAY n_array',
        'pclassconstantevent = CCREPLACE pdefaultcache_old porigin_trigger n_prefix pconstantfact_write*',
        '$class_constant_roots(S_after.CLASSCONSTANTCACHE) = [HARRAY n_array]',
        '$class_constant_compile_prefix(S_after.DECLARATIONS,1,0) = (n_eval_prefix)',
        '$class_constant_compile_entry(S_after,1) = (S_projection)',
        '$default_cache_at(S_projection.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_old)',
        '$trait_notice_cache_prefix(S_after,S_after.CLASSCONSTANTHISTORY,n_eval_prefix) = [pdefaultcache_old]',
        '$owned_class_next_snapshot(S_after.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL) = (pdefaultcache_old)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
        '$class_constant_compile_entry(S_done,1) = (S_projection_done)',
        '$default_cache_at(S_projection_done.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_old)']


def lookup(fixture, path):
    return start(fixture, path) + bind() + [
        'S_bind.RESULT = KNOWN (POBJECT n_donor)',
        '$constant_fact_at(pconstantcontext_bind.FACTS,pclassconstantdesc.INITIALIZER) = (pconstantfact)',
        'pconstantfact.LOOKUP = (pconstantlookup)',
        '$(pconstantlookup.PREFIX < |S_bind.USERCONSTANTS|)',
        '$global_constant_lookup_valid(S_bind,pclassconstantcontext.DECL,pconstantfact,S_bind.USERCONSTANTS)',
        '~$global_constant_lookup_valid(S_bind,pclassconstantcontext.DECL,pconstantfact[.LOOKUP = eps],S_bind.USERCONSTANTS)',
        '~$global_constant_lookup_valid(S_bind,pclassconstantcontext.DECL,pconstantfact[.LOOKUP = (pconstantlookup[.PREFIX = |S_bind.USERCONSTANTS|])],S_bind.USERCONSTANTS)',
        '$global_constant_alias(S_bind,S_bind.USERCONSTANTS,pclassconstantdesc.INITIALIZER) = (puserconstant_current)',
        'puserconstant_current.VALUE = PINT 9',
        'S_after = $drive_steps(S_bind,1)'] + published() + [
        'pdefaultcache.VALUE = POBJECT n_donor',
        'pclassconstantevent = CCCACHE_READ pclassconstantcontext.DECL porigin_trigger n_prefix pconstantfact_read*',
        '$constant_fact_at(pconstantfact_read*,pclassconstantdesc.INITIALIZER) = (pconstantfact)',
        '$owned_class_stored_flow(S_after,pclassconstantdesc,pclassconstantdesc.INITIALIZER,pdefaultcache.CLASS,n_prefix)',
        '~$owned_class_flow_fact(S_after,pclassconstantdesc,pclassconstantdesc.INITIALIZER,pdefaultcache.CLASS,eps)',
        '$class_constant_roots(S_after.CLASSCONSTANTCACHE) = [HOBJECT n_donor]',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
        '$owned_class_stored_flow(S_done,pclassconstantdesc,pclassconstantdesc.INITIALIZER,pdefaultcache.CLASS,n_prefix)']


def heap_snapshot(fixture, path, response):
    binder = bind(True)
    binder[0] = 'S_bind = $class_owned_parent_pause(S_entered,pclassconstantcontext,10000)'
    return start(fixture, path) + [
        'S_wait = $drive_steps(S_warn,10000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')', 'S_entered.COMPLETION = NORMAL'] + binder + [
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_old)',
        'pdefaultcache_old.VALUE = POBJECT n_donor',
        '$owned_class_snapshot_available(S_bind,pdefaultcache_old)',
        '~$owned_class_snapshot_available(S_bind[.USERCONSTANTS = eps],pdefaultcache_old)',
        '$class_constant_roots(S_bind.CLASSCONSTANTCACHE) = [HOBJECT n_donor]',
        '(HOBJECT n_donor) <- $user_constant_roots(S_bind.USERCONSTANTS)',
        '$owned_class_last_write(S_bind.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL) = (pclassconstantevent_old)',
        'pclassconstantevent_old = CCCACHE_READ pclassconstantcontext.DECL porigin_child n_old_prefix pconstantfact_old*',
        '$constant_fact_at(pconstantfact_old*,pclassconstantdesc.INITIALIZER) = (pconstantfact_child)',
        'pconstantfact_child.CLASS = pdefaultcache_old.CLASS',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        'S_after = $drive_steps(S_bind,1)'] + published() + [
        'pclassconstantevent = CCREPLACE pdefaultcache_old porigin_trigger n_prefix pconstantfact_new*',
        'pclassconstantevent =/= pclassconstantevent_old',
        '$constant_fact_at(pconstantfact_new*,pclassconstantdesc.INITIALIZER) = (pconstantfact_parent)',
        'pconstantfact_parent.CLASS = pdefaultcache.CLASS',
        'pconstantfact_parent.CLASS =/= pdefaultcache_old.CLASS',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$class_constant_roots(S_after.CLASSCONSTANTCACHE) = [HARRAY n_array]',
        '~((HOBJECT n_donor) <- $class_constant_roots(S_after.CLASSCONSTANTCACHE))',
        '(HOBJECT n_donor) <- $user_constant_roots(S_after.USERCONSTANTS)',
        '$owned_class_snapshot_available(S_after,pdefaultcache_old)',
        '~$owned_class_snapshot_available(S_after[.USERCONSTANTS = eps],pdefaultcache_old)',
        '~$owned_class_stored_flow(S_after,pclassconstantdesc,pclassconstantdesc.INITIALIZER,pdefaultcache_old.CLASS,n_old_prefix)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)']


def source_path(group):
    if group == 'heap_snapshot':
        return ROOT / 'tests/semantics/deprecated_global_constant' / (SELECTIONS[group] + '.php')
    return SOURCE / (SELECTIONS[group] + '.php')


def prepare(out, group):
    path = source_path(group)
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        if group in ('reentry', 'heap_snapshot'):
            prefix = b'const SNAP194 =' if group == 'reentry' else b'namespace Ns194; const X ='
            code, = [base64.b64decode(node['fields'][0]['bytes']) for node, _ in nodes(parsed['ast']['program'])
                if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(prefix)]
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
            assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
            checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True}); assert checked_eval['ok']
            response = 'SOURCE_ACCEPT 1 ($ptascii(' + json.dumps(code.decode()) + ')) ' + checked_eval['fixture']
            (out / 'eval-source.php').write_bytes(code)
    finally:
        try: adapter.close()
        finally: frontend.close()
    if group in ('reentry', 'heap_snapshot'):
        checks = {'reentry': reentry, 'heap_snapshot': heap_snapshot}[group](checked['fixture'], path, response)
    else:
        checks = {'cleanup': cleanup, 'publication': publication, 'lookup': lookup}[group](checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=tuple(SELECTIONS), default='cleanup')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), source_path(args.group), *modules, *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
