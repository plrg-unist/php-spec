#!/usr/bin/env python3
"""Callable-first reception retains the object and its live argument frames."""
import argument_introspection_calls_protocol as arguments
import callable_string_protocol as callable_parameters

PREFIX = arguments.PREFIX
SOURCE = (b'<?php class ArgCallable13{public function __invoke($a){'
          b'echo func_num_args(),":",func_get_arg(0),":",func_get_args()[0];}'
          b'public function __toString():string{echo "BAD";throw new Exception("wrong conversion");}}'
          b'function argaccept13(callable|string $value){echo func_num_args(),":",'
          b'func_get_arg(0)===$value?"same":"bad",";";$value(a:7);}'
          b'argaccept13(value:new ArgCallable13);')
EXPECTED = b"1:same;1:7:7"
SOURCES = {'callable-first-live-argument-views': {'source': SOURCE, 'expected_stdout': EXPECTED}}

CASES = [
    {
        'id': 'callable-first-receive-argument-object',
        'source_id': 'callable-first-live-argument-views',
        'stage': callable_parameters.STAGE,
        'checks': [
            *callable_parameters.RECEIVE,
            '~$typed_caller_strict(S)',
            'pcallcontext.ARGC = 1',
            'pcallcontext.PARAMS = [$ptascii("value")]',
            '$arginfo_values(S, pcallcontext) = [POBJECT n_receiver]',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.PARAMS = eps])])',
            *callable_parameters.ADMITTED,
            'S_done.TODO = eps',
            'S_done.FRAMES = eps',
            'S_done.TRACE = eps',
            '$outputs(S_done.EVENTS) = $ptascii("1:same;1:7:7")',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 1000)',
        ],
    },
    {
        'id': 'callable-first-source-invoke-saved-arguments',
        'source_id': 'callable-first-live-argument-views',
        'stage': ('S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*\n'
                  '  -- if S.CURRENT = (pcallcontext)\n'
                  '  -- if pcallcontext.RECEIVER = (n_receiver)'),
        'checks': [
            'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
            'pargcall.KIND = INTRINSIC_FUNC_NUM_ARGS',
            '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
            'pcallcontext.INSTANCE = eps',
            'pcallcontext.RECEIVER = (n_receiver)',
            'pcallcontext.ARGC = 1',
            'pcallcontext.PARAMS = [$ptascii("a")]',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
            'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
            '$target_function(S, pcallcontext.TARGET) = (pfunction)',
            'S.CVS = pfunction.CVS',
            '$lookup(S.ENV, $ptascii("a")) = (n_a)',
            'S.STORE[n_a] = DEFINED (PINT 7)',
            '$arginfo_values(S, pcallcontext) = [PINT 7]',
            '$task_nodes(ARGINFO_INVOKE pargcall) = eps',
            'S.FRAMES = pframe :: pframe_tail*',
            'pframe.CONTEXT = (pcallcontext_saved)',
            'pcallcontext_saved.NAME = $ptascii("argaccept13")',
            'pcallcontext_saved.ARGC = 1',
            'pcallcontext_saved.PARAMS = [$ptascii("value")]',
            '$function_at($all_functions(S), pcallcontext_saved.FUNCTION) = (pfunction_saved)',
            'pframe.LOCALS = (psymboltable)',
            'psymboltable.CVS = pfunction_saved.CVS',
            '$lookup(psymboltable.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (POBJECT n_receiver)',
            '$call_saved_context_valid(S, pframe)',
            'S_saved = S[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO][.ENV = psymboltable.ENV][.CVS = psymboltable.CVS][.SYMBOLS = psymboltable.SYMBOLS]',
            '$arginfo_values(S_saved, pcallcontext_saved) = [POBJECT n_receiver]',
            '$typed_callable(S, POBJECT n_receiver) = (true)',
            '$stringable_instance(S, n_receiver)',
            '$outputs(S.EVENTS) = $ptascii("1:same;")',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (n_receiver)])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.RECEIVER = eps])])',
            '~$call_saved_context_valid(S, pframe[.LOCALS = (psymboltable[.CVS = eps])])',
            '~$call_descriptors_valid(S[.FRAMES = pframe[.CONTEXT = (pcallcontext_saved[.PARAMS = eps])] :: pframe_tail*])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.LINE = 999])',
            *arguments.GUARDS,
            *arguments.FINISH,
            '$outputs(S_done.EVENTS) = $ptascii("1:same;1:7:7")',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
]
