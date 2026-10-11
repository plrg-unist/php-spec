#!/usr/bin/env python3
"""Reached file-compiler notice owners, identity completion and abrupt unwinds."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import static_types as types
from recorded_worker import Worker
import file_compile_notice_sources as source
from typed_static_invoke_set_protocol import process

ROOT = source.ROOT
seq = lambda data: '(' + str(list(data)) + ')'
byte_expr = lambda data: '$base64(' + json.dumps(source.b64(data)) + ')'

PREFIX = r'''dec $seek(pstate,nat) : pstate
def $seek(S,n) = S -- if $stage(S)
def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,n) = S -- otherwise
dec $one(pstate) : pstate
def $one(S) = S_next -- PhpStep: S ~> S_next
dec $forge_exit(pdeclaration*) : pdeclaration*
dec $forge_exit_item(pdeclaration) : pdeclaration
def $forge_exit(eps) = eps
def $forge_exit(pdeclaration :: pdeclaration_tail*) = $forge_exit_item(pdeclaration) :: $forge_exit(pdeclaration_tail*)
def $forge_exit_item(PDEXIT 1 PCSCOMPLETE) = PDEXIT 1 PCSREJECT
def $forge_exit_item(pdeclaration) = pdeclaration -- otherwise
'''

COMMON = [
    'S.FILECONTEXTS = [pfilecontext]', 'pfilecontext.UNIT = (1)',
    'pfilecontext.PHASE = FILE_UNIT_RUN', 'pfilecontext.OPENED = (preqbytes_opened)',
    '$call_descriptors_valid(S)', '$declaration_entry_check(S) = S',
    '$heap_valid($heap_graph(S))',
]
PENDING = [
    'S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail*',
    'pdeclnoticebatch.KIND = NOTICE_FILE 1', 'pdeclnoticebatch.INDEX = 0',
]
SAVED = [
    'S.CURRENT = (pcallcontext)', 'S.FRAMES = pframe :: eps',
    'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
    'perrorcall.RESUME = DECL_NOTICE_RESUME pdeclnoticebatch',
    'pdeclnoticebatch.KIND = NOTICE_FILE 1', 'pdeclnoticebatch.INDEX = 1',
]

STAGES = {
    'pending': ('include-return', PENDING, COMMON + [
        '~(preqbytes_opened <- S.INCLUDEDOPENED)', '$iterator_notice_file_flushing(S,pfilecontext)',
        '$file_notice_opened(S,S.FILECONTEXTS,pdeclnoticebatch) = (preqbytes_opened)',
        'S_missing = S[.TODO = ptask_tail*]', '~$call_descriptors_valid(S_missing)',
        '$call_entry_check(S_missing).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'pdeclnoticebatch_line = pdeclnoticebatch[.LINE = $(pdeclnoticebatch.LINE + 1)]',
        'S_line = S[.TODO = (DECL_NOTICES pdeclnoticebatch_line) :: ptask_tail*]',
        '~$call_descriptors_valid(S_line)', '$file_notice_opened(S_line,S_line.FILECONTEXTS,pdeclnoticebatch_line) = eps',
        'pdeclnoticebatch_site = pdeclnoticebatch[.SITE = PORIGIN 1 eps]',
        'S_site = S[.TODO = (DECL_NOTICES pdeclnoticebatch_site) :: ptask_tail*]',
        '~$call_descriptors_valid(S_site)', '$file_notice_opened(S_site,S_site.FILECONTEXTS,pdeclnoticebatch_site) = eps',
        'pdeclnoticebatch_unit = pdeclnoticebatch[.KIND = NOTICE_FILE 99]',
        'S_unit = S[.TODO = (DECL_NOTICES pdeclnoticebatch_unit) :: ptask_tail*]',
        '~$call_descriptors_valid(S_unit)', '$file_notice_opened(S_unit,S_unit.FILECONTEXTS,pdeclnoticebatch_unit) = eps',
        'S_opened = S[.FILECONTEXTS = [pfilecontext[.OPENED = ($ptascii("/forged.php"))]]]',
        '~$call_descriptors_valid(S_opened)', '$file_notice_opened(S_opened,S_opened.FILECONTEXTS,pdeclnoticebatch) = eps',
        'S_owner = S[.FILECONTEXTS = [pfilecontext[.OWNER = 1]]]',
        '~$call_descriptors_valid(S_owner)', '$file_notice_opened(S_owner,S_owner.FILECONTEXTS,pdeclnoticebatch) = eps',
        'S_duplicate = S[.TODO = (DECL_NOTICES pdeclnoticebatch) :: S.TODO]',
        '~$call_descriptors_valid(S_duplicate)',
        'pdeclnoticebatch_items = pdeclnoticebatch[.NOTICES = eps]',
        'S_items = S[.TODO = (DECL_NOTICES pdeclnoticebatch_items) :: ptask_tail*]',
        '~$call_descriptors_valid(S_items)', '$file_notice_opened(S_items,S_items.FILECONTEXTS,pdeclnoticebatch_items) = eps',
        'S_history = S[.DECLARATIONS = $forge_exit(S.DECLARATIONS)]',
        'S_history.DECLARATIONS =/= S.DECLARATIONS',
        '$declaration_entry_check(S_history).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
        '$file_notice_opened(S_history,S_history.FILECONTEXTS,pdeclnoticebatch) = eps',
    ]),
    'once-pending': ('require_once-throw', PENDING, COMMON + [
        'preqbytes_opened <- S.INCLUDEDOPENED', '$file_once_kind(pfilecontext.KIND)',
        'S.INCLUDEDOPENED = [preqbytes_main,preqbytes_opened]',
        '~$call_descriptors_valid(S[.INCLUDEDOPENED = [preqbytes_main]])',
        'S_idempotent = $file_notice_complete(S,pdeclnoticebatch)',
        'S_idempotent.INCLUDEDOPENED = S.INCLUDEDOPENED',
    ]),
    'saved-handler': ('include-return', SAVED, COMMON + [
        '~(preqbytes_opened <- S.INCLUDEDOPENED)', '$iterator_notice_file_flushing(S,pfilecontext)',
        'pfilecontext.OWNER = 0', 'pcallcontext.ARGC = 4',
        'S_scope = $constant_frame_scope(S,pframe,eps)',
        '$file_notice_opened(S_scope,S_scope.FILECONTEXTS,pdeclnoticebatch) = (preqbytes_opened)',
        '$file_notice_opened(S,S.FILECONTEXTS,pdeclnoticebatch) = eps',
        'S_missing = S[.FRAMES = [pframe[.TODO = ptask_saved*]]]', '~$call_descriptors_valid(S_missing)',
        'S_borrowed = S[.TODO = (DECL_NOTICE_RESUME pdeclnoticebatch) :: S.TODO]',
        '~$call_descriptors_valid(S_borrowed)',
    ]),
    'done': ('include-return', [
        'S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail*',
        'pdeclnoticebatch.KIND = NOTICE_FILE 1', 'pdeclnoticebatch.INDEX = |pdeclnoticebatch.NOTICES|',
    ], COMMON + [
        '~(preqbytes_opened <- S.INCLUDEDOPENED)', 'S_next = $one(S)',
        'S_next.TODO = ptask_tail*', 'S_next.INCLUDEDOPENED = S.INCLUDEDOPENED ++ [preqbytes_opened]',
        '~$iterator_notice_file_flushing(S_next,pfilecontext)', '$call_descriptors_valid(S_next)',
        '$declaration_entry_check(S_next) = S_next',
        '~$call_descriptors_valid(S_next[.INCLUDEDOPENED = S.INCLUDEDOPENED])',
        '$file_notice_complete(S_next,pdeclnoticebatch).INCLUDEDOPENED = S_next.INCLUDEDOPENED',
    ]),
    'throw': ('include-throw-repeated', [
        'S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DECL_NOTICE_RESUME pdeclnoticebatch', 'pdeclnoticebatch.KIND = NOTICE_FILE 1',
    ], COMMON + [
        '~(preqbytes_opened <- S.INCLUDEDOPENED)', 'pdeclnoticebatch.INDEX = 1',
        '|pdeclnoticebatch.NOTICES| = 3', 'S_next = $one(S)',
        'S_next.TODO = (THROW_SEARCH n) :: ptask_tail*',
        'S_next.INCLUDEDOPENED = S.INCLUDEDOPENED ++ [preqbytes_opened]',
        '~$iterator_notice_file_flushing(S_next,pfilecontext)',
        '|S_next.EVENTS| = $(|S.EVENTS| + 1)', '$call_descriptors_valid(S_next)',
        '$declaration_entry_check(S_next) = S_next',
    ]),
    'exit': ('include-exit-repeated', ['S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*', *SAVED], COMMON + [
        '~(preqbytes_opened <- S.INCLUDEDOPENED)', 'S_exit = $one(S)', 'S_exit.COMPLETION = EXITED 7',
        '$declaration_entry_check(S_exit) = S_exit',
        'S_unwind = $exit_start_unwind(S_exit,7)', 'S_unwind.TODO = [EXIT_UNWIND 7]',
        '$call_descriptors_valid(S_unwind)', '$declaration_entry_check(S_unwind) = S_unwind',
        '~(preqbytes_opened <- S_unwind.INCLUDEDOPENED)',
        'S_restored = $one(S_unwind)', 'S_restored.FRAMES = eps', 'S_restored.CURRENT = eps',
        'S_restored.INCLUDEDOPENED = S.INCLUDEDOPENED ++ [preqbytes_opened]',
        '|S_restored.EVENTS| = $(|S_exit.EVENTS| + 1)', 'S_restored.TODO = [EXIT_UNWIND 7]',
        '$call_descriptors_valid(S_restored)', '$declaration_entry_check(S_restored) = S_restored',
    ]),
    'fatal': ('include-fatal', ['S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*', *SAVED], COMMON + [
        '~(preqbytes_opened <- S.INCLUDEDOPENED)', 'S_fatal = $one(S)',
        'S_fatal.COMPLETION = USERFATAL $ptascii("stop") z true',
        '$declaration_entry_check(S_fatal) = S_fatal',
        'S_unwind = $start_error_unwind(S_fatal)', 'S_restored = $one(S_unwind)',
        'S_restored.FRAMES = eps', 'S_restored.CURRENT = eps',
        '~(preqbytes_opened <- S_restored.INCLUDEDOPENED)',
        'S_restored.FILEBINDINGS = S.FILEBINDINGS',
        'S_cleared = $one(S_restored)', 'S_cleared.FILECONTEXTS = eps',
        '~(preqbytes_opened <- S_cleared.INCLUDEDOPENED)', '$declaration_entry_check(S_cleared) = S_cleared',
    ]),
    'body': ('body-once', [], COMMON + [
        'preqbytes_opened <- S.INCLUDEDOPENED', '~$iterator_notice_file_flushing(S,pfilecontext)',
        'S.INCLUDEDOPENED = [preqbytes_main,preqbytes_opened]',
        '~$call_descriptors_valid(S[.INCLUDEDOPENED = [preqbytes_main]])',
    ]),
}


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        fixtures = {}
        for case in dict.fromkeys(STAGES[name][0] for name in names):
            directory = sources / case
            main = directory / 'main.php'
            child = directory / 'unit.php'
            row = source.cases()[case]
            assert main.read_bytes() == row[0].encode() and child.read_bytes() == row[1]
            native = directory / 'native'
            assert (native / 'stdout').read_bytes() == row[2].encode()
            assert json.loads((native / 'process.json').read_text())['exit_status'] == row[3]
            parsed = frontend.request({'op': 'parse', 'source': source.b64(main.read_bytes())})
            assert parsed['accepted'], parsed
            main_fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            parsed = frontend.request({'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
                'requested': source.b64(os.fsencode(child)), 'resolved': source.b64(os.fsencode(child)),
                'opened': source.b64(os.fsencode(child)), 'source': source.b64(child.read_bytes())})
            assert parsed['accepted'], parsed
            child_fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            fixtures[case] = (main_fixture, child_fixture)
        for name in names:
            case, stage, checks = STAGES[name]
            directory = sources / case
            main_path, child_path = directory / 'main.php', directory / 'unit.php'
            main_fixture, child_fixture = fixtures[case]
            setup = [
                'S_wait = $php_file_run(' + main_fixture + ',1200,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.FILECONTEXTS = [pfilecontext_wait]',
                'S_parse = $file_open_resume(S_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED (' + seq(os.fsencode(child_path)) + ') (' + seq(os.fsencode(child_path)) + ') ' + seq(child_path.read_bytes()) + ')',
                'S_parse.COMPLETION = SOURCE_PENDING',
                'S_ready = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + seq(child_path.read_bytes()) + ' ' + child_fixture + ')',
                'S_ready.COMPLETION = NORMAL', 'S_found = $seek(S_ready,400)',
                'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                'S = S_found[.COMPLETION = NORMAL]', *stage,
            ]
            assertions = setup + checks
            target = out / name
            target.mkdir()
            text = 'dec $stage(pstate) : bool\ndef $stage(S) = true\n' + ''.join('  -- if ' + item + '\n' for item in stage)
            text += 'def $stage(S) = false -- otherwise\n' + PREFIX
            text += '\ndec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + item + '\n' for item in assertions)
            for phase, entry in [('admission', 'true'), ('protocol', '$body()')]:
                (target / (phase + '.watsup')).write_text(text + '\ndec $main() : bool\ndef $main() = ' + entry + '\n')
            (target / 'assertions.json').write_text(json.dumps(assertions, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'admission', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    assert args.attempt > 0
    run_label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    names = args.stage or list(STAGES)
    assert names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    out, sources = args.output.resolve(), args.sources.resolve()
    before = source.inputs()
    for path in [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']:
        before[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL':'C','TZ':'UTC'},
        'records': [], 'result': 'fail', 'runtime_assertions': 0}
    print(out, flush=True)
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                directory = out / name
                fixture = directory / ('protocol.watsup' if args.phase == 'check' else 'admission.watsup')
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(fixture)],
                    directory / run_label, 90, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                count = len(json.loads((directory / 'assertions.json').read_text())) if args.phase == 'check' else 0
                report['records'].append({'id': name, 'pass': passed, 'runtime_assertions': count,
                    'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()})
                report['runtime_assertions'] += count if passed else 0
                print(name, passed, flush=True)
                if not passed:
                    return False
        report['result'] = 'pass'
    finally:
        report['stable_inputs'] = all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value for path,value in before.items())
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (run_label + '-report.json')).write_text(json.dumps(report,indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
