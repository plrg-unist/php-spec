#!/usr/bin/env python3
"""A consumed CHDIR failure resumes after a real handler directory change."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

from include_chdir_pipe_protocol import ROOT, PREFIX, b64, seq
from include_mutable_execution import CASES
from recorded_worker import Worker

CASE = 'chdir-warning-normal-held-cwd'
SEEK = '''dec $dir_warning_result_ready(pstate) : bool
def $dir_warning_result_ready(S) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CHDIR_WARNING_RESULT pdircontext n_error* n_errno
def $dir_warning_result_ready(S) = false -- otherwise
dec $dir_warning_probe_live(pstate) : bool
def $dir_warning_probe_live(S) = (~S.COMPILESTOP /\\ (S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET))
dec $dir_warning_seek_result(pstate, nat) : pstate
def $dir_warning_seek_result(S, 0) = S
def $dir_warning_seek_result(S, n + 1) = S -- if $dir_warning_result_ready(S)
def $dir_warning_seek_result(S, n + 1) = S
  -- if ~$dir_warning_result_ready(S)
  -- if ~$dir_warning_probe_live(S)
def $dir_warning_seek_result(S, n + 1) = $dir_warning_seek_result($drive_steps(S[.COMPLETION = NORMAL], 1), n)
  -- if ~$dir_warning_result_ready(S)
  -- if $dir_warning_probe_live(S)
'''


def prepare(program, main, cwd):
    initial = seq(os.fsencode(cwd.resolve()))
    sub = seq(os.fsencode((cwd / 'sub').resolve()))
    start = ('$php_file_run(' + program + ',10000,$base64('
             + json.dumps(b64(os.fsencode(main.resolve()))) + '),$base64('
             + json.dumps(b64(os.fsencode(cwd.resolve()))) + '))')
    failure = 'DIR_FAILED 1 ' + sub + ' ' + seq(b'missing') + ' ' + seq(b'No such file or directory') + ' 2'
    checks = [
        'S_inner = ' + start,
        'S_inner.COMPLETION = SOURCE_PENDING',
        '~S_inner.COMPILESTOP',
        'S_inner.DIRCONTEXT = (pdircontext_inner)',
        'pdircontext_inner.NONCE = 0',
        'pdircontext_inner.CWD = ' + initial,
        'pdircontext_inner.REQUESTED = $ptascii("sub")',
        'pdircontext_inner.FRAMEOWNER = 2',
        'S_inner.CURRENT = (pcallcontext_string)',
        'pcallcontext_string.ARGC = 0',
        'pcallcontext_string.PARAMS = eps',
        '$config_string_trace_context(S_inner,pcallcontext_string)',
        '$outputs(S_inner.EVENTS) = $ptascii("2:A:B|RC0ZN")',
        '$call_descriptors_valid(S_inner)',
        'S = $dir_continue(S_inner,DIR_CHANGED 0 ' + initial + ' ' + seq(b'sub') + ' ' + sub + ')',
        'S.COMPLETION = SOURCE_PENDING',
        'S.DIRCONTEXT = (pdircontext)',
        'pdircontext.NONCE = 1',
        'pdircontext.CWD = ' + sub,
        'pdircontext.REQUESTED = $ptascii("missing")',
        'pdircontext.FRAMEOWNER = 1',
        'pdircontext.CONVERSION = (0)',
        'pconfigcall = pdircontext.CALL',
        'pconfigcall.KIND = INTRINSIC_CHDIR',
        'pconfigcall.OWNER = (n_owner)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
        'pconfigcall.SITE = PORIGIN n_unit pcpath',
        'porigin_child = PORIGIN n_unit (pcpath ++ [PCFIELD 0])',
        'z_child = $pipe_send_line(S,pconfigcall.SITE)',
        'z_child =/= pconfigcall.LINE',
        '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
        'S.CURRENT = (pcallcontext_caller)',
        'pcallcontext_caller.ARGC = 2',
        'S.FILECWD = (' + sub + ')',
        'S.FILEINCLUDEPATH = (' + seq(b'.:\0before') + ')',
        '$dir_response_valid(S,' + failure + ')',
        '~$dir_response_valid(S,DIR_FAILED 0 ' + sub + ' ' + seq(b'missing') + ' ' + seq(b'No such file or directory') + ' 2)',
        '~$dir_response_valid(S,DIR_FAILED 1 ' + initial + ' ' + seq(b'missing') + ' ' + seq(b'No such file or directory') + ' 2)',
        '~$dir_response_valid(S,DIR_FAILED 1 ' + sub + ' ' + seq(b'forged') + ' ' + seq(b'No such file or directory') + ' 2)',
        'S_dispatch = $dir_resume(S,' + failure + ')',
        'S_dispatch.COMPLETION = NORMAL',
        'S_dispatch.DIRCONTEXT = eps',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: pdircontext.TAIL',
        'perrorcall.RESUME = CHDIR_WARNING_RESULT pdircontext $ptascii("No such file or directory") 2',
        'perrorcall.SITE = pconfigcall.SITE',
        'perrorcall.LEVEL = 2',
        'perrorcall.LINE = pconfigcall.LINE',
        'perrorcall.MESSAGE = $ptascii("chdir(): No such file or directory (errno 2)")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE',
        'S_dispatch.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        '$error_call_valid(S_dispatch,perrorcall)',
        '$dir_warning_valid(S_dispatch,pdircontext,$ptascii("No such file or directory"),2)',
        '$call_descriptors_valid(S_dispatch)',
        '(HOBJECT n_object) <- $task_nodes(perrorcall.RESUME)',
        '(HOBJECT n_owner) <- $task_nodes(perrorcall.RESUME)',
        '~$error_call_valid(S_dispatch[.CODE = eps],perrorcall)',
        '~$error_call_valid(S_dispatch,perrorcall[.SITE = porigin_child])',
        '~$error_call_valid(S_dispatch,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_dispatch,perrorcall[.LINE = 999])',
        '~$error_call_valid(S_dispatch,perrorcall[.MESSAGE = $ptascii("forged")])',
        '~$error_call_valid(S_dispatch,perrorcall[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE perrorcall.LINE])',
        '~$dir_warning_valid(S_dispatch,pdircontext[.NONCE = 0],$ptascii("No such file or directory"),2)',
        '~$dir_warning_valid(S_dispatch,pdircontext[.REQUESTED = $ptascii("forged")],$ptascii("No such file or directory"),2)',
        '~$dir_warning_valid(S_dispatch,pdircontext[.CALL = pconfigcall[.KIND = INTRINSIC_INI_GET]],$ptascii("No such file or directory"),2)',
        '~$dir_warning_valid(S_dispatch,pdircontext[.FRAMEOWNER = 0],$ptascii("No such file or directory"),2)',
        '~$dir_warning_valid(S_dispatch,pdircontext[.TAIL = eps],$ptascii("No such file or directory"),2)',
        '~$call_descriptors_valid(S_dispatch[.ALLOCATIONS = $call_remove_owner(S_dispatch.ALLOCATIONS,HOBJECT n_object)])',
        '~$call_descriptors_valid(S_dispatch[.ALLOCATIONS = $call_remove_owner(S_dispatch.ALLOCATIONS,HOBJECT n_owner)])',
        'S_handler = $drive_steps(S_dispatch,10000)',
        'S_handler.COMPLETION = SOURCE_PENDING',
        'S_handler.DIRCONTEXT = (pdircontext_handler)',
        'pdircontext_handler.NONCE = 2',
        'pdircontext_handler.CWD = ' + sub,
        'pdircontext_handler.REQUESTED = $ptascii("..")',
        'S_handler.CURRENT = (pcallcontext_handler)',
        'pcallcontext_handler.ARGC = 4',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall) = [PSTRING $ptascii("missing")]',
        'S_handler.FRAMES = pframe_caller :: pframe_tail*',
        'pframe_caller.CONTEXT = (pcallcontext_caller)',
        'pframe_caller.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: pdircontext.TAIL',
        'perrorcall_entered.RESUME = perrorcall.RESUME',
        '$call_descriptors_valid(S_handler)',
        '$outputs(S_handler.EVENTS) = $ptascii("2:A:B|RC0ZNH4W")',
        'S_back = $dir_resume(S_handler,DIR_CHANGED 2 ' + sub + ' ' + seq(b'..') + ' ' + initial + ')',
        'S_result = $dir_warning_seek_result(S_back,1000)',
        '$dir_warning_result_ready(S_result)',
        'S_result.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: pdircontext.TAIL',
        'S_result.RESULT = KNOWN (PINT 0)',
        'S_result.CURRENT = (pcallcontext_caller)',
        'S_result.DIRSEQ = 3',
        'S_result.FILECWD = (' + initial + ')',
        'S_result.FILEINCLUDEPATH = (' + seq(b'.:\0normal') + ')',
        '$dir_warning_valid(S_result,pdircontext,$ptascii("No such file or directory"),2)',
        '~$dir_warning_valid(S_result,pdircontext[.NONCE = 2],$ptascii("No such file or directory"),2)',
        '~$dir_warning_valid(S_result,pdircontext[.REQUESTED = $ptascii("..")],$ptascii("No such file or directory"),2)',
        '$call_descriptors_valid(S_result)',
        'S_ready = $drive_steps(S_result[.COMPLETION = NORMAL],1)',
        'S_ready.TODO = (CHDIR_WARNING_RESULT pdircontext $ptascii("No such file or directory") 2) :: pdircontext.TAIL',
        'S_ready.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        'S_ready.EVENTS = S_result.EVENTS',
        'S_done = $drive_steps(S_ready[.COMPLETION = NORMAL],1)',
        'S_done.RESULT = KNOWN (PBOOL false)',
        'S_done.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_done.TODO = pdircontext.TAIL',
        'S_done.ORIGIN = (pconfigcall.SITE)',
        'S_done.FILECWD = S_result.FILECWD',
        'S_done.FILEINCLUDEPATH = S_result.FILEINCLUDEPATH',
        'S_done.EVENTS = S_result.EVENTS',
        '$call_descriptors_valid(S_done)',
        'S_file = $drive_steps(S_done[.COMPLETION = NORMAL],10000)',
        'S_file.COMPLETION = SOURCE_PENDING',
        'S_file.DIRCONTEXT = eps',
        'S_file.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
        'pfilecontext.PHASE = FILE_RESOLVE_WAIT',
        'pfilecontext.CWD = ' + initial,
        '$outputs(S_file.EVENTS) = $ptascii("2:A:B|RC0ZNH4WFS")',
        '$call_descriptors_valid(S_file)',
    ]
    for completion in ['PHPERROR $ptascii("stop") 1', 'EXITED 7', 'SOURCE_PENDING']:
        checks += ['S_stopped = S_result[.TODO = eps][.COMPLETION = ' + completion + ']',
                   '$dir_warning_seek_result(S_stopped,3) = S_stopped']
    return (PREFIX + SEEK + 'dec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks), len(checks))


def main():
    directory = Path(tempfile.mkdtemp(prefix='include-chdir-warning-', dir=ROOT / '.tools'))
    (directory / 'sub').mkdir()
    main_path = directory / 'main.php'
    source = CASES[CASE]
    main_path.write_bytes(source)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': b64(source)})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        try:
            if adapter is not None:
                adapter.close()
        finally:
            if frontend is not None:
                frontend.close()
    body, count = prepare(checked['fixture'], main_path, directory)
    fixture = directory / 'protocol.watsup'
    fixture.write_text(body)
    modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    result = subprocess.run([str(ROOT / '_build/default/tests/semantics/numeric_runner.exe'),
                             *modules, str(fixture)], cwd=ROOT, capture_output=True, timeout=300)
    (directory / 'numeric.stdout').write_bytes(result.stdout)
    (directory / 'numeric.stderr').write_bytes(result.stderr)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    print('CHDIR warning continuation:', count, 'checks passed', directory)


if __name__ == '__main__':
    main()
