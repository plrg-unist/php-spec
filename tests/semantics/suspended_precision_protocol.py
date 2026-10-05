#!/usr/bin/env python3
"""Source-derived later-fold precision, image, array and callback controls."""
from pathlib import Path
import argparse
import hashlib
import subprocess
import base64
import json
import re
import sys
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('suspended_precision')

B64 = lambda value: base64.b64encode(value).decode()
HELPERS = '''
dec $epoch_without(pnode*, pnode) : pnode*
def $epoch_without(eps, pnode) = eps
def $epoch_without(pnode :: pnode_tail*, pnode) = $epoch_without(pnode_tail*, pnode)
def $epoch_without(pnode_other :: pnode_tail*, pnode) = pnode_other :: $epoch_without(pnode_tail*, pnode)
  -- if pnode_other =/= pnode
dec $epoch_ready(pstate, nat) : bool
def $epoch_ready(S, n) = true
  -- if S.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*
  -- if $eval_precision_epochs(S.DECLARATIONS, pevalcompile.PLAN.UNIT) = (epochs)
  -- if |epochs| = n
def $epoch_ready(S, n) = false -- otherwise
dec $epoch_seek(pstate, nat, nat) : pstate
def $epoch_seek(S, n_epoch, n) = S -- if $epoch_ready(S, n_epoch)
def $epoch_seek(S, n_epoch, n) = S
  -- if ~$epoch_ready(S, n_epoch)
  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET
def $epoch_seek(S, n_epoch, 0) = S
  -- if ~$epoch_ready(S, n_epoch)
  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET
def $epoch_seek(S, n_epoch, n) = $epoch_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_epoch, $nabs($(n - 1)))
  -- if ~$epoch_ready(S, n_epoch)
  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $epoch_meta_tag(pconstant) : bool
dec $epoch_meta(pconstant*) : pconstant?
def $epoch_meta((PCCPRECISION pcpath z) :: pconstant*) = (PCCPRECISION pcpath z)
def $epoch_meta(pconstant :: pconstant_tail*) = $epoch_meta(pconstant_tail*)
  -- if ~$epoch_meta_tag(pconstant)
def $epoch_meta(eps) = eps
def $epoch_meta_tag(PCCPRECISION pcpath z) = true
def $epoch_meta_tag(pconstant) = false -- otherwise
dec $epoch_meta_replace(pconstant*, pconstant) : pconstant*
def $epoch_meta_replace((PCCPRECISION pcpath z) :: pconstant*, pconstant_new) = pconstant_new :: pconstant*
def $epoch_meta_replace(pconstant :: pconstant_tail*, pconstant_new) = pconstant :: $epoch_meta_replace(pconstant_tail*, pconstant_new)
  -- if ~$epoch_meta_tag(pconstant)
def $epoch_meta_replace(eps, pconstant) = eps
dec $epoch_meta_remove(pconstant*) : pconstant*
def $epoch_meta_remove((PCCPRECISION pcpath z) :: pconstant*) = $epoch_meta_remove(pconstant*)
def $epoch_meta_remove(pconstant :: pconstant_tail*) = pconstant :: $epoch_meta_remove(pconstant_tail*)
  -- if ~$epoch_meta_tag(pconstant)
def $epoch_meta_remove(eps) = eps
'''

KEY_HELPERS = '\ndec $key_ready(pstate) : bool\ndef $key_ready(S) = true\n  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*\n  -- if S.ORIGIN = (porigin_user)\n  -- if $class_at(S.CLASSES,porigin_user) = (pclassdesc_user)\n  -- if pclassdesc_user.NAME = $ptascii("PrecisionKeyUser")\ndef $key_ready(S) = false -- otherwise\ndec $key_seek(pstate,nat) : pstate\ndef $key_seek(S,n) = S -- if $key_ready(S)\ndef $key_seek(S,n) = S\n  -- if ~$key_ready(S)\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $key_seek(S,0) = S\n  -- if ~$key_ready(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\ndef $key_seek(S,n) = $key_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))\n  -- if ~$key_ready(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\n'

def seed(name):
    body = B64(BODIES[name])
    return [f'S_open = $php_precision_run(program_main,1000,"{B64(bytes(PATHS[name]))}",eps,false,eps,$ptascii("5junk"))',
            'S_open.COMPLETION = SOURCE_PENDING',
            '$declaration_precision(S_open.DECLARATIONS,1) = (3)',
            f'S_ready = $epoch_seek($eval_resume(S_open,(SOURCE_ACCEPT 1 $base64("{body}") program_body)),0,1000)',
            'S_ready.COMPLETION = BUDGET',
            'S_ready.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
            '$eval_compile_cursor_valid(S_ready,pevalcompile)',
            '$call_descriptors_valid(S_ready)',
            '$source_precision(S_ready,(PORIGIN 1 eps)) = (3)',
            '$precision_value(S_ready) = 1',
            '~$precision_eval_resume_valid(S_ready,pevalcompile)',
            '$drive_steps(S_ready[.COMPLETION = NORMAL],0)[.COMPLETION = BUDGET] = S_ready',
            '$source_unit(S_ready.SOURCES,1) = (pcunit)',
            'P_old = $declaration_compiler_state($eval_source_ppstate(S_ready,pcunit))',
            '$compilation_image_valid(S_ready,pcunit,P_old)',
            'S_resumed = $drive_steps(S_ready[.COMPLETION = NORMAL],1)',
            'S_resumed.COMPLETION = BUDGET',
            '$eval_precision_epochs(S_resumed.DECLARATIONS,1) = ([(pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,1)])',
            '$declaration_precision(S_resumed.DECLARATIONS,1) = (3)',
            'P_new = $declaration_compiler_state($eval_source_ppstate(S_resumed,pcunit))',
            '$eval_compile_precision_prefix(P_old,P_new,pevalcompile)',
            '$compilation_image_valid(S_resumed,pcunit,P_new)',
            '$call_descriptors_valid(S_resumed)']

PATHS = {name: SOURCES / filename for name,filename in [
    ('arrays','arrays.php'), ('child','child-warning.php'), ('throw','throw.php'), ('exit','exit.php'),
    ('chronology','main.php'), ('names','names.php'), ('trait','trait-bound.php')]}
PATHS['key'] = SOURCES / 'trait-key.php'
PATHS['legacy'] = R / 'tests/semantics/precision/state/early.php'
BODIES = {}
for name, path in PATHS.items():
    if name == 'key':
        continue
    if name == 'legacy':
        BODIES[name] = b'function precisionPaused($x){return "${x}";} class PrecisionLater {}'
    else:
        match = re.search(rb"<<<'PHP'\n(.*?)\nPHP", path.read_bytes(), re.S)
        assert match, name
        BODIES[name] = match.group(1)

CHECKS = {}
CHECKS['arrays'] = seed('arrays') + [
    '$quiet_name(S_ready,$ptascii("escaped" )).RESULT = KNOWN (PARRAY n_escaped)',
    '$quiet_name(S_ready,$ptascii("allocated" )).RESULT = KNOWN (PARRAY n_callback)',
    'n_escaped =/= n_callback',
    '$quiet_name(S_resumed,$ptascii("escaped" )).RESULT = KNOWN (PARRAY n_escaped)',
    '$quiet_name(S_resumed,$ptascii("allocated" )).RESULT = KNOWN (PARRAY n_callback)',
    'S_resumed.ARRAYS[n_escaped] = S_ready.ARRAYS[n_escaped]',
    'S_resumed.ARRAYS[n_callback] = S_ready.ARRAYS[n_callback]',
    '(HARRAY n_escaped) <- S_resumed.ALLOCATIONS /\\ (HARRAY n_callback) <- S_resumed.ALLOCATIONS',
    '$pool_at(S_ready.POOLS,1) = (ppool_old)',
    '$pool_at(S_resumed.POOLS,1) = (ppool_new)',
    '$compilation_correspondence(S_ready,P_old.INSTALLED,ppool_old.CONSTANTS) = (pcompilemap_old)',
    '$compilation_correspondence(S_resumed,P_new.INSTALLED,ppool_new.CONSTANTS) = (pcompilemap)',
    'pcompilemap = (n_first,n_live_first) :: (n_second,n_live_second) :: pcompilemap_tail',
    'n_live_first =/= n_live_second',
    '|pcompilemap| = |P_new.INSTALLED.ALLOCATIONS|',
    '$compilation_map_arrays(S_resumed,P_new.INSTALLED.ARRAYS,P_new.INSTALLED.ALLOCATIONS,pcompilemap)',
    'pcompilemap_bad = (n_first,n_live_first) :: (n_second,n_live_first) :: pcompilemap_tail',
    '$compilation_correspondence(S_resumed,P_new.INSTALLED,$compilation_map_constants(P_new.INSTALLED.CONSTANTS,pcompilemap_bad)) = eps',
    '~$compilation_map_arrays(S_resumed[.ARRAYS[n_live_first].NEXT = $(S_resumed.ARRAYS[n_live_first].NEXT + 1)],P_new.INSTALLED.ARRAYS,P_new.INSTALLED.ALLOCATIONS,pcompilemap)',
    '~$compilation_map_arrays(S_resumed[.ARRAYS[n_live_first].SERIAL = $nabs($(S_resumed.ARRAYS[n_live_first].SERIAL + 1))],P_new.INSTALLED.ARRAYS,P_new.INSTALLED.ALLOCATIONS,pcompilemap)',
    '~$compilation_map_arrays(S_resumed[.ALLOCATIONS = $epoch_without(S_resumed.ALLOCATIONS,HARRAY n_live_first)],P_new.INSTALLED.ARRAYS,P_new.INSTALLED.ALLOCATIONS,pcompilemap)',
    '$epoch_meta(ppool_new.CONSTANTS) = (PCCPRECISION pcpath_precision z_precision)',
    'z_precision = 1',
    '$compiled_precision(S_resumed,(PORIGIN 1 pcpath_precision)) = (1)',
    '$compilation_correspondence(S_resumed,P_new.INSTALLED,$epoch_meta_replace(ppool_new.CONSTANTS,PCCPRECISION pcpath_precision 2)) = eps',
    '$compilation_correspondence(S_resumed,P_new.INSTALLED,$epoch_meta_remove(ppool_new.CONSTANTS)) = eps',
    '$eval_precision_epochs(S_resumed.DECLARATIONS ++ [PDEVALRESUMEPRECISION 1 S_resumed.REPORTING 2],1) = eps',
    '~$eval_compile_cursor_valid(S_ready,pevalcompile[.CHECKPOINT = $(pevalcompile.CHECKPOINT + 1)])',
    '~$eval_compile_cursor_valid(S_ready,pevalcompile[.DIAGNOSTIC = $(pevalcompile.DIAGNOSTIC + 1)])',
    '~$eval_compile_cursor_valid(S_ready,pevalcompile[.PLAN.UNIT = 0])',
    '$precision_resume_value(S_ready,1,pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,eps) = (3)',
    '$precision_resume_value(S_ready,1,pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,(3)) = eps',
    '$precision_resume_input(PDEVALRESUMEPRECISION 1 30719 (-2)) = eps',
    '$precision_resume_input(PDEVALRESUMEPRECISION 1 30719 9223372036854775808) = eps',
    'S_done = $drive(S_resumed[.COMPLETION = NORMAL],1000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.EVALCONTEXTS = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
CHECKS['child'] = seed('child') + [
    'F_scratch = $pfbegin(0,program_main)[.PARSEPRECISION = 3][.MEMORY = $precision_memory($initial_state(NORMAL),1)]',
    '$pfcompiler_precision(F_scratch) = F_scratch',
    'epochs_empty = eps',
    'F_compiler = F_scratch[.COMPILEPRECISIONS = (epochs_empty)]',
    '$precision_value($pfcompiler_precision(F_compiler).MEMORY) = 3',
    '$pool_at(S_resumed.POOLS,1) = (ppool)',
    '$epoch_meta(ppool.CONSTANTS) = (PCCPRECISION pcpath z)',
    'z = 1', '$compiled_precision(S_resumed,(PORIGIN 1 pcpath)) = (1)',
    '$source_precision(S_resumed,(PORIGIN 1 pcpath)) = (3)',
    'S_done = $drive(S_resumed[.COMPLETION = NORMAL],1000)',
    'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)',
    'porigin_concat = PORIGIN 1 ([PCINDEX 1,PCFIELD 0,PCFIELD 1])',
    '$origin_node(S_resumed.SOURCES,porigin_concat) = (NExprBinaryOpConcat expression_left expression_right metadata)',
    '$origin_child((porigin_concat),[PCFIELD 0]) = (porigin_left)',
    '$compiled_read(S_resumed,porigin_left) = (PFLOAT n_bits)',
    '$compiled_precision(S_resumed,(porigin_left)) = (1)',
    '$source_precision(S_resumed,(porigin_left)) = (3)']

# Later groups use the same immutable sources, with no new native claims.
# Pending states are inspected before normalization retires the genuine cursor.
for name, completion in [('throw', 'THROWING n'), ('exit', 'EXITED 0')]:
    rows = seed(name)
    rows += ['pevalcompile.PENDING = ' + completion,
             'S_done = $drive(S_resumed[.COMPLETION = NORMAL],1000)']
    if name == 'throw':
        rows += ['S_done.COMPLETION = NORMAL /\\ S_done.EVALCONTEXTS = eps',
                 '$eval_compile_cursors(S_done) = eps',
                 'S_done.FRAMES = eps', 'S_done.TODO = eps']
    else:
        rows += ['S_done.EVALCONTEXTS = eps', '$eval_compile_released(S_done)']
    rows += ['$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
    CHECKS[name] = rows


CHECKS['chronology'] = seed('chronology') + [
    'S_second = $epoch_seek(S_resumed,1,1000)',
    'S_second.COMPLETION = BUDGET',
    'S_second.TODO = (EVAL_COMPILE_RESUME pevalcompile_second) :: ptask_second_tail*',
    '$eval_compile_cursor_valid(S_second,pevalcompile_second)',
    '$call_descriptors_valid(S_second)',
    '$precision_value(S_second) = 2',
    '$source_precision(S_second,(PORIGIN 1 eps)) = (3)',
    '$precision_compiler_current(S_second,1,pevalcompile_second.CHECKPOINT,pevalcompile_second.DIAGNOSTIC) = (1)',
    '~$precision_eval_resume_valid(S_second,pevalcompile_second)',
    '$precision_resume_value(S_second,1,pevalcompile_second.CHECKPOINT,pevalcompile_second.DIAGNOSTIC,(1)) = eps',
    'S_final = $drive_steps(S_second[.COMPLETION = NORMAL],1)',
    'S_final.COMPLETION = BUDGET',
    '$eval_precision_epochs(S_final.DECLARATIONS,1) = (epochs)',
    'epochs = [(pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,1),(pevalcompile_second.CHECKPOINT,pevalcompile_second.DIAGNOSTIC,2)]',
    '$compiler_epoch_value(epochs,0,0,3) = 3',
    '$compiler_epoch_value(epochs,pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,3) = 1',
    '$compiler_epoch_value(epochs,pevalcompile_second.CHECKPOINT,pevalcompile_second.DIAGNOSTIC,3) = 2',
    '$compiled_precision(S_final,(PORIGIN 1 ([PCINDEX 2,PCFIELD 0,PCFIELD 1,PCFIELD 0]))) = (3)',
    '$compiled_precision(S_final,(PORIGIN 1 ([PCINDEX 5,PCFIELD 0,PCFIELD 1,PCFIELD 0]))) = (1)',
    '$compiled_precision(S_final,(PORIGIN 1 ([PCINDEX 8,PCFIELD 0,PCFIELD 1,PCFIELD 0]))) = (2)',
    '$call_descriptors_valid(S_final)',
    '~$call_descriptors_valid(S_final[.DECLARATIONS = S_final.DECLARATIONS ++ [PDEVALRESUMEPRECISION 1 S_final.REPORTING 2]])',
    'S_done = $drive(S_final[.COMPLETION = NORMAL],1000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.EVALCONTEXTS = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
CHECKS['names'] = seed('names') + [
    'porigin_name = PORIGIN 1 ([PCINDEX 1,PCFIELD 0,PCFIELD 0,PCFIELD 0])',
    '$compiled_read(S_resumed,porigin_name) = (PFLOAT n_bits_name)',
    '$compiled_precision(S_resumed,(porigin_name)) = (1)',
    '$source_precision(S_resumed,(porigin_name)) = (3)',
    '$compiled_name_bytes_at(PFLOAT n_bits_name,1) = $ptascii("1.0E+1")',
    '$compiled_name_bytes_at(PFLOAT n_bits_name,3) = $ptascii("12.3")',
    'S_name = S_resumed[.ORIGIN = (PORIGIN 1 ([PCINDEX 1,PCFIELD 0,PCFIELD 0]))]',
    '$captured_name(S_name,[PCFIELD 0],KNOWN (PFLOAT n_bits_name)) = KNOWN (PSTRING $ptascii("1.0E+1"))',
    'S_done = $drive(S_resumed[.COMPLETION = NORMAL],1000)',
    'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
CHECKS['trait'] = seed('trait') + [
    '$quiet_name(S_ready,$ptascii("held" )).RESULT = KNOWN (POBJECT n_held)',
    'S_ready.OBJECTS[n_held] = INSTANCE porigin_user',
    '$class_at(S_ready.CLASSES,porigin_user) = (pclassdesc_live)',
    '$class_at(P_old.INSTALLED.CLASSES,porigin_user) = (pclassdesc_pure)',
    'pclassdesc_live =/= pclassdesc_pure',
    '$(|pclassdesc_live.PROPERTIES| > |pclassdesc_pure.PROPERTIES|)',
    '$(|pclassdesc_live.CONSTANTS| > |pclassdesc_pure.CONSTANTS|)',
    '$class_at(P_new.INSTALLED.CLASSES,porigin_user) = (pclassdesc_pure)',
    '$class_at(S_resumed.CLASSES,porigin_user) = (pclassdesc_live)',
    '$quiet_name(S_resumed,$ptascii("held" )).RESULT = KNOWN (POBJECT n_held)',
    '$compilation_live_class(S_ready.CLASSES,P_old.INSTALLED.CLASSES,pclassdesc_pure) = (pclassdesc_live)',
    '$compilation_live_class(S_ready.CLASSES,P_old.INSTALLED.CLASSES,pclassdesc_pure[.NAME = $ptascii("forged")]) = eps',
    '$eval_compile_waiting(S_ready.DECLARATIONS) = (n_unit,n_checkpoint,n_diagnostic,n_ordinal,pdeclnoticeitem*) :: pevalcompileclaim*',
    'pdeclnoticeitem* =/= eps',
    '$eval_binding_at(S_ready.EVALBINDINGS,n_unit) = (pevalbinding)',
    '$declaration_compiler_callback_site(S_ready,pevalbinding.SITE)',
    '~$declaration_compiler_callback_site(S_open,pevalbinding.SITE)',
    'n_after = $nabs($(n_ordinal + 1))',
    'n_remaining = $nabs($(|S_ready.DECLARATIONS| - n_after))',
    'S_without = S_ready[.DECLARATIONS = S_ready.DECLARATIONS[0:n_ordinal] ++ S_ready.DECLARATIONS[n_after:n_remaining]]',
    '~$declaration_compiler_callback_site(S_without,pevalbinding.SITE)',
    '~$call_descriptors_valid(S_without)',
    '~$declaration_compiler_callback_site(S_ready[.DECLARATIONS = S_ready.DECLARATIONS ++ [PDEVALRESUMEPRECISION n_unit S_ready.REPORTING 1]],pevalbinding.SITE)',
    '~$declaration_compiler_callback_site(S_ready[.EVALBINDINGS = [pevalbinding[.SITE = PORIGIN 0 eps]]],pevalbinding.SITE)',
    'n_last = $nabs($(|S_ready.DECLARATIONS| - 1))',
    'S_ready.DECLARATIONS[n_last] = PDRCLASS porigin_user pdeclcause',
    '$declaration_cause_valid(S_ready,porigin_user,pdeclcause)',
    'pdeclcause.CALLS = (porigin_function,porigin_callsite?,porigin_lexical?,porigin_called?) :: (porigin_function_second,porigin_callsite_second?,porigin_lexical_second?,porigin_called_second?) :: pdeclcalls',
    'pdeclcalls = eps',
    '~$declaration_cause_valid(S_ready,porigin_user,pdeclcause[.CALLS = [(porigin_function,porigin_callsite?,porigin_lexical?,porigin_called?),(porigin_function,porigin_callsite_second?,porigin_lexical_second?,porigin_called_second?)]])',
    'S_done = $drive(S_resumed[.COMPLETION = NORMAL],1000)',
    'S_done.COMPLETION = NORMAL', '$class_at(S_done.CLASSES,porigin_user) = (pclassdesc_live)',
    '~$declaration_compiler_callback_site(S_done,pevalbinding.SITE)',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']

CHECKS['legacy'] = [
    'S_open = $php_precision_run(program_main,1000,"' + B64(bytes(PATHS['legacy'])) + '",eps,false,eps,$ptascii("5junk"))',
    'S_open.COMPLETION = SOURCE_PENDING',
    'S_ready = $epoch_seek($eval_resume(S_open,(SOURCE_ACCEPT 1 $base64("' + B64(BODIES['legacy']) + '") program_body)),0,1000)',
    'S_ready.COMPLETION = BUDGET',
    'S_ready.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
    '$eval_compile_cursor_valid(S_ready,pevalcompile)',
    '$precision_value(S_ready) = 1',
    '~$precision_eval_resume_valid(S_ready,pevalcompile)',
    'S_changed = $drive_steps(S_ready[.COMPLETION = NORMAL],1)',
    'S_changed.COMPLETION = BUDGET',
    '$eval_precision_epochs(S_changed.DECLARATIONS,1) = ([(pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,1)])',
    '$source_precision(S_changed,(PORIGIN 1 eps)) = (3)',
    '$call_descriptors_valid(S_changed)',
    'S_done = $drive(S_changed[.COMPLETION = NORMAL],1000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.EVALCONTEXTS = eps',
    '$eval_compile_cursors(S_done) = eps', 'S_done.FRAMES = eps', 'S_done.TODO = eps',
    '$call_descriptors_valid(S_done)']

CHECKS['key'] = [
    'S_initial = $php_precision_run(program_main,0,"' + B64(bytes(PATHS['key'])) + '",eps,false,eps,$ptascii("5junk"))',
    'S_pre = $key_seek(S_initial,1000)',
    'S_pre.COMPLETION = BUDGET',
    'S_pre.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*',
    'S_pre.ORIGIN = (porigin_user)',
    '$class_at(S_pre.CLASSES,porigin_user) = (pclassdesc_user)',
    'pclassdesc_user.NAME = $ptascii("PrecisionKeyUser")',
    'S = $activate_class(S_pre[.COMPLETION = NORMAL][.TODO = ptask_tail*],pclassdesc_user)',
    'S.COMPLETION = NORMAL',
    '$call_descriptors_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$source_precision(S,(PORIGIN 0 eps)) = (5)',
    '$precision_value(S) = 1',
    '$class_named(S.CLASSNAMES,$ptascii("precisionkeyowner")) = (porigin_owner)',
    '$class_at(S.CLASSES,porigin_owner) = (pclassdesc_owner)',
    '$class_constant_desc(pclassdesc_owner.CONSTANTS,$ptascii("VALUE")) = (pclassconstantdesc)',
    '$default_cache_at(S.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = (pdefaultcache)',
    '$trait_cache_event_at(S.CLASSCONSTANTHISTORY,pclassconstantdesc.ORIGIN) = (ptraitcachecause)',
    'porigin_first = $constant_child(pclassconstantdesc.INITIALIZER,[PCFIELD 0,PCINDEX 0,PCFIELD 0])',
    'porigin_second = $constant_child(pclassconstantdesc.INITIALIZER,[PCFIELD 0,PCINDEX 1,PCFIELD 0])',
    '$compiled_read(S,porigin_first) = eps',
    '$compiled_read(S,porigin_second) = eps',
    '$trait_cache_source_key(S,porigin_first,porigin_owner,ptraitcachecause.PREFIX) = (PSTRING $ptascii("12.346P2048"))',
    '$trait_cache_source_key(S,porigin_second,porigin_owner,ptraitcachecause.PREFIX) = (PSTRING $ptascii("22.346R2048"))',
    'S.DECLARATIONS = (PDENTERPRECISION 0 eps z_reporting 5) :: pdeclaration_tail*',
    'S_missing = S[.DECLARATIONS = pdeclaration_tail*]',
    '$source_precision(S_missing,(porigin_first)) = eps',
    '$trait_cache_source_key(S_missing,porigin_first,porigin_owner,ptraitcachecause.PREFIX) = eps',
]

def render(fixtures, group):
    function = 'key_program' if group == 'key' else 'epoch_main'
    prefix = f'dec ${function}() : program\ndef ${function}() = '+fixtures[group]+'\n'
    setup = [f'program_main = ${function}()']
    if group != 'key':
        prefix += 'dec $epoch_body() : program\ndef $epoch_body() = '+fixtures[group+'_body']+'\n'
        setup.append('program_body = $epoch_body()')
    main = [*setup, *CHECKS[group]]
    helpers = KEY_HELPERS if group == 'key' else HELPERS
    return (prefix + helpers + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if '+row+'\n' for row in main)
            + 'def $main() = false -- otherwise\n')


def prepare(directory):
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    flags = [arg for key,value in profile.items() for arg in ('-d',key+'='+value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags,
                       '-d', 'extension='+str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')],
                      directory / 'frontend')
    parsed = {}
    try:
        for name,path in PATHS.items():
            parsed[name] = frontend.request({'op':'parse','source':B64(path.read_bytes())})
            assert parsed[name]['accepted'], parsed[name]
            if name == 'key':
                continue
            parsed[name+'_body'] = frontend.request({'op':'parse-eval','id':'1','mode':'eval',
                'profile':'cli-raw-85','source':B64(BODIES[name])})
            assert parsed[name+'_body']['accepted'], parsed[name+'_body']
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], directory / 'syntax-adapter')
    fixtures = {}
    try:
        for name,item in parsed.items():
            fixtures[name] = adapter.request({'op':'check','ast':item['ast'],'fixture':True})['fixture']
    finally:
        adapter.close()
    for group in CHECKS:
        (directory/(group+'.watsup')).write_text(render(fixtures,group))
    metadata = {'counts':{k:len(v) for k,v in CHECKS.items()},
                'paths':{k:str(v) for k,v in PATHS.items()},
                'bodies':{k:B64(v) for k,v in BODIES.items()}}
    (directory/'prepared.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata


def main(groups):
    out = Path(tempfile.mkdtemp(prefix='suspended-precision-controls-',dir=R / '.tools'))
    print(out,flush=True)
    metadata = prepare(out)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    paths = [*modules, R / 'spec/semantics/modules.json', R / 'tests/semantics/numeric_runner.ml',
             types.RUNNER, R / '_build/default/adapter/main.exe', R / '.tools/php-file.so',
             R / '.tools/php/bin/php', R / 'tests/semantics/profile.json',
             R / 'tests/semantics/recorded_worker.py', R / 'tests/semantics/error_handler_run.py',
             Path(__file__), *PATHS.values(), *(out/(group+'.watsup') for group in groups)]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = {str(path):sha(path) for path in paths}
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    rows = []
    for group in groups:
        flags = ['--sl'] if group == 'key' else []
        result = recorded([str(types.RUNNER), *flags, *map(str,modules), str(out/(group+'.watsup'))],
                          out/group,90)
        passed = (result['exit']==0 and not result['timeout']
                  and (out/group).with_suffix('.stdout').read_bytes()==b'true\n'
                  and not (out/group).with_suffix('.stderr').read_bytes())
        rows.append({'group':group,'mode':'SL' if flags else 'AL','supplied_checks':metadata['counts'][group],
                     'program_bindings':1 if group=='key' else 2,'process':result,'passed':passed})
        print(group,passed,flush=True)
        if not passed:
            break
    stable = inputs=={str(path):sha(path) for path in paths}
    assert revision==subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    (out/'report.json').write_text(json.dumps({'revision':revision,'inputs':inputs,'rows':rows,
        'inputs_stable':stable,'supplied_checks':sum(metadata['counts'][group] for group in groups),
        'program_bindings':sum(1 if group=='key' else 2 for group in groups),'environment':{'LC_ALL':'C','TZ':'UTC','PHP_SPEC_SCRIPT_ENCODING':'absent'}},indent=2)+'\n')
    return stable and len(rows)==len(groups) and all(row['passed'] for row in rows)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group',action='append',choices=list(CHECKS))
    args = parser.parse_args()
    raise SystemExit(0 if main(args.group or list(CHECKS)) else 1)
