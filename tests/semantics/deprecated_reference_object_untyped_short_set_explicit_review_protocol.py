#!/usr/bin/env python3
"""Check explicit untyped short SET Param receipts and physical cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_short_set_explicit_review') / 'nested-untyped-short-set-explicit-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: '$base64(' + json.dumps(base64.b64encode(s.encode()).decode()) + ')'
SELECTED = FETCH_SELECTED + r'''
dec $hook_peer_ready(pstate,nat,nat) : bool
def $hook_peer_ready(S,0,n_middle) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
  -- if $call_reference_operand_valid(S,S.RESULT)
def $hook_peer_ready(S,1,n_middle) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_middle)
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|H|9|P|")
def $hook_peer_ready(S,2,n_middle) = true
  -- if $instance_storage_for(S,n_middle) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 1
def $hook_peer_ready(S,3,n_middle) = true
  -- if $instance_storage_for(S,n_middle) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 2
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
def $hook_peer_ready(S,4,n_root) = true
  -- if $instance_storage_for(S,n_root) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 3
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
def $hook_peer_ready(S,5,n_middle) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $hook_peer_ready(S,n_phase,n_middle) = false -- otherwise
dec $hook_peer_pause(pstate,nat,nat,nat) : pstate
def $hook_peer_pause(S,n_phase,n_middle,n_budget) = S -- if $hook_peer_ready(S,n_phase,n_middle)
def $hook_peer_pause(S,n_phase,n_middle,n_budget) = $hook_peer_pause(S_next[.COMPLETION = NORMAL],n_phase,n_middle,$nabs($(n_budget - 1)))
  -- if ~$hook_peer_ready(S,n_phase,n_middle)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $hook_peer_pause(S,n_phase,n_middle,n_budget) = S -- otherwise
'''


def fields(fixture):
    root = quoted('Ns269UntypedShortSetExplicitPeer\\Root269')
    middle = quoted('Ns269UntypedShortSetExplicitPeer\\Middle269')
    leaf = quoted('Ns269UntypedShortSetExplicitPeer\\Leaf269')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $hook_peer_pause(S_start[.COMPLETION = NORMAL],0,0,30000)', '$hook_peer_ready(S_raw,0,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_root', '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_middle,ppropertyslot_rootpad,ppropertyslot_tail])',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle', '$class_at(S_raw.CLASSES,porigin_middle) = (pclassdesc_middle)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad,ppropertyslot_edge])',
        'S_raw.OBJECTS[n_leaf] = INSTANCE porigin_leaf', '$class_at(S_raw.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_leaf) = (eps)',
        'pclassdesc_root.NAME = ' + root, 'pclassdesc_middle.NAME = ' + middle, 'pclassdesc_leaf.NAME = ' + leaf,
        'S_raw.PROPREFS = eps', '$object_table_at(S_raw.OBJECTTABLES,n_receiver) = eps',
        '$object_table_at(S_raw.OBJECTTABLES,n_middle) = eps',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]', '$node_children(S_raw,HOBJECT n_leaf) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1', '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3',
        'S_global = $global_table_view(S_raw)', '$lookup(S_global.ENV,$ptascii("outside269peer")) = (n_outside)',
        'S_global.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")']
    for field, owner, name, value in [('middle','n_receiver','middle','POBJECT n_middle'),
        ('rootpad','n_receiver','pad','PBOOL false'), ('tail','n_receiver','tail','POBJECT n_leaf'),
        ('middlepad','n_middle','pad','PBOOL true'), ('edge','n_middle','edge','POBJECT n_leaf')]:
        prop = 'ppropertydesc_' + field; slot = 'ppropertyslot_' + field
        if field not in ('middle','tail'):
            checks += [slot + '.STATE = PROP_VALUE (DIRECT (' + value + '))']
        checks += ['$property_slot_descriptor(S_raw,' + owner + ',' + slot + ') = (' + prop + ')',
            slot + '.DECL = (' + prop + '.ORIGIN)', slot + '.NAME = ' + prop + '.KEY',
            prop + '.NAME = $ptascii("' + name + '")', prop + '.KEY = ' + prop + '.NAME',
            prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps',
            '~' + prop + '.STATIC', '~' + prop + '.READONLY', '~' + prop + '.FINAL', prop + '.TYPE = eps',
            '$typed_exact(' + prop + '.TYPE,' + value + ')', '~$typed_object_exact(S_raw,' + prop + '.TYPE,' + value + ')',
            '$class_constant_reference_object_field_type(S_raw,' + prop + ',' + slot + ')',
            '~$class_constant_reference_object_hook_field(S_raw,' + owner + ',' + prop + ',' + slot + ')',
            '$property_hook_origin(S_raw,' + prop + ') = eps']
        if field in ('rootpad','middlepad'):
            origin = 'porigin_set_' + field
            parameter_name = 'outerValue269' if field == 'rootpad' else 'innerValue269'
            checks += ['$property_hook_source_declared(S_raw,' + prop + ')', '$property_hook_declared(S_raw,' + owner + ',' + slot + '.NAME)',
                '$property_set_origin(S_raw,' + prop + ') = (' + origin + ')',
                '~$property_hook_virtual(S_raw,' + prop + ')', '~$property_hook_backing(S_raw,' + owner + ',' + prop + ')',
                '$origin_node(S_raw.SOURCES,' + origin + ') = (NPropertyHook phpType14_' + field + ' phpType24_' + field + ' phpType4_' + field + ' phpType11_' + field + ' phpType16_' + field + ' expression_set_' + field + ' metadata_' + field + ')',
                'phpType16_' + field + ' = SEQUENCE ([phpType17_parameter_' + field + '])',
                'phpType17_parameter_' + field + ' = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter_' + field + ') metadata_parameter_name_' + field + ') ABSENT (SEQUENCE eps) metadata_parameter_' + field,
                '~$property_set_parameters(phpType16_' + field + ')',
                '~$property_set_explicit_origin(S_raw,' + origin + ')',
                'phpType39_' + field + ' = expression_set_' + field,
                '$property_set_expression(S_raw,' + origin + ') = ((' + prop + ',expression_set_' + field + ',z_hook_' + field + '))',
                '~$hook_body_backed(expression_set_' + field + ',' + prop + '.NAME)',
                '~$property_hook_override_backed(S_raw,' + prop + ')', '$class_constant_reference_object_hook_backed(S_raw,' + prop + ')',
                '$function_at(S_raw.FUNCTIONS,' + origin + ') = (pfunction_set_' + field + ')',
                '$origin_source(' + origin + ') = PORIGIN n_source_' + field + ' pcpath_hook_' + field,
                '$origin_node(S_raw.SOURCES,PORIGIN n_source_' + field + ' (pcpath_hook_' + field + ' ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter_' + field + ')',
                'pfunction_set_' + field + '.BODY = pcpath_hook_' + field + ' ++ [PCFIELD 5]',
                '$origin_node(S_raw.SOURCES,PORIGIN n_source_' + field + ' pfunction_set_' + field + '.BODY) = (expression_set_' + field + ')',
                '$code_expression(pfunction_set_' + field + '.CODE.EXPRESSIONS,pfunction_set_' + field + '.BODY) = ((z_hook_' + field + ',false))',
                'pfunction_set_' + field + '.DEFAULTS = eps', '~pfunction_set_' + field + '.EARLY',
                'pfunction_set_' + field + '.SIGNATURE.PARAMETERS = [psparam_' + field + ']',
                'psparam_' + field + '.NAME = $ptascii("' + parameter_name + '")', 'psparam_' + field + '.NAME = $base64(text_parameter_' + field + ')', 'psparam_' + field + '.TYPE = eps',
                '~psparam_' + field + '.BYREF', '~psparam_' + field + '.VARIADIC',
                'psparam_' + field + '.REQUIRED', 'psparam_' + field + '.DEFAULT = PSNONE',
                'pfunction_set_' + field + '.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
                '$property_set_signature_at(S_raw,' + prop + ') = (pfunction_set_' + field + '.SIGNATURE)',
                '~pfunction_set_' + field + '.SIGNATURE.BYREF',
                '$class_constant_reference_object_untyped_hook_field(S_raw,' + owner + ',' + prop + ',' + slot + ')']
        else:
            checks += ['$property_set_origin(S_raw,' + prop + ') = eps', '~$property_hook_source_declared(S_raw,' + prop + ')', '~$property_hook_declared(S_raw,' + owner + ',' + slot + '.NAME)',
                '~$class_constant_reference_object_untyped_hook_field(S_raw,' + owner + ',' + prop + ',' + slot + ')']
        if value.startswith('POBJECT'):
            checks += [prop + '.DEFAULT = PROP_NULL',
                '$property_slot_release_job(S_raw,' + owner + ',' + slot + ') = [DESTRUCTION_VALUE (HOBJECT ' + value.split()[1] + ')]']
        else:
            checks += [prop + '.DEFAULT = PROP_STORED porigin_default_' + field, '$property_slot_release_job(S_raw,' + owner + ',' + slot + ') = eps']
    checks += ['$lookup(S_global.ENV,$ptascii("called269peer")) = (n_called)', 'S_global.STORE[n_called] = DEFINED (PBOOL false)',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_rootpad,ppropertydesc_tail]',
        'pclassdesc_middle.PROPERTIES = [ppropertydesc_middlepad,ppropertydesc_edge]',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING pclassdesc_root.NAME)', 'S_class.STORE = S_raw.STORE', 'S_class.OBJECTPROPS = S_raw.OBJECTPROPS',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)', '$class_constant_reference_object_graph(S_class,n_middle,[n_receiver])',
        '~$class_constant_reference_object_fields(S_class,n_receiver,[ppropertyslot_middle,ppropertyslot_rootpad,ppropertyslot_tail])',
        '$class_constant_reference_object_fields(S_class,n_middle,[ppropertyslot_middlepad,ppropertyslot_edge])',
        '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_root)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)']
    checks += ['S_function_base = S_class[.FUNCTIONS = [pfunction_set_middlepad]]',
        '$property_set_origin(S_function_base,ppropertydesc_middlepad) = (porigin_set_middlepad)',
        '$property_set_expression(S_function_base,porigin_set_middlepad) = ((ppropertydesc_middlepad,expression_set_middlepad,z_hook_middlepad))',
        '$class_constant_reference_object_graph(S_function_base,n_middle,[n_receiver])']
    for tag, change in [
        ('name', '.NAME = $ptascii("wrong")'),
        ('parameter_name', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.NAME = $ptascii("value")]]'),
        ('body', '.BODY = pcpath_hook_middlepad'),
        ('code', '.CODE.EXPRESSIONS = eps'),
        ('type', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.TYPE = [PTBRANCH ([PTBUILTIN "mixed"])]]]'),
        ('byref', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.BYREF = true]]'),
        ('optional', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.REQUIRED = false]]'),
        ('returns', '.SIGNATURE.RETURNS = eps')]:
        state = 'S_function_' + tag
        checks += [state + ' = S_function_base[.FUNCTIONS = [pfunction_set_middlepad[' + change + ']]]',
            '$property_set_origin(' + state + ',ppropertydesc_middlepad) = eps',
            '$property_set_expression(' + state + ',porigin_set_middlepad) = eps',
            '~$class_constant_reference_object_untyped_hook_field(' + state + ',n_middle,ppropertydesc_middlepad,ppropertyslot_middlepad)',
            '~$class_constant_reference_object_graph(' + state + ',n_middle,[n_receiver])']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference)']:
        slot = 'ppropertyslot_middlepad[.STATE = ' + state + ']'
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[' + slot + ',ppropertyslot_edge])]'
        checks += ['~$class_constant_reference_object_untyped_hook_field(' + view + ',n_middle,ppropertydesc_middlepad,' + slot + ')',
            '~$class_constant_reference_object_graph(' + view + ',n_receiver,eps)']
    for value in ['PNULL','PINT 17','PBOOL false']:
        slot = 'ppropertyslot_middlepad[.STATE = PROP_VALUE (DIRECT (' + value + '))]'
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[' + slot + ',ppropertyslot_edge])]'
        checks += ['$class_constant_reference_object_untyped_hook_field(' + view + ',n_middle,ppropertydesc_middlepad,' + slot + ')',
            '$class_constant_reference_object_graph(' + view + ',n_receiver,eps)']
    checks += ['ppropertyslot_array = ppropertyslot_middlepad[.STATE = PROP_VALUE (DIRECT (PARRAY 0))]',
        'S_array = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[ppropertyslot_array,ppropertyslot_edge])]',
        '$class_constant_reference_object_field_type(S_array,ppropertydesc_middlepad,ppropertyslot_array)',
        '$class_constant_reference_object_untyped_hook_field(S_array,n_middle,ppropertydesc_middlepad,ppropertyslot_array)',
        '~$class_constant_reference_object_graph(S_array,n_receiver,eps)',
        '~$class_constant_reference_object_capture_entry(S_array,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_cycle = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[ppropertyslot_middlepad[.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))],ppropertyslot_edge])]',
        '$class_constant_reference_object_untyped_hook_field(S_cycle,n_middle,ppropertydesc_middlepad,ppropertyslot_middlepad[.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))])',
        '~$class_constant_reference_object_graph(S_cycle,n_receiver,eps)',
        'S_retired = S_class[.ALLOCATIONS = $native_remove_one(S_class.ALLOCATIONS,HOBJECT n_leaf)]',
        '~$class_constant_reference_object_graph(S_retired,n_receiver,eps)',
        'S_order = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot_tail,ppropertyslot_rootpad,ppropertyslot_middle])]',
        '$class_constant_reference_object_graph(S_order,n_receiver,eps)', '~$call_descriptors_valid(S_order)',
        '~$class_constant_reference_object_capture_entry(S_order,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ppropertyslot_wrong = ppropertyslot_middlepad[.DECL = (ppropertydesc_tail.ORIGIN)]',
        '$property_slot_descriptor(S_class,n_middle,ppropertyslot_wrong) = eps',
        'S_wrong = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[ppropertyslot_wrong,ppropertyslot_edge])]',
        '~$class_constant_reference_object_graph(S_wrong,n_receiver,eps)',
        'S_default = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_root[.PROPERTIES = [ppropertydesc_middle,ppropertydesc_rootpad[.DEFAULT = PROP_UNINITIALIZED],ppropertydesc_tail]])]',
        '~$call_descriptors_valid(S_default)',
        '~$class_constant_reference_object_capture_entry(S_default,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_missing = S_class[.FUNCTIONS = eps]',
        '$property_set_origin(S_missing,ppropertydesc_middlepad) = eps',
        '$property_set_expression(S_missing,porigin_set_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_missing,n_receiver,eps)',
        '~$call_descriptors_valid(S_missing)',
        '~$class_constant_reference_object_capture_entry(S_missing,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_class.SOURCES = [pcunit]', '$origin_source(porigin_set_middlepad) = PORIGIN n_source pcpath_hook',
        'ppropertydesc_middlepad.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        '$origin_node(S_class.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_set])) metadata_group)',
        'phpType38_set = NPropertyHook phpType14_middlepad phpType24_middlepad phpType4_middlepad phpType11_middlepad phpType16_middlepad phpType39_middlepad metadata_middlepad',
        'phpType38_empty = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_middlepad (SEQUENCE eps) (SEQUENCE eps) metadata_middlepad',
        'pcnode_group_empty = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_empty])) metadata_group',
        'S_empty = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_group_empty) :: (PCOCCURRENCE pcpath_hook phpType38_empty) :: pcunit.OCCURRENCES]]]',
        '$property_hook_source_declared(S_empty,ppropertydesc_middlepad)',
        '$property_set_origin(S_empty,ppropertydesc_middlepad) = eps',
        '~$class_constant_reference_object_untyped_hook_field(S_empty,n_middle,ppropertydesc_middlepad,ppropertyslot_middlepad)',
        '~$class_constant_reference_object_graph(S_empty,n_receiver,eps)',
        '~$class_constant_reference_object_capture_entry(S_empty,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_hook ++ [PCFIELD 5]) (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_child,ppropertydesc_middlepad) = eps',
        '$property_set_expression(S_child,porigin_set_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_child,n_receiver,eps)',
        'phpType38_other = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_middlepad (SEQUENCE eps) (NScalarInt (INTEGER 0) eps) metadata_middlepad',
        'S_hook = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_hook phpType38_other) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_hook,ppropertydesc_middlepad) = eps',
        '$property_set_expression(S_hook,porigin_set_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_hook,n_receiver,eps)',
        'pcpath_parameter = pcpath_hook ++ [PCFIELD 4,PCINDEX 0]',
        'S_parameter_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parameter (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_parameter_child,ppropertydesc_middlepad) = eps',
        '$property_set_expression(S_parameter_child,porigin_set_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_parameter_child,n_receiver,eps)']
    for tag, raw_type, byref, variadic, variable, default in [
        ('type', '(NIdentifier (BYTES "aW50") eps)', 'false', 'false', 'text_parameter_middlepad', 'ABSENT'),
        ('byref', 'ABSENT', 'true', 'false', 'text_parameter_middlepad', 'ABSENT'),
        ('variadic', 'ABSENT', 'false', 'true', 'text_parameter_middlepad', 'ABSENT'),
        ('default', 'ABSENT', 'false', 'false', 'text_parameter_middlepad', '(NScalarInt (INTEGER 0) eps)'),
        ('name', 'ABSENT', 'false', 'false', '"dmFsdWU="', 'ABSENT')]:
        param = 'phpType17_forged_' + tag
        hook = 'phpType38_parameter_' + tag
        group = 'pcnode_parameter_' + tag
        state = 'S_parameter_' + tag
        checks += [param + ' = NParam (SEQUENCE eps) (INTEGER 0) ' + raw_type + ' (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES ' + variable + ') metadata_parameter_name_middlepad) ' + default + ' (SEQUENCE eps) metadata_parameter_middlepad',
            hook + ' = NPropertyHook phpType14_middlepad phpType24_middlepad phpType4_middlepad phpType11_middlepad (SEQUENCE ([' + param + '])) expression_set_middlepad metadata_middlepad',
            group + ' = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([' + hook + '])) metadata_group',
            state + ' = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group ' + group + ') :: (PCOCCURRENCE pcpath_hook ' + hook + ') :: (PCOCCURRENCE pcpath_parameter ' + param + ') :: pcunit.OCCURRENCES]]]',
            '$property_set_origin(' + state + ',ppropertydesc_middlepad) = eps',
            '$property_set_expression(' + state + ',porigin_set_middlepad) = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    checks += ['phpType38_arity = NPropertyHook phpType14_middlepad phpType24_middlepad phpType4_middlepad phpType11_middlepad (SEQUENCE ([phpType17_parameter_middlepad,phpType17_parameter_middlepad])) expression_set_middlepad metadata_middlepad',
        'pcnode_arity = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_arity])) metadata_group',
        'S_arity = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_arity) :: (PCOCCURRENCE pcpath_hook phpType38_arity) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_arity,ppropertydesc_middlepad) = eps',
        '$property_set_expression(S_arity,porigin_set_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_arity,n_receiver,eps)',
        'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + root + ' z',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)',
        'S_middle = $hook_peer_pause(S_release,1,n_middle,30000)', '$hook_peer_ready(S_middle,1,n_middle)',
        '$instance_storage_for(S_middle,n_receiver) = (pinstancestorage_root)', 'pinstancestorage_root.NEXT = 1',
        '$heap_owners($heap_graph(S_middle),HOBJECT n_leaf) = 3',
        'S_pad = $hook_peer_pause(S_middle,2,n_middle,30000)', '$hook_peer_ready(S_pad,2,n_middle)',
        '$objectprops_at(S_pad.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad[.STATE = PROP_UNSET],ppropertyslot_edge])',
        '$heap_owners($heap_graph(S_pad),HOBJECT n_leaf) = 3',
        '$property_slot_release_job(S_pad,n_middle,ppropertyslot_middlepad) = eps',
        'S_edge = $hook_peer_pause(S_pad,3,n_middle,30000)', '$hook_peer_ready(S_edge,3,n_middle)',
        '$objectprops_at(S_edge.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad[.STATE = PROP_UNSET],ppropertyslot_edge[.STATE = PROP_UNSET]])',
        '$heap_owners($heap_graph(S_edge),HOBJECT n_leaf) = 2', '$node_children(S_edge,HOBJECT n_middle) = eps',
        '~(n_leaf <- S_edge.DESTRUCTION.CALLED)', '$call_descriptors_valid(S_edge)',
        'S_tail = $hook_peer_pause(S_edge,4,n_receiver,30000)', '$hook_peer_ready(S_tail,4,n_receiver)',
        '$objectprops_at(S_tail.OBJECTPROPS,n_receiver) = ([ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET]])',
        '$heap_owners($heap_graph(S_tail),HOBJECT n_leaf) = 1', '$node_children(S_tail,HOBJECT n_receiver) = eps',
        'S_tail.PROPREFS = eps', '$call_descriptors_valid(S_tail)',
        'S_pair = $hook_peer_pause(S_tail,5,n_middle,30000)', '$hook_peer_ready(S_pair,5,n_middle)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|H|9|P|I|F|M|N|")',
        'S_pair.STORE[n_called] = DEFINED (PBOOL false)', 'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("B"))',
        '~((HCELL n_reference) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_pair.ALLOCATIONS)',
        '~((HOBJECT n_middle) <- S_pair.ALLOCATIONS)', '(HOBJECT n_leaf) <- S_pair.ALLOCATIONS',
        '$heap_owners($heap_graph(S_pair),HOBJECT n_leaf) = 1', 'S_pair.DESTRUCTION.OPERATIONS = eps',
        'S_warn = $ccn_pause(S_pair,0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + root + ' $ptascii("B") z',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|H|9|P|I|F|M|N|H|")',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + root + ',$ptascii("B"),z)',
        'S_done = $drive(S_resume,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|C|D|H|9|P|I|F|M|N|H|10|Z|L|E|")',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_called] = DEFINED (PBOOL false)', 'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_edge,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_edge',
        'S_one = $drive_steps(S_edge,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
