#!/usr/bin/env python3
"""Check authentic short reference returns, real cells and shared-child cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('parentless_short_reference_get_hook_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
PREFIX = r'''
var U : program
dec $srgh_output(pevent*) : ptbytes
def $srgh_output(eps) = eps
def $srgh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $srgh_output(pevent*)
dec $srgh_phase(pstate,nat,nat) : bool
def $srgh_phase(S,0,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("root292")
def $srgh_phase(S,1,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 0
def $srgh_phase(S,2,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 1
def $srgh_phase(S,3,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 2
def $srgh_phase(S,4,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("outside292peer")
def $srgh_phase(S,5,n) = ($property_hook_ref_plan(S) =/= eps)
def $srgh_phase(S,6,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
def $srgh_phase(S,7,n) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $srgh_phase(S,n_stage,n) = false -- otherwise
dec $srgh_seek(pstate,nat,nat,nat) : pstate
def $srgh_seek(S,n_stage,n_object,n) = S[.COMPLETION = NORMAL]
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $srgh_phase(S,n_stage,n_object) \/ n = 0
def $srgh_seek(S,n_stage,n_object,n) = $srgh_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,n_object,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$srgh_phase(S,n_stage,n_object) /\ $(n > 0)
def $srgh_seek(S,n_stage,n_object,n) = S -- otherwise
dec $srgh_noarrow(pcodeexpr*,pcpath) : pcodeexpr*
def $srgh_noarrow(eps,pcpath) = eps
def $srgh_noarrow((CODEARROW pcpath z) :: pcodeexpr_tail*,pcpath) = $srgh_noarrow(pcodeexpr_tail*,pcpath)
def $srgh_noarrow(pcodeexpr :: pcodeexpr_tail*,pcpath) = pcodeexpr :: $srgh_noarrow(pcodeexpr_tail*,pcpath)
  -- if $arrow_line_entry(pcodeexpr,pcpath) = eps
dec $srgh_noexpr(pcodeexpr*,pcpath) : pcodeexpr*
def $srgh_noexpr(eps,pcpath) = eps
def $srgh_noexpr((CODEEXPR pcpath z b) :: pcodeexpr_tail*,pcpath) = $srgh_noexpr(pcodeexpr_tail*,pcpath)
def $srgh_noexpr(pcodeexpr :: pcodeexpr_tail*,pcpath) = pcodeexpr :: $srgh_noexpr(pcodeexpr_tail*,pcpath)
  -- if $code_expression([pcodeexpr],pcpath) = eps
dec $srgh_explicit(metadata) : metadata
def $srgh_explicit(eps) = eps
def $srgh_explicit((MhookParameterList b) :: metadataEntry_tail*) = (MhookParameterList true) :: $srgh_explicit(metadataEntry_tail*)
def $srgh_explicit(metadataEntry :: metadataEntry_tail*) = metadataEntry :: $srgh_explicit(metadataEntry_tail*)
  -- if ~$hook_parameter_entry(metadataEntry)
'''


def fields(fixture, source, form):
    initial = 'PINT 17' if form == 'initialized' else 'PNULL'
    namespace = 'Ns292ShortReference' + form.title() + 'Peer' + chr(92)
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')',
        'S_front = $srgh_seek(S_start,5,0,30000)', '$srgh_phase(S_front,5,0)',
        'S_front.COMPLETION = NORMAL', '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("root292")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = $base64(' + quoted(namespace + 'Root292') + ')',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps',
        '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_pad,ppropertydesc_tail]',
        '$property_effective_desc(S_front,n_root,$ptascii("pad")) = (ppropertydesc_pad)',
        '$property_hook_reference_decl(S_front,ppropertydesc_pad)',
        '$property_hook_origin(S_front,ppropertydesc_pad) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction_get)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF true}',
        'pfunction_get.NAME = pclassdesc_root.NAME ++ $ptascii("::$pad::get")',
        'pfunction_get.DEFAULTS = eps', '~pfunction_get.EARLY',
        'ppropertydesc_pad.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'ppropertyhook.HOOK = PORIGIN n_source pcpath_hook',
        'pcpath_hook = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pfunction_get.ORIGIN = ppropertyhook.HOOK', 'pfunction_get.BODY = pcpath_hook ++ [PCFIELD 5]',
        'pfunction_get.CODE.UNIT = n_source',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) phpType5_default metadata_item])) (SEQUENCE ([phpType38_get])) metadata_group)',
        '$base64(text_pad) = $ptascii("pad")',
        'phpType38_get = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) expression_get metadata_get',
        '$hook_parameter_facts(metadata_get) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("pad")',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$source_line(metadata_get) = 23', '$source_line(metadata_expression) = 24',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((24,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (24)',
        '$property_hook_reference_expression_return(S_front,ppropertyhook.HOOK,24) = (expression_get)',
        '$property_hook_expression_return(S_front,ppropertyhook.HOOK,24) = eps',
        '$function_body_tasks(S_front,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),DIM_PREP expression_get),RETURN_REF_FETCH 24]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initialmiddle,ppropertyslot_initialpad,ppropertyslot_initialtail])',
        'ppropertyslot_initialpad.STATE = PROP_VALUE (DIRECT (' + initial + '))',
        '$heap_owners($heap_graph(S_front),HOBJECT n_root) = 1',
        '$srgh_output(S_front.EVENTS) = $ptascii("B|Q|")',
        'S_return = $srgh_seek(S_front,6,n_root,30000)', '$srgh_phase(S_return,6,n_root)',
        'S_return.COMPLETION = NORMAL', 'S_return.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
        'pcallcontext_get.FUNCTION = ppropertyhook.HOOK', 'S_return.ORIGIN = (ppropertyhook.HOOK)',
        'pcallcontext_get.RECEIVER = (n_root)', 'pcallcontext_get.INSTANCE = eps',
        'S_return.TODO = (RETURN_REF_FETCH 24) :: ptask_return*',
        'S_return.BASE = BASE_PROPERTY_PENDING (BASE_VALUE (KNOWN (POBJECT n_root))) (KNOWN (PSTRING ($ptascii("pad")))) 24',
        'S_resolved = $property_pending_resolve(S_return,BASE_VALUE (KNOWN (POBJECT n_root)),KNOWN (PSTRING ($ptascii("pad"))),PPW,24,24)',
        'S_resolved.COMPLETION = NORMAL', 'S_resolved.BASE = BASE_PROPERTY (POBJECT n_root) ($ptascii("pad"))',
        '$reference_returning(S_return)', '$reference_return_source(S_return,24)',
        '$reference_return_fetch_valid(S_return,24)', '~$reference_return_value_valid(S_return,24)',
        '$arrow_return(S_return,24) = eps',
        '$property_hook_backing(S_return,n_root,ppropertydesc_pad)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_root) = 3',
        '$base_nodes(S_return.BASE) = [HOBJECT n_root]',
        '$call_context_roots(S_return.CURRENT) = [HOBJECT n_root]',
        '$node_children(S_return,HCELL n_rootcell) = [HOBJECT n_root]',
        '$call_descriptors_valid(S_return)', '$property_state_valid(S_return)',
        'S_fetch = $srgh_seek(S_return,7,n_root,30000)', '$srgh_phase(S_fetch,7,n_root)',
        'S_fetch.COMPLETION = NORMAL', 'S_fetch.RESULT = REFERENCE n_padcell',
        'S_fetch.STORE[n_padcell] = DEFINED (' + initial + ')',
        '$heap_owners($heap_graph(S_fetch),HCELL n_padcell) = 2',
        '$heap_owners($heap_graph(S_fetch),HOBJECT n_root) = 1',
        '$propref_at(S_fetch.PROPREFS,n_padcell) = eps',
        '$call_reference_operand_valid(S_fetch,S_fetch.RESULT)',
        '$property_hook_result_tail(S_fetch,ppropertyhook,S_fetch.TODO)',
        '$srgh_output(S_fetch.EVENTS) = $ptascii("B|Q|")',
        '$call_descriptors_valid(S_fetch)', '$property_state_valid(S_fetch)',
        'S_raw = $srgh_seek(S_fetch,0,n_root,30000)', '$srgh_phase(S_raw,0,n_root)',
        'S_raw.COMPLETION = NORMAL', 'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$lookup(S_raw.ENV,$ptascii("outside292peer")) = (n_outside)',
        'S_raw.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$lookup(S_raw.ENV,$ptascii("alias292peer")) = eps',
        '$property_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_middle,ppropertydesc_pad,ppropertydesc_tail]',
        '$objectprops_at(S_raw.OBJECTPROPS,n_root) = ([ppropertyslot_middle,ppropertyslot_pad,ppropertyslot_tail])',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_pad.STATE = PROP_VALUE (ALIAS n_padcell)',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
        'S_raw.STORE[n_padcell] = DEFINED (POBJECT n_pad)',
        '$propref_at(S_raw.PROPREFS,n_padcell) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_padcell) = 1',
        '$node_children(S_raw,HCELL n_padcell) = [HOBJECT n_pad]',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HCELL n_padcell,HOBJECT n_tail]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_tail) = [HOBJECT n_leaf]',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_pad) = 1',
        '$srgh_output(S_raw.EVENTS) = $ptascii("B|Q|G|W|C|")',
        '$call_descriptors_valid(S_raw)', '$property_state_valid(S_raw)',
        '$heap_valid($heap_prune($heap_graph(S_raw)))',
    ]
    for name in ('middle', 'pad', 'tail'):
        desc, slot = 'ppropertydesc_' + name, 'ppropertyslot_' + name
        checks += [
            '$property_slot_descriptor(S_raw,n_root,' + slot + ') = (' + desc + ')',
            slot + '.DECL = (' + desc + '.ORIGIN)', slot + '.NAME = ' + desc + '.KEY',
            desc + '.NAME = $ptascii("' + name + '")', desc + '.TYPE = eps',
        ]
    checks += [
        'S_storage = $srgh_seek(S_raw,1,n_root,30000)', '$srgh_phase(S_storage,1,n_root)',
        '$instance_storage_for(S_storage,n_root) = (pinstancestorage)',
        '$instance_storage_valid(S_storage,pinstancestorage)',
        '$srgh_output(S_storage.EVENTS) = $ptascii("B|Q|G|W|C|R|")',
        'S_middle = $srgh_seek(S_storage,2,n_root,30000)', '$srgh_phase(S_middle,2,n_root)',
        '$srgh_output(S_middle.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|")',
        '$node_children(S_middle,HOBJECT n_root) = [HCELL n_padcell,HOBJECT n_tail]',
        '$heap_owners($heap_graph(S_middle),HOBJECT n_leaf) = 2',
        '~((HOBJECT n_middle) <- S_middle.ALLOCATIONS)', '~(n_pad <- S_middle.DESTRUCTION.CALLED)',
        'S_pad = $srgh_seek(S_middle,3,n_root,30000)', '$srgh_phase(S_pad,3,n_root)',
        '$srgh_output(S_pad.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|U|")',
        '$node_children(S_pad,HOBJECT n_root) = [HOBJECT n_tail]',
        '$heap_owners($heap_graph(S_pad),HOBJECT n_leaf) = 2',
        '~((HCELL n_padcell) <- S_pad.ALLOCATIONS)', '~((HOBJECT n_pad) <- S_pad.ALLOCATIONS)',
        '~(n_tail <- S_pad.DESTRUCTION.CALLED)',
        'S_outside = $srgh_seek(S_pad,4,n_root,30000)', '$srgh_phase(S_outside,4,n_root)',
        '$srgh_output(S_outside.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|U|T|Z|")',
        '~((HOBJECT n_root) <- S_outside.ALLOCATIONS)', '~((HOBJECT n_tail) <- S_outside.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_outside),HOBJECT n_leaf) = 1',
        'S_done = $drive(S_outside,30000)', 'S_done.COMPLETION = NORMAL',
        '$srgh_output(S_done.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|U|T|Z|L|E|")',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$call_descriptors_valid(S_done)', '$property_state_valid(S_done)',
        '$heap_valid($heap_prune($heap_graph(S_done)))',
    ]
    for label, state in (('return', 'S_return'), ('fetch', 'S_fetch'), ('cleanup', 'S_middle')):
        checks += [
            f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
            f'S_{label}_one = $drive_steps({state},1)', f'S_{label}_one.COMPLETION = BUDGET',
        ]
        if label == 'return':
            checks += [
                'S_return_resume = S_return_one[.COMPLETION = NORMAL]',
                '(RETURN_REF_UNWIND (REFERENCE n_padcell) 24 false ppropertyhook.HOOK) <- S_return_resume.TODO',
                '$reference_arrow_boundary(S_return_resume,ppropertyhook.HOOK,24)',
                '$arrow_context(S_return_resume)',
                '~$reference_return_null_valid(S_return_resume,24)',
                '~$reference_return_notice(S_return_resume,REFERENCE n_padcell)',
                '$reference_notice_count(S_return_resume.TODO) = 0',
                '$reference_notice_presence(S_return_resume)',
                '$reference_return_result_valid(S_return_resume)',
                '~$goto_scope_valid(S_return_resume,ppropertyhook.HOOK)',
                '$call_task_valid(S_return_resume,RETURN_REF_UNWIND (REFERENCE n_padcell) 24 false ppropertyhook.HOOK)',
                '~$call_task_valid(S_return_resume,RETURN_REF_UNWIND (REFERENCE n_padcell) 24 true ppropertyhook.HOOK)',
                '$call_descriptors_valid(S_return_resume)',
                '$call_entry_check(S_return_resume) = S_return_resume',
            ]
        checks += [
            f'$drive(S_{label}_zero[.COMPLETION = NORMAL],30000) = S_done',
            f'$drive(S_{label}_one[.COMPLETION = NORMAL],30000) = S_done',
        ]
    checks += [
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        '~$reference_return_source(S_return,23)', '~$reference_return_fetch_valid(S_return,23)',
        '~$reference_arrow_boundary(S_return,ppropertyhook.HOOK,23)',
        '~$reference_arrow_boundary(S_return,PORIGIN n_source pfunction_get.BODY,24)',
        'S_no_current = S_return[.CURRENT = eps]',
        '~$reference_arrow_boundary(S_no_current,ppropertyhook.HOOK,24)',
        '~$arrow_context(S_no_current)',
        'S_target = S_return[.CURRENT = (pcallcontext_get[.TARGET = ppropertyhook.HOOK])]',
        '~$reference_return_source(S_target,24)',
        '~$reference_arrow_boundary(S_target,ppropertyhook.HOOK,24)',
        '~$arrow_context(S_target)',
        'S_origin = S_return[.ORIGIN = (PORIGIN n_source pfunction_get.BODY)]',
        '~$reference_return_source(S_origin,24)',
        '~$arrow_context(S_origin)',
        'pcpath_forged = pcpath_hook ++ [PCFIELD 7]',
        'statement_forged = NStmtReturn (NScalarInt (INTEGER 1) eps) eps',
        'pfunction_forged = pfunction_get[.CODE = pfunction_get.CODE[.EXPRESSIONS = (CODEEXPR pcpath_forged 24 false) :: pfunction_get.CODE.EXPRESSIONS]]',
        'S_forged = S_return[.ORIGIN = (PORIGIN n_source pcpath_forged)][.FUNCTIONS = pfunction_forged :: S_return.FUNCTIONS][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_forged statement_forged) :: pcunit.OCCURRENCES]]]',
        '$reference_return_source(S_forged,24)',
        '$property_hook_reference_expression_return(S_forged,ppropertyhook.HOOK,24) = (expression_get)',
        '~$arrow_context(S_forged)',
        '$reference_return_notice(S_forged,KNOWN (PINT 1))',
        '~$reference_arrow_boundary(S_forged,PORIGIN n_source pcpath_forged,24)',
    ]
    for label, change in (
        ('name', '[.NAME = $ptascii("fake")]'), ('body', '[.BODY = pcpath_group]'),
        ('signature', '[.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}]'),
        ('header', '[.LINE = 0]'), ('endline', '[.ENDLINE = 23]'),
        ('unit', '[.CODE = pfunction_get.CODE[.UNIT = $(n_source + 1)]]'),
        ('marker', '[.CODE = pfunction_get.CODE[.EXPRESSIONS = $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]]'),
        ('line', '[.CODE = pfunction_get.CODE[.EXPRESSIONS = (CODEARROW pfunction_get.BODY 23) :: $srgh_noarrow(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]]'),
        ('expression', '[.CODE = pfunction_get.CODE[.EXPRESSIONS = $srgh_noexpr(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]]'),
        ('read', '[.CODE = pfunction_get.CODE[.EXPRESSIONS = (CODEEXPR pfunction_get.BODY 24 true) :: $srgh_noexpr(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)]]'),
    ):
        checks += [
            f'S_{label} = S_return[.FUNCTIONS = (pfunction_get{change}) :: S_return.FUNCTIONS]',
            f'~$reference_return_source(S_{label},24)',
            f'~$reference_arrow_boundary(S_{label},ppropertyhook.HOOK,24)',
            f'~$arrow_context(S_{label})',
        ]
    checks += [
        'phpType38_hookparam = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) expression_get ($srgh_explicit(metadata_get))',
        'S_hookparam = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_hook phpType38_hookparam) :: pcunit.OCCURRENCES]]]',
        '~$reference_return_source(S_hookparam,24)',
        '$property_hook_reference_expression_return(S_hookparam,ppropertyhook.HOOK,24) = eps',
        '~$reference_arrow_boundary(S_hookparam,ppropertyhook.HOOK,24)',
        '~$arrow_context(S_hookparam)',
        'phpType38_hookvalue = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) expression_get metadata_get',
        'S_hookvalue = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_hook phpType38_hookvalue) :: pcunit.OCCURRENCES]]]',
        '~$reference_return_source(S_hookvalue,24)',
        '$property_hook_reference_expression_return(S_hookvalue,ppropertyhook.HOOK,24) = eps',
        '~$reference_arrow_boundary(S_hookvalue,ppropertyhook.HOOK,24)',
        '~$arrow_context(S_hookvalue)',
    ]
    for label, body, metadata in (
        ('param', 'expression_get', '([MhookParameterList true])'),
        ('otherfield', 'NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES "b3RoZXI=") metadata_field) metadata_expression', 'metadata_get'),
        ('nested', 'NExprArrowFunction (SEQUENCE eps) (BOOLEAN false) (BOOLEAN false) (SEQUENCE eps) ABSENT expression_get eps', 'metadata_get'),
    ):
        checks += [
            f'phpType38_{label} = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) ({body}) {metadata}',
            f'statement_{label} = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) phpType5_default metadata_item])) (SEQUENCE ([phpType38_{label}])) metadata_group',
            f'S_{label} = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_{label}) :: pcunit.OCCURRENCES]]]',
            f'~$property_hook_reference_decl(S_{label},ppropertydesc_pad)',
            f'~$reference_return_source(S_{label},24)',
            f'~$reference_arrow_boundary(S_{label},ppropertyhook.HOOK,24)',
            f'~$arrow_context(S_{label})',
        ]
    for label, desc in (('typed', 'ppropertydesc_pad[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]'),
                        ('parented', 'ppropertydesc_pad')):
        class_change = (f'[.PROPERTIES = [ppropertydesc_middle,{desc},ppropertydesc_tail]]' if label == 'typed'
                        else '[.PARENT = ($ptascii("OtherParent"))]')
        checks += [
            f'S_{label} = S_return[.CLASSES = (pclassdesc_root{class_change}) :: S_return.CLASSES]',
            f'~$property_hook_reference_decl(S_{label},{desc})',
            f'~$reference_return_source(S_{label},24)',
            f'~$reference_arrow_boundary(S_{label},ppropertyhook.HOOK,24)',
            f'~$arrow_context(S_{label})',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['initialized', 'null'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('short-reference-' + args.form + '-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + check + '\n' for check in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__': main()
