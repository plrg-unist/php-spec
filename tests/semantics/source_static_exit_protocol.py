#!/usr/bin/env python3
"""Graceful exit retires source tables through real frame and destructor steps."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_static_retirement_protocol as retirement
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT, inputs, types = retirement.ROOT, retirement.inputs, retirement.types
seq, byte_expr, b64 = retirement.seq, retirement.byte_expr, retirement.b64
STAGES = {
    'eval-source': ('static-native-v9', 'eval-main-exit-shutdown'),
    'file-source': ('static-native-v9', 'file-main-exit-shutdown'),
    'eval-callee': ('static-native-v9', 'eval-callee-local-exit'),
    'mixed-source': ('static-native-v10', 'file-eval-nested-source-exit'),
    'eval-escaped': ('static-native-v9', 'eval-escaped-source-exit'),
    'eval-reentry': ('static-native-v2', 'eval-exit-reentry'),
}
PREFIX = r'''dec $stage(pstate,text) : bool
def $stage(S,"invoke") = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
def $stage(S,"callback") = $destructor_context_kind(S,pcallcontext)
  -- if S.CURRENT = (pcallcontext)
def $stage(S,"operation") = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXIT_UNWIND 7) :: (EVAL_END n) :: ptask_tail*
def $stage(S,"operation") = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXIT_UNWIND 7) :: (FILE_END n) :: ptask_tail*
def $stage(S,"outer") = true
  -- if S.TODO = (EXIT_UNWIND 7) :: (FILE_END 1) :: ptask_tail*
def $stage(S,"caller") = true
  -- if S.TODO = (STATIC_INIT (PORIGIN 1 pcpath)) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = PORIGIN 1 pcpath_function
def $stage(S,"end") = true
  -- if S.TODO = (EVAL_END 1) :: ptask_tail*
def $stage(S,text) = false -- otherwise
dec $seek(pstate,text,nat) : pstate
def $seek(S,text,n) = S -- if $stage(S,text)
def $seek(S,text,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),text,$nabs($(n - 1)))
  -- if ~$stage(S,text) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,text,n) = S -- otherwise
''' + retirement.PREFIX[retirement.PREFIX.index('dec $one'):]


def reached(name, expression):
    return [name + '_found = ' + expression,
        name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
        name + ' = ' + name + '_found[.COMPLETION = NORMAL]']


def public(name):
    return ['$call_descriptors_valid(' + name + ')', '$declaration_entry_check(' + name + ') = ' + name,
        '$heap_valid($heap_graph(' + name + '))']


def native_record(sources, suite, case):
    report = json.loads((sources / suite / 'report.json').read_text())
    rows = report.get('records', report.get('rows'))
    row, = [row for row in rows if row.get('id', row.get('name')) == case]
    assert report.get('target', report.get('profile')) == types.PROFILE
    if 'stable_inputs' in report:
        assert report['stable_inputs']
    assert report['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    directory = sources / suite / case
    assert json.loads((directory / 'native/process.json').read_text())['exit_status'] == row['exit'] == 7
    assert (directory / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (directory / 'native/stderr').read_bytes() == row['stderr'].encode() == b''
    for name, digest in row['originals'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    return directory, row


def release_checks(before, label, unit, marker, context_kind, after_statics, box, output):
    raw, production = 'S_' + label + '_raw', 'S_' + label + '_production'
    callback, done = 'S_' + label + '_callback', 'S_' + label + '_done'
    restored = 'S_' + label + '_restored'
    operation, call = 'pdestructionoperation_' + label, 'pdestructorcall_' + label
    frame, frames = 'pframe_' + label, 'pframe_' + label + '_tail*'
    saved = 'S_' + label + '_saved'
    checks = [raw + ' = $one(' + before + ')', raw + '.STATICS = ' + after_statics,
        raw + '.TODO = ' + before + '.TODO', raw + '.EVALCONTEXTS = ' + before + '.EVALCONTEXTS',
        raw + '.FILECONTEXTS = ' + before + '.FILECONTEXTS', raw + '.EVENTS = ' + before + '.EVENTS', *public(raw),
        *reached(production, '$drive_steps(' + before + ',1)'), production + '.STATICS = ' + after_statics,
        production + '.EVALCONTEXTS = ' + before + '.EVALCONTEXTS',
        production + '.FILECONTEXTS = ' + before + '.FILECONTEXTS',
        production + '.DESTRUCTION.OPERATIONS = [' + operation + ']',
        operation + '.SOURCE = EXIT_UNWIND 7', operation + '.COMPLETION = NORMAL', operation + '.PENDING = eps',
        operation + '.CALLER = ' + before + '.CURRENT', operation + '.ORIGIN = eps',
        operation + '.VALUE = KNOWN PNULL', operation + '.BASE = BASE_VALUE (KNOWN PNULL)',
        '$exit_unwind_operation((' + operation + '),7)',
        '$exit_unwind_valid(' + production + ',7)', '$destructor_operation_valid(' + production + ',' + operation + ')',
        '~$exit_unwind_operation((' + operation + '[.SOURCE = EXIT_UNWIND 8]),7)',
        '~$exit_unwind_operation((' + operation + '[.PENDING = (' + box + ')]),7)',
        '~$exit_unwind_valid(' + production + '[.TODO = (ORIGIN_RETURN eps) :: ' + production + '.TODO],7)',
        *public(production), *reached(callback, '$seek(' + production + ',"callback",600)'),
        callback + '.CURRENT = (pcallcontext_' + label + ')',
        '$destructor_context_kind(' + callback + ',pcallcontext_' + label + ')',
        callback + '.FRAMES = ' + frame + ' :: ' + frames, frames + ' = ' + before + '.FRAMES',
        frame + '.CONTEXT = ' + before + '.CURRENT', frame + '.ORIGIN = eps',
        frame + '.TODO = (DESTRUCTOR_RESULT ' + call + ') :: ptask_' + label + '_callback_tail*',
        call + '.OBJECT = ' + box, call + '.PENDING = eps', call + '.OPERATION = (' + operation + ')',
        saved + ' = $destructor_saved_frame_scope($constant_frame_scope(' + callback + ',' + frame + ',' + frames + '),' + frame + ')',
        '$call_tasks_valid(' + saved + ',' + frame + '.TODO)',
        '$exit_unwind_tasks(' + saved + ',' + frame + '.TODO,7)',
        '$source_static_exit_tail(' + saved + ',' + frame + '.TODO) = (' + marker + ') :: ptask_' + label + '_tail*',
        '~$source_static_exit_' + context_kind + '(' + callback + ',' + str(unit) + ',ptask_' + label + '_tail*)',
        *public(callback), *reached(done, '$seek(' + callback + ',"operation",600)'),
        done + '.TODO = (DESTRUCTOR_OPERATION_EXIT ' + operation + ') :: (EXIT_UNWIND 7) :: (' + marker + ') :: ptask_' + label + '_tail*',
        done + '.DESTRUCTION.OPERATIONS = [' + operation + ']', done + '.CURRENT = ' + before + '.CURRENT',
        done + '.EVALCONTEXTS = ' + before + '.EVALCONTEXTS', done + '.FILECONTEXTS = ' + before + '.FILECONTEXTS',
        '$test_outputs(' + done + '.EVENTS) = $ptascii(' + json.dumps(output) + ')',
        '$exit_unwind_valid(' + done + ',7)', *public(done), restored + ' = $one(' + done + ')',
        restored + '.TODO = (EXIT_UNWIND 7) :: (' + marker + ') :: ptask_' + label + '_tail*',
        restored + '.DESTRUCTION.OPERATIONS = eps', restored + '.STATICS = ' + after_statics,
        restored + '.CURRENT = ' + before + '.CURRENT', restored + '.EVALCONTEXTS = ' + before + '.EVALCONTEXTS',
        restored + '.FILECONTEXTS = ' + before + '.FILECONTEXTS',
        '$source_static_next(' + restored + ',' + str(unit) + ') = eps', '$exit_unwind_valid(' + restored + ',7)', *public(restored)]
    return checks, done, restored


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(source, mode, unit=1, child=None):
            request = {'op': 'parse', 'source': b64(source)} if mode == 'main' else {
                'op': 'parse-' + mode, 'id': str(unit), 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(child)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            return parsed['ast'], adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']

        def setup(directory, is_file, prefix='S'):
            main_path = directory / 'main.php'
            main_ast, main_fixture = checked(main_path.read_bytes(), 'main')
            child_path = directory / 'unit.php' if is_file else None
            if is_file:
                child_bytes = child_path.read_bytes()
            else:
                evaluation = next(node for _, node, ancestors in retirement.nodes(main_ast['program'])
                    if node['node'] == 'Expr_Eval' and 'Stmt_ClassMethod' not in ancestors)
                child_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
            child_ast, child_fixture = checked(child_bytes, 'file' if is_file else 'eval', child=child_path)
            checks = [prefix + '_wait = $php_file_run(' + main_fixture + ',1800,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                prefix + '_wait.COMPLETION = SOURCE_PENDING']
            if is_file:
                checks += [prefix + '_wait.FILECONTEXTS = [pfilecontext_' + prefix + '_wait]',
                    prefix + '_parse = $file_open_resume(' + prefix + '_wait,FILE_OPENED pfilecontext_' + prefix + '_wait.NONCE pfilecontext_' + prefix + '_wait.CALLER pfilecontext_' + prefix + '_wait.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    prefix + '_parse.COMPLETION = SOURCE_PENDING',
                    prefix + '_ready = $file_parse_resume(' + prefix + '_parse,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
            else:
                checks += [prefix + '_ready = $eval_resume(' + prefix + '_wait,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
            return checks + [prefix + '_ready.COMPLETION = NORMAL'], child_ast, main_ast

        for name in names:
            suite, case = STAGES[name]
            directory, native = native_record(sources, suite, case)
            is_file = name in ['file-source', 'mixed-source']
            checks, child_ast, main_ast = setup(directory, is_file)
            if name == 'eval-reentry':
                evaluation = next(node for _, node, ancestors in retirement.nodes(main_ast['program'])
                    if node['node'] == 'Expr_Eval' and 'Stmt_ClassMethod' in ancestors)
                inner_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
                _, inner_fixture = checked(inner_bytes, 'eval', 2)
                response = 'SOURCE_ACCEPT 2 ' + seq(inner_bytes) + ' ' + inner_fixture
                response_next = 'SOURCE_ACCEPT 3 ' + seq(inner_bytes) + ' ' + inner_fixture
                checks += ['S_pending = $drive_steps(S_ready,2400)', 'S_pending.COMPLETION = SOURCE_PENDING',
                    'S_pending.TODO = (EVAL_AWAIT 2) :: ptask_pending_tail*',
                    'S_pending.EVALCONTEXTS = [pevalcontext_pending,pevalcontext_source]',
                    'pevalcontext_pending.UNIT = 2', 'pevalcontext_pending.PHASE = PARSER_WAIT',
                    'pevalcontext_pending.OWNER = 1', 'pevalcontext_source.UNIT = 1',
                    'pevalcontext_source.PHASE = UNIT_RUN', 'pevalcontext_source.OWNER = 0',
                    'S_pending.STATICS = eps', '$test_outputs(S_pending.EVENTS) = $ptascii("B|D|")',
                    '$eval_pending_response(S_pending.EVALCONTEXTS,' + response + ')',
                    '$eval_response_valid(S_pending,' + response + ')', *public('S_pending'),
                    'S_pending.FRAMES = [pframe]', 'S_pending.CURRENT = (pcallcontext)',
                    '$destructor_context_kind(S_pending,pcallcontext)',
                    'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_callback_tail*',
                    'S_saved = $destructor_saved_frame_scope($constant_frame_scope(S_pending,pframe,eps),pframe)',
                    'S_saved.EVALCONTEXTS = S_pending.EVALCONTEXTS',
                    '$eval_context_at(S_saved.EVALCONTEXTS,1) = (pevalcontext_source)',
                    '$source_static_eval_owner(S_saved,(pevalcontext_source))',
                    '$source_static_exit_eval(S_saved,1,pevalcontext_source.TAIL)',
                    '$exit_unwind_valid(S_saved,7)', '$exit_unwind_tasks(S_saved,pframe.TODO,7)',
                    '$call_tasks_valid(S_saved,pframe.TODO)',
                    '$source_static_exit_tail(S_saved,pframe.TODO) = (EVAL_END 1) :: pevalcontext_source.TAIL',
                    '~$source_static_exit_eval(S_pending,1,pevalcontext_source.TAIL)',
                    '~$source_static_exit_eval(S_saved,2,pevalcontext_source.TAIL)',
                    '~$source_static_exit_eval(S_saved,99,pevalcontext_source.TAIL)',
                    '~$source_static_exit_eval(S_saved,1,[ORIGIN_RETURN eps])',
                    '~$eval_response_valid(S_pending,SOURCE_ACCEPT 3 ' + seq(inner_bytes) + ' ' + inner_fixture + ')']
                for field, value in [('UNIT', '99'), ('OWNER', '1'), ('TAIL', '[ORIGIN_RETURN eps]')]:
                    checks += ['~$call_descriptors_valid(S_pending[.EVALCONTEXTS = [pevalcontext_pending,pevalcontext_source[.' + field + ' = ' + value + ']]])']
                checks += ['S_inner_ready = $eval_resume(S_pending,' + response + ')',
                    'S_inner_ready.COMPLETION = NORMAL', *public('S_inner_ready'),
                    'S_second = $drive_steps(S_inner_ready,1800)', 'S_second.COMPLETION = SOURCE_PENDING',
                    'S_second.TODO = (EVAL_AWAIT 3) :: ptask_second_tail*',
                    'S_second.EVALCONTEXTS = [pevalcontext_second,pevalcontext_source]',
                    'pevalcontext_second.UNIT = 3', 'pevalcontext_second.PHASE = PARSER_WAIT',
                    'pevalcontext_second.OWNER = 1', 'S_second.STATICS = eps',
                    '$test_outputs(S_second.EVENTS) = $ptascii("B|D|4|")',
                    '$eval_response_valid(S_second,' + response_next + ')', *public('S_second'),
                    'S_last_ready = $eval_resume(S_second,' + response_next + ')', 'S_last_ready.COMPLETION = NORMAL',
                    'S_finished = $drive_steps(S_last_ready,2400)', 'S_finished.COMPLETION = EXITED 7',
                    'S_finished.EVALCONTEXTS = eps', 'S_finished.FILECONTEXTS = eps', 'S_finished.STATICS = eps',
                    '$test_clean_events(S_finished.EVENTS)', '$test_outputs(S_finished.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
                    *public('S_finished')]
                target = out / name
                target.mkdir()
                (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
                (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
                continue
            ready = 'S_ready'
            unit, marker, context_kind = 1, 'FILE_END 1' if is_file else 'EVAL_END 1', 'file' if is_file else 'eval'
            if name == 'mixed-source':
                evaluation = next(node for _, node, _ in retirement.nodes(child_ast['program']) if node['node'] == 'Expr_Eval')
                inner_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
                _, inner_fixture = checked(inner_bytes, 'eval', 2)
                checks += ['S_inner_wait = $drive_steps(S_ready,1200)', 'S_inner_wait.COMPLETION = SOURCE_PENDING',
                    'S_inner_ready = $eval_resume(S_inner_wait,SOURCE_ACCEPT 2 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    'S_inner_ready.COMPLETION = NORMAL']
                ready, unit, marker, context_kind = 'S_inner_ready', 2, 'EVAL_END 2', 'eval'
            checks += [*reached('S', '$seek(' + ready + ',"invoke",1800)'),
                'S.TODO = (EXIT_INVOKE pexitcall) :: ptask_original*', 'pexitcall.SENT = [KNOWN (PINT 7)]',
                '$exit_invoke_valid(S,pexitcall)', *public('S')]
            contexts, context = ('FILECONTEXTS', 'pfilecontext') if context_kind == 'file' else ('EVALCONTEXTS', 'pevalcontext')
            checks += ['S.' + contexts + ' = [' + context + ']',
                context + '.UNIT = ' + ('(' + str(unit) + ')' if context_kind == 'file' else str(unit)),
                context + '.PHASE = ' + ('FILE_UNIT_RUN' if context_kind == 'file' else 'UNIT_RUN')]
            if name == 'mixed-source':
                checks += ['S.FILECONTEXTS = [pfilecontext_outer]', 'S.STATICS = [pstaticcell_outer,pstaticcell]',
                    'S.STORE[pstaticcell_outer.CELL] = DEFINED (POBJECT n_outer)', '$source_static_next(S,1) = (pstaticcell_outer.ORIGIN)']
            else:
                checks += ['S.STATICS = [pstaticcell]']
            checks += ['S.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_box)',
                '$source_static_next(S,' + str(unit) + ') = (pstaticcell.ORIGIN)']
            if name == 'eval-callee':
                checks += ['S.CURRENT = (pcallcontext_callee)', 'pcallcontext_callee.FUNCTION = PORIGIN 0 pcpath_callee',
                    'S.FRAMES = [pframe_callee_saved]', 'pevalcontext.OWNER = 0',
                    '$lookup(S.ENV,$ptascii("local")) = (n_local)', 'S.STORE[n_local] = DEFINED (POBJECT n_callee)',
                    'n_callee =/= n_box', '$source_static_exit_tail(S,S.TODO) = eps',
                    'S_raw_invoke = $one(S)', 'S_raw_invoke.COMPLETION = EXITED 7', 'S_raw_invoke.TODO = eps',
                    'S_raw_invoke.EVALCONTEXTS = S.EVALCONTEXTS', 'S_raw_invoke.STATICS = S.STATICS',
                    *reached('S_callee', '$drive_steps(S,1)'), 'S_callee.TODO = [EXIT_UNWIND 7]',
                    'S_callee.FRAMES = S.FRAMES', 'S_callee.CURRENT = S.CURRENT', 'S_callee.STATICS = S.STATICS',
                    '$exit_unwind_valid(S_callee,7)', *public('S_callee'),
                    'S_raw_restore = $one(S_callee)', 'S_raw_restore.FRAMES = eps',
                    'S_raw_restore.TODO = (EXIT_UNWIND 7) :: (EVAL_END 1) :: pevalcontext.TAIL',
                    'S_raw_restore.STATICS = S.STATICS', *public('S_raw_restore'),
                    *reached('S_frame_production', '$drive_steps(S_callee,1)'),
                    'S_frame_production.STATICS = S.STATICS',
                    'S_frame_production.DESTRUCTION.OPERATIONS = [pdestructionoperation_frame]',
                    'pdestructionoperation_frame.SOURCE = EXIT_UNWIND 7', 'pdestructionoperation_frame.PENDING = eps',
                    *public('S_frame_production'), *reached('S_frame_callback', '$seek(S_frame_production,"callback",600)'),
                    'S_frame_callback.CURRENT = (pcallcontext_frame)', '$destructor_context_kind(S_frame_callback,pcallcontext_frame)',
                    'pcallcontext_frame.RECEIVER = (n_callee)', 'S_frame_callback.STATICS = S.STATICS', *public('S_frame_callback'),
                    *reached('S_frame_done', '$seek(S_frame_callback,"operation",600)'),
                    'S_frame_done.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_frame) :: (EXIT_UNWIND 7) :: (EVAL_END 1) :: pevalcontext.TAIL',
                    'S_frame_done.STATICS = S.STATICS', '$test_outputs(S_frame_done.EVENTS) = $ptascii("B|F|F-D|")',
                    *public('S_frame_done'), *reached('S_exit', '$drive_steps(S_frame_done,1)')]
            else:
                checks += [context + '.OWNER = |S.FRAMES|', 'S.CURRENT = eps', '$source_static_running(S,' + str(unit) + ')',
                    'S_raw_invoke = $one(S)', 'S_raw_invoke.COMPLETION = NORMAL',
                    'S_raw_invoke.TODO = (EXIT_UNWIND 7) :: (' + marker + ') :: ' + context + '.TAIL',
                    'S_raw_invoke.STATICS = S.STATICS', *public('S_raw_invoke'), *reached('S_exit', '$drive_steps(S,1)')]
            checks += ['S_exit.TODO = (EXIT_UNWIND 7) :: (' + marker + ') :: ptask_source_tail*',
                'ptask_source_tail* = ' + context + '.TAIL', 'S_exit.CURRENT = eps', 'S_exit.FRAMES = eps',
                'S_exit.' + contexts + ' = S.' + contexts, 'S_exit.STATICS = S.STATICS',
                '$source_static_exit_tail(S_exit,S_exit.TODO) = (' + marker + ') :: ptask_source_tail*',
                '$exit_unwind_valid(S_exit,7)', *public('S_exit'),
                '~$exit_unwind_valid(S_exit,8)',
                '~$call_descriptors_valid(S_exit[.' + contexts + ' = [' + context + '[.OWNER = 1]]])',
                '~$call_descriptors_valid(S_exit[.' + contexts + ' = [' + context + '[.TAIL = [ORIGIN_RETURN eps]]]])',
                '~$call_descriptors_valid(S_exit[.' + contexts + ' = [' + context + '[.SITE = PORIGIN 99 eps]]])',
                '$source_static_exit_tail(S_exit,[(EVAL_END 99)] ++ ptask_source_tail*) = eps']
            if name == 'eval-escaped':
                checks += ['$lookup(S_exit.ENV,$ptascii("refs")) = (n_refs_cell)',
                    'S_exit.STORE[n_refs_cell] = DEFINED (PARRAY n_refs)', 'S_exit.ARRAYS[n_refs].ITEMS = [ENTRY (KINT 0) (ALIAS pstaticcell.CELL)]',
                    'S_raw = $one(S_exit)', 'S_raw.STATICS = eps', 'S_raw.TODO = S_exit.TODO', *public('S_raw'),
                    *reached('S_drop', '$drive_steps(S_exit,1)'), 'S_drop.STATICS = eps',
                    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_escaped) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_escaped) :: S_exit.TODO',
                    'S_drop.DESTRUCTION.OPERATIONS = [pdestructionoperation_escaped]',
                    'S_drop.DESTRUCTION.RELEASES = [pdestructionrelease_escaped]',
                    'pdestructionoperation_escaped.SOURCE = EXIT_UNWIND 7', 'pdestructionoperation_escaped.PENDING = eps',
                    '$exit_unwind_operation((pdestructionoperation_escaped),7)', '$exit_unwind_valid(S_drop,7)',
                    'S_drop.ARRAYS = S_exit.ARRAYS',
                    '(HCELL n_refs_cell) <- $machine_roots(S_drop)',
                    '(HEDGE (HARRAY n_refs) (HCELL pstaticcell.CELL)) <- $heap_graph(S_drop).EDGES',
                    '(HEDGE (HCELL pstaticcell.CELL) (HOBJECT n_box)) <- $heap_graph(S_drop).EDGES',
                    '$heap_owners($heap_graph(S_drop),HOBJECT n_box) = 1',
                    '$test_outputs(S_drop.EVENTS) = $ptascii("B|")', *public('S_drop'),
                    *reached('S_released', '$seek(S_drop,"operation",600)'),
                    'S_released.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_escaped) :: S_exit.TODO',
                    'S_released.DESTRUCTION.OPERATIONS = [pdestructionoperation_escaped]',
                    'S_released.DESTRUCTION.RELEASES = eps', 'S_released.CURRENT = eps', 'S_released.FRAMES = eps',
                    'S_released.STATICS = eps', 'S_released.EVALCONTEXTS = S_exit.EVALCONTEXTS',
                    'S_released.ARRAYS = S_exit.ARRAYS', 'S_released.EVENTS = S_exit.EVENTS',
                    '(HCELL n_refs_cell) <- $machine_roots(S_released)',
                    '$heap_owners($heap_graph(S_released),HOBJECT n_box) = 1', *public('S_released'),
                    'S_restored = $one(S_released)', 'S_restored.TODO = S_exit.TODO',
                    'S_restored.DESTRUCTION.OPERATIONS = eps', 'S_restored.EVALCONTEXTS = S_exit.EVALCONTEXTS',
                    *public('S_restored'),
                    'S_crossed = $one(S_restored)', 'S_crossed.EVALCONTEXTS = eps', 'S_crossed.TODO = [EXIT_UNWIND 7]',
                    'S_crossed.ARRAYS = S_restored.ARRAYS', '(HCELL n_refs_cell) <- $machine_roots(S_crossed)',
                    '$heap_owners($heap_graph(S_crossed),HOBJECT n_box) = 1', *public('S_crossed')]
                final = 'S_drop'
            else:
                output = 'O-B|I-B|I|' if name == 'mixed-source' else 'B|F|F-D|D|' if name == 'eval-callee' else 'B|D|'
                part, final, restored = release_checks('S_exit', 'source', unit, marker, context_kind,
                    '[pstaticcell_outer]' if name == 'mixed-source' else 'eps', 'n_box', output)
                checks += part + ['S_crossed = $one(' + restored + ')', 'S_crossed.' + contexts + ' = eps',
                    '~$source_static_running(S_crossed,' + str(unit) + ')', *public('S_crossed')]
                if name == 'mixed-source':
                    checks += ['S_crossed.FILECONTEXTS = S.FILECONTEXTS', 'S_crossed.STATICS = [pstaticcell_outer]',
                        'S_crossed.TODO = (EXIT_UNWIND 7) :: (FILE_END 1) :: pfilecontext_outer.TAIL',
                        '(HCELL pstaticcell_outer.CELL) <- $machine_roots(S_crossed)',
                        *reached('S_outer', '$seek(' + final + ',"outer",600)'),
                        'S_outer.TODO = S_crossed.TODO', 'S_outer.FILECONTEXTS = S.FILECONTEXTS',
                        'S_outer.STATICS = [pstaticcell_outer]', *public('S_outer')]
                    part, final, outer_restored = release_checks('S_outer', 'outer', 1, 'FILE_END 1', 'file', 'eps', 'n_outer', 'O-B|I-B|I|O|')
                    checks += part + ['S_outer_crossed = $one(' + outer_restored + ')', 'S_outer_crossed.FILECONTEXTS = eps',
                        'S_outer_crossed.TODO = [EXIT_UNWIND 7]', *public('S_outer_crossed')]
                else:
                    checks += ['S_crossed.TODO = [EXIT_UNWIND 7]']
            checks += ['S_finished = $drive_steps(' + final + ',2400)', 'S_finished.COMPLETION = EXITED 7',
                'S_finished.EVALCONTEXTS = eps', 'S_finished.FILECONTEXTS = eps', 'S_finished.STATICS = eps',
                '$test_clean_events(S_finished.EVENTS)', '$test_outputs(S_finished.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
                *public('S_finished')]
            if name == 'eval-source':
                caller_directory, _ = retirement.native_record(sources, 'static-native-v5', 'eval-retained-cell')
                extra, _, _ = setup(caller_directory, False, 'S_caller')
                checks += extra + [*reached('S_callable', '$seek(S_caller_ready,"caller",1200)'),
                    'S_callable.CURRENT = (pcallcontext_same)', 'pcallcontext_same.FUNCTION = PORIGIN 1 pcpath_same',
                    '~$source_static_caller(S_callable,1)', *public('S_callable'),
                    *reached('S_end', '$seek(S_callable,"end",1200)'), 'S_end.EVALCONTEXTS = [pevalcontext_same]',
                    '$source_static_exit_eval(S_end,1,pevalcontext_same.TAIL)', *public('S_end'),
                    'S_borrow = S_end[.CURRENT = (pcallcontext_same)]',
                    '$source_static_eval_owner(S_borrow,(pevalcontext_same))', '~$source_static_caller(S_borrow,1)',
                    '~$source_static_exit_eval(S_borrow,1,pevalcontext_same.TAIL)',
                    '$source_static_exit_tail(S_borrow,S_end.TODO) = eps', '~$call_descriptors_valid(S_borrow)']
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names = args.stage or list(STAGES)
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    out, sources = args.output.resolve(), args.sources.resolve()
    paths = [Path(__file__), Path(retirement.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    selections = [STAGES[name] for name in names]
    if 'eval-source' in names:
        selections += [('static-native-v5', 'eval-retained-cell')]
    for suite, case in selections:
        directory = sources / suite / case
        paths += [sources / suite / 'report.json', *sorted(directory.glob('*.php')),
            *[directory / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        for name in names:
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                directory = out / name
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(directory / 'protocol.watsup')], directory / label, 90, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                count = len(json.loads((directory / 'assertions.json').read_text()))
                report['records'].append({'id': name, 'pass': passed, 'runtime_assertions': count})
                report['runtime_assertions'] += count if passed else 0
                print(name, passed, flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
