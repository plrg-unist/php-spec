#!/usr/bin/env python3
"""Reached FINAL throw takeover, authentic caller guard and fatal resumption."""
import argparse
from pathlib import Path
import fiber_state_review as review
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
VALID=['$output_state_valid(S)','$destruction_state_valid(S)',
       '$call_descriptors_valid(S)','$heap_valid($heap_graph(S))']
CASES={
 'restored-final-error-takes-over-and-resumes-fatal':{
  'source':(HERE/'output_request_end_held_throw.php').read_text(),
  'stage':'S.TODO = [THROW_SEARCH n_throwable, OB_USER_RESULT pobinvoke, OUTPUT_DRAIN pobdrain] '
          '-- if S.CURRENT = eps -- if S.FRAMES = eps',
  'checks':[
   'pobinvoke.CALL = OB_FINAL pobdrain',
   'S.SHUTDOWN.PHASE = SHUTDOWN_DONE','S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
   'S.EXCEPTIONHANDLER = eps','S.OBJECTS[n_throwable] = THROWABLE pthrowable',
   'pthrowable.KIND = "Error"',
   '$throwable_field(S, n_throwable, "message") = PSTRING $ptascii("Can only throw objects")',
   '$throwable_field(S, n_throwable, "previous") = PNULL',
   '$throwable_field(S, n_throwable, "string") = PSTRING eps',
   'pobdrain.VALUE = KNOWN PNULL','pobdrain.BASE = BASE_VALUE (KNOWN PNULL)',
   'pobdrain.COMPLETION = NORMAL',
   'pobinvoke.SENT = [KNOWN pobinvoke.INPUT, KNOWN (PINT pobinvoke.PHASE)]',
   '$output_final_throw_ready(S, pobinvoke, n_throwable)',
   '~$output_final_throw_ready(S[.TODO = [THROW_SEARCH n_throwable, OB_USER_RESULT pobinvoke]], pobinvoke, n_throwable)',
   '~$output_final_throw_ready(S[.EXCEPTIONHANDLER = (pobdrain.SOURCE.ZOH)], pobinvoke, n_throwable)',
   'pobdrain_wrong = pobdrain[.SOURCE = pobdrain.SOURCE[.NAME = $ptascii("wrong")]]',
   'pobinvoke_wrong = pobinvoke[.CALL = OB_FINAL pobdrain_wrong][.BUFFER = pobinvoke.BUFFER[.HANDLER = (pobdrain_wrong.SOURCE)]]',
   '~$output_final_throw_ready(S[.TODO = [THROW_SEARCH n_throwable, OB_USER_RESULT pobinvoke_wrong, OUTPUT_DRAIN pobdrain_wrong]], pobinvoke_wrong, n_throwable)',
   *VALID,
   'S_next = $drive_steps(S, 1)','S_next.COMPLETION = BUDGET',
   'S_next.TODO = [OUTPUT_FINAL_PENDING pobdeactivate_pending n_throwable true]',
   'S_next.OUTPUTBUFFERS = S.OUTPUTBUFFERS',
   'pobdeactivate_pending.CALL = pobinvoke',
   '$call_task_valid(S_next[.COMPLETION = NORMAL], OUTPUT_FINAL_PENDING pobdeactivate_pending n_throwable true)',
   '$heap_owners($heap_graph(S_next), HOBJECT n_throwable) = 1',
   'S_deactivated = $drive_steps(S_next[.COMPLETION = NORMAL], 2)',
   'S_deactivated.COMPLETION = BUDGET',
   'S_deactivated.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]',
   'pobdeactivate.CALL = pobinvoke','pobdeactivate.BUFFERS = S.OUTPUTBUFFERS',
   'pobdeactivate.INDEX = 0',
   'pobdeactivate.COMPLETION = REQUESTFATAL $ptascii("Error") $ptascii("Can only throw objects") 4',
   'S_deactivated.OUTPUTBUFFERS = eps','S_deactivated.EXITSTATUS = 255',
   '$output_deactivate_active(S_deactivated, pobdeactivate)',
   '~$output_deactivate_active(S_deactivated[.TODO = eps], pobdeactivate)',
   '~$output_deactivate_valid(S_deactivated, pobdeactivate[.COMPLETION = NORMAL])',
   'n_buffers = |pobdeactivate.BUFFERS|',
   '~$output_deactivate_valid(S_deactivated, pobdeactivate[.INDEX = $(n_buffers + 1)])',
   '$task_nodes(OUTPUT_FINAL_DEACTIVATE pobdeactivate) = $operand_nodes(pobdrain.VALUE) ++ $base_nodes(pobdrain.BASE) ++ $output_roots(S.OUTPUTBUFFERS)',
   '$output_state_valid(S_deactivated)','$destruction_state_valid(S_deactivated)',
   '$call_descriptors_valid(S_deactivated)','$heap_valid($heap_graph(S_deactivated))',
   'S_zero = $drive_steps(S_deactivated[.COMPLETION = NORMAL], 0)',
   'S_zero.COMPLETION = BUDGET','S_zero.TODO = S_deactivated.TODO',
   'S_zero.ALLOCATIONS = S_deactivated.ALLOCATIONS',
   'S_done = $drive_steps(S_deactivated[.COMPLETION = NORMAL], 600)',
   '$drive_steps(S_zero[.COMPLETION = NORMAL], 600) = S_done',
   'S_done.COMPLETION = pobdeactivate.COMPLETION','S_done.EXITSTATUS = 255',
   'S_done.TODO = eps','S_done.OUTPUTBUFFERS = eps',
   'S_done.CURRENT = eps','S_done.FRAMES = eps',
   'S_done.EVENTS = S_deactivated.EVENTS',
   '~((HOBJECT n_throwable) <- S_done.ALLOCATIONS)',
   'S_done.DESTRUCTION.CALLS = eps','S_done.DESTRUCTION.RELEASES = eps',
   'S_done.DESTRUCTION.FRAMES = eps','S_done.DESTRUCTION.OPERATIONS = eps',
   'S_done.DESTRUCTION.CLEANUPS = eps',
   '~$output_final_destructors(S_done)','$destruction_state_valid(S_done)',
   '$call_descriptors_valid(S_done)','$heap_valid($heap_graph(S_done))',
  ]},
}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',action='append');args=parser.parse_args()
 assert not args.case or set(args.case)<=CASES.keys()
 review.ROOT=ROOT;review.CASES=CASES
 for name in args.case or list(CASES):assert review.run([name])
