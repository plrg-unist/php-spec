#!/usr/bin/env python3
"""Check actual static-default recipients, selected aliases and retired cells."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_static_default_review'
SELECTIONS = {'lookup': 'global-closure-alias', 'reference': 'retired-typed-reference',
    'publication': 'reentrant-old-slot-release'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def source_path(group):
    directory = ROOT / 'tests/semantics/deprecated_static_property_default' if group == 'publication' else SOURCE
    return directory / (SELECTIONS[group] + '.php')


EXTRA = r'''
dec $static_review_bind_ready(pstate,pstaticdefaultcontext) : bool
def $static_review_bind_ready(S,pstaticdefaultcontext) = true
  -- if S.TODO = (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask*
def $static_review_bind_ready(S,pstaticdefaultcontext) = false -- otherwise
dec $static_review_bind_pause(pstate,pstaticdefaultcontext,nat) : pstate
def $static_review_bind_pause(S,pstaticdefaultcontext,n) = S
  -- if $static_review_bind_ready(S,pstaticdefaultcontext)
def $static_review_bind_pause(S,pstaticdefaultcontext,n) = $static_review_bind_pause(S_next[.COMPLETION = NORMAL],pstaticdefaultcontext,$nabs($(n - 1)))
  -- if ~$static_review_bind_ready(S,pstaticdefaultcontext)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $static_review_bind_pause(S,pstaticdefaultcontext,n) = S -- otherwise
dec $static_review_committed(pstate,porigin,pvalue) : bool
def $static_review_committed(S,porigin,pvalue) = true
  -- if $class_static_at(S.CLASSSTATICS,porigin) = (pclassstatic)
  -- if pclassstatic.STATE = PROP_VALUE (DIRECT pvalue)
def $static_review_committed(S,porigin,pvalue) = false -- otherwise
dec $static_review_commit_pause(pstate,porigin,pvalue,nat) : pstate
def $static_review_commit_pause(S,porigin,pvalue,n) = S
  -- if $static_review_committed(S,porigin,pvalue)
def $static_review_commit_pause(S,porigin,pvalue,n) = $static_review_commit_pause(S_next[.COMPLETION = NORMAL],porigin,pvalue,$nabs($(n - 1)))
  -- if ~$static_review_committed(S,porigin,pvalue)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $static_review_commit_pause(S,porigin,pvalue,n) = S -- otherwise
dec $static_review_drop_ready(pstate,nat) : bool
def $static_review_drop_ready(S,n_old) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_old)
  -- if S.OBJECTS[n_old] = INSTANCE porigin_drop
  -- if $class_at(S.CLASSES,porigin_drop) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Drop196")
  -- if $destructor_method(S,n_old) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $static_review_drop_ready(S,n_old) = false -- otherwise
dec $static_review_drop_pause(pstate,nat,nat) : pstate
def $static_review_drop_pause(S,n_old,n) = S -- if $static_review_drop_ready(S,n_old)
def $static_review_drop_pause(S,n_old,n) = $static_review_drop_pause(S_next[.COMPLETION = NORMAL],n_old,$nabs($(n - 1)))
  -- if ~$static_review_drop_ready(S,n_old)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $static_review_drop_pause(S,n_old,n) = S -- otherwise
dec $static_review_publish_ready(pstate) : bool
def $static_review_publish_ready(S) = true
  -- if S.TODO = (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext pvalue pvalueclass) :: ptask*
def $static_review_publish_ready(S) = false -- otherwise
dec $static_review_publish_pause(pstate,nat) : pstate
def $static_review_publish_pause(S,n) = S -- if $static_review_publish_ready(S)
def $static_review_publish_pause(S,n) = $static_review_publish_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$static_review_publish_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $static_review_publish_pause(S,n) = S -- otherwise
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
        '$static_default_context_at(S_warn.TODO) = (pstaticdefaultcontext)',
        'pstaticdefaultcontext.DECL = pconstantcontext.ORIGIN',
        '$class_static_active_desc(S_warn,S_warn.CLASSNAMES,pstaticdefaultcontext.DECL) = (ppropertydesc)',
        'ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer',
        '$class_static_at(S_warn.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic)',
        'pclassstatic.STATE = PROP_DEFERRED porigin_initializer',
        '$owned_static_source(S_warn,ppropertydesc)', '$owned_static_scope(S_warn)',
        '$static_default_context_valid(S_warn,pconstantcontext)',
        '$deprecated_constant_static_ast(S_warn,pdeprecatedconstant.SITE)',
        '$deprecated_constant_payload_valid(S_warn,pdeprecatedconstant)',
        '~$owned_static_scope(S_warn[.CONSTCONTEXT = eps])',
        '~$owned_static_scope(S_warn[.CLASSSTATICS = eps])',
        '~$owned_static_source(S_warn,ppropertydesc[.STATIC = false])',
        '$call_descriptors_valid(S_warn)']


def binder(entered='S_warn'):
    return ['S_bind = $static_review_bind_pause(' + entered + ',pstaticdefaultcontext,10000)',
        'S_bind.COMPLETION = NORMAL', '$static_review_bind_ready(S_bind,pstaticdefaultcontext)',
        'S_bind.CONSTCONTEXT = (pconstantcontext_bind)',
        '$owned_static_scope(S_bind)', '$static_default_bind_valid(S_bind,pstaticdefaultcontext)',
        '$call_descriptors_valid(S_bind)']


def lookup(fixture, path):
    return start(fixture, path) + [
        '$deprecated_constant_value(S_warn,pdeprecatedconstant.SITE) = POBJECT n_global'
    ] + binder() + [
        'S_bind.RESULT = KNOWN (POBJECT n_global)',
        '$constant_fact_at(pconstantcontext_bind.FACTS,porigin_initializer) = (pconstantfact)',
        'pconstantfact.LOOKUP = (pconstantlookup)',
        '$(pconstantlookup.PREFIX < |S_bind.USERCONSTANTS|)',
        '$owned_static_lookup_required(S_bind,pstaticdefaultcontext.DECL,pconstantfact)',
        '$global_constant_lookup_valid(S_bind,pstaticdefaultcontext.DECL,pconstantfact,S_bind.USERCONSTANTS)',
        '~$global_constant_lookup_valid(S_bind,pstaticdefaultcontext.DECL,pconstantfact[.LOOKUP = eps],S_bind.USERCONSTANTS)',
        '~$global_constant_lookup_valid(S_bind,pstaticdefaultcontext.DECL,pconstantfact[.LOOKUP = (pconstantlookup[.PREFIX = |S_bind.USERCONSTANTS|])],S_bind.USERCONSTANTS)',
        '$global_constant_alias(S_bind,S_bind.USERCONSTANTS,porigin_initializer) = (puserconstant_now)',
        'puserconstant_now.VALUE = PINT 9',
        '$property_default_transfer_valid(S_bind,ppropertydesc,pconstantfact.CLASS)',
        '$class_static_roots(S_bind.CLASSSTATICS) = eps',
        'S_after = $drive_steps(S_bind,1)', 'S_after.COMPLETION = BUDGET',
        '$class_static_at(S_after.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_after)',
        'pclassstatic_after.STATE = PROP_VALUE (DIRECT (POBJECT n_global))',
        '$class_static_roots(S_after.CLASSSTATICS) = [HOBJECT n_global]',
        'S_after.OBJECTS = S_bind.OBJECTS',
        'S_after.CONSTANTCLOSURES = S_bind.CONSTANTCLOSURES',
        'S_after.CLOSUREBINDINGS = S_bind.CLOSUREBINDINGS',
        'S_after.CLOSURECACHES = S_bind.CLOSURECACHES',
        '~$owned_static_scope(S_after)', '$class_statics_valid(S_after)',
        '$call_descriptors_valid(S_after)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
        '$class_static_at(S_done.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_done)',
        'pclassstatic_done.STATE = pclassstatic_after.STATE',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']


def reference(fixture, path, response):
    return start(fixture, path) + [
        'S_wait = $drive_steps(S_warn,10000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')', 'S_entered.COMPLETION = NORMAL'
    ] + binder('S_entered') + [
        'S_bind.RESULT = KNOWN (PARRAY n_new)',
        '$class_static_at(S_bind.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_old)',
        'pclassstatic_old.STATE = PROP_VALUE (ALIAS n_reference)',
        '$lookup($global_table_view(S_bind).ENV,$ptascii("alias")) = (n_reference)',
        'S_bind.STORE[n_reference] = DEFINED (PARRAY n_old)',
        'S_bind.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        'S_bind.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$propref_source_present(S_bind.PROPREFS,n_reference,CLASS_PROP_SOURCE pstaticdefaultcontext.DECL)',
        '$propref_source_valid(S_bind,n_reference,CLASS_PROP_SOURCE pstaticdefaultcontext.DECL)',
        'n_retired = |S_bind.CLASSCONSTANTHISTORY|',
        '$constant_fact_at(pconstantcontext_bind.FACTS,porigin_initializer) = (pconstantfact_array)',
        'pconstantfact_array.LOOKUP = (pconstantlookup_array)',
        '$(pconstantlookup_array.PREFIX < |S_bind.USERCONSTANTS|)',
        '$global_constant_lookup_valid(S_bind,pstaticdefaultcontext.DECL,pconstantfact_array,S_bind.USERCONSTANTS)',
        'S_stage = $drive_steps(S_bind,1)', 'S_stage.COMPLETION = BUDGET',
        'S_stage.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) :: ptask_tail*',
        '$static_publication_valid(S_stage,pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        '$constant_value_class_valid(S_stage,PARRAY n_old,pvalueclass_new)',
        'S_bad = S_stage[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_old) pvalueclass_new) :: ptask_tail*]',
        '~$static_publication_valid(S_bad,pstaticdefaultcontext,PARRAY n_old,pvalueclass_new)',
        '~$class_statics_valid(S_bad)',
        'S_after = $static_review_commit_pause(S_bind,pstaticdefaultcontext.DECL,PARRAY n_new,10000)',
        'S_after.COMPLETION = NORMAL',
        '$class_static_at(S_after.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_new)',
        'pclassstatic_new.STATE = PROP_VALUE (DIRECT (PARRAY n_new))',
        '$lookup($global_table_view(S_after).ENV,$ptascii("alias")) = (n_reference)',
        'S_after.STORE[n_reference] = DEFINED (PARRAY n_old)',
        '~((HCELL n_reference) <- $class_static_roots(S_after.CLASSSTATICS))',
        '(HCELL n_reference) <- $machine_roots(S_after)',
        '$static_default_retirement_event(S_after.CLASSCONSTANTHISTORY[n_retired],pstaticdefaultcontext.DECL,n_reference)',
        '$propref_source_present(S_after.PROPREFS,n_reference,RETIRED_CLASS_PROP_SOURCE pstaticdefaultcontext.DECL n_retired)',
        '$propref_source_valid(S_after,n_reference,RETIRED_CLASS_PROP_SOURCE pstaticdefaultcontext.DECL n_retired)',
        '~$propref_source_valid(S_after,n_reference,CLASS_PROP_SOURCE pstaticdefaultcontext.DECL)',
        '~$propref_source_valid(S_after,n_reference,RETIRED_CLASS_PROP_SOURCE pstaticdefaultcontext.DECL 0)',
        '$class_statics_valid(S_after)', '$call_descriptors_valid(S_after)',
        'S_done = $drive_steps(S_after,10000)', 'S_done.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_done)',
        '$class_static_at(S_done.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_done)',
        'pclassstatic_done.STATE = pclassstatic_new.STATE',
        'S_done.STORE[n_reference] = DEFINED (PARRAY n_changed)',
        'S_done.ARRAYS[n_changed].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8))]',
        '$propref_source_valid(S_done,n_reference,RETIRED_CLASS_PROP_SOURCE pstaticdefaultcontext.DECL n_retired)']


def publication(fixture, path):
    return start(fixture, path) + binder() + [
        'S_bind.RESULT = KNOWN (PARRAY n_new)',
        '$class_static_at(S_bind.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_old)',
        'pclassstatic_old.STATE = PROP_VALUE (DIRECT (POBJECT n_old))',
        'S_bind.OBJECTS[n_old] = INSTANCE porigin_old',
        '$class_at(S_bind.CLASSES,porigin_old) = (pclassdesc_old)',
        'pclassdesc_old.NAME = $ptascii("Drop196")',
        '$static_default_filled(S_bind,ppropertydesc)',
        '(HOBJECT n_old) <- $class_static_roots(S_bind.CLASSSTATICS)',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_old) = 1',
        '(HARRAY n_new) <- $user_constant_roots(S_bind.USERCONSTANTS)',
        'n_baseline = $heap_owners($heap_graph(S_bind[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]),HARRAY n_new)',
        '$class_named(S_bind.CLASSNAMES,$ptascii("ns196\\other196")) = (porigin_other)',
        '$class_static_select(S_bind,porigin_other,$ptascii("value")) = (ppropertydesc_other)',
        'ppropertydesc_other.DEFAULT = PROP_DEFERRED porigin_other_initializer',
        '$class_static_at(S_bind.CLASSSTATICS,ppropertydesc_other.ORIGIN) = (pclassstatic_other)',
        'pclassstatic_other.STATE = PROP_DEFERRED porigin_other_initializer',
        '~$static_default_filled(S_bind,ppropertydesc_other)',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero.CLASSSTATICS = S_bind.CLASSSTATICS',
        'S_zero.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        'S_stage = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_stage.COMPLETION = BUDGET',
        'S_stage.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
        '$destructor_release_valid(S_stage,pdestructionrelease)',
        'S_stage.RESULT = KNOWN PNULL', 'S_stage.BASE = BASE_VALUE (KNOWN PNULL)',
        '$class_static_at(S_stage.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_marker)',
        'pclassstatic_marker.STATE = PROP_STATIC_BINDING',
        'S_stage.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        '~((HOBJECT n_old) <- $class_static_roots(S_stage.CLASSSTATICS))',
        '$class_static_roots(S_stage.CLASSSTATICS) = eps',
        '$task_nodes(STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) = [HARRAY n_new]',
        '$heap_owners($heap_graph(S_stage),HARRAY n_new) = $(n_baseline + 1)',
        '$heap_owners($heap_graph(S_stage),HOBJECT n_old) = 1',
        '$static_publication_valid(S_stage,pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        '$class_statics_valid(S_stage)', '$gc_state_valid(S_stage)',
        '$destruction_state_valid(S_stage)', '$call_descriptors_valid(S_stage)',
        '~$static_publication_valid(S_stage[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*],pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        '~$class_statics_valid(S_stage[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*])',
        'pstaticdefaultcontext_bad = pstaticdefaultcontext[.ROOT = pstaticdefaultcontext.DECL]',
        'S_badroot = S_stage[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext_bad (PARRAY n_new) pvalueclass_new) :: ptask_tail*]',
        '~$static_publication_valid(S_badroot,pstaticdefaultcontext_bad,PARRAY n_new,pvalueclass_new)',
        '~$class_statics_valid(S_badroot)',
        '~$static_default_binders_unique((STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) :: (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) :: ptask_tail*,eps)',
        'S_read = $class_static_read(S_stage,pstaticdefaultcontext.ROOT,ppropertydesc.NAME,pstaticdefaultcontext.LINE)',
        'S_read.COMPLETION = UNSUPPORTED "static default slot release"',
        'S_quiet = $class_static_quiet(S_stage,pstaticdefaultcontext.ROOT,ppropertydesc.NAME)',
        'S_quiet.COMPLETION = UNSUPPORTED "static default slot release"',
        'S_store = $class_static_store_ordinary(S_stage,pstaticdefaultcontext.ROOT,ppropertydesc.NAME,PINT 77,pstaticdefaultcontext.LINE)',
        'S_store.COMPLETION = UNSUPPORTED "static default slot release"',
        'S_ref = $class_static_reference_fetch_ordinary(S_stage,pstaticdefaultcontext.DECL,pstaticdefaultcontext.LINE)',
        'S_ref.COMPLETION = UNSUPPORTED "static default slot release"',
        'S_drop = $static_review_drop_pause(S_stage[.COMPLETION = NORMAL],n_old,10000)',
        'S_drop.COMPLETION = NORMAL', '$static_review_drop_ready(S_drop,n_old)',
        '(HOBJECT n_old) <- S_drop.ALLOCATIONS',
        'n_old <- S_drop.DESTRUCTION.CALLED',
        '(HOBJECT n_old) <- $call_context_roots(S_drop.CURRENT)',
        '$class_static_at(S_drop.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_marker)',
        '~((HOBJECT n_old) <- $class_static_roots(S_drop.CLASSSTATICS))',
        '$static_publication_frames(S_drop,S_drop.FRAMES,pstaticdefaultcontext.DECL)',
        '$heap_owners($heap_graph(S_drop),HARRAY n_new) = $(n_baseline + 1)',
        '$class_statics_valid(S_drop)', '$gc_state_valid(S_drop)',
        '$destruction_state_valid(S_drop)', '$constant_context_valid(S_drop)',
        '$call_current_valid(S_drop)',
        '$class_static_at(S_drop.CLASSSTATICS,ppropertydesc_other.ORIGIN) = (pclassstatic_other)',
        'S_ready = $static_review_publish_pause(S_drop,10000)',
        'S_ready.COMPLETION = NORMAL', '$static_review_publish_ready(S_ready)',
        'S_ready.TODO = (STATIC_DEFAULT_PUBLISH pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) :: ptask_ready*',
        '~((HOBJECT n_old) <- S_ready.ALLOCATIONS)',
        '$class_static_at(S_ready.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_marker)',
        '$static_publication_valid(S_ready,pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        '$class_statics_valid(S_ready)', '$call_descriptors_valid(S_ready)',
        '$static_default_filled(S_ready,ppropertydesc_other)',
        '$class_static_at(S_ready.CLASSSTATICS,ppropertydesc_other.ORIGIN) = (pclassstatic_other_filled)',
        'pclassstatic_other_filled.STATE = PROP_VALUE (DIRECT (PARRAY n_other))',
        'S_ready.ARRAYS[n_other].ITEMS = eps',
        'S_after = $drive_steps(S_ready,1)', 'S_after.COMPLETION = BUDGET',
        '$class_static_at(S_after.CLASSSTATICS,pstaticdefaultcontext.DECL) = (pclassstatic_new)',
        'pclassstatic_new.STATE = PROP_VALUE (DIRECT (PARRAY n_new))',
        'S_after.CLASSCONSTANTHISTORY = S_ready.CLASSCONSTANTHISTORY',
        '$class_statics_valid(S_after)', '$call_descriptors_valid(S_after)',
        '~$static_publication_valid(S_after,pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)',
        'S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS',
        'S_done.CLASSSTATICS = S_full.CLASSSTATICS',
        'S_done.CLASSCONSTANTHISTORY = S_full.CLASSCONSTANTHISTORY']


def prepare(out, group):
    path = source_path(group)
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter', seconds=45)
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        if group == 'reference':
            code, = [base64.b64decode(node['fields'][0]['bytes']) for node, _ in nodes(parsed['ast']['program'])
                if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'namespace Ns196; const X =')]
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
            assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
            checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
            response = 'SOURCE_ACCEPT 1 ($ptascii(' + json.dumps(code.decode()) + ')) ' + checked_eval['fixture']
            (out / 'eval-source.php').write_bytes(code)
    finally:
        try: adapter.close()
        finally: frontend.close()
    if group == 'lookup': checks = lookup(checked['fixture'], path)
    elif group == 'reference': checks = reference(checked['fixture'], path, response)
    else: checks = publication(checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=tuple(SELECTIONS), required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), source_path(args.group), *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
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
