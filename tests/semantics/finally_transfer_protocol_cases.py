"""Pending finally transfer provenance in active and suspended call frames."""

PREFIX = r'''
dec $transfer_pending_task(ptask) : bool
def $transfer_pending_task(FINALLY_RETURN porigin porigin_source poperand) = true
def $transfer_pending_task(FINALLY_REF_RETURN porigin porigin_source poperand z) = true
def $transfer_pending_task(FINALLY_JUMP porigin porigin_source n_depth n_original b_continue) = true
def $transfer_pending_task(FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target) = true
def $transfer_pending_task(ptask) = false -- otherwise
dec $transfer_task(ptask*) : ptask?
def $transfer_task(eps) = eps
def $transfer_task((FINALLY_RETURN porigin porigin_source poperand) :: ptask*) = (FINALLY_RETURN porigin porigin_source poperand)
def $transfer_task((FINALLY_REF_RETURN porigin porigin_source poperand z) :: ptask*) = (FINALLY_REF_RETURN porigin porigin_source poperand z)
def $transfer_task((FINALLY_JUMP porigin porigin_source n_depth n_original b_continue) :: ptask*) = (FINALLY_JUMP porigin porigin_source n_depth n_original b_continue)
def $transfer_task((FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target) :: ptask*) = (FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target)
def $transfer_task(ptask :: ptask_tail*) = $transfer_task(ptask_tail*)
  -- if ~$transfer_pending_task(ptask)
dec $replace_transfer(ptask*, ptask, ptask) : ptask*
def $replace_transfer(eps, ptask_old, ptask_new) = eps
def $replace_transfer(ptask_old :: ptask_tail*, ptask_old, ptask_new) = ptask_new :: ptask_tail*
def $replace_transfer(ptask :: ptask_tail*, ptask_old, ptask_new) = ptask :: $replace_transfer(ptask_tail*, ptask_old, ptask_new)
  -- if ptask =/= ptask_old
dec $drop_transfer(ptask*, ptask) : ptask*
def $drop_transfer(eps, ptask_old) = eps
def $drop_transfer(ptask_old :: ptask_tail*, ptask_old) = ptask_tail*
def $drop_transfer(ptask :: ptask_tail*, ptask_old) = ptask :: $drop_transfer(ptask_tail*, ptask_old)
  -- if ptask =/= ptask_old
dec $other_goto(pstate, pcoccurrence*, nat, pcpath, pcpath) : pcpath?
dec $other_goto_at(pstate, pcoccurrence, nat, pcpath, pcpath) : bool
def $other_goto_at(S, PCOCCURRENCE pcpath_other (NStmtGoto phpType11 metadata), n, pcpath_source, pcpath_target) = (pcpath_other =/= pcpath_source /\ $goto_site(S, PORIGIN n pcpath_other, pcpath_target))
def $other_goto_at(S, pcoccurrence, n, pcpath_source, pcpath_target) = false -- otherwise
def $other_goto(S, eps, n, pcpath_source, pcpath_target) = eps
def $other_goto(S, (PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence_tail*, n, pcpath_source, pcpath_target) = (pcpath_other)
  -- if $other_goto_at(S, PCOCCURRENCE pcpath_other pcnode, n, pcpath_source, pcpath_target)
def $other_goto(S, pcoccurrence :: pcoccurrence_tail*, n, pcpath_source, pcpath_target) = $other_goto(S, pcoccurrence_tail*, n, pcpath_source, pcpath_target)
  -- if ~$other_goto_at(S, pcoccurrence, n, pcpath_source, pcpath_target)
'''

CASES = [
 ('transfer-return-current', b'<?php function f(){try{return 1;}finally{echo "F";}}echo f();',
  'S.TODO = (FINALLY_RETURN porigin porigin_source poperand) :: ptask*',
  ['S.TODO = (FINALLY_RETURN porigin porigin_source poperand) :: ptask*',
   '$call_task_valid(S,FINALLY_RETURN porigin porigin_source poperand)',
   '~$call_task_valid(S,FINALLY_RETURN porigin (PORIGIN 999 eps) poperand)',
   '~$call_descriptors_valid(S[.TODO = (FINALLY_RESUME porigin eps) :: ptask*])',
   '~$call_descriptors_valid(S[.TODO = ptask*])',
   '~$call_descriptors_valid(S[.TODO = S.TODO ++ [FINALLY_PHASE porigin 2]])',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-ref-current', b'<?php function &f(): int {$x=1;try{return $x;}finally{$x=2;echo "F";}}$y=&f();echo $y;',
  'S.TODO = (FINALLY_REF_RETURN porigin porigin_source (REFERENCE n_cell) z) :: ptask*',
  ['S.TODO = (FINALLY_REF_RETURN porigin porigin_source (REFERENCE n_cell) z) :: ptask*',
   '$call_task_valid(S,FINALLY_REF_RETURN porigin porigin_source (REFERENCE n_cell) z)',
   '~$call_task_valid(S,FINALLY_REF_RETURN porigin porigin_source (REFERENCE n_cell) $(z + 1))',
   '~$call_task_valid(S,FINALLY_REF_RETURN porigin porigin_source (REFERENCE 999) z)',
   '~$call_descriptors_valid(S[.TODO = ptask*])',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-jump-current', b'<?php for($i=0;$i<2;$i++){switch($i){case 0:try{continue 2;}finally{echo "F";}}echo "X";}echo "E";',
  'S.TODO = (FINALLY_JUMP porigin porigin_source n_depth n_original b_continue) :: ptask*',
  ['S.TODO = (FINALLY_JUMP porigin porigin_source n_depth n_original b_continue) :: ptask*',
   '$call_task_valid(S,FINALLY_JUMP porigin porigin_source n_depth n_original b_continue)',
   '~$call_task_valid(S,FINALLY_JUMP porigin porigin_source $(n_depth + 1) n_original b_continue)',
   '~$call_task_valid(S,FINALLY_JUMP porigin porigin_source n_depth n_original false)',
   '~$call_descriptors_valid(S[.TODO = ptask*])',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-goto-current', b'<?php try{goto OUT;goto OUT;}finally{echo "F";}OUT:echo "E";',
  'S.TODO = (FINALLY_GOTO porigin (PORIGIN n pcpath_source) pcpath_source pcpath_target) :: ptask*',
  ['S.TODO = (FINALLY_GOTO porigin (PORIGIN n pcpath_source) pcpath_source pcpath_target) :: ptask*',
   '$source_unit(S.SOURCES,n) = (pcunit)',
   '$other_goto(S,pcunit.OCCURRENCES,n,pcpath_source,pcpath_target) = (pcpath_other)',
   '$call_task_valid(S,FINALLY_GOTO porigin (PORIGIN n pcpath_source) pcpath_source pcpath_target)',
   '~$call_task_valid(S,FINALLY_GOTO porigin (PORIGIN n pcpath_other) pcpath_source pcpath_target)',
   '~$call_task_valid(S,FINALLY_GOTO porigin (PORIGIN n pcpath_source) pcpath_source pcpath_source)',
   '~$call_descriptors_valid(S[.TODO = ptask*])',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-return-saved', b'<?php function step(){echo "X";}function f(){try{return 7;}finally{step();}}echo f();',
  'S.FRAMES = pframe :: pframe_tail*\n  -- if $transfer_task(pframe.TODO) = (FINALLY_RETURN porigin porigin_source poperand)',
  ['S.FRAMES = pframe :: pframe_tail*',
   '$transfer_task(pframe.TODO) = (FINALLY_RETURN porigin porigin_source poperand)',
   '$call_frames_valid(S,S.FRAMES)',
   'S_bad = S[.FRAMES = pframe[.TODO = $replace_transfer(pframe.TODO, FINALLY_RETURN porigin porigin_source poperand, FINALLY_RESUME porigin eps)] :: pframe_tail*]',
   '~$call_frames_valid(S_bad,S_bad.FRAMES)',
   'S_deleted = S[.FRAMES = pframe[.TODO = $drop_transfer(pframe.TODO, FINALLY_RETURN porigin porigin_source poperand)] :: pframe_tail*]',
   '~$call_frames_valid(S_deleted,S_deleted.FRAMES)',
   'S_duplicate = S[.FRAMES = pframe[.TODO = pframe.TODO ++ [FINALLY_PHASE porigin 2]] :: pframe_tail*]',
   '~$call_frames_valid(S_duplicate,S_duplicate.FRAMES)',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-ref-saved', b'<?php function step(){echo "X";}function &f(): int{$x=1;try{return $x;}finally{$x=2;step();}}$y=&f();echo $y;',
  'S.FRAMES = pframe :: pframe_tail*\n  -- if $transfer_task(pframe.TODO) = (FINALLY_REF_RETURN porigin porigin_source poperand z)',
  ['S.FRAMES = pframe :: pframe_tail*',
   '$transfer_task(pframe.TODO) = (FINALLY_REF_RETURN porigin porigin_source poperand z)',
   '$call_frames_valid(S,S.FRAMES)',
   'S_bad = S[.FRAMES = pframe[.TODO = $replace_transfer(pframe.TODO, FINALLY_REF_RETURN porigin porigin_source poperand z, FINALLY_REF_RETURN porigin porigin_source poperand $(z + 1))] :: pframe_tail*]',
   '~$call_frames_valid(S_bad,S_bad.FRAMES)',
   'S_deleted = S[.FRAMES = pframe[.TODO = $drop_transfer(pframe.TODO, FINALLY_REF_RETURN porigin porigin_source poperand z)] :: pframe_tail*]',
   '~$call_frames_valid(S_deleted,S_deleted.FRAMES)',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-jump-saved', b'<?php function step(){echo "X";}for($i=0;$i<2;$i++){switch($i){case 0:try{continue 2;}finally{step();}}}echo "E";',
  'S.FRAMES = pframe :: pframe_tail*\n  -- if $transfer_task(pframe.TODO) = (FINALLY_JUMP porigin porigin_source n_depth n_original b_continue)',
  ['S.FRAMES = pframe :: pframe_tail*',
   '$transfer_task(pframe.TODO) = (FINALLY_JUMP porigin porigin_source n_depth n_original b_continue)',
   '$call_frames_valid(S,S.FRAMES)',
   'S_bad = S[.FRAMES = pframe[.TODO = $replace_transfer(pframe.TODO, FINALLY_JUMP porigin porigin_source n_depth n_original b_continue, FINALLY_JUMP porigin porigin_source $(n_depth + 1) n_original b_continue)] :: pframe_tail*]',
   '~$call_frames_valid(S_bad,S_bad.FRAMES)',
   'S_deleted = S[.FRAMES = pframe[.TODO = $drop_transfer(pframe.TODO, FINALLY_JUMP porigin porigin_source n_depth n_original b_continue)] :: pframe_tail*]',
   '~$call_frames_valid(S_deleted,S_deleted.FRAMES)',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-goto-saved', b'<?php function step(){echo "X";}try{goto OUT;}finally{step();}OUT:echo "E";',
  'S.FRAMES = pframe :: pframe_tail*\n  -- if $transfer_task(pframe.TODO) = (FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target)',
  ['S.FRAMES = pframe :: pframe_tail*',
   '$transfer_task(pframe.TODO) = (FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target)',
   '$call_frames_valid(S,S.FRAMES)',
   'S_bad = S[.FRAMES = pframe[.TODO = $replace_transfer(pframe.TODO, FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target, FINALLY_GOTO porigin porigin_source pcpath_source pcpath_source)] :: pframe_tail*]',
   '~$call_frames_valid(S_bad,S_bad.FRAMES)',
   'S_deleted = S[.FRAMES = pframe[.TODO = $drop_transfer(pframe.TODO, FINALLY_GOTO porigin porigin_source pcpath_source pcpath_target)] :: pframe_tail*]',
   '~$call_frames_valid(S_deleted,S_deleted.FRAMES)',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-ref-unwind', b'<?php function &f(): int{$x=1;try{return $x;}finally{$x=2;}}$y=&f();echo $y;',
  'S.TODO = (RETURN_REF_UNWIND poperand z b porigin_source) :: ptask*',
  ['S.TODO = (RETURN_REF_UNWIND poperand z b porigin_source) :: ptask*',
   '$call_task_valid(S,RETURN_REF_UNWIND poperand z b porigin_source)',
   '~$call_task_valid(S,RETURN_REF_UNWIND poperand $(z + 1) b porigin_source)',
   '~$call_task_valid(S,RETURN_REF_UNWIND poperand z b (PORIGIN 999 eps))',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
 ('transfer-goto-unwind', b'<?php try{goto OUT;goto OUT;}finally{echo "F";}OUT:echo "E";',
  'S.TODO = (GOTO_UNWIND (PORIGIN n pcpath_source) pcpath_source pcpath_target) :: ptask*',
  ['S.TODO = (GOTO_UNWIND (PORIGIN n pcpath_source) pcpath_source pcpath_target) :: ptask*',
   '$source_unit(S.SOURCES,n) = (pcunit)',
   '$other_goto(S,pcunit.OCCURRENCES,n,pcpath_source,pcpath_target) = (pcpath_other)',
   '$call_task_valid(S,GOTO_UNWIND (PORIGIN n pcpath_source) pcpath_source pcpath_target)',
   '~$call_task_valid(S,GOTO_UNWIND (PORIGIN n pcpath_other) pcpath_source pcpath_target)',
   '~$call_task_valid(S,GOTO_UNWIND (PORIGIN n pcpath_source) pcpath_source pcpath_source)',
   '$call_descriptors_valid(S)',
   '$drive(S,1000).COMPLETION = NORMAL']),
]
