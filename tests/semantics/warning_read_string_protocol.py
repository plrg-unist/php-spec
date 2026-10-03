"""One selected method-string caller with an authentic saved borrowed read."""
from pathlib import Path
import argparse
import sys

from warning_read_protocol import PREFIX, GUARDS, FINISH
from warning_read_run import describe, inputs as base_inputs

SOURCE = Path(__file__).with_name('warning_read_string.php')
SOURCES = [('string-caller-borrow', SOURCE.read_bytes(), b'4;1:9:1', 'normal')]
CASES = [
    ('string-caller-saved-borrow', 'string-caller-borrow',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*', [
         'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
         'pargcall.KIND = INTRINSIC_FUNC_NUM_ARGS',
         '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.ARGC = 4',
         '$target_function(S, pcallcontext.TARGET) = (pfunction_handler)',
         'pfunction_handler.NAME = $ptascii("borrowStringWarning13")',
         'S.CVS = pfunction_handler.CVS', 'S.BORROWEDREAD = eps',
         'S.ERRORHANDLER.CALLBACK = eps',
         'S.FRAMES = [pframe_method,pframe_main]',
         'pframe_method.CONTEXT = (pcallcontext_method)',
         'pcallcontext_method.TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_requested porigin_method) pstringselection',
         'pcallcontext_method.ARGC = 1', 'pcallcontext_method.INSTANCE = eps',
         'pcallcontext_method.RECEIVER = eps',
         'pstringselection.REQUESTED = porigin_requested',
         'pstringselection.ORIGINAL = $ptascii("BorrowStringChild13::read")',
         '$string_site_valid(S, pstringselection, false)',
         '$string_target_identity(S, STATIC_METHOD_TARGET porigin_requested porigin_method, pstringselection)',
         '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
         'pmethoddesc.STATIC', 'pmethoddesc.OWNER =/= porigin_requested',
         'pcallcontext_method.LEXICAL_CLASS = (pmethoddesc.OWNER)',
         'pcallcontext_method.CALLED_CLASS = (porigin_requested)',
         '$target_function(S, pcallcontext_method.TARGET) = (pfunction_method)',
         'pcallcontext_method.FUNCTION = pfunction_method.ORIGIN',
         'pframe_method.LOCALS = (psymboltable_method)',
         'psymboltable_method.CVS = pfunction_method.CVS',
         'pframe_main.CONTEXT = eps', 'pframe_main.LOCALS = eps',
         'pframe_main.BORROWEDREAD = eps',
         'pframe_method.BORROWEDREAD = (pidentityread)',
         'pframe_method.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
         'perrorcall.RESUME = ERROR_IDENTITY_RESULT pidentityread',
         'pidentityread.OP = IDENTICAL', 'pidentityread.LEFT = $ptascii("left")',
         'pidentityread.RIGHT = $ptascii("missing")',
         '$lookup(psymboltable_method.ENV, $ptascii("left")) = (pidentityread.CELL)',
         'S.GLOBALTABLE = (psymboltable_main)',
         '$lookup(psymboltable_main.ENV, $ptascii("x")) = (pidentityread.CELL)',
         'S.STORE[pidentityread.CELL] = DEFINED PNULL',
         '$lookup(psymboltable_main.ENV, $ptascii("a")) = (n_other)',
         '$lookup(psymboltable_main.ENV, $ptascii("y")) = (n_other)',
         'n_other =/= pidentityread.CELL', 'S.STORE[n_other] = DEFINED (PINT 9)',
         '$heap_owners($heap_prune($heap_graph(S)), HCELL pidentityread.CELL) = 2',
         '~((HCELL pidentityread.CELL) <- $task_nodes(perrorcall.RESUME))',
         'S_caller = $set_active_table(S[.CURRENT = pframe_method.CONTEXT][.FRAMES = [pframe_main]][.ORIGIN = pframe_method.ORIGIN][.TODO = pframe_method.TODO][.BORROWEDREAD = pframe_method.BORROWEDREAD], psymboltable_method)',
         '$identity_read_valid(S_caller, pidentityread)',
         '$error_entered_call_valid(S_caller, perrorcall)',
         '$error_context_valid(S, pcallcontext)',
         '~$call_frames_valid(S, [pframe_method[.BORROWEDREAD = eps],pframe_main])',
         '~$call_frames_valid(S, [pframe_method[.TODO = (ERROR_HANDLER_RESULT perrorcall[.RESUME = ERROR_IDENTITY_RESULT pidentityread[.CELL = n_other]]) :: ptask_saved*],pframe_main])',
         '~$call_saved_context_valid(S, pframe_method[.CONTEXT = (pcallcontext_method[.TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_requested porigin_method) pstringselection[.REQUESTED = pmethoddesc.OWNER]])])',
         '~$call_frames_valid(S, [pframe_method[.LOCALS = (psymboltable_method[.CVS = eps])],pframe_main])',
         *GUARDS, *FINISH,
     ]),
]


def inputs():
    watched = base_inputs()
    for path in (Path(__file__).resolve(), SOURCE):
        watched[str(path)] = describe(path)
    return watched


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'run'))
    parser.add_argument('prepared', type=Path, nargs='?')
    args = parser.parse_args()
    if args.mode == 'prepare':
        assert args.prepared is None
        import warning_read_prepare as helper
    else:
        assert args.prepared is not None
        import warning_read_run as helper
        helper.SOURCE_CAP, helper.FINITE_CAP = 150, 330
        sys.argv = [sys.argv[0], str(args.prepared)]
    helper.SOURCES, helper.CASES, helper.inputs = SOURCES, CASES, inputs
    raise SystemExit(0 if helper.main() else 1)
