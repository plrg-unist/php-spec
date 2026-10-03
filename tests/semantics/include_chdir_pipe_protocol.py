#!/usr/bin/env python3
"""Source-derived CHDIR PIPE pauses with live post-callback CWD."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

from include_mutable_execution import CASES
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASE = 'pipe-config-chdir-dynamic-live-cwd'
PREFIX = '''dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''


def b64(data):
    return base64.b64encode(data).decode()


def seq(data):
    return '(' + str(list(data)) + ')'


def prepare(program, main, cwd):
    initial = seq(os.fsencode(cwd.resolve()))
    sub = seq(os.fsencode((cwd / 'sub').resolve()))
    start = ('$php_file_run(' + program + ',10000,$base64('
             + json.dumps(b64(os.fsencode(main.resolve()))) + '),$base64('
             + json.dumps(b64(os.fsencode(cwd.resolve()))) + '))')
    changed = 'DIR_CHANGED 1 ' + sub + ' ' + seq(b'..') + ' ' + initial
    failed = 'DIR_FAILED 1 ' + sub + ' ' + seq(b'..') + ' ' + seq(b'Permission denied') + ' 13'
    checks = [
        'S_inner = ' + start,
        'S_inner.COMPLETION = SOURCE_PENDING',
        '~S_inner.COMPILESTOP',
        'S_inner.DIRCONTEXT = (pdircontext_inner)',
        'pdircontext_inner.NONCE = 0',
        'pdircontext_inner.CWD = ' + initial,
        'pdircontext_inner.REQUESTED = $ptascii("sub")',
        'pdircontext_inner.FRAMEOWNER = 1',
        'pdircontext_inner.CONVERSION = eps',
        'S_inner.CURRENT = (pcallcontext)',
        'pcallcontext.ARGC = 0',
        'pcallcontext.PARAMS = eps',
        'S_inner.FRAMES = [pframe]',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
        '$config_string_site_valid(S_inner,pconfigcall,n_object,porigin_child,z_child,z_call)',
        '$config_string_trace_context(S_inner,pcallcontext)',
        '$call_descriptors_valid(S_inner)',
        '$outputs(S_inner.EVENTS) = $ptascii("RC0ZN")',
        'S = $dir_continue(S_inner,DIR_CHANGED 0 ' + initial + ' ' + seq(b'sub') + ' ' + sub + ')',
        'S.COMPLETION = SOURCE_PENDING',
        '~S.COMPILESTOP',
        'S.CURRENT = eps',
        'S.FRAMES = eps',
        'S.DIRCONTEXT = (pdircontext)',
        'S.TODO = (CHDIR_AWAIT pconfigcall 1) :: ptask_tail*',
        'pdircontext.CALL = pconfigcall',
        'pdircontext.NONCE = 1',
        'pdircontext.CWD = ' + sub,
        'pdircontext.REQUESTED = $ptascii("..")',
        'pdircontext.FRAMEOWNER = 0',
        'pdircontext.CONVERSION = (0)',
        'S.FILECWD = (' + sub + ')',
        'S.FILEINCLUDEPATH = (' + seq(b'.:\0tail') + ')',
        'S.DIRSEQ = 2',
        'S.FILESEQ = 0',
        'S.DIRCONVSEQ = 1',
        'S.DIRCONVERSIONS = [pdirconversion]',
        'pdirconversion.NONCE = 0',
        'pdirconversion.OBJECT = n_object',
        'pdirconversion.RESULT = $ptascii("..")',
        'pdirconversion.CALLSITE = pconfigcall.SITE',
        'pdirconversion.CALLLINE = z_call',
        'pdirconversion.OWNERDEPTH = 0',
        'pdirconversion.SELECTION = pconfigcall.SELECTION',
        'pconfigcall.KIND = INTRINSIC_CHDIR',
        'pconfigcall.OWNER = eps',
        'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection] = pselectedcall',
        '$selected_entry_active_valid(S,pselectedcall)',
        '~pconfigcall.NAMED',
        'pconfigcall.INDEX = 1',
        'pconfigcall.PACKS = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
        'pconfigcall.SITE = PORIGIN n_unit pcpath',
        'porigin_child = PORIGIN n_unit (pcpath ++ [PCFIELD 0])',
        'z_child = $pipe_send_line(S,pconfigcall.SITE)',
        'z_child =/= z_call',
        '$pipe_lines_valid(S,pconfigcall.SITE,z_child,z_call)',
        '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
        '$config_string_site_valid(S,pconfigcall,n_object,porigin_child,z_child,z_call)',
        '$lookup(S.ENV,$ptascii("left")) = (n_left)',
        'S.STORE[n_left] = DEFINED PNULL',
        '(HOBJECT n_object) <- $task_nodes(CHDIR_AWAIT pconfigcall 1)',
        '$getclass_live_object(S,n_object)',
        '$dir_pending_state_valid(S)',
        '$call_descriptors_valid(S)',
        '~$dir_pending_state_valid(S[.FILECWD = (' + initial + ')])',
        '~$call_descriptors_valid(S[.DIRSEQ = 3])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.NONCE = 0])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.FRAMEOWNER = 1])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.TAIL = eps])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.REQUESTED = $ptascii("forged")])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CONVERSION = eps])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.KIND = INTRINSIC_INI_RESTORE]])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.SELECTION = eps]])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.OWNER = (n_object)]])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.SITE = porigin_child]])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.LINE = 999]])])',
        '~$call_descriptors_valid(S[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.SENT = eps]])])',
        '~$call_descriptors_valid(S[.DIRCONVERSIONS = [pdirconversion[.RESULT = $ptascii("forged")]]])',
        '~$call_descriptors_valid(S[.DIRCONVERSIONS = [pdirconversion[.OWNERDEPTH = 1]]])',
        '~$call_descriptors_valid(S[.DIRCONVERSIONS = [pdirconversion[.CALLLINE = 999]]])',
        '~$call_descriptors_valid(S[.DIRCONVERSIONS = eps])',
        '~$call_descriptors_valid(S[.TODO = (CHDIR_AWAIT pconfigcall 1) :: S.TODO])',
        '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HOBJECT n_object)])',
        '~$dir_requested_valid(S[.OBJECTS = $object_set(S.OBJECTS,n_object,STDINSTANCE)],pdircontext)',
        '~$config_string_site_valid(S,pconfigcall,n_object,pconfigcall.SITE,z_child,z_call)',
        '~$config_string_site_valid(S,pconfigcall,n_object,porigin_child,999,z_call)',
        '$dir_response_valid(S,' + changed + ')',
        '$dir_response_valid(S,' + failed + ')',
        '~$dir_response_valid(S,DIR_CHANGED 0 ' + sub + ' ' + seq(b'..') + ' ' + initial + ')',
        '~$dir_response_valid(S,DIR_CHANGED 1 ' + initial + ' ' + seq(b'..') + ' ' + initial + ')',
        '~$dir_response_valid(S,DIR_CHANGED 1 ' + sub + ' ' + seq(b'forged') + ' ' + initial + ')',
        '~$dir_response_valid(S,DIR_CHANGED 1 ' + sub + ' ' + seq(b'..') + ' ' + seq(b'relative') + ')',
        '~$dir_response_valid(S[.SERVICELEFT = eps],' + changed + ')',
        'S_invalid = $dir_resume(S,DIR_CHANGED 0 ' + sub + ' ' + seq(b'..') + ' ' + initial + ')',
        'S_invalid.COMPLETION = UNSUPPORTED text_reason',
        'S_invalid.FILECWD = S.FILECWD',
        'S_invalid.DIRCONTEXT = S.DIRCONTEXT',
        'S_invalid.TODO = S.TODO',
    ]
    for name, response, next_cwd, output in [('changed', changed, initial, b'RC0ZNT'),
                                             ('failed', failed, sub, b'RC0ZNF')]:
        state = 'S_' + name
        checks += [state + ' = $dir_continue(S,' + response + ')',
                   state + '.COMPLETION = SOURCE_PENDING', state + '.DIRCONTEXT = eps',
                   state + '.FILECWD = (' + next_cwd + ')',
                   state + '.FILEINCLUDEPATH = S.FILEINCLUDEPATH',
                   state + '.DIRSEQ = 2', state + '.FILESEQ = 1',
                   state + '.FILECONTEXTS = pfilecontext_' + name + ' :: pfilecontext_tail_' + name + '*',
                   'pfilecontext_' + name + '.PHASE = FILE_RESOLVE_WAIT',
                   'pfilecontext_' + name + '.CWD = ' + next_cwd,
                   '$outputs(' + state + '.EVENTS) = ' + seq(output),
                   '$call_descriptors_valid(' + state + ')']
    return (PREFIX + 'dec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + line + '\n' for line in checks), len(checks))


def main():
    directory = Path(tempfile.mkdtemp(prefix='include-chdir-pipe-', dir=ROOT / '.tools'))
    (directory / 'sub').mkdir()
    source = CASES[CASE]
    main_path = directory / 'main.php'
    main_path.write_bytes(source)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], directory / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source)})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        try:
            adapter.close()
        finally:
            frontend.close()
    body, assertions = prepare(checked['fixture'], main_path, directory)
    fixture = directory / 'protocol.watsup'
    fixture.write_text(body)
    modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)]
    (directory / 'command.json').write_text(json.dumps(command) + '\n')
    with (directory / 'stdout').open('xb') as out, (directory / 'stderr').open('xb') as err:
        result = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err, timeout=300)
    assert result.returncode == 0 and (directory / 'stdout').read_bytes() == b'true\n' and not (directory / 'stderr').read_bytes()
    print(directory, assertions, 'PASS')


if __name__ == '__main__':
    main()
