#!/usr/bin/env python3
"""Authenticate Deprecated fetch/API continuations and their selected entries."""
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
SOURCE = Path(__file__).with_name('deprecated_global_constant')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()

PREFIX = '''
var U : program
dec $dep_ready(ptask*) : bool
def $dep_ready((ERROR_HANDLER_INVOKE perrorcall) :: ptask*) = true
  -- if perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant
def $dep_ready((ERROR_HANDLER_INVOKE perrorcall) :: ptask*) = true
  -- if perrorcall.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall n
def $dep_ready(ptask*) = false -- otherwise
dec $dep_pause(pstate,nat) : pstate
def $dep_pause(S,n) = S -- if $dep_ready(S.TODO)
def $dep_pause(S,n) = $dep_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if ~$dep_ready(S.TODO)
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $dep_pause(S,n) = S -- otherwise
dec $dep_exit_ready(ptask*) : bool
def $dep_exit_ready((DEPRECATED_HANDLER_EXIT pdestructioncleanup z ptask_saved*) :: ptask_tail*) = true
def $dep_exit_ready(ptask*) = false -- otherwise
dec $dep_exit_pause(pstate,nat) : pstate
def $dep_exit_pause(S,n) = S -- if $dep_exit_ready(S.TODO)
def $dep_exit_pause(S,n) = $dep_exit_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if ~$dep_exit_ready(S.TODO)
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $dep_exit_pause(S,n) = S -- otherwise
dec $dep_throw_ready(ptask*) : bool
def $dep_throw_ready((THROW_SEARCH n) :: (DEPRECATED_HANDLER_EXIT pdestructioncleanup z ptask_saved*) :: ptask_tail*) = true
def $dep_throw_ready(ptask*) = false -- otherwise
dec $dep_throw_pause(pstate,nat) : pstate
def $dep_throw_pause(S,n) = S -- if $dep_throw_ready(S.TODO)
def $dep_throw_pause(S,n) = $dep_throw_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if ~$dep_throw_ready(S.TODO)
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $dep_throw_pause(S,n) = S -- otherwise
'''


def nodes(value, path=()):
    if isinstance(value, dict) and 'node' in value:
        yield value, path
        for index, field in enumerate(value['fields']):
            yield from nodes(field, (*path, ('PCFIELD', index)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from nodes(child, (*path, ('PCINDEX', index)))


def prepare(out):
    cases = json.loads((SOURCE / 'cases.json').read_text())
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    cancellations = ('local-throw-pending', 'cancel-source-exit3', 'cancel-api-rebind',
        'cancel-saved-handler-read', 'cancel-saved-handler-fresh-throw', 'cancel-captured-intrinsic')
    selected = ('handler-true', 'handler-false', 'interned-string', 'namespace-identity',
        'source-reference-handler', 'api-reference-handler', 'captured-intrinsic', 'array-source-pending',
        'parameter-cache', 'class-cache', 'relative-null-pending', 'metadata-expression-pending',
        'exit-shutdown', 'api-exit-shutdown', *cancellations)
    try:
        for name in selected:
            path = SOURCE / cases[name]['source']; tag = name.replace('-', '_')
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            checks += ['U_' + tag + ' = ' + checked['fixture'],
                'P_' + tag + ' = $ppstart(0,U_' + tag + ',' + types.byte_expr(str(path)) + ')']
            if name in ('relative-null-pending', 'metadata-expression-pending'):
                checks += ['P_' + tag + '.COMPLETION = PPCABRUPT (UNSUPPORTED "Deprecated global constant metadata")']
            elif name in cancellations:
                state = 'S_frontier_' + tag
                cleanup = 'pdestructioncleanup_cancel_' + tag
                saved = 'ptask_cancel_' + tag + '_saved*'
                tail = 'ptask_cancel_' + tag + '_tail*'
                error = 'perrorcall_cancel_' + tag
                initial = 'n_cancel_' + tag
                current = 'n_cancel_after_' + tag
                status = 'z_cancel_' + tag
                marker = 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ' + saved
                released = 'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ' + saved
                release = 'S_cancel_released_' + tag
                resume = 'S_cancel_resume_' + tag
                checks += ['P_' + tag + '.COMPLETION = PPCNORMAL',
                    'S_' + tag + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')',
                    'S_' + tag + '.COMPLETION = BUDGET',
                    state + ' = $dep_throw_pause(S_' + tag + '[.COMPLETION = NORMAL],10000)',
                    state + '.TODO = (THROW_SEARCH ' + initial + ') :: (' + marker + ') :: eps',
                    cleanup + '.SOURCE = ERROR_HANDLER_RESULT ' + error,
                    '~' + cleanup + '.RELEASED',
                    saved + ' = (ERROR_HANDLER_RESULT ' + error + ') :: ' + tail,
                    '$call_descriptors_valid(' + state + ')',
                    '(HOBJECT ' + initial + ') <- $machine_roots(' + state + ')',
                    '$deprecated_global_protected(' + state + ',$ptascii("X"))',
                    'S_cancel_step_' + tag + ' = $drive_steps(' + state + ',1)',
                    'S_cancel_step_' + tag + '.COMPLETION = BUDGET',
                    release + ' = $dep_throw_pause(S_cancel_step_' + tag + '[.COMPLETION = NORMAL],10000)',
                    release + '.TODO = (THROW_SEARCH ' + current + ') :: (' + released + ') :: eps',
                    '$call_descriptors_valid(' + release + ')',
                    release + '.EXITSTATUS = ' + state + '.EXITSTATUS',
                    '$deprecated_global_protected(' + release + ',$ptascii("X"))',
                    '(HOBJECT ' + current + ') <- $machine_roots(' + release + ')',
                    '$task_nodes(' + released + ') = $task_nodes(' + error + '.RESUME) ++ $tasks_nodes(' + tail + ')',
                    'PhpStep: ' + release + ' ~> ' + resume,
                    resume + '.TODO = (THROW_SEARCH ' + current + ') :: ' + tail,
                    resume + '.EXITSTATUS = ' + state + '.EXITSTATUS',
                    resume + '.CURRENT = ' + state + '.CURRENT',
                    resume + '.CONSTCONTEXT = ' + state + '.CONSTCONTEXT',
                    '~$deprecated_global_protected(' + resume + ',$ptascii("X"))',
                    '$call_descriptors_valid(' + resume + ')',
                    'S_cancel_done_' + tag + ' = $drive(' + resume + ',10000)',
                    'S_cancel_done_' + tag + '.COMPLETION = NORMAL',
                    'S_cancel_done_' + tag + '.EXITSTATUS = ' + str(cases[name].get('exit_status', 0)),
                    '$call_descriptors_valid(S_cancel_done_' + tag + ')']
                if name == 'cancel-saved-handler-fresh-throw':
                    checks += [current + ' =/= ' + initial,
                        '$throwable_field(' + release + ',' + current + ',"previous") = POBJECT ' + initial]
                else:
                    checks += [current + ' = ' + initial]
                if name.startswith('cancel-saved-handler'):
                    checks += [error + '.CALLBACK = POBJECT n_saved_callback_' + tag,
                        '~((HOBJECT n_saved_callback_' + tag + ') <- ' + release + '.ALLOCATIONS)']
                if name in ('cancel-api-rebind', 'cancel-captured-intrinsic'):
                    config = 'pconfigcall_cancel_' + tag
                    prefix = 'n_cancel_prefix_' + tag
                    checks += [error + '.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT ' + config + ' ' + prefix,
                        '$deprecated_api_query(' + config + ') = ($ptascii("X"))']
                    if name == 'cancel-captured-intrinsic':
                        bad_error = 'perrorcall_cancel_bad_owner'
                        bad_cleanup = cleanup + '[.SOURCE = ERROR_HANDLER_RESULT ' + bad_error + ']'
                        bad_saved = '((ERROR_HANDLER_RESULT ' + bad_error + ') :: ' + tail + ')'
                        bad_marker = 'DEPRECATED_HANDLER_EXIT ' + bad_cleanup + ' ' + status + ' ' + bad_saved
                        checks += [config + '.OWNER = (n_cancel_intrinsic_owner)',
                            '(HOBJECT n_cancel_intrinsic_owner) <- $task_nodes(' + marker + ')',
                            '(HOBJECT n_cancel_intrinsic_owner) <- $task_nodes(' + released + ')',
                            '(HOBJECT n_cancel_intrinsic_owner) <- $machine_roots(' + release + ')',
                            '~((HOBJECT n_cancel_intrinsic_owner) <- $machine_roots(' + resume + '))',
                            '~((HOBJECT n_cancel_intrinsic_owner) <- S_cancel_done_' + tag + '.ALLOCATIONS)',
                            bad_error + ' = ' + error + '[.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT ' + config + '[.OWNER = (100000)] ' + prefix + ']',
                            'S_cancel_bad_owner = ' + state + '[.TODO = [(THROW_SEARCH ' + initial + '),(' + bad_marker + ')]]',
                            '~$call_descriptors_valid(S_cancel_bad_owner)']
                if name == 'local-throw-pending':
                    drop = 'S_cancel_drop_' + tag
                    checks += [drop + ' = ' + state + '[.TODO = [THROW_SEARCH ' + initial + ']]',
                        '$return_discard(' + drop + ',DEPRECATED_HANDLER_EXIT ' + cleanup + '[.SOURCE = DISCARD] ' + status + ' ' + saved + ') = ' + drop,
                        '$return_discard(' + drop + ',DEPRECATED_HANDLER_EXIT ' + cleanup + ' $(' + status + ' + 1) ' + saved + ') = ' + drop,
                        '~$call_descriptors_valid(' + state + '[.TODO = [(THROW_SEARCH $(' + initial + ' + 100)),(' + marker + ')]])']
            elif name in ('exit-shutdown', 'api-exit-shutdown'):
                checks += ['P_' + tag + '.COMPLETION = PPCNORMAL',
                    'S_' + tag + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')',
                    'S_' + tag + '.COMPLETION = BUDGET',
                    'S_frontier_' + tag + ' = $dep_exit_pause(S_' + tag + '[.COMPLETION = NORMAL],10000)',
                    '$call_descriptors_valid(S_frontier_' + tag + ')']
            elif name == 'array-source-pending':
                path_fetch = next(path for node, path in nodes(parsed['ast']['program']) if node['node'] == 'Expr_ConstFetch')
                term = '[' + ','.join('(' + kind + ' ' + str(index) + ')' for kind, index in path_fetch) + ']'
                checks += ['P_' + tag + '.COMPLETION = PPCNORMAL',
                    'S_array = $php_run(U_' + tag + ',10000,' + json.dumps(b64(bytes(path))) + ')',
                    'S_array.COMPLETION = NORMAL',
                    'S_array.USERCONSTANTS = [puserconstant_array]', 'puserconstant_array.VALUE = PARRAY n_array',
                    '$global_constant_user_valid(S_array,puserconstant_array)',
                    'pcpath_array_fetch = ' + term, 'porigin_array_fetch = PORIGIN 0 pcpath_array_fetch',
                    '$deprecated_constant_source(S_array,porigin_array_fetch,1) = (z_array)',
                    'pdeprecatedconstant_array = {SITE porigin_array_fetch, LINE z_array, PREFIX 1, COPIED eps}',
                    'S_array_bad = S_array[.COMPLETION = NORMAL][.ORIGIN = (porigin_array_fetch)][.TODO = [DEPRECATED_CONSTANT_RESULT pdeprecatedconstant_array]]',
                    '~$deprecated_constant_valid(S_array_bad,pdeprecatedconstant_array)',
                    '~$call_task_valid(S_array_bad,DEPRECATED_CONSTANT_RESULT pdeprecatedconstant_array)']
            else:
                checks += ['P_' + tag + '.COMPLETION = PPCNORMAL',
                    'S_' + tag + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')',
                    'S_' + tag + '.COMPLETION = BUDGET',
                    'S_frontier_' + tag + ' = $dep_pause(S_' + tag + '[.COMPLETION = NORMAL],10000)',
                    'S_frontier_' + tag + '.TODO = (ERROR_HANDLER_INVOKE perrorcall_' + tag + ') :: ptask_' + tag + '*',
                    '$call_descriptors_valid(S_frontier_' + tag + ')']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks += [
        'S_source = S_frontier_handler_true', 'perrorcall_source = perrorcall_handler_true',
        'perrorcall_source.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'pdeprecatedconstant.PREFIX = 1', 'perrorcall_source.LEVEL = 16384',
        '$deprecated_constant_valid(S_source,pdeprecatedconstant)',
        '$deprecated_constant_value(S_source,pdeprecatedconstant.SITE) = PINT 7',
        '$deprecated_constant_identity(S_source,pdeprecatedconstant.SITE) = $ptascii("X")',
        '$deprecated_constant_message_at(S_source,pdeprecatedconstant.SITE) = $ptascii("Constant X is deprecated since 8.5, old")',
        '$deprecated_global_metadata(S_source,S_source.USERCONSTANTS[0].ORIGIN) = DEPRECATED_ATTRIBUTE ($ptascii("old")) ($ptascii("8.5"))',
        '$deprecated_constant_protected(S_source,pdeprecatedconstant.SITE)',
        '~$deprecated_global_protected(S_source,$ptascii("Y"))',
        '~$deprecated_constant_valid(S_source,pdeprecatedconstant[.LINE = $(pdeprecatedconstant.LINE + 1)])',
        '~$deprecated_constant_valid(S_source,pdeprecatedconstant[.PREFIX = 0])',
        '~$deprecated_constant_valid(S_source,pdeprecatedconstant[.PREFIX = 2])',
        '~$deprecated_constant_valid(S_source,pdeprecatedconstant[.SITE = S_source.USERCONSTANTS[0].ORIGIN])',
        'PhpStep: S_source ~> S_source_send',
        'S_source_send.TODO = (API_CALLBACK_SEND papiargcursor_source) :: ptask_source*',
        '$call_descriptors_valid(S_source_send)',
        '$deprecated_constant_valid(S_source_send,pdeprecatedconstant)',
        '$deprecated_global_protected(S_source_send,$ptascii("X"))',
        'S_source_done = $drive(S_source_send,10000)', 'S_source_done.COMPLETION = NORMAL',
        '~$deprecated_global_protected(S_source_done,$ptascii("X"))', '$call_descriptors_valid(S_source_done)',
        'S_api = S_frontier_handler_false', 'perrorcall_api = perrorcall_handler_false',
        'perrorcall_api.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall n_prefix',
        'n_prefix = 1', '$deprecated_api_valid(S_api,pconfigcall,n_prefix)',
        '$deprecated_api_query(pconfigcall) = ($ptascii("X"))',
        '$deprecated_api_identity(S_api,$ptascii("X")) = $ptascii("X")',
        '$deprecated_api_level(S_api,$ptascii("X")) = 16384',
        '$deprecated_api_value(S_api,$ptascii("X")) = (PINT 7)',
        '$task_nodes(DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall n_prefix) = $config_nodes(pconfigcall)',
        '$selected_task_nonce(DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall n_prefix) = pconfigcall.SELECTION',
        'PhpStep: S_api ~> S_api_send',
        'S_api_send.TODO = (API_CALLBACK_SEND papiargcursor_api) :: ptask_api*',
        '$call_descriptors_valid(S_api_send)', '$deprecated_api_valid(S_api_send,pconfigcall,n_prefix)',
        '$deprecated_global_protected(S_api_send,$ptascii("X"))',
        'S_api_done = $drive(S_api_send,10000)', 'S_api_done.COMPLETION = NORMAL',
        '~$deprecated_global_protected(S_api_done,$ptascii("X"))', '$call_descriptors_valid(S_api_done)',
        'perrorcall_captured_intrinsic.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall_capture n_prefix_capture',
        'pconfigcall_capture.OWNER = (n_owner)',
        '(HOBJECT n_owner) <- $task_nodes(DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall_capture n_prefix_capture)',
        '$deprecated_api_valid(S_frontier_captured_intrinsic,pconfigcall_capture,n_prefix_capture)',
        'S_capture_done = $drive(S_frontier_captured_intrinsic,10000)',
        'S_capture_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_capture_done)',
    ]
    variants = {
        'prefix-zero': ('pconfigcall', '0'), 'prefix-large': ('pconfigcall', '2'),
        'line': ('pconfigcall[.LINE = $(pconfigcall.LINE + 1)]', 'n_prefix'),
        'site': ('pconfigcall[.SITE = S_api.USERCONSTANTS[0].ORIGIN]', 'n_prefix'),
        'kind': ('pconfigcall[.KIND = INTRINSIC_DEFINED]', 'n_prefix'),
        'index': ('pconfigcall[.INDEX = 0]', 'n_prefix'),
        'named': ('pconfigcall[.NAMED = true]', 'n_prefix'),
        'empty': ('pconfigcall[.SENT = eps]', 'n_prefix'),
        'query': ('pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Y"))))]]', 'n_prefix'),
        'owner': ('pconfigcall[.OWNER = (999)]', 'n_prefix'),
        'selection': ('pconfigcall[.SELECTION = (999)]', 'n_prefix'),
    }
    for tag, (call, prefix) in variants.items():
        state = 'S_bad_' + tag.replace('-', '_')
        checks += [state + ' = S_api[.TODO = (ERROR_HANDLER_INVOKE perrorcall_api[.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT '
            + call + ' ' + prefix + ']) :: ptask_handler_false*]', '~$call_descriptors_valid(' + state + ')']
    for tag, change in [('level', '.LEVEL = 8192'), ('message', '.MESSAGE = eps'), ('line', '.LINE = 0')]:
        checks += ['~$error_call_valid(S_api,perrorcall_api[' + change + '])']
    for tag in ('parameter_cache', 'class_cache'):
        checks += ['S_' + tag + '_done = $drive(S_frontier_' + tag + ',10000)',
            'S_' + tag + '_done.COMPLETION = NORMAL',
            '$call_descriptors_valid(S_' + tag + '_done)',
            '~$deprecated_global_protected(S_' + tag + '_done,$ptascii("X"))']
    for tag in ('source', 'api'):
        state = 'S_frontier_' + tag + '_reference_handler'
        callback = 'perrorcall_' + tag + '_reference_handler'
        send = 'S_' + tag + '_ref_send'; ref = 'S_' + tag + '_ref'
        cursor = 'papiargcursor_' + tag + '_ref'
        if tag == 'source':
            checks += [callback + '.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant_ref']
            valid = '$deprecated_constant_valid(' + ref + ',pdeprecatedconstant_ref)'
        else:
            checks += [callback + '.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall_ref n_prefix_ref']
            valid = '$deprecated_api_valid(' + ref + ',pconfigcall_ref,n_prefix_ref)'
        checks += ['PhpStep: ' + state + ' ~> ' + send, 'PhpStep: ' + send + ' ~> ' + ref,
            ref + '.TODO = (API_CALLBACK_REF ' + cursor + ') :: ptask_' + tag + '_ref*',
            '$call_descriptors_valid(' + ref + ')', valid,
            '$deprecated_global_protected(' + ref + ',$ptascii("X"))',
            '~$deprecated_global_protected(' + ref + ',$ptascii("Y"))',
            'PhpStep: ' + ref + ' ~> S_' + tag + '_ref_ready',
            '$call_descriptors_valid(S_' + tag + '_ref_ready)',
            'S_' + tag + '_ref_done = $drive(S_' + tag + '_ref_ready,10000)',
            'S_' + tag + '_ref_done.COMPLETION = NORMAL',
            '$call_descriptors_valid(S_' + tag + '_ref_done)']
    checks += [
        'S_frontier_namespace_identity.USERCONSTANTS[0].ORIGIN = PORIGIN 0 pcpath_namespace',
        '$constant_declaration_context(S_frontier_namespace_identity.SOURCES[0],S_frontier_namespace_identity.CODE[0],pcpath_namespace) = (ptcontext_namespace)',
        'ptcontext_namespace.NAMESPACE = $ptascii("Ns")',
        '$deprecated_global_metadata(S_frontier_namespace_identity,S_frontier_namespace_identity.USERCONSTANTS[0].ORIGIN) = DEPRECATED_ATTRIBUTE ($ptascii("old")) eps',
        '$deprecated_api_identity(S_frontier_namespace_identity,$ptascii("NS\\\\X")) = $ptascii("ns\\\\X")',
        '$deprecated_api_message(S_frontier_namespace_identity,$ptascii("NS\\\\X")) = $ptascii("Constant Ns\\\\X is deprecated, old")',
        'S_string = $drive(S_frontier_interned_string,10000)', 'S_string.COMPLETION = NORMAL',
        '|S_string.USERCONSTANTS| = 2', 'S_string.USERCONSTANTS[1].CLASS = PVSTRING true',
        '$string_bytes(S_string.USERCONSTANTS[1].VALUE) = ($ptascii("value"))', '$call_descriptors_valid(S_string)',
        '$deprecated_global_nonowning(PINT 7)', '$deprecated_global_nonowning(PBOOL false)',
        '$deprecated_global_nonowning(PNULL)', '$deprecated_global_nonowning(PFLOAT 4609434218613702656)',
        '$deprecated_global_nonowning(PSTRING_CARRIER INTERNED_STRING ($ptascii("value")))',
        '~$deprecated_global_nonowning(PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("value")))',
        '~$deprecated_global_nonowning(PARRAY 0)', '~$deprecated_global_nonowning(POBJECT 0)',
    ]
    checks += ['$constant_declaration_context(S_frontier_namespace_identity.SOURCES[0][.ID = 99],S_frontier_namespace_identity.CODE[0],pcpath_namespace) = eps',
        '$constant_declaration_context(S_frontier_namespace_identity.SOURCES[0],S_frontier_namespace_identity.CODE[0],eps) = eps']
    for tag in ('exit_shutdown', 'api_exit_shutdown'):
        state = 'S_frontier_' + tag
        cleanup = 'pdestructioncleanup_' + tag
        saved = 'ptask_' + tag + '_saved*'
        tail = 'ptask_' + tag + '_tail*'
        error = 'perrorcall_' + tag
        status = 'z_' + tag
        marker = 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ' + saved
        released = 'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ' + saved
        checks += [state + '.TODO = (' + marker + ') :: eps',
            cleanup + '.SOURCE = ERROR_HANDLER_RESULT ' + error,
            saved + ' = (ERROR_HANDLER_RESULT ' + error + ') :: ' + tail,
            '~' + cleanup + '.RELEASED', status + ' = ' + state + '.EXITSTATUS',
            state + '.ERRORHANDLER.CALLBACK = eps',
            '$call_task_valid(' + state + ',' + marker + ')',
            '$task_nodes(' + marker + ') = $tasks_nodes(' + saved + ')',
            '$deprecated_global_protected(' + state + ',$ptascii("X"))',
            'PhpStep: ' + state + ' ~> S_release_' + tag,
            'S_release_' + tag + '.TODO = (' + released + ') :: eps',
            'S_release_' + tag + '.ERRORHANDLER.CALLBACK = (' + error + '.CALLBACK)',
            '$call_descriptors_valid(S_release_' + tag + ')',
            '$deprecated_global_protected(S_release_' + tag + ',$ptascii("X"))',
            '$task_nodes(' + released + ') = $task_nodes(' + error + '.RESUME) ++ $tasks_nodes(' + tail + ')',
            'PhpStep: S_release_' + tag + ' ~> S_unwind_' + tag,
            'S_unwind_' + tag + '.TODO = (EXIT_UNWIND ' + status + ') :: eps',
            '$call_descriptors_valid(S_unwind_' + tag + ')',
            '~$deprecated_global_protected(S_unwind_' + tag + ',$ptascii("X"))']
        cross = 'perrorcall_api' if tag == 'exit_shutdown' else 'perrorcall_source'
        malformed = [
            'DEPRECATED_HANDLER_EXIT ' + cleanup + ' $(' + status + ' + 1) ' + saved,
            'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.SOURCE = DISCARD] ' + status + ' ' + saved,
            'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.ORIGIN = eps] ' + status + ' ' + saved,
            'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' eps',
            'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ([DISCARD])',
            'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ((ERROR_HANDLER_RESULT ' + error + ') :: ' + saved + ')',
            'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.SOURCE = ERROR_HANDLER_RESULT ' + cross + '] ' + status + ' ' + saved,
        ]
        for index, bad in enumerate(malformed):
            bad_state = 'S_marker_bad_' + tag + '_' + str(index)
            checks += [bad_state + ' = ' + state + '[.TODO = [(' + bad + ')]]',
                '~$call_task_valid(' + bad_state + ',' + bad + ')',
                '~$call_descriptors_valid(' + bad_state + ')']
        checks += ['S_marker_duplicate_' + tag + ' = ' + state + '[.TODO = [(' + marker + '),(' + marker + ')]]',
            '~$call_descriptors_valid(S_marker_duplicate_' + tag + ')']
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    hashes = json.loads((SOURCE / 'hashes.json').read_text())
    watched = [Path(__file__), *modules, SOURCE / 'cases.json', SOURCE / 'hashes.json', *(SOURCE / name for name in hashes),
        *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'adapter/main.ml',
            'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'bin/php-semantics',
            '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
            'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/static_types.py',
            'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
            and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr']
            and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
