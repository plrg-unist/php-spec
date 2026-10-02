#!/usr/bin/env python3
"""Source-derived argument and owner guards for include_path intrinsics."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('no-file-chdir', b"<?php chdir('.'); echo 'X';",
     'S.COMPLETION = UNSUPPORTED "include_path intrinsic requires finite file mode"', [
         'S.COMPLETION = UNSUPPORTED "include_path intrinsic requires finite file mode"',
         'S.FILECWD = eps',
         'S.FILEINCLUDEPATH = eps',
         '$outputs(S.EVENTS) = eps',
     ]),
    ('direct', b"<?php echo set_include_path('sub');",
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING n_new*))]',
         '$config_invoke_valid(S,pconfigcall)',
         '$call_descriptors_valid(S)',
         '~$config_call_valid(S,pconfigcall[.LINE = 999])',
         '~$config_call_valid(S,pconfigcall[.KIND = INTRINSIC_INI_SET])',
         'S_bad = $drive(S[.TODO = (CONFIG_INVOKE pconfigcall[.LINE = 999]) :: ptask*],1000)',
         'S_bad.COMPLETION = UNSUPPORTED text',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.FILEINCLUDEPATH = ($ptascii("sub"))',
         '$outputs(S_done.EVENTS) = $ptascii(".:")',
     ]),
    ('first-class', b"<?php $f=set_include_path(...); echo $f('sub');",
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*',
         'pconfigcall.OWNER = (n_owner)',
         '(HOBJECT n_owner) <- $task_nodes(CONFIG_INVOKE pconfigcall)',
         '$config_selected_valid(S,pconfigcall)',
         '~$config_selected_valid(S,pconfigcall[.OWNER = (999)])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.FILEINCLUDEPATH = ($ptascii("sub"))',
     ]),
    ('unpack', b"<?php echo set_include_path(...['include_path'=>'sub']);",
     'S.TODO = (CONFIG_UNPACK_NEXT pconfigcall poperand 0) :: ptask*', [
         'S.TODO = (CONFIG_UNPACK_NEXT pconfigcall poperand 0) :: ptask*',
         '$config_unpack_valid(S,pconfigcall,poperand,0)',
         '$call_descriptors_valid(S)',
         '~$config_unpack_valid(S,pconfigcall,poperand,2)',
         '~$config_unpack_valid(S[.CODE = eps],pconfigcall,poperand,0)',
         'S_bad = $drive(S[.TODO = (CONFIG_UNPACK_NEXT pconfigcall poperand 2) :: ptask*],1000)',
         'S_bad.COMPLETION = UNSUPPORTED text',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.FILEINCLUDEPATH = ($ptascii("sub"))',
     ]),
    ('restore', b"<?php set_include_path('sub'); ini_restore('include_path');",
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*\n  -- if pconfigcall.KIND = INTRINSIC_INI_RESTORE', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*',
         'pconfigcall.KIND = INTRINSIC_INI_RESTORE',
         'S.FILEINCLUDEPATH = ($ptascii("sub"))',
         '$config_invoke_valid(S,pconfigcall)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.FILEINCLUDEPATH = ($ptascii(".:"))',
     ]),
    ('dynamic-bound', b"<?php $f='ini_restore'; $f('include_path');",
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*',
         'pconfigcall.KIND = INTRINSIC_INI_RESTORE',
         'pconfigcall.OWNER = eps',
         'pconfigcall.SELECTION = (n_nonce)',
         'S.SELECTEDCALLS = [pselectedcall]',
         'pselectedcall.NONCE = n_nonce',
         'pselectedcall.KIND = INTRINSIC_INI_RESTORE',
         'pselectedcall.LOOKUP = $ptascii("ini_restore")',
         '$config_selected_valid(S,pconfigcall)',
         '$call_descriptors_valid(S)',
         '~$config_call_valid(S,pconfigcall[.KIND = INTRINSIC_SET_INCLUDE_PATH])',
         '~$call_descriptors_valid(S[.SELECTSEQ = $(S.SELECTSEQ + 1)])',
         '~$call_descriptors_valid(S[.SELECTEDCALLS = [pselectedcall[.KIND = INTRINSIC_SET_INCLUDE_PATH]]])',
         '~$call_descriptors_valid(S[.TODO = (AT pconfigcall.SITE (CONFIG_INVOKE pconfigcall)) :: (CONFIG_INVOKE pconfigcall) :: ptask*])',
         'S_bad = $drive(S[.TODO = (CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_SET_INCLUDE_PATH]) :: ptask*],1000)',
         'S_bad.COMPLETION = UNSUPPORTED text',
         'S_bad.FILEINCLUDEPATH = S.FILEINCLUDEPATH',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.COMPLETION = NORMAL',
         'S_done.FILEINCLUDEPATH = ($ptascii(".:"))',
     ]),
    ('dynamic-saved', b"<?php function arg(){return 'sub';} $f='set_include_path'; echo $f(arg());",
     'S.SELECTEDCALLS = [pselectedcall]\n  -- if $selected_frame_count(S.FRAMES,pselectedcall.NONCE) = 1\n  -- if $selected_task_count(S.TODO,pselectedcall.NONCE) = 0', [
         'S.SELECTEDCALLS = [pselectedcall]',
         '$selected_entry_active_valid(S,pselectedcall)',
         '$selected_task_count($selected_owner_tasks(S,pselectedcall),pselectedcall.NONCE) = 1',
         '$call_descriptors_valid(S)',
         'n_top = |S.FRAMES|',
         '~$selected_entry_active_valid(S,pselectedcall[.DEPTH = n_top])',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.COMPLETION = NORMAL',
         '$outputs(S_done.EVENTS) = $ptascii(".:")',
     ]),
    ('dynamic-reentry', b"<?php function g($x){$f='set_include_path'; return $f($x ? throw new Exception('boom') : 'sub');} try{g(true);}catch(Throwable $e){} echo g(false);",
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*\n  -- if S.SELECTEDCALLS = [pselectedcall_old,pselectedcall_new]', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*',
         'S.SELECTEDCALLS = [pselectedcall_old,pselectedcall_new]',
         'pselectedcall_old.NONCE = 0',
         'pselectedcall_new.NONCE = 1',
         'pselectedcall_old.SITE = pselectedcall_new.SITE',
         'S.SELECTSEQ = 2',
         'pconfigcall.SELECTION = (1)',
         '$selected_log_valid(S,S.SELECTEDCALLS,0)',
         '~$config_call_valid(S,pconfigcall[.SELECTION = (0)])',
         '~$call_descriptors_valid(S[.TODO = (CONFIG_INVOKE pconfigcall[.SELECTION = (0)]) :: ptask*])',
         'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
         'S_done.COMPLETION = NORMAL',
         '$outputs(S_done.EVENTS) = $ptascii(".:")',
     ]),
    ('dynamic-chdir-pending', b"<?php $f='chdir'; $f('sub');",
     'S.TODO = (CHDIR_AWAIT pconfigcall n_dir) :: ptask*', [
         'S.TODO = (CHDIR_AWAIT pconfigcall n_dir) :: ptask*',
         'S.COMPLETION = SOURCE_PENDING',
         'S.DIRCONTEXT = (pdircontext)',
         'pdircontext.CALL = pconfigcall',
         'pconfigcall.SELECTION = (n_selection)',
         'S.SELECTEDCALLS[n_selection] = pselectedcall',
         'pselectedcall.KIND = INTRINSIC_CHDIR',
         '$selected_task_count(S.TODO,n_selection) = 1',
         '$selected_entry_active_valid(S,pselectedcall)',
         '$dir_pending_state_valid(S)',
         '$call_descriptors_valid(S)',
         '~$dir_pending_state_valid(S[.TODO = (CHDIR_AWAIT pconfigcall[.SELECTION = eps] n_dir) :: ptask*])',
         '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.SELECTION = eps]])])',
     ]),
    ('stringable-entered', b"<?php class O { function __toString(): string { return 'sub'; } } chdir(new O);",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '$call_descriptors_valid(S)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.LINE = 999] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child 999) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('stringable-dynamic-entered', b"<?php class O { function __toString(): string { return 'sub'; } } $f='chdir'; $f(new O);",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.SELECTION = (n_selection)',
         'S.SELECTEDCALLS[n_selection] = pselectedcall',
         '$selected_entry_active_valid(S,pselectedcall)',
         '$selected_task_count(pframe.TODO,n_selection) = 1',
         '$call_descriptors_valid(S)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SELECTION = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SELECTION = (999)] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('stringable-named-dynamic-entered', b"<?php\nclass O { function __toString():string { return 'sub'; } }\n$f='chdir';\n$f(\n directory: new O\n);\n",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.NAMED',
         'pconfigcall.INDEX = 1',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         'z_call = 4',
         'z_child = 5',
         '$config_string_child_site(S,porigin_child,z_call)',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '(HOBJECT n_object) <- $task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call)',
         'pconfigcall.SELECTION = (n_selection)',
         'S.SELECTEDCALLS[n_selection] = pselectedcall',
         '$selected_entry_active_valid(S,pselectedcall)',
         '$call_descriptors_valid(S)',
         '~$config_string_site_valid(S,pconfigcall[.NAMED = false],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.INDEX = 0],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.KIND = INTRINSIC_INI_RESTORE],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.SITE = PORIGIN 999 eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.SENT = eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,PORIGIN 999 eps,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,999)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.NAMED = false] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.LINE = 999] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT 999))]] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SELECTION = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SELECTION = (999)] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LINE = 999])])',
         '~$call_descriptors_valid(S[.ALLOCATIONS = eps])',
     ]),
    ('stringable-named-invoke-entered', b"<?php class O { function __toString():string { return 'sub'; } } $f=chdir(...); $f->__invoke(directory:new O);",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.NAMED',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         'pconfigcall.OWNER = (n_owner)',
         '(HOBJECT n_object) <- $task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call)',
         '(HOBJECT n_owner) <- $task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call)',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '$call_descriptors_valid(S)',
         '~$config_string_site_valid(S,pconfigcall[.NAMED = false],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.OWNER = eps],n_object,porigin_child,z_child,z_call)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.OWNER = (999)] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SENT = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('unpack-active-capture', b"<?php class O { function __toString():string { return 'sub'; } } $x=new O; $a=['directory'=>&$x]; $f='chdir'; $f(...$a);",
     'S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) n_cursor) :: ptask_tail*\n  -- if n_cursor = 0', [
         'S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) n_cursor) :: ptask_tail*',
         'n_cursor = 0',
         'pconfigcall.PACKS = [pconfigpack]',
         'pconfigpack.INDEX = 0',
         'pconfigpack.ARRAY = n_array',
         'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT (POBJECT n_object))]',
         'S.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING $ptascii("directory")) (ALIAS n_cell)]',
         'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
         'pconfigcall.SENT = eps',
         '~pconfigcall.NAMED',
         '$config_unpack_valid(S,pconfigcall,KNOWN (PARRAY n_array),0)',
         '$call_descriptors_valid(S)',
         '(HARRAY n_array) <- $task_nodes(CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) 0)',
         '~((HOBJECT n_object) <- $task_nodes(CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) 0))',
         '~$config_unpack_valid(S,pconfigcall,KNOWN (PARRAY 999),0)',
         '~$config_unpack_valid(S,pconfigcall,KNOWN (PARRAY n_array),1)',
         '~$config_unpack_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.NAMED = true],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = eps],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack,pconfigpack]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.ARRAY = 999]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.INDEX = 1]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.SITE = PORIGIN 999 eps]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.LINE = 999]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.ITEMS = eps]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (ALIAS n_cell)]]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT PNULL)]]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]]]],KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S[.ALLOCATIONS = eps],pconfigcall,KNOWN (PARRAY n_array),0)',
     ]),
    ('unpack-active-prefix', b"<?php class O { function __toString():string { return 'sub'; } } chdir(...['directory'=>new O,new O]);",
     'S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) n_cursor) :: ptask_tail*\n  -- if n_cursor = 1', [
         'S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) n_cursor) :: ptask_tail*',
         'n_cursor = 1',
         'pconfigcall.PACKS = [pconfigpack]',
         'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT (POBJECT n_first)),ENTRY (KINT 0) (DIRECT (POBJECT n_second))]',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_first))]',
         'pconfigcall.NAMED',
         '$config_pack_named(pconfigpack.ITEMS[0:1])',
         '$config_unpack_valid(S,pconfigcall,KNOWN (PARRAY n_array),1)',
         '$call_descriptors_valid(S)',
         '(HOBJECT n_first) <- $task_nodes(CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) 1)',
         '~((HOBJECT n_second) <- $task_nodes(CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) 1))',
         '~$config_unpack_valid(S,pconfigcall,KNOWN (PARRAY n_array),0)',
         '~$config_unpack_valid(S,pconfigcall,KNOWN (PARRAY n_array),2)',
         '~$config_unpack_valid(S,pconfigcall[.SENT = eps],KNOWN (PARRAY n_array),1)',
         '~$config_unpack_valid(S,pconfigcall[.NAMED = false],KNOWN (PARRAY n_array),1)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = eps],KNOWN (PARRAY n_array),1)',
         '~$config_unpack_valid(S,pconfigcall[.PACKS = [pconfigpack[.ITEMS = [pconfigpack.ITEMS[1],pconfigpack.ITEMS[0]]]]],KNOWN (PARRAY n_array),1)',
         '~$config_unpack_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT n_second))]],KNOWN (PARRAY n_array),1)',
         '~$config_unpack_valid(S,pconfigcall[.INDEX = 1],KNOWN (PARRAY n_array),1)',
     ]),
    ('unpack-retired-callback', b"<?php class O {function __toString():string {global $x,$a; echo ($x==='changed' && $a===[])?'E':'N'; echo 'T'; throw new Exception('X');}} $x=new O; $a=['directory'=>&$x]; function later(){global $x,$a; echo 'A'; $x='changed'; $a=[]; return [];} $f=chdir(...); $f->__invoke(...$a,...later());",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.NAMED',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '$call_descriptors_valid(S)',
         '~$config_string_site_valid(S,pconfigcall[.NAMED = false],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,PORIGIN 999 eps,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,999)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SENT = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.ALLOCATIONS = eps])',
         'pconfigcall.INDEX = 2',
         'pconfigcall.PACKS = [pconfigpack_first,pconfigpack_later]',
         'pconfigpack_first.INDEX = 0',
         'pconfigpack_later.INDEX = 1',
         'pconfigpack_first.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT (POBJECT n_object))]',
         'pconfigpack_later.ITEMS = eps',
         'porigin_child = pconfigpack_first.SITE',
         'z_child = pconfigpack_first.LINE',
         '~((HARRAY pconfigpack_first.ARRAY) <- S.ALLOCATIONS)',
         '~((HARRAY pconfigpack_first.ARRAY) <- $config_nodes(pconfigcall))',
         'pconfigcall.OWNER = (n_owner)',
         '(HOBJECT n_owner) <- $config_nodes(pconfigcall)',
         '(HOBJECT n_object) <- $config_nodes(pconfigcall)',
         '$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.ARRAY = pconfigpack_later.ARRAY],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_later,pconfigpack_first]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first,pconfigpack_later,pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.INDEX = 1],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.SITE = pconfigpack_later.SITE],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.LINE = 999],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT PNULL)]],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.OWNER = eps],n_object,porigin_child,z_child,z_call)',
     ]),
    ('unpack-empty-ordinary-callback', b"<?php class O { function __toString():string { return 'sub'; } } chdir(...[],directory:new O);",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.NAMED',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '$call_descriptors_valid(S)',
         '~$config_string_site_valid(S,pconfigcall[.NAMED = false],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,PORIGIN 999 eps,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,999)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SENT = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.ALLOCATIONS = eps])',
         'pconfigcall.INDEX = 2',
         'pconfigcall.PACKS = [pconfigpack_empty]',
         'pconfigpack_empty.INDEX = 0',
         'pconfigpack_empty.ITEMS = eps',
         'porigin_child =/= pconfigpack_empty.SITE',
         '~$config_string_site_valid(S,pconfigcall,n_object,pconfigpack_empty.SITE,pconfigpack_empty.LINE,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_empty[.INDEX = 1]]],n_object,porigin_child,z_child,z_call)',
     ]),
    ('unpack-no-pack-record-guard', b"<?php $a=[]; class O { function __toString():string { return 'sub'; } } chdir(new O);",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.PACKS = eps',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '(HARRAY 0) <- S.ALLOCATIONS',
         'pconfigpack = {INDEX 0, SITE porigin_child, LINE z_child, ARRAY 0, ITEMS ([ENTRY (KINT 0) (DIRECT (POBJECT n_object))])}',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack]],n_object,porigin_child,z_child,z_call)',
     ]),
    ('set-stringable-dynamic-entered', b"<?php class O {function __toString():string {return 'outer';}} function a(){global $f;$f='ini_restore';return new O;} $f='set_include_path';$f(include_path:a());",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'pconfigcall.NAMED',
         'pconfigcall.OWNER = eps',
         'pconfigcall.SELECTION = (n_selection)',
         'S.SELECTEDCALLS = [pselectedcall]',
         'pselectedcall.NONCE = n_selection',
         'pselectedcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         'pconfigcall.PACKS = eps',
         'S.CODE = [pcode]',
         '~pcode.STRICT',
         '~$config_strict(S,pconfigcall)',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '$call_descriptors_valid(S)',
         '$task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) = [HOBJECT n_object] ++ $config_nodes(pconfigcall)',
         '~$config_string_site_valid(S,pconfigcall[.KIND = INTRINSIC_CHDIR],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.KIND = INTRINSIC_INI_SET],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.NAMED = false],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.SELECTION = eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.SITE = PORIGIN 999 eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.LINE = 999],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,PORIGIN 999 eps,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,999)',
         '~$config_string_site_valid(S[.CODE = [pcode[.STRICT = true]]],pconfigcall,n_object,porigin_child,z_child,z_call)',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HOBJECT n_object)])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.SENT = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LINE = 999])])',
     ]),
    ('set-stringable-unpack-invoke-entered', b"<?php declare(strict_types=1);class O {function __toString():string {return 'outer';}} $x=new O;$a=['include_path'=>&$x];function later(){global $x,$a;$x='changed';$a=[];return [];} $f=set_include_path(...);$f->__invoke(...$a,...later());",
     'S.CURRENT = (pcallcontext)\n  -- if S.FRAMES = pframe :: pframe_tail*\n  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'pconfigcall.NAMED',
         'pconfigcall.OWNER = (n_owner)',
         'pconfigcall.SELECTION = eps',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         'pconfigcall.PACKS = [pconfigpack_first,pconfigpack_later]',
         'pconfigpack_first.ITEMS = [ENTRY pkey (DIRECT (POBJECT n_object))]',
         'pkey = KSTRING n_key*',
         'n_key* = $ptascii("include_path")',
         'pconfigpack_later.ITEMS = eps',
         'S.CODE = [pcode]',
         'pcode.STRICT',
         '~$config_strict(S,pconfigcall)',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$config_string_trace_context(S,pcallcontext)',
         '$call_descriptors_valid(S)',
         '(HOBJECT n_owner) <- $task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call)',
         '~$config_string_site_valid(S,pconfigcall[.OWNER = eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.KIND = INTRINSIC_CHDIR],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = eps],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_later,pconfigpack_first]],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall[.PACKS = [pconfigpack_first[.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT (POBJECT n_object))]],pconfigpack_later]],n_object,porigin_child,z_child,z_call)',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HOBJECT n_object)])',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HOBJECT n_owner)])',
     ]),
    ('set-stringable-post-callback', b"<?php class O {function __toString():string {set_include_path('inner');return 'outer';}} echo set_include_path(new O);",
     'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'S.RESULT = KNOWN (PSTRING n_new*)',
         'n_new* = $ptascii("outer")',
         'S.FILEINCLUDEPATH = (n_old*)',
         'n_old* = $ptascii("inner")',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$call_descriptors_valid(S)',
         'S_step = $drive_steps(S,1)',
         'S_step.COMPLETION = BUDGET',
         'S_ready = S_step[.COMPLETION = NORMAL]',
         'S_ready.TODO = ptask_tail*',
         'S_ready.ORIGIN = (pconfigcall.SITE)',
         'S_ready.RESULT = KNOWN (PSTRING n_old*)',
         'S_ready.FILEINCLUDEPATH = (n_new*)',
         'S_ready.FILECWD = S.FILECWD',
         'S_ready.DIRSEQ = S.DIRSEQ',
         'S_ready.DIRCONVSEQ = S.DIRCONVSEQ',
         'S_ready.DIRCONVERSIONS = S.DIRCONVERSIONS',
         'S_ready.DIRCONTEXT = S.DIRCONTEXT',
         '~$config_string_site_valid(S,pconfigcall[.KIND = INTRINSIC_CHDIR],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HOBJECT n_object)])',
     ]),
    ('set-stringable-empty-post-callback', b"<?php class O {function __toString():string {set_include_path('inner');return '';}} echo set_include_path(include_path:new O);",
     'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'pconfigcall.NAMED',
         'S.RESULT = KNOWN (PSTRING eps)',
         'S.FILEINCLUDEPATH = (n_old*)',
         'n_old* = $ptascii("inner")',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         'S_step = $drive_steps(S,1)',
         'S_step.COMPLETION = BUDGET',
         'S_ready = S_step[.COMPLETION = NORMAL]',
         'S_ready.TODO = ptask_tail*',
         'S_ready.RESULT = KNOWN (PBOOL false)',
         'S_ready.FILEINCLUDEPATH = S.FILEINCLUDEPATH',
         'S_ready.FILECWD = S.FILECWD',
         'S_ready.DIRSEQ = S.DIRSEQ',
         'S_ready.DIRCONVSEQ = S.DIRCONVSEQ',
         'S_ready.DIRCONVERSIONS = S.DIRCONVERSIONS',
     ]),
    ('ini-prefix-scalar-set-result', b'<?php ini_set(\'include_path\',"a\\0b");echo set_include_path(\'end\');',
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*\n  -- if pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'S.FILEINCLUDEPATH = ($ptascii("a") ++ [0] ++ $ptascii("b"))',
         '$config_invoke_valid(S,pconfigcall)',
         '$call_descriptors_valid(S)',
         '~$config_call_valid(S,pconfigcall[.LINE = 999])',
         'S_ready = $config_receive(S,pconfigcall)',
         'S_ready.COMPLETION = NORMAL',
         'S_ready.TODO = ptask_tail*',
         'S_ready.RESULT = KNOWN (PSTRING $ptascii("a"))',
         'S_ready.FILEINCLUDEPATH = ($ptascii("end"))',
         'S_ready.FILECWD = S.FILECWD',
         '$call_descriptors_valid(S_ready)',
         'S_done = $drive_steps(S_ready,1000)',
         'S_done.COMPLETION = NORMAL',
         '$outputs(S_done.EVENTS) = $ptascii("a")',
     ]),
    ('ini-prefix-ini-full-result', b'<?php ini_set(\'include_path\',"a\\0b");echo ini_set(\'include_path\',\'end\');',
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*\n  -- if pconfigcall.KIND = INTRINSIC_INI_SET\n  -- if S.FILEINCLUDEPATH = ($ptascii("a") ++ [0] ++ $ptascii("b"))', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_INI_SET',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("include_path"))),NAMED_SENT (KNOWN (PSTRING $ptascii("end")))]',
         'S.FILEINCLUDEPATH = (n_old*)',
         'n_old* = $ptascii("a") ++ [0] ++ $ptascii("b")',
         '$config_invoke_valid(S,pconfigcall)',
         '$call_descriptors_valid(S)',
         'S_ready = $config_receive(S,pconfigcall)',
         'S_ready.COMPLETION = NORMAL',
         'S_ready.TODO = ptask_tail*',
         'S_ready.RESULT = KNOWN (PSTRING n_old*)',
         'S_ready.FILEINCLUDEPATH = ($ptascii("end"))',
         'S_ready.FILECWD = S.FILECWD',
         '$call_descriptors_valid(S_ready)',
         'S_done = $drive_steps(S_ready,1000)',
         'S_done.COMPLETION = NORMAL',
         '$outputs(S_done.EVENTS) = n_old*',
     ]),
    ('ini-prefix-leading-nul-result', b'<?php ini_set(\'include_path\',"a\\0b");echo ini_set(\'include_path\',"\\0tail")?\'Y\':\'F\';',
     'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*\n  -- if pconfigcall.KIND = INTRINSIC_INI_SET\n  -- if S.FILEINCLUDEPATH = ($ptascii("a") ++ [0] ++ $ptascii("b"))', [
         'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_INI_SET',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("include_path"))),NAMED_SENT (KNOWN (PSTRING ([0] ++ $ptascii("tail"))))]',
         'S.FILEINCLUDEPATH = (n_old*)',
         'n_old* = $ptascii("a") ++ [0] ++ $ptascii("b")',
         '$config_invoke_valid(S,pconfigcall)',
         '$call_descriptors_valid(S)',
         'S_ready = $config_receive(S,pconfigcall)',
         'S_ready.COMPLETION = NORMAL',
         'S_ready.TODO = ptask_tail*',
         'S_ready.RESULT = KNOWN (PBOOL false)',
         'S_ready.FILEINCLUDEPATH = S.FILEINCLUDEPATH',
         'S_ready.FILECWD = S.FILECWD',
         '$call_descriptors_valid(S_ready)',
         'S_done = $drive_steps(S_ready,1000)',
         'S_done.COMPLETION = NORMAL',
         'S_done.FILEINCLUDEPATH = (n_old*)',
         '$outputs(S_done.EVENTS) = $ptascii("F")',
     ]),
    ('ini-prefix-stringable-set-result', b'<?php class O {function __toString():string {ini_set(\'include_path\',"inner\\0tail");return \'end\';}} echo set_include_path(new O);',
     'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'S.RESULT = KNOWN (PSTRING n_new*)',
         'n_new* = $ptascii("end")',
         'S.FILEINCLUDEPATH = (n_old*)',
         'n_old* = $ptascii("inner") ++ [0] ++ $ptascii("tail")',
         '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
         '$call_descriptors_valid(S)',
         '~$config_string_site_valid(S,pconfigcall[.KIND = INTRINSIC_CHDIR],n_object,porigin_child,z_child,z_call)',
         '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HOBJECT n_object)])',
         'S_step = $drive_steps(S,1)',
         'S_step.COMPLETION = BUDGET',
         'S_ready = S_step[.COMPLETION = NORMAL]',
         'S_ready.TODO = ptask_tail*',
         'S_ready.ORIGIN = (pconfigcall.SITE)',
         'S_ready.RESULT = KNOWN (PSTRING $ptascii("inner"))',
         'S_ready.FILEINCLUDEPATH = (n_new*)',
         'S_ready.FILECWD = S.FILECWD',
         'S_ready.DIRSEQ = S.DIRSEQ',
         'S_ready.DIRCONVSEQ = S.DIRCONVSEQ',
         'S_ready.DIRCONVERSIONS = S.DIRCONVERSIONS',
         'S_ready.DIRCONTEXT = S.DIRCONTEXT',
         '$call_descriptors_valid(S_ready)',
         'S_done = $drive_steps(S_ready,1000)',
         'S_done.COMPLETION = NORMAL',
         '$outputs(S_done.EVENTS) = $ptascii("inner")',
     ]),
]

PREFIX = '''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
dec $ini_prefix_live(pstate) : bool
def $ini_prefix_live(S) = ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ini_prefix_live(S) = false -- otherwise
dec $ini_prefix_seek(pstate, nat) : pstate
def $ini_prefix_seek(S,n) = S -- if $ini_prefix_live(S) -- if $stage(S)
def $ini_prefix_seek(S,n) = $ini_prefix_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $ini_prefix_live(S)
  -- if ~$stage(S)
  -- if $(n > 0)
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree


def main(cases=None, extra_inputs=()):
    cases = CASES if cases is None else cases
    out = Path(tempfile.mkdtemp(prefix='include-mutable-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / 'tests/semantics/numeric_runner.ml', ROOT / '_build/default/adapter/main.exe',
              ROOT / 'frontend/worker.php', ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php', ROOT / 'frontend/target.php',
              ROOT / 'frontend/SourcePrinter.php', ROOT / 'frontend/encoding.php', ROOT / 'frontend/wire.php',
              ROOT / 'frontend/wire.py', ROOT / 'spec/schema.json', ROOT / 'spec/php.watsup',
              ROOT / 'adapter/main.ml', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/recorded_worker.py', Path(__file__),
              *extra_inputs]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = vendor_identity()
    results = []
    modules_args = [str(path) for path in modules]
    for name, source, stage, checks in cases:
        directory = out / name
        directory.mkdir()
        source_path = directory / 'main.php'
        source_path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': b64(source)})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close()
            adapter.close()
        pending = name == 'dynamic-chdir-pending'
        if name == 'no-file-chdir':
            start = '$php_run(' + checked['fixture'] + ', 300, ' + json.dumps(b64(str(source_path.resolve()).encode())) + ')'
            conditions = ['S_initial = ' + start, 'S = S_initial'] + checks
        else:
            start = '$php_file_run(' + checked['fixture'] + (', 300, ' if pending else ', 0, ') + '$base64(' + json.dumps(b64(str(source_path.resolve()).encode())) + '), $base64(' + json.dumps(b64(str(ROOT.resolve()).encode())) + '))'
            if name.startswith('ini-prefix-'):
                conditions = ['S_initial = ' + start,
                              '~S_initial.COMPILESTOP',
                              '$ini_prefix_live(S_initial)',
                              '~$ini_prefix_live(S_initial[.COMPILESTOP = true])',
                              '~$ini_prefix_live(S_initial[.COMPLETION = UNSUPPORTED "guard"])',
                              '~$ini_prefix_live(S_initial[.COMPLETION = PHPERROR eps 1])',
                              '~$ini_prefix_live(S_initial[.COMPLETION = EXITED 0])',
                              '~$ini_prefix_live(S_initial[.COMPLETION = SOURCE_PENDING])',
                              'S = $ini_prefix_seek(S_initial[.COMPLETION = NORMAL],1000)[.COMPLETION = NORMAL]'] + checks
            else:
                conditions = ['S_initial = ' + start,
                              'S = S_initial' if pending else
                              'S = $seek(S_initial[.COMPLETION = NORMAL],1000)[.COMPLETION = NORMAL]'] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + line + '\n' for line in conditions))
        process = subprocess.run([str(runner), *modules_args, str(fixture)],
                                 capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stdout[-1000:], process.stderr[-2000:])
        results.append({'case': name, 'assertions': len(conditions), 'source_sha256': digest(source_path),
                        'fixture_sha256': digest(fixture)})
        print(name, len(conditions), flush=True)
    after = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'passed': True, 'cases': results, 'inputs': before,
              'input_changes': [key for key in before if before[key] != after[key]],
              'vendor_tree': vendor_before,
              'assertions': sum(row['assertions'] for row in results)}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    assert not report['input_changes'] and vendor_before == vendor_identity()


if __name__ == '__main__':
    main()
