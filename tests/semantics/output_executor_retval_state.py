#!/usr/bin/env python3
"""Check the source-reached noarg start during selected-handler retval cleanup."""
import argparse
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
review.ROOT = ROOT
review.CASES = {
    'retval-destructor-failed-start': {
        'source': (HERE / 'output_executor_post_deactivate_retval.php').read_text(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if pconfigcall.SENT = eps '
                 '-- if S.FRAMES = [pframe, pframe_executor] '
                 '-- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
                 '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_saved*',
        'checks': [
            'pconfigcall.INDEX = 0',
            'pconfigcall.LINE = 5',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1 /\\ ~S.OUTPUTBLOCKED',
            'S.ERRORHANDLER.CALLBACK = eps',
            'perrorcall.RESUME = OB_NOTICE_RESULT pobnotice',
            'ptask_saved* = pobnotice.TAIL',
            'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            'S.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructorcall.RELEASE = (pdestructionrelease_saved)',
            'pdestructionrelease_saved.JOBS = [DESTRUCTION_VALUE (HOBJECT pdestructorcall.OBJECT)]',
            'pdestructionrelease.JOBS = eps',
            'pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
            'S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
            'S_invoke = S[.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*]',
            '$config_invoke_valid(S_invoke, pconfigcall)',
            '$executor_normal_scope(S_invoke)',
            '$executor_retval_notice_start(S_invoke)',
            '$executor_ob_start_allowed(S_invoke)',
            '$executor_boundary(S_invoke) = eps',
            '~$executor_retval_notice_start(S_invoke[.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)])',
            '~$executor_retval_notice_start(S_invoke[.DESTRUCTION.CLEANUPS = eps])',
            'pdestructionrelease_bad = pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT pdestructorcall.OBJECT)]]',
            'S_release_bad = S_invoke[.DESTRUCTION.RELEASES = pdestructionrelease_bad :: pdestructionrelease_tail*]',
            '~$executor_retval_notice_start(S_release_bad)',
            'S_view = S_invoke[.TODO = pframe.TODO][.CURRENT = pframe.CONTEXT]'
            '[.ORIGIN = pframe.ORIGIN][.CONSTCONTEXT = pframe.CONSTCONTEXT]'
            '[.FRAMES = [pframe_executor]]',
            '$ob_notice_valid(S_view, pobnotice)',
            'S_done = $drive_steps(S_invoke, 1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=120) else 1)
