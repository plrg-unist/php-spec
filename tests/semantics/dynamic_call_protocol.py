#!/usr/bin/env python3
"""Source-bound dynamic/fixed-name call stages with arbitrary consistent values."""
from pathlib import Path
import base64,json,os,subprocess,tempfile
import request_environment as q
import request_environment_state as rs
import function_scope as fs
from recorded_worker import Worker
R=Path(__file__).resolve().parents[2]
SOURCES = {'dynamic-hole-float-cache-fresh-reference': 'PD9waHAKY29uc3QgQz0iMi41eCI7ZnVuY3Rpb24gJmYoaW50ICYkeD1DKzEsJHk9MCl7cmV0dXJuICR4O30KJG49ImYiO0AoJGE9JiRuKHk6MCkpOyRhPTc7JGI9JiRuKHk6MCk7ZWNobyAkYSwkYjs=',
 'dynamic-reference-callee-owner-before-argument': 'PD9waHAKJG49ImYiO2Z1bmN0aW9uICZuYW1lKCl7Z2xvYmFsICRuO3JldHVybiAkbjt9CmZ1bmN0aW9uIGtpbGwoKXt1bnNldCgkR0xPQkFMU1sibiJdKTtyZXR1cm4gMDt9ZnVuY3Rpb24gZigkeCl7cmV0dXJuIFsxXTt9CiRhPShuYW1lKCkpKGtpbGwoKSk7JGI9JGE7JGFbMF09MjtlY2hvICRiWzBdLCRhWzBdOw==',
 'dynamic-fixed-constant-selected-target': 'PD9waHAgZnVuY3Rpb24gZjEoJHgpe2VjaG8gMTt9ZnVuY3Rpb24gZygkeCl7ZWNobyAyO30oImYiLigxKzApKSgwKTs='}
CASES = [{'id': 'control',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': 'a0fd4a2f57fc63d2d85ba54895ad1e618dacd7e5d1919e2d4eb5c16c40283980'},
 {'id': 'wrong-init-line',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.TODO = (CALL_DYNAMIC porigin $(z_init + 100) z_call) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': 'f7ed02fe0cc908556eee5d6205eca494d17d8a1db8ac82cea15b5896c43853ee'},
 {'id': 'wrong-call-line',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.TODO = (CALL_DYNAMIC porigin z_init $(z_call + 100)) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': 'ae92a945b0bf9f298af95802db82df0e7971bf8627a2041d4facce8206c73450'},
 {'id': 'wrong-source-origin',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'porigin_other = PORIGIN 0 eps',
             'S_changed = S[.TODO = (CALL_DYNAMIC porigin_other z_init z_call) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': 'a422b02729549a7d24a3a847ada42a2c7fdf589d2f687c35b9b1b08ecda75989'},
 {'id': 'wrong-literal-cv-name',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'n_other* = [97]',
             'S_changed = S[.RESULT = VARIABLE n_other* z_read]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': '5fb49434184b3ed31865468cfbb01e8debfae6f4b74f5744014e48e3d200c14f'},
 {'id': 'wrong-cv-owning-result',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'n_f* = [102]',
             'S_changed = S[.RESULT = KNOWN (PSTRING n_f*)]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': 'b0426978bb80683b089de45eb6ee39f083dbc5b3456a51b46ed5f8c160776a27'},
 {'id': 'forged-source-init-marker',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n'
            'dec $review_init_match(pcodeexpr, pcpath) : bool\n'
            'def $review_init_match(CODECALL_INIT pcpath z, pcpath) = true\n'
            'def $review_init_match(pcodeexpr, pcpath) = false -- otherwise\n'
            'dec $review_init_rewrite(pcodeexpr*, pcpath, int) : pcodeexpr*\n'
            'def $review_init_rewrite(eps, pcpath, z) = eps\n'
            'def $review_init_rewrite((CODECALL_INIT pcpath z_old) :: pcodeexpr*, pcpath, z) = '
            '(CODECALL_INIT pcpath z) :: pcodeexpr*\n'
            'def $review_init_rewrite(pcodeexpr :: pcodeexpr_tail*, pcpath, z) = pcodeexpr :: '
            '$review_init_rewrite(pcodeexpr_tail*, pcpath, z)\n'
            '  -- if ~$review_init_match(pcodeexpr, pcpath)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'porigin = PORIGIN n_unit pcpath',
             'S.CODE = [pcode]',
             'pcode_new = pcode[.EXPRESSIONS = $review_init_rewrite(pcode.EXPRESSIONS, pcpath, $(z_init + '
             '100))]',
             'pcode_changed* = [pcode_new]',
             'S_changed = S[.CODE = pcode_changed*][.TODO = (CALL_DYNAMIC porigin $(z_init + 100) z_call) :: '
             'ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': '49a6c1329515ceb82b26d324e466979189ddf7dbebfe5e27106871fa5d5fbfca'},
 {'id': 'arbitrary-cv-store-scalar',
  'source': 'dynamic-hole-float-cache-fresh-reference',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n'
            'dec $review_init_match(pcodeexpr, pcpath) : bool\n'
            'def $review_init_match(CODECALL_INIT pcpath z, pcpath) = true\n'
            'def $review_init_match(pcodeexpr, pcpath) = false -- otherwise\n'
            'dec $review_init_rewrite(pcodeexpr*, pcpath, int) : pcodeexpr*\n'
            'def $review_init_rewrite(eps, pcpath, z) = eps\n'
            'def $review_init_rewrite((CODECALL_INIT pcpath z_old) :: pcodeexpr*, pcpath, z) = '
            '(CODECALL_INIT pcpath z) :: pcodeexpr*\n'
            'def $review_init_rewrite(pcodeexpr :: pcodeexpr_tail*, pcpath, z) = pcodeexpr :: '
            '$review_init_rewrite(pcodeexpr_tail*, pcpath, z)\n'
            '  -- if ~$review_init_match(pcodeexpr, pcpath)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = VARIABLE n_name* z_read',
             'n_name* = [110]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             '$lookup(S.ENV, n_name*) = (n_cell)',
             'S_changed = S[.STORE[n_cell] = DEFINED (PINT 99)]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "Error" n_message* z_error'],
  'original_fixture_sha256': '525f7e899542044942ad8d5a68a7d83817ece8aa16ad978c3ab6799eda8161f2'},
 {'id': 'reference-result-control',
  'source': 'dynamic-reference-callee-owner-before-argument',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = REFERENCE n_result',
             'n_name* = [110]',
             'n_f* = [102]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': '233672812873a10cc867036bf9695032b9357169abf2052974818118bbf7e4da'},
 {'id': 'wrong-call-result-variable',
  'source': 'dynamic-reference-callee-owner-before-argument',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = REFERENCE n_result',
             'n_name* = [110]',
             'n_f* = [102]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.RESULT = VARIABLE n_name* z_init]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': 'c28e4655ad8cf00f63950601bb4606d3855a05a1c6014e3bc33398fd6563df88'},
 {'id': 'arbitrary-owning-known-string',
  'source': 'dynamic-reference-callee-owner-before-argument',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = REFERENCE n_result',
             'n_name* = [110]',
             'n_f* = [102]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.RESULT = KNOWN (PSTRING n_f*)]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': '91d7a91aa3cd844dcb11b69e5846cc059c28ca9018bf112b718229212eb4ae9c'},
 {'id': 'arbitrary-owning-known-integer',
  'source': 'dynamic-reference-callee-owner-before-argument',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'S.RESULT = REFERENCE n_result',
             'n_name* = [110]',
             'n_f* = [102]',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.RESULT = KNOWN (PINT 99)]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = THROWN "Error" n_message* z_error'],
  'original_fixture_sha256': '7dded99fd65b411e3d9c33ecbfd9bc1c40d333e6d42e78363eb793c116af285b'},
 {'id': 'selected-control',
  'source': 'dynamic-reference-callee-owner-before-argument',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true\n'
            '  -- if S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* (porigin) z_call) :: '
            'ptask_tail*\n'
            '  -- if $dynamic_site(S, (porigin))\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* (porigin) z_call) :: ptask_tail*',
             'poperand* = eps',
             'S.RESULT = KNOWN PNULL',
             'n_kill* = [107,105,108,108]',
             '$call_target(S, n_kill*, eps) = (pfunction_other)',
             'pfunction_other.ORIGIN =/= porigin_function',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S',
             '$call_descriptors_valid(S_changed)',
             '$heap_valid($heap_graph(S_changed))',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': 'e36f771c6ca9e50a0eb9692f59eb5a831a8d68b0d2beef22f8b9a3221f0cc566'},
 {'id': 'arbitrary-selected-registered-function',
  'source': 'dynamic-reference-callee-owner-before-argument',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true\n'
            '  -- if S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* (porigin) z_call) :: '
            'ptask_tail*\n'
            '  -- if $dynamic_site(S, (porigin))\n'
            'def $review_stage(S) = false -- otherwise\n'
            'dec $review_find(pstate, nat) : pstate\n'
            'def $review_find(S, n) = S -- if $review_stage(S)\n'
            'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
            '  -- if ~$review_stage(S)\n'
            '  -- if $(n > 0)\n'
            '  -- if n_rest = $(n - 1)\n'
            '  -- if S_next = $drive_steps(S, 1)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* (porigin) z_call) :: ptask_tail*',
             'poperand* = eps',
             'S.RESULT = KNOWN PNULL',
             'n_kill* = [107,105,108,108]',
             '$call_target(S, n_kill*, eps) = (pfunction_other)',
             'pfunction_other.ORIGIN =/= porigin_function',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.TODO = (CALL_ARGS pfunction_other.ORIGIN phpType7* 0 poperand* (porigin) '
             'z_call) :: ptask_tail*]',
             '$call_descriptors_valid(S_changed)',
             '$heap_valid($heap_graph(S_changed))',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': '7ff37f8596fbf88298184ebdbce211f8a3ef2a0b1d4295bbaf4a330f00f3380f'},
 {'id': 'fixed-selected-control',
  'source': 'dynamic-fixed-constant-selected-target',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* '
            '(porigin) z_call) :: ptask_tail*\n'
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
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* (porigin) z_call) :: ptask_tail*',
             'poperand* = eps',
             'n_g* = [103]',
             '$call_target(S, n_g*, eps) = (pfunction_other)',
             'pfunction_other.ORIGIN =/= porigin_function',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S',
             '$call_descriptors_valid(S_changed)',
             '$heap_valid($heap_graph(S_changed))',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             '$outputs(S_full.EVENTS) = [49]'],
  'original_fixture_sha256': 'e649f7a01360f339b7c13a7ef11925d60975c1767a30c27494c9cdcded38964e'},
 {'id': 'wrong-fixed-selected-function',
  'source': 'dynamic-fixed-constant-selected-target',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* '
            '(porigin) z_call) :: ptask_tail*\n'
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
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_ARGS porigin_function phpType7* 0 poperand* (porigin) z_call) :: ptask_tail*',
             'poperand* = eps',
             'n_g* = [103]',
             '$call_target(S, n_g*, eps) = (pfunction_other)',
             'pfunction_other.ORIGIN =/= porigin_function',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.TODO = (CALL_ARGS pfunction_other.ORIGIN phpType7* 0 poperand* (porigin) '
             'z_call) :: ptask_tail*]',
             '$call_descriptors_valid(S_changed) = false',
             '$heap_valid($heap_graph(S_changed))',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': '28f91053dc6d4b0417c493d53aaf7b55946bdfe051736d39770b90fcbe68173a'},
 {'id': 'fixed-lookup-control',
  'source': 'dynamic-fixed-constant-selected-target',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
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
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n'
            '\n'
            'dec $review_name_match(pcodename, pcpath) : bool\n'
            'def $review_name_match(CODENAME pcpath n* n_fallback*?, pcpath) = true\n'
            'def $review_name_match(pcodename, pcpath) = false -- otherwise\n'
            'dec $review_name_rewrite(pcodename*, pcpath, preqbytes) : pcodename*\n'
            'def $review_name_rewrite(eps, pcpath, n*) = eps\n'
            'def $review_name_rewrite((CODENAME pcpath n_old* n_fallback*?) :: pcodename*, pcpath, n*) = '
            '(CODENAME pcpath n* eps) :: pcodename*\n'
            'def $review_name_rewrite(pcodename :: pcodename_tail*, pcpath, n*) = pcodename :: '
            '$review_name_rewrite(pcodename_tail*, pcpath, n*)\n'
            '  -- if ~$review_name_match(pcodename, pcpath)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'porigin = PORIGIN n_unit pcpath',
             'S.CODE = [pcode]',
             'n_fixed* = [102,49]',
             'n_g* = [103]',
             '$code_name(pcode.NAMES, pcpath) = ((n_fixed*, eps))',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             '$outputs(S_full.EVENTS) = [49]'],
  'original_fixture_sha256': '5d8c45d7a39a30ffa85ef7345bdc06a817c1ff2be241b876074bb932b4433776'},
 {'id': 'unused-owning-fixed-result',
  'source': 'dynamic-fixed-constant-selected-target',
  'valid': True,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
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
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n'
            '\n'
            'dec $review_name_match(pcodename, pcpath) : bool\n'
            'def $review_name_match(CODENAME pcpath n* n_fallback*?, pcpath) = true\n'
            'def $review_name_match(pcodename, pcpath) = false -- otherwise\n'
            'dec $review_name_rewrite(pcodename*, pcpath, preqbytes) : pcodename*\n'
            'def $review_name_rewrite(eps, pcpath, n*) = eps\n'
            'def $review_name_rewrite((CODENAME pcpath n_old* n_fallback*?) :: pcodename*, pcpath, n*) = '
            '(CODENAME pcpath n* eps) :: pcodename*\n'
            'def $review_name_rewrite(pcodename :: pcodename_tail*, pcpath, n*) = pcodename :: '
            '$review_name_rewrite(pcodename_tail*, pcpath, n*)\n'
            '  -- if ~$review_name_match(pcodename, pcpath)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'porigin = PORIGIN n_unit pcpath',
             'S.CODE = [pcode]',
             'n_fixed* = [102,49]',
             'n_g* = [103]',
             '$code_name(pcode.NAMES, pcpath) = ((n_fixed*, eps))',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'S_changed = S[.RESULT = KNOWN (PINT 99)]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = true',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET',
             'S_full = $drive(S_changed, 10000)',
             'S_full.COMPLETION = NORMAL',
             '$outputs(S_full.EVENTS) = [49]'],
  'original_fixture_sha256': '1d80a72a180b3dc1fa1861267dfb1f5d37c8f79e54faf9b137fff2d4c12fb0b6'},
 {'id': 'wrong-fixed-name-metadata',
  'source': 'dynamic-fixed-constant-selected-target',
  'valid': False,
  'prefix': 'dec $review_stage(pstate) : bool\n'
            'def $review_stage(S) = true -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*\n'
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
            'def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)\n'
            '\n'
            'dec $review_name_match(pcodename, pcpath) : bool\n'
            'def $review_name_match(CODENAME pcpath n* n_fallback*?, pcpath) = true\n'
            'def $review_name_match(pcodename, pcpath) = false -- otherwise\n'
            'dec $review_name_rewrite(pcodename*, pcpath, preqbytes) : pcodename*\n'
            'def $review_name_rewrite(eps, pcpath, n*) = eps\n'
            'def $review_name_rewrite((CODENAME pcpath n_old* n_fallback*?) :: pcodename*, pcpath, n*) = '
            '(CODENAME pcpath n* eps) :: pcodename*\n'
            'def $review_name_rewrite(pcodename :: pcodename_tail*, pcpath, n*) = pcodename :: '
            '$review_name_rewrite(pcodename_tail*, pcpath, n*)\n'
            '  -- if ~$review_name_match(pcodename, pcpath)\n'
            '\n',
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
             'S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*',
             'porigin = PORIGIN n_unit pcpath',
             'S.CODE = [pcode]',
             'n_fixed* = [102,49]',
             'n_g* = [103]',
             '$code_name(pcode.NAMES, pcpath) = ((n_fixed*, eps))',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'pcode_changed = pcode[.NAMES = $review_name_rewrite(pcode.NAMES, pcpath, n_g*)]',
             'pcode_values* = [pcode_changed]',
             'S_changed = S[.CODE = pcode_values*]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed) = false',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'],
  'original_fixture_sha256': '8ec4a4f94e249f2dce471c471e83bb8610c693668ef62bbf3d8b2c025436e857'}]

D=Path(tempfile.mkdtemp(prefix='dynamic-call-protocol-',dir=R/'.tools'))
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
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','scope':'Actual CALL_DYNAMIC source/class/init/call lines, fixed-name metadata and selected function relations. Arbitrary CV values, owning callee results and legitimate dynamic selected functions remain valid; fixed emitted names retain source relation. Three native contexts overlap source coverage, with one dedicated fixed-target control.','fingerprint':before,'raw':str(D),'sources':len(originals),'cases':len(records),'assertions':sum(r['assertions'] for r in records),'records':records}
(D/'report.json').write_text(json.dumps(report,indent=2));target=R/'coverage/semantics/dynamic-call-protocol.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2));assert report['result']=='pass'
