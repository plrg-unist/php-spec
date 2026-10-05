#!/usr/bin/env python3
"""Source-derived precision entry, retained capture and deferred AST controls."""
from pathlib import Path
import argparse
import base64
import copy
import hashlib
import json
import subprocess
import sys
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('precision')
b64 = lambda value: base64.b64encode(value).decode()

CHECKS = {'initial': ['S_base = $initial_state(NORMAL)',
             '$precision_state_valid(S_base)',
             'S_base.PRECISIONINI = $ptascii("14")',
             '~S_base.PRECISIONMODIFIED',
             '$precision_ini_valid(eps)',
             '$precision_ini_long(eps) = 0',
             '$precision_ini_long($ptascii("  +0005tail")) = 5',
             '$precision_ini_long($ptascii("1") ++ [0,255]) = 1',
             '$precision_ini_long($ptascii("9223372036854775808")) = 9223372036854775807',
             '$precision_ini_long($ptascii("-9223372036854775809")) = -9223372036854775808',
             '$precision_ini_valid($ptascii("-1"))',
             '~$precision_ini_valid($ptascii("-2"))',
             '~$precision_ini_valid([256])',
             'preqbytes_file = $base64("@SEED@")',
             'preqbytes_cwd = $base64("@CWD@")',
             'Q = {ENV eps, ARGV ([preqbytes_file]), FILE preqbytes_file, SECONDS 0, MICROSECONDS 0, '
             'VARIABLES $ptascii("EGPCS"), JIT true, CWD (preqbytes_cwd)}',
             'S_plain = $php_precision_run(program_seed,0,"@SEED@",eps,false,eps,$ptascii("5junk"))',
             'S_request = '
             '$php_request_precision_run(program_seed,0,"@SEED@",Q,eps,false,eps,$ptascii("5junk"))',
             'S_file = '
             '$php_file_precision_run(program_seed,0,preqbytes_file,preqbytes_cwd,eps,false,eps,$ptascii("5junk"))',
             'S_both = '
             '$php_request_file_precision_run(program_seed,0,preqbytes_file,Q,preqbytes_cwd,eps,false,eps,$ptascii("5junk"))',
             '$call_descriptors_valid(S_plain)',
             '$call_descriptors_valid(S_request)',
             '$call_descriptors_valid(S_file)',
             '$call_descriptors_valid(S_both)',
             'S_plain.PRECISIONINIT = $ptascii("5junk")',
             'S_plain.PRECISIONINI = S_plain.PRECISIONINIT',
             'S_plain.FILECWD = eps /\\ S_plain.FILEINCLUDEPATH = eps',
             'S_request.FILECWD = eps /\\ S_request.REQUEST = (Q)',
             'S_file.FILECWD = (preqbytes_cwd) /\\ S_file.FILEINCLUDEPATH = ($ptascii(".:"))',
             'S_both.REQUEST = (Q) /\\ S_both.INCLUDEDOPENED = [preqbytes_file]',
             '$declaration_precision(S_plain.DECLARATIONS,0) = (5)',
             '$declaration_entry_input(PDENTER 0 eps 30719,0) = ((porigin_entry?,z_entry,z_capture))',
             'porigin_entry? = eps /\\ z_entry = 30719 /\\ z_capture = 14',
             '$declaration_entry_input(PDENTERPRECISION 0 eps 30719 14,0) = eps',
             '$declaration_entry_input(PDENTERPRECISION 0 eps 30719 (-2),0) = eps',
             '$declaration_entry_input(PDENTERPRECISION 0 eps 30719 9223372036854775808,0) = eps',
             '~$precision_state_valid(S_plain[.PRECISIONINI = $ptascii("3")])',
             '~$precision_state_valid(S_plain[.PRECISIONINI = [256]])',
             '~$precision_state_valid(S_plain[.PRECISIONINIT = [256]])',
             '~$precision_state_valid(S_plain[.PRECISIONINIT = $ptascii("3")][.PRECISIONMODIFIED = true])',
             'S_same = $precision_set(S_plain,$ptascii("  +0005tail"),S_plain.PRECISIONINI)',
             'S_same.PRECISIONINI = $ptascii("  +0005tail") /\\ S_same.PRECISIONMODIFIED',
             'S_same.RESULT = KNOWN (PSTRING S_plain.PRECISIONINI)',
             '$precision_state_valid(S_same)',
             'S_changed = $precision_set(S_same,$ptascii("2tail"),S_same.PRECISIONINI)',
             '$precision_value(S_changed) = 2',
             'S_reject = $precision_set(S_changed,$ptascii("-2"),S_changed.PRECISIONINI)',
             'S_reject.PRECISIONINI = S_changed.PRECISIONINI /\\ S_reject.PRECISIONMODIFIED',
             'S_reject.RESULT = KNOWN (PBOOL false)',
             '$precision_state_valid(S_reject)',
             'S_restored = $precision_restore(S_reject)',
             'S_restored.PRECISIONINI = S_plain.PRECISIONINIT /\\ ~S_restored.PRECISIONMODIFIED',
             '$precision_restore(S_restored) = S_restored',
             '$source_precision(S_changed,(PORIGIN 0 eps)) = (5)'],
 'dynamic': ['S_eval = $php_precision_run(program_eval,1000,"@EVAL@",eps,false,eps,$ptascii("5junk"))',
             'S_eval.COMPLETION = SOURCE_PENDING',
             'S_eval.EVALCONTEXTS = pevalcontext :: eps',
             'pevalcontext.UNIT = 1 /\\ pevalcontext.PHASE = PARSER_WAIT',
             '$precision_value(S_eval) = 3',
             '$declaration_precision(S_eval.DECLARATIONS,1) = (3)',
             '$call_descriptors_valid(S_eval)',
             '~$precision_state_valid(S_eval[.PRECISIONINI = $ptascii("1tail")])',
             '~$eval_response_valid(S_eval[.PRECISIONINI = $ptascii("1tail")],(SOURCE_ACCEPT 1 '
             '$base64("cmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7") program_evalbody))',
             '$eval_response_valid(S_eval,(SOURCE_ACCEPT 1 $base64("cmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7") '
             'program_evalbody))',
             'S_eval_done = $eval_continue(S_eval,(SOURCE_ACCEPT 1 '
             '$base64("cmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7") program_evalbody))',
             'S_eval_done.COMPLETION = NORMAL /\\ S_eval_done.EVALCONTEXTS = eps',
             '$precision_value(S_eval_done) = 1',
             '$call_descriptors_valid(S_eval_done)',
             '$source_precision(S_eval_done,(PORIGIN 1 eps)) = (3)',
             'porigin_literal = PORIGIN 1 ([PCINDEX 0, PCFIELD 0])',
             '$origin_node(S_eval_done.SOURCES,porigin_literal) = (expression_literal)',
             '$parser_literal_origin(S_eval_done,(porigin_literal),expression_literal) = (PSTRING '
             '$ptascii("12.3L"))',
             '$compiled_read(S_eval_done,porigin_literal) = (PSTRING $ptascii("12.3L"))',
             '$parser_literal_origin(S_eval_done[.PRECISIONINI = '
             '$ptascii("2tail")],(porigin_literal),expression_literal) = (PSTRING $ptascii("12.3L"))',
             '~$call_descriptors_valid(S_eval_done[.DECLARATIONS = '
             '$precision_control_capture(S_eval_done.DECLARATIONS,1,4)])',
             '~$call_descriptors_valid(S_eval_done[.DECLARATIONS = '
             '$precision_control_remove(S_eval_done.DECLARATIONS,1)])',
             'S_open = '
             '$php_file_precision_run(program_file,1000,$base64("@FILE@"),$base64("@CWD@"),eps,false,eps,$ptascii("5junk"))',
             'S_open.COMPLETION = SOURCE_PENDING',
             'S_open.FILECONTEXTS = pfilecontext :: eps',
             'pfilecontext.PHASE = FILE_RESOLVE_WAIT',
             '$call_descriptors_valid(S_open)',
             'S_parse = $file_open_resume(S_open,FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER '
             'pfilecontext.REQUESTED $base64("@CHILD@") $base64("@CHILD@") '
             '$base64("PD9waHAgcmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7"))',
             'S_parse.COMPLETION = SOURCE_PENDING',
             '$call_descriptors_valid(S_parse)',
             '$declaration_precision(S_parse.DECLARATIONS,1) = (3)',
             '~$precision_state_valid(S_parse[.PRECISIONINI = $ptascii("1tail")])',
             '~$file_parse_response_valid(S_parse[.PRECISIONINI = $ptascii("1tail")],(SOURCE_ACCEPT 1 '
             '$base64("PD9waHAgcmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7") program_child))',
             '$file_parse_response_valid(S_parse,(SOURCE_ACCEPT 1 '
             '$base64("PD9waHAgcmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7") program_child))',
             'S_file_done = $file_parse_continue(S_parse,(SOURCE_ACCEPT 1 '
             '$base64("PD9waHAgcmV0dXJuIDEyLjM0NTY3ODkgLiAnTCc7") program_child))',
             'S_file_done.COMPLETION = NORMAL /\\ S_file_done.FILECONTEXTS = eps',
             '$precision_value(S_file_done) = 1',
             '$call_descriptors_valid(S_file_done)',
             '$source_precision(S_file_done,(PORIGIN 1 eps)) = (3)'],
 'abrupt': ['S_rejected = '
 '$php_precision_run(program_rejected,1000,"@REJECTED@",eps,false,eps,$ptascii("5junk"))',
 'S_rejected.COMPLETION = SOURCE_PENDING',
 'S_rejected.EVALCONTEXTS = pevalcontext :: eps',
 '$declaration_precision(S_rejected.DECLARATIONS,1) = (3)',
 '$call_descriptors_valid(S_rejected)',
 'S_rejected_done = $eval_continue(S_rejected,(SOURCE_PARSE_REJECT 1 pevalcontext.BYTES '
 '$ptascii("Unclosed \'(\'") 1))',
 'S_rejected_done.COMPLETION = NORMAL',
 '$precision_value(S_rejected_done) = 1',
 '$call_descriptors_valid(S_rejected_done)',
 '$declaration_history_valid(S_rejected_done)',
 '$failed_source_at(S_rejected_done.FAILEDSOURCES,1) = (pfailedsource)',
 'pfailedsource.KIND = FAILED_PARSE',
 '$source_precision(S_rejected_done,(PORIGIN 1 eps)) = (3)',
 'S_open = $php_precision_run(program_early,1000,"@EARLY@",eps,false,eps,$ptascii("5junk"))',
 'S_open.COMPLETION = SOURCE_PENDING',
 'S_ready = $precision_resume_seek($eval_resume(S_open,(SOURCE_ACCEPT 1 '
 '$base64("ZnVuY3Rpb24gcHJlY2lzaW9uUGF1c2VkKCR4KXtyZXR1cm4gIiR7eH0iO30gY2xhc3MgUHJlY2lzaW9uTGF0ZXIge30=") '
 'program_earlybody)),1000)',
 'S_ready.COMPLETION = BUDGET',
 'S_ready.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
 '$eval_compile_cursor_valid(S_ready,pevalcompile)',
 '$precision_value(S_ready) = 1',
 '~$precision_eval_resume_valid(S_ready,pevalcompile)',
 'S_changed = $drive_steps(S_ready[.COMPLETION = NORMAL],1)',
 'S_changed.COMPLETION = BUDGET',
 '$eval_precision_epochs(S_changed.DECLARATIONS,1) = '
 '([(pevalcompile.CHECKPOINT,pevalcompile.DIAGNOSTIC,1)])',
 '$source_precision(S_changed,(PORIGIN 1 eps)) = (3)',
 '$call_descriptors_valid(S_changed)',
 'S_done = $drive(S_changed[.COMPLETION = NORMAL],1000)',
 'S_done.COMPLETION = NORMAL /\\ S_done.EVALCONTEXTS = eps',
 '$eval_compile_cursors(S_done) = eps',
 'S_done.FRAMES = eps',
 'S_done.TODO = eps',
 '$call_descriptors_valid(S_done)'],
 'ast': ['S_ast_class = '
         '$precision_ast_seek($php_precision_run(program_class,0,"@CLASS@",eps,false,eps,$ptascii("5junk")),0,1000)',
         'S_ast_class.COMPLETION = BUDGET',
         '$call_descriptors_valid(S_ast_class)',
         'S_ast_class.TODO = (CONCAT_PREP poperand_left_class poperand_right_class false false '
         'z_concat_class) :: ptask_tail_class*',
         'S_ast_class.CONSTCONTEXT = (pconstantcontext_class)',
         'S_ast_class.ORIGIN = (porigin_concat_class)',
         '$origin_child((porigin_concat_class),[PCFIELD 1]) = (porigin_float_class)',
         '$compiled_read(S_ast_class,porigin_float_class) = (PFLOAT n_bits_class)',
         '$precision_value(S_ast_class) = 1 /\\ $source_precision(S_ast_class,(porigin_float_class)) = (5)',
         '$concat_runtime_constant(S_ast_class,porigin_float_class)',
         '~$concat_constant(S_ast_class,(porigin_float_class))',
         '~$concat_runtime_constant(S_ast_class,PORIGIN 0 eps)',
         '$concat_constant(S_ast_class[.CONSTCONTEXT = eps],(porigin_float_class))',
         'S_format_class = $stringify(S_ast_class[.COMPLETION = NORMAL],PFLOAT n_bits_class,z_concat_class)',
         'S_format_class.RESULT = KNOWN (PSTRING $ptascii("1.0E+1"))',
         'S_ast_global = '
         '$precision_ast_seek($php_precision_run(program_global,0,"@GLOBAL@",eps,false,eps,$ptascii("5junk")),1,1000)',
         'S_ast_global.COMPLETION = BUDGET',
         '$call_descriptors_valid(S_ast_global)',
         'S_ast_global.TODO = (CONCAT_PREP poperand_left_global poperand_right_global false false '
         'z_concat_global) :: ptask_tail_global*',
         'S_ast_global.CONSTCONTEXT = (pconstantcontext_global)',
         'S_ast_global.ORIGIN = (porigin_concat_global)',
         '$origin_child((porigin_concat_global),[PCFIELD 1]) = (porigin_float_global)',
         '$compiled_read(S_ast_global,porigin_float_global) = (PFLOAT n_bits_global)',
         '$precision_value(S_ast_global) = 1 /\\ $source_precision(S_ast_global,(porigin_float_global)) = '
         '(5)',
         '$concat_runtime_constant(S_ast_global,porigin_float_global)',
         '~$concat_constant(S_ast_global,(porigin_float_global))',
         '~$concat_runtime_constant(S_ast_global,PORIGIN 0 eps)',
         '$concat_constant(S_ast_global[.CONSTCONTEXT = eps],(porigin_float_global))',
         'S_format_global = $stringify(S_ast_global[.COMPLETION = NORMAL],PFLOAT '
         'n_bits_global,z_concat_global)',
         'S_format_global.RESULT = KNOWN (PSTRING $ptascii("1.0E+1"))',
         'S_ast_parameter = '
         '$precision_ast_seek($php_precision_run(program_parameter,0,"@PARAMETER@",eps,false,eps,$ptascii("5junk")),2,1000)',
         'S_ast_parameter.COMPLETION = BUDGET',
         '$call_descriptors_valid(S_ast_parameter)',
         'S_ast_parameter.TODO = (CONCAT_PREP poperand_left_parameter poperand_right_parameter false false '
         'z_concat_parameter) :: ptask_tail_parameter*',
         'S_ast_parameter.CONSTCONTEXT = (pconstantcontext_parameter)',
         'S_ast_parameter.ORIGIN = (porigin_concat_parameter)',
         '$origin_child((porigin_concat_parameter),[PCFIELD 1]) = (porigin_float_parameter)',
         '$compiled_read(S_ast_parameter,porigin_float_parameter) = (PFLOAT n_bits_parameter)',
         '$precision_value(S_ast_parameter) = 1 /\\ '
         '$source_precision(S_ast_parameter,(porigin_float_parameter)) = (5)',
         '$concat_runtime_constant(S_ast_parameter,porigin_float_parameter)',
         '~$concat_constant(S_ast_parameter,(porigin_float_parameter))',
         '~$concat_runtime_constant(S_ast_parameter,PORIGIN 0 eps)',
         '$concat_constant(S_ast_parameter[.CONSTCONTEXT = eps],(porigin_float_parameter))',
         'S_format_parameter = $stringify(S_ast_parameter[.COMPLETION = NORMAL],PFLOAT '
         'n_bits_parameter,z_concat_parameter)',
         'S_format_parameter.RESULT = KNOWN (PSTRING $ptascii("1.0E+1"))',
         'S_ast_property = '
         '$precision_ast_seek($php_precision_run(program_property,0,"@PROPERTY@",eps,false,eps,$ptascii("5junk")),3,1000)',
         'S_ast_property.COMPLETION = BUDGET',
         '$call_descriptors_valid(S_ast_property)',
         'S_ast_property.TODO = (CONCAT_PREP poperand_left_property poperand_right_property false false '
         'z_concat_property) :: ptask_tail_property*',
         'S_ast_property.CONSTCONTEXT = (pconstantcontext_property)',
         'S_ast_property.ORIGIN = (porigin_concat_property)',
         '$origin_child((porigin_concat_property),[PCFIELD 1]) = (porigin_float_property)',
         '$compiled_read(S_ast_property,porigin_float_property) = (PFLOAT n_bits_property)',
         '$precision_value(S_ast_property) = 1 /\\ '
         '$source_precision(S_ast_property,(porigin_float_property)) = (5)',
         '$concat_runtime_constant(S_ast_property,porigin_float_property)',
         '~$concat_constant(S_ast_property,(porigin_float_property))',
         '~$concat_runtime_constant(S_ast_property,PORIGIN 0 eps)',
         '$concat_constant(S_ast_property[.CONSTCONTEXT = eps],(porigin_float_property))',
         'S_format_property = $stringify(S_ast_property[.COMPLETION = NORMAL],PFLOAT '
         'n_bits_property,z_concat_property)',
         'S_format_property.RESULT = KNOWN (PSTRING $ptascii("1.0E+1"))',
         'S_handler = '
         '$precision_ast_seek($php_precision_run(program_global,0,"@GLOBAL@",eps,false,eps,$ptascii("5junk")),4,1000)',
         'S_handler.COMPLETION = BUDGET',
         '$call_descriptors_valid(S_handler)',
         'S_handler.TODO = (CONCAT_PREP poperand_left poperand_right true false z_concat) :: ptask_tail*',
         'S_handler.CONSTCONTEXT = eps',
         'S_handler.ORIGIN = (porigin_concat)',
         '$origin_child((porigin_concat),[PCFIELD 0]) = (porigin_float)',
         'S_handler.FRAMES = pframe :: pframe_tail*',
         'pframe.CONSTCONTEXT = (pconstantcontext)',
         '~$constant_expression_below(S_handler,pconstantcontext.ORIGIN,porigin_float)',
         '~$concat_runtime_constant(S_handler[.CONSTCONTEXT = (pconstantcontext)],porigin_float)',
         '$concat_constant(S_handler,(porigin_float))',
         '$compiled_read(S_handler,porigin_float) = (PFLOAT n_bits)',
         '$concat_operand(S_handler,KNOWN (PFLOAT n_bits),true,z_concat) = (S_handler,KNOWN (PSTRING '
         '$ptascii("12.346")))']}

HELPERS = {'dynamic': 'dec $precision_control_capture(pdeclaration*, nat, int) : pdeclaration*\n'
            'def $precision_control_capture(eps, n, z_capture) = eps\n'
            'def $precision_control_capture(pdeclaration :: pdeclaration_tail*, n, z_capture) = '
            '(PDENTERPRECISION n porigin_site? z_reporting z_capture) :: pdeclaration_tail*\n'
            '  -- if $declaration_entry_input(pdeclaration, n) = ((porigin_site?, z_reporting, z_original))\n'
            'def $precision_control_capture(pdeclaration :: pdeclaration_tail*, n, z_capture) = pdeclaration '
            ':: $precision_control_capture(pdeclaration_tail*, n, z_capture)\n'
            '  -- if $declaration_entry_input(pdeclaration, n) = eps\n'
            'dec $precision_control_remove(pdeclaration*, nat) : pdeclaration*\n'
            'def $precision_control_remove(eps, n) = eps\n'
            'def $precision_control_remove(pdeclaration :: pdeclaration_tail*, n) = pdeclaration_tail*\n'
            '  -- if $declaration_entry_input(pdeclaration, n) =/= eps\n'
            'def $precision_control_remove(pdeclaration :: pdeclaration_tail*, n) = pdeclaration :: '
            '$precision_control_remove(pdeclaration_tail*, n)\n'
            '  -- if $declaration_entry_input(pdeclaration, n) = eps\n',
 'abrupt': 'dec $precision_resume_ready(pstate) : bool\n'
           'def $precision_resume_ready(S) = true\n'
           '  -- if S.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*\n'
           '  -- if $eval_precision_epochs(S.DECLARATIONS, pevalcompile.PLAN.UNIT) = (epochs)\n'
           '  -- if |epochs| = 0\n'
           'def $precision_resume_ready(S) = false -- otherwise\n'
           'dec $precision_resume_seek(pstate, nat) : pstate\n'
           'def $precision_resume_seek(S, n) = S -- if $precision_resume_ready(S)\n'
           'def $precision_resume_seek(S, n) = S\n'
           '  -- if ~$precision_resume_ready(S)\n'
           '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
           'def $precision_resume_seek(S, 0) = S\n'
           '  -- if ~$precision_resume_ready(S)\n'
           '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
           'def $precision_resume_seek(S, n) = $precision_resume_seek($drive_steps(S[.COMPLETION = NORMAL], '
           '1), $nabs($(n - 1)))\n'
           '  -- if ~$precision_resume_ready(S)\n'
           '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
           '  -- if $(n > 0)\n',
 'ast': 'dec $precision_ast_kind(pstate, nat) : bool\n'
        'def $precision_ast_kind(S, 0) = $class_constant_ast_active(S)\n'
        'def $precision_ast_kind(S, 1) = true\n'
        '  -- if S.CONSTCONTEXT = (pconstantcontext)\n'
        '  -- if $constant_declaration(S, pconstantcontext.ORIGIN) = ((preqbytes, z))\n'
        '  -- if $class_constant_origin(S.CLASSES, pconstantcontext.ORIGIN) = eps\n'
        'def $precision_ast_kind(S, 2) = $default_context_valid(S, pconstantcontext)\n'
        '  -- if S.CONSTCONTEXT = (pconstantcontext)\n'
        'def $precision_ast_kind(S, 3) = $static_default_ast_active(S)\n'
        'def $precision_ast_kind(S, n) = false -- otherwise\n'
        'dec $precision_ast_ready(pstate, nat) : bool\n'
        'def $precision_ast_ready(S, n) = true\n'
        '  -- if S.TODO = (CONCAT_PREP poperand_left poperand_right b_left b_right z) :: ptask_tail*\n'
        '  -- if $precision_ast_kind(S, n)\n'
        'def $precision_ast_ready(S, 4) = true\n'
        '  -- if S.TODO = (CONCAT_PREP poperand_left poperand_right true false z) :: ptask_tail*\n'
        '  -- if S.CONSTCONTEXT = eps\n'
        '  -- if S.CURRENT = (pcallcontext)\n'
        'def $precision_ast_ready(S, n) = false -- otherwise\n'
        'dec $precision_ast_seek(pstate, nat, nat) : pstate\n'
        'def $precision_ast_seek(S, n_kind, n) = S -- if $precision_ast_ready(S, n_kind)\n'
        'def $precision_ast_seek(S, n_kind, n) = S\n'
        '  -- if ~$precision_ast_ready(S, n_kind)\n'
        '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
        'def $precision_ast_seek(S, n_kind, 0) = S\n'
        '  -- if ~$precision_ast_ready(S, n_kind)\n'
        '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
        'def $precision_ast_seek(S, n_kind, n) = $precision_ast_seek($drive_steps(S[.COMPLETION = NORMAL], '
        '1), n_kind, $nabs($(n - 1)))\n'
        '  -- if ~$precision_ast_ready(S, n_kind)\n'
        '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
        '  -- if $(n > 0)\n'}

GROUP_PROGRAMS = {'initial': ['seed'], 'dynamic': ['eval', 'evalbody', 'file', 'child'],
                  'abrupt': ['rejected', 'early', 'earlybody'], 'ast': ['class', 'global', 'parameter', 'property']}
BODIES = {'evalbody': b"return 12.3456789 . 'L';",
          'earlybody': b'function precisionPaused($x){return "${x}";} class PrecisionLater {}'}


def render(fixtures, paths, cwd, group):
    prefix = ''.join('dec $precision_program_' + name + '() : program\ndef $precision_program_' + name + '() = ' + fixture + '\n'
                     for name, fixture in fixtures.items())
    checks = [row.replace('@CWD@', b64(bytes(Path(cwd)))) for row in CHECKS[group]]
    for name, path in paths.items():
        checks = [row.replace('@' + name.upper() + '@', b64(bytes(path))) for row in checks]
    assert all('@' not in row for row in checks)
    setup = ['program_' + name + ' = $precision_program_' + name + '()' for name in GROUP_PROGRAMS[group]]
    return (prefix + HELPERS.get(group, '') + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + row + '\n' for row in setup + checks) + 'def $main() = false -- otherwise\n')


def prepare(directory):
    paths = {name: SOURCES / 'state' / (name + '.php') for name in ['seed', 'eval', 'rejected', 'early', 'child', 'parameter', 'property']}
    paths['global'] = SOURCES / 'global-constant.php'
    paths['class'] = SOURCES / 'deferred-concat.php'
    paths['file'] = directory / 'file.php'
    paths['file'].write_bytes(b'<?php ini_set("precision","3tail"); $x=include '
                              + json.dumps(str(paths['child'])).encode()
                              + b'; ini_set("precision","1tail"); echo $x;')
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], directory / 'frontend')
    parsed = {}
    try:
        for name, path in paths.items():
            parsed[name] = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed[name]['accepted'], parsed[name]
        for name, body in BODIES.items():
            parsed[name] = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                             'profile': 'cli-raw-85', 'source': b64(body)})
            assert parsed[name]['accepted'], parsed[name]
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], directory / 'syntax-adapter')
    fixtures = {}
    try:
        for name, response in parsed.items():
            fixtures[name] = adapter.request({'op': 'check', 'ast': response['ast'], 'fixture': True})['fixture']
    finally:
        adapter.close()
    for group in CHECKS:
        (directory / (group + '.watsup')).write_text(render(fixtures, paths, R, group))
    metadata = {'sources': {name: str(path) for name, path in paths.items()}, 'parsed': parsed,
                'counts': {group: len(rows) for group, rows in CHECKS.items()},
                'program_bindings': {group: len(rows) for group, rows in GROUP_PROGRAMS.items()}}
    (directory / 'prepared.json').write_text(json.dumps(metadata) + '\n')
    return directory / 'prepared.json'


def transport(prepared_path, directory):
    metadata = json.loads(prepared_path.read_text())
    filename = b64(bytes(Path(metadata['sources']['seed'])))
    startup = {'precision': b64(b'5junk')}
    request = {'op': 'execute', 'ast': metadata['parsed']['seed']['ast'], 'steps': 0,
               'filename': filename, 'startup_ini': startup}
    snapshot = {'version': 1, 'main': filename, 'cwd': b64(bytes(R)),
                'include_path': b64(b'.:'), 'entries': []}
    facts = {'env': [], 'argv': [filename], 'file': filename, 'seconds': '0',
             'microseconds': 0, 'variables': b64(b'EGPCS'), 'jit': True, 'cwd': snapshot['cwd']}
    cases = [(name, dict(request, **extra), None) for name, extra in [
        ('precision-ordinary', {}), ('precision-request', {'request': facts}),
        ('precision-file', {'file_snapshot': snapshot}),
        ('precision-request-file', {'request': facts, 'file_snapshot': snapshot})]]
    cases.append(('precision-present-empty', dict(request, startup_ini={'precision': ''}), None))
    cases.append(('nullable-display-precision', dict(request, startup_ini=dict(startup, display_errors=None)), None))
    combined = copy.deepcopy(dict(request, request=facts, file_snapshot=snapshot))
    combined['startup_ini'].update(error_reporting=b64(b'30719'), include_path=b64(b'/registered'), display_errors='')
    combined['file_snapshot']['include_path'] = b64(b'/registered')
    cases.append(('four-directive-request-file', combined, None))
    cases += [(name, dict(request, startup_ini=ini), reason) for name, ini, reason in [
        ('nullable-precision', {'precision': None}, 'expected string'),
        ('invalid-startup-precision', {'precision': b64(b'-2')}, 'invalid startup precision facts'),
        ('partial-reporting-precision', dict(startup, error_reporting=b64(b'1')), 'unexpected/missing fields')]]
    rows = []
    worker = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], directory / 'entry-worker')
    try:
        for name, payload, reason in cases:
            sequence = worker.sequence
            try:
                result = worker.request(payload)
            except AssertionError:
                result = types.wire.loads((worker.output / (str(sequence) + '.response')).read_text())
            if reason is None:
                state = result['state']
                ini = payload['startup_ini']
                precision = list(map(str, base64.b64decode(ini['precision'])))
                path = ini.get('include_path', b64(b'.:'))
                expected_path = list(map(str, base64.b64decode(path))) if 'file_snapshot' in payload or 'include_path' in ini else None
                display = ini.get('display_errors', b64(b'stderr'))
                expected_display = None if display is None else list(map(str, base64.b64decode(display)))
                passed = (result['ok'] and state['COMPLETION']['tag'] == 'BUDGET'
                          and state['PRECISIONINIT'] == precision and state['PRECISIONINI'] == precision
                          and state['PRECISIONMODIFIED'] is False
                          and state['DISPLAYINI'] == expected_display
                          and state['FILEINCLUDEPATH'] == expected_path
                          and (state['REQUEST'] is not None) == ('request' in payload)
                          and (state['FILECWD'] is not None) == ('file_snapshot' in payload))
            else:
                passed = result.get('ok') is False and result.get('category') == 'runner_failure' and reason in result.get('message', '')
            rows.append({'id': name, 'packet': sequence, 'passed': passed, 'expected_reason': reason, 'actual_reason': result.get('message')})
            print(json.dumps(rows[-1]), flush=True)
            assert passed, (name, result)
    finally:
        worker.close()

    raw_packet = types.wire.dumps(request).replace(types.wire.dumps(startup), '{"precision":"NWp1bms=","precision":"Mg=="}')
    assert raw_packet != types.wire.dumps(request)
    packet_path = directory / 'duplicate-precision.stdin'
    packet_path.write_text(raw_packet + '\n')
    process = recorded(['bash', '-c', 'exec "$1" "$2" < "$3"', '--',
                        str(R / '_build/default/adapter/main.exe'), str(R), str(packet_path)],
                       directory / 'duplicate-precision', 30)
    response = types.wire.loads((directory / 'duplicate-precision.stdout').read_text())
    passed = (process['exit'] == 0 and not process['timeout'] and not (directory / 'duplicate-precision.stderr').read_bytes()
              and response.get('ok') is False and response.get('category') == 'runner_failure'
              and 'unexpected/missing fields' in response.get('message', ''))
    rows.append({'id': 'duplicate-precision-key', 'passed': passed, 'process': process, 'actual_reason': response.get('message')})
    assert passed, response

    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *types.FLAGS, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], directory / 'resume-frontend')
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], directory / 'resume-adapter')
    try:
        first = adapter.request({'op': 'execute', 'ast': metadata['parsed']['eval']['ast'], 'steps': 1000,
                                 'filename': b64(bytes(Path(metadata['sources']['eval']))), 'startup_ini': startup})
        assert first['pending']['mode'] == 'eval' and first['state']['PRECISIONINI'] == list(map(str, b'3tail'))
        parsed = frontend.request({'op': 'parse-eval', **first['pending']})
        response = {key: value for key, value in parsed.items() if key not in ('ok', 'diagnostics')}
        resumed = adapter.request({'op': 'resume_eval', 'response': response})
        state = resumed['state']
        entries = [event for event in state['DECLARATIONS'] if event['tag'] == 'PDENTERPRECISION' and event['args'][0] == '1']
        output = b''.join(bytes(map(int, event['args'][0])) for event in state['EVENTS'] if event['tag'] == 'OUTPUT')
        passed = (state['COMPLETION']['tag'] == 'NORMAL' and 'pending' not in resumed
                  and state['PRECISIONINIT'] == list(map(str, b'5junk'))
                  and state['PRECISIONINI'] == list(map(str, b'1tail')) and state['PRECISIONMODIFIED'] is True
                  and len(entries) == 1 and entries[0]['args'][3] == '3' and output == b'12.3L')
        rows.append({'id': 'genuine-execute-eval-resume-capture', 'passed': passed})
        assert passed, resumed
    finally:
        adapter.close()
        frontend.close()
    assert len(rows) == 12
    report = {'scope': 'new precision entry and exact transport boundaries', 'prepared': str(prepared_path),
              'rows': rows, 'passed': all(row['passed'] for row in rows)}
    (directory / 'transport-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'rows': len(rows), 'passed': report['passed']}), flush=True)



def main(groups=None):
    directory = Path(tempfile.mkdtemp(prefix='precision-protocol-', dir=R / '.tools'))
    print(directory, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'adapter/main.ml', R / 'bin/php-semantics',
               R / '_build/default/adapter/main.exe', R / 'tests/semantics/_build/default/numeric_runner.exe',
               R / '.tools/php/bin/php', R / '.tools/php-file.so', R / 'tests/semantics/profile.json',
               R / 'tests/semantics/recorded_worker.py', R / 'tests/semantics/error_handler_run.py',
               Path(__file__), *sorted(SOURCES.rglob('*.php'))]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = {str(path.relative_to(R)): sha(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    prepared_path = prepare(directory)
    rows = []
    for group in groups or CHECKS:
        process = recorded([str(R / 'tests/semantics/_build/default/numeric_runner.exe'),
                            *map(str, modules), str(directory / (group + '.watsup'))], directory / ('numeric-' + group), 90)
        passed = (process['exit'] == 0 and not process['timeout'] and not (directory / ('numeric-' + group + '.stderr')).read_bytes()
                  and (directory / ('numeric-' + group + '.stdout')).read_bytes() == b'true\n')
        rows.append({'group': group, 'checks': len(CHECKS[group]), 'program_bindings': len(GROUP_PROGRAMS[group]),
                     'process': process, 'passed': passed})
        assert passed, rows[-1]
    process = recorded([sys.executable, str(Path(__file__).resolve()), '--transport', str(prepared_path)], directory / 'transport', 90)
    rows.append({'transport': 12, 'process': process, 'passed': process['exit'] == 0 and not process['timeout']
                 and not (directory / 'transport.stderr').read_bytes()})
    assert inputs == {str(path.relative_to(R)): sha(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    report = {'revision': revision, 'inputs': inputs, 'rows': rows, 'passed': all(row['passed'] for row in rows),
              'scope': '199 supplied checks plus12 program bindings; later eval folding follows authenticated precision epochs.',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', action='append', choices=list(CHECKS))
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--transport', type=Path)
    args = parser.parse_args()
    if args.transport:
        transport(args.transport, args.transport.parent)
    elif args.prepare_only:
        directory = Path(tempfile.mkdtemp(prefix='precision-prepared-', dir=R / '.tools'))
        print(prepare(directory), flush=True)
    else:
        main(args.group)
