#!/usr/bin/env python3
"""Check declared child ownership through reference-object constant selection."""
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

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'tests/semantics/deprecated_reference_object_property/child-before-member.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $reference_object_ready(pstate,nat) : bool
def $reference_object_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier phpType33 metadata_member) z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_object_ready(S,1) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_object_ready(S,2) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_object_ready(S,n) = false -- otherwise
dec $reference_object_pause(pstate,nat,nat) : pstate
def $reference_object_pause(S,n_phase,n_budget) = S -- if $reference_object_ready(S,n_phase)
def $reference_object_pause(S,n_phase,n_budget) = $reference_object_pause(S_next[.COMPLETION = NORMAL],n_phase,$nabs($(n_budget - 1)))
  -- if ~$reference_object_ready(S,n_phase)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_object_pause(S,n_phase,n_budget) = S -- otherwise
'''


def fields_local(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['child-before-member']['stdout']
    child=quoted('Ns242RefProperty\\Child242');base=quoted('Ns242RefProperty\\Base242')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')']
    previous='S_start[.COMPLETION = NORMAL]'
    for i,(phase,prefix,member,value) in enumerate([(0,'L|C|','A',9),(1,'L|C|D|H|9|P|H|9|R|C|','B',10)],1):
        raw=f'S_raw{i}';cl=f'S_class{i}';neutral=f'S_neutral{i}';release=f'S_release{i}'
        w=f'S_warn{i}';r=f'S_resume{i}';v=f'S_value{i}';n=f'n_reference{i}';obj=f'n_object{i}';payload=f'n_payload{i}';slot=f'ppropertyslot_payload{i}';prop=f'ppropertydesc_payload{i}'
        fn=f'expression_class{i}';m=f'phpType20_member{i}' if phase==0 else f'expression_member{i}';z=f'z_{i}';tail=f'ptask_tail{i}*'
        site=f'porigin_site{i}';desc=f'pclassconstantdesc_{i}';ctx=f'pclassdesc_{i}';op=f'pdestructionoperation_{i}'
        literal_args=','.join([cl,'REFERENCE '+n,fn,m,z,tail])
        selector=lambda state,operand:'$class_constant_reference_object_selector('+state+','+operand+')'
        checks += [raw+' = $reference_object_pause('+previous+','+str(phase)+',30000)','$reference_object_ready('+raw+','+str(phase)+')',
            raw+'.TODO = (CLASS_CONST_CLASS '+fn+' '+m+' '+z+') :: '+tail,
            raw+'.ORIGIN = ('+site+')',raw+'.RESULT = REFERENCE '+n,
            raw+'.CURRENT = eps',raw+'.FRAMES = eps',raw+'.HELD = eps',
            '$call_reference_operand_valid('+raw+',REFERENCE '+n+')',
            raw+'.STORE['+n+'] = DEFINED (POBJECT '+obj+')',
            '(HCELL '+n+') <- '+raw+'.ALLOCATIONS','(HOBJECT '+obj+') <- '+raw+'.ALLOCATIONS',
            raw+'.OBJECTS['+obj+'] = INSTANCE porigin_child'+str(i),
            '$objectprops_at('+raw+'.OBJECTPROPS,'+obj+') = (['+slot+'])',
            slot+'.STATE = PROP_VALUE (DIRECT (POBJECT '+payload+'))',
            '$property_slot_descriptor('+raw+','+obj+','+slot+') = ('+prop+')',
            prop+'.VISIBILITY = PROPERTY_PUBLIC',prop+'.SETVISIBILITY = eps',prop+'.TYPE = eps',
            '~'+prop+'.STATIC','~'+prop+'.READONLY',
            '~$property_hook_source_declared('+raw+','+prop+')',
            '~$property_hook_declared('+raw+','+obj+','+slot+'.NAME)',
            '$class_at('+raw+'.CLASSES,porigin_child'+str(i)+') = (pclassdesc_owner'+str(i)+')',
            'pclassdesc_owner'+str(i)+'.PROPERTIES = eps',
            '(HOBJECT '+payload+') <- '+raw+'.ALLOCATIONS',
            raw+'.OBJECTS['+payload+'] = INSTANCE porigin_payload'+str(i),
            '$objectprops_at('+raw+'.OBJECTPROPS,'+payload+') = (eps)',
            '$object_table_at('+raw+'.OBJECTTABLES,'+payload+') = eps',
            '$heap_owners($heap_graph('+raw+'),HOBJECT '+payload+') = 1',
            '$object_table_at('+raw+'.OBJECTTABLES,'+obj+') = eps',
            '$heap_owners($heap_graph('+raw+'),HCELL '+n+') = 1',
            '$heap_owners($heap_graph('+raw+'),HOBJECT '+obj+') = 1',
            '$machine_base_roots('+raw+') = eps','$call_descriptors_valid('+raw+')',
            '$ccn_output('+raw+'.EVENTS) = '+quoted(prefix),
            cl+' = $class_constant_selector('+raw+','+fn+','+z+')',cl+'.COMPLETION = NORMAL',
            cl+'.RESULT = KNOWN (PSTRING '+child+')',
            '$heap_owners($heap_graph('+cl+'),HCELL '+n+') = 0',
            '$heap_owners($heap_graph('+cl+'),HOBJECT '+obj+') = 1',
            '$heap_owners($heap_graph('+cl+'),HOBJECT '+payload+') = 1',
            '$eager_slots('+raw+','+cl+') = [HCELL '+n+']',
            selector(cl,'REFERENCE '+n)+' = ('+ctx+')',ctx+'.NAME = '+child,
            selector(cl,'KNOWN (POBJECT '+obj+')')+' = eps',
            selector(cl,'REFERENCE (|'+cl+'.STORE|)')+' = eps',
            selector(cl+'[.REFCELLS = eps]','REFERENCE '+n)+' = eps',
            selector(cl+'[.ALLOCATIONS = $native_remove_one('+cl+'.ALLOCATIONS,HCELL '+n+')]','REFERENCE '+n)+' = eps',
            selector(cl+'[.ALLOCATIONS = $native_remove_one('+cl+'.ALLOCATIONS,HOBJECT '+obj+')]','REFERENCE '+n)+' = eps',
            selector(cl+'[.STORE = $set_cell('+cl+'.STORE,'+n+',UNDEFINED)]','REFERENCE '+n)+' = eps',
            selector(cl+'[.STORE = $set_cell('+cl+'.STORE,'+n+',DEFINED PNULL)]','REFERENCE '+n)+' = eps',
            selector(cl+'[.STORE = $set_cell('+cl+'.STORE,'+n+',DEFINED (PSTRING '+child+'))]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTS = eps]','REFERENCE '+n)+' = eps',
            selector(cl+'[.ALLOCATIONS = $native_remove_one('+cl+'.ALLOCATIONS,HOBJECT '+payload+')]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTTABLES = [{OBJECT '+payload+', TABLE 0}]]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTPROPS = $objectprops_set('+cl+'.OBJECTPROPS,'+payload+',['+slot+'])]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTPROPS = $objectprops_set('+cl+'.OBJECTPROPS,'+obj+',['+slot+'[.STATE = PROP_VALUE (DIRECT PNULL)]])]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTPROPS = $objectprops_set('+cl+'.OBJECTPROPS,'+obj+',['+slot+'[.STATE = PROP_VALUE (ALIAS '+n+')]])]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTPROPS = $objectprops_set('+cl+'.OBJECTPROPS,'+obj+',['+slot+'[.STATE = PROP_VALUE (DIRECT (POBJECT '+obj+'))]])]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTPROPS = eps]','REFERENCE '+n)+' = eps',
            selector(cl+'[.OBJECTTABLES = [{OBJECT '+obj+', TABLE 0}]]','REFERENCE '+n)+' = eps',
            selector(cl+'[.RESULT = KNOWN (PSTRING '+base+')]','REFERENCE '+n)+' = eps',
            '$class_constant_reference_selector('+cl+',REFERENCE '+n+') = eps',
            '$class_constant_lookup('+cl+','+ctx+'.ORIGIN,$ptascii("'+member+'"),|'+cl+'.CLASSES|) = ('+desc+')']
        if phase==0:
            entry='$class_constant_reference_object_literal_entry'
            checks += [entry+'('+literal_args+') = ('+desc+')',
                '$class_constant_object_entry('+literal_args+') = eps',
                '$class_constant_reference_literal_entry('+literal_args+') = eps']
            result=' = eps'
        else:
            entry='$class_constant_reference_object_capture_entry'
            checks += [entry+'('+literal_args+')',
                '~$class_constant_object_class_entry('+literal_args+')',
                '~$class_constant_reference_capture_entry('+literal_args+')']
            result=' = false'
        for change in ['.COMPLETION = BUDGET','.HELD = [HCELL '+n+']','.BASE = BASE_VALUE (REFERENCE '+n+')','.ORIGIN = eps','.TODO = '+tail,'.SOURCES = eps']:
            checks += [entry+'('+','.join([cl+'['+change+']','REFERENCE '+n,fn,m,z,tail])+')'+result]
        checks += [neutral+' = $class_constant_class_forward('+literal_args+')',
            neutral+'.COMPLETION = NORMAL',neutral+'.RESULT = KNOWN PNULL',neutral+'.BASE = BASE_VALUE (KNOWN PNULL)',
            '$heap_owners($heap_graph('+neutral+'),HCELL '+n+') = 0',
            '$heap_owners($heap_graph('+neutral+'),HOBJECT '+obj+') = 1',
            '$heap_owners($heap_graph('+neutral+'),HOBJECT '+payload+') = 1']
        if phase==0:
            marker='CLASS_CONST_OBJECT_FETCH '+site+' '+child+' $ptascii("A") '+z
            checks += [neutral+'.TODO = ('+marker+') :: '+tail,
                '$class_constant_object_fetch_valid('+neutral+','+site+','+child+',$ptascii("A"),'+z+')']
        else:
            marker='CLASS_CONST_OBJECT_CAPTURE '+site+' '+child+' '+z
            checks += [f'ptask_marker{i} = '+marker,
                f'ptask_member{i} = $at_task($origin_child(('+site+'),[PCFIELD 1]),EVAL '+m+')',
                neutral+'.TODO = ptask_member'+str(i)+' :: (CLASS_CONST_MEMBER '+fn+' (KNOWN (PSTRING '+child+')) '+z+') :: (CLASS_CONST_CAPTURE '+site+' (KNOWN (PSTRING '+child+')) '+z+') :: ptask_marker'+str(i)+' :: '+tail,
                '$class_constant_object_capture_source('+neutral+','+site+','+child+','+z+')']
        checks += ['$task_nodes('+marker+') = eps','~$class_constant_notice_protected('+neutral+','+desc+'.ORIGIN)',
            '$eager_operation_source('+raw+',CLASS_CONST_CLASS '+fn+' '+m+' '+z+') = '+marker,
            f'S_step{i} = $drive_steps('+raw+',1)',f'S_step{i}.COMPLETION = BUDGET',
            release+f' = S_step{i}[.COMPLETION = NORMAL]',
            release+'.DESTRUCTION.OPERATIONS = ['+op+']',op+'.SOURCE = '+marker,
            op+'.VALUE = KNOWN PNULL',op+'.BASE = BASE_VALUE (KNOWN PNULL)',op+'.COMPLETION = NORMAL',op+'.PENDING = eps',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT '+op+') = eps',
            '$eager_operation_source_guard('+release+','+op+')',
            '$destructor_operation_live('+release+','+op+')','$call_descriptors_valid('+release+')',
            '~$class_constant_notice_protected('+release+','+desc+'.ORIGIN)',
            '$ccn_output('+release+'.EVENTS) = '+quoted(prefix)]
        if phase==0:
            checks += ['S_inner_warn = $ccn_pause('+release+',0,30000)','$ccn_ready(S_inner_warn,0)',
                'S_inner_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_inner) :: ptask_inner*',
                'perrorcall_inner.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT '+desc+'.ORIGIN '+child+' $ptascii("A") z_inner',
                '$ccn_output(S_inner_warn.EVENTS) = '+quoted(prefix+'D|'),
                '~((HCELL '+n+') <- S_inner_warn.ALLOCATIONS)',
                '(HOBJECT '+obj+') <- S_inner_warn.ALLOCATIONS',
                'S_inner_warn.CURRENT = (pcallcontext_inner)','pcallcontext_inner.RECEIVER = ('+obj+')',
                '(HOBJECT '+payload+') <- S_inner_warn.ALLOCATIONS',
                '$heap_owners($heap_graph(S_inner_warn),HOBJECT '+payload+') = 1',
                '$call_descriptors_valid(S_inner_warn)',
                '$class_constant_notice_valid(S_inner_warn,'+desc+'.ORIGIN,'+child+',$ptascii("A"),z_inner)',
                'S_inner_resume = $ccn_pause(S_inner_warn,1,30000)','$ccn_ready(S_inner_resume,1)',
                '$ccn_output(S_inner_resume.EVENTS) = '+quoted(prefix+'D|H|'),
                'S_inner_step = $drive_steps(S_inner_resume,1)','S_inner_step.COMPLETION = BUDGET',
                'S_inner_value = S_inner_step[.COMPLETION = NORMAL]','S_inner_value.RESULT = KNOWN (PINT 9)',
                '~$class_constant_notice_protected(S_inner_value,'+desc+'.ORIGIN)']
            before_warn='S_inner_value';warnprefix=prefix+'D|H|9|P|'
        else:
            checks += ['S_pair = $reference_object_pause('+release+',2,30000)','$reference_object_ready(S_pair,2)',
                'S_pair.TODO = (CLASS_CONST_MEMBER '+fn+' (KNOWN (PSTRING '+child+')) '+z+') :: (CLASS_CONST_CAPTURE '+site+' (KNOWN (PSTRING '+child+')) '+z+') :: ptask_marker'+str(i)+' :: '+tail,
                'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("B"))',
                '$ccn_output(S_pair.EVENTS) = '+quoted(prefix+'D|H|9|P|M|'),
                '~((HCELL '+n+') <- S_pair.ALLOCATIONS)','~((HOBJECT '+obj+') <- S_pair.ALLOCATIONS)','~((HOBJECT '+payload+') <- S_pair.ALLOCATIONS)',
                'S_pair.DESTRUCTION.OPERATIONS = eps',
                '$class_constant_object_member_entry(S_pair,S_pair.RESULT,'+fn+',KNOWN (PSTRING '+child+'),'+z+','+tail+') = ('+desc+')']
            before_warn='S_pair';warnprefix=prefix+'D|H|9|P|M|'
        checks += [w+' = $ccn_pause('+before_warn+',0,30000)','$ccn_ready('+w+',0)',
            w+f'.TODO = (ERROR_HANDLER_INVOKE perrorcall_{i}) :: ptask_warn{i}*',
            f'perrorcall_{i}.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT '+desc+'.ORIGIN '+child+' $ptascii("'+member+'") '+z,
            '$ccn_output('+w+'.EVENTS) = '+quoted(warnprefix),w+'.DESTRUCTION.OPERATIONS = eps',
            '~((HCELL '+n+') <- '+w+'.ALLOCATIONS)','~((HOBJECT '+obj+') <- '+w+'.ALLOCATIONS)',
            '$heap_owners($heap_graph('+w+'),HCELL '+n+') = 0','$heap_owners($heap_graph('+w+'),HOBJECT '+obj+') = 0',
            '~((HOBJECT '+payload+') <- '+w+'.ALLOCATIONS)','$heap_owners($heap_graph('+w+'),HOBJECT '+payload+') = 0',
            '~$call_reference_operand_valid('+w+',REFERENCE '+n+')',
            selector(w+'[.STORE = '+cl+'.STORE][.REFCELLS = '+cl+'.REFCELLS][.RESULT = KNOWN (PSTRING '+child+')]','REFERENCE '+n)+' = eps',
            '$class_constant_notice_valid('+w+','+desc+'.ORIGIN,'+child+',$ptascii("'+member+'"),'+z+')',
            f'$task_nodes(perrorcall_{i}.RESUME) = eps',f'$error_call_valid({w},perrorcall_{i})','$call_descriptors_valid('+w+')',
            r+' = $ccn_pause('+w+',1,30000)','$ccn_ready('+r+',1)',
            '$ccn_output('+r+'.EVENTS) = '+quoted(warnprefix+'H|'),
            f'S_global{i} = $global_table_view('+r+')',
            f'$lookup(S_global{i}.ENV,$ptascii("member242")) = (n_member{i})',
            f'S_global{i}.STORE[n_member{i}] = DEFINED pvalue_now{i}',
            f'$string_bytes(pvalue_now{i}) = ($ptascii("A"))',
            '$class_constant_notice_valid('+r+','+desc+'.ORIGIN,'+child+',$ptascii("'+member+'"),'+z+')',
            f'S_value_step{i} = $drive_steps('+r+',1)',f'S_value_step{i}.COMPLETION = BUDGET',
            v+f' = S_value_step{i}[.COMPLETION = NORMAL]',v+'.RESULT = KNOWN (PINT '+str(value)+')',
            v+'.EVENTS = '+r+'.EVENTS',v+'.CLASSCONSTANTCACHE = eps',v+'.CLASSCONSTANTHISTORY = '+r+'.CLASSCONSTANTHISTORY',
            '~$class_constant_notice_protected('+v+','+desc+'.ORIGIN)']
        previous=v
    checks += ['S_done = $drive_steps(S_value2,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']
    return checks


SOURCE_RETAINED=SOURCE.with_name('retained-child-cow.php')


def fields_retained(fixture):
    child=quoted('Ns242RetainedChild\\Child242')
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['retained-child-cow']['stdout']
    return ['U_ext = '+fixture,'S_ext_start = $php_run(U_ext,0,'+json.dumps(base64.b64encode(bytes(SOURCE_RETAINED)).decode())+')',
        'S_ext_raw = $reference_object_pause(S_ext_start[.COMPLETION = NORMAL],1,30000)',
        '$reference_object_ready(S_ext_raw,1)',
        'S_ext_raw.TODO = (CLASS_CONST_CLASS expression_ext_class expression_ext_member z_ext) :: ptask_ext_tail*',
        'S_ext_raw.ORIGIN = (porigin_ext_site)','S_ext_raw.RESULT = REFERENCE n_ext_reference',
        'S_ext_raw.CURRENT = eps','S_ext_raw.FRAMES = eps','S_ext_raw.HELD = eps',
        '$call_reference_operand_valid(S_ext_raw,REFERENCE n_ext_reference)',
        'S_ext_raw.STORE[n_ext_reference] = DEFINED (POBJECT n_ext_object)',
        '$objectprops_at(S_ext_raw.OBJECTPROPS,n_ext_object) = ([ppropertyslot_ext])',
        'ppropertyslot_ext.STATE = PROP_VALUE (DIRECT (POBJECT n_ext_payload))',
        '$property_slot_descriptor(S_ext_raw,n_ext_object,ppropertyslot_ext) = (ppropertydesc_ext)',
        'ppropertydesc_ext.VISIBILITY = PROPERTY_PUBLIC','ppropertydesc_ext.TYPE = eps',
        '$lookup(S_ext_raw.ENV,$ptascii("payload242")) = (n_ext_global)',
        'S_ext_raw.STORE[n_ext_global] = DEFINED (POBJECT n_ext_payload)',
        '$heap_owners($heap_graph(S_ext_raw),HCELL n_ext_reference) = 1',
        '$heap_owners($heap_graph(S_ext_raw),HOBJECT n_ext_object) = 1',
        '$heap_owners($heap_graph(S_ext_raw),HOBJECT n_ext_payload) = 2',
        '$ccn_output(S_ext_raw.EVENTS) = $ptascii("B|C|")',
        'S_ext_class = $class_constant_selector(S_ext_raw,expression_ext_class,z_ext)',
        'S_ext_class.RESULT = KNOWN (PSTRING '+child+')',
        '$heap_owners($heap_graph(S_ext_class),HCELL n_ext_reference) = 0',
        '$heap_owners($heap_graph(S_ext_class),HOBJECT n_ext_object) = 1',
        '$heap_owners($heap_graph(S_ext_class),HOBJECT n_ext_payload) = 2',
        '$class_constant_reference_object_selector(S_ext_class,S_ext_raw.RESULT) = (pclassdesc_ext)',
        '$class_constant_reference_object_capture_entry(S_ext_class,S_ext_raw.RESULT,expression_ext_class,expression_ext_member,z_ext,ptask_ext_tail*)',
        '$class_constant_lookup(S_ext_class,pclassdesc_ext.ORIGIN,$ptascii("TREE"),|S_ext_class.CLASSES|) = (pclassconstantdesc_ext)',
        'pclassconstantdesc_ext.FOLDED',
        '$pool_value(S_ext_class.POOLS,pclassconstantdesc_ext.INITIALIZER) = (PARRAY n_ext_donor)',
        'S_ext_neutral = $class_constant_class_forward(S_ext_class,S_ext_raw.RESULT,expression_ext_class,expression_ext_member,z_ext,ptask_ext_tail*)',
        'ptask_ext_marker = CLASS_CONST_OBJECT_CAPTURE porigin_ext_site '+child+' z_ext',
        'ptask_ext_member = $at_task($origin_child((porigin_ext_site),[PCFIELD 1]),EVAL expression_ext_member)',
        'S_ext_neutral.TODO = ptask_ext_member :: (CLASS_CONST_MEMBER expression_ext_class (KNOWN (PSTRING '+child+')) z_ext) :: (CLASS_CONST_CAPTURE porigin_ext_site (KNOWN (PSTRING '+child+')) z_ext) :: ptask_ext_marker :: ptask_ext_tail*',
        'S_ext_neutral.RESULT = KNOWN PNULL','S_ext_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_ext_marker) = eps',
        '$eager_slots(S_ext_raw,S_ext_neutral) = [HCELL n_ext_reference]',
        '$eager_operation_source(S_ext_raw,CLASS_CONST_CLASS expression_ext_class expression_ext_member z_ext) = ptask_ext_marker',
        'S_ext_step = $drive_steps(S_ext_raw,1)','S_ext_step.COMPLETION = BUDGET',
        'S_ext_release = S_ext_step[.COMPLETION = NORMAL]',
        'S_ext_release.DESTRUCTION.OPERATIONS = [pdestructionoperation_ext]',
        'pdestructionoperation_ext.SOURCE = ptask_ext_marker','pdestructionoperation_ext.VALUE = KNOWN PNULL',
        'pdestructionoperation_ext.BASE = BASE_VALUE (KNOWN PNULL)','pdestructionoperation_ext.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_ext) = eps',
        '$eager_operation_source_guard(S_ext_release,pdestructionoperation_ext)',
        '$call_descriptors_valid(S_ext_release)',
        'S_ext_pair = $reference_object_pause(S_ext_release,2,30000)','$reference_object_ready(S_ext_pair,2)',
        'S_ext_pair.TODO = (CLASS_CONST_MEMBER expression_ext_class (KNOWN (PSTRING '+child+')) z_ext) :: (CLASS_CONST_CAPTURE porigin_ext_site (KNOWN (PSTRING '+child+')) z_ext) :: ptask_ext_marker :: ptask_ext_tail*',
        'S_ext_pair.RESULT = KNOWN pvalue_ext_member','$string_bytes(pvalue_ext_member) = ($ptascii("TREE"))',
        '$ccn_output(S_ext_pair.EVENTS) = $ptascii("B|C|D|H|2|M|")',
        '~((HCELL n_ext_reference) <- S_ext_pair.ALLOCATIONS)',
        '~((HOBJECT n_ext_object) <- S_ext_pair.ALLOCATIONS)',
        '(HOBJECT n_ext_payload) <- S_ext_pair.ALLOCATIONS',
        '$heap_owners($heap_graph(S_ext_pair),HOBJECT n_ext_payload) = 1',
        'S_ext_pair.DESTRUCTION.OPERATIONS = eps',
        '$class_constant_object_member_entry(S_ext_pair,S_ext_pair.RESULT,expression_ext_class,KNOWN (PSTRING '+child+'),z_ext,ptask_ext_tail*) = (pclassconstantdesc_ext)',
        'S_ext_warn = $ccn_pause(S_ext_pair,0,30000)','$ccn_ready(S_ext_warn,0)',
        'S_ext_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_ext) :: ptask_ext_warn*',
        'perrorcall_ext.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_ext.ORIGIN '+child+' $ptascii("TREE") z_ext',
        '$task_nodes(perrorcall_ext.RESUME) = eps','$error_call_valid(S_ext_warn,perrorcall_ext)',
        'S_ext_resume = $ccn_pause(S_ext_warn,1,30000)','$ccn_ready(S_ext_resume,1)',
        '$ccn_output(S_ext_resume.EVENTS) = $ptascii("B|C|D|H|2|M|H|")',
        'S_ext_resume.STORE[n_ext_global] = DEFINED (POBJECT n_ext_payload)',
        '$heap_owners($heap_graph(S_ext_resume),HOBJECT n_ext_payload) = 1',
        '$class_constant_notice_valid(S_ext_resume,pclassconstantdesc_ext.ORIGIN,'+child+',$ptascii("TREE"),z_ext)',
        'S_ext_globals = $global_table_view(S_ext_resume)',
        '$lookup(S_ext_globals.ENV,$ptascii("member242")) = (n_ext_member)',
        'S_ext_globals.STORE[n_ext_member] = DEFINED pvalue_ext_now',
        '$string_bytes(pvalue_ext_now) = ($ptascii("OTHER"))',
        'n_ext_donor_owners = $heap_owners($heap_graph(S_ext_resume),HARRAY n_ext_donor)',
        'S_ext_value_step = $drive_steps(S_ext_resume,1)','S_ext_value_step.COMPLETION = BUDGET',
        'S_ext_value = S_ext_value_step[.COMPLETION = NORMAL]','S_ext_value.RESULT = KNOWN (PARRAY n_ext_donor)',
        '$heap_owners($heap_graph(S_ext_value),HARRAY n_ext_donor) = $(n_ext_donor_owners + 1)',
        '$heap_owners($heap_graph(S_ext_value),HOBJECT n_ext_payload) = 1',
        'S_ext_done = $drive_steps(S_ext_value,30000)','S_ext_done.COMPLETION = NORMAL',
        '$ccn_output(S_ext_done.EVENTS) = '+quoted(expected),
        '$lookup(S_ext_done.ENV,$ptascii("payload242")) = eps',
        '~((HOBJECT n_ext_payload) <- S_ext_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_ext_done),HOBJECT n_ext_payload) = 0',
        '$lookup(S_ext_done.ENV,$ptascii("value242")) = (n_ext_value)',
        'S_ext_done.STORE[n_ext_value] = DEFINED (PARRAY n_ext_copy)','n_ext_copy =/= n_ext_donor',
        'S_ext_done.ARRAYS[n_ext_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_ext_done.ARRAYS[n_ext_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        'S_ext_done.DESTRUCTION.OPERATIONS = eps','S_ext_done.CLASSCONSTANTCACHE = eps',
        'S_ext_done.CLASSCONSTANTHISTORY = S_ext_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_ext_done)','$call_descriptors_valid(S_ext_done)',
        'S_ext_zero = $drive_steps(S_ext_release,0)','S_ext_zero.COMPLETION = BUDGET',
        'S_ext_zero[.COMPLETION = NORMAL] = S_ext_release',
        'S_ext_one = $drive_steps(S_ext_release,1)','S_ext_one.COMPLETION = BUDGET',
        '$drive_steps(S_ext_zero[.COMPLETION = NORMAL],30000) = S_ext_done',
        '$drive_steps(S_ext_one[.COMPLETION = NORMAL],30000) = S_ext_done']


def prepare(out):
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    try:
        checks=[]
        for source,build in [(SOURCE,fields_local),(SOURCE_RETAINED,fields_retained)]:
            parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
            checks += build(checked['fixture'])
    finally:
        try:adapter.close()
        finally:frontend.close()
    (out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
    return len(checks)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    modules=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths=[Path(__file__),SOURCE,SOURCE_RETAINED,SOURCE.parent/'cases.json',*modules,*(ROOT/p for p in (
        'spec/semantics/modules.json','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py','tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py','tests/semantics/profile.json',
        '.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
    before={str(p.relative_to(ROOT)):sha(p) for p in paths};head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report={'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'passed':False}
    try:
        report['premises']=prepare(out)
        report['process']=recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out/'protocol.watsup')],out/'check',240)
        report['stdout']=(out/'check.stdout').read_text();report['stderr']=(out/'check.stderr').read_text()
        report['head_stable']=head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable']=before=={str(p.relative_to(ROOT)):sha(p) for p in paths}
        report['passed']=report['process']['exit']==0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout']=='true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']:print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed'];print('pass',report['premises'])


if __name__=='__main__':main()
