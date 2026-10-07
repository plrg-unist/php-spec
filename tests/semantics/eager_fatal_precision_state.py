#!/usr/bin/env python3
"""Captured fatal cursor before a genuine compiler precision image refresh."""
import argparse
import json
from pathlib import Path

import shutdown_state_review as runner

SOURCE = next(row['source'] for row in json.loads(
    Path(__file__).with_name('eager_fatal_review_cases.json').read_text())
    if row['id'] == 'compiler-fatal-retains-old-plan-after-method-precision-warning')

runner.CASES = {
    'fatal-cursor-keeps-pre-resume-precision-plan': {
        'source': SOURCE,
        'eval': "$unused=(12.3456789+0).'L';class Bad extends Exception{protected function __wakeup(){}public function later(){return (12.3456789+0).'L';}}",
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
            'pdestructioncleanup.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
            'pdestructionfatal.COMPILESTOP',
            'pdestructionfatal.FRAME.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
            'S_history = $eager_fatal_history(S, pdestructionfatal)',
            '$source_unit(S.SOURCES, pevalcompile.PLAN.UNIT) = (pcunit)',
            'P_old = $declaration_compiler_state($eval_source_ppstate(S_history, pcunit))',
            'P_live = $declaration_compiler_state($eval_source_ppstate(S, pcunit))',
            'pevalcompile.PLAN = $eval_compile_plan(P_old)',
            'pevalcompile.PLAN = $eval_compile_plan(P_live)',
            'P_old.INSTALLED =/= P_live.INSTALLED',
            'P_old.EXPRESSIONS =/= P_live.EXPRESSIONS',
            '$compilation_image_valid(S, pcunit, P_live)',
            '~$compilation_image_valid(S, pcunit, P_old)',
            '$eager_cleanup_valid(S, pdestructioncleanup)',
            '$call_descriptors_valid(S)', '$destruction_state_valid(S)',
            'pdestructionfatal.FRAME.CONTEXT = (pcallcontext)',
            'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$throwable_previous_id(S, n_receiver) = (n_previous)',
            '$heap_owners($heap_graph(S), HOBJECT n_previous) = 1',
            'pevalcompile_plan = pevalcompile[.PLAN.COMPLETION = PPCABRUPT pdestructionfatal.COMPLETION]',
            '~$eager_fatal_cursor_plans_valid(S_history, [pevalcompile_plan])',
            'pdestructionfatal_plan = pdestructionfatal[.FRAME.TODO = (EVAL_COMPILE_RESUME pevalcompile_plan) :: ptask_tail*]',
            'pdestructioncleanup_plan = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_plan]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_plan]], pdestructioncleanup_plan)',
            '$eager_fatal_resume_prefix(pdestructionfatal.DECLARATIONS, pevalcompile.PLAN.UNIT) = (pdeclaration_prefix*)',
            'n_resume = |pdeclaration_prefix*|',
            'pdestructionfatal.DECLARATIONS[n_resume] = PDEVALRESUMEPRECISION pevalcompile.PLAN.UNIT z_reporting 1',
            'n_tail_start = $(n_resume + 1)',
            'n_tail_count = $nabs($(|pdestructionfatal.DECLARATIONS| - n_tail_start))',
            'pdeclaration_tail* = pdestructionfatal.DECLARATIONS[n_tail_start:n_tail_count]',
            'pdestructionfatal_epoch = pdestructionfatal[.DECLARATIONS = pdeclaration_prefix* ++ [PDEVALRESUMEPRECISION pevalcompile.PLAN.UNIT z_reporting 2] ++ pdeclaration_tail*]',
            'pdestructioncleanup_epoch = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_epoch]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_epoch]], pdestructioncleanup_epoch)',
            '$callable_at(S.CALLABLES, $ptascii("after_fatal")) = eps',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.DESTRUCTION = S.DESTRUCTION',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = S.SHUTDOWN.COMPLETION',
            'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S_done.DESTRUCTION.ABANDONED = S.DESTRUCTION.ABANDONED',
            '$callable_at(S_done.CALLABLES, $ptascii("after_fatal")) =/= eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S_done), HOBJECT n_previous) = 1',
            '$destruction_state_valid(S_done)',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("S:"), OUTPUT $ptascii("1"), OUTPUT $ptascii(";"), OUTPUT $ptascii("D:"), OUTPUT $ptascii("a"), OUTPUT $ptascii(";"), OUTPUT $ptascii("D:"), OUTPUT $ptascii("b"), OUTPUT $ptascii(";")]',
        ],
    },
}

# One logical checkpoint, split at the same fixed cap. Authentication covers the
# captured state; publication repeats only its required record/owner bindings.
# Final admission reaches DONE directly, avoiding another partial drive. Every
# original premise is retained across the bounded groups.
fixture = runner.CASES.pop('fatal-cursor-keeps-pre-resume-precision-plan')
checks = fixture['checks']
runner.CASES = {
    'fatal-precision-cursor-authentication': {
        **fixture, 'checks': checks[:38],
    },
    'fatal-precision-budget-input': {
        **fixture, 'checks': checks[38:42] + [checks[50]],
    },
    'fatal-precision-publication-events': {
        **fixture, 'checks': checks[42:47] + [checks[51]],
    },
    'fatal-precision-completed-source-owners': {
        **fixture,
        'stage': 'S.DESTRUCTION.PHASE = DESTRUCTION_DONE -- if S.COMPLETION = NORMAL',
        'checks': checks[2:4] + checks[19:21] + [checks[22]] + [
            'S_done = S[.COMPLETION = S.SHUTDOWN.COMPLETION]',
            checks[47], checks[48]],
    },
    'fatal-precision-completed-source-admission': {
        **fixture,
        'stage': 'S.DESTRUCTION.PHASE = DESTRUCTION_DONE -- if S.COMPLETION = NORMAL',
        'checks': ['S_done = S[.COMPLETION = S.SHUTDOWN.COMPLETION]',
                   '$destruction_state_valid(S_done)'],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=runner.CASES)
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
