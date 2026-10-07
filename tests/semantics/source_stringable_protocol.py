#!/usr/bin/env python3
"""Reached Stringable pending source authority, independently reviewed37.

The original15-line observer fixture is driven only through eval at line12;
its ordinary-library observer on line13 is never reached. Prepare-only checks
frontend/adapter and writes the exact fixture without a model application.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HELPERS = '\ndec $string_pending_review_reached(pstate) : bool\ndef $string_pending_review_reached(S) = true\n  -- if S.TODO = (SOURCE_STRING_PENDING psourceoperand n_text* n) :: ptask_tail*\n  -- if psourceoperand.KIND = 0\n  -- if psourceoperand.LINE = 12\ndef $string_pending_review_reached(S) = false -- otherwise\ndec $string_pending_review_seek(pstate, nat) : pstate\ndef $string_pending_review_seek(S, n) = S -- if $string_pending_review_reached(S)\ndef $string_pending_review_seek(S, n) = S\n  -- if ~$string_pending_review_reached(S)\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $string_pending_review_seek(S, 0) = S -- if ~$string_pending_review_reached(S)\ndef $string_pending_review_seek(S, n) = $string_pending_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))\n  -- if ~$string_pending_review_reached(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\n'
PREMISES = '  -- if S_reached = $string_pending_review_seek(S_initial, 2500)\n  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET\n  -- if S = S_reached[.COMPLETION = NORMAL]\n  -- if S.TODO = (SOURCE_STRING_PENDING psourceoperand n_text* n) :: ptask_tail*\n  -- if psourceoperand.KIND = 0\n  -- if psourceoperand.LINE = 12\n  -- if psourceoperand.INPUT = VARIABLE n_name* z\n  -- if psourceoperand.OWNER = 0\n  -- if psourceoperand.TAIL = ptask_tail*\n  -- if n_text* = $ptascii("function borrowedThrowCompiled(int $value = null) {} echo \\"BODY|\\"; return 77;")\n  -- if S_request = $drive_steps(S, 1)\n  -- if S_request.COMPLETION = SOURCE_PENDING\n  -- if S_request.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*\n  -- if S_request.TODO = (EVAL_AWAIT pevalcontext.UNIT) :: pevalcontext.TAIL\n  -- if pevalcontext.TAIL = (SOURCE_STRING_PROPAGATE psourceoperand n_text* n) :: ptask_tail*\n  -- if n_outside = |S_request.OBJECTS|\n  -- if $source_string_pending_valid(S, psourceoperand, n_text*, n)\n  -- if $call_task_valid(S, SOURCE_STRING_PENDING psourceoperand n_text* n)\n  -- if $call_descriptors_valid(S)\n  -- if $call_entry_check(S) = S\n  -- if $heap_valid($heap_graph(S))\n  -- if $task_nodes(SOURCE_STRING_PENDING psourceoperand n_text* n) = [HOBJECT n]\n  -- if $task_nodes(SOURCE_STRING_PROPAGATE psourceoperand n_text* n) = [HOBJECT n]\n  -- if $source_eval_pending_marker(pevalcontext)\n  -- if $source_eval_pending_context(S_request, pevalcontext)\n  -- if $source_compile_initial_pending(S_request, pevalcontext.UNIT) = THROWING n\n  -- if $call_descriptors_valid(S_request)\n  -- if $heap_valid($heap_graph(S_request))\n  -- if ~$source_eval_pending_context(S_request, pevalcontext[.BYTES = n_text* ++ [32]])\n  -- if ~$source_eval_pending_context(S_request, pevalcontext[.SITE = $source_operand_child(psourceoperand)])\n  -- if ~$source_eval_pending_context(S_request, pevalcontext[.OWNER = $(pevalcontext.OWNER + 1)])\n  -- if ~$source_eval_pending_context(S_request, pevalcontext[.TAIL = (SOURCE_STRING_PROPAGATE psourceoperand[.KIND = 1] n_text* n) :: ptask_tail*])\n  -- if ~$source_eval_pending_context(S_request, pevalcontext[.TAIL = (SOURCE_STRING_PROPAGATE psourceoperand n_text* n) :: [DISCARD] ++ ptask_tail*])\n  -- if ~$source_eval_pending_context(S_request, pevalcontext[.TAIL = (SOURCE_STRING_PROPAGATE psourceoperand n_text* n_outside) :: ptask_tail*])\n  -- if ~$source_eval_pending_context(S_request[.TODO = [EVAL_AWAIT pevalcontext.UNIT]], pevalcontext)\n  -- if ~$source_eval_pending_context(S_request[.TODO = (EVAL_AWAIT pevalcontext.UNIT) :: (SOURCE_STRING_PROPAGATE psourceoperand n_text* n) :: [DISCARD] ++ ptask_tail* ++ [(SOURCE_STRING_PROPAGATE psourceoperand n_text* n)] ++ ptask_tail*], pevalcontext)\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--semantic-root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    semantic = args.semantic_root.resolve()
    sys.path.insert(0, str(ROOT / 'tests/semantics'))
    import error_handler_run as recorder
    from recorded_worker import Worker
    recorder.ROOT = ROOT
    source = ROOT / 'tests/semantics/source-stringable/borrowed-throw-observer.php'
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = dict(json.loads(profile_file.read_bytes()), include_path='.:', error_reporting='30719')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    php = ROOT / '.tools/php/bin/php'
    bridge = ROOT / '.tools/php-file.so'
    worker = ROOT / 'frontend/worker.php'
    adapter = ROOT / '_build/default/adapter/main.exe'
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    watched = [source, Path(__file__), profile_file, php, bridge, worker,
               ROOT / 'frontend/target.php', ROOT / 'spec/schema.json', adapter,
               ROOT / 'tests/semantics/recorded_worker.py',
               ROOT / 'tests/semantics/error_handler_run.py']
    modules = []
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    if not args.prepare_only:
        manifest = semantic / 'spec/semantics/modules.json'
        modules = [semantic / name for name in json.loads(manifest.read_bytes())]
        assert any(path.name == '298-source-stringable-lifetime.watsup' for path in modules)
        watched += [manifest, *modules, runner]
    snapshot = lambda: {str(p): sha(p) for p in watched}
    before = snapshot()
    def git(*parts):
        result = subprocess.run(['git', *parts], cwd=ROOT, env=recorder.ENV,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip() if result.returncode == 0 else None
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    out = Path(tempfile.mkdtemp(prefix='source-stringable-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'working_tree_status': status, 'inputs': before,
              'profile': profile, 'source': str(source), 'mode': 'SL', 'cache': False, 'det': True,
              'compiler_pin': 'da36ac3c434cd291940293a63da64544307730a3',
              'selected': 'actual post-cast pending task and next parser-await at eval line12',
              'binding_premises': 17, 'selected_admission_premises': 37,
              'semantic_root': str(semantic), 'source_agreements': 0, 'application_evaluations': 0, 'passed': False,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
        finally:
            frontend.close()
        checked_worker = Worker([str(adapter), str(ROOT)], out / 'adapter')
        try:
            checked = checked_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
        finally:
            checked_worker.close()
        (out / 'checked.json').write_text(json.dumps(checked) + '\n')
        start = '$php_startup_run($string_pending_review_program(), 0, ' + json.dumps(base64.b64encode(bytes(source)).decode()) + ', {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})'
        fixture = 'dec $string_pending_review_program() : program\ndef $string_pending_review_program() = ' + checked['fixture'] + '\n' + HELPERS
        fixture += '\ndec $main() : bool\ndef $main() = true\n  -- if S_initial = ' + start + '\n' + PREMISES + 'def $main() = false -- otherwise\n'
        (out / 'admission.watsup').write_text(fixture)
        report.update(frontend_accepted=True, adapter_ok=True, generated_fixture=str(out / 'admission.watsup'))
        if args.prepare_only:
            report['passed'] = True
        else:
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(out / 'admission.watsup')], out / 'admission', 90)
            stdout = (out / 'admission.stdout').read_bytes()
            stderr = (out / 'admission.stderr').read_bytes()
            report.update(process=process, observed=stdout.decode(errors='replace'), stderr=stderr.decode(errors='replace'), application_evaluations=1)
            report['passed'] = (process['exit'] == 0 and not process['timeout'] and not stderr
                                and not process['group_after'] and stdout == b'true\n')
    finally:
        report['inputs_stable'] = before == snapshot()
        report['head_stable'] = revision == git('rev-parse', 'HEAD')
        report['status_stable'] = status == git('status', '--short')
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report.get(k) for k in ('passed', 'application_evaluations', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert all(report[k] for k in ('passed', 'inputs_stable', 'head_stable', 'status_stable'))

if __name__ == '__main__':
    main()
