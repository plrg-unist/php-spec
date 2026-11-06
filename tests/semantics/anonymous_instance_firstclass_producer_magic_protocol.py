#!/usr/bin/env python3
"""Fresh FCC receiver edge, borrowed This and receiver-retirement frontier."""
import argparse
import base64
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol
ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_instance_firstclass_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_instance_firstclass_producer_magic_controls.json'
ROWS = {row['id']:row for p in (CATALOGUE,CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-instance-firstclass-pending-leaf'
UNPACK = 'magic-instance-firstclass-unpack-prefix-refused'
CONVERT = ('S.TODO = (METHOD_CONVERT (METHOD_TARGET n_receiver porigin_method) porigin_capture z_capture) :: ptask_capture_tail* '
           '-- if S.CURRENT = eps -- if S.ORIGIN = (porigin_capture)')
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_string_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_producer) metadata_string_producer) :: expression_echo_tail*)) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) phpType7_remaining* 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.CURRENT = eps -- if S.RESULT = KNOWN (POBJECT n_sent)')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
# Constructor and ordinary table/child contracts retain their earlier proofs.
PREFIX = names.PREFIX.replace(names.FRONT,CONVERT)
for label,front in [('shift',SHIFT),('producer',PRODUCER),('send',SEND),('return',RETURN),('boundary',BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT,front).replace('$factory182_','$instancefcc210_'+label+'_')
PREFIX += r'''
dec $instancefcc210_outer_one(ptask) : pmagicmethodcall?
def $instancefcc210_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) = (pmagicmethodcall)
def $instancefcc210_outer_one(ptask) = eps -- otherwise
dec $instancefcc210_outer(ptask*) : pmagicmethodcall?
def $instancefcc210_outer(eps) = eps
def $instancefcc210_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $instancefcc210_outer_one(ptask) = (pmagicmethodcall)
def $instancefcc210_outer(ptask :: ptask_tail*) = $instancefcc210_outer(ptask_tail*) -- if $instancefcc210_outer_one(ptask) = eps
dec $instancefcc210_sent_one(ptask) : (nat, nat)?
def $instancefcc210_sent_one(CALL_SEND (CLOSURE_TARGET n_wrapper) eps 1 ([KNOWN (POBJECT n_old)]) porigin? z) = ((n_wrapper,n_old))
def $instancefcc210_sent_one(ptask) = eps -- otherwise
dec $instancefcc210_sent(ptask*) : (nat, nat)?
def $instancefcc210_sent(eps) = eps
def $instancefcc210_sent(ptask :: ptask_tail*) = ((n_wrapper,n_old)) -- if $instancefcc210_sent_one(ptask) = ((n_wrapper,n_old))
def $instancefcc210_sent(ptask :: ptask_tail*) = $instancefcc210_sent(ptask_tail*) -- if $instancefcc210_sent_one(ptask) = eps
'''

def ownership(fixture,filename):
    return [
        'S_initial = $php_run('+fixture+',0,'+filename+')',r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)','S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',CONVERT,
        '$instancefcc210_outer(S.TODO) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
        'pmagicmethodcall.ARGUMENTS = [phpType7_producer,phpType7_later]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_arg',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_child((porigin_producer),[PCFIELD 0]) = (porigin_capture)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = (pfunction)',
        'pfunction.ORIGIN = porigin_method',
        '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc)',
        '$object_class_origin(S,n_receiver) = (porigin_class)',
        '$target_called_class(S,METHOD_TARGET n_receiver porigin_method) = (porigin_class)',
        '$target_lexical_class(S,METHOD_TARGET n_receiver porigin_method) = (pmethoddesc.OWNER)',
        'pmethoddesc.OWNER =/= porigin_class',
        '$call_task_valid(S,METHOD_CONVERT (METHOD_TARGET n_receiver porigin_method) porigin_capture z_capture)',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        'n_wrapper = |S.OBJECTS|',
        'S_captured = $drive_steps(S,1)','S_captured.COMPLETION = BUDGET',
        '$object_body(S_captured.OBJECTS[n_wrapper]) = METHODCLOSURE porigin_method porigin_capture porigin_class pmethodcapture?',
        'S_captured.OBJECTS = S.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_class pmethodcapture?]',
        '$closure_scope_at(S_captured.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER','pclosurescope.CALLED = porigin_class','pclosurescope.RECEIVER = (n_receiver)',
        '$node_children(S_captured,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_wrapper) = 1',
        '$call_descriptors_valid(S_captured)','$closure_state_valid(S_captured)','$gc_state_valid(S_captured)','$heap_valid($heap_graph(S_captured))',
        'S_shift_found = $instancefcc210_shift_seek(S_captured,2048)','S_shift_found.COMPLETION = BUDGET',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]',SHIFT.replace('S.','S_shift.'),
        'S_shift.FRAMES = [pframe]','$instancefcc210_outer(pframe.TODO) = (pmagicmethodcall)',
        '$instancefcc210_sent(pframe.TODO) = ((n_wrapper,n_old))',
        '$node_children(S_shift,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_old) = 1',
        '$factory182_output(S_shift.EVENTS) = eps',
        'S_producer_found = $instancefcc210_producer_seek(S_shift,2048)','S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]',PRODUCER.replace('S.','S_producer.'),
        'pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper','pcallcontext_producer.INSTANCE = (n_wrapper)',
        'pcallcontext_producer.RECEIVER = (n_receiver)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$node_children(S_producer,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 1',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
        'S_producer.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$factory182_output(S_producer.EVENTS) = $ptascii("SHIFT;")',
        'S_split = $drive_steps(S_producer,2)','S_split.COMPLETION = BUDGET',
        'S_send_split = $instancefcc210_send_seek(S_split[.COMPLETION = NORMAL],512)',
        'S_send_direct = $instancefcc210_send_seek(S_producer,514)',
        'S_send_split = S_send_direct','S_send_split.COMPLETION = BUDGET',
        'S_send = S_send_split[.COMPLETION = NORMAL]',SEND.replace('S.','S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall','n_sent = n_old','porigin_send = pmagicmethodcall.SITE',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)','~((HOBJECT n_receiver) <- S_send.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$magic_method_firstclass_producer(S_send,porigin_producer,expression_producer) = (pfunction)',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;PRODUCER;ProducerBase210/ProducerChild210;PROVIDER;")',
        '$call_descriptors_valid(S_send)','$closure_state_valid(S_send)','$gc_state_valid(S_send)','$heap_valid($heap_graph(S_send))',
        'S_sent = $drive_steps(S_send,1)','S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) ([phpType7_later]) 1 ([KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_sent_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
        'S_return_found = $instancefcc210_return_seek(S_sent,2048)','S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',RETURN.replace('S.','S_return.'),
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)','S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot_items*)',
        '$property_slot_at(ppropertyslot_items*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_return,HARRAY n_arguments) = [HOBJECT n_old]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_old) = 1',
        'S_done = $drive_steps(S_return,4096)',r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = '+names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']),filename),
        '~((HOBJECT n_wrapper) <- S_done.ALLOCATIONS)','~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)','~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '$gc_state_valid(S_done)','$heap_valid($heap_graph(S_done))',
    ]

def unpack_boundary(fixture,filename):
    return [
        'S_initial = $php_run('+fixture+',0,'+filename+')',r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $instancefcc210_boundary_seek(S_initial,2048)','S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',BOUNDARY,
        'S.ORIGIN = (porigin_site)','phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = (pfunction)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)','$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '$lookup(S.ENV,$base64(text_pack)) = (n_pack_cell)','S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)',
        'S.ARRAYS[n_pack] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7_boundary*)',
        'S_done = $drive_steps(S,2048)','S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]

def render(case,fixture,filename):
    clauses=unpack_boundary(fixture,filename) if case['source']==ROWS[UNPACK]['source'] else ownership(fixture,filename)
    return PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+clause+'\n' for clause in clauses),len(clauses)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sl',action='store_true');parser.add_argument('--case',action='append',choices=(CASE,UNPACK));args=parser.parse_args()
    protocol.run({key:{'source':ROWS[key]['source']} for key in (CASE,UNPACK) if not args.case or key in args.case},extra_inputs=(CATALOGUE,CONTROLS,Path(__file__)),fixture_renderer=render,runner_flags=('--sl',) if args.sl else ())
if __name__=='__main__':main()
