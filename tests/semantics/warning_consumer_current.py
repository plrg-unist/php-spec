"""Actual cached handler and static reference prior through array-copy redirect."""
from pathlib import Path
from warning_consumer_protocol import GUARDS, FINISH, PREFIX as BASE_PREFIX

PREFIX = BASE_PREFIX + '''
dec $current_is_send(ptask) : bool
def $current_is_send(CALL_SEND pcalltarget phpType7* n poperand* porigin? z) = true
def $current_is_send(ptask) = false -- otherwise
dec $current_send(ptask*) : ptask?
def $current_send((CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*) = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z)
def $current_send(ptask :: ptask_tail*) = $current_send(ptask_tail*) -- if ~$current_is_send(ptask)
def $current_send(eps) = eps
'''

SOURCE = (Path(__file__).with_name('warning_consumer_current.php')).read_bytes()
EXPECTED = b'H4;S2:9:N;5:7:1'
ID = 'static-reference-prior-array-copy-cache-handler'
STAGE = 'S.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail* -- if perrorread.ORIGINAL = VALUE_COPY z'
CHECKS = [
    'S.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
    'S.CURRENT = eps', 'S.FRAMES = eps', 'S.BORROWEDREAD = eps',
    'S.ORIGIN = (porigin_copy)',
    'perrorread.ORIGINAL = VALUE_COPY z', 'perrorread.TASK = perrorread.ORIGINAL',
    'perrorread.INPUT = VARIABLE $ptascii("missing213") z_variable',
    'perrorread.NAME = $ptascii("missing213")', 'perrorread.RESULT = KNOWN PNULL',
    'perrorread.LINE = z',
    '$error_read_valid(S, perrorread)',
    '$call_task_valid(S, ERROR_READ_RESULT perrorread)',
    '$origin_node(S.SOURCES, porigin_copy) = (NExprTernary expression_cond expression_left expression_right metadata)',
    '$compiled_read(S, porigin_copy) = eps',
    '$compiled_redirect(S, porigin_copy) = ((porigin_left, expression_left, false, z_parent))',
    '$origin_child(S.ORIGIN, [PCFIELD 1]) = (porigin_left)',
    '$compiled_copy_redirect(S, porigin_copy) = (z)',
    '$error_copy_selected(S, porigin_copy, [PCFIELD 1])',
    '~$error_copy_selected(S, porigin_copy, [PCFIELD 2])',
    '$current_send(ptask_tail*) = (CALL_SEND pcalltarget eps 1 ([REFERENCE n_cell]) (porigin_call) z_call)',
    '$target_function(S, pcalltarget) = (pfunction_sink)',
    'pfunction_sink.NAME = $ptascii("sink213")',
    '$call_task_valid(S, CALL_SEND pcalltarget eps 1 ([REFERENCE n_cell]) (porigin_call) z_call)',
    '$call_parameter_reference(S, pcalltarget, 0)',
    '~$call_parameter_reference(S, pcalltarget, 1)',
    'S.CLASSSTATICS = [pclassstatic]',
    'pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)',
    'S.STORE[n_cell] = DEFINED (PINT 9)',
    'n_cell <- S.REFCELLS',
    '$propref_at(S.PROPREFS, n_cell) = (ppropref)',
    'ppropref.SOURCES =/= eps',
    '$heap_owners($heap_graph(S), HCELL n_cell) = 2',
    '$lookup(S.ENV, $ptascii("missing213")) = (n_missing)',
    'S.STORE[n_missing] = DEFINED (PINT 7)',
    '$lookup(S.ENV, $ptascii("right213")) = (n_right)',
    'S.STORE[n_right] = DEFINED (PINT 8)',
    'S.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
    'S.ERRORHANDLER.LEVELS = 2',
    '$constant_callable_record(S.CONSTANTCLOSURES, n_handler) = (pconstantclosure)',
    'S.OBJECTS[n_handler] = CONSTANTCLOSURE pconstantclosure.SITE (REALCLOSURE pconstantclosure.SITE eps pstaticcell*)',
    '$constant_callable_record_valid(S, pconstantclosure)',
    '$default_cache_at(S.CLASSCONSTANTCACHE, pconstantclosure.DECL) = (pdefaultcache)',
    'pdefaultcache.VALUE = POBJECT n_handler',
    '(HOBJECT n_handler) <- $class_constant_roots(S.CLASSCONSTANTCACHE)',
    '$heap_owners($heap_graph(S), HOBJECT n_handler) = 2',
    'S.CLASSCONSTANTINIT = eps', 'S.CONSTCONTEXT = eps',
    '~$error_read_valid(S, perrorread[.RESULT = KNOWN (PINT 7)])',
    '~$error_read_valid(S, perrorread[.NAME = $ptascii("right213")][.INPUT = VARIABLE $ptascii("right213") z_variable])',
    '~$error_read_valid(S[.ORIGIN = (porigin_left)], perrorread)',
    '~$error_read_valid(S, perrorread[.LINE = 999])',
    '~$constant_callable_record_valid(S, pconstantclosure[.SITE = porigin_left])',
    'PhpStep: S ~> S_resume', 'S_resume.COMPLETION = NORMAL',
    'S_resume.RESULT = KNOWN PNULL', 'S_resume.TODO = perrorread.TASK :: ptask_tail*',
    'S_resume.STORE[n_missing] = DEFINED (PINT 7)',
    'S_resume.STORE[n_cell] = DEFINED (PINT 9)',
    'PhpStep: S_resume ~> S_copy', 'S_copy.COMPLETION = NORMAL',
    'S_copy.RESULT = KNOWN PNULL', 'S_copy.TODO = ptask_tail*',
    '$heap_valid($heap_graph(S_copy))',
    *GUARDS, *FINISH,
    'S_done.STORE[n_cell] = DEFINED (PINT 5)',
    '$heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
    'S_done.STORE[n_missing] = DEFINED (PINT 7)',
    '$default_cache_at(S_done.CLASSCONSTANTCACHE, pconstantclosure.DECL) = (pdefaultcache)',
    '$heap_owners($heap_graph(S_done), HOBJECT n_handler) = 1',
    '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
    '$class_constant_state_valid(S_done)',
]
SOURCES = [(ID, SOURCE, EXPECTED, 'normal')]
CASES = [('static-prior-copy-redirect-cache-roots', ID, STAGE, CHECKS)]
