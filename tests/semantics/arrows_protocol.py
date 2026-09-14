#!/usr/bin/env python3
"""Arrow capture, source-return, demand and shared suppression guards."""
from pathlib import Path
import base64,json,os,subprocess,tempfile
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
R=Path(__file__).resolve().parents[2]
SOURCES = {'arrow-never-discarded-reference-call': 'PD9waHAgZnVuY3Rpb24gJnIoKXtyZXR1cm4gMzt9JGY9Zm4oKTpuZXZlcj0+cigpOyRmKCk7',
 'arrow-never-suppressed-reference-call': 'PD9waHAgZnVuY3Rpb24gJnIoKXtyZXR1cm4gMzt9JGY9Zm4oKTpuZXZlcj0+QHIoKTskZigpOw==',
 'arrow-reference-return-value-and-call': 'PD9waHAKJHg9MjtmdW5jdGlvbiAmcigpe3JldHVybiAkR0xPQkFMU1sieCJdO30KJGE9Zm4gJigpPT4gMzsKJGI9Zm4gJigpPT5yKCk7CiR2PSYkYSgpOyR3PSYkYigpOyR3PTc7ZWNobyAkdiwkeDsK',
 'arrow-undefined-late-definition-read': 'PD9waHAgJGY9Zm4oKT0+JHg7ZWNobyAiQyI7JHg9OTtlY2hvICRmKCksIkUiOw==',
 'closure-body-suppressed-reference-call': 'PD9waHAgZnVuY3Rpb24gJnIoKXtyZXR1cm4gMzt9JGY9ZnVuY3Rpb24oKXtyZXR1cm4gQHIoKTt9OyRmKCk7',
 'silence-nested-call-restoration': 'PD9waHAgZnVuY3Rpb24gZygpe2VjaG8gIkciLCRtaXNzaW5nO3JldHVybiAxO31mdW5jdGlvbiBmKCl7ZWNobyBAZygpLCRpbnNpZGU7cmV0dXJuIDI7fWVjaG8gQGYoKSwkYWZ0ZXIsIkRPTkUiOw=='}
PREFIXES = {'384591ab1f6f': '\n'
                 'dec $resume_destructuring(pstate, nat) : pstate\n'
                 'def $resume_destructuring(S, n) = $drive(S[.COMPLETION = '
                 'NORMAL], n) -- if S.COMPLETION = BUDGET\n'
                 'def $resume_destructuring(S, n) = S -- if S.COMPLETION =/= '
                 'BUDGET\n'
                 '\n'
                 'var U : pcunit\n'
                 'dec $outputs(pevent*) : nat*\n'
                 'def $outputs(eps) = eps\n'
                 'def $outputs((OUTPUT n*) :: pevent*) = n* ++ '
                 '$outputs(pevent*)\n'
                 'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
                 'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = '
                 '$outputs(pevent*)\n'
                 'dec $messages(pevent*) : pevent*\n'
                 'def $messages(eps) = eps\n'
                 'def $messages((OUTPUT n*) :: pevent*) = $messages(pevent*)\n'
                 'def $messages((WARNING n* z) :: pevent*) = (WARNING n* z) :: '
                 '$messages(pevent*)\n'
                 'def $messages((DIAGNOSTIC text n* z) :: pevent*) = '
                 '(DIAGNOSTIC text n* z) :: $messages(pevent*)\n'
                 '\n'
                 'dec $review_stage(pstate, nat) : bool\n'
                 'def $review_stage(S, 0) = true -- if S.TODO = '
                 '(CLOSURE_CAPTURE 0 0) :: ptask*\n'
                 'def $review_stage(S, 1) = $closure_callable(S, 0)\n'
                 'def $review_stage(S, 2) = true -- if S.TODO = '
                 '(CLOSURE_RECEIVE porigin 0) :: ptask*\n'
                 'def $review_stage(S, n) = false -- otherwise\n'
                 'dec $review_seek(pstate, nat, nat) : pstate\n'
                 'def $review_seek(S, n_kind, n_left) = S -- if '
                 '$review_stage(S, n_kind)\n'
                 'def $review_seek(S, n_kind, n_left) = '
                 '$review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
                 'n_kind, n_rest)\n'
                 '  -- if ~$review_stage(S, n_kind)\n'
                 '  -- if $(n_left > 0)\n'
                 '  -- if n_rest = $(n_left - 1)\n'
                 '\n',
 '9771a4e12ed8': '\n'
                 'dec $resume_destructuring(pstate, nat) : pstate\n'
                 'def $resume_destructuring(S, n) = $drive(S[.COMPLETION = '
                 'NORMAL], n) -- if S.COMPLETION = BUDGET\n'
                 'def $resume_destructuring(S, n) = S -- if S.COMPLETION =/= '
                 'BUDGET\n'
                 '\n'
                 'var U : pcunit\n'
                 'dec $outputs(pevent*) : nat*\n'
                 'def $outputs(eps) = eps\n'
                 'def $outputs((OUTPUT n*) :: pevent*) = n* ++ '
                 '$outputs(pevent*)\n'
                 'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
                 'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = '
                 '$outputs(pevent*)\n'
                 'dec $messages(pevent*) : pevent*\n'
                 'def $messages(eps) = eps\n'
                 'def $messages((OUTPUT n*) :: pevent*) = $messages(pevent*)\n'
                 'def $messages((WARNING n* z) :: pevent*) = (WARNING n* z) :: '
                 '$messages(pevent*)\n'
                 'def $messages((DIAGNOSTIC text n* z) :: pevent*) = '
                 '(DIAGNOSTIC text n* z) :: $messages(pevent*)\n'
                 '\n'
                 'dec $review_stage(pstate, nat) : bool\n'
                 'def $review_stage(S, 0) = true\n'
                 '  -- if S.CURRENT = (pcallcontext)\n'
                 '  -- if pcallcontext.INSTANCE = (0)\n'
                 '  -- if S.TODO = (RETURN_VALUE z) :: ptask*\n'
                 'def $review_stage(S, 1) = true\n'
                 '  -- if S.CURRENT = (pcallcontext)\n'
                 '  -- if pcallcontext.NAME = [114]\n'
                 '  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*\n'
                 'def $review_stage(S, 2) = true\n'
                 '  -- if S.CURRENT = (pcallcontext)\n'
                 '  -- if pcallcontext.NAME = [114]\n'
                 '  -- if S.TODO = (RETURN_REF_VALUE z) :: ptask*\n'
                 'def $review_stage(S, n) = false -- otherwise\n'
                 'dec $review_seek(pstate, nat, nat) : pstate\n'
                 'def $review_seek(S, n_kind, n_left) = S -- if '
                 '$review_stage(S, n_kind)\n'
                 'def $review_seek(S, n_kind, n_left) = '
                 '$review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
                 'n_kind, n_rest)\n'
                 '  -- if ~$review_stage(S, n_kind)\n'
                 '  -- if $(n_left > 0)\n'
                 '  -- if n_rest = $(n_left - 1)\n'
                 'dec $review_no_arrow_entry(pcodeexpr) : pcodeexpr*\n'
                 'def $review_no_arrow_entry(CODEARROW pcpath z) = eps\n'
                 'def $review_no_arrow_entry(pcodeexpr) = [pcodeexpr] -- '
                 'otherwise\n'
                 'dec $review_no_arrow(pcodeexpr*) : pcodeexpr*\n'
                 'def $review_no_arrow(eps) = eps\n'
                 'def $review_no_arrow(pcodeexpr_head :: pcodeexpr_tail*) = '
                 '$review_no_arrow_entry(pcodeexpr_head) ++ '
                 '$review_no_arrow(pcodeexpr_tail*)\n'
                 'dec $review_bad_implicit_entry(pcodeexpr) : pcodeexpr\n'
                 'def $review_bad_implicit_entry(CODEIMPLICIT pcpath ptbytes '
                 'z) = CODEIMPLICIT pcpath ([113]) z\n'
                 'def $review_bad_implicit_entry(pcodeexpr) = pcodeexpr -- '
                 'otherwise\n'
                 'dec $review_bad_implicit(pcodeexpr*) : pcodeexpr*\n'
                 'def $review_bad_implicit(eps) = eps\n'
                 'def $review_bad_implicit(pcodeexpr_head :: pcodeexpr_tail*) '
                 '= $review_bad_implicit_entry(pcodeexpr_head) :: '
                 '$review_bad_implicit(pcodeexpr_tail*)\n'
                 'dec $review_bad_return_entry(ptask) : ptask\n'
                 'def $review_bad_return_entry(RETURN_REF_VALUE z) = '
                 'RETURN_REF_VALUE $(z + 1)\n'
                 'def $review_bad_return_entry(ptask) = ptask -- otherwise\n'
                 'dec $review_bad_return(ptask*) : ptask*\n'
                 'def $review_bad_return(eps) = eps\n'
                 'def $review_bad_return(ptask_head :: ptask_tail*) = '
                 '$review_bad_return_entry(ptask_head) :: '
                 '$review_bad_return(ptask_tail*)\n'
                 '\n',
 '0d13940d62ab': '\n'
                 'dec $resume_destructuring(pstate, nat) : pstate\n'
                 'def $resume_destructuring(S, n) = $drive(S[.COMPLETION = '
                 'NORMAL], n) -- if S.COMPLETION = BUDGET\n'
                 'def $resume_destructuring(S, n) = S -- if S.COMPLETION =/= '
                 'BUDGET\n'
                 '\n'
                 'var U : pcunit\n'
                 'dec $outputs(pevent*) : nat*\n'
                 'def $outputs(eps) = eps\n'
                 'def $outputs((OUTPUT n*) :: pevent*) = n* ++ '
                 '$outputs(pevent*)\n'
                 'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
                 'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = '
                 '$outputs(pevent*)\n'
                 'dec $messages(pevent*) : pevent*\n'
                 'def $messages(eps) = eps\n'
                 'def $messages((OUTPUT n*) :: pevent*) = $messages(pevent*)\n'
                 'def $messages((WARNING n* z) :: pevent*) = (WARNING n* z) :: '
                 '$messages(pevent*)\n'
                 'def $messages((DIAGNOSTIC text n* z) :: pevent*) = '
                 '(DIAGNOSTIC text n* z) :: $messages(pevent*)\n'
                 '\n'
                 'dec $review_stage(pstate, nat) : bool\n'
                 'def $review_stage(S, n_depth) = true\n'
                 '  -- if S.CURRENT = (pcallcontext)\n'
                 '  -- if $(|S.FRAMES| >= n_depth)\n'
                 '  -- if S.FRAMES = pframe_saved :: pframe_tail*\n'
                 '  -- if pframe_saved.SILENCES =/= eps\n'
                 'def $review_stage(S, n_depth) = false -- otherwise\n'
                 'dec $review_seek(pstate, nat, nat) : pstate\n'
                 'def $review_seek(S, n_depth, n_left) = S -- if '
                 '$review_stage(S, n_depth)\n'
                 'def $review_seek(S, n_depth, n_left) = '
                 '$review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
                 'n_depth, n_rest)\n'
                 '  -- if ~$review_stage(S, n_depth)\n'
                 '  -- if $(n_left > 0)\n'
                 '  -- if n_rest = $(n_left - 1)\n'
                 '\n',
 'df5deb1ce95b': '\n'
                 'dec $resume_destructuring(pstate, nat) : pstate\n'
                 'def $resume_destructuring(S, n) = $drive(S[.COMPLETION = '
                 'NORMAL], n) -- if S.COMPLETION = BUDGET\n'
                 'def $resume_destructuring(S, n) = S -- if S.COMPLETION =/= '
                 'BUDGET\n'
                 '\n'
                 'var U : pcunit\n'
                 'dec $outputs(pevent*) : nat*\n'
                 'def $outputs(eps) = eps\n'
                 'def $outputs((OUTPUT n*) :: pevent*) = n* ++ '
                 '$outputs(pevent*)\n'
                 'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
                 'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = '
                 '$outputs(pevent*)\n'
                 'dec $messages(pevent*) : pevent*\n'
                 'def $messages(eps) = eps\n'
                 'def $messages((OUTPUT n*) :: pevent*) = $messages(pevent*)\n'
                 'def $messages((WARNING n* z) :: pevent*) = (WARNING n* z) :: '
                 '$messages(pevent*)\n'
                 'def $messages((DIAGNOSTIC text n* z) :: pevent*) = '
                 '(DIAGNOSTIC text n* z) :: $messages(pevent*)\n'
                 '\n'
                 'dec $review_stage(pstate) : bool\n'
                 'def $review_stage(S) = true\n'
                 '  -- if S.CURRENT = (pcallcontext)\n'
                 '  -- if pcallcontext.NAME = [114]\n'
                 '  -- if S.TODO = (RETURN_REF_VALUE z) :: ptask*\n'
                 'def $review_stage(S) = true\n'
                 '  -- if S.CURRENT = (pcallcontext)\n'
                 '  -- if pcallcontext.NAME = [114]\n'
                 '  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*\n'
                 'def $review_stage(S) = false -- otherwise\n'
                 'dec $review_seek(pstate, nat) : pstate\n'
                 'def $review_seek(S, n) = S -- if $review_stage(S)\n'
                 'def $review_seek(S, n) = '
                 '$review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
                 'n_next)\n'
                 '  -- if ~$review_stage(S)\n'
                 '  -- if $(n > 0)\n'
                 '  -- if n_next = $(n - 1)\n'}
CASES = [{'id': 'partial-undefined-not-callable',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (CLOSURE_CAPTURE 0 0) :: ptask_tail*',
             'S.OBJECTS[0] = REALCLOSURE porigin_template pitem* pstaticcell*',
             'pitem* = [UNINITIALIZED]'],
  'predicate': '~$closure_callable(S, 0)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/partial-undefined-not-callable/control.watsup',
  'original_fixture_sha256': '05b21671b8ee36b3a16628ceeb732fdf21648b1b0f571b7feec9bc30d32c80ec'},
 {'id': 'partial-undefined-not-typed',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (CLOSURE_CAPTURE 0 0) :: ptask_tail*',
             'S.OBJECTS[0] = REALCLOSURE porigin_template pitem* pstaticcell*',
             'pitem* = [UNINITIALIZED]'],
  'predicate': '~$typed_closure(S, 0)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/partial-undefined-not-typed/control.watsup',
  'original_fixture_sha256': '1d0d21015691bce572f2eaedce94c46c51cbb811bc763a6f1404e5fe52f39a83'},
 {'id': 'legitimate-undefined-cursor-end',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (CLOSURE_CAPTURE 0 0) :: ptask_tail*',
             'S.OBJECTS[0] = REALCLOSURE porigin_template pitem* pstaticcell*',
             'pitem* = [UNINITIALIZED]',
             'S_changed = S[.TODO = (CLOSURE_CAPTURE 0 1) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '~$closure_callable(S_changed, 0)',
             '~$typed_closure(S_changed, 0)'],
  'predicate': '$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/legitimate-undefined-cursor-end/control.watsup',
  'original_fixture_sha256': 'd68513f1dfc6a9b49ab4fd44ca6a681716f3c8908c44ae68e773b714fddedcab'},
 {'id': 'reject-out-of-range-cursor',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (CLOSURE_CAPTURE 0 0) :: ptask_tail*',
             'S.OBJECTS[0] = REALCLOSURE porigin_template pitem* pstaticcell*',
             'pitem* = [UNINITIALIZED]',
             'S_changed = S[.TODO = (CLOSURE_CAPTURE 0 2) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/reject-out-of-range-cursor/control.watsup',
  'original_fixture_sha256': 'd8cc916cbae88f08d69e7e34f556572a1b6ef86341c48c5b0b8268101667a59e'},
 {'id': 'reject-capture-origin',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (CLOSURE_CAPTURE 0 0) :: ptask_tail*',
             'S.OBJECTS[0] = REALCLOSURE porigin_template pitem* pstaticcell*',
             'pitem* = [UNINITIALIZED]',
             'S_changed = S[.ORIGIN = (PORIGIN 0 eps)]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/reject-capture-origin/control.watsup',
  'original_fixture_sha256': '54e07532416513c35ebc4cf6c73efc48940c0e6790c87977f8cdc34298179574'},
 {'id': 'legitimate-arbitrary-completed-prefix',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (CLOSURE_CAPTURE 0 0) :: ptask_tail*',
             'S.OBJECTS[0] = REALCLOSURE porigin_template pitem* pstaticcell*',
             'pitem* = [UNINITIALIZED]',
             'S_changed = S[.OBJECTS = $object_set(S.OBJECTS, 0, REALCLOSURE porigin_template ([DIRECT (PINT '
             '99)]) pstaticcell*)][.TODO = (CLOSURE_CAPTURE 0 1) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '~$closure_callable(S_changed, 0)'],
  'predicate': '$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/legitimate-arbitrary-completed-prefix/control.watsup',
  'original_fixture_sha256': '492e25cb13876c714b3e90d7a0a8e6b33118a203d8ad1b24b049a97e111b9b5a'},
 {'id': 'completed-undefined-is-callable-and-typed',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$review_stage(S, 1)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.OBJECTS[0] = REALCLOSURE porigin_template ([UNINITIALIZED]) pstaticcell*',
             '$closure_callable(S, 0)'],
  'predicate': '$typed_closure(S, 0)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/completed-undefined-is-callable-and-typed/control.watsup',
  'original_fixture_sha256': '62c1a0cd635dbbff32efb5997f0e46f9579e8b0df56a7c8c7b67203933dfd8cd'},
 {'id': 'receive-undefined-completed-instance',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 2, 512)',
             '$review_stage(S, 2)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.INSTANCE = (0)',
             'S.OBJECTS[0] = REALCLOSURE porigin_template ([UNINITIALIZED]) pstaticcell*',
             '$closure_callable(S, 0)'],
  'predicate': '$call_descriptors_valid(S)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/receive-undefined-completed-instance/control.watsup',
  'original_fixture_sha256': '5d32cf416384eb67a3f2f4944f0c41b17dcc9bcc5dd60decf1ab729940945900'},
 {'id': 'reject-receive-instance-absence',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '384591ab1f6f',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 2, 512)',
             '$review_stage(S, 2)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.CURRENT = (pcallcontext)',
             'S_changed = S[.CURRENT = (pcallcontext[.INSTANCE = eps])]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/initial-arrow-controls-jgcfbzvr/reject-receive-instance-absence/control.watsup',
  'original_fixture_sha256': 'f223e5cf60875d4f053d799474c8d5fe2ddbed5dd447fda40e3d5c02515f5be6'},
 {'id': 'actual-arrow-value-return',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (RETURN_VALUE z) :: ptask_tail*'],
  'predicate': '$call_descriptors_valid(S)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/actual-arrow-value-return/control.watsup',
  'original_fixture_sha256': 'e89e5a83e5c709eafb2357a97203a005db332b16dcf9397d12c65861951b938b'},
 {'id': 'reject-arrow-return-line',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (RETURN_VALUE z) :: ptask_tail*',
             'S_changed = S[.TODO = (RETURN_VALUE $(z + 1)) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-arrow-return-line/control.watsup',
  'original_fixture_sha256': 'cf51f2e80b092c9689bbd501d5f5373053cf6667bd24f6a6cdc475b13bfb7fe2'},
 {'id': 'reject-arrow-return-origin',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (RETURN_VALUE z) :: ptask_tail*',
             'S_changed = S[.ORIGIN = (PORIGIN 0 eps)]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-arrow-return-origin/control.watsup',
  'original_fixture_sha256': '1780d567e73faca45501e109c75d13501cc8c52cb4bfa81a7c025a330f535de3'},
 {'id': 'reject-arrow-value-as-reference-return',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.TODO = (RETURN_VALUE z) :: ptask_tail*',
             'S_changed = S[.TODO = (RETURN_REF_VALUE z) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-arrow-value-as-reference-return/control.watsup',
  'original_fixture_sha256': '3cc2c4c21b3bc5d071000a97595c0a78a276fde2cedcaa5d0e8ffd430f835a81'},
 {'id': 'reject-source-arrow-marker-removal',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.CLOSURETEMPLATES = [pfunction]',
             'pfunction_new = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = '
             '$review_no_arrow(pfunction.CODE.EXPRESSIONS)]]',
             'S_changed = S[.CLOSURETEMPLATES = [pfunction_new]]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-source-arrow-marker-removal/control.watsup',
  'original_fixture_sha256': 'c6651760f4890502fc3a4016b2e5a93f474fc64d857c2717cec05f67e7c91a14'},
 {'id': 'reject-source-implicit-name-forgery',
  'source': 'arrow-undefined-late-definition-read',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 0, 512)',
             '$review_stage(S, 0)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.CLOSURETEMPLATES = [pfunction]',
             'pfunction_new = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = '
             '$review_bad_implicit(pfunction.CODE.EXPRESSIONS)]]',
             'S_changed = S[.CLOSURETEMPLATES = [pfunction_new]]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-source-implicit-name-forgery/control.watsup',
  'original_fixture_sha256': '05e7cbd038e8c3567e05a9936fdcf5fb9f4c556c640e9ba71db268d82bb26dd2'},
 {'id': 'actual-saved-arrow-reference-return',
  'source': 'arrow-reference-return-value-and-call',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$review_stage(S, 1)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe_saved :: pframe_tail*',
             'pframe_saved.CONTEXT = (pcallcontext_saved)',
             'pcallcontext_saved.INSTANCE = (n_instance)'],
  'predicate': '$call_frames_valid(S[.RESULT = KNOWN (PINT 99)], S.FRAMES)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/actual-saved-arrow-reference-return/control.watsup',
  'original_fixture_sha256': 'd29f170cdd444d0f9941bb6dec6020d04afee11f255f1ed29f591b87004a9664'},
 {'id': 'reject-saved-arrow-return-line',
  'source': 'arrow-reference-return-value-and-call',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$review_stage(S, 1)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe_saved :: pframe_tail*',
             'pframe_saved.CONTEXT = (pcallcontext_saved)',
             'pcallcontext_saved.INSTANCE = (n_instance)',
             'ptask_bad* = $review_bad_return(pframe_saved.TODO)',
             'ptask_bad* =/= pframe_saved.TODO',
             'S_changed = S[.FRAMES = (pframe_saved[.TODO = ptask_bad*]) :: pframe_tail*]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-saved-arrow-return-line/control.watsup',
  'original_fixture_sha256': '371c208df227ebf8b592d376389abf92e053231b30c54070c18f787c5940aec1'},
 {'id': 'reject-saved-arrow-instance-absence',
  'source': 'arrow-reference-return-value-and-call',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$review_stage(S, 1)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe_saved :: pframe_tail*',
             'pframe_saved.CONTEXT = (pcallcontext_saved)',
             'pcallcontext_saved.INSTANCE = (n_instance)',
             'S_changed = S[.FRAMES = (pframe_saved[.CONTEXT = (pcallcontext_saved[.INSTANCE = eps])]) :: '
             'pframe_tail*]',
             '$heap_valid($heap_graph(S_changed))'],
  'predicate': '~$call_descriptors_valid(S_changed)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-saved-arrow-instance-absence/control.watsup',
  'original_fixture_sha256': '666e3a0ccf8e48c028691f2e289d8774d8a56f7ae3c12f0e89c5231b869b9e3b'},
 {'id': 'reject-never-implicit-return',
  'source': 'arrow-never-discarded-reference-call',
  'prefix': '9771a4e12ed8',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 2, 512)',
             '$review_stage(S, 2)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe_saved :: pframe_tail*',
             'pframe_saved.CONTEXT = (pcallcontext_saved)',
             'pcallcontext_saved.INSTANCE = (n_instance)',
             'S_scope = S[.CURRENT = (pcallcontext_saved)][.ORIGIN = (pcallcontext_saved.FUNCTION)]'],
  'predicate': '~$call_task_valid(S_scope, RETURN_VALUE 1)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/return-arrow-controls-6m8dgya1/reject-never-implicit-return/control.watsup',
  'original_fixture_sha256': '04a798248260e573536b2db89f23fbdd261214890a4299f33e00ecc5f655cccb'},
 {'id': 'suppression-arrow-never-suppressed-reference-call-depth1',
  'source': 'arrow-never-suppressed-reference-call',
  'prefix': '0d13940d62ab',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe :: pframe_tail*',
             'pframe.SILENCES = (SILENCE porigin i_reporting) :: psilence*',
             '$silence_origin_valid(S[.CURRENT = pframe.CONTEXT], porigin)',
             '$call_frames_valid(S[.RESULT = KNOWN (PINT 99)], S.FRAMES)',
             '$drive(S[.COMPLETION = NORMAL], 1) = $drive_steps(S[.COMPLETION = NORMAL], 1)',
             '$drive(S[.COMPLETION = NORMAL], 10000) = $drive_steps(S[.COMPLETION = NORMAL], 10000)',
             'pframe.CONTEXT = (pcallcontext)',
             '~$silence_owner(S[.CURRENT = eps], porigin)'],
  'predicate': 'true',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/suppression-controls-review12-arrows-suppression1024-51ixceuk/arrow-never-suppressed-reference-call/1.watsup',
  'original_fixture_sha256': 'b739f569e50c855be2ebf22454f8b61114562b058f76c9cc0fae3c703f06c62f'},
 {'id': 'suppression-closure-body-suppressed-reference-call-depth1',
  'source': 'closure-body-suppressed-reference-call',
  'prefix': '0d13940d62ab',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe :: pframe_tail*',
             'pframe.SILENCES = (SILENCE porigin i_reporting) :: psilence*',
             '$silence_origin_valid(S[.CURRENT = pframe.CONTEXT], porigin)',
             '$call_frames_valid(S[.RESULT = KNOWN (PINT 99)], S.FRAMES)',
             '$drive(S[.COMPLETION = NORMAL], 1) = $drive_steps(S[.COMPLETION = NORMAL], 1)',
             '$drive(S[.COMPLETION = NORMAL], 10000) = $drive_steps(S[.COMPLETION = NORMAL], 10000)',
             'pframe.CONTEXT = (pcallcontext)',
             '~$silence_owner(S[.CURRENT = eps], porigin)'],
  'predicate': 'true',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/suppression-controls-review12-arrows-suppression1024-51ixceuk/closure-body-suppressed-reference-call/1.watsup',
  'original_fixture_sha256': 'beabb7cc9b0b889306c08b70eed9b12cf8c412989dbd31384e89e9ed6fe5d367'},
 {'id': 'suppression-silence-nested-call-restoration-depth1',
  'source': 'silence-nested-call-restoration',
  'prefix': '0d13940d62ab',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 1, 512)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe :: pframe_tail*',
             'pframe.SILENCES = (SILENCE porigin i_reporting) :: psilence*',
             '$silence_origin_valid(S[.CURRENT = pframe.CONTEXT], porigin)',
             '$call_frames_valid(S[.RESULT = KNOWN (PINT 99)], S.FRAMES)',
             '$drive(S[.COMPLETION = NORMAL], 1) = $drive_steps(S[.COMPLETION = NORMAL], 1)',
             '$drive(S[.COMPLETION = NORMAL], 10000) = $drive_steps(S[.COMPLETION = NORMAL], 10000)'],
  'predicate': 'true',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/suppression-controls-review12-arrows-suppression1024-51ixceuk/silence-nested-call-restoration/1.watsup',
  'original_fixture_sha256': '17acbb9a79fef28fb68cf75bd17b5d29e6c281c39b2093fa0bffa8383d1fca2c'},
 {'id': 'suppression-silence-nested-call-restoration-depth2',
  'source': 'silence-nested-call-restoration',
  'prefix': '0d13940d62ab',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 2, 512)',
             '$heap_valid($heap_graph(S))',
             '$call_descriptors_valid(S)',
             'S.FRAMES = pframe :: pframe_tail*',
             'pframe.SILENCES = (SILENCE porigin i_reporting) :: psilence*',
             '$silence_origin_valid(S[.CURRENT = pframe.CONTEXT], porigin)',
             '$call_frames_valid(S[.RESULT = KNOWN (PINT 99)], S.FRAMES)',
             '$drive(S[.COMPLETION = NORMAL], 1) = $drive_steps(S[.COMPLETION = NORMAL], 1)',
             '$drive(S[.COMPLETION = NORMAL], 10000) = $drive_steps(S[.COMPLETION = NORMAL], 10000)'],
  'predicate': 'true',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/suppression-controls-review12-arrows-suppression1024-51ixceuk/silence-nested-call-restoration/2.watsup',
  'original_fixture_sha256': 'a10a82ba46a7cac2ec524c413b6ad84771f8ad3548c6fb02577b0c8b37acaf61'},
 {'id': 'demand-arrow-never-discarded-reference-call',
  'source': 'arrow-never-discarded-reference-call',
  'prefix': 'df5deb1ce95b',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 512)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.NAME = [114]',
             'S.FRAMES =/= eps',
             '$review_stage(S)'],
  'predicate': '~$reference_return_used(S)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/never-demand-review12-arrows-demand1021-68snresz/control.watsup',
  'original_fixture_sha256': '838e50211960d094b0cd1f411055f24424d3bc59153104ea1a7258bfa3ddbeb0'},
 {'id': 'demand-arrow-reference-return-value-and-call',
  'source': 'arrow-reference-return-value-and-call',
  'prefix': 'df5deb1ce95b',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 512)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.NAME = [114]',
             'S.FRAMES =/= eps',
             '$review_stage(S)'],
  'predicate': '$reference_return_used(S)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/never-demand-review12-arrows-demand1021-epo3d_92/control.watsup',
  'original_fixture_sha256': 'c66f9b897a93f412b85d104e7d826593abd8b176b6dcd1675d679e0ab0091d95'},
 {'id': 'demand-arrow-never-suppressed-reference-call',
  'source': 'arrow-never-suppressed-reference-call',
  'prefix': 'df5deb1ce95b',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_seek(S_initial[.COMPLETION = NORMAL], 512)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.NAME = [114]',
             'S.FRAMES =/= eps',
             '$review_stage(S)'],
  'predicate': '~$reference_return_used(S)',
  'original_fixture': '/home/user/workspace/php-spec/.tools/review12-arrows118/never-demand-review12-arrows-suppression1024-44qy_mph/control.watsup',
  'original_fixture_sha256': 'a79252b6ceea2191e77caaa61c5c8678d059aa7e7afe87de53bdf5c70ec9d626'}]
D=Path(tempfile.mkdtemp(prefix='arrows-protocol-',dir=R/'.tools'))
(D/'producer.py').write_bytes(Path(__file__).read_bytes())
before=q.t.syntax_validation.implementation_fingerprint()
(D/'inputs.json').write_text(json.dumps({'fingerprint':before},indent=2));print(D,flush=True)
modules=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_text())]
runner=R/'tests/semantics/_build/default/numeric_runner.exe'
f=a=None;initials={};fulls={};originals=[];records=[]
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],D/'frontend-wire')
 a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],D/'adapter-wire')
 for name,source64 in SOURCES.items():
  directory=D/name;directory.mkdir();path=directory/'source.php';path.write_bytes(base64.b64decode(source64))
  payload=directory/'request.input';payload.write_bytes(q.packet(1700000000,125000,[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one']))
  request={'env':[[q.b64(k),q.b64(v)] for k,v in [(b'LC_ALL',b'C'),(b'TZ',b'UTC'),(b'FIRST',b'one')]],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(directory))}
  parsed=f.request({'op':'parse','source':source64});assert parsed['accepted']
  checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});(directory/'checked.json').write_text(json.dumps(checked))
  originals.append({'id':name,'source_base64':source64,'context':str(path),'request':request});(D/'originals.json').write_text(json.dumps(originals,indent=2))
  initials[name]='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
  fulls[name]='$php_request_run('+checked['fixture']+', 10000, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
finally:
 try:
  if f:f.close()
 finally:
  if a:a.close()
for case in CASES:
 checks=[s.replace('__INITIAL__',initials[case['source']]).replace('__FULL__',fulls[case['source']]) for s in case['checks']]
 fixture=D/(case['id']+'.watsup');fixture.write_text(PREFIXES[case['prefix']]+'\ndec $main() : bool\ndef $main() = '+case['predicate']+'\n'+''.join('  -- if '+s+'\n' for s in checks))
 command=[str(runner),*map(str,modules),str(fixture)];(D/(case['id']+'.command.json')).write_text(json.dumps(command))
 try:
  z=subprocess.run(command,capture_output=True,timeout=900)
 except subprocess.TimeoutExpired as e:
  (D/(case['id']+'.stdout')).write_bytes(e.stdout or b'');(D/(case['id']+'.stderr')).write_bytes(e.stderr or b'');(D/(case['id']+'.status.json')).write_text(json.dumps({'status':'timeout','seconds':900}));raise
 (D/(case['id']+'.stdout')).write_bytes(z.stdout);(D/(case['id']+'.stderr')).write_bytes(z.stderr);(D/(case['id']+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':z.returncode}))
 record={'id':case['id'],'source':case['source'],'assertions':len(checks)+1,'pass':z.returncode==0 and z.stdout==b'true\n' and not z.stderr};records.append(record);(D/'results.json').write_text(json.dumps(records,indent=2));print(record,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint()
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','scope':'Twenty-six original finite arrow capture/source/return/demand and shared suppression controls. Exact predicates and group helpers are retained; only checked source/request initializers are rebound. No native execution or history reconstruction','fingerprint':before,'raw':str(D),'sources':len(originals),'cases':len(records),'assertions':sum(r['assertions'] for r in records),'records':records}
(D/'report.json').write_text(json.dumps(report,indent=2));target=R/'coverage/semantics/arrows-protocol.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2));assert report['result']=='pass'
