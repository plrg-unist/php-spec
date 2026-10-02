#!/usr/bin/env python3
"""Source-derived chdir provider pauses, mutation ordering and forged facts."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('success', b"<?php echo chdir('__SUB__')?'T':'F'; echo include 'one.php';", b'__SUB__', True, False),
    ('failure', b"<?php echo chdir('missing')?'T':'F'; echo include 'one.php';", b'missing', False, False),
    ('function', b"<?php function f(){return chdir('__SUB__');} f(); echo include 'one.php';", b'__SUB__', True, True),
    ('stringable', b"<?php class O { function __toString(): string { return '__SUB__'; } } chdir(new O); echo include 'one.php';", b'__SUB__', True, False),
    ('stringable-dynamic', b"<?php class O { function __toString(): string { return '__SUB__'; } } $f='chdir'; $f(new O); echo include 'one.php';", b'__SUB__', True, False),
    ('stringable-named-dynamic', b"<?php class O { function __toString():string { return '__SUB__'; } } $f='chdir'; $f(directory:new O); echo include 'one.php';", b'__SUB__', True, False),
    ('stringable-named-invoke', b"<?php class O { function __toString():string { return '__SUB__'; } } $f=chdir(...); $f->__invoke(directory:new O); echo include 'one.php';", b'__SUB__', True, False),
]


def b64(data):
    return base64.b64encode(data).decode()


def seq(data):
    return '(' + str(list(data)) + ')'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree


def main():
    out = Path(tempfile.mkdtemp(prefix='include-chdir-protocol-', dir=ROOT / '.tools'))
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
    cwd = os.fsencode(ROOT.resolve())
    for name, template, requested_template, succeeds, saved in CASES:
        directory = out / name
        directory.mkdir()
        sub = directory / 'sub'
        sub.mkdir()
        requested = os.fsencode(sub.resolve()) if requested_template == b'__SUB__' else requested_template
        source = template.replace(b'__SUB__', requested)
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
        start = '$php_file_run(' + checked['fixture'] + ', 300, $base64(' + json.dumps(b64(os.fsencode(source_path.resolve()))) + '), $base64(' + json.dumps(b64(cwd)) + '))'
        response = ('DIR_CHANGED 0 ' + seq(cwd) + ' ' + seq(requested) + ' ' + seq(requested)
                    if succeeds else 'DIR_FAILED 0 ' + seq(cwd) + ' ' + seq(requested)
                    + ' ' + seq(b'No such file or directory') + ' 2')
        checks = [
            'S_initial = ' + start,
            'S_initial.COMPLETION = SOURCE_PENDING',
            'S_initial.DIRCONTEXT = (pdircontext)',
            'S_initial.TODO = (CHDIR_AWAIT pconfigcall 0) :: ptask_tail*',
            'pdircontext.CALL = pconfigcall',
            'pdircontext.REQUESTED = ' + seq(requested),
            'pdircontext.CWD = ' + seq(cwd),
            'pdircontext.FRAMEOWNER = ' + ('1' if saved else '0'),
            'S_initial.DIRSEQ = 1',
            'S_initial.FILESEQ = 0',
            '$dir_pending_state_valid(S_initial)',
            '$call_descriptors_valid(S_initial)',
            '~$call_descriptors_valid(S_initial[.DIRSEQ = 2])',
            '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.REQUESTED = ' + seq(b'forged') + '])])',
            '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.FRAMEOWNER = 999])])',
            '~$call_descriptors_valid(S_initial[.TODO = (CHDIR_AWAIT pconfigcall 0) :: S_initial.TODO])',
            '~$call_descriptors_valid(S_initial[.TODO = (FILE_RESOLVE_AWAIT 0) :: S_initial.TODO])',
            '~$call_descriptors_valid(S_initial[.TODO = (EVAL_AWAIT 1) :: S_initial.TODO])',
            '$dir_response_valid(S_initial, ' + response + ')',
            '~$dir_response_valid(S_initial, DIR_CHANGED 1 ' + seq(cwd) + ' ' + seq(requested) + ' ' + seq(requested) + ')',
            '~$dir_response_valid(S_initial, DIR_CHANGED 0 ' + seq(cwd) + ' ' + seq(requested) + ' ' + seq(b'relative') + ')',
            'S_invalid = $dir_resume(S_initial, DIR_CHANGED 1 ' + seq(cwd) + ' ' + seq(requested) + ' ' + seq(requested) + ')',
            'S_invalid.COMPLETION = UNSUPPORTED text_invalid',
            'S_invalid.FILECWD = S_initial.FILECWD',
            'S_after = $dir_continue(S_initial, ' + response + ')',
            'S_after.COMPLETION = SOURCE_PENDING',
            'S_after.DIRCONTEXT = eps',
            'S_after.FILECWD = (' + seq(requested if succeeds else cwd) + ')',
            'S_after.FILEINCLUDEPATH = S_initial.FILEINCLUDEPATH',
            'S_after.FILESEQ = 1',
            'S_after.DIRSEQ = 1',
            'S_after.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
            'pfilecontext.PHASE = FILE_RESOLVE_WAIT',
            'pfilecontext.CWD = ' + seq(requested if succeeds else cwd),
            '$call_descriptors_valid(S_after)',
        ]
        if saved:
            checks += [
                'S_initial.FRAMES = pframe :: pframe_tail*',
                '~$call_descriptors_valid(S_initial[.FRAMES = pframe[.TODO = (CHDIR_AWAIT pconfigcall 0) :: pframe.TODO] :: pframe_tail*])',
            ]
        if name.startswith('stringable'):
            checks += [
                'S_initial.DIRCONVSEQ = 1',
                'S_initial.DIRCONVERSIONS = [pdirconversion]',
                'pdircontext.CONVERSION = (0)',
                'pdirconversion.NONCE = 0',
                'pdirconversion.RESULT = ' + seq(requested),
                'pdirconversion.CALLSITE = pconfigcall.SITE',
                'pdirconversion.CALLLINE = pconfigcall.LINE',
                'pdirconversion.SELECTION = pconfigcall.SELECTION',
                '~$dir_requested_valid(S_initial[.OBJECTS = $object_set(S_initial.OBJECTS,pdirconversion.OBJECT,STDINSTANCE)],pdircontext)',
                '~$call_descriptors_valid(S_initial[.DIRCONVSEQ = 2])',
                '~$call_descriptors_valid(S_initial[.DIRCONVERSIONS = eps])',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.CONVERSION = eps])])',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.REQUESTED = ' + seq(b'forged') + '])])',
            ]
        if name in ('stringable-dynamic', 'stringable-named-dynamic'):
            checks += [
                'pconfigcall.SELECTION = (n_selection)',
                'S_initial.SELECTEDCALLS[n_selection] = pselectedcall',
                '$selected_entry_active_valid(S_initial,pselectedcall)',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.SELECTION = eps]])])',
            ]
        if name.startswith('stringable-named'):
            checks += [
                'pconfigcall.NAMED',
                'pconfigcall.INDEX = 1',
                'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
                'pdirconversion.OBJECT = n_object',
                '(HOBJECT n_object) <- $task_nodes(CHDIR_AWAIT pconfigcall 0)',
                '~$config_invoke_valid(S_initial,pconfigcall[.NAMED = false])',
                '~$dir_requested_valid(S_initial,pdircontext[.CALL = pconfigcall[.NAMED = false]])',
                '~$dir_requested_valid(S_initial,pdircontext[.CALL = pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT 999))]]])',
                '~$call_descriptors_valid(S_initial[.DIRCONVERSIONS = [pdirconversion[.OBJECT = 999]]])',
                '~$call_descriptors_valid(S_initial[.DIRCONVERSIONS = [pdirconversion[.OWNERDEPTH = 999]]])',
                '~$call_descriptors_valid(S_initial[.DIRCONVERSIONS = [pdirconversion[.NONCE = 999]]])',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.CONVERSION = (999)])])',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.INDEX = 0]])])',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.LINE = 999]])])',
                '~$call_descriptors_valid(S_initial[.ALLOCATIONS = eps])',
            ]
        if name == 'stringable-named-invoke':
            checks += [
                'pconfigcall.OWNER = (n_owner)',
                '(HOBJECT n_owner) <- $task_nodes(CHDIR_AWAIT pconfigcall 0)',
                '~$dir_requested_valid(S_initial,pdircontext[.CALL = pconfigcall[.OWNER = eps]])',
                '~$call_descriptors_valid(S_initial[.DIRCONTEXT = (pdircontext[.CALL = pconfigcall[.OWNER = (999)]])])',
            ]
        fixture = directory / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + line + '\n' for line in checks))
        process = subprocess.run([str(runner), *map(str, modules), str(fixture)],
                                 capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stdout[-1000:], process.stderr[-2000:])
        results.append({'case': name, 'assertions': len(checks), 'source_sha256': digest(source_path),
                        'fixture_sha256': digest(fixture)})
        print(name, len(checks), flush=True)
    after = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_after = vendor_identity()
    report = {'passed': True, 'cases': results, 'inputs': before,
              'vendor_tree': vendor_before,
              'input_changes': [key for key in before if before[key] != after[key]],
              'assertions': sum(row['assertions'] for row in results)}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    assert not report['input_changes']
    assert vendor_before == vendor_after


if __name__ == '__main__':
    main()
