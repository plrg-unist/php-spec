#!/usr/bin/env python3
"""Genuine eval compiler pauses, source prefixes, callback frames and owners."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
from iterator_declaration_notices import literal
import user_iterator as source

ROOT = source.ROOT
METHODS = 'public function current(){return 7;}public function next():void{}public function key():mixed{return 10;}public function valid():bool{return true;}public function rewind():void{}'
normal = ('class A extends ParentIt {' + METHODS + '}\nclass W {protected function __invoke(){}}\n'
          'class B extends ParentIt {' + METHODS + '}echo "e";')
outer = 'class A extends ParentIt {' + METHODS + '}\nclass B extends ParentIt {' + METHODS + '}echo "e";'
inner = 'class InnerIt extends ParentIt {' + METHODS + '}echo "i";'
hard_outer = ('class A extends ParentIt {' + METHODS + '}\nclass B extends ParentIt {' +
              METHODS.replace('next():void', 'next($x):void') + '}\necho "BAD";')
hard_inner = 'class InnerBad extends ParentIt {' + METHODS.replace('next():void', 'next($x):void') + '}'
prefix = '<?php\nabstract class ParentIt implements Iterator {}\n'
throwing_notice = '''function notice($level,$message,$file,$line){echo "H";throw new NoticeException("handler");}
set_error_handler("notice");
try{eval(''' + literal(hard_outer) + ''');}catch(Exception $e){echo "caught";}
echo "BAD";
'''
cases = {
    'normal': (prefix + '''function notice($l,$m,$f,$line){
 echo "H",$l,";";
 foreach(new A as $key=>$value){echo "[",$key,":",$value,"]";break;}
 return true;
}
set_error_handler("notice");
eval(''' + literal(normal) + ''');
echo "d";
''', [('outer', normal)], b'H8192;[10:7]H2;[10:7]H8192;[10:7]ed'),
    'nested': (prefix + '''$count=0;
function notice($l,$m,$f,$line){
 global $count;++$count;echo "H",$count,";";
 if($count===1){set_error_handler("notice");eval(''' + literal(inner) + ''');echo "O";}
 return true;
}
set_error_handler("notice");
eval(''' + literal(outer) + ''');echo "d";
''', [('outer', outer), ('inner', inner)], b'H1;H2;iOH3;ed'),
    'throw': (prefix + '''function notice($l,$m,$f,$line){echo "H";throw new Exception("held");}
set_error_handler("notice");
try{eval(''' + literal(outer) + ''');}catch(Exception $e){echo "C:",$e->getMessage(),";";}
echo (new B) instanceof Iterator?"B":"b";
''', [('outer', outer)], b'HC:held;B'),
    'fatal': (prefix + '''function finish(){echo "S";try{new A;echo "A";}catch(Error $e){echo "a";}try{new B;echo "B";}catch(Error $e){echo "b";}}
register_shutdown_function("finish");
function notice($level,$message,$file,$line){echo "H";trigger_error("stop",E_USER_ERROR);}
set_error_handler("notice");
eval(''' + literal(outer.replace('echo "e";', 'echo "BAD";')) + ''');
echo "BAD";
''', [('outer', outer.replace('echo "e";', 'echo "BAD";'))], b'HSAb'),
    'formatter': (prefix + '''function publish(){if(true){class Rendered {}}echo (new Rendered) instanceof Rendered?"R":"r";}
class NoticeException extends Exception {function __toString():string {echo "F";publish();return "formatted";}}
''' + throwing_notice, [('outer', hard_outer)], b'HFR'),
    'nested-fatal': (prefix + '''class NoticeException extends Exception {function __toString():string {echo "F";eval(''' +
                     literal(hard_inner) + ''');return "formatted";}}
''' + throwing_notice, [('outer', hard_outer), ('inner', hard_inner)], b'HF'),
    'file-fatal': (prefix + '''class NoticeException extends Exception {function __toString():string {echo "F";include __DIR__."/bad.php";return "formatted";}}
''' + throwing_notice, [('outer', hard_outer), ('file', '<?php\n' + hard_inner + '\n')], b'HF'),
}

PREFIX = '''dec $await(pstate,nat) : pstate
def $await(S,n) = S -- if S.COMPLETION = SOURCE_PENDING
def $await(S,n) = $await($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET -- if $(n > 0)
def $await(S,n) = S -- otherwise
dec $seek(pstate,nat) : pstate
def $seek(S,n) = S -- if $stage(S)
def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,n) = S -- otherwise
dec $eval_row(ptraceframe*) : ptraceframe
def $eval_row(ptraceframe :: ptraceframe_tail*) = ptraceframe
  -- if ptraceframe.FUNCTION = $ptascii("eval")
def $eval_row(ptraceframe :: ptraceframe_tail*) = $eval_row(ptraceframe_tail*)
  -- if ptraceframe.FUNCTION =/= $ptascii("eval")
dec $forge_prefix(pdeclaration*) : pdeclaration*
dec $forge_prefix_item(pdeclaration) : pdeclaration
def $forge_prefix(eps) = eps
def $forge_prefix(pdeclaration :: pdeclaration_tail*) = $forge_prefix_item(pdeclaration) :: $forge_prefix(pdeclaration_tail*)
def $forge_prefix_item(PDEVALFATALNOTICES 1 pdeclnoticeitem*) = PDEVALFATALNOTICES 1 eps
def $forge_prefix_item(pdeclaration) = pdeclaration -- otherwise
dec $formatter_publication_has(pdeclaration*, porigin) : bool
dec $formatter_publication_item(pdeclaration, porigin) : bool
def $formatter_publication_has(eps, porigin) = false
def $formatter_publication_has(pdeclaration :: pdeclaration_tail*, porigin) = ($formatter_publication_item(pdeclaration, porigin) \\/ $formatter_publication_has(pdeclaration_tail*, porigin))
def $formatter_publication_item(PDRCLASS porigin pdeclcause, porigin) = true
def $formatter_publication_item(pdeclaration, porigin) = false -- otherwise
dec $forge_file_exit_item(pdeclaration) : pdeclaration
def $forge_file_exit_item(PDEXIT 2 pcompilestop) = PDEXIT 2 PCSREJECT
def $forge_file_exit_item(pdeclaration) = pdeclaration -- otherwise
dec $forge_file_exit(pdeclaration*) : pdeclaration*
def $forge_file_exit(eps) = eps
def $forge_file_exit(pdeclaration :: pdeclaration_tail*) = $forge_file_exit_item(pdeclaration) :: $forge_file_exit(pdeclaration_tail*)
'''

STAGES = {
    'pending': ('normal', [
        'S.TODO = (DECL_NOTICES pdeclnoticebatch) :: (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
        'pdeclnoticebatch.KIND = NOTICE_EVAL 1 n_ordinal',
        'pdeclnoticebatch.INDEX = 0',
    ], [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$eval_compile_owners_valid(S)', '$eval_compile_cursor_valid(S,pevalcompile)',
        'pevalcompile.PLAN.UNIT = 1', 'pevalcompile.CHECKPOINT = 1', 'pevalcompile.DIAGNOSTIC = 0',
        'pevalcompile.PENDING = NORMAL', '$task_nodes(EVAL_COMPILE_RESUME pevalcompile) = eps',
        'S.EVALCONTEXTS = pevalcontext :: eps', 'pevalcontext.PHASE = EVAL_COMPILE',
        'ptask_tail* = (EVAL_COMPILE_END 1) :: pevalcontext.TAIL',
        '$class_named(S.CLASSNAMES,$ptascii("a")) = (porigin_a)',
        '$class_named(S.CLASSNAMES,$ptascii("w")) = eps', '$class_named(S.CLASSNAMES,$ptascii("b")) = eps',
        '$code_at(S.CODE,1) =/= eps', '~$declaration_unit_complete(S.DECLARATIONS,1)',
        '$iterator_notice_batch_valid(S,pdeclnoticebatch)',
        'pdeclnoticebatch.NOTICES = [METHOD_NOTICE pdeclnotice_a]',
        'pdeclnotice_a.CLASS = porigin_a', 'pdeclnotice_a.LINE = 1',
        'S.DECLARATIONS[n_ordinal] = PDEVALPAUSE 1 1 0 pdeclnoticebatch.NOTICES',
        '$declaration_images(S,S.SOURCES) = DECLIMAGES (n_image,P_image)*',
        '$eval_compile_plans_valid(S,(n_image,P_image)*)',
        'pevalcompile_forged = pevalcompile[.PLAN = pevalcompile.PLAN[.WORK = eps]]',
        '$eval_compile_cursor_valid(S,pevalcompile_forged)',
        '~$eval_compile_plan_list_valid([pevalcompile_forged],(n_image,P_image)*)',
        'pdeclnotice_forged = pdeclnotice_a[.LINE = 2]',
        'pdeclnoticebatch_forged = pdeclnoticebatch[.NOTICES = [METHOD_NOTICE pdeclnotice_forged]]',
        'pdeclaration_prefix* = S.DECLARATIONS[0:n_ordinal]',
        'S_forged = S[.DECLARATIONS = pdeclaration_prefix* ++ [PDEVALPAUSE 1 1 0 pdeclnoticebatch_forged.NOTICES]][.TODO = (DECL_NOTICES pdeclnoticebatch_forged) :: (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*]',
        '$iterator_notice_batch_items(S_forged,pdeclnoticebatch_forged)',
        '$declaration_entry_check(S_forged).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
        '~$eval_compile_cursor_valid(S,pevalcompile[.CHECKPOINT = 2])',
        '~$eval_compile_cursor_valid(S,pevalcompile[.DIAGNOSTIC = 1])',
        '~$eval_compile_notice_owner(S,pdeclnoticebatch[.KIND = NOTICE_EVAL 1 $(n_ordinal + 1)])',
        '~$eval_compile_notice_owner(S,pdeclnoticebatch[.SITE = porigin_a])',
        '~$eval_compile_notice_owner(S,pdeclnoticebatch[.LINE = 1])',
        '~$eval_compile_owners_valid(S[.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: S.TODO])',
        '~$eval_compile_owners_valid(S[.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail*])',
        '~$eval_tasks_markers_valid(S,(AT pdeclnoticebatch.SITE (EVAL_COMPILE_END 1)) :: S.TODO)',
        'ptask_branch* = [EVAL_COMPILE_END 1]',
        '~$eval_tasks_markers_valid(S,(CHOOSE ptask_branch* eps 0) :: S.TODO)',
        'ptask_cursor_branch* = [EVAL_COMPILE_RESUME pevalcompile]',
        'S_choose = S[.TODO = (CHOOSE ptask_cursor_branch* eps 9) :: S.TODO]',
        '$heap_graph(S_choose) = $heap_graph(S)',
        '~$eval_tasks_markers_valid(S_choose,S_choose.TODO)',
        '~$eval_tasks_markers_valid(S,(AT pdeclnoticebatch.SITE (EVAL_COMPILE_RESUME pevalcompile)) :: ptask_tail*)',
        'ptask_notice_branch* = [DECL_NOTICES pdeclnoticebatch]',
        '~$eval_tasks_markers_valid(S,(CHOOSE ptask_notice_branch* eps 9) :: S.TODO)',
        '~$eval_tasks_markers_valid(S,(AT pdeclnoticebatch.SITE (DECL_NOTICE_RESUME pdeclnoticebatch)) :: S.TODO)',
        '~$call_task_valid(S,EVAL_END 1)',
        'ptraceframe_eval = $eval_row($eval_exception_trace(S))',
        '~ptraceframe_eval.HASARGS', 'ptraceframe_eval.ARGS = eps',
    ]),
    'function-forgery': ('normal', [
        'S.TODO = (DECL_NOTICES pdeclnoticebatch) :: (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
        'pdeclnoticebatch.KIND = NOTICE_EVAL 1 n_ordinal',
        'pdeclnoticebatch.INDEX = 0',
    ], [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))', '$eval_compile_owners_valid(S)',
        'S.FUNCTIONS = pfunction :: pfunction_tail*', 'pfunction.NAME = $ptascii("notice")',
        'pfunction.EARLY = true',
        'S_forged = S[.FUNCTIONS = pfunction[.EARLY = false] :: pfunction_tail*]',
        'S_forged.FUNCTIONS =/= S.FUNCTIONS',
        '$call_registry_valid(S_forged.FUNCTIONS,S_forged.CALLABLES)',
        '$heap_graph(S_forged) = $heap_graph(S)', '$eval_compile_owners_valid(S_forged)',
        '$eval_compile_cursor_valid(S_forged,pevalcompile)', '$scope_codes_valid(S_forged,S_forged.CODE)',
        '$call_entry_check(S_forged[.COMPLETION = NORMAL]).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
    ]),
    'handler': ('normal', [
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (EVAL_COMPILE_RESUME pevalcompile) :: ptask_saved*',
        'perrorcall.RESUME = DECL_NOTICE_RESUME pdeclnoticebatch',
        'pdeclnoticebatch.KIND = NOTICE_EVAL 1 n_ordinal',
        'pdeclnoticebatch.INDEX = 1',
    ], [
        '$call_tasks_valid(S,S.TODO)', '$call_frames_valid(S,S.FRAMES)', '$call_current_valid(S)',
        '$eval_compile_owners_valid(S)', '$iterator_notice_owners_valid(S.TODO,S.FRAMES)',
        '$heap_valid($heap_graph(S))', '$error_context_valid(S,pcallcontext)',
        'pcallcontext.ARGC = 4', 'pcallcontext.LINE = 9', 'perrorcall.LINE = 1',
        'pcallcontext.CALLSITE = (pdeclnoticebatch.SITE)', '$error_callback_line(S,perrorcall) = 9',
        '$error_handler_file(S,perrorcall) = $call_sourcefile(S.FILES,PORIGIN 1 eps)',
        '~$error_context_valid(S,pcallcontext[.LINE = 1])',
        '~$error_context_valid(S,pcallcontext[.CALLSITE = eps])',
        'S_scope = $constant_frame_scope(S,pframe,pframe_tail*)',
        '$error_entered_call_valid(S_scope,perrorcall)',
        '~$error_entered_call_valid(S_scope,perrorcall[.LINE = 9])',
        '~$error_entered_call_valid(S_scope,perrorcall[.RESUME = DECL_NOTICE_RESUME pdeclnoticebatch[.INDEX = 0]])',
        '~$eval_compile_owners_valid(S[.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: S.TODO])',
        'ptraceframe_eval = $eval_row($eval_exception_trace(S))',
        '~ptraceframe_eval.HASARGS', 'ptraceframe_eval.ARGS = eps',
    ]),
    'iterator': ('normal', [
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = pframe :: pframe_handler :: pframe_tail*',
        'pframe.TODO = (USERITER_RESULT n n_object statement porigin_site z "current" poperand) :: ptask_saved*',
    ], [
        '$call_tasks_valid(S,S.TODO)', '$call_frames_valid(S,S.FRAMES)', '$call_current_valid(S)',
        '$heap_valid($heap_graph(S))', '$eval_compile_owners_valid(S)',
        '$useriter_frame(S,pcallcontext,pframe)', '$useriter_chain_valid(S,S.CURRENT,S.FRAMES)',
        'S.OBJECTS[n_object] = INSTANCE porigin_a', '$class_at(S.CLASSES,porigin_a) = (pclassdesc_a)',
        'pclassdesc_a.NAME = $ptascii("A")', '(HOBJECT n_object) <- $heap_graph(S).ROOTS',
        'pframe.CONTEXT = (pcallcontext_handler)', '$error_context_valid(S,pcallcontext_handler)',
        'pcallcontext_handler.LINE = 9', '~$declaration_unit_complete(S.DECLARATIONS,1)',
        '$class_named(S.CLASSNAMES,$ptascii("b")) = eps',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (EVAL_COMPILE_RESUME pevalcompile) :: ptask_handler*',
        'pevalcompile.PLAN.UNIT = 1',
    ]),
    'nested': ('nested', [
        'S.TODO = (DECL_NOTICES pdeclnoticebatch_inner) :: (EVAL_COMPILE_RESUME pevalcompile_inner) :: ptask_inner*',
        'pdeclnoticebatch_inner.KIND = NOTICE_EVAL 2 n_ordinal_inner',
        'S.CURRENT = (pcallcontext_outer)', 'S.FRAMES = pframe_outer :: eps',
        'pframe_outer.TODO = (ERROR_HANDLER_RESULT perrorcall_outer) :: (EVAL_COMPILE_RESUME pevalcompile_outer) :: ptask_outer*',
    ], [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))', '$eval_compile_owners_valid(S)',
        'S.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_outer :: eps',
        'pevalcontext_inner.UNIT = 2', 'pevalcontext_outer.UNIT = 1',
        'pevalcontext_inner.OWNER = 1', 'pevalcontext_outer.OWNER = 0',
        'pevalcontext_inner.PHASE = EVAL_COMPILE', 'pevalcontext_outer.PHASE = EVAL_COMPILE',
        'pevalcompile_inner.PLAN.UNIT = 2', 'pevalcompile_outer.PLAN.UNIT = 1',
        '$eval_compile_cursor_valid(S,pevalcompile_inner)', '$eval_compile_cursor_valid(S,pevalcompile_outer)',
        '$eval_compile_waiting(S.DECLARATIONS) = (2,n_cp_inner,n_diag_inner,n_ordinal_inner,pdeclnoticeitem_inner*) :: (1,n_cp_outer,n_diag_outer,n_ordinal_outer,pdeclnoticeitem_outer*) :: eps',
        '$class_named(S.CLASSNAMES,$ptascii("a")) =/= eps',
        '$class_named(S.CLASSNAMES,$ptascii("innerit")) =/= eps',
        '$class_named(S.CLASSNAMES,$ptascii("b")) = eps',
        '~$declaration_unit_complete(S.DECLARATIONS,1)', '~$declaration_unit_complete(S.DECLARATIONS,2)',
        'S_moved = S[.TODO = (EVAL_COMPILE_RESUME pevalcompile_outer) :: S.TODO][.FRAMES = [pframe_outer[.TODO = (ERROR_HANDLER_RESULT perrorcall_outer) :: ptask_outer*]]]',
        '$eval_state_valid(S_moved)', '$eval_compile_cursor_valid(S_moved,pevalcompile_outer)',
        '$heap_graph(S_moved) = $heap_graph(S)', '~$eval_compile_owners_valid(S_moved)',
        '~$eval_compile_owners_valid(S[.TODO = (EVAL_COMPILE_RESUME pevalcompile_outer) :: S.TODO])',
    ]),
    'throw': ('throw', [
        'S.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
        'pevalcompile.PENDING = THROWING n_object',
    ], [
        '$call_tasks_valid(S,S.TODO)', '$call_frames_valid(S,S.FRAMES)', '$call_current_valid(S)',
        '$eval_compile_owners_valid(S)', '$eval_compile_cursor_valid(S,pevalcompile)',
        '$heap_valid($heap_graph(S))', '$throwable_member(S,n_object)',
        '(HOBJECT n_object) <- $heap_graph(S).ROOTS',
        '$heap_owners($heap_graph(S),HOBJECT n_object) = 1',
        '$task_nodes(EVAL_COMPILE_RESUME pevalcompile) = [HOBJECT n_object]',
        'S.CURRENT = eps', 'S.FRAMES = eps',
        '~$declaration_unit_complete(S.DECLARATIONS,1)',
        '$class_named(S.CLASSNAMES,$ptascii("a")) =/= eps', '$class_named(S.CLASSNAMES,$ptascii("b")) = eps',
        '$throwable_field(S,n_object,"message") = PSTRING $ptascii("held")',
        'S_lost = S[.TODO = ptask_tail*]',
        '$heap_owners($heap_graph(S_lost),HOBJECT n_object) = 0', '~$eval_compile_owners_valid(S_lost)',
        'n_dead = (|S.OBJECTS|)',
        '~$eval_compile_cursor_valid(S,pevalcompile[.PENDING = THROWING n_dead])',
    ]),
    'fatal-teardown': ('fatal', [
        'S.TODO = [ERROR_UNWIND (USERFATAL ptbytes z_fatal b)]',
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = pframe :: eps',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (EVAL_COMPILE_RESUME pevalcompile) :: ptask_saved*',
    ], [
        '$call_descriptors_valid(S)', '$declaration_entry_check(S).COMPLETION = S.COMPLETION',
        '$heap_valid($heap_graph(S))', '$eval_compile_owners_valid(S)',
        'S.EVALCONTEXTS = pevalcontext :: eps', 'pevalcontext.PHASE = EVAL_COMPILE',
        'pevalcontext.UNIT = 1', 'pevalcontext.OWNER = 0',
        'pevalcompile.PLAN.UNIT = 1', 'ptask_saved* = (EVAL_COMPILE_END 1) :: pevalcontext.TAIL',
        '$eval_owner_marker_count(S,pevalcontext) = 1',
        '$class_named(S.CLASSNAMES,$ptascii("a")) =/= eps',
        '$class_named(S.CLASSNAMES,$ptascii("b")) = eps',
        '~$declaration_unit_complete(S.DECLARATIONS,1)',
        'S_restored = $drive_steps(S[.COMPLETION = NORMAL],1)',
        'S_restored.TODO = [ERROR_UNWIND (USERFATAL ptbytes z_fatal b)]',
        'S_restored.CURRENT = eps', 'S_restored.FRAMES = eps', 'S_restored.EVALCONTEXTS = eps',
        '$eval_compile_cursors(S_restored) = eps', '$eval_compile_owners_valid(S_restored)',
        '$eval_state_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
        '~$eval_state_valid(S_restored[.EVALCONTEXTS = [pevalcontext]])',
        'S_done = $drive_steps(S_restored[.COMPLETION = NORMAL],2000)',
        'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes z_fatal', 'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
        'S_done.EVALCONTEXTS = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.TODO = eps',
        '$eval_compile_cursors(S_done) = eps', '$eval_compile_owners_valid(S_done)',
        '$eval_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        'S_done.DECLARATIONS = S.DECLARATIONS',
        '$class_named(S_done.CLASSNAMES,$ptascii("b")) = eps',
    ]),
    'formatter': ('formatter', [
        'S.CURRENT = (pcallcontext_current)', 'S.FRAMES = pframe_active :: pframe :: pframe_tail*',
        'pframe_active.CONTEXT = (pcallcontext)',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site z) :: (EVAL_COMPILE_FATAL pevalcompilefatal) :: ptask_tail*',
        '$class_named(S.CLASSNAMES,$ptascii("rendered")) = (porigin_rendered)',
    ], [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$eval_compile_owners_valid(S)', '$eval_compile_fatal_valid(S,pevalcompilefatal)',
        '$eval_compile_string_frame(S,(pcallcontext),pframe,porigin_site,z)',
        'pevalcompilefatal.CURSOR.PLAN.UNIT = 1', 'pevalcompilefatal.CURSOR.CHECKPOINT = 2',
        'pevalcompilefatal.CURSOR.PENDING = THROWING n_object',
        '$eval_binding_at(S.EVALBINDINGS,1) = (pevalbinding)',
        'porigin_site = pevalbinding.SITE', 'z = 7',
        'pcallcontext.CALLSITE = (porigin_site)', 'pcallcontext.LINE = z',
        '$function_at(S.FUNCTIONS,pcallcontext_current.FUNCTION) = (pfunction_current)',
        'pfunction_current.NAME = $ptascii("publish")',
        '$formatter_publication_has(S.DECLARATIONS,porigin_rendered)',
        '$context_target(pcallcontext) = METHOD_TARGET n_object porigin_method',
        'S.OBJECTS[n_object] = INSTANCE porigin_class',
        '$effective_method(S,porigin_class,$ptascii("__toString"),|S.CLASSES|) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$task_nodes(EVAL_COMPILE_FATAL pevalcompilefatal) = [HOBJECT n_object]',
        '$class_named(S.CLASSNAMES,$ptascii("a")) =/= eps',
        '$class_named(S.CLASSNAMES,$ptascii("b")) = eps',
        'pevalcompilefatal.PREFIX = [METHOD_NOTICE pdeclnotice]', 'pdeclnotice.LINE = 2',
        '~$eval_compile_string_frame(S,(pcallcontext[.LINE = 0]),pframe,porigin_site,0)',
        '~$eval_compile_string_frame(S,(pcallcontext[.CALLSITE = (porigin_method)]),pframe,porigin_method,z)',
        'pevalcompilefatal_forged = pevalcompilefatal[.PREFIX = eps]',
        'S_forged = S[.DECLARATIONS = $forge_prefix(S.DECLARATIONS)][.FRAMES = pframe_active :: pframe[.TODO = (STRINGIFY_RESULT n_object porigin_site z) :: (EVAL_COMPILE_FATAL pevalcompilefatal_forged) :: ptask_tail*] :: pframe_tail*]',
        '$eval_compile_fatal_valid(S_forged,pevalcompilefatal_forged)',
        '$heap_graph(S_forged) = $heap_graph(S)',
        '$declaration_entry_check(S_forged).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
        '~$eval_compile_owners_valid(S[.TODO = (EVAL_COMPILE_FATAL pevalcompilefatal) :: S.TODO])',
    ]),
    'nested-fatal': ('nested-fatal', [], []),
    'file-public': ('file-fatal', [], []),
    'file-history-retirement': ('file-fatal', [], []),
}


REPORT_CHECKS = [
    'S_report.COMPLETION = REQUESTFATAL ptbytes_class ptbytes_message z_fatal',
    '$shutdown_compiler_snapshot(pevalcompilefatal.COMPLETION) = (S_report.COMPLETION)',
    '~S_report.COMPILESTOP', 'S_report.SERVICELEFT = eps', 'S_report.TODO = eps',
    'S_report.EVALCONTEXTS = [pevalcontext_outer]',
    '$call_descriptors_valid(S_report)', '$heap_valid($heap_graph(S_report))',
    '$eval_compile_owners_valid(S_report)', '$eval_state_valid(S_report)',
    '$eval_compile_cursors(S_report) = [pevalcompilefatal.CURSOR]',
    '$class_named(S_report.CLASSNAMES,$ptascii("a")) =/= eps',
    '$class_named(S_report.CLASSNAMES,$ptascii("b")) = eps',
    '$class_named(S_report.CLASSNAMES,$ptascii("innerbad")) = eps',
    'S_report.TRACE = [ptraceframe]', 'ptraceframe.FUNCTION = $ptascii("__toString")', 'ptraceframe.LINE = 6',
]
RETIRE_CHECKS = [
    'S_unwind = $start_error_unwind(S_report)',
    'S_unwind.TODO = [ERROR_UNWIND S_report.COMPLETION]',
    '$eval_state_valid(S_unwind)', '$eval_compile_owners_valid(S_unwind)',
    'S_restored = $drive_steps(S_unwind,1)',
    'S_restored.TODO = [ERROR_UNWIND S_report.COMPLETION]',
    'S_restored.FRAMES = eps', 'S_restored.CURRENT = eps', 'S_restored.EVALCONTEXTS = eps',
    '$eval_compile_cursors(S_restored) = eps', '$eval_compile_owners_valid(S_restored)',
    '$eval_state_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
    '~$eval_state_valid(S_restored[.EVALCONTEXTS = [pevalcontext_outer]])',
    'S_done = $drive_steps(S_restored[.COMPLETION = NORMAL],2000)',
    'S_done.COMPLETION = S_report.COMPLETION', r'S_done.SHUTDOWN.PHASE = SHUTDOWN_PENDING /\ S_done.SHUTDOWN.ENTRIES = eps',
    'S_done.EVALCONTEXTS = eps', 'S_done.TODO = eps', '$eval_compile_cursors(S_done) = eps',
    '$eval_compile_owners_valid(S_done)', '$eval_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    'S_done.DECLARATIONS = S_report.DECLARATIONS',
]

def prepare_packets(path, directory, units):
    frontend = Worker([str(source.driver.types.PHP), '-n', *source.driver.types.FLAGS,
                       '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], directory / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': source.driver.b64(path.read_bytes())})
        assert parsed['accepted'], parsed
        main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
        responses = []
        for n, (kind, code) in enumerate(units, 1):
            request = {'op': 'parse' if kind == 'file' else 'parse-eval',
                       'source': source.driver.b64(code.encode())}
            if kind != 'file':
                request.update(id=str(n), mode='eval', profile='cli-raw-85')
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            responses.append('(SOURCE_ACCEPT ' + str(n) + ' (' + str(list(code.encode())) + ') ' + checked['fixture'] + ')')
        return main, responses
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def assertions(main, responses, path, directory, name):
    case, stage, checks = STAGES[name]
    start = '$php_file_run(' + main + ',0,' + source.driver.byte_expr(os.fsencode(path)) + ',' + source.driver.byte_expr(os.fsencode(directory)) + ')'
    conditions = ['S_initial = ' + start, 'S_wait = $await(S_initial[.COMPLETION = NORMAL],600)',
                  'S_wait.COMPLETION = SOURCE_PENDING', 'S_compiled = $eval_resume(S_wait,' + responses[0] + ')',
                  'S_compiled.COMPLETION = NORMAL']
    if case == 'nested-fatal':
        conditions += ['S_inner_wait = $await(S_compiled,800)', 'S_inner_wait.COMPLETION = SOURCE_PENDING',
                       'S_inner_wait.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_outer :: eps',
                       'pevalcontext_inner.UNIT = 2', 'pevalcontext_inner.PHASE = PARSER_WAIT',
                       'pevalcontext_outer.UNIT = 1', 'pevalcontext_outer.PHASE = EVAL_COMPILE',
                       '$eval_compile_fatal_current(S_inner_wait) = (pevalcompilefatal)',
                       'pevalcompilefatal.CURSOR.PLAN.UNIT = 1',
                       'pevalcompilefatal.CURSOR.PENDING = THROWING n_object',
                       'S_report = $eval_resume(S_inner_wait,' + responses[1] + ')']
        return stage, conditions + REPORT_CHECKS + RETIRE_CHECKS
    if case == 'file-fatal':
        child = directory / 'bad.php'
        seq = source.driver.byte_expr
        conditions += ['S_resolve = $await(S_compiled,800)', 'S_resolve.COMPLETION = SOURCE_PENDING',
                       'S_resolve.FILECONTEXTS = [pfilecontext]',
                       'pfilecontext.PHASE = FILE_RESOLVE_WAIT', 'pfilecontext.UNIT = eps',
                       'pfilecontext.REQUESTED = ' + seq(os.fsencode(child)),
                       '$eval_compile_fatal_current(S_resolve) = (pevalcompilefatal)',
                       'pevalcompilefatal.CURSOR.PLAN.UNIT = 1',
                       'pevalcompilefatal.CURSOR.PENDING = THROWING n_object',
                       'S_resolve.EVALCONTEXTS = [pevalcontext_outer]', 'pevalcontext_outer.UNIT = 1',
                       'S_parse = $file_open_resume(S_resolve,FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED (' + seq(os.fsencode(child)) + ') (' + seq(os.fsencode(child)) + ') (' + seq(child.read_bytes()) + '))',
                       'S_parse.COMPLETION = SOURCE_PENDING', 'S_parse.FILECONTEXTS = [pfilecontext_parse]',
                       'pfilecontext_parse.UNIT = (2)', 'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
                       'S_report = $file_parse_resume(S_parse,' + responses[1] + ')']
        file_checks = ['S_report.FILECONTEXTS = eps',
                       '$file_binding_at(S_report.FILEBINDINGS,2) = (pfilebinding)',
                       'pfilebinding.SITE = pfilecontext.SITE',
                       'pfilebinding.OPENED = ' + seq(os.fsencode(child)),
                       'pdeclaration_forged* = $forge_file_exit(S_report.DECLARATIONS)',
                       'pdeclaration_forged* =/= S_report.DECLARATIONS',
                       '$declaration_entry_check(S_report[.DECLARATIONS = pdeclaration_forged*]).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
                       'S_unwind = $start_error_unwind(S_report)',
                       '$eval_state_valid(S_unwind)', '$eval_compile_owners_valid(S_unwind)',
                       'S_restored = $drive_steps(S_unwind,1)',
                       'S_restored.FRAMES = eps', 'S_restored.CURRENT = eps',
                       'S_restored.EVALCONTEXTS = eps',
                       '$eval_compile_cursors(S_restored) = eps', '$eval_compile_owners_valid(S_restored)',
                       '$eval_state_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
                       '~$eval_state_valid(S_restored[.EVALCONTEXTS = [pevalcontext_outer]])',
                       'S_restored.FILECONTEXTS = eps']
        if name == 'file-public':
            return stage, conditions + REPORT_CHECKS + file_checks[:4]
        live_checks = [check for check in REPORT_CHECKS[:11]
                       if check != '$call_descriptors_valid(S_report)']
        return stage, conditions + live_checks + file_checks[:1] + file_checks[4:]
    if case == 'nested':
        conditions += ['S_inner_wait = $await(S_compiled,800)', 'S_inner_wait.COMPLETION = SOURCE_PENDING',
                       'S_inner_compiled = $eval_resume(S_inner_wait,' + responses[1] + ')',
                       'S_inner_compiled.COMPLETION = NORMAL', 'S = $seek(S_inner_compiled,100)']
    else:
        conditions += ['S = $seek(S_compiled,800)']
    return stage, conditions + [r'S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET', *stage, *checks]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', help='Comma-separated phase IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(STAGES)
    assert names and len(names) == len(set(names)) and all(name in STAGES for name in names)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    out = Path(tempfile.mkdtemp(prefix='eval-notice-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
              ROOT / 'tests/semantics/iterator_declaration_notices.py',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'assertions': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': source.driver.types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'inputs': before}
    print(out, flush=True)
    try:
        report['runtime'] = source.runtime(out)
        for name in names:
            directory = out / name
            directory.mkdir()
            case, _, _ = STAGES[name]
            text, units, expected = cases[case]
            path = directory / 'source.php'
            path.write_text(text)
            for kind, code in units:
                if kind == 'file':
                    (directory / 'bad.php').write_text(code)
            native = source.process([str(source.driver.types.PHP), '-n', *source.driver.types.FLAGS, str(path)], directory / 'native', 10, directory)
            fatal = case in ['fatal', 'formatter', 'nested-fatal', 'file-fatal']
            assert native.returncode == (255 if fatal else 0) and native.stdout == expected, (name, native.returncode, native.stdout, native.stderr)
            if case == 'fatal':
                assert b'Fatal error: stop in ' + os.fsencode(path) + b' on line 5\n' in native.stderr
            elif fatal:
                assert b'Declaration of B::next($x): void must be compatible with Iterator::next(): void' in native.stderr
                if case in ['nested-fatal', 'file-fatal']:
                    assert b'InnerBad' not in native.stderr
            else:
                assert not native.stderr, (name, native.stderr)
            checked, responses = prepare_packets(path, directory, units)
            stage, checks = assertions(checked, responses, path, directory, name)
            fixture = directory / 'protocol.watsup'
            fixture.write_text('dec $stage(pstate) : bool\ndef $stage(S) = true\n' +
                               ''.join('  -- if ' + item + '\n' for item in stage) +
                               'def $stage(S) = false -- otherwise\n' + PREFIX +
                               '\ndec $body() : bool\ndef $body() = true\n' +
                               ''.join('  -- if ' + item + '\n' for item in checks) +
                               '\ndec $main() : bool\ndef $main() = ' + ('true' if args.mode == 'prepare' else '$body()') + '\n')
            (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            runtime_mode = 'SL' if name in ['file-public', 'file-history-retirement'] else 'AL'
            row = {'id': name, 'assertions': len(checks), 'evaluated': args.mode == 'check',
                   'runtime_mode': runtime_mode}
            report['records'].append(row)
            if args.mode != 'fixtures':
                if runtime_mode == 'AL':
                    source.driver.numeric(fixture, directory)
                else:
                    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
                    result = source.driver.process(
                        [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                         *[str(ROOT / module) for module in modules], str(fixture)],
                        directory / 'numeric', 300, ROOT)
                    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['assertions'] += len(checks) if args.mode == 'check' else 0
            row['passed'] = True
            print(name, args.mode, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['stable_inputs'] = before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
