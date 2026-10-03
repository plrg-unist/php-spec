"""One current setter/borrowed-read interaction, using the fixed reliable runners."""
from pathlib import Path
import argparse
import sys

from warning_read_protocol import PREFIX, GUARDS, FINISH
from warning_read_run import describe, inputs as base_inputs

SOURCE = Path(__file__).with_name('warning_read_static_set.php')
SOURCES = [('static-set-borrow-frame', SOURCE.read_bytes(), b'1;0:9:9;blocked:9:1', 'normal')]
CASES = [
    ('static-setter-saved-borrow', 'static-set-borrow-frame',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*', [
         'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
         'pargcall.KIND = INTRINSIC_FUNC_NUM_ARGS',
         '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.ARGC = 1',
         'pcallcontext.INSTANCE = eps', 'pcallcontext.RECEIVER = eps',
         'pcallcontext.TARGET = SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector',
         '$target_function(S, pcallcontext.TARGET) = (pfunction)',
         'pcallcontext.NAME = pfunction.NAME', 'S.CVS = pfunction.CVS',
         'pcallcontext.LEXICAL_CLASS = (porigin_class)',
         '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
         'pclassdesc.PROPERTIES = [ppropertydesc]',
         'ppropertydesc.NAME = $ptascii("value")', 'ppropertydesc.STATIC',
         'ppropertydesc.VISIBILITY = PROPERTY_PUBLIC',
         'ppropertydesc.SETVISIBILITY = (PROPERTY_PRIVATE)', 'ppropertydesc.TYPE =/= eps',
         '$class_static_set_allowed(S, ppropertydesc)',
         '$class_static_at(S.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)',
         'S.BORROWEDREAD = eps', 'S.ERRORHANDLER.CALLBACK = eps',
         'S.FRAMES = [pframe_callback,pframe_main]',
         'pframe_callback.BORROWEDREAD = eps',
         'pframe_callback.CONTEXT = (pcallcontext_callback)',
         'pcallcontext_callback.NAME = $ptascii("warningBorrowSetter13")',
         'pcallcontext_callback.ARGC = 4', 'pcallcontext_callback.INSTANCE = eps',
         'pframe_main.CONTEXT = eps', 'pframe_main.LOCALS = eps',
         'pframe_main.BORROWEDREAD = (pidentityread)',
         'pframe_main.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
         'perrorcall.RESUME = ERROR_IDENTITY_RESULT pidentityread',
         'pidentityread.OP = IDENTICAL', 'pidentityread.LEFT = $ptascii("a")',
         'pidentityread.RIGHT = $ptascii("missing_allowed")',
         'pclassstatic.STATE = PROP_VALUE (ALIAS pidentityread.CELL)',
         'S.STORE[pidentityread.CELL] = DEFINED (PINT 9)',
         '$propref_source_present(S.PROPREFS, pidentityread.CELL, CLASS_PROP_SOURCE ppropertydesc.ORIGIN)',
         '$heap_owners($heap_prune($heap_graph(S)), HCELL pidentityread.CELL) = 3',
         '~((HCELL pidentityread.CELL) <- $task_nodes(perrorcall.RESUME))',
         '$class_statics_valid(S)', '$error_context_valid(S, pcallcontext_callback)',
         'S_caller = S[.CURRENT = eps][.FRAMES = eps][.ORIGIN = pframe_main.ORIGIN][.TODO = pframe_main.TODO][.BORROWEDREAD = pframe_main.BORROWEDREAD]',
         '$identity_read_valid(S_caller, pidentityread)', '$error_entered_call_valid(S_caller, perrorcall)',
         '~$call_frames_valid(S, [pframe_callback,pframe_main[.BORROWEDREAD = eps]])',
         '~$call_saved_context_valid(S, pframe_callback[.CONTEXT = (pcallcontext_callback[.ARGC = 0])])',
         '$lookup(S.ENV, $ptascii("value")) = (n_received)', 'n_received =/= pidentityread.CELL',
         '~$call_frames_valid(S, [pframe_callback,pframe_main[.TODO = (ERROR_HANDLER_RESULT perrorcall[.RESUME = ERROR_IDENTITY_RESULT pidentityread[.CELL = n_received]]) :: ptask_saved*]])',
         *GUARDS, *FINISH, '$class_statics_valid(S_done)',
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
