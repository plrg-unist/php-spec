#!/usr/bin/env python3
"""Focused independent VM-owner and compiler-proof checks after fatal bailout."""
import argparse

import shutdown_state_review as runner

COMMON = [
    'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
    'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = eps',
    'S.CONSTCONTEXT = eps', 'S.COMPLETION = NORMAL',
    'S.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
    'S.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
    'pdestructioncleanup.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
    '~pdestructioncleanup.RELEASED',
    'pdestructionfatal.FRAME.CONTEXT = (pcallcontext)',
    'pdestructionfatal.FRAME.LOCALS = (psymboltable)',
    'pdestructioncleanup.CALLER = (pcallcontext)',
    'pdestructioncleanup.ORIGIN = pdestructionfatal.FRAME.ORIGIN',
    'pdestructioncleanup.CONSTCONTEXT = pdestructionfatal.FRAME.CONSTCONTEXT',
    'S.DESTRUCTION.CALLS = eps', 'S.DESTRUCTION.RELEASES = eps',
    'S.DESTRUCTION.FRAMES = eps', 'S.DESTRUCTION.OPERATIONS = eps',
    'S.DESTRUCTION.CLEANUPS = eps',
    '$eager_cleanup_valid(S, pdestructioncleanup)',
    '$heap_subset($eager_fatal_nodes(pdestructionfatal), S.ALLOCATIONS)',
    '$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
    '$call_descriptors_valid(S)', '$class_state_valid(S)',
    '$destruction_state_valid(S)', '$heap_valid($heap_graph(S))',
    '~$call_task_valid(S, DESTRUCTOR_FATAL pdestructionfatal)',
    '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = eps], pdestructioncleanup)',
    'pdestructionfatal_bad = pdestructionfatal[.FRAME.LOCALS = eps]',
    'pdestructioncleanup_bad = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_bad]',
    '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_bad]], pdestructioncleanup_bad)',
    'pdestructionfatal_rows = pdestructionfatal[.HANDLERS = pdestructionfatal.HANDLERS ++ [{VALUE PNULL, ARRAY eps, CELLS eps}]]',
    'pdestructioncleanup_rows = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_rows]',
    '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_rows]], pdestructioncleanup_rows)',
    'n_array_limit = |S.ARRAYS|',
    'pdestructionfatal_bounds = pdestructionfatal[.HANDLERS = [{VALUE PARRAY n_array_limit, ARRAY ($array_empty()), CELLS eps}]]',
    'pdestructioncleanup_bounds = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_bounds]',
    '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_bounds]], pdestructioncleanup_bounds)',
]


def finish(completion):
    return [
        'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
        'S_paused.DESTRUCTION = S.DESTRUCTION',
        'S_paused.ALLOCATIONS = S.ALLOCATIONS',
        'S_done = $drive(S, 2000)', 'S_done.COMPLETION = ' + completion,
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.HELD = eps', 'S_done.CONSTCONTEXT = eps',
        'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
        'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
        'S_done.DESTRUCTION.ABANDONED = S.DESTRUCTION.ABANDONED',
        '$destruction_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive(S_paused[.COMPLETION = NORMAL], 2000) = S_done',
    ]


CASES = {
    'fatal-helper-retains-local-cells-before-cleanup': {
        'source': '<?php class P{function __destruct(){echo "P;";}}class D{public $id;function __construct($id){$this->id=$id;}function __destruct(){echo "D:",$this->id,";";}}function fail_now(){$a=new P;$b=new P;trigger_error("fatal",E_USER_ERROR);}register_shutdown_function(static function(){echo "S;";$GLOBALS["born"]=[new D("a"),new D("b")];});echo "M;";eval("fail_now();");',
        'eval': 'fail_now();',
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            *COMMON,
            'pcallcontext.NAME = $ptascii("fail_now")',
            'pdestructionfatal.COMPLETION = USERFATAL $ptascii("fatal") 1 true',
            'pdestructionfatal.FROZEN = REQUESTFATAL $ptascii("Error") $ptascii("fatal") 1',
            'pdestructionfatal.SHUTDOWN.PHASE = SHUTDOWN_PENDING',
            '~pdestructionfatal.COMPILESTOP',
            '$eager_cleanup_valid(S[.REPORTING = 0], pdestructioncleanup)',
            'pdestructionfatal_mask = pdestructionfatal[.REPORTING = 0]',
            'pdestructioncleanup_mask = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_mask]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_mask]], pdestructioncleanup_mask)',
            'S_history = $eager_fatal_history(S, pdestructionfatal)',
            '$eval_state_valid(S_history)',
            'S_history.EVALCONTEXTS =/= eps',
            'pdestructionfatal.FRAMES = [pframe_original]',
            '(EVAL_END 1) <- pframe_original.TODO',
            '~$call_frames_valid(S_history[.EVALCONTEXTS = eps], S_history.FRAMES)',
            '$lookup(psymboltable.ENV, $ptascii("a")) = (n_cell_a)',
            '$lookup(psymboltable.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)',
            'n_a =/= n_b',
            '$heap_owners($heap_graph(S), HCELL n_cell_a) = 1',
            '$heap_owners($heap_graph(S), HCELL n_cell_b) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_a) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_b) = 1',
            'n_a <- S.DESTRUCTION.CALLED', 'n_b <- S.DESTRUCTION.CALLED',
            '~(S.DESTRUCTION.HANDLES[n_a] <- S.DESTRUCTION.FREE)',
            '~(S.DESTRUCTION.HANDLES[n_b] <- S.DESTRUCTION.FREE)',
            'pdestructionfatal_wrong = pdestructionfatal[.COMPLETION = USERFATAL $ptascii("changed") 1 true][.FROZEN = REQUESTFATAL $ptascii("Error") $ptascii("changed") 1]',
            'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_wrong]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_wrong]], pdestructioncleanup_wrong)',
            *finish('REQUESTFATAL $ptascii("Error") $ptascii("fatal") 1'),
            '$heap_owners($heap_graph(S_done), HCELL n_cell_a) = 1',
            '$heap_owners($heap_graph(S_done), HCELL n_cell_b) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_a) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_b) = 1',
            '~((OUTPUT $ptascii("P;")) <- S_done.EVENTS)',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("S;"), OUTPUT $ptascii("D:"), OUTPUT $ptascii("a"), OUTPUT $ptascii(";"), OUTPUT $ptascii("D:"), OUTPUT $ptascii("b"), OUTPUT $ptascii(";")]',
        ],
    },
    'serviced-compiler-fatal-binds-original-producer': {
        'source': '<?php class P extends Exception{function __destruct(){echo "P;";}}class E extends Exception{function __destruct(){echo "E;";eval("class Bad extends Exception{protected function __wakeup(){}}");}}class D{public $id;function __construct($id){$this->id=$id;}function __destruct(){echo "D:",$this->id,";";}}set_exception_handler(static function($e){echo "H;";unset($GLOBALS["p"]);});register_shutdown_function(static function(){echo "S;";if(true){function after_fatal(){}}after_fatal();$GLOBALS["born"]=[new D("a"),new D("b")];});$p=new P("previous");throw new E("original",0,$p);',
        'eval': 'class Bad extends Exception{protected function __wakeup(){}}',
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            *COMMON,
            'pdestructionfatal.FRAME.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*',
            'pevalcompile.CHECKPOINT = 0', 'pevalcompile.DIAGNOSTIC = 1',
            '|pevalcompile.PLAN.PUBLICATIONS| = 1',
            'pdestructionfatal_cp = pdestructionfatal[.FRAME.TODO = (EVAL_COMPILE_RESUME (pevalcompile[.CHECKPOINT = 1])) :: ptask_tail*]',
            'pdestructioncleanup_cp = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_cp]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_cp]], pdestructioncleanup_cp)',
            'pdestructionfatal_diag = pdestructionfatal[.FRAME.TODO = (EVAL_COMPILE_RESUME (pevalcompile[.DIAGNOSTIC = 0])) :: ptask_tail*]',
            'pdestructioncleanup_diag = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_diag]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_diag]], pdestructioncleanup_diag)',
            'pdestructionfatal_plan = pdestructionfatal[.FRAME.TODO = (EVAL_COMPILE_RESUME (pevalcompile[.PLAN.PUBLICATIONS = eps])) :: ptask_tail*]',
            'pdestructioncleanup_plan = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_plan]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_plan]], pdestructioncleanup_plan)',
            'pdestructionfatal.COMPILESTOP',
            'pdestructionfatal.COMPLETION = STATICBYTES $ptascii("Access level to Bad::__wakeup() must be public (as in class Exception)") 1',
            'pdestructionfatal.FROZEN = S.SHUTDOWN.COMPLETION',
            'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$throwable_previous_id(S, n_receiver) = (n_previous)',
            '$heap_owners($heap_graph(S), HOBJECT n_previous) = 1',
            'n_receiver <- S.DESTRUCTION.CALLED',
            'n_previous <- S.DESTRUCTION.CALLED',
            '$callable_at(S.CALLABLES, $ptascii("after_fatal")) = eps',
            'pdestructionfatal_wrong = pdestructionfatal[.COMPLETION = STATICBYTES $ptascii("changed") 9][.FROZEN = REQUESTFATAL $ptascii("CompileError") $ptascii("changed") 9]',
            'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_wrong]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_wrong]], pdestructioncleanup_wrong)',
            *finish('S.SHUTDOWN.COMPLETION'),
            '$callable_at(S_done.CALLABLES, $ptascii("after_fatal")) =/= eps',
            'n_last_declaration = $nabs($(|S_done.DECLARATIONS| - 1))',
            'S_done.DECLARATIONS[n_last_declaration] = PDRFUNCTION porigin_after pdeclcause_after',
            'pdeclcause_after.CALLS = [(porigin_callback, eps, eps, eps)]',
            '$declaration_cause_valid(S_done, porigin_after, pdeclcause_after)',
            '~$declaration_cause_valid(S_done, porigin_after, pdeclcause_after[.UNIT = 1])',
            '$class_named(S_done.CLASSNAMES, $ptascii("e")) = (porigin_class)',
            '~$declaration_cause_valid(S_done, porigin_after, pdeclcause_after[.CALLS = [(porigin_callback, eps, (porigin_class), eps)]])',
            '~$shutdown_declaration_scope(S_done, S_done.SHUTDOWN.ENTRIES, pcallcontext.FUNCTION, eps, eps)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S_done), HOBJECT n_previous) = 1',
            '~((OUTPUT $ptascii("P;")) <- S_done.EVENTS)',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("S;"), OUTPUT $ptascii("D:"), OUTPUT $ptascii("a"), OUTPUT $ptascii(";"), OUTPUT $ptascii("D:"), OUTPUT $ptascii("b"), OUTPUT $ptascii(";")]',
        ],
    },
}

# These groups prove one compiler checkpoint. Repeated setup earns no extra
# assertion credit; every original control, completion and replay check remains.
COMPILER_NAME = 'serviced-compiler-fatal-binds-original-producer'
compiler = CASES.pop(COMPILER_NAME)
checks = compiler['checks']
finish_start = checks.index('S_paused = $drive(S, 0)')
bindings = COMMON[:COMMON.index('$eager_cleanup_valid(S, pdestructioncleanup)')]
receiver_bindings = [
    'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
    '$throwable_previous_id(S, n_receiver) = (n_previous)',
]
groups = {
    'cursor-auth': checks[:finish_start],
    'publication-owners': bindings + receiver_bindings + [
        clause for clause in checks[finish_start:] if 'S_paused' not in clause],
    # Restored input identity is stronger than equal final outputs for $drive.
    # The completed continuation runs once; the zero-budget state loses no field.
    'budget-replay': bindings + [
        'S_paused[.COMPLETION = NORMAL] = S'
        if clause == '$drive(S_paused[.COMPLETION = NORMAL], 2000) = S_done'
        else clause
        for clause in checks[finish_start:]
        if 'S_paused' in clause or clause.startswith('S_done =')
        or clause.startswith('S_done.COMPLETION =')],
}
for group, clauses in groups.items():
    CASES[COMPILER_NAME + '-' + group] = {**compiler, 'checks': clauses}
runner.CASES = CASES

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selection = None if args.case is None else [
        name for selected in args.case for name in (
            [COMPILER_NAME + '-' + group for group in groups]
            if selected == COMPILER_NAME else [selected])]
    raise SystemExit(0 if runner.run(selection) else 1)
