#!/usr/bin/env python3
"""Source-reached clone selection receipts and cached consumer births."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from readonly_clone_updates_protocol import PREFIX
from readonly_clone_selection_sources import ROWS, snapshot

ROOT = Path(__file__).resolve().parents[2]

GROUPS = {'consumer-birth': (('dyn', 'readonly-clone-dynamic-string-maker-survives-selector-change'),
                    ('fcc', 'readonly-clone-fcc-maker-survives-selector-retirement'),
                    ('manual', 'readonly-manual-computed-clone-maker-retires')),
 'computed-name-birth': (('manual', 'readonly-manual-computed-name-clone-maker-retires'),),
 'reused-maker-birth': (('manual', 'readonly-manual-clone-maker-reuses-genuine-selection'),),
 'private-manual-birth-positive': (('manual',
                                    'readonly-private-manual-clone-fiber-after-retirement'),),
 'shared-origin-positive': (('manual',
                             'readonly-manual-invoke-shares-trait-clone-origin-after-retirement'),),
 'autoload-birth': (('manual',
                     'readonly-selected-manual-clone-autoload-publishes-after-unregister'),),
 'keyword-shutdown-birth': (('shutdown',
                             'readonly-dynamic-clone-created-private-keyword-shutdown-after-retirement'),),
 'closer-window': (('source',
                    'readonly-live-clone-window-survives-fiber-close-caller-parking'),)}

FIBER_PREFIX = r'''
def $clone_updates_review_phase(S,16) = true
  -- if S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail*
  -- if $intrinsic_count(S,pfiberstart.SITE) = (pfiberstart.INDEX)
'''

AUTOLOAD_PREFIX = r'''
def $clone_updates_review_phase(S,17) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("Later")
def $clone_updates_review_phase(S,18) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("Later")
  -- if S.AUTOLOAD.ENTRIES = eps /\ S.AUTOLOAD.BIRTHS = eps
  -- if S.AUTOSEQ = 5
'''

CLOSER_PREFIX = r'''
def $clone_updates_review_phase(S,19) = true
  -- if S.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*
  -- if S.ACTIVEFIBER = (pfiberclose.OBJECT)
  -- if S.CLONES = [pclonewindow]
  -- if pclonewindow.PHASE = CLONE_CALLBACK
  -- if $clone_window_vm(pfiberclose.VM,pclonewindow.OPERATION,CLONE_CALLBACK)
'''

CLAUSES = {
    'consumer-birth': r'''
S_dyn_found = $clone_updates_review_seek(S_initial_dyn,16,2048)
S_dyn_found.COMPLETION = NORMAL \/ S_dyn_found.COMPLETION = BUDGET
S_dyn = S_dyn_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_dyn,16)
S_dyn.CURRENT = eps
S_dyn.FRAMES = eps
S_dyn.CLONES = eps
$call_descriptors_valid(S_dyn)
$heap_valid($heap_graph(S_dyn))
S_dyn.TODO = (FIBER_ARGS pfiberstart_dyn) :: ptask_dyn_tail*
$fiber_at(S_dyn,pfiberstart_dyn.OBJECT) = (pfiber_dyn)
pfiber_dyn.STATUS = FIBER_INIT
pfiber_dyn.READY
pfiber_dyn.PRODUCER = (pshutdownproducer_dyn)
pfiber_dyn.CAPTURE = (pmethodcapture_dyn)
$fiber_producer_valid(S_dyn,pfiber_dyn)
$fiber_cache_valid(S_dyn,pfiberstart_dyn.OBJECT,pfiber_dyn)
S_history_dyn = $consumer_producer_history(S_dyn,pshutdownproducer_dyn)
pshutdownproducer_dyn.TARGET = METHOD_TARGET n_maker_dyn porigin_method_dyn
~((HOBJECT n_maker_dyn) <- S_dyn.ALLOCATIONS)
~((HOBJECT n_maker_dyn) <- $node_children(S_dyn,HOBJECT pfiberstart_dyn.OBJECT))
pshutdownproducer_dyn.INTERNAL
pshutdownproducer_dyn.CLONE = (pcloneproducer_dyn)
pshutdownproducer_dyn.SITE = (pcloneproducer_dyn.SITE)
pcloneproducer_dyn.NAME = ($ptascii("clone"))
pcloneproducer_dyn.CLOSURE = eps
$lookup(S_dyn.ENV,$ptascii("cloner")) = (n_cloner_dyn)
S_dyn.STORE[n_cloner_dyn] = DEFINED (PSTRING $ptascii("unrelated"))
$consumer_clone_selection_valid(S_history_dyn,pcloneproducer_dyn)
$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_dyn)
$consumer_producer_internal_at(S_history_dyn,pshutdownproducer_dyn)
~$consumer_producer_internal(S_history_dyn,pshutdownproducer_dyn.TARGET)
pshutdownproducer_missing = pshutdownproducer_dyn[.CLONE = eps]
~$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_missing)
pfiber_missing = pfiber_dyn[.PRODUCER = (pshutdownproducer_missing)][.CAPTURE = (pmethodcapture_dyn)]
S_missing = $fiber_put(S_dyn,pfiberstart_dyn.OBJECT,pfiber_missing)
$heap_valid($heap_graph(S_missing))
~$fiber_producer_valid(S_missing,pfiber_missing)
~$fiber_cache_valid(S_missing,pfiberstart_dyn.OBJECT,pfiber_missing)
~$call_descriptors_valid(S_missing)
pshutdownproducer_name = pshutdownproducer_dyn[.CLONE = (pcloneproducer_dyn[.NAME = ($ptascii("unrelated"))])]
~$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_name)
pfiber_name = pfiber_dyn[.PRODUCER = (pshutdownproducer_name)][.CAPTURE = (pmethodcapture_dyn)]
S_name = $fiber_put(S_dyn,pfiberstart_dyn.OBJECT,pfiber_name)
$heap_valid($heap_graph(S_name))
~$fiber_producer_valid(S_name,pfiber_name)
~$fiber_cache_valid(S_name,pfiberstart_dyn.OBJECT,pfiber_name)
~$call_descriptors_valid(S_name)
pshutdownproducer_receipt_site = pshutdownproducer_dyn[.CLONE = (pcloneproducer_dyn[.SITE = pfiberstart_dyn.SITE])]
~$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_receipt_site)
pfiber_receipt_site = pfiber_dyn[.PRODUCER = (pshutdownproducer_receipt_site)][.CAPTURE = (pmethodcapture_dyn)]
S_receipt_site = $fiber_put(S_dyn,pfiberstart_dyn.OBJECT,pfiber_receipt_site)
$heap_valid($heap_graph(S_receipt_site))
~$fiber_producer_valid(S_receipt_site,pfiber_receipt_site)
~$fiber_cache_valid(S_receipt_site,pfiberstart_dyn.OBJECT,pfiber_receipt_site)
~$call_descriptors_valid(S_receipt_site)
pmethodcapture_coherent_site = pmethodcapture_dyn[.CALLSITE = (pfiberstart_dyn.SITE)]
pcloneproducer_coherent_site = pcloneproducer_dyn[.SITE = pfiberstart_dyn.SITE]
~$consumer_clone_selection_valid(S_history_dyn,pcloneproducer_coherent_site)
pshutdownproducer_coherent_site = pshutdownproducer_dyn[.SITE = (pfiberstart_dyn.SITE)][.CLONE = (pcloneproducer_coherent_site)]
~$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_coherent_site)
pfiber_coherent_site = pfiber_dyn[.PRODUCER = (pshutdownproducer_coherent_site)][.CAPTURE = (pmethodcapture_coherent_site)]
S_coherent_site = $fiber_put(S_dyn,pfiberstart_dyn.OBJECT,pfiber_coherent_site)
$heap_valid($heap_graph(S_coherent_site))
~$fiber_producer_valid(S_coherent_site,pfiber_coherent_site)
~$fiber_cache_valid(S_coherent_site,pfiberstart_dyn.OBJECT,pfiber_coherent_site)
~$call_descriptors_valid(S_coherent_site)
pshutdownproducer_false_role = pshutdownproducer_dyn[.INTERNAL = false]
~$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_false_role)
pfiber_false_role = pfiber_dyn[.PRODUCER = (pshutdownproducer_false_role)][.CAPTURE = (pmethodcapture_dyn)]
S_false_role = $fiber_put(S_dyn,pfiberstart_dyn.OBJECT,pfiber_false_role)
$heap_valid($heap_graph(S_false_role))
~$fiber_producer_valid(S_false_role,pfiber_false_role)
~$fiber_cache_valid(S_false_role,pfiberstart_dyn.OBJECT,pfiber_false_role)
~$call_descriptors_valid(S_false_role)
~$consumer_producer_snapshot(pshutdownproducer_false_role)
pshutdownproducer_hidden_role = pshutdownproducer_dyn[.INTERNAL = false][.CLONE = eps]
~$consumer_clone_producer_valid(S_history_dyn,pshutdownproducer_hidden_role)
pfiber_hidden_role = pfiber_dyn[.PRODUCER = (pshutdownproducer_hidden_role)][.CAPTURE = (pmethodcapture_dyn)]
S_hidden_role = $fiber_put(S_dyn,pfiberstart_dyn.OBJECT,pfiber_hidden_role)
$heap_valid($heap_graph(S_hidden_role))
~$fiber_producer_valid(S_hidden_role,pfiber_hidden_role)
~$fiber_cache_valid(S_hidden_role,pfiberstart_dyn.OBJECT,pfiber_hidden_role)
~$call_descriptors_valid(S_hidden_role)
$consumer_producer_snapshot(pshutdownproducer_hidden_role)
S_fcc_found = $clone_updates_review_seek(S_initial_fcc,16,2048)
S_fcc_found.COMPLETION = NORMAL \/ S_fcc_found.COMPLETION = BUDGET
S_fcc = S_fcc_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_fcc,16)
S_fcc.CURRENT = eps
S_fcc.FRAMES = eps
S_fcc.CLONES = eps
$call_descriptors_valid(S_fcc)
$heap_valid($heap_graph(S_fcc))
S_fcc.TODO = (FIBER_ARGS pfiberstart_fcc) :: ptask_fcc_tail*
$fiber_at(S_fcc,pfiberstart_fcc.OBJECT) = (pfiber_fcc)
pfiber_fcc.STATUS = FIBER_INIT
pfiber_fcc.READY
pfiber_fcc.PRODUCER = (pshutdownproducer_fcc)
pfiber_fcc.CAPTURE = (pmethodcapture_fcc)
$fiber_producer_valid(S_fcc,pfiber_fcc)
$fiber_cache_valid(S_fcc,pfiberstart_fcc.OBJECT,pfiber_fcc)
S_history_fcc = $consumer_producer_history(S_fcc,pshutdownproducer_fcc)
pshutdownproducer_fcc.TARGET = METHOD_TARGET n_maker_fcc porigin_method_fcc
~((HOBJECT n_maker_fcc) <- S_fcc.ALLOCATIONS)
~((HOBJECT n_maker_fcc) <- $node_children(S_fcc,HOBJECT pfiberstart_fcc.OBJECT))
pshutdownproducer_fcc.INTERNAL
pshutdownproducer_fcc.CLONE = (pcloneproducer_fcc)
pshutdownproducer_fcc.SITE = (pcloneproducer_fcc.SITE)
pcloneproducer_fcc.NAME = eps
pcloneproducer_fcc.CLOSURE = (n_selector_fcc)
$(n_selector_fcc < |S_fcc.OBJECTS|)
S_fcc.OBJECTS[n_selector_fcc] = INTRINSICCLOSURE INTRINSIC_CLONE
~((HOBJECT n_selector_fcc) <- S_fcc.ALLOCATIONS)
~((HOBJECT n_selector_fcc) <- $node_children(S_fcc,HOBJECT pfiberstart_fcc.OBJECT))
$consumer_clone_selection_valid(S_history_fcc,pcloneproducer_fcc)
$consumer_clone_producer_valid(S_history_fcc,pshutdownproducer_fcc)
$consumer_producer_internal_at(S_history_fcc,pshutdownproducer_fcc)
pfiber_fcc.RAW = POBJECT n_callback_fcc
pshutdownproducer_generic = pshutdownproducer_fcc[.TARGET = CLOSURE_TARGET n_callback_fcc]
$consumer_producer_internal(S_history_fcc,pshutdownproducer_generic.TARGET)
~$consumer_producer_internal_at(S_history_fcc,pshutdownproducer_generic)
pshutdownproducer_nonclone_owner = pshutdownproducer_fcc[.CLONE = (pcloneproducer_fcc[.CLOSURE = (n_maker_fcc)])]
~$consumer_clone_producer_valid(S_history_fcc,pshutdownproducer_nonclone_owner)
pfiber_nonclone_owner = pfiber_fcc[.PRODUCER = (pshutdownproducer_nonclone_owner)][.CAPTURE = (pmethodcapture_fcc)]
S_nonclone_owner = $fiber_put(S_fcc,pfiberstart_fcc.OBJECT,pfiber_nonclone_owner)
$heap_valid($heap_graph(S_nonclone_owner))
~$fiber_producer_valid(S_nonclone_owner,pfiber_nonclone_owner)
~$fiber_cache_valid(S_nonclone_owner,pfiberstart_fcc.OBJECT,pfiber_nonclone_owner)
~$call_descriptors_valid(S_nonclone_owner)
pshutdownproducer_both_fields = pshutdownproducer_fcc[.CLONE = (pcloneproducer_fcc[.NAME = ($ptascii("clone"))])]
~$consumer_clone_producer_valid(S_history_fcc,pshutdownproducer_both_fields)
pfiber_both_fields = pfiber_fcc[.PRODUCER = (pshutdownproducer_both_fields)][.CAPTURE = (pmethodcapture_fcc)]
S_both_fields = $fiber_put(S_fcc,pfiberstart_fcc.OBJECT,pfiber_both_fields)
$heap_valid($heap_graph(S_both_fields))
~$fiber_producer_valid(S_both_fields,pfiber_both_fields)
~$fiber_cache_valid(S_both_fields,pfiberstart_fcc.OBJECT,pfiber_both_fields)
~$call_descriptors_valid(S_both_fields)
S_manual_found = $clone_updates_review_seek(S_initial_manual,16,2048)
S_manual_found.COMPLETION = NORMAL \/ S_manual_found.COMPLETION = BUDGET
S_manual = S_manual_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_manual,16)
S_manual.CURRENT = eps
S_manual.FRAMES = eps
S_manual.CLONES = eps
$call_descriptors_valid(S_manual)
$heap_valid($heap_graph(S_manual))
S_manual.TODO = (FIBER_ARGS pfiberstart_manual) :: ptask_manual_tail*
$fiber_at(S_manual,pfiberstart_manual.OBJECT) = (pfiber_manual)
pfiber_manual.STATUS = FIBER_INIT
pfiber_manual.READY
pfiber_manual.PRODUCER = (pshutdownproducer_manual)
pfiber_manual.CAPTURE = (pmethodcapture_manual)
$fiber_producer_valid(S_manual,pfiber_manual)
$fiber_cache_valid(S_manual,pfiberstart_manual.OBJECT,pfiber_manual)
S_history_manual = $consumer_producer_history(S_manual,pshutdownproducer_manual)
pshutdownproducer_manual.TARGET = METHOD_TARGET n_maker_manual porigin_method_manual
~((HOBJECT n_maker_manual) <- S_manual.ALLOCATIONS)
~((HOBJECT n_maker_manual) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
~pshutdownproducer_manual.INTERNAL
pshutdownproducer_manual.CLONE = eps
$lookup(S_manual.ENV,$ptascii("cloner")) = (n_cloner_manual)
S_manual.STORE[n_cloner_manual] = DEFINED (POBJECT n_selector_manual)
(HOBJECT n_selector_manual) <- S_manual.ALLOCATIONS
S_manual.OBJECTS[n_selector_manual] = INTRINSICCLOSURE INTRINSIC_CLONE
pshutdownproducer_manual.SITE = (porigin_manual)
$exit_method_site(S_manual,porigin_manual)
~$consumer_clone_method_site(S_manual,porigin_manual)
pcloneproducer_manual = {SITE porigin_manual, NAME eps, CLOSURE (n_selector_manual)}
~$consumer_clone_selection_valid(S_history_manual,pcloneproducer_manual)
pshutdownproducer_manual_flip = pshutdownproducer_manual[.INTERNAL = true]
~$consumer_clone_producer_valid(S_history_manual,pshutdownproducer_manual_flip)
pfiber_manual_flip = pfiber_manual[.PRODUCER = (pshutdownproducer_manual_flip)][.CAPTURE = (pmethodcapture_manual)]
S_manual_flip = $fiber_put(S_manual,pfiberstart_manual.OBJECT,pfiber_manual_flip)
$heap_valid($heap_graph(S_manual_flip))
~$fiber_producer_valid(S_manual_flip,pfiber_manual_flip)
~$fiber_cache_valid(S_manual_flip,pfiberstart_manual.OBJECT,pfiber_manual_flip)
~$call_descriptors_valid(S_manual_flip)
pshutdownproducer_manual_fcc_forge = pshutdownproducer_manual[.INTERNAL = true][.CLONE = (pcloneproducer_manual)]
~$consumer_clone_producer_valid(S_history_manual,pshutdownproducer_manual_fcc_forge)
pfiber_manual_fcc_forge = pfiber_manual[.PRODUCER = (pshutdownproducer_manual_fcc_forge)][.CAPTURE = (pmethodcapture_manual)]
S_manual_fcc_forge = $fiber_put(S_manual,pfiberstart_manual.OBJECT,pfiber_manual_fcc_forge)
$heap_valid($heap_graph(S_manual_fcc_forge))
~$fiber_producer_valid(S_manual_fcc_forge,pfiber_manual_fcc_forge)
~$fiber_cache_valid(S_manual_fcc_forge,pfiberstart_manual.OBJECT,pfiber_manual_fcc_forge)
~$call_descriptors_valid(S_manual_fcc_forge)
pshutdownproducer_manual_false_receipt = pshutdownproducer_manual[.CLONE = (pcloneproducer_manual)]
~$consumer_clone_producer_valid(S_history_manual,pshutdownproducer_manual_false_receipt)
pfiber_manual_false_receipt = pfiber_manual[.PRODUCER = (pshutdownproducer_manual_false_receipt)][.CAPTURE = (pmethodcapture_manual)]
S_manual_false_receipt = $fiber_put(S_manual,pfiberstart_manual.OBJECT,pfiber_manual_false_receipt)
$heap_valid($heap_graph(S_manual_false_receipt))
~$fiber_producer_valid(S_manual_false_receipt,pfiber_manual_false_receipt)
~$fiber_cache_valid(S_manual_false_receipt,pfiberstart_manual.OBJECT,pfiber_manual_false_receipt)
~$call_descriptors_valid(S_manual_false_receipt)
~$consumer_producer_snapshot(pshutdownproducer_manual_false_receipt)
S_dyn.CLONEMAKERS = [pclonemaker_dyn]
pclonemaker_dyn.OBJECT = n_maker_dyn
pclonemaker_dyn.SELECTION = pcloneproducer_dyn
$clone_maker_at(S_dyn.CLONEMAKERS,n_maker_dyn) = (pcloneproducer_dyn)
$clone_makers_valid(S_dyn,S_dyn.CLONEMAKERS,eps)
S_fcc.CLONEMAKERS = [pclonemaker_fcc]
pclonemaker_fcc.OBJECT = n_maker_fcc
pclonemaker_fcc.SELECTION = pcloneproducer_fcc
$clone_maker_at(S_fcc.CLONEMAKERS,n_maker_fcc) = (pcloneproducer_fcc)
$clone_makers_valid(S_fcc,S_fcc.CLONEMAKERS,eps)
pfiber_dyn.CALL = (pconfigcall_dyn)
pclonemaker_dyn.CONSUMERS = [pcloneconsumer_dyn]
pcloneconsumer_dyn.KIND = INTRINSIC_FIBER_CONSTRUCT
pcloneconsumer_dyn.ID = pfiberstart_dyn.OBJECT
pcloneconsumer_dyn.SITE = pconfigcall_dyn.SITE
$consumer_clone_birth_valid(S_dyn,pconfigcall_dyn,pconfigcall_dyn.OWNER,pfiber_dyn.PRODUCER)
pfiber_fcc.CALL = (pconfigcall_fcc)
pclonemaker_fcc.CONSUMERS = [pcloneconsumer_fcc]
pcloneconsumer_fcc.KIND = INTRINSIC_FIBER_CONSTRUCT
pcloneconsumer_fcc.ID = pfiberstart_fcc.OBJECT
pcloneconsumer_fcc.SITE = pconfigcall_fcc.SITE
$consumer_clone_birth_valid(S_fcc,pconfigcall_fcc,pconfigcall_fcc.OWNER,pfiber_fcc.PRODUCER)
~$consumer_clone_birth_valid(S_dyn,pconfigcall_dyn,pconfigcall_dyn.OWNER,(pshutdownproducer_hidden_role))
S_missing_birth = S_dyn[.CLONEMAKERS = [pclonemaker_dyn[.CONSUMERS = eps]]]
$heap_valid($heap_graph(S_missing_birth))
$clone_makers_valid(S_missing_birth,S_missing_birth.CLONEMAKERS,eps)
~$consumer_clone_birth_valid(S_missing_birth,pconfigcall_dyn,pconfigcall_dyn.OWNER,pfiber_dyn.PRODUCER)
~$fiber_producer_valid(S_missing_birth,pfiber_dyn)
~$fiber_cache_valid(S_missing_birth,pfiberstart_dyn.OBJECT,pfiber_dyn)
~$call_descriptors_valid(S_missing_birth)
S_bad_birth_kind = S_dyn[.CLONEMAKERS = [pclonemaker_dyn[.CONSUMERS = [pcloneconsumer_dyn[.KIND = INTRINSIC_AUTO_REGISTER]]]]]
$heap_valid($heap_graph(S_bad_birth_kind))
~$clone_makers_valid(S_bad_birth_kind,S_bad_birth_kind.CLONEMAKERS,eps)
~$fiber_cache_valid(S_bad_birth_kind,pfiberstart_dyn.OBJECT,pfiber_dyn)
~$call_descriptors_valid(S_bad_birth_kind)
S_duplicate_birth = S_dyn[.CLONEMAKERS = [pclonemaker_dyn[.CONSUMERS = [pcloneconsumer_dyn,pcloneconsumer_dyn]]]]
$heap_valid($heap_graph(S_duplicate_birth))
~$clone_consumer_keys_unique($clone_consumer_keys(S_duplicate_birth.CLONEMAKERS),eps)
~$call_descriptors_valid(S_duplicate_birth)
S_manual.CLONEMAKERS = eps
$clone_maker_at(S_manual.CLONEMAKERS,n_maker_manual) = eps
$clone_makers_valid(S_manual,S_manual.CLONEMAKERS,eps)
S_missing_history = S_dyn[.CLONEMAKERS = eps]
S_history_missing_history = $consumer_producer_history(S_missing_history,pshutdownproducer_dyn)
$clone_makers_valid(S_missing_history,S_missing_history.CLONEMAKERS,eps)
$heap_valid($heap_graph(S_missing_history))
~$consumer_clone_producer_valid(S_history_missing_history,pshutdownproducer_dyn)
~$fiber_producer_valid(S_missing_history,pfiber_dyn)
~$fiber_cache_valid(S_missing_history,pfiberstart_dyn.OBJECT,pfiber_dyn)
~$call_descriptors_valid(S_missing_history)
S_dyn.OBJECTS[0] = S_dyn.OBJECTS[n_maker_dyn]
0 =/= n_maker_dyn
pclonemaker_wrong_physical = pclonemaker_dyn[.OBJECT = 0]
S_wrong_physical = S_dyn[.CLONEMAKERS = [pclonemaker_wrong_physical]]
S_history_wrong_physical = $consumer_producer_history(S_wrong_physical,pshutdownproducer_dyn)
$clone_makers_valid(S_wrong_physical,S_wrong_physical.CLONEMAKERS,eps)
$heap_valid($heap_graph(S_wrong_physical))
~$consumer_clone_producer_valid(S_history_wrong_physical,pshutdownproducer_dyn)
~$fiber_producer_valid(S_wrong_physical,pfiber_dyn)
~$fiber_cache_valid(S_wrong_physical,pfiberstart_dyn.OBJECT,pfiber_dyn)
~$call_descriptors_valid(S_wrong_physical)
pclonemaker_changed_history = pclonemaker_dyn[.SELECTION.NAME = ($ptascii("unrelated"))]
S_changed_history = S_dyn[.CLONEMAKERS = [pclonemaker_changed_history]]
S_history_changed_history = $consumer_producer_history(S_changed_history,pshutdownproducer_dyn)
~$clone_makers_valid(S_changed_history,S_changed_history.CLONEMAKERS,eps)
$heap_valid($heap_graph(S_changed_history))
~$consumer_clone_producer_valid(S_history_changed_history,pshutdownproducer_dyn)
~$fiber_producer_valid(S_changed_history,pfiber_dyn)
~$fiber_cache_valid(S_changed_history,pfiberstart_dyn.OBJECT,pfiber_dyn)
~$call_descriptors_valid(S_changed_history)
S_duplicate_history = S_dyn[.CLONEMAKERS = [pclonemaker_dyn,pclonemaker_dyn]]
$heap_valid($heap_graph(S_duplicate_history))
~$clone_makers_valid(S_duplicate_history,S_duplicate_history.CLONEMAKERS,eps)
~$clone_windows_valid(S_duplicate_history)
~$call_descriptors_valid(S_duplicate_history)
S_done_dyn = $drive_steps(S_dyn,2048)
S_done_dyn.COMPLETION = NORMAL /\ S_done_dyn.TODO = eps /\ S_done_dyn.CURRENT = eps /\ S_done_dyn.FRAMES = eps
$clone_updates_review_output(S_done_dyn.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_dyn)
$heap_valid($heap_graph(S_done_dyn))
S_done_fcc = $drive_steps(S_fcc,2048)
S_done_fcc.COMPLETION = NORMAL /\ S_done_fcc.TODO = eps /\ S_done_fcc.CURRENT = eps /\ S_done_fcc.FRAMES = eps
$clone_updates_review_output(S_done_fcc.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_fcc)
$heap_valid($heap_graph(S_done_fcc))
S_done_manual = $drive_steps(S_manual,2048)
S_done_manual.COMPLETION = NORMAL /\ S_done_manual.TODO = eps /\ S_done_manual.CURRENT = eps /\ S_done_manual.FRAMES = eps
$clone_updates_review_output(S_done_manual.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_manual)
$heap_valid($heap_graph(S_done_manual))
''',
    'computed-name-birth': r'''
S_manual_found = $clone_updates_review_seek(S_initial_manual,16,2048)
S_manual_found.COMPLETION = NORMAL \/ S_manual_found.COMPLETION = BUDGET
S_manual = S_manual_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_manual,16)
S_manual.CURRENT = eps
S_manual.FRAMES = eps
S_manual.CLONES = eps
$call_descriptors_valid(S_manual)
$heap_valid($heap_graph(S_manual))
S_manual.TODO = (FIBER_ARGS pfiberstart_manual) :: ptask_manual_tail*
$fiber_at(S_manual,pfiberstart_manual.OBJECT) = (pfiber_manual)
pfiber_manual.STATUS = FIBER_INIT
pfiber_manual.READY
pfiber_manual.PRODUCER = (pshutdownproducer_manual)
pfiber_manual.CAPTURE = (pmethodcapture_manual)
$fiber_producer_valid(S_manual,pfiber_manual)
$fiber_cache_valid(S_manual,pfiberstart_manual.OBJECT,pfiber_manual)
S_history_manual = $consumer_producer_history(S_manual,pshutdownproducer_manual)
pshutdownproducer_manual.TARGET = METHOD_TARGET n_maker_manual porigin_method_manual
~((HOBJECT n_maker_manual) <- S_manual.ALLOCATIONS)
~((HOBJECT n_maker_manual) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
~pshutdownproducer_manual.INTERNAL
pshutdownproducer_manual.CLONE = eps
S_manual.CLONEMAKERS = eps
$clone_maker_at(S_manual.CLONEMAKERS,n_maker_manual) = eps
$clone_makers_valid(S_manual,S_manual.CLONEMAKERS,eps)
$lookup(S_manual.ENV,$ptascii("cloner")) = (n_cloner_manual)
S_manual.STORE[n_cloner_manual] = DEFINED (POBJECT n_selector_manual)
(HOBJECT n_selector_manual) <- S_manual.ALLOCATIONS
S_manual.OBJECTS[n_selector_manual] = INTRINSICCLOSURE INTRINSIC_CLONE
$lookup(S_manual.ENV,$ptascii("method")) = (n_method_manual)
S_manual.STORE[n_method_manual] = DEFINED (PSTRING $ptascii("unrelated"))
pshutdownproducer_manual.SITE = (porigin_manual)
$consumer_clone_method_site(S_manual,porigin_manual)
pcloneproducer_manual = {SITE porigin_manual, NAME eps, CLOSURE (n_selector_manual)}
$consumer_clone_selection_valid(S_history_manual,pcloneproducer_manual)
pfiber_manual.CALL = (pconfigcall_manual)
$consumer_clone_birth_valid(S_manual,pconfigcall_manual,pconfigcall_manual.OWNER,pfiber_manual.PRODUCER)
pshutdownproducer_manual_unknown_forge = pshutdownproducer_manual[.INTERNAL = true][.CLONE = (pcloneproducer_manual)]
~$consumer_clone_producer_valid(S_history_manual,pshutdownproducer_manual_unknown_forge)
pfiber_manual_unknown_forge = pfiber_manual[.PRODUCER = (pshutdownproducer_manual_unknown_forge)][.CAPTURE = (pmethodcapture_manual)]
S_manual_unknown_forge = $fiber_put(S_manual,pfiberstart_manual.OBJECT,pfiber_manual_unknown_forge)
$heap_valid($heap_graph(S_manual_unknown_forge))
~$fiber_producer_valid(S_manual_unknown_forge,pfiber_manual_unknown_forge)
~$fiber_cache_valid(S_manual_unknown_forge,pfiberstart_manual.OBJECT,pfiber_manual_unknown_forge)
~$call_descriptors_valid(S_manual_unknown_forge)
~$consumer_clone_birth_valid(S_manual,pconfigcall_manual,pconfigcall_manual.OWNER,(pshutdownproducer_manual_unknown_forge))
S_done_manual = $drive_steps(S_manual,2048)
S_done_manual.COMPLETION = NORMAL /\ S_done_manual.TODO = eps /\ S_done_manual.CURRENT = eps /\ S_done_manual.FRAMES = eps
$clone_updates_review_output(S_done_manual.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_manual)
$heap_valid($heap_graph(S_done_manual))
''',
    'reused-maker-birth': r'''
S_manual_found = $clone_updates_review_seek(S_initial_manual,16,2048)
S_manual_found.COMPLETION = NORMAL \/ S_manual_found.COMPLETION = BUDGET
S_manual = S_manual_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_manual,16)
S_manual.CURRENT = eps
S_manual.FRAMES = eps
S_manual.CLONES = eps
$call_descriptors_valid(S_manual)
$heap_valid($heap_graph(S_manual))
S_manual.TODO = (FIBER_ARGS pfiberstart_manual) :: ptask_manual_tail*
$fiber_at(S_manual,pfiberstart_manual.OBJECT) = (pfiber_manual)
pfiber_manual.STATUS = FIBER_INIT
pfiber_manual.READY
pfiber_manual.PRODUCER = (pshutdownproducer_manual)
pfiber_manual.CAPTURE = (pmethodcapture_manual)
$fiber_producer_valid(S_manual,pfiber_manual)
$fiber_cache_valid(S_manual,pfiberstart_manual.OBJECT,pfiber_manual)
S_history_manual = $consumer_producer_history(S_manual,pshutdownproducer_manual)
pshutdownproducer_manual.TARGET = METHOD_TARGET n_maker_manual porigin_method_manual
~((HOBJECT n_maker_manual) <- S_manual.ALLOCATIONS)
~((HOBJECT n_maker_manual) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
~pshutdownproducer_manual.INTERNAL
pshutdownproducer_manual.CLONE = eps
S_manual.CLONEMAKERS = [pclonemaker_retained]
pclonemaker_retained.OBJECT = n_maker_manual
pclonemaker_retained.SELECTION = pcloneproducer_retained
pshutdownproducer_manual.SITE = (pcloneproducer_retained.SITE)
pcloneproducer_retained.NAME = eps
pcloneproducer_retained.CLOSURE = (n_selector_retained)
$(n_selector_retained < |S_manual.OBJECTS|)
S_manual.OBJECTS[n_selector_retained] = INTRINSICCLOSURE INTRINSIC_CLONE
~((HOBJECT n_selector_retained) <- S_manual.ALLOCATIONS)
~((HOBJECT n_selector_retained) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
$clone_maker_at(S_manual.CLONEMAKERS,n_maker_manual) = (pcloneproducer_retained)
$clone_makers_valid(S_manual,S_manual.CLONEMAKERS,eps)
$consumer_clone_selection_valid(S_history_manual,pcloneproducer_retained)
~$consumer_clone_producer_valid(S_history_manual,pshutdownproducer_manual)
pfiber_manual.CALL = (pconfigcall_manual)
$consumer_clone_birth_valid(S_manual,pconfigcall_manual,pconfigcall_manual.OWNER,pfiber_manual.PRODUCER)
pclonemaker_retained.CONSUMERS = [pcloneconsumer_old]
pcloneconsumer_old.KIND = INTRINSIC_FIBER_CONSTRUCT
pcloneconsumer_old.ID =/= pfiberstart_manual.OBJECT
S_manual.OBJECTS[pcloneconsumer_old.ID] = FIBER pfiber_old
~((HOBJECT pcloneconsumer_old.ID) <- S_manual.ALLOCATIONS)
~((HOBJECT pcloneconsumer_old.ID) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
$clone_consumer_maker_at(S_manual.CLONEMAKERS,INTRINSIC_FIBER_CONSTRUCT,pfiberstart_manual.OBJECT) = eps
$clone_consumer_maker_at(S_manual.CLONEMAKERS,INTRINSIC_FIBER_CONSTRUCT,pcloneconsumer_old.ID) = (pclonemaker_retained)
pshutdownproducer_retained_forge = pshutdownproducer_manual[.INTERNAL = true][.CLONE = (pcloneproducer_retained)]
$consumer_clone_producer_valid(S_history_manual,pshutdownproducer_retained_forge)
~$consumer_clone_birth_valid(S_history_manual,pconfigcall_manual,pconfigcall_manual.OWNER,(pshutdownproducer_retained_forge))
pfiber_retained_forge = pfiber_manual[.PRODUCER = (pshutdownproducer_retained_forge)][.CAPTURE = (pmethodcapture_manual)]
S_retained_forge = $fiber_put(S_manual,pfiberstart_manual.OBJECT,pfiber_retained_forge)
$heap_valid($heap_graph(S_retained_forge))
~$fiber_producer_valid(S_retained_forge,pfiber_retained_forge)
~$fiber_cache_valid(S_retained_forge,pfiberstart_manual.OBJECT,pfiber_retained_forge)
~$call_descriptors_valid(S_retained_forge)
S_done_manual = $drive_steps(S_manual,2048)
S_done_manual.COMPLETION = NORMAL /\ S_done_manual.TODO = eps /\ S_done_manual.CURRENT = eps /\ S_done_manual.FRAMES = eps
$clone_updates_review_output(S_done_manual.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_manual)
$heap_valid($heap_graph(S_done_manual))
''',
    'private-manual-birth-positive': r'''
S_manual_found = $clone_updates_review_seek(S_initial_manual,16,2048)
S_manual_found.COMPLETION = NORMAL \/ S_manual_found.COMPLETION = BUDGET
S_manual = S_manual_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_manual,16)
S_manual.CURRENT = eps
S_manual.FRAMES = eps
S_manual.CLONES = eps
$call_descriptors_valid(S_manual)
$heap_valid($heap_graph(S_manual))
S_manual.TODO = (FIBER_ARGS pfiberstart_manual) :: ptask_manual_tail*
$fiber_at(S_manual,pfiberstart_manual.OBJECT) = (pfiber_manual)
pfiber_manual.STATUS = FIBER_INIT
pfiber_manual.READY
pfiber_manual.PRODUCER = (pshutdownproducer_manual)
pfiber_manual.CAPTURE = (pmethodcapture_manual)
$fiber_producer_valid(S_manual,pfiber_manual)
$fiber_cache_valid(S_manual,pfiberstart_manual.OBJECT,pfiber_manual)
S_history_manual = $consumer_producer_history(S_manual,pshutdownproducer_manual)
pshutdownproducer_manual.TARGET = METHOD_TARGET n_maker_manual porigin_method_manual
~((HOBJECT n_maker_manual) <- S_manual.ALLOCATIONS)
~((HOBJECT n_maker_manual) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
~pshutdownproducer_manual.INTERNAL
pshutdownproducer_manual.CLONE = eps
S_manual.CLONEMAKERS = eps
$clone_method(S_history_manual,n_maker_manual) = (pmethoddesc_private)
pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE
pmethoddesc_private.NAME = $ptascii("__clone")
pshutdownproducer_manual.SITE = (porigin_private)
$method_site_scope(S_history_manual,pmethoddesc_private.FUNCTION.ORIGIN,porigin_private) = eps
~$method_accessible(S_history_manual,pmethoddesc_private,eps)
~$method_call_selected(S_history_manual,pshutdownproducer_manual.TARGET,pshutdownproducer_manual.SITE)
pfiber_manual.CALL = (pconfigcall_private)
$consumer_capture_valid(S_manual,pconfigcall_private.SITE,(pmethodcapture_manual))
$consumer_producer_ordinary_at(S_history_manual,pshutdownproducer_manual)
pfiber_manual.CALL = (pconfigcall_manual)
$consumer_clone_birth_valid(S_manual,pconfigcall_manual,pconfigcall_manual.OWNER,pfiber_manual.PRODUCER)
S_done_manual = $drive_steps(S_manual,2048)
S_done_manual.COMPLETION = NORMAL /\ S_done_manual.TODO = eps /\ S_done_manual.CURRENT = eps /\ S_done_manual.FRAMES = eps
$clone_updates_review_output(S_done_manual.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_manual)
$heap_valid($heap_graph(S_done_manual))
''',
    'shared-origin-positive': r'''
S_manual_found = $clone_updates_review_seek(S_initial_manual,16,2048)
S_manual_found.COMPLETION = NORMAL \/ S_manual_found.COMPLETION = BUDGET
S_manual = S_manual_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_manual,16)
S_manual.CURRENT = eps
S_manual.FRAMES = eps
S_manual.CLONES = eps
$call_descriptors_valid(S_manual)
$heap_valid($heap_graph(S_manual))
S_manual.TODO = (FIBER_ARGS pfiberstart_manual) :: ptask_manual_tail*
$fiber_at(S_manual,pfiberstart_manual.OBJECT) = (pfiber_manual)
pfiber_manual.STATUS = FIBER_INIT
pfiber_manual.READY
pfiber_manual.PRODUCER = (pshutdownproducer_manual)
pfiber_manual.CAPTURE = (pmethodcapture_manual)
$fiber_producer_valid(S_manual,pfiber_manual)
$fiber_cache_valid(S_manual,pfiberstart_manual.OBJECT,pfiber_manual)
S_history_manual = $consumer_producer_history(S_manual,pshutdownproducer_manual)
pshutdownproducer_manual.TARGET = METHOD_TARGET n_maker_manual porigin_method_manual
~((HOBJECT n_maker_manual) <- S_manual.ALLOCATIONS)
~((HOBJECT n_maker_manual) <- $node_children(S_manual,HOBJECT pfiberstart_manual.OBJECT))
~pshutdownproducer_manual.INTERNAL
pshutdownproducer_manual.CLONE = eps
S_manual.CLONEMAKERS = eps
pfiber_manual.CALL = (pconfigcall_manual)
$consumer_clone_birth_valid(S_manual,pconfigcall_manual,pconfigcall_manual.OWNER,pfiber_manual.PRODUCER)
$consumer_clone_function_site(S_manual,pshutdownproducer_manual.SITE)
$clone_method(S_manual,n_maker_manual) = (pmethoddesc_clone)
$object_invoke_method(S_history_manual,n_maker_manual) = (pmethoddesc_invoke)
pmethoddesc_clone.FUNCTION.ORIGIN =/= porigin_method_manual
$origin_source(pmethoddesc_clone.FUNCTION.ORIGIN) = $origin_source(porigin_method_manual)
pmethoddesc_clone.FUNCTION.CODE = pmethoddesc_invoke.FUNCTION.CODE
pmethoddesc_clone.FUNCTION.BODY = pmethoddesc_invoke.FUNCTION.BODY
pmethoddesc_invoke.FUNCTION.ORIGIN = porigin_method_manual
$consumer_clone_object_call(S_history_manual,n_maker_manual,porigin_method_manual)
$consumer_producer_ordinary_at(S_history_manual,pshutdownproducer_manual)
S_done_manual = $drive_steps(S_manual,2048)
S_done_manual.COMPLETION = NORMAL /\ S_done_manual.TODO = eps /\ S_done_manual.CURRENT = eps /\ S_done_manual.FRAMES = eps
$clone_updates_review_output(S_done_manual.EVENTS) = $ptascii("private|done")
$call_descriptors_valid(S_done_manual)
$heap_valid($heap_graph(S_done_manual))
''',
    'autoload-birth': r'''
S_current_found = $clone_updates_review_seek(S_initial_manual,17,2048)
S_current_found.COMPLETION = NORMAL \/ S_current_found.COMPLETION = BUDGET
S_current = S_current_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_current,17)
$call_descriptors_valid(S_current)
$heap_valid($heap_graph(S_current))
S_current.CURRENT = eps
S_current.FRAMES = eps
S_current.CLONES = eps
S_current.AUTOSEQ = 4
|S_current.AUTOLOAD.ENTRIES| = 1
S_current.AUTOLOAD.ENTRIES[0] = (pautoloadentry_current)
|S_current.AUTOLOAD.BIRTHS| = 1
S_current.AUTOLOAD.BIRTHS[0] = (3)
pautoloadentry_current.BIRTH = (3)
pautoloadentry_current.CALL.KIND = INTRINSIC_AUTO_REGISTER
pautoloadentry_current.PRODUCER = (pshutdownproducer_current)
~pshutdownproducer_current.INTERNAL
pshutdownproducer_current.CLONE = eps
S_current.CLONEMAKERS = [pclonemaker_old]
pclonemaker_old.CONSUMERS = [pcloneconsumer_old]
pcloneconsumer_old.KIND = INTRINSIC_AUTO_REGISTER
pcloneconsumer_old.ID = 0
pcloneconsumer_old.SITE = pautoloadentry_current.CALL.SITE
pshutdownproducer_current.TARGET = METHOD_TARGET pclonemaker_old.OBJECT porigin_method
pshutdownproducer_current.SITE = (pclonemaker_old.SELECTION.SITE)
~((HOBJECT pclonemaker_old.OBJECT) <- S_current.ALLOCATIONS)
pclonemaker_old.SELECTION.CLOSURE = (n_selector)
S_current.OBJECTS[n_selector] = INTRINSICCLOSURE INTRINSIC_CLONE
~((HOBJECT n_selector) <- S_current.ALLOCATIONS)
$consumer_clone_birth_valid(S_current,pautoloadentry_current.CALL,pautoloadentry_current.BIRTH,pautoloadentry_current.PRODUCER)
$autoload_births_match(S_current.AUTOLOAD.ENTRIES,S_current.AUTOLOAD.BIRTHS)
$autoload_entry_valid(S_current,pautoloadentry_current)
$autoload_registry_valid(S_current)
S_history = $consumer_producer_history(S_current,pshutdownproducer_current)
pshutdownproducer_forge = pshutdownproducer_current[.INTERNAL = true][.CLONE = (pclonemaker_old.SELECTION)]
$consumer_clone_producer_valid(S_history,pshutdownproducer_forge)
~$consumer_clone_birth_valid(S_current,pautoloadentry_current.CALL,pautoloadentry_current.BIRTH,(pshutdownproducer_forge))
pautoloadentry_forge = pautoloadentry_current[.PRODUCER = (pshutdownproducer_forge)]
S_producer_forge = S_current[.AUTOLOAD.ENTRIES = [$autoload_bucket(pautoloadentry_forge)]]
$heap_valid($heap_graph(S_producer_forge))
~$autoload_entry_valid(S_producer_forge,pautoloadentry_forge)
~$autoload_registry_valid(S_producer_forge)
~$call_descriptors_valid(S_producer_forge)
pautoloadentry_oldid = pautoloadentry_forge[.BIRTH = (pcloneconsumer_old.ID)]
$consumer_clone_birth_valid(S_current,pautoloadentry_oldid.CALL,pautoloadentry_oldid.BIRTH,pautoloadentry_oldid.PRODUCER)
$autoload_entry_valid(S_current,pautoloadentry_oldid)
S_registry_forge = S_current[.AUTOLOAD.ENTRIES = [$autoload_bucket(pautoloadentry_oldid)]]
$heap_valid($heap_graph(S_registry_forge))
~$autoload_births_match(S_registry_forge.AUTOLOAD.ENTRIES,S_registry_forge.AUTOLOAD.BIRTHS)
~$autoload_registry_valid(S_registry_forge)
~$call_descriptors_valid(S_registry_forge)
S_retired_found = $clone_updates_review_seek(S_current,18,2048)
S_retired_found.COMPLETION = NORMAL \/ S_retired_found.COMPLETION = BUDGET
S_retired = S_retired_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S_retired,18)
$call_descriptors_valid(S_retired)
$heap_valid($heap_graph(S_retired))
S_retired.CURRENT = (pcallcontext_loader)
S_retired.FRAMES = pframe_loader :: pframe_tail*
pframe_loader.TODO = (AUTO_RESULT pautoloadcall_selected pautoloadentry_selected poperand_selected) :: ptask_tail*
S_retired_scope = $constant_frame_scope(S_retired,pframe_loader,pframe_tail*)
S_retired.AUTOLOAD.ENTRIES = eps
S_retired.AUTOLOAD.BIRTHS = eps
pautoloadcall_selected.BIRTH = (3)
pautoloadentry_selected.BIRTH = (3)
$autoload_entry_valid(S_retired,pautoloadentry_selected)
$autoload_selected_valid(S_retired_scope,pautoloadcall_selected,pautoloadentry_selected)
$autoload_context_valid(S_retired,pcallcontext_loader)
pautoloadentry_selected = pautoloadentry_current
$autoload_entry_valid(S_retired,pautoloadentry_oldid)
~$autoload_selected_valid(S_retired_scope,pautoloadcall_selected,pautoloadentry_oldid)
pframe_forge = pframe_loader[.TODO = (AUTO_RESULT pautoloadcall_selected pautoloadentry_oldid poperand_selected) :: ptask_tail*]
S_selected_forge = S_retired[.FRAMES = pframe_forge :: pframe_tail*]
$heap_valid($heap_graph(S_selected_forge))
~$call_descriptors_valid(S_selected_forge)
$declaration_autoload_invocation(S_retired,pautoloadcall_selected,pautoloadentry_selected,pcallcontext_loader.FUNCTION,pcallcontext_loader.CALLSITE,pcallcontext_loader.LEXICAL_CLASS,pcallcontext_loader.CALLED_CLASS)
~$declaration_autoload_invocation(S_retired,pautoloadcall_selected,pautoloadentry_oldid,pcallcontext_loader.FUNCTION,pcallcontext_loader.CALLSITE,pcallcontext_loader.LEXICAL_CLASS,pcallcontext_loader.CALLED_CLASS)
S_done = $drive_steps(S_retired,2048)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
$clone_updates_review_output(S_done.EVENTS) = $ptascii("Later|done")
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
$declaration_history_valid(S_done)
n_declaration = $nabs($(|S_done.DECLARATIONS| - 1))
S_done.DECLARATIONS[n_declaration] = PDRCLASS porigin_later pdeclcause_later
$class_named(S_done.CLASSNAMES,$ptascii("later")) = (porigin_later)
pdeclcause_later.AUTOLOAD = [(n_depth,pautoloadcall_cause,pautoloadentry_cause)]
pautoloadcall_cause.BIRTH = (3)
pautoloadentry_cause.BIRTH = (3)
pdeclcause_later.CALLS[n_depth] = (porigin_loader,porigin_site?,porigin_lexical?,porigin_called?)
pdeclcause_forge = pdeclcause_later[.AUTOLOAD = [(n_depth,pautoloadcall_cause,pautoloadentry_oldid)]]
S_cause_forge = S_done[.DECLARATIONS = S_done.DECLARATIONS[0:n_declaration] ++ [PDRCLASS porigin_later pdeclcause_forge]]
$heap_valid($heap_graph(S_cause_forge))
~$declaration_autoload_invocation(S_cause_forge,pautoloadcall_cause,pautoloadentry_oldid,porigin_loader,porigin_site?,porigin_lexical?,porigin_called?)
~$declaration_history_valid(S_cause_forge)
~$call_descriptors_valid(S_cause_forge)
''',
    'keyword-shutdown-birth': r'''
S_initial_shutdown.COMPLETION = BUDGET
S_done = $drive_steps(S_initial_shutdown[.COMPLETION = NORMAL],2048)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done.CLONES = eps
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.SILENCES = eps
S_done.REPORTING = 30719
S_done.SHUTDOWN.INDEX = 1
$clone_updates_review_output(S_done.EVENTS) = $ptascii("done|private|")
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.SHUTDOWN.ENTRIES = [pshutdownentry_shutdown]
pshutdownentry_shutdown.BIRTH = (0)
pshutdownentry_shutdown.CALL.KIND = INTRINSIC_REGISTER_SHUTDOWN_FUNCTION
pshutdownentry_shutdown.PRODUCER = (pshutdownproducer_shutdown)
pshutdownentry_shutdown.TARGET = API_METHOD_TARGET papiquery_shutdown porigin_callback ptbytes_callback b_static
pshutdownproducer_shutdown.INTERNAL
pshutdownproducer_shutdown.CLONE = (pcloneproducer_shutdown)
pshutdownproducer_shutdown.TARGET = METHOD_TARGET n_maker porigin_method
S_done.CLONEMAKERS = [pclonemaker_shutdown]
pclonemaker_shutdown.OBJECT = n_maker
pclonemaker_shutdown.SELECTION = pcloneproducer_shutdown
pcloneproducer_shutdown.NAME = ($ptascii("clone"))
pcloneproducer_shutdown.CLOSURE = eps
pclonemaker_shutdown.CONSUMERS = [pcloneconsumer_shutdown]
pcloneconsumer_shutdown.KIND = INTRINSIC_REGISTER_SHUTDOWN_FUNCTION
pcloneconsumer_shutdown.ID = 0
pcloneconsumer_shutdown.SITE = pshutdownentry_shutdown.CALL.SITE
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- $shutdown_roots(S_done.SHUTDOWN.ENTRIES))
$lookup(S_done.ENV,$ptascii("cloner")) = (n_cloner_cell)
S_done.STORE[n_cloner_cell] = DEFINED (PSTRING $ptascii("unrelated"))
$consumer_clone_birth_valid(S_done,pshutdownentry_shutdown.CALL,pshutdownentry_shutdown.BIRTH,pshutdownentry_shutdown.PRODUCER)
$consumer_producer_capture(S_done,pshutdownentry_shutdown)
$shutdown_entry_valid(S_done,pshutdownentry_shutdown)
$clone_shutdown_births_valid(S_done,S_done.SHUTDOWN.ENTRIES,0)
S_missing = S_done[.CLONEMAKERS = [pclonemaker_shutdown[.CONSUMERS = eps]]]
$heap_valid($heap_graph(S_missing))
~$consumer_clone_birth_valid(S_missing,pshutdownentry_shutdown.CALL,pshutdownentry_shutdown.BIRTH,pshutdownentry_shutdown.PRODUCER)
~$consumer_producer_capture(S_missing,pshutdownentry_shutdown)
~$call_descriptors_valid(S_missing)
pshutdownproducer_hidden = pshutdownproducer_shutdown[.INTERNAL = false][.CLONE = eps]
pshutdownentry_hidden = pshutdownentry_shutdown[.PRODUCER = (pshutdownproducer_hidden)]
S_hidden = S_done[.SHUTDOWN.ENTRIES = [pshutdownentry_hidden]]
$heap_valid($heap_graph(S_hidden))
~$consumer_clone_birth_valid(S_hidden,pshutdownentry_hidden.CALL,pshutdownentry_hidden.BIRTH,pshutdownentry_hidden.PRODUCER)
~$consumer_producer_capture(S_hidden,pshutdownentry_hidden)
~$call_descriptors_valid(S_hidden)
pshutdownentry_absent = pshutdownentry_shutdown[.BIRTH = eps]
S_absent = S_done[.SHUTDOWN.ENTRIES = [pshutdownentry_absent]]
$heap_valid($heap_graph(S_absent))
~$consumer_clone_birth_valid(S_absent,pshutdownentry_absent.CALL,pshutdownentry_absent.BIRTH,pshutdownentry_absent.PRODUCER)
~$clone_shutdown_births_valid(S_absent,S_absent.SHUTDOWN.ENTRIES,0)
~$call_descriptors_valid(S_absent)
pshutdownentry_wrong = pshutdownentry_shutdown[.BIRTH = (1)]
S_wrong = S_done[.SHUTDOWN.ENTRIES = [pshutdownentry_wrong]]
$heap_valid($heap_graph(S_wrong))
~$consumer_clone_birth_valid(S_wrong,pshutdownentry_wrong.CALL,pshutdownentry_wrong.BIRTH,pshutdownentry_wrong.PRODUCER)
~$clone_shutdown_births_valid(S_wrong,S_wrong.SHUTDOWN.ENTRIES,0)
~$call_descriptors_valid(S_wrong)
S_wrong_key = S_done[.CLONEMAKERS = [pclonemaker_shutdown[.CONSUMERS = [pcloneconsumer_shutdown[.ID = 1]]]]]
$heap_valid($heap_graph(S_wrong_key))
~$clone_makers_valid(S_wrong_key,S_wrong_key.CLONEMAKERS,eps)
~$consumer_clone_birth_valid(S_wrong_key,pshutdownentry_shutdown.CALL,pshutdownentry_shutdown.BIRTH,pshutdownentry_shutdown.PRODUCER)
~$call_descriptors_valid(S_wrong_key)
S_transplant = S_done[.SHUTDOWN.ENTRIES = [pshutdownentry_shutdown,pshutdownentry_shutdown]]
$heap_valid($heap_graph(S_transplant))
$consumer_producer_capture(S_transplant,pshutdownentry_shutdown)
~$clone_shutdown_births_valid(S_transplant,S_transplant.SHUTDOWN.ENTRIES,0)
~$call_descriptors_valid(S_transplant)
''',
    'closer-window': r'''
~S_initial_source.COMPILESTOP
S_found = $clone_updates_review_seek(S_initial_source,19,4096)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
$clone_updates_review_phase(S,19)
S.CLONES = [pclonewindow]
pclonewindow.PHASE = CLONE_CALLBACK
pcloneoperation = pclonewindow.OPERATION
pclonewindow.AVAILABLE = [$ptascii("x")]
$clone_written_revision(S.CLONES,pcloneoperation.TARGET,$ptascii("x")) = (0)
$location_slot(S,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("seed"))
S.FIBERCLOSERS = pfiberclose :: pfiberclose_tail*
pfiberclose.PREVIOUS = eps
pfiberclose.VM.CURRENT = (pcallcontext_clone)
pcallcontext_clone.TARGET = METHOD_TARGET pcloneoperation.TARGET porigin_method
pcallcontext_clone.CALLSITE = (pcloneoperation.SITE)
pfiberclose.VM.FRAMES = pframe_clone :: pframe_clone_tail*
pframe_clone.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_clone_tail*
S_vm = $fiber_vm_restore(S,pfiberclose.VM)
$clone_context_valid(S_vm,pcallcontext_clone)
S_source = $constant_frame_scope(S_vm,pframe_clone,pframe_clone_tail*)
$clone_operation_source_valid(S_source,pcloneoperation)
$clone_window_vm(pfiberclose.VM,pcloneoperation,CLONE_CALLBACK)
$clone_window_closers(S.FIBERCLOSERS,pcloneoperation,CLONE_CALLBACK)
~$clone_window_tasks(S.TODO,pcloneoperation,CLONE_CALLBACK)
~$clone_window_frames(S.FRAMES,pcloneoperation,CLONE_CALLBACK)
~$clone_window_fibers(S,S.ALLOCATIONS,pcloneoperation,CLONE_CALLBACK)
~$clone_window_callers(S.FIBERCALLERS,pcloneoperation,CLONE_CALLBACK)
$clone_window_live(S,pcloneoperation,CLONE_CALLBACK)
$clone_windows_valid(S)
$call_descriptors_valid(S)
$call_entry_check(S) = S
$heap_valid($heap_graph(S))
(HOBJECT pcloneoperation.TARGET) <- $fiber_vm_nodes(pfiberclose.VM)
pcloneoperation_bad = pcloneoperation[.LINE = $(pcloneoperation.LINE + 1)]
pframe_bad = pframe_clone[.TODO = (CLONE_CALLBACK_RESULT pcloneoperation_bad) :: ptask_clone_tail*]
pfiberclose_bad = pfiberclose[.VM.FRAMES = pframe_bad :: pframe_clone_tail*]
S_bad = S[.FIBERCLOSERS = pfiberclose_bad :: pfiberclose_tail*]
$heap_graph(S_bad) = $heap_graph(S)
~$clone_window_vm(pfiberclose_bad.VM,pcloneoperation,CLONE_CALLBACK)
~$clone_window_closers(S_bad.FIBERCLOSERS,pcloneoperation,CLONE_CALLBACK)
~$clone_window_live(S_bad,pcloneoperation,CLONE_CALLBACK)
~$clone_windows_valid(S_bad)
~$call_descriptors_valid(S_bad)
$drive(S_bad,0).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
S_coherent = S_bad[.CLONES = [pclonewindow[.OPERATION = pcloneoperation_bad]]]
$heap_graph(S_coherent) = $heap_graph(S)
$clone_window_live(S_coherent,pcloneoperation_bad,CLONE_CALLBACK)
$clone_window_body_valid(S_coherent,pclonewindow[.OPERATION = pcloneoperation_bad])
$clone_windows_valid(S_coherent)
S_coherent_vm = $fiber_vm_restore(S_coherent,pfiberclose_bad.VM)
S_coherent_source = $constant_frame_scope(S_coherent_vm,pframe_bad,pframe_clone_tail*)
~$clone_operation_source_valid(S_coherent_source,pcloneoperation_bad)
~$clone_context_frame_valid(S_coherent_vm,pcallcontext_clone,pframe_bad,pframe_clone_tail*)
~$call_descriptors_valid(S_coherent)
$drive(S_coherent,0).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
$clone_windows_valid(S_zero)
$call_descriptors_valid(S_zero)
$heap_valid($heap_graph(S_zero))
S_one_found = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one_found.COMPLETION = NORMAL \/ S_one_found.COMPLETION = BUDGET
S_one = S_one_found[.COMPLETION = NORMAL]
$clone_windows_valid(S_one)
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_one.CLONES = [pclonewindow]
$clone_window_live(S_one,pcloneoperation,CLONE_CALLBACK)
S_done = $drive_steps(S_one,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
$clone_updates_review_output(S_done.EVENTS) = $ptascii("close|seed/late|done")
S_done.CLONES = eps
S_done.FIBERCLOSERS = eps
$clone_windows_valid(S_done)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(freeze):
    result = snapshot(freeze)
    for name in ('readonly_clone_selection_protocol.py', 'readonly_clone_updates_protocol.py'):
        path = Path(__file__).with_name(name)
        result['watched'][str(path.relative_to(ROOT))] = {
            'sha256': sha(path), 'mode': oct(path.stat().st_mode & 0o7777)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True, choices=list(GROUPS))
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--prepare', action='store_true', help='frontend/adapter only; no model credit')
    parser.add_argument('--sl', action='store_true', help='strict SL runner; default is AL')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='readonly-clone-selection-'+args.group+'-', dir=ROOT/'.tools')).resolve()
    report = {'passed': False, 'prepared': False, 'before': before, 'group': args.group,
              'sources': [], 'state_assertions_evaluated': 0,
              'mode': 'prepared; model UNRUN' if args.prepare else 'source-reached',
              'profile': cross.invoke.types.PROFILE,
              'runner_mode': 'strict SL' if args.sl else 'AL', 'numeric_cap_seconds': 120,
              'jobs': 1, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    frontend = adapter = None
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        clauses = []
        for tag, name in GROUPS[args.group]:
            row = next(row for row in ROWS if row['id'] == name)
            source = row['source'].encode()
            path = out/('source-'+tag+'.php'); path.write_bytes(source)
            source_sha256 = sha(path)
            assert source_sha256 == row['source_sha256']
            report['sources'].append({'case': name, 'source': str(path),
                'source_sha256': source_sha256, 'expected_stdout': row['expected_stdout']})
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            initial = '$php_run(program_'+tag+',0,'+json.dumps(base64.b64encode(os.fsencode(path)).decode())+')'
            clauses += ['program_'+tag+' = '+checked['fixture'], 'S_initial_'+tag+' = '+initial]
        clauses += CLAUSES[args.group].strip().splitlines()
        prefix = PREFIX
        if args.group == 'autoload-birth':
            prefix += AUTOLOAD_PREFIX
        elif args.group == 'closer-window':
            prefix += CLOSER_PREFIX
        elif args.group != 'keyword-shutdown-birth':
            prefix += FIBER_PREFIX
        fixture = out/'protocol.watsup'
        fixture.write_text(prefix+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+
            '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(prepared=True, prepared_assertions=len(clauses))
        if not args.prepare:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
                *(['--sl'] if args.sl else []), *[str(ROOT/p) for p in modules],
                str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report.update(passed=True, state_assertions_evaluated=len(clauses))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = inputs(args.freeze)
        report['inputs_unchanged'] = report['before'] == report['after']
        report['sources_unchanged'] = all(row['source_sha256'] == sha(Path(row['source'])) for row in report['sources'])
        report['passed'] = report['passed'] and report['inputs_unchanged'] and report['sources_unchanged']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['mode'] if args.prepare else report['passed'], flush=True)
    assert report['inputs_unchanged'] and report['sources_unchanged']
    assert report['prepared'] if args.prepare else report['passed']


if __name__ == '__main__':
    main()
