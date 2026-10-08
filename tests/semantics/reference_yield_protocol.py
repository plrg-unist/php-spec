#!/usr/bin/env python3
"""Real reference-cache acquisition, callback retirement and alias close owners."""
import os

import generator_force_close_protocol as driver
import reference_yield_prepare as author
import reference_yield_review as source

CASES = {
    'key-cache-retirement': source.CASES['key-warning-reference-overwrite-retires-payload-immediately'],
    'alias-frame-close': source.CASES['foreach-alias-keeps-payload-after-generator-frame-close'],
    'literal-notice-cache-wrapper': source.CASES['literal-yield-notice-then-foreach-wraps-only-cache'],
    'literal-notice-throw-cache': source.CASES['literal-notice-throw-skips-body-and-suppresses-key-warning'],
    'ordinary-retired-key': source.CASES['ordinary-previous-key-during-new-key-warning'],
    'reference-retired-key': source.CASES['reference-previous-key-during-new-key-warning'],
    'ordinary-retired-value': source.CASES['ordinary-previous-value-during-new-value-warning'],
    'notice-retval-borrow': author.CASES['handler-retval-retirement-keeps-key-and-notice-ingress'],
}
WATCHED = driver.source.WATCHED + [
    'spec/semantics/97-call-reference-acquisition.watsup',
    'spec/semantics/99-reference-returns.watsup',
    'spec/semantics/118-arrows.watsup',
    'spec/semantics/207-error-handler-runtime.watsup',
    'spec/semantics/243-file-warning-continuations.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/296-weak-references.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'spec/semantics/321-yield-key-warning.watsup',
    'spec/semantics/328-generator-reference-yields.watsup',
    'tests/semantics/reference_yield_review.py',
    'tests/semantics/reference_yield_prepare.py',
    'tests/semantics/reference_yield_protocol.py',
]
PREFIX = r'''
dec $reference_yield_remove(nat*,nat) : nat*
def $reference_yield_remove(eps,n) = eps
def $reference_yield_remove(n :: n_tail*,n) = n_tail*
def $reference_yield_remove(n_head :: n_tail*,n) = n_head :: $reference_yield_remove(n_tail*,n)
  -- if n_head =/= n
dec $reference_yield_phase(pstate,nat) : bool
def $reference_yield_phase(S,0) = true
  -- if S.TODO = (GENERATOR_YIELD_KEY n porigin z) :: ptask*
def $reference_yield_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_current_call(S,pcallcontext) = (perrorcall)
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $trace_slot(S,psymboltable.ENV,$ptascii("value")) = PNULL
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask*
  -- if $close_outputs(S.EVENTS) = $ptascii("C|W5|P|")
def $reference_yield_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.REFCELL =/= eps
def $reference_yield_phase(S,3) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask*
  -- if $trace_slot(S,S.ENV,$ptascii("generator")) = POBJECT n
  -- if $trace_slot(S,S.ENV,$ptascii("alias")) = POBJECT n_payload
  -- if S.ITERATORS = eps
def $reference_yield_phase(S,4) = true
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.STAGE = CLOSE_BODY porigin
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("give")
def $reference_yield_phase(S,5) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask*
  -- if $trace_slot(S,S.ENV,$ptascii("alias")) = POBJECT n_payload
  -- if $close_outputs(S.EVENTS) = $ptascii("A|1|F|")
def $reference_yield_phase(S,6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n porigin poperand? pvalue z
def $reference_yield_phase(S,7) = true
  -- if S.TODO = (GENERATOR_YIELD_REF_NOTICE n porigin poperand? pvalue z) :: ptask*
def $reference_yield_phase(S,8) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask*
  -- if $trace_slot(S,S.ENV,$ptascii("alias")) = PINT 5
  -- if $close_outputs(S.EVENTS) = $ptascii("C|N8:3|")
def $reference_yield_phase(S,9) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
  -- if $throwable_field(S,n,"message") = PSTRING $ptascii("notice")
def $reference_yield_phase(S,10) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED /\ pgenerator.KEY = (PNULL)
def $reference_yield_phase(S,11) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin eps
  -- if $close_outputs(S.EVENTS) = $ptascii("C|1:8|")
def $reference_yield_phase(S,12) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n porigin poperand? (PINT 5) z
  -- if $close_outputs(S.EVENTS) = $ptascii("C|W2|D:4|4|")
def $reference_yield_phase(S,13) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = pdestructionjob :: pdestructionjob_tail*
  -- if $generator_reference_cleanup(S,S.TODO) = (perrorcall)
  -- if perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n porigin poperand? (PINT 5) z
  -- if $close_outputs(S.EVENTS) = $ptascii("C|W2|D:4|4|W8|")
def $reference_yield_phase(S,14) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall
  -- if perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n porigin poperand? (PINT 5) z
  -- if $close_outputs(S.EVENTS) = $ptascii("C|W2|D:4|4|W8|D")
def $reference_yield_phase(S,n) = false -- otherwise
dec $reference_yield_seek(pstate,nat,nat) : pstate
def $reference_yield_seek(S,n_phase,n) = S -- if $reference_yield_phase(S,n_phase)
def $reference_yield_seek(S,n_phase,n) = S
  -- if ~$reference_yield_phase(S,n_phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $reference_yield_seek(S,n_phase,0) = S -- if ~$reference_yield_phase(S,n_phase)
def $reference_yield_seek(S,n_phase,n) = $reference_yield_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$reference_yield_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $reference_yield_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$reference_yield_phase({state},{phase})']


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})',
                                 f'$call_entry_check({state}) = {state}']


def cache_owner(state, record, generator, cell):
    return [f'{record}.VALUE = eps', f'{record}.REFCELL = ({cell})',
            f'{cell} <- {state}.REFCELLS', f'(HCELL {cell}) <- {state}.ALLOCATIONS',
            f'H_{state} = $heap_graph({state})',
            f'H_{state}_uncached = $heap_graph($generator_set({state},{generator},{record}[.REFCELL = eps]))',
            f'$heap_owners(H_{state},HCELL {cell}) = $($heap_owners(H_{state}_uncached,HCELL {cell}) + 1)']


def reject(checks, label, expression, original='S_key', same_heap=True):
    state = 'S_bad_' + label
    relation = '=' if same_heap else '=/='
    checks += [f'{state} = {expression}', f'$heap_graph({state}) {relation} $heap_graph({original})',
               f'$heap_valid($heap_graph({state}))', f'~$call_descriptors_valid({state})',
               f'$call_entry_check({state}).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']


def borrow(checks, state, record, generator, value, key):
    checks += [f'{record}.BORROWED = (pgeneratorborrowed_{state})',
               f'pgeneratorborrowed_{state}.VALUE = {value}',
               f'pgeneratorborrowed_{state}.KEY = ({key})',
               f'$generator_borrowed_node_valid({state},{generator})',
               f'$heap_graph($generator_set({state},{generator},{record}[.BORROWED = eps])) = $heap_graph({state})']


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name == 'key-cache-retirement':
        checks += seek('S_key', 'S_initial', 0) + valid('S_key')
        checks += r'''
S_key.TODO = (GENERATOR_YIELD_KEY n_generator porigin z) :: ptask_tail*
S_key.OBJECTS[n_generator] = GENERATOR pgenerator_key
pgenerator_key.PHASE = GENERATOR_RUNNING /\ pgenerator_key.KEY = eps
pgenerator_key.FRAME = eps /\ pgenerator_key.RETURN = eps /\ pgenerator_key.DELEGATE = eps
pgenerator_key.REFCELL = (n_cell)
S_key.STORE[n_cell] = DEFINED (POBJECT n_payload)
S_key.GLOBALTABLE = (psymboltable_key)
$lookup(psymboltable_key.ENV,$ptascii("value")) = (n_cell)
$lookup(S_key.ENV,$ptascii("value")) = (n_cell)
$trace_slot(S_key,psymboltable_key.ENV,$ptascii("weak")) = POBJECT n_weak
$weakref_get(S_key,n_weak) = POBJECT n_payload
$heap_owners($heap_graph(S_key),HOBJECT n_payload) = 1
$generator_cached_value(S_key,n_generator,false) = POBJECT n_payload
$generator_yield_key_read_valid(S_key,n_generator,porigin,z)
$generator_yield_key_node_valid(S_key,n_generator)
'''.strip().splitlines()
        checks += cache_owner('S_key', 'pgenerator_key', 'n_generator', 'n_cell')
        reject(checks, 'mixed', '$generator_set(S_key,n_generator,pgenerator_key[.VALUE = (PINT 17)])')
        reject(checks, 'unmarked', 'S_key[.REFCELLS = $reference_yield_remove(S_key.REFCELLS,n_cell)]')
        reject(checks, 'missing_cache', '$generator_set(S_key,n_generator,pgenerator_key[.REFCELL = eps])', same_heap=False)
        checks += ['$heap_owners($heap_graph(S_key),HCELL n_cell) = $($heap_owners($heap_graph(S_bad_missing_cache),HCELL n_cell) + 1)']
        reject(checks, 'input', 'S_key[.RESULT = KNOWN (PINT 17)]')
        reject(checks, 'base', 'S_key[.BASE = BASE_VALUE (KNOWN (PINT 17))]')
        reject(checks, 'duplicate', 'S_key[.TODO = (GENERATOR_YIELD_KEY n_generator porigin z) :: S_key.TODO]')
        checks += seek('S_overwritten', 'S_key', 1) + valid('S_overwritten')
        checks += ['S_overwritten.OBJECTS[n_generator] = GENERATOR pgenerator_overwritten',
                   'pgenerator_overwritten.REFCELL = (n_cell)', 'pgenerator_overwritten.KEY = eps',
                   'S_overwritten.STORE[n_cell] = DEFINED PNULL',
                   '$generator_cached_value(S_overwritten,n_generator,false) = PNULL',
                   '$weakref_get(S_overwritten,n_weak) = PNULL',
                   '~((HOBJECT n_payload) <- S_overwritten.ALLOCATIONS)']
        previous = 'S_overwritten'
    elif name == 'alias-frame-close':
        checks += seek('S_paused', 'S_initial', 2) + valid('S_paused')
        checks += ['S_paused.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_paused*',
                   'n_generator = pgeneratorop.OBJECT',
                   'S_paused.OBJECTS[n_generator] = GENERATOR pgenerator_paused',
                   'pgenerator_paused.KEY = (PINT 0)',
                   'pgenerator_paused.REFCELL = (n_cell)',
                   'S_paused.STORE[n_cell] = DEFINED (POBJECT n_payload)']
        checks += cache_owner('S_paused', 'pgenerator_paused', 'n_generator', 'n_cell')
        checks += seek('S_alias', 'S_paused', 3) + valid('S_alias')
        checks += ['$lookup(S_alias.ENV,$ptascii("alias")) = (n_cell)',
                   '$heap_owners($heap_graph(S_alias),HCELL n_cell) = 3',
                   '$heap_owners($heap_graph(S_alias),HOBJECT n_payload) = 1']
        checks += seek('S_body', 'S_alias', 4) + valid('S_body')
        checks += driver.body_binding('S_body', 'give')
        checks += ['pgenclose_body.OBJECT = n_generator',
                   'pgenerator_body.REFCELL = (n_cell)',
                   'S_body.STORE[n_cell] = DEFINED (POBJECT n_payload)',
                   '$lookup(S_body.ENV,$ptascii("value")) = (n_cell)']
        checks += seek('S_closed', 'S_body', 5) + valid('S_closed')
        checks += ['~((HOBJECT n_generator) <- S_closed.ALLOCATIONS)',
                   '$heap_owners($heap_graph(S_closed),HCELL n_cell) = 1',
                   '$heap_owners($heap_graph(S_closed),HOBJECT n_payload) = 1',
                   '$lookup(S_closed.ENV,$ptascii("alias")) = (n_cell)']
        previous = 'S_closed'
    elif name in ['ordinary-retired-key', 'reference-retired-key']:
        checks += seek('S_key', 'S_initial', 0) + valid('S_key')
        checks += r'''
S_key.TODO = (GENERATOR_YIELD_KEY n_generator porigin z) :: ptask_tail*
S_key.OBJECTS[n_generator] = GENERATOR pgenerator_key
pgenerator_key.PHASE = GENERATOR_RUNNING /\ pgenerator_key.KEY = eps
pgenerator_key.INDEX = 8 /\ ~pgenerator_key.FIRST
$generator_cached_value(S_key,n_generator,true) = PINT 8
$generator_yield_key_read_valid(S_key,n_generator,porigin,z)
$generator_yield_key_node_valid(S_key,n_generator)
'''.strip().splitlines()
        borrow(checks, 'S_key', 'pgenerator_key', 'n_generator', 'eps', 'PINT 8')
        if name == 'ordinary-retired-key':
            checks += ['pgenerator_key.VALUE = (PINT 2)', 'pgenerator_key.REFCELL = eps',
                       '$generator_cached_value(S_key,n_generator,false) = PINT 2',
                       '$close_outputs(S_key.EVENTS) = $ptascii("C|1:8|")']
        else:
            checks += ['pgenerator_key.REFCELL = (n_cell)',
                       'S_key.STORE[n_cell] = DEFINED (PINT 4)',
                       '$generator_cached_value(S_key,n_generator,false) = PINT 4',
                       '$close_outputs(S_key.EVENTS) = $ptascii("C|4:8|")']
            checks += cache_owner('S_key', 'pgenerator_key', 'n_generator', 'n_cell')
        reject(checks, 'owned_key', '$generator_set(S_key,n_generator,pgenerator_key[.KEY = (PINT 8)])')
        reject(checks, 'key_carrier_duplicate', 'S_key[.TODO = (GENERATOR_YIELD_KEY n_generator porigin z) :: S_key.TODO]')
        checks += seek('S_replaced', 'S_key', 10) + valid('S_replaced')
        checks += ['S_replaced.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_replaced*',
                   'pgeneratorop.OBJECT = n_generator',
                   'S_replaced.OBJECTS[n_generator] = GENERATOR pgenerator_replaced',
                   'pgenerator_replaced.KEY = (PNULL)', 'pgenerator_replaced.INDEX = 8',
                   'pgenerator_replaced.BORROWED = eps',
                   '$generator_cached_value(S_replaced,n_generator,true) = PNULL']
        previous = 'S_replaced'
    elif name == 'ordinary-retired-value':
        checks += seek('S_warning', 'S_initial', 11) + valid('S_warning')
        checks += r'''
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning_tail*
perrorcall.RESUME = ERROR_READ_RESULT perrorread
perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin eps
perrorread.RESULT = KNOWN PNULL /\ perrorread.BASE = BASE_VALUE (KNOWN PNULL)
perrorread.NAME = $ptascii("missingValue") /\ perrorread.LINE = 3
S_warning.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
n_generator = pgeneratorop.OBJECT
S_warning.OBJECTS[n_generator] = GENERATOR pgenerator_warning
pgenerator_warning.PHASE = GENERATOR_RUNNING /\ ~pgenerator_warning.FIRST
pgenerator_warning.VALUE = eps /\ pgenerator_warning.REFCELL = eps /\ pgenerator_warning.KEY = eps
pgenerator_warning.INDEX = 8
$error_read_valid(S_warning,perrorread)
$error_call_valid(S_warning,perrorcall)
$generator_cache_present(S_warning,n_generator)
$generator_borrowed_readable(S_warning,n_generator,false)
$generator_borrowed_readable(S_warning,n_generator,true)
$generator_cached_value(S_warning,n_generator,false) = PINT 1
$generator_cached_value(S_warning,n_generator,true) = PINT 8
~$eval_wrapped_marker(ERROR_HANDLER_INVOKE perrorcall)
~$eval_wrapped_marker(ERROR_HANDLER_RESULT perrorcall)
$eval_wrapped_marker(ERROR_HANDLER_INVOKE perrorcall[.RESUME = FILE_WARNING_PHASE 0 0])
$eval_wrapped_marker(ERROR_HANDLER_RESULT perrorcall[.RESUME = FILE_WARNING_PHASE 0 0])
'''.strip().splitlines()
        borrow(checks, 'S_warning', 'pgenerator_warning', 'n_generator', '(KNOWN (PINT 1))', 'PINT 8')
        reject(checks, 'value_mixed', '$generator_set(S_warning,n_generator,pgenerator_warning[.VALUE = (PINT 1)])', 'S_warning')
        reject(checks, 'value_owned_key', '$generator_set(S_warning,n_generator,pgenerator_warning[.KEY = (PINT 8)])', 'S_warning')
        reject(checks, 'value_hidden', 'S_warning[.TODO = (CHOOSE ([ERROR_HANDLER_INVOKE perrorcall]) eps 3) :: ptask_warning_tail*]', 'S_warning')
        checks += ['~$generator_borrowed_node_valid(S_bad_value_hidden,n_generator)']
        previous = 'S_warning'
    elif name == 'notice-retval-borrow':
        checks += seek('S_notice', 'S_initial', 12) + valid('S_notice')
        checks += r'''
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice_tail*
perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 5) z
perrorcall.LEVEL = 8 /\ z = 4
S_notice.OBJECTS[n_generator] = GENERATOR pgenerator_notice
pgenerator_notice.PHASE = GENERATOR_RUNNING /\ ~pgenerator_notice.FIRST
pgenerator_notice.VALUE = eps /\ pgenerator_notice.REFCELL = eps /\ pgenerator_notice.KEY = eps
pgenerator_notice.INDEX = $(-1)
pgenerator_notice.BORROWED = (pgeneratorborrowed_notice)
pgeneratorborrowed_notice.VALUE = (REFERENCE n_cell)
pgeneratorborrowed_notice.KEY = (PNULL)
S_notice.STORE[n_cell] = DEFINED (PINT 4)
$generator_cached_value(S_notice,n_generator,false) = PINT 4
$generator_cached_value(S_notice,n_generator,true) = PNULL
$heap_owners($heap_graph(S_notice),HCELL n_cell) = 2
$error_call_valid(S_notice,perrorcall)
'''.strip().splitlines()
        borrow(checks, 'S_notice', 'pgenerator_notice', 'n_generator', '(REFERENCE n_cell)', 'PNULL')
        checks += seek('S_release', 'S_notice', 13) + valid('S_release')
        checks += r'''
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release*
$generator_reference_cleanup(S_release,S_release.TODO) = (perrorcall_release)
perrorcall_release.RESUME = GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 5) z
$destructor_release_valid(S_release,pdestructionrelease)
$error_cleanup_valid(S_release,perrorcall_release)
$generator_reference_notice_tasks(S_release.TODO) = [n_generator]
$generator_reference_notice_frames(S_release.FRAMES) = eps
S_release.OBJECTS[n_generator] = GENERATOR pgenerator_release
$heap_owners($heap_graph(S_release),HCELL n_cell) = 2
$generator_cached_value(S_release,n_generator,false) = PINT 4
'''.strip().splitlines()
        borrow(checks, 'S_release', 'pgenerator_release', 'n_generator', '(REFERENCE n_cell)', 'PNULL')
        reject(checks, 'cleanup_hidden', 'S_release[.TODO = (CHOOSE (S_release.TODO) eps z)]', 'S_release')
        checks += ['~$generator_borrowed_node_valid(S_bad_cleanup_hidden,n_generator)',
                   '$generator_reference_cleanup(S_bad_cleanup_hidden,S_bad_cleanup_hidden.TODO) = eps']
        reject(checks, 'cleanup_duplicate', 'S_release[.TODO = S_release.TODO ++ [GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 5) z]]', 'S_release')
        reject(checks, 'cleanup_mixed', '$generator_set(S_release,n_generator,pgenerator_release[.REFCELL = (n_cell)])', 'S_release', same_heap=False)
        checks += ['$heap_owners($heap_graph(S_bad_cleanup_mixed),HCELL n_cell) = $($heap_owners($heap_graph(S_release),HCELL n_cell) + 1)']
        checks += seek('S_destructor', 'S_release', 14) + valid('S_destructor')
        checks += r'''
S_destructor.CURRENT = (pcallcontext_destructor)
$destructor_context_call(pcallcontext_destructor,S_destructor.CURRENT,S_destructor.FRAMES) = (pdestructorcall)
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall_release
S_destructor.OBJECTS[n_generator] = GENERATOR pgenerator_destructor
S_destructor.STORE[n_cell] = DEFINED (PINT 4)
$heap_owners($heap_graph(S_destructor),HCELL n_cell) = 2
$generator_cached_value(S_destructor,n_generator,false) = PINT 4
$generator_borrowed_readable(S_destructor,n_generator,false)
'''.strip().splitlines()
        borrow(checks, 'S_destructor', 'pgenerator_destructor', 'n_generator', '(REFERENCE n_cell)', 'PNULL')
        checks += seek('S_replaced', 'S_destructor', 10) + valid('S_replaced')
        checks += ['S_replaced.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_replaced*',
                   'pgeneratorop.OBJECT = n_generator',
                   'S_replaced.OBJECTS[n_generator] = GENERATOR pgenerator_replaced',
                   'pgenerator_replaced.VALUE = (PINT 5)', 'pgenerator_replaced.REFCELL = eps',
                   'pgenerator_replaced.KEY = (PNULL)', 'pgenerator_replaced.BORROWED = eps',
                   '$generator_cached_value(S_replaced,n_generator,false) = PINT 5',
                   '$heap_owners($heap_graph(S_replaced),HCELL n_cell) = 2']
        previous = 'S_replaced'
    else:
        checks += seek('S_notice', 'S_initial', 6) + valid('S_notice')
        checks += r'''
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice_tail*
perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 5) z
perrorcall.LEVEL = 8 /\ perrorcall.LINE = 3 /\ z = 3
perrorcall.MESSAGE = $generator_reference_message()
perrorcall.EVENT = DIAGNOSTIC "Notice" ($generator_reference_message()) z
S_notice.OBJECTS[n_generator] = GENERATOR pgenerator_notice
pgenerator_notice.PHASE = GENERATOR_RUNNING
pgenerator_notice.VALUE = eps /\ pgenerator_notice.REFCELL = eps /\ pgenerator_notice.KEY = eps
$error_call_valid(S_notice,perrorcall)
$generator_reference_notice_tasks(S_notice.TODO) = [n_generator]
$generator_reference_notice_frames(S_notice.FRAMES) = eps
'''.strip().splitlines()
        resume = 'GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 17) z'
        reject(checks, 'payload', f'S_notice[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = {resume}]) :: ptask_notice_tail*]', 'S_notice')
        reject(checks, 'notice_line', 'S_notice[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.LINE = 4]) :: ptask_notice_tail*]', 'S_notice')
        reject(checks, 'notice_duplicate', 'S_notice[.TODO = (GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 5) z) :: S_notice.TODO]', 'S_notice')
        reject(checks, 'notice_hidden', 'S_notice[.TODO = S_notice.TODO ++ [CHOOSE ([GENERATOR_YIELD_REF_NOTICE n_generator porigin poperand_key? (PINT 5) z]) eps 3]]', 'S_notice')
        if name == 'literal-notice-cache-wrapper':
            checks += ['poperand_key? = eps']
            checks += seek('S_bare', 'S_notice', 7) + valid('S_bare')
            checks += ['S_bare.TODO = (GENERATOR_YIELD_REF_NOTICE n_generator porigin eps (PINT 5) z) :: ptask_bare_tail*',
                       'S_bare.RESULT = KNOWN PNULL', 'S_bare.BASE = BASE_VALUE (KNOWN PNULL)',
                       'S_bare.OBJECTS[n_generator] = GENERATOR pgenerator_bare',
                       r'pgenerator_bare.VALUE = eps /\ pgenerator_bare.REFCELL = eps /\ pgenerator_bare.KEY = eps']
            reject(checks, 'notice_input', 'S_bare[.RESULT = KNOWN (PINT 17)]', 'S_bare')
            reject(checks, 'notice_base', 'S_bare[.BASE = BASE_VALUE (KNOWN (PINT 17))]', 'S_bare')
            checks += seek('S_wrapped', 'S_bare', 8) + valid('S_wrapped')
            checks += ['$trace_slot(S_wrapped,S_wrapped.ENV,$ptascii("generator")) = POBJECT n_generator',
                       'S_wrapped.OBJECTS[n_generator] = GENERATOR pgenerator_wrapped',
                       'pgenerator_wrapped.PHASE = GENERATOR_PAUSED',
                       'pgenerator_wrapped.KEY = (PINT 0)', 'pgenerator_wrapped.REFCELL = (n_cell)',
                       '$lookup(S_wrapped.ENV,$ptascii("alias")) = (n_cell)',
                       'S_wrapped.STORE[n_cell] = DEFINED (PINT 5)',
                       '$heap_owners($heap_graph(S_wrapped),HCELL n_cell) = 2']
            checks += cache_owner('S_wrapped', 'pgenerator_wrapped', 'n_generator', 'n_cell')
            previous = 'S_wrapped'
        else:
            checks += ['poperand_key? = (poperand_present_key)', '$generator_yield_key_operand(S_notice,porigin) = (poperand_present_key)']
            checks += seek('S_catch', 'S_notice', 9) + valid('S_catch')
            checks += ['S_catch.TODO = (CATCH_BIND porigin_catch n_index n_throwable) :: ptask_catch_tail*',
                       '$trace_slot(S_catch,S_catch.ENV,$ptascii("error")) = POBJECT n_throwable',
                       'S_catch.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
                       'pgenerator_closed.PHASE = GENERATOR_CLOSED',
                       r'pgenerator_closed.FRAME = eps /\ pgenerator_closed.REFCELL = eps',
                       r'pgenerator_closed.VALUE = (PINT 5) /\ pgenerator_closed.KEY = (PNULL)',
                       '$close_outputs(S_catch.EVENTS) = $ptascii("C|N8:3|")']
            previous = 'S_catch'
    checks += [f'S_stopped = $drive_steps({previous},0)',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name in ['key-cache-retirement', 'alias-frame-close']:
        checks += ['~((HOBJECT n_payload) <- S_resumed.ALLOCATIONS)']
    if name == 'alias-frame-close':
        checks += ['~((HCELL n_cell) <- S_resumed.ALLOCATIONS)']
    elif name == 'literal-notice-cache-wrapper':
        checks += ['S_resumed.STORE[n_cell] = DEFINED (PINT 8)',
                   '$heap_owners($heap_graph(S_resumed),HCELL n_cell) = 1']
    return checks


def main():
    driver.CASES = CASES
    driver.PREFIX += PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
