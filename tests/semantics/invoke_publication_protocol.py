#!/usr/bin/env python3
"""Source-derived __invoke compiler order and retained-callee witnesses."""
from pathlib import Path
import hashlib
import json
import tempfile

import closure_call_protocol as protocol
import compiler_publication_protocol as compiler
import source_invoke_protocol as invocation

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('invoke_publication_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())}

CASES = {
    'public-and-private-lookup-policy': invocation.CASES['public-descriptor-and-selected-task'],
    'private-selected-callee-survives-argument-replacement': {
        'source': SOURCES['private-selected-receiver-before-argument-replacement'],
        'stage': ('S.TODO = (CALL_SEND (METHOD_TARGET n_receiver porigin_method) '
                  'phpType7* 0 eps (porigin_site) z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PINT 3)'),
        'checks': [
            'n_receiver = 0',
            '$lookup(S.ENV, $ptascii("o")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_replacement)',
            'n_replacement =/= n_receiver',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '(HOBJECT n_replacement) <- S.ALLOCATIONS',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
            'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
            '$typed_callable(S, POBJECT n_receiver) = (true)',
            '$target_nodes(METHOD_TARGET n_receiver porigin_method) = [HOBJECT n_receiver]',
            '$call_task_valid(S, CALL_SEND (METHOD_TARGET n_receiver porigin_method) phpType7* 0 eps (porigin_site) z)',
            '~$call_task_valid(S, CALL_SEND (STATIC_METHOD_TARGET pmethoddesc.OWNER porigin_method) phpType7* 0 eps (porigin_site) z)',
            '~$call_task_valid(S, CALL_SEND (METHOD_TARGET n_receiver porigin_method) phpType7* 0 eps (porigin_method) z)',
            '~$call_task_valid(S, CALL_SEND (METHOD_TARGET n_receiver porigin_method) phpType7* 0 eps (porigin_site) $(z + 100))',
            '$call_descriptors_valid(S)', '$class_state_valid(S)',
            '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
            'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("The magic method Hidden::__invoke() must have public visibility")) 1, OUTPUT ($ptascii("W")), OUTPUT ($ptascii("1")), OUTPUT ($ptascii("3")), OUTPUT ($ptascii("|")), OUTPUT ($ptascii("2"))]',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '(HOBJECT n_replacement) <- S_done.ALLOCATIONS',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
            '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        ],
    },
}

VISIBILITY_MESSAGE = 'The magic method Hidden::__invoke() must have public visibility'
STATIC_MESSAGE = 'Method Invalid::__invoke() cannot be static'
FINAL_MESSAGE = 'Private methods cannot be final as they are never overridden by other classes'

CASES['strict-user-truth-warning-private-object-receive'] = {
    "source": SOURCES['strict-user-truth-warning-private-object-receive'],
    "stage": 'S.TODO = [TYPE_RECEIVE porigin_method 0] -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
    "checks": [
        '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
        '~pmethoddesc.STATIC /\\ ~pmethoddesc.ABSTRACT',
        '$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)',
        'pclassdesc_owner.NAME = $ptascii("Owner")',
        'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
        '$class_at(S.CLASSES, porigin_called) = (pclassdesc_child)',
        'pclassdesc_child.NAME = $ptascii("Child")',
        'pmethoddesc.OWNER =/= porigin_called',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.CALLED_CLASS = (porigin_called)',
        'pcallcontext.RECEIVER = (n_receiver)',
        'pcallcontext.ARGC = 4',
        '$function_at($all_functions(S), porigin_method) = (pfunction)',
        'pfunction.SIGNATURE.PARAMETERS[0].NAME = $ptascii("level")',
        '$lookup(S.ENV, $ptascii("level")) = (n_level)',
        'S.STORE[n_level] = DEFINED (PINT 2)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.CONTEXT = eps',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
        'perrorcall.CALLBACK = POBJECT n_receiver',
        'perrorcall.TARGET = (pcallcontext.TARGET)',
        'perrorcall.LEVEL = 2',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorread.NAME = $ptascii("missing")',
        'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing',
        'perrorread.RESULT = KNOWN PNULL',
        'perrorread.ORIGINAL = CHOOSE ptask_true* ptask_false* z_choose',
        'perrorread.TASK = perrorread.ORIGINAL',
        'perrorread.LINE = z_choose',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.LINE = perrorread.LINE',
        'pcallcontext.CALLSITE = (perrorcall.SITE)',
        'pcallcontext.LINE = perrorcall.LINE',
        '$arginfo_values(S, pcallcontext) = [PINT 2, PSTRING perrorcall.MESSAGE, PSTRING ptbytes_file, PINT perrorcall.LINE]',
        'S_emitter = S[.CURRENT = pframe.CONTEXT][.FRAMES = pframe_tail*][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO][.BORROWEDREAD = pframe.BORROWEDREAD]',
        '$error_read_valid(S_emitter, perrorread)',
        '$error_entered_call_valid(S_emitter, perrorcall)',
        '$error_context_valid(S, pcallcontext)',
        'S.ERRORHANDLER.CALLBACK = eps',
        'S.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV, $ptascii("receiver")) = (n_old_receiver)',
        'S.STORE[n_old_receiver] = DEFINED PNULL',
        'HOBJECT n_receiver <- S.ALLOCATIONS',
        'HOBJECT n_receiver <- $task_nodes(ERROR_HANDLER_RESULT perrorcall)',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_receiver]',
        '$typed_callable(S, POBJECT n_receiver) = (true)',
        '~$method_accessible(S, pmethoddesc, eps)',
        '$typed_caller_strict(S)',
        '~$error_context_direct_trigger(S)',
        '$typed_parameter_conversion(S, pfunction.SIGNATURE.PARAMETERS[0], PINT 2) = TYPEREJECT',
        '$call_descriptors_valid(S)',
        '$class_state_valid(S)',
        '$heap_valid($heap_graph(S))',
        '~$error_read_valid(S_emitter, perrorread[.NAME = $ptascii("other")])',
        '~$error_entered_call_valid(S_emitter, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_context_valid(S, pcallcontext[.CALLED_CLASS = (pmethoddesc.OWNER)])',
        '~$error_context_valid(S, pcallcontext[.RECEIVER = eps])',
        '~$call_descriptors_valid(S[.TODO = [TYPE_RECEIVE porigin_method 99]])',
        '~$call_descriptors_valid(S[.TODO = [TYPE_RECEIVE porigin_method 0, DISCARD]])',
        'PhpStep: S ~> S_one',
        'S_one.COMPLETION = THROWN "TypeError" n_message* z_error',
        'S_one.STORE = S.STORE',
        'S_one.EVENTS = S.EVENTS',
        'S_one.ALLOCATIONS = S.ALLOCATIONS',
        '$heap_valid($heap_graph(S_one))',
        'S_done = $drive(S_one, 5000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        'S_done.FRAMES = eps',
        'S_done.CURRENT = eps',
        'S_done.ERRORHANDLER.CALLBACK = eps',
        'S_done.ERRORHANDLERS = eps',
        'S_done.BORROWEDREAD = eps',
        '~(HOBJECT n_receiver <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        'S_done.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("The magic method Owner::__invoke() must have public visibility")) 4, OUTPUT $ptascii("R")]',
    ],
}

COMPILER_CASES = {
    'unreached-nonpublic-warning-without-class-activation': {
        'source': SOURCES['unreached-private-class-still-publishes-warning'],
        'checks': [
            'P.COMPLETION = PPCNORMAL',
            'P.CLASSES = [pclassdesc]',
            'pclassdesc.NAME = $ptascii("Hidden")',
            'pclassdesc.METHODS = [pmethoddesc]',
            'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
            '~pmethoddesc.STATIC /\\ ~pmethoddesc.ABSTRACT',
            'P.DIAGNOSTICS = [PLDIAGNOSTIC "warning" "class-message" ([$ptascii("' + VISIBILITY_MESSAGE + '")]) pllocation]',
            'pllocation.LINE = 1',
            'P.PUBLICATIONS = eps',
            'S.COMPLETION = NORMAL',
            'S.CLASSES = [pclassdesc]',
            '$class_named(S.CLASSNAMES, $ptascii("hidden")) = eps',
            'S.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("' + VISIBILITY_MESSAGE + '")) 1]',
            '$declaration_history_valid(S)',
            '~$declaration_history_valid(S[.DECLARATIONS = eps])',
        ],
    },
    'static-private-fatal-without-visibility-warning': {
        'source': SOURCES['private-static-invoke-rejected-before-public-warning'],
        'checks': [
            'P.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii("' + STATIC_MESSAGE + '")) 1)',
            'P.DIAGNOSTICS = eps', 'P.CLASSES = eps', 'P.PUBLICATIONS = eps',
            'S.COMPLETION = STATICBYTES ($ptascii("' + STATIC_MESSAGE + '")) 1',
            'S.EVENTS = eps', 'S.CLASSES = eps', 'S.FUNCTIONS = eps',
            'S.CODE = [P.INSTALLED.CODE]', 'S.POOLS = [{UNIT 0, CONSTANTS P.INSTALLED.CONSTANTS}]', 'S.CLASSNAMES = eps',
            'S.DECLARATIONS = [PDENTER 0 eps z_reporting, PDEXIT 0 PCSCOMPILER]',
            '$declaration_history_valid(S)',
            '~$declaration_history_valid(S[.DECLARATIONS = eps])',
        ],
    },
    'static-private-final-keeps-prior-diagnostic': {
        'source': SOURCES['private-final-static-invoke-keeps-earlier-final-warning'],
        'checks': [
            'P.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii("' + STATIC_MESSAGE + '")) 1)',
            'P.DIAGNOSTICS = [PLDIAGNOSTIC "warning" "private-final-method" eps pllocation]',
            'pllocation.LINE = 1', 'P.CLASSES = eps', 'P.PUBLICATIONS = eps',
            'S.COMPLETION = STATICBYTES ($ptascii("' + STATIC_MESSAGE + '")) 1',
            'S.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("' + FINAL_MESSAGE + '")) 1]',
            'S.CLASSES = eps', 'S.FUNCTIONS = eps', 'S.CODE = [P.INSTALLED.CODE]',
            '$declaration_history_valid(S)',
        ],
    },
    'body-rejection-before-static-and-visibility-checks': {
        'source': '<?php echo "before";if(false){class Invalid{protected static function __invoke(){break;}}}echo "after";',
        'checks': [
            'P.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii("\'break\' not in the \'loop\' or \'switch\' context")) 1)',
            'P.DIAGNOSTICS = eps', 'P.CLASSES = eps', 'P.PUBLICATIONS = eps',
            'S.COMPLETION = STATICBYTES ($ptascii("\'break\' not in the \'loop\' or \'switch\' context")) 1',
            'S.EVENTS = eps', 'S.CLASSES = eps', 'S.CODE = [P.INSTALLED.CODE]',
            '$declaration_history_valid(S)',
        ],
    },
}


def run_compiler(names=None):
    selected = COMPILER_CASES if names is None else {name: COMPILER_CASES[name] for name in names}
    rows = [dict(case, id=name, source_sha256=hashlib.sha256(case['source'].encode()).hexdigest())
            for name, case in selected.items()]
    output = Path(tempfile.mkdtemp(prefix='invoke-publication-compiler-selection-', dir=ROOT / '.tools'))
    compiler.CATALOGUE = output / 'cases.json'
    compiler.CATALOGUE.write_text(json.dumps({'cases': rows}, indent=2) + '\n')
    return compiler.run('')


if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(invocation.__file__)))
    raise SystemExit(0 if run_compiler() else 1)
