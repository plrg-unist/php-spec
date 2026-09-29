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


def main():
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
              ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/recorded_worker.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = vendor_identity()
    results = []
    modules_args = [str(path) for path in modules]
    for name, source, stage, checks in CASES:
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
