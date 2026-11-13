#!/usr/bin/env python3
"""Check CV-name NaN Isset guards with absent Get and abrupt receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_nan_cv_isset_reentry_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''


dec $nan_cv_review_dtor(pstate,nat) : bool
def $nan_cv_review_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $nan_cv_review_dtor(S,n) = false -- otherwise
dec $nan_cv_review_seek_dtor(pstate,nat,nat) : pstate
def $nan_cv_review_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_cv_review_seek_dtor(S,n_object,n) = S
  -- if $nan_cv_review_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_dtor(S,n_object,0) = S
  -- if ~$nan_cv_review_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_dtor(S,n_object,n) = $nan_cv_review_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nan_cv_review_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $nan_cv_review_catch(pstate) : bool
def $nan_cv_review_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $nan_cv_review_catch(S) = false -- otherwise
dec $nan_cv_review_seek_catch(pstate,nat) : pstate
def $nan_cv_review_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_cv_review_seek_catch(S,n) = S
  -- if $nan_cv_review_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_catch(S,0) = S
  -- if ~$nan_cv_review_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_catch(S,n) = $nan_cv_review_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nan_cv_review_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $nan_cv_review_name_stage(pstate,ptbytes) : bool
def $nan_cv_review_name_stage(S,ptbytes) = true
  -- if S.TODO = (PROPERTY_NAME (POBJECT n) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail*
  -- if $property_magic_cv_name(S,porigin,z) = (ptbytes)
def $nan_cv_review_name_stage(S,ptbytes) = false -- otherwise
dec $nan_cv_review_seek_name(pstate,ptbytes,nat) : pstate
def $nan_cv_review_seek_name(S,ptbytes,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_cv_review_seek_name(S,ptbytes,n) = S -- if $nan_cv_review_name_stage(S,ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_name(S,ptbytes,0) = S -- if ~$nan_cv_review_name_stage(S,ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_name(S,ptbytes,n) = $nan_cv_review_seek_name($drive_steps(S[.COMPLETION = NORMAL],1),ptbytes,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nan_cv_review_name_stage(S,ptbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $nan_cv_review_resume(pstate) : bool
def $nan_cv_review_resume(S) = true -- if S.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask_tail*
def $nan_cv_review_resume(S) = false -- otherwise
dec $nan_cv_review_seek_resume(pstate,nat) : pstate
def $nan_cv_review_seek_resume(S,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_cv_review_seek_resume(S,n) = S -- if $nan_cv_review_resume(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_resume(S,0) = S -- if ~$nan_cv_review_resume(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nan_cv_review_seek_resume(S,n) = $nan_cv_review_seek_resume($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nan_cv_review_resume(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $nan_cv_review_after(pstate,pstate) : pstate
def $nan_cv_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))
'''

CHECKS = ['z_other = 11 /\\ S.ORIGIN = (porigin_other)',
 'S.CURRENT = (pcallcontext_handler)',
 'S.FRAMES = [pframe_handler]',
 'pcallcontext_handler.TARGET = API_BORROWED_TARGET pshutdownproducer',
 'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_caller*',
 'perrorcall.RESUME = PROPERTY_EMPTY_NAN ppropertyemptynan',
 'ppropertyempty = ppropertyemptynan.EMPTY',
 'ppropertyempty.OBJECT = n_receiver /\\ ppropertyempty.NAME = $ptascii("value") /\\ ppropertyempty.LINE = 19 '
 '/\\ ppropertyempty.PROPERTY = eps',
 'ppropertyemptynan.FLOAT = 9221120237041090560 /\\ ppropertyemptynan.OWNER = 0 /\\ ppropertyemptynan.CALLER = '
 'eps /\\ ppropertyemptynan.TAIL = ptask_caller*',
 'S_caller = $constant_frame_scope(S,pframe_handler,eps)',
 '$property_empty_nan_valid(S_caller,ppropertyemptynan) /\\ $property_empty_valid(S_caller,ppropertyempty)',
 '~$property_empty_capture(S_caller,ppropertyempty)',
 '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
 'pfunction_get = pmethoddesc_get.FUNCTION',
 'pfunction_get.ORIGIN = ppropertyempty.GET /\\ pfunction_get.ENDLINE = 4',
 'pfunction_get.SIGNATURE.RETURNS = eps /\\ ~pfunction_get.SIGNATURE.BYREF /\\ ~pfunction_get.CODE.STRICT',
 '$class_at(S.CLASSES,pmethoddesc_get.OWNER) = (pclassdesc)',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\\ pclassdesc.PARENT = eps',
 'pfunction_get.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,pfunction_get.ORIGIN) = (NStmtClassMethod (SEQUENCE eps) (INTEGER 1) (BOOLEAN false) (NIdentifier (BYTES text_get) metadata_get) (SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parameter_type) metadata_type) (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_parameter_name) ABSENT (SEQUENCE eps) metadata_parameter])) ABSENT (SEQUENCE statement_get*) metadata_method)',
 'ptcontext = {NAMESPACE pfunction_get.ENV.NAMESPACE, IMPORTS pfunction_get.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc_get.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction_get.ORIGIN), LINE pfunction_get.LINE}',
 '$property_get_return_type_source(ABSENT,eps,ptcontext,true) /\\ '
 '$property_get_return_type_source(ABSENT,eps,ptcontext,false)',
 '$property_get_method_source(S,pmethoddesc_get,true) /\\ $property_empty_get_source(S,pmethoddesc_get)',
 '$property_quiet_get_source(S,pmethoddesc_get)',
 '$property_magic_cv_result_supported(S_caller,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PFLOAT '
 '9221120237041090560))',
 '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_other',
 '$string_bytes(pvalue_other) = ($ptascii("other"))',
 'n_reader <- S.REFCELLS /\\ n_selector <- S.REFCELLS',
 '$property_isset_plan(S) = (ppropertyisset_other)',
 'ppropertyisset_other.OBJECT = n_receiver /\\ ppropertyisset_other.NAME = $ptascii("other") /\\ '
 'ppropertyisset_other.SITE = porigin_other /\\ ppropertyisset_other.LINE = z_other',
 '$property_isset_capture(S,ppropertyisset_other) /\\ $property_isset_source(S,ppropertyisset_other)',
 '$property_empty_nan_guard(S,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_nan_guard(S,n_receiver,ppropertyisset_other.NAME)',
 '$task_nodes(PROPERTY_NAME (POBJECT n_receiver) z_other) = [HOBJECT n_receiver]',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 3',
 'S.EVENTS = [OUTPUT $ptascii("ISSET:"),OUTPUT $ptascii("value"),OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("GET;"),OUTPUT $ptascii("WARN;"),OUTPUT $ptascii("unexpected NAN value was coerced to bool"),OUTPUT '
 '$ptascii(";")]',
 '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
 'PhpStep: S ~> S_other_raw',
 'S_other_raw.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset_other) eps 1 ([KNOWN (PSTRING '
 '$ptascii("other"))]) (porigin_other) z_other) :: (PROPERTY_ISSET_RESULT ppropertyisset_other) :: '
 'ptask_other*',
 'S_other_raw.EVENTS = S.EVENTS /\\ S_other_raw.STORE = S.STORE',
 '$heap_owners($heap_graph(S_other_raw),HOBJECT n_receiver) = 3',
 '$property_empty_nan_guard(S_other_raw,n_receiver,ppropertyempty.NAME)',
 'S_same_found = $nan_cv_review_seek_name($nan_cv_review_after(S,S_other_raw),$ptascii("value"),2000)',
 'S_same_found.COMPLETION = NORMAL \\/ S_same_found.COMPLETION = BUDGET',
 'S_same = S_same_found[.COMPLETION = NORMAL]',
 'S_same.TODO = (PROPERTY_NAME (POBJECT n_receiver) 13) :: (ORIGIN_RETURN (porigin_same)) :: (ISSET_RESULT '
 'false 13) :: ptask_same*',
 'S_same.CURRENT = (pcallcontext_handler)',
 'S_same.FRAMES = [pframe_same]',
 'pframe_same.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_caller*',
 'S_same.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("value"))',
 'S_same.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\\ S_same.STORE[n_destination] = DEFINED (PINT 42)',
 '$property_isset_plan(S_same) = (ppropertyisset_same)',
 'ppropertyisset_same.SITE = porigin_same /\\ ppropertyisset_same.OBJECT = n_receiver /\\ '
 'ppropertyisset_same.NAME = ppropertyempty.NAME /\\ ppropertyisset_same.LINE = 13',
 '$property_isset_capture(S_same,ppropertyisset_same) /\\ $property_isset_source(S_same,ppropertyisset_same)',
 '$property_empty_nan_guard(S_same,n_receiver,ppropertyisset_same.NAME) /\\ '
 '~$property_empty_get_active(S_same,n_receiver,ppropertyempty.NAME)',
 '~$property_empty_nan_guard(S_same,n_receiver,$ptascii("other"))',
 '$property_isset_plan(S_same[.SOURCES = eps]) = eps /\\ ~$property_empty_nan_guard(S_same[.SOURCES = '
 'eps],n_receiver,ppropertyempty.NAME)',
 '$property_isset_plan(S_same[.ORIGIN = eps]) = eps',
 '$property_isset_plan(S_same[.TODO = (PROPERTY_NAME (POBJECT n_receiver) 14) :: (ORIGIN_RETURN '
 '(porigin_same)) :: (ISSET_RESULT false 14) :: ptask_same*]) = eps',
 '$property_isset_plan(S_same[.TODO = (PROPERTY_NAME (POBJECT n_receiver) 13) :: (ORIGIN_RETURN '
 '(porigin_same)) :: (ISSET_RESULT true 13) :: ptask_same*]) = eps',
 '~$property_isset_capture(S_same,ppropertyisset_same[.NAME = $ptascii("other")])',
 '$heap_owners($heap_graph(S_same),HOBJECT n_receiver) = 3',
 'S_same.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("ISSET:"),OUTPUT $ptascii("other"),OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("OTHER;")]',
 'PhpStep: S_same ~> S_guarded',
 'S_guarded = S_same[.TODO = ptask_same*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
 '$heap_owners($heap_graph(S_guarded),HOBJECT n_receiver) = 2',
 '$property_empty_nan_guard(S_guarded,n_receiver,ppropertyempty.NAME)',
 '$call_descriptors_valid(S_guarded) /\\ $heap_valid($heap_graph(S_guarded))',
 'S_zero = $drive_steps(S_same,0)',
 'S_zero = S_same[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one[.COMPLETION = NORMAL] = $nan_cv_review_after(S_same,S_guarded)',
 'S_resume_found = $nan_cv_review_seek_resume($nan_cv_review_after(S_same,S_guarded),2000)',
 'S_resume_found.COMPLETION = NORMAL \\/ S_resume_found.COMPLETION = BUDGET',
 'S_resume = S_resume_found[.COMPLETION = NORMAL]',
 'S_resume.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask_caller*',
 'S_resume.CURRENT = eps /\\ S_resume.FRAMES = eps /\\ S_resume.RESULT = KNOWN PNULL',
 'S_resume.STORE[n_reader] = DEFINED PNULL /\\ S_resume.STORE[n_destination] = DEFINED (PINT 42)',
 'S_resume.STORE[n_selector] = DEFINED pvalue_selector',
 'S_resume.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK) /\\ S_resume.ERRORHANDLER.LEVELS = '
 'S.ERRORHANDLER.LEVELS',
 '$property_empty_nan_valid(S_resume,ppropertyemptynan) /\\ ~$property_empty_capture(S_resume,ppropertyempty)',
 '$property_empty_nan_guard(S_resume,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_get_active(S_resume,n_receiver,ppropertyempty.NAME)',
 '$heap_owners($heap_graph(S_resume),HOBJECT n_receiver) = 1',
 'S_resume.EVENTS = S_same.EVENTS ++ [OUTPUT $ptascii("GUARD;")]',
 'PhpStep: S_resume ~> S_release',
 'S_release.TODO = ptask_caller* /\\ S_release.RESULT = KNOWN (PBOOL false) /\\ S_release.BASE = BASE_VALUE '
 '(KNOWN PNULL)',
 'S_release.STORE = S_resume.STORE /\\ S_release.EVENTS = S_resume.EVENTS',
 '$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 0',
 '~$property_empty_nan_guard(S_release,n_receiver,ppropertyempty.NAME)',
 'S_receiver_found = $nan_cv_review_seek_dtor(S_resume,n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = '
 '(pdestructorcall_receiver)',
 'pdestructorcall_receiver.OBJECT = n_receiver',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.SOURCE = PROPERTY_EMPTY_NAN ppropertyemptynan',
 'pdestructionoperation_receiver.VALUE = KNOWN (PBOOL false) /\\ pdestructionoperation_receiver.PENDING = eps',
 'S_receiver.EVENTS = S_resume.EVENTS',
 '~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertyempty.NAME)',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_catch_found = $nan_cv_review_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("receiver-cv-nan"))',
 '$throwable_field(S_catch,n_receiver_error,"previous") = PNULL',
 'S_catch.EVENTS = S_resume.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
 '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ ~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 'S_done.EVENTS = S_resume.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("receiver-cv-nan"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("NO_PREVIOUS;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT '
 '$ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42) /\\ '
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps',
 '~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S,4096) = S_done',
 '$drive_steps(S_same,4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done']

CASES = {
    'anonymous-nan-cv-isset-name-snapshot-and-pending-cleanup': {
        'source': ROW['source'],
        'stage': 'S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z_other) :: (ORIGIN_RETURN (porigin_other)) :: (ISSET_RESULT false z_other) :: ptask_other* -- if $property_magic_cv_name(S,porigin_other,z_other) = ($ptascii("other"))',
        'checks': CHECKS,
    },
}


def render(case, fixture, filename):
    stage = case['stage']
    text = (HELPERS + '\ndec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + stage + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate,nat) : pstate\n'
            'def $seek(S,n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'def $seek(S,n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) '
            '-- if $(n > 0) /\\ ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found = $seek(S_initial,2000)\n'
            '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            '  -- if S = S_found[.COMPLETION = NORMAL]\n'
            '  -- if ' + stage + '\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__),CATALOGUE),runner_flags=('--sl',),fixture_renderer=render)
