#!/usr/bin/env python3
"""Check genuine instance-template publication, selection and object copies."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_instance_default_review'
SELECTIONS = {'alias': 'object-alias-cleanup', 'inheritance': 'inherited-template-snapshot',
    'legacy': 'legacy-last-write', 'release': 'retired-global-template'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

EXTRA = r'''
dec $instance_review_bind_ready(pstate,porigin,pstaticdefaultcontext) : bool
def $instance_review_bind_ready(S,porigin_class,pstaticdefaultcontext) = true
  -- if S.TODO = (INSTANCE_DEFAULT_BIND porigin_class pstaticdefaultcontext) :: ptask*
def $instance_review_bind_ready(S,porigin_class,pstaticdefaultcontext) = false -- otherwise
dec $instance_review_bind_pause(pstate,porigin,pstaticdefaultcontext,nat) : pstate
def $instance_review_bind_pause(S,porigin_class,pstaticdefaultcontext,n) = S
  -- if $instance_review_bind_ready(S,porigin_class,pstaticdefaultcontext)
def $instance_review_bind_pause(S,porigin_class,pstaticdefaultcontext,n) = $instance_review_bind_pause(S_next[.COMPLETION = NORMAL],porigin_class,pstaticdefaultcontext,$nabs($(n - 1)))
  -- if ~$instance_review_bind_ready(S,porigin_class,pstaticdefaultcontext)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $instance_review_bind_pause(S,porigin_class,pstaticdefaultcontext,n) = S -- otherwise
dec $instance_review_node(pstate,pnode,porigin) : bool
def $instance_review_node(S,HOBJECT n,porigin_class) = true
  -- if $(n < |S.OBJECTS|)
  -- if S.OBJECTS[n] = INSTANCE porigin_class
def $instance_review_node(S,pnode,porigin_class) = false -- otherwise
dec $instance_review_live_count(pstate,pnode*,porigin) : nat
def $instance_review_live_count(S,eps,porigin_class) = 0
def $instance_review_live_count(S,pnode :: pnode_tail*,porigin_class) = $(1 + $instance_review_live_count(S,pnode_tail*,porigin_class))
  -- if $instance_review_node(S,pnode,porigin_class)
def $instance_review_live_count(S,pnode :: pnode_tail*,porigin_class) = $instance_review_live_count(S,pnode_tail*,porigin_class)
  -- if ~$instance_review_node(S,pnode,porigin_class)
dec $instance_review_new_ready(pstate,porigin) : bool
def $instance_review_new_ready(S,porigin_class) = true
  -- if S.TODO = (CLASS_CONST_CONSTRUCT ptbytes phpType7* b z) :: ptask*
  -- if $class_named(S.CLASSNAMES,$ptlc(ptbytes)) = (porigin_class)
def $instance_review_new_ready(S,porigin_class) = false -- otherwise
dec $instance_review_new_pause(pstate,porigin,nat) : pstate
def $instance_review_new_pause(S,porigin_class,n) = S
  -- if $instance_review_new_ready(S,porigin_class)
def $instance_review_new_pause(S,porigin_class,n) = $instance_review_new_pause(S_next[.COMPLETION = NORMAL],porigin_class,$nabs($(n - 1)))
  -- if ~$instance_review_new_ready(S,porigin_class)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $instance_review_new_pause(S,porigin_class,n) = S -- otherwise
dec $instance_review_written(pstate,porigin,porigin,pvalue) : bool
def $instance_review_written(S,porigin_class,porigin_decl,pvalue) = true
  -- if $instance_default_at(S.INSTANCEDEFAULTS,porigin_class,porigin_decl) = (pinstancetemplate)
  -- if $instance_default_value(pinstancetemplate.STATE) = ((pvalue,pvalueclass))
def $instance_review_written(S,porigin_class,porigin_decl,pvalue) = false -- otherwise
dec $instance_review_write_pause(pstate,porigin,porigin,pvalue,nat) : pstate
def $instance_review_write_pause(S,porigin_class,porigin_decl,pvalue,n) = S
  -- if $instance_review_written(S,porigin_class,porigin_decl,pvalue)
def $instance_review_write_pause(S,porigin_class,porigin_decl,pvalue,n) = $instance_review_write_pause(S_next[.COMPLETION = NORMAL],porigin_class,porigin_decl,pvalue,$nabs($(n - 1)))
  -- if ~$instance_review_written(S,porigin_class,porigin_decl,pvalue)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $instance_review_write_pause(S,porigin_class,porigin_decl,pvalue,n) = S -- otherwise
dec $instance_review_drop_ready(pstate) : bool
def $instance_review_drop_ready(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_drop)
  -- if S.OBJECTS[n_drop] = INSTANCE porigin_drop
  -- if $class_at(S.CLASSES,porigin_drop) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Drop197")
  -- if $destructor_method(S,n_drop) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $instance_review_drop_ready(S) = false -- otherwise
dec $instance_review_drop_pause(pstate,nat) : pstate
def $instance_review_drop_pause(S,n) = S -- if $instance_review_drop_ready(S)
def $instance_review_drop_pause(S,n) = $instance_review_drop_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$instance_review_drop_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $instance_review_drop_pause(S,n) = S -- otherwise
dec $instance_review_publish_ready(pstate) : bool
def $instance_review_publish_ready(S) = true
  -- if S.TODO = (INSTANCE_DEFAULT_PUBLISH porigin pstaticdefaultcontext pvalue pvalueclass) :: ptask*
def $instance_review_publish_ready(S) = false -- otherwise
dec $instance_review_publish_pause(pstate,nat) : pstate
def $instance_review_publish_pause(S,n) = S -- if $instance_review_publish_ready(S)
def $instance_review_publish_pause(S,n) = $instance_review_publish_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$instance_review_publish_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $instance_review_publish_pause(S,n) = S -- otherwise
dec $instance_review_lookup_head(pclassconstantevent,porigin,porigin) : pinstanceglobalcertificate?
def $instance_review_lookup_head(CCINSTANCE_LOOKUP pinstanceglobalcertificate,porigin_class,porigin_decl) = (pinstanceglobalcertificate)
  -- if $instance_global_write_matches(pinstanceglobalcertificate,porigin_class,porigin_decl)
def $instance_review_lookup_head(pclassconstantevent,porigin_class,porigin_decl) = eps -- otherwise
dec $instance_review_lookup(pclassconstantevent*,porigin,porigin) : pinstanceglobalcertificate?
def $instance_review_lookup(eps,porigin_class,porigin_decl) = eps
def $instance_review_lookup(pclassconstantevent :: pclassconstantevent_tail*,porigin_class,porigin_decl) = (pinstanceglobalcertificate)
  -- if $instance_review_lookup_head(pclassconstantevent,porigin_class,porigin_decl) = (pinstanceglobalcertificate)
def $instance_review_lookup(pclassconstantevent :: pclassconstantevent_tail*,porigin_class,porigin_decl) = $instance_review_lookup(pclassconstantevent_tail*,porigin_class,porigin_decl)
  -- if $instance_review_lookup_head(pclassconstantevent,porigin_class,porigin_decl) = eps
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'pdeprecatedconstant.COPIED = eps',
        '$instance_default_context_at(S_warn.TODO) = (porigin_class)',
        '$static_default_context_at(S_warn.TODO) = (pstaticdefaultcontext)',
        '$property_default_active_desc(S_warn,pstaticdefaultcontext.DECL) = (ppropertydesc)',
        'ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer',
        '$instance_default_at(S_warn.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_pending)',
        'pinstancetemplate_pending.STATE = INSTANCE_PENDING porigin_initializer',
        '$deprecated_constant_payload_valid(S_warn,pdeprecatedconstant)',
        '$call_descriptors_valid(S_warn)']


def binder(entered='S_warn'):
    return ['S_bind = $instance_review_bind_pause(' + entered + ',porigin_class,pstaticdefaultcontext,10000)',
        'S_bind.COMPLETION = NORMAL',
        '$instance_review_bind_ready(S_bind,porigin_class,pstaticdefaultcontext)',
        '$instance_default_bind_valid(S_bind,porigin_class,pstaticdefaultcontext)',
        '$call_descriptors_valid(S_bind)']


def alias(fixture, path):
    return start(fixture, path) + [
        '$deprecated_constant_value(S_warn,pdeprecatedconstant.SITE) = POBJECT n_global'
    ] + binder() + [
        'S_bind.RESULT = KNOWN (POBJECT n_global)',
        '$instance_review_live_count(S_bind,S_bind.ALLOCATIONS,porigin_class) = 0',
        '$instance_default_roots(S_bind.INSTANCEDEFAULTS) = eps',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        '$constant_fact_at(pconstantcontext.FACTS,porigin_initializer) = (pconstantfact)',
        'pconstantfact.LOOKUP = (pconstantlookup)',
        '$(pconstantlookup.PREFIX < |S_bind.USERCONSTANTS|)',
        '$global_constant_alias(S_bind,S_bind.USERCONSTANTS,porigin_initializer) = (puserconstant_now)',
        'puserconstant_now.VALUE = PINT 9',
        'n_baseline = $heap_owners($heap_graph(S_bind[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]),HOBJECT n_global)',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero.INSTANCEDEFAULTS = S_bind.INSTANCEDEFAULTS',
        'S_zero.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        'S_after = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_after.COMPLETION = BUDGET',
        '$instance_default_at(S_after.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate)',
        'pinstancetemplate.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_global) pvalueclass (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate)',
        'pinstanceglobalcertificate.TARGET = porigin_class',
        'pinstanceglobalcertificate.DECL = pstaticdefaultcontext.DECL',
        'pinstanceglobalcertificate.VALUE = POBJECT n_global',
        'pinstanceglobalcertificate.CLASS = pvalueclass',
        'S_after.CLASSCONSTANTHISTORY[pinstanceglobalcertificate.HISTORY] = CCINSTANCE_LOOKUP pinstanceglobalcertificate',
        '$constant_fact_at(pinstanceglobalcertificate.FACTS,porigin_initializer) = (pconstantfact)',
        '$instance_default_roots(S_after.INSTANCEDEFAULTS) = [HOBJECT n_global]',
        '$heap_owners($heap_graph(S_after),HOBJECT n_global) = $(n_baseline + 1)',
        '$instance_review_live_count(S_after,S_after.ALLOCATIONS,porigin_class) = 0',
        'S_after.OBJECTS = S_bind.OBJECTS',
        'S_after.CONSTANTOBJECTS = S_bind.CONSTANTOBJECTS',
        'S_after.CONSTANTCLOSURES = S_bind.CONSTANTCLOSURES',
        'S_after.CLOSUREBINDINGS = S_bind.CLOSUREBINDINGS',
        '$instance_default_row_state_valid(S_after,pinstancetemplate,ppropertydesc)',
        '~$instance_default_row_state_valid(S_after,pinstancetemplate[.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_global) pvalueclass (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate[.HISTORY = 0])],ppropertydesc)',
        '$call_descriptors_valid(S_after)',
        'S_ready = $instance_review_new_pause(S_after[.COMPLETION = NORMAL],porigin_class,10000)',
        'S_ready.COMPLETION = NORMAL', '$instance_review_new_ready(S_ready,porigin_class)',
        '$instance_review_live_count(S_ready,S_ready.ALLOCATIONS,porigin_class) = 0',
        'n_object = |S_ready.OBJECTS|',
        'n_before = $heap_owners($heap_graph(S_ready),HOBJECT n_global)',
        'S_new = $drive_steps(S_ready,1)', 'S_new.COMPLETION = BUDGET',
        '|S_new.OBJECTS| = $(n_object + 1)',
        'S_new.OBJECTS[n_object] = INSTANCE porigin_class',
        '$objectprops_at(S_new.OBJECTPROPS,n_object) = ([{DECL (pstaticdefaultcontext.DECL),NAME ppropertydesc.KEY,STATE PROP_VALUE (DIRECT (POBJECT n_global))}])',
        '$heap_owners($heap_graph(S_new),HOBJECT n_global) = $(n_before + 1)',
        'S_new.INSTANCEDEFAULTS = S_after.INSTANCEDEFAULTS',
        '$call_descriptors_valid(S_new)',
        'S_done = $drive_steps(S_new[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
        'S_done.INSTANCEDEFAULTS = S_after.INSTANCEDEFAULTS',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)',
        'S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS',
        'S_done.INSTANCEDEFAULTS = S_full.INSTANCEDEFAULTS',
        'S_done.CLASSCONSTANTHISTORY = S_full.CLASSCONSTANTHISTORY']


def inheritance(fixture, path, responses):
    return start(fixture, path) + [
        'S_wait1 = $drive_steps(S_warn,10000)', 'S_wait1.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait1,' + responses[0] + ')',
        'S_entered1 = $eval_resume(S_wait1,' + responses[0] + ')',
        'S_entered1.COMPLETION = NORMAL',
        'S_wait2 = $drive_steps(S_entered1,10000)', 'S_wait2.COMPLETION = SOURCE_PENDING',
        '$instance_default_at(S_wait2.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_parent)',
        'pinstancetemplate_parent.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_inner) pvalueclass (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_old)',
        'S_wait2.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$class_named(S_wait2.CLASSNAMES,$ptascii("ns197") ++ [92] ++ $ptascii("child197")) = eps',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_entered2 = $eval_resume(S_wait2,' + responses[1] + ')',
        'S_entered2.COMPLETION = NORMAL'
    ] + binder('S_entered2') + [
        'S_bind.RESULT = KNOWN (PARRAY n_outer)',
        'S_bind.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'n_inner =/= n_outer',
        '$instance_default_at(S_bind.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_parent)',
        '$class_named(S_bind.CLASSNAMES,$ptascii("ns197") ++ [92] ++ $ptascii("child197")) = (porigin_child)',
        '$instance_default_at(S_bind.INSTANCEDEFAULTS,porigin_child,pstaticdefaultcontext.DECL) = (pinstancetemplate_child)',
        'pinstancetemplate_child.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_inner) pvalueclass pinstanceobjectcertificate_child',
        'pinstanceobjectcertificate_child = INSTANCE_OBJECT_COPY porigin_child n_child (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_old)',
        '$heap_count(HARRAY n_inner,$instance_default_roots(S_bind.INSTANCEDEFAULTS)) = 2',
        '$instance_object_certificate_valid(S_bind,pinstanceobjectcertificate_child,porigin_child,pstaticdefaultcontext.DECL,pvalueclass)',
        'S_after = $instance_review_write_pause(S_bind,porigin_class,pstaticdefaultcontext.DECL,PARRAY n_outer,10000)',
        'S_after.COMPLETION = NORMAL',
        '$instance_default_at(S_after.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_new)',
        'pinstancetemplate_new.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_outer) pvalueclass (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_new)',
        '$instance_default_at(S_after.INSTANCEDEFAULTS,porigin_child,pstaticdefaultcontext.DECL) = (pinstancetemplate_child)',
        '$instance_default_link_prefix(S_after.CLASSCONSTANTHISTORY,porigin_child,eps) = (pclassconstantevent_before*)',
        'n_link = |pclassconstantevent_before*|',
        'S_after.CLASSCONSTANTHISTORY[n_link] = CCLINK porigin_child n_child',
        '$(pinstanceglobalcertificate_old.HISTORY < n_link)',
        '$(pinstanceglobalcertificate_new.HISTORY > n_link)',
        'S_after.CLASSCONSTANTHISTORY[pinstanceglobalcertificate_old.HISTORY] = CCINSTANCE_LOOKUP pinstanceglobalcertificate_old',
        'S_after.CLASSCONSTANTHISTORY[pinstanceglobalcertificate_new.HISTORY] = CCINSTANCE_LOOKUP pinstanceglobalcertificate_new',
        '$instance_object_certificate_valid(S_after,pinstanceobjectcertificate_child,porigin_child,pstaticdefaultcontext.DECL,pvalueclass)',
        '~$instance_object_certificate_valid(S_after,INSTANCE_OBJECT_COPY porigin_child n_child (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_new),porigin_child,pstaticdefaultcontext.DECL,pvalueclass)',
        '$constant_value_class_valid(S_after,PARRAY n_inner,pvalueclass)',
        '$constant_value_class_valid(S_after,PARRAY n_outer,pvalueclass)',
        'pinstanceglobalcertificate_bad = pinstanceglobalcertificate_new[.VALUE = PARRAY n_inner]',
        'pinstancetemplate_bad = pinstancetemplate_new[.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_inner) pvalueclass (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_bad)]',
        'S_bad = S_after[.CLASSCONSTANTHISTORY[pinstanceglobalcertificate_new.HISTORY] = CCINSTANCE_LOOKUP pinstanceglobalcertificate_bad][.INSTANCEDEFAULTS = $instance_default_set(S_after.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL,pinstancetemplate_bad.STATE)]',
        '~$instance_default_row_state_valid(S_bad,pinstancetemplate_bad,ppropertydesc)',
        '$heap_count(HARRAY n_inner,$instance_default_roots(S_after.INSTANCEDEFAULTS)) = 1',
        '$heap_count(HARRAY n_outer,$instance_default_roots(S_after.INSTANCEDEFAULTS)) = 1',
        '$call_descriptors_valid(S_after)',
        'S_done = $drive_steps(S_after,10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.INSTANCEDEFAULTS = S_after.INSTANCEDEFAULTS',
        '$instance_object_certificate_valid(S_done,pinstanceobjectcertificate_child,porigin_child,pstaticdefaultcontext.DECL,pvalueclass)',
        '$call_descriptors_valid(S_done)',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']


def legacy(fixture, path, responses):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_wait1 = $drive_steps(S_start[.COMPLETION = NORMAL],10000)',
        'S_wait1.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait1,' + responses[0] + ')',
        'S_entered1 = $eval_resume(S_wait1,' + responses[0] + ')',
        'S_wait2 = $drive_steps(S_entered1,10000)',
        'S_wait2.COMPLETION = SOURCE_PENDING',
        '$class_named(S_wait2.CLASSNAMES,$ptascii("ns197") ++ [92] ++ $ptascii("box197")) = (porigin_class)',
        '$class_at(S_wait2.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.PROPERTIES = [ppropertydesc]',
        'porigin_decl = ppropertydesc.ORIGIN',
        '$instance_default_at(S_wait2.INSTANCEDEFAULTS,porigin_class,porigin_decl) = (pinstancetemplate)',
        'pinstancetemplate.STATE = INSTANCE_VALUE (PINT 9) PVSCALAR',
        '$property_default_active_desc(S_wait2,porigin_decl) = (ppropertydesc)',
        '$instance_global_last_event(S_wait2.CLASSCONSTANTHISTORY,porigin_class,porigin_decl) = (CCINSTANCE_WRITE porigin_class porigin_decl n_write)',
        '$instance_review_lookup(S_wait2.CLASSCONSTANTHISTORY,porigin_class,porigin_decl) = (pinstanceglobalcertificate_old)',
        'pinstanceglobalcertificate_old.PREFIX = n_write',
        'pinstanceglobalcertificate_old.VALUE = PARRAY n_inner',
        'pvalueclass = pinstanceglobalcertificate_old.CLASS',
        '$instance_global_record_valid(S_wait2,pinstanceglobalcertificate_old)',
        '$instance_global_last_write(S_wait2.CLASSCONSTANTHISTORY,porigin_class,porigin_decl) = eps',
        '$instance_global_last_event(S_wait2.CLASSCONSTANTHISTORY,porigin_class,porigin_decl) = (CCINSTANCE_WRITE porigin_class porigin_decl n_write)',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_entered2 = $eval_resume(S_wait2,' + responses[1] + ')',
        'S_done = $drive_steps(S_entered2,10000)', 'S_done.COMPLETION = NORMAL',
        '$class_named(S_done.CLASSNAMES,$ptascii("ns197") ++ [92] ++ $ptascii("child197")) = (porigin_child)',
        '$instance_default_at(S_done.INSTANCEDEFAULTS,porigin_child,porigin_decl) = (pinstancetemplate_child)',
        'pinstancetemplate_child.STATE = INSTANCE_VALUE (PINT 9) PVSCALAR',
        '$instance_default_link_prefix(S_done.CLASSCONSTANTHISTORY,porigin_child,eps) = (pclassconstantevent_link*)',
        'n_link = |pclassconstantevent_link*|',
        'S_done.CLASSCONSTANTHISTORY[n_link] = CCLINK porigin_child n_child',
        'pinstanceobjectcertificate_bad = INSTANCE_OBJECT_COPY porigin_child n_child (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_old)',
        '$instance_object_certificate_valid(S_done,pinstanceobjectcertificate_bad,porigin_child,porigin_decl,pvalueclass)',
        '~$instance_global_snapshot_valid(S_done,pinstanceobjectcertificate_bad,porigin_child,porigin_decl,S_done.CLASSCONSTANTHISTORY)',
        '~$instance_default_row_state_valid(S_done,pinstancetemplate_child[.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_inner) pvalueclass pinstanceobjectcertificate_bad],ppropertydesc)',
        'pclassconstantevent_tail* = S_done.CLASSCONSTANTHISTORY[n_link:$nabs($(|S_done.CLASSCONSTANTHISTORY| - n_link))]',
        'S_duplicate = S_done[.CLASSCONSTANTHISTORY = pclassconstantevent_link* ++ [CCINSTANCE_LOOKUP pinstanceglobalcertificate_old] ++ pclassconstantevent_tail*]',
        '$instance_global_record_valid(S_duplicate,pinstanceglobalcertificate_old)',
        '$instance_global_snapshot_valid(S_duplicate,pinstanceobjectcertificate_bad,porigin_child,porigin_decl,S_duplicate.CLASSCONSTANTHISTORY)',
        '~$class_constant_history_valid(S_duplicate)',
        '$class_constant_history_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$machine_roots(S_duplicate) = $machine_roots(S_done)']


def release(fixture, path, responses):
    return start(fixture, path) + [
        'S_wait = $drive_steps(S_warn,10000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait,' + responses[0] + ')',
        'S_entered = $eval_resume(S_wait,' + responses[0] + ')',
        'S_entered.COMPLETION = NORMAL'
    ] + binder('S_entered') + [
        'S_bind.RESULT = KNOWN (PARRAY n_new)',
        '$instance_default_at(S_bind.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_old)',
        'pinstancetemplate_old.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_old) pvalueclass_old (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_old)',
        'S_bind.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old_closure)),ENTRY (KINT 1) (DIRECT (PARRAY n_old_global))]',
        'S_bind.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new_closure)),ENTRY (KINT 1) (DIRECT (PARRAY n_new_global))]',
        'n_old =/= n_new', 'n_old_closure =/= n_new_closure',
        '$heap_owners($heap_graph(S_bind),HARRAY n_old) = 1',
        '$heap_owners($heap_graph(S_bind),HARRAY n_new) = 1',
        'S_stage = $drive_steps(S_bind,1)', 'S_stage.COMPLETION = BUDGET',
        'S_stage.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (INSTANCE_DEFAULT_PUBLISH porigin_class pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) :: ptask_tail*',
        '$instance_default_at(S_stage.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_marker)',
        'pinstancetemplate_marker.STATE = INSTANCE_BINDING',
        'S_stage.RESULT = KNOWN PNULL', 'S_stage.BASE = BASE_VALUE (KNOWN PNULL)',
        '$instance_default_roots(S_stage.INSTANCEDEFAULTS) = eps',
        '$task_nodes(INSTANCE_DEFAULT_PUBLISH porigin_class pstaticdefaultcontext (PARRAY n_new) pvalueclass_new) = [HARRAY n_new]',
        '$heap_owners($heap_graph(S_stage),HARRAY n_new) = 1',
        '$instance_publication_valid(S_stage,porigin_class,pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        '~$instance_publication_row_valid(S_stage[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*],pinstancetemplate_marker)',
        '$call_descriptors_valid(S_stage)',
        'S_drop = $instance_review_drop_pause(S_stage[.COMPLETION = NORMAL],10000)',
        'S_drop.COMPLETION = NORMAL', '$instance_review_drop_ready(S_drop)',
        '~((HARRAY n_old) <- S_drop.ALLOCATIONS)',
        '~((HOBJECT n_old_closure) <- S_drop.ALLOCATIONS)',
        '(HARRAY n_new) <- S_drop.ALLOCATIONS',
        '(HOBJECT n_new_closure) <- S_drop.ALLOCATIONS',
        '$heap_owners($heap_graph(S_drop),HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_drop),HOBJECT n_new_closure) = 1',
        '$instance_publication_frames(S_drop,S_drop.FRAMES,porigin_class,pstaticdefaultcontext.DECL)',
        '$instance_global_record_valid(S_drop,pinstanceglobalcertificate_old)',
        '~$constant_value_class_valid(S_drop,PARRAY n_old,pvalueclass_old)',
        'S_poison = S_drop[.ARRAYS[n_old].ITEMS = eps]',
        '$instance_global_record_valid(S_poison,pinstanceglobalcertificate_old)',
        '$machine_roots(S_drop[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_drop)',
        '$class_constant_history_valid(S_drop)',
        'S_ready = $instance_review_publish_pause(S_drop,10000)',
        'S_ready.COMPLETION = NORMAL', '$instance_review_publish_ready(S_ready)',
        '$instance_global_last_write(S_ready.CLASSCONSTANTHISTORY,porigin_class,pstaticdefaultcontext.DECL) = (pinstanceglobalcertificate_old)',
        '$instance_publication_valid(S_ready,porigin_class,pstaticdefaultcontext,PARRAY n_new,pvalueclass_new)',
        '$call_descriptors_valid(S_ready)',
        'S_after = $drive_steps(S_ready,1)', 'S_after.COMPLETION = BUDGET',
        '$instance_default_at(S_after.INSTANCEDEFAULTS,porigin_class,pstaticdefaultcontext.DECL) = (pinstancetemplate_new)',
        'pinstancetemplate_new.STATE = INSTANCE_OBJECT_VALUE (PARRAY n_new) pvalueclass_new (INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_new)',
        'S_after.CLASSCONSTANTHISTORY[pinstanceglobalcertificate_new.HISTORY] = CCINSTANCE_LOOKUP pinstanceglobalcertificate_new',
        '$instance_global_last_write(S_after.CLASSCONSTANTHISTORY,porigin_class,pstaticdefaultcontext.DECL) = (pinstanceglobalcertificate_new)',
        '$instance_global_record_valid(S_after,pinstanceglobalcertificate_old)',
        '~$instance_global_snapshot_valid(S_after,INSTANCE_GLOBAL_BIND pinstanceglobalcertificate_old,porigin_class,pstaticdefaultcontext.DECL,S_after.CLASSCONSTANTHISTORY)',
        '$heap_owners($heap_graph(S_after),HARRAY n_new) = 1',
        '$call_descriptors_valid(S_after)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)']


def prepare(out, group):
    path = SOURCE / (SELECTIONS[group] + '.php')
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter', seconds=45)
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
        responses = []
        if group != 'alias':
            codes = [base64.b64decode(node['fields'][0]['bytes']) for node, _ in nodes(parsed['ast']['program'])
                if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'namespace Ns197;')]
            assert len(codes) == (1 if group == 'release' else 2)
            for request_id, code in enumerate(codes, 1):
                parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(request_id), 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
                assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
                checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
                assert checked_eval['ok']
                responses.append('SOURCE_ACCEPT ' + str(request_id) + ' (' + types.byte_expr(code.decode()) + ') ' + checked_eval['fixture'])
                (out / ('eval-' + str(request_id) + '.php')).write_bytes(code)
    finally:
        try: adapter.close()
        finally: frontend.close()
    if group == 'alias': checks = alias(checked['fixture'], path)
    elif group == 'inheritance': checks = inheritance(checked['fixture'], path, responses)
    elif group == 'legacy': checks = legacy(checked['fixture'], path, responses)
    else: checks = release(checked['fixture'], path, responses)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=tuple(SELECTIONS), required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE / (SELECTIONS[args.group] + '.php'), *modules, *(ROOT / path for path in (
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
