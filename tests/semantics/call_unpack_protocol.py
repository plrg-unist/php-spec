#!/usr/bin/env python3
"""Source-bound unpack preparation, expansion and default-preflight controls."""
from pathlib import Path
import base64,json,os,subprocess,tempfile
import request_environment as q
import request_environment_state as rs
import function_scope as fs
from recorded_worker import Worker
R=Path(__file__).resolve().parents[2]
SOURCES = {'unpack-hole-default-before-type': 'PD9waHAKY29uc3QgQz0iMngiO2Z1bmN0aW9uIGYoaW50ICR4LCR5PUMrMSwkej0zKXt9CmYoLi4uWyJ6Ij0+MywieCI9PltdXSk7',
 'unpack-nested-call-send-line': 'PD9waHAKZnVuY3Rpb24gZiguLi4keCl7fQpmdW5jdGlvbiBnKCR4KXtyZXR1cm4gMTt9CmYoLi4uZygKIDEKKSk7',
 'unpack-suppressed-reference-assignment': 'PD9waHAgZnVuY3Rpb24gZigmJHgpeyR4PTI7fSAkYT1bMV07ZiguLi5AKCRjPSYkYSkpO2VjaG8gJGFbMF0sJGNbMF07',
 'unpack-reference-cv-array-cow': 'PD9waHAgZnVuY3Rpb24gZigmJHgpeyR4PTI7fSRhPVsxXTskYj0kYTtmKC4uLiRhKTtlY2hvICRhWzBdLCRiWzBdOw==',
 'unpack-reference-computed-variable-copy': 'PD9waHAgZnVuY3Rpb24gZigmJHgpeyR4PTI7fSRhPVsxXTskYj0kYTskbj0iYSI7ZiguLi4kJG4pO2VjaG8gJGFbMF0sJGJbMF07',
 'unpack-cv-later-deep-variable': 'PD9waHAgZnVuY3Rpb24gZigmJHgpeyR4PTI7fSRhPVsxXTskYj0kYTtmKC4uLiRhKTtlY2hvIHRydWU/KCRiWzBdPz8wKTowLCRhWzBdOw==',
 'unpack-fixed-name-then-separate-positional-array': 'PD9waHAgZnVuY3Rpb24gZigkYSwkYil7ZWNobyAkYSwkYjt9ZiguLi5bImEiPT4xXSwuLi5bMl0pOw=='}
CASES = [{'source': 'unpack-hole-default-before-type',
  'id': 'next-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "TypeError" n_message* 2',
             'S_full.REPORTING = 30719',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             'S_full.SILENCES = eps',
             '$heap_valid($heap_graph(S_full))']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-skip-entry',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall poperand 2 true) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-outside-container',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall poperand 99 true) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-forget-string-prefix',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall poperand 1 false) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-wrong-function',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall[.FUNCTION = porigin_call] poperand 1 true) :: '
             'ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-wrong-source-index',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall[.INDEX = 9] poperand 1 true) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-wrong-call-line',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall[.LINE = 99] poperand 1 true) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-container-scalar',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall (KNOWN (PINT 99)) 1 true) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-arbitrary-sent-value',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall[.SENT = pnamedargs_new] poperand 1 true) :: '
             'ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "TypeError" n_message* 2',
             'S_full.REPORTING = 30719',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             'S_full.SILENCES = eps',
             '$heap_valid($heap_graph(S_full))']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-arbitrary-active-result',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.RESULT = KNOWN (PINT 99)]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "TypeError" n_message* 2',
             'S_full.REPORTING = 30719',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             'S_full.SILENCES = eps',
             '$heap_valid($heap_graph(S_full))']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-change-unconsumed-value',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert(S.ARRAYS[n_array], '
             'KSTRING n_x*, DIRECT (PINT 99)))]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.REPORTING = 30719',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             'S_full.SILENCES = eps',
             '$heap_valid($heap_graph(S_full))']},
 {'source': 'unpack-nested-call-send-line',
  'id': 'line-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $review_line(pcodeexpr*, pcpath) : pcodeexpr*\n'
            'def $review_line(eps, pcpath) = eps\n'
            'def $review_line((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath $(z + 100) b) '
            ':: pcodeexpr*\n'
            'def $review_line((CODEEXPR pcpath_other z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath_other z '
            'b) :: $review_line(pcodeexpr*, pcpath)\n'
            '  -- if pcpath_other =/= pcpath\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0]',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "TypeError" n_message* 5',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps']},
 {'source': 'unpack-nested-call-send-line',
  'id': 'line-narg-forgery',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $review_line(pcodeexpr*, pcpath) : pcodeexpr*\n'
            'def $review_line(eps, pcpath) = eps\n'
            'def $review_line((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath $(z + 100) b) '
            ':: pcodeexpr*\n'
            'def $review_line((CODEEXPR pcpath_other z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath_other z '
            'b) :: $review_line(pcodeexpr*, pcpath)\n'
            '  -- if pcpath_other =/= pcpath\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0]',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.CODE = [pcode[.EXPRESSIONS = $review_line(pcode.EXPRESSIONS, pcpath)]]]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-suppressed-reference-assignment',
  'id': 'class-reference-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'S.RESULT = REFERENCE n_cell',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_VAR)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [50, 50]']},
 {'source': 'unpack-suppressed-reference-assignment',
  'id': 'class-forged-truth-redirect',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'S.RESULT = REFERENCE n_cell',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_VAR)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.CODE = [pcode[.REDIRECTS = (CODEREDIRECT pcpath pcpath_child true) :: '
             'pcode.REDIRECTS]]]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-suppressed-reference-assignment',
  'id': 'class-arbitrary-reference-value',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'S.RESULT = REFERENCE n_cell',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_VAR)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert(S.ARRAYS[n_array], '
             'KINT 0, DIRECT (PINT 99)))]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [50, 50]']},
 {'source': 'unpack-reference-cv-array-cow',
  'id': 'cv-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'n_a* = [97]',
             'n_b* = [98]',
             'S.RESULT = VARIABLE n_a* z_result',
             '$lookup(S.ENV, n_a*) = (n_cell)',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_CV)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [50, 49]']},
 {'source': 'unpack-reference-cv-array-cow',
  'id': 'cv-forged-variable-name',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'n_a* = [97]',
             'n_b* = [98]',
             'S.RESULT = VARIABLE n_a* z_result',
             '$lookup(S.ENV, n_a*) = (n_cell)',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_CV)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.RESULT = VARIABLE n_b* z_result]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-reference-cv-array-cow',
  'id': 'cv-arbitrary-array-value',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'n_a* = [97]',
             'n_b* = [98]',
             'S.RESULT = VARIABLE n_a* z_result',
             '$lookup(S.ENV, n_a*) = (n_cell)',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_CV)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert(S.ARRAYS[n_array], '
             'KINT 0, DIRECT (PINT 99)))]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [50, 57, 57]']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'preflight-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = [NAMED_PREFLIGHT porigin 0]\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = [NAMED_PREFLIGHT porigin 0]',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.FUNCTION = porigin',
             'pcallcontext.ARGC = 3',
             'n_x_name* = [120]',
             'n_y_name* = [121]',
             'n_z_name* = [122]',
             '$lookup(S.ENV, n_x_name*) = (n_x)',
             '$lookup(S.ENV, n_y_name*) = eps',
             '$lookup(S.ENV, n_z_name*) = (n_z)',
             'S.STORE[n_z] = DEFINED (PINT 3)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "TypeError" n_message* 2',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             'S_full.DEFAULTCACHE = [pdefaultcache]',
             'pdefaultcache.VALUE = PINT 3']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'preflight-shrink-extent',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = [NAMED_PREFLIGHT porigin 0]\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = [NAMED_PREFLIGHT porigin 0]',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.FUNCTION = porigin',
             'pcallcontext.ARGC = 3',
             'n_x_name* = [120]',
             'n_y_name* = [121]',
             'n_z_name* = [122]',
             '$lookup(S.ENV, n_x_name*) = (n_x)',
             '$lookup(S.ENV, n_y_name*) = eps',
             '$lookup(S.ENV, n_z_name*) = (n_z)',
             'S.STORE[n_z] = DEFINED (PINT 3)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.CURRENT = (pcallcontext[.ARGC = 1])]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'preflight-skip-hole',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = [NAMED_PREFLIGHT porigin 0]\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = [NAMED_PREFLIGHT porigin 0]',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.FUNCTION = porigin',
             'pcallcontext.ARGC = 3',
             'n_x_name* = [120]',
             'n_y_name* = [121]',
             'n_z_name* = [122]',
             '$lookup(S.ENV, n_x_name*) = (n_x)',
             '$lookup(S.ENV, n_y_name*) = eps',
             '$lookup(S.ENV, n_z_name*) = (n_z)',
             'S.STORE[n_z] = DEFINED (PINT 3)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.TODO = [NAMED_PREFLIGHT porigin 3]]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'preflight-legacy-type-bypass',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = [NAMED_PREFLIGHT porigin 0]\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = [NAMED_PREFLIGHT porigin 0]',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.FUNCTION = porigin',
             'pcallcontext.ARGC = 3',
             'n_x_name* = [120]',
             'n_y_name* = [121]',
             'n_z_name* = [122]',
             '$lookup(S.ENV, n_x_name*) = (n_x)',
             '$lookup(S.ENV, n_y_name*) = eps',
             '$lookup(S.ENV, n_z_name*) = (n_z)',
             'S.STORE[n_z] = DEFINED (PINT 3)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.TODO = [TYPE_RECEIVE porigin 0]]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'preflight-arbitrary-provided-value',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = [NAMED_PREFLIGHT porigin 0]\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = [NAMED_PREFLIGHT porigin 0]',
             'S.CURRENT = (pcallcontext)',
             'pcallcontext.FUNCTION = porigin',
             'pcallcontext.ARGC = 3',
             'n_x_name* = [120]',
             'n_y_name* = [121]',
             'n_z_name* = [122]',
             '$lookup(S.ENV, n_x_name*) = (n_x)',
             '$lookup(S.ENV, n_y_name*) = eps',
             '$lookup(S.ENV, n_z_name*) = (n_z)',
             'S.STORE[n_z] = DEFINED (PINT 3)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.STORE = $set_cell(S.STORE, n_x, DEFINED (PINT 99))]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             'S_full.DEFAULTCACHE = [pdefaultcache]',
             'pdefaultcache.VALUE = PINT 3']},
 {'source': 'unpack-nested-call-send-line',
  'id': 'call-result-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0]',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'n_missing* = [117]',
             'S.RESULT = KNOWN (PINT 1)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "TypeError" n_message* 5',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps']},
 {'source': 'unpack-nested-call-send-line',
  'id': 'call-result-variable',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0]',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'n_missing* = [117]',
             'S.RESULT = KNOWN (PINT 1)',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.RESULT = VARIABLE n_missing* 5]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'legacy-positional-unpack-lane',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*',
             'punpackcall.FUNCTION = porigin',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = phpType7*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.LINE = z',
             'punpackcall.SENT = pnamedargs',
             'pnamedargs.SLOTS = eps',
             'pnamedargs.NAMED = eps',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'poperand_sent* = eps',
             'S_changed = S[.TODO = (CALL_ARGS porigin phpType7* 0 poperand_sent* (porigin_call) z) :: '
             'ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'legacy-named-unpack-lane',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*',
             'punpackcall.FUNCTION = porigin',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = phpType7*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.LINE = z',
             'punpackcall.SENT = pnamedargs',
             'pnamedargs.SLOTS = eps',
             'pnamedargs.NAMED = eps',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'poperand_sent* = eps',
             'S_changed = S[.TODO = (NAMED_ARGS porigin phpType7* 0 pnamedargs (porigin_call) z) :: '
             'ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-reference-computed-variable-copy',
  'id': 'computed-prep-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'S.RESULT = KNOWN (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_VALUE)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [49, 49]']},
 {'source': 'unpack-cv-later-deep-variable',
  'id': 'cv-target-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $review_target_hit(pcoccurrence, nat) : bool\n'
            'def $review_target_hit(PCOCCURRENCE pcpath (NExprVariable (BYTES "Yg==") metadata), n) = '
            '$(|pcpath| > n)\n'
            'def $review_target_hit(pcoccurrence, n) = false -- otherwise\n'
            'dec $review_target(pcoccurrence*, nat) : pcpath?\n'
            'def $review_target((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, n) = (pcpath)\n'
            '  -- if $review_target_hit(PCOCCURRENCE pcpath pcnode, n)\n'
            'def $review_target(pcoccurrence :: pcoccurrence_tail*, n) = $review_target(pcoccurrence_tail*, '
            'n)\n'
            '  -- if ~$review_target_hit(pcoccurrence, n)\n'
            'def $review_target(eps, n) = eps\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'n_a* = [97]',
             'n_b* = [98]',
             'S.RESULT = VARIABLE n_a* z_result',
             '$lookup(S.ENV, n_a*) = (n_cell)',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_CV)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             '$source_unit(S.SOURCES, n_unit) = (pcunit)',
             '$review_target(pcunit.OCCURRENCES, |pcpath|) = (pcpath_target)',
             '$code_expression(pcode.EXPRESSIONS, pcpath_target) = ((z_target, false))',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$unpack_class(S_changed, punpackcall) = (UNPACK_CV)',
             '$outputs(S_full.EVENTS) = [49, 50]']},
 {'source': 'unpack-cv-later-deep-variable',
  'id': 'cv-same-class-target-forgery',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $review_target_hit(pcoccurrence, nat) : bool\n'
            'def $review_target_hit(PCOCCURRENCE pcpath (NExprVariable (BYTES "Yg==") metadata), n) = '
            '$(|pcpath| > n)\n'
            'def $review_target_hit(pcoccurrence, n) = false -- otherwise\n'
            'dec $review_target(pcoccurrence*, nat) : pcpath?\n'
            'def $review_target((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, n) = (pcpath)\n'
            '  -- if $review_target_hit(PCOCCURRENCE pcpath pcnode, n)\n'
            'def $review_target(pcoccurrence :: pcoccurrence_tail*, n) = $review_target(pcoccurrence_tail*, '
            'n)\n'
            '  -- if ~$review_target_hit(pcoccurrence, n)\n'
            'def $review_target(eps, n) = eps\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'porigin_call = PORIGIN n_unit pcpath_call',
             'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
             'pcpath_child = pcpath ++ [PCFIELD 0]',
             'n_a* = [97]',
             'n_b* = [98]',
             'S.RESULT = VARIABLE n_a* z_result',
             '$lookup(S.ENV, n_a*) = (n_cell)',
             'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
             '$unpack_class(S, punpackcall) = (UNPACK_CV)',
             'S.CODE = [pcode]',
             'pcode.UNIT = n_unit',
             'S.CURRENT = eps',
             '$source_unit(S.SOURCES, n_unit) = (pcunit)',
             '$review_target(pcunit.OCCURRENCES, |pcpath|) = (pcpath_target)',
             '$code_expression(pcode.EXPRESSIONS, pcpath_target) = ((z_target, false))',
             'S.DEFAULTCACHE = eps',
             '$call_descriptors_valid(S)',
             'S_changed = S[.CODE = [pcode[.REDIRECTS = (CODEREDIRECT pcpath pcpath_target false) :: '
             'pcode.REDIRECTS]]][.RESULT = VARIABLE n_b* z_result]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-hole-default-before-type',
  'id': 'next-rewind-before-first-container',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: '
            'ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 1 true) :: ptask_tail*',
             'punpackcall.CALLSITE = (porigin_call)',
             'punpackcall.INDEX = 0',
             'punpackcall.ARGUMENTS = eps',
             'punpackcall.SENT.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
             'punpackcall.SENT.NAMED = eps',
             'poperand = KNOWN (PARRAY n_array)',
             '$call_descriptors_valid(S)',
             'n_x* = [120]',
             'pnamedslot_new* = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']},
 {'source': 'unpack-fixed-name-then-separate-positional-array',
  'id': 'second-container-zero-control',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true\n'
            '  -- if S.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail*\n'
            '  -- if punpackcall.INDEX = 1\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail*',
             'punpackcall.INDEX = 1',
             'punpackcall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]',
             'punpackcall.SENT.NAMED = eps',
             'pnamedslot_new* = [NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             '$call_descriptors_valid(S)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [49, 50]']},
 {'source': 'unpack-fixed-name-then-separate-positional-array',
  'id': 'second-container-arbitrary-prior-value',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true\n'
            '  -- if S.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail*\n'
            '  -- if punpackcall.INDEX = 1\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            'dec $outputs(pevent*) : nat*\n'
            'def $outputs(eps) = eps\n'
            'def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)\n'
            'def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)\n'
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
             'S.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail*',
             'punpackcall.INDEX = 1',
             'punpackcall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]',
             'punpackcall.SENT.NAMED = eps',
             'pnamedslot_new* = [NAMED_SENT (KNOWN (PINT 99))]',
             'pnamedargs_new = {SLOTS pnamedslot_new*, NAMED eps}',
             '$call_descriptors_valid(S)',
             'S_changed = S[.TODO = (UNPACK_NEXT punpackcall[.SENT = pnamedargs_new] poperand 0 false) :: '
             'ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             'S_full.DEFAULTCACHE = eps',
             'S_full.FRAMES = eps',
             'S_full.CURRENT = eps',
             'S_full.HELD = eps',
             '$heap_valid($heap_graph(S_full))',
             '$outputs(S_full.EVENTS) = [57, 57, 50]']}]

D=Path(tempfile.mkdtemp(prefix='call-unpack-protocol-',dir=R/'.tools'))
(D/'producer.py').write_bytes(Path(__file__).read_bytes())
before=q.t.syntax_validation.implementation_fingerprint()
(D/'inputs.json').write_text(json.dumps({'fingerprint':before},indent=2));print(D,flush=True)
modules=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_text())]
runner=R/'tests/semantics/_build/default/numeric_runner.exe'
f=a=None;initials={};originals=[];records=[]
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],D/'frontend-wire')
 a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],D/'adapter-wire')
 for name,source64 in SOURCES.items():
  directory=D/name;directory.mkdir();path=directory/'source.php';path.write_bytes(base64.b64decode(source64))
  payload=directory/'request.input';payload.write_bytes(q.packet(1700000000,125000,[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one']))
  request={'env':[[q.b64(k),q.b64(v)] for k,v in [(b'LC_ALL',b'C'),(b'TZ',b'UTC'),(b'FIRST',b'one')]],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(directory))}
  native=fs.native(path,payload,directory);parsed=f.request({'op':'parse','source':source64});assert parsed['accepted']
  checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});(directory/'checked.json').write_text(json.dumps(checked))
  result=a.request({'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(os.fsencode(path)),'request':request});(directory/'state.json').write_text(json.dumps(result))
  actual=q.cli.observe(result['state'],str(path));assert actual['status'] in ('normal','php_error') and all(actual[k]==native[k] for k in ['stdout','stderr','exit_status'])
  originals.append({'id':name,'source_base64':source64,'context':str(path),'request':request,'native':native,'actual':actual});(D/'originals.json').write_text(json.dumps(originals,indent=2))
  initials[name]='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
finally:
 try:
  if f:f.close()
 finally:
  if a:a.close()
for case in CASES:
 checks=[s.replace('__INITIAL__',initials[case['source']]) for s in case['checks']]
 fixture=D/(case['id']+'.watsup');fixture.write_text(case['prefix']+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+s+'\n' for s in checks))
 command=[str(runner),*map(str,modules),str(fixture)];(D/(case['id']+'.command.json')).write_text(json.dumps(command))
 try:
  z=subprocess.run(command,capture_output=True,timeout=90)
 except subprocess.TimeoutExpired as e:
  (D/(case['id']+'.stdout')).write_bytes(e.stdout or b'');(D/(case['id']+'.stderr')).write_bytes(e.stderr or b'');(D/(case['id']+'.status.json')).write_text(json.dumps({'status':'timeout','seconds':90}));raise
 (D/(case['id']+'.stdout')).write_bytes(z.stdout);(D/(case['id']+'.stderr')).write_bytes(z.stderr);(D/(case['id']+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':z.returncode}))
 record={'id':case['id'],'source':case['source'],'valid':case['valid'],'assertions':len(checks),'pass':z.returncode==0 and z.stdout.strip()==b'true' and not z.stderr};records.append(record);(D/'results.json').write_text(json.dumps(records,indent=2));print(record,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint()
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','scope':'Actual-source unpack stage, descriptor and default-preflight relations; arbitrary consistent values and references remain valid. Native contexts overlap maintained source coverage.','fingerprint':before,'raw':str(D),'sources':len(originals),'cases':len(records),'assertions':sum(r['assertions'] for r in records),'records':records}
(D/'report.json').write_text(json.dumps(report,indent=2));target=R/'coverage/semantics/call-unpack-protocol.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2));assert report['result']=='pass'
