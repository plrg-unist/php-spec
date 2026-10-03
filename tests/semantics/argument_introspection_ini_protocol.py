#!/usr/bin/env python3
"""Live raw INI bytes under source __invoke ARGINFO and borrowed SET packs."""
import argument_introspection_calls_protocol as union

PREFIX = union.PREFIX
SOURCE = (b'<?php declare(strict_types=1);class ArgIniInner13{public function __invoke($a){'
          b'ini_set("include_path","live\\0tail");echo func_num_args(),func_get_arg(0),'
          b'func_get_args()[0],get_include_path(),"|";return "union-path";}}'
          b'class ArgIniString13{public function __toString():string{$i=new ArgIniInner13;'
          b'return $i(7);}}$f=set_include_path(...);'
          b'echo $f->__invoke(...["include_path"=>new ArgIniString13]);')
EXPECTED = b"177live\0tail|live"
RAW = '$ptascii("live") ++ [0] ++ $ptascii("tail")'
OUTPUT = '$ptascii("177live") ++ [0] ++ $ptascii("tail|live")'
SOURCES = {'live-nul-set-source-invoke': {'source': SOURCE, 'expected_stdout': EXPECTED}}

CASES = [
    {
        'id': 'live-nul-arginfo-config-packs',
        'source_id': 'live-nul-set-source-invoke',
        'stage': union.CASES[3]['stage'],
        'checks': [
            'S.FILEINCLUDEPATH = (' + RAW + ')',
            '$file_include_path(S.FILEINCLUDEPATH) = ($ptascii("live"))',
            '$file_state_valid(S)',
            *union.CASES[3]['checks'][:-1],
            '$outputs(S_done.EVENTS) = ' + OUTPUT,
        ],
    },
    {
        'id': 'live-nul-set-post-callback',
        'source_id': 'live-nul-set-source-invoke',
        'stage': 'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
        'checks': [
            'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
            'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
            'S.RESULT = KNOWN (PSTRING n_new*)',
            'n_new* = $ptascii("union-path")',
            'S.FILEINCLUDEPATH = (n_old*)',
            'n_old* = ' + RAW,
            '$file_include_path(S.FILEINCLUDEPATH) = ($ptascii("live"))',
            'S.ORIGIN = (porigin_child)',
            'pconfigcall.NAMED',
            'pconfigcall.OWNER = (n_owner)',
            'pconfigcall.SELECTION = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
            'pconfigcall.PACKS = [pconfigpack]',
            'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("include_path")) (DIRECT (POBJECT n_object))]',
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_SET_INCLUDE_PATH',
            '$config_string_site_valid(S, pconfigcall, n_object, porigin_child, z_child, z_call)',
            '$config_nodes(pconfigcall) = [HOBJECT n_owner, HOBJECT n_object]',
            '$task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) = [HOBJECT n_object, HOBJECT n_owner, HOBJECT n_object]',
            '~((HARRAY pconfigpack.ARRAY) <- $config_nodes(pconfigcall))',
            '$outputs(S.EVENTS) = $ptascii("177live") ++ [0] ++ $ptascii("tail|")',
            '~$config_string_site_valid(S, pconfigcall[.PACKS = eps], n_object, porigin_child, z_child, z_call)',
            '~$config_string_site_valid(S, pconfigcall[.PACKS = [pconfigpack[.INDEX = 999]]], n_object, porigin_child, z_child, z_call)',
            '~$config_string_site_valid(S, pconfigcall[.OWNER = (n_object)], n_object, porigin_child, z_child, z_call)',
            '~$config_string_site_valid(S, pconfigcall[.LINE = 999], n_object, porigin_child, z_child, z_call)',
            '~$call_descriptors_valid(S[.TODO = (CONFIG_STRING_RESULT pconfigcall[.PACKS = eps] n_object porigin_child z_child z_call) :: ptask_tail*])',
            *union.GUARDS,
            '$file_state_valid(S)',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_ready = S_step[.COMPLETION = NORMAL]',
            'S_ready.TODO = ptask_tail*',
            'S_ready.ORIGIN = (pconfigcall.SITE)',
            'S_ready.RESULT = KNOWN (PSTRING $ptascii("live"))',
            'S_ready.FILEINCLUDEPATH = (n_new*)',
            'S_ready.FILECWD = S.FILECWD',
            'S_ready.DIRSEQ = S.DIRSEQ',
            'S_ready.DIRCONVSEQ = S.DIRCONVSEQ',
            'S_ready.DIRCONVERSIONS = S.DIRCONVERSIONS',
            'S_ready.DIRCONTEXT = S.DIRCONTEXT',
            '$call_descriptors_valid(S_ready)',
            '$file_state_valid(S_ready)',
            *union.FINISH,
            'S_done.FILEINCLUDEPATH = (n_new*)',
            '$outputs(S_done.EVENTS) = ' + OUTPUT,
        ],
    },
]
