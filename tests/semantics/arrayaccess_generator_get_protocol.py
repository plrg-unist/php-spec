"""Source-reached implicit Generator Get ownership and resume controls."""
from error_handler_protocol import PREFIX

CASES = [
    ('creation-escape-and-paused-close', 'generator-get-escaped-key-and-receiver'),
    ('reference-yield-running-and-paused', 'generator-get-reference-yield-api-snapshot'),
]

EXTRA = r'''
dec $get_phase(pstate, nat) : bool
def $get_phase(S, 0) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $outputs(S.EVENTS) = $ptascii("A;")
  -- if $lookup(S.ENV, $ptascii("gen344")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
def $get_phase(S, 1) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.ACCESS =/= eps
def $get_phase(S, 2) = true
  -- if $generator_close_active(S)
  -- if S.CURRENT = (pcallcontext)
  -- if $access_context_kind(S, pcallcontext)
def $get_phase(S, 3) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.ACCESS =/= eps
def $get_phase(S, 4) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
  -- if pgenerator.ACCESS =/= eps
def $get_phase(S, 5) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_DONE pgenclose) :: ptask*
  -- if pgenclose.STAGE = CLOSE_FINISHED
  -- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.ACCESS =/= eps
def $get_phase(S, 6) = true
  -- if S.TODO = (ACCESS_RESULT paccess) :: ptask*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
  -- if pgenerator.ACCESS =/= eps
def $get_phase(S, n) = false -- otherwise
dec $get_seek(pstate, nat, nat) : pstate
def $get_seek(S, n_phase, n) = S
  -- if $get_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $get_seek(S, n_phase, n) = $get_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$get_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $get_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$generator_state_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def seek(state, previous, phase):
    return [f'{state}_reached = $get_seek({previous}, {phase}, 1500)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$get_phase({state}, {phase})']


def certificate_forgeries(state, generator, certificate, context, suffix, other=None):
    mutations = [('site', f'{certificate}[.SITE = PORIGIN 999 eps]'),
                 ('line', f'{certificate}[.LINE = $({certificate}.LINE + 1)]')]
    if other:
        mutations.append(('receiver', f'{certificate}[.TARGET = METHOD_TARGET {other} {context}.FUNCTION]'))
    checks = []
    for name, mutated in mutations:
        bad = 'S_bad_' + suffix + '_' + name
        checks += [f'{bad} = {state}[.OBJECTS[n_gen] = GENERATOR {generator}[.ACCESS = ({mutated})]]',
                   f'$heap_graph({bad}) = $heap_graph({state})',
                   f'$heap_valid($heap_graph({bad}))',
                   f'~$access_generator_context({bad}, {context})',
                   f'~$call_descriptors_valid({bad})']
    return checks


def creation_close():
    stage = 'S.TODO = (GENERATOR_CREATE porigin_method) :: ptask_tail*'
    checks = r'''
S.TODO = [GENERATOR_CREATE porigin_method]
S.CURRENT = (pcallcontext)
S.FRAMES = pframe_caller :: pframe_tail*
pframe_caller.TODO = (ACCESS_RESULT paccess) :: ptask_caller*
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
paccess.OBJECT = (n_box)
paccess.OFFSET = POBJECT n_key
~paccess.KEYHOLE
$context_target(pcallcontext) = METHOD_TARGET n_box porigin_method
pcallcontext.ARGC = 1
pcallcontext.HOLES = eps
pcallcontext.NAMED = eps
pcallcontext.WRAPPER = eps
$access_frame(S, pcallcontext, pframe_caller)
$access_generator_creation(S, pcallcontext)
$generator_creation_supported(S, pcallcontext)
$access_generator_capture(S, pcallcontext) = (pgeneratoraccess)
pgeneratoraccess.TARGET = $context_target(pcallcontext)
pgeneratoraccess.SITE = paccess.SITE
pgeneratoraccess.LINE = paccess.LINE
S_bad_live = S[.FRAMES = pframe_caller[.TODO = (ACCESS_RESULT paccess[.LINE = $(paccess.LINE + 1)]) :: ptask_caller*] :: pframe_tail*]
$heap_graph(S_bad_live) = $heap_graph(S)
~$access_generator_creation(S_bad_live, pcallcontext)
~$generator_creation_supported(S_bad_live, pcallcontext)
$access_generator_capture(S_bad_live, pcallcontext) = eps
$outputs(S.EVENTS) = eps
n_gen = |S.OBJECTS|
PhpStep: S ~> S_allocated
S_allocated.OBJECTS[n_gen] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
pgenerator.ACCESS = (pgeneratoraccess)
S_allocated.RESULT = KNOWN PNULL
S_allocated.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_creation) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_creation) :: (ACCESS_RESULT paccess) :: ptask_caller*
pdestructionframe_creation.VALUE = KNOWN (POBJECT n_gen)
'''.strip().splitlines() + guards('S') + guards('S_allocated')
    checks += seek('S_created', 'S_allocated', 6) + r'''
S_created.RESULT = KNOWN (POBJECT n_gen)
S_created.OBJECTS[n_gen] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
pgenerator.ACCESS = (pgeneratoraccess)
pgenerator.CLOSURE = eps
pgenerator.FRAME = (pframe_gen)
pframe_gen.CONTEXT = (pcallcontext)
pframe_gen.LOCALS = (psymboltable)
psymboltable.ENV = [BIND $ptascii("key") n_key_cell]
S_created.STORE[n_key_cell] = DEFINED (POBJECT n_key)
$node_children(S_created, HOBJECT n_gen) = [HCELL n_key_cell, HOBJECT n_box]
S_created.TODO = (ACCESS_RESULT paccess) :: ptask_caller*
S_created.CURRENT = pframe_caller.CONTEXT
$access_generator_record_valid(S_created, pgenerator)
S_view = $generator_frame_scope(S_created, pframe_gen)
$access_generator_context(S_view, pcallcontext)
$access_context(S_view, pcallcontext)
$access_chain(S_view, (pcallcontext), eps)
~$access_generator_creation(S_view, pcallcontext)
$lookup(S_created.ENV, $ptascii("other344")) = (n_other_cell)
S_created.STORE[n_other_cell] = DEFINED (POBJECT n_other)
n_other =/= n_box
S_created.OBJECTS[n_other] = S_created.OBJECTS[n_box]
(HOBJECT n_other) <- S_created.ALLOCATIONS
'''.strip().splitlines() + guards('S_created') + [
        # This saved-frame proof view has no operational caller frame.
        '$call_current_valid(S_view)',
        '$call_frames_valid(S_view, S_view.FRAMES)',
        '$call_tasks_valid(S_view, pframe_gen.TODO)',
        '$generator_frame_valid(S_created, pgenerator, pframe_gen)',
    ]
    checks += certificate_forgeries('S_created', 'pgenerator', 'pgeneratoraccess', 'pcallcontext', 'fresh', 'n_other')
    checks += seek('S_escape', 'S_created', 0) + r'''
S_escape.OBJECTS[n_gen] = GENERATOR pgenerator
$error_missing_operand(S_escape, VARIABLE $ptascii("key344") 0)
$error_missing_operand(S_escape, VARIABLE $ptascii("box344") 0)
$node_children(S_escape, HOBJECT n_gen) = [HCELL n_key_cell, HOBJECT n_box]
$heap_owners($heap_prune($heap_graph(S_escape)), HOBJECT n_key) = 1
$heap_owners($heap_prune($heap_graph(S_escape)), HOBJECT n_box) = 1
$access_generator_record_valid(S_escape, pgenerator)
'''.strip().splitlines() + guards('S_escape')
    checks += seek('S_close', 'S_escape', 1) + r'''
S_close.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_close*
pgenclose.OBJECT = n_gen
pgenclose.CONTEXT = pcallcontext
pgenclose.FRAME = (pframe_close)
S_close.OBJECTS[n_gen] = GENERATOR pgenerator_closing
pgenerator_closing.PHASE = GENERATOR_CLOSING
pgenerator_closing.FRAME = eps
pgenerator_closing.ACCESS = (pgeneratoraccess)
$generator_close_enter_valid(S_close, pgenclose)
$access_generator_context(S_close, pcallcontext)
$node_children(S_close, HOBJECT n_gen) = eps
$task_nodes(GENERATOR_CLOSE_ENTER pgenclose) = [HOBJECT n_gen] ++ $frames_roots([pframe_close])
$heap_owners($heap_prune($heap_graph(S_close)), HOBJECT n_key) = 1
$heap_owners($heap_prune($heap_graph(S_close)), HOBJECT n_box) = 1
$outputs(S_close.EVENTS) = $ptascii("A;C:G:1;7;U;")
'''.strip().splitlines() + guards('S_close')
    checks += seek('S_closing_body', 'S_close', 2) + r'''
S_closing_body.CURRENT = (pcallcontext)
S_closing_body.OBJECTS[n_gen] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pgenerator_running.ACCESS = (pgeneratoraccess)
$access_generator_context(S_closing_body, pcallcontext)
$access_context(S_closing_body, pcallcontext)
$access_chain(S_closing_body, S_closing_body.CURRENT, S_closing_body.FRAMES)
'''.strip().splitlines() + guards('S_closing_body')
    checks += certificate_forgeries('S_closing_body', 'pgenerator_running', 'pgeneratoraccess', 'pcallcontext', 'close', 'n_other')
    checks += seek('S_release', 'S_closing_body', 5) + r'''
S_release.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_frame) :: (GENERATOR_CLOSE_DONE pgenclose_done) :: ptask_release*
pgenrelease_frame.JOBS = [DESTRUCTION_VALUE (HOBJECT n_key), DESTRUCTION_VALUE (HOBJECT n_box)]
pgenrelease_frame.PENDING = eps
pgenclose_done.OBJECT = n_gen
pgenclose_done.CONTEXT = pcallcontext
pgenclose_done.STAGE = CLOSE_FINISHED
pgenclose_done.FRAME = eps
pgenclose_done.PENDING = eps
S_release.CURRENT = eps
S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
$destructor_operation_valid(S_release, pdestructionoperation)
S_release.OBJECTS[n_gen] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.ACCESS = (pgeneratoraccess)
$access_generator_close_valid(S_release, pgenclose_done)
$generator_close_done_valid(S_release, pgenclose_done)
$generator_close_destructor_ready(S_release, pgenrelease_frame)
~$access_generator_context(S_release, pcallcontext)
$outputs(S_release.EVENTS) = $ptascii("A;C:G:1;7;U;F;")
'''.strip().splitlines() + guards('S_release')
    done_mutations = [
        ('target', 'pgenclose_done[.CONTEXT = pcallcontext[.RECEIVER = (n_other)]]'),
        ('site', 'pgenclose_done[.CONTEXT = pcallcontext[.CALLSITE = (PORIGIN 999 eps)]]'),
        ('line', 'pgenclose_done[.CONTEXT = pcallcontext[.LINE = $(pcallcontext.LINE + 1)]]'),
        ('arity', 'pgenclose_done[.CONTEXT = pcallcontext[.ARGC = 0]]'),
        ('holes', 'pgenclose_done[.CONTEXT = pcallcontext[.HOLES = [0]]]'),
        ('extent', 'pgenclose_done[.CONTEXT = pcallcontext[.EXTRA = [KNOWN PNULL]]]'),
        ('stage', 'pgenclose_done[.STAGE = CLOSE_SCANNING]'),
        ('caller_site', 'pgenclose_done[.CALLSITE = (PORIGIN 999 eps)]'),
    ]
    for name, mutated in done_mutations:
        bad = 'S_bad_done_' + name
        checks += [
            f'{bad} = S_release[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_frame) :: (GENERATOR_CLOSE_DONE {mutated}) :: ptask_release*]',
            f'$heap_graph({bad}) = $heap_graph(S_release)',
            f'$heap_valid($heap_graph({bad}))',
            f'~$generator_close_done_valid({bad}, {mutated})',
            f'~$generator_close_destructor_ready({bad}, pgenrelease_frame)',
            f'~$call_descriptors_valid({bad})',
        ]
    checks += r'''
pgenerator_wrong_receiver = pgenerator_closed[.ACCESS = (pgeneratoraccess[.TARGET = METHOD_TARGET n_other pcallcontext.FUNCTION])]
S_bad_done_certificate = S_release[.OBJECTS[n_gen] = GENERATOR pgenerator_wrong_receiver]
$heap_graph(S_bad_done_certificate) = $heap_graph(S_release)
$heap_valid($heap_graph(S_bad_done_certificate))
$access_generator_record_valid(S_bad_done_certificate, pgenerator_wrong_receiver)
~$access_generator_close_valid(S_bad_done_certificate, pgenclose_done)
~$generator_close_done_valid(S_bad_done_certificate, pgenclose_done)
~$generator_close_destructor_ready(S_bad_done_certificate, pgenrelease_frame)
~$call_descriptors_valid(S_bad_done_certificate)
'''.strip().splitlines()
    return stage, checks


def reference_resume():
    stage = 'S.TODO = (GENERATOR_YIELD_DONE porigin_yield poperand_key?) :: ptask_tail*'
    checks = r'''
S.TODO = (GENERATOR_YIELD_DONE porigin_yield poperand_key?) :: ptask_tail*
S.CURRENT = (pcallcontext)
S.FRAMES = pframe_resume :: pframe_tail*
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
n_gen = pgeneratorop.OBJECT
S.OBJECTS[n_gen] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.ACCESS = (pgeneratoraccess)
pgeneratoraccess.TARGET = $context_target(pcallcontext)
pgeneratoraccess.SITE = porigin_get
pgeneratoraccess.LINE = pcallcontext.LINE
$context_target(pcallcontext) = METHOD_TARGET n_box porigin_method
$generator_reference_active(S)
~$reference_returning(S)
$access_generator_context(S, pcallcontext)
$access_context(S, pcallcontext)
$access_chain(S, S.CURRENT, S.FRAMES)
$call_selected_valid(S, $context_target(pcallcontext), pcallcontext.CALLSITE)
$outputs(S.EVENTS) = $ptascii("A;G;")
~$access_generator_shape(S, pcallcontext[.ARGC = 0], pgeneratoraccess)
~$access_generator_shape(S, pcallcontext[.HOLES = [0]], pgeneratoraccess)
~$access_generator_shape(S, pcallcontext[.EXTRA = [KNOWN PNULL]], pgeneratoraccess)
~$access_generator_shape(S, pcallcontext[.PARAMS = eps], pgeneratoraccess)
~$access_generator_shape(S, pcallcontext[.LINE = $(pcallcontext.LINE + 1)], pgeneratoraccess)
~$access_generator_shape(S, pcallcontext[.CALLSITE = (PORIGIN 999 eps)], pgeneratoraccess)
S_bad_extent = S[.CURRENT = (pcallcontext[.ARGC = 0])]
$heap_graph(S_bad_extent) = $heap_graph(S)
~$call_current_valid(S_bad_extent)
~$call_descriptors_valid(S_bad_extent)
S_bad_holes = S[.CURRENT = (pcallcontext[.HOLES = [0]])]
$heap_graph(S_bad_holes) = $heap_graph(S)
~$call_current_valid(S_bad_holes)
~$call_descriptors_valid(S_bad_holes)
'''.strip().splitlines() + guards('S')
    checks += certificate_forgeries('S', 'pgenerator', 'pgeneratoraccess', 'pcallcontext', 'running')
    checks += seek('S_paused', 'S', 3) + r'''
S_paused.OBJECTS[n_gen] = GENERATOR pgenerator_paused
pgenerator_paused.PHASE = GENERATOR_PAUSED
pgenerator_paused.ACCESS = (pgeneratoraccess)
pgenerator_paused.FRAME = (pframe_paused)
pframe_paused.CONTEXT = (pcallcontext)
pgenerator_paused.VALUE = eps
pgenerator_paused.REFCELL = (n_row)
n_row <- S_paused.REFCELLS
S_paused.STORE[n_row] = DEFINED (PARRAY n_array)
$generator_reference_producer(S_paused, pgenerator_paused)
$access_generator_context(S_paused, pcallcontext)
$access_generator_record_valid(S_paused, pgenerator_paused)
$heap_owners($heap_prune($heap_graph(S_paused)), HCELL n_row) = 2
$heap_owners($heap_prune($heap_graph(S_paused)), HOBJECT n_box) = 1
$outputs(S_paused.EVENTS) = $ptascii("A;G;")
'''.strip().splitlines() + guards('S_paused')
    checks += certificate_forgeries('S_paused', 'pgenerator_paused', 'pgeneratoraccess', 'pcallcontext', 'paused')
    checks += seek('S_closed', 'S_paused', 4) + r'''
S_closed.OBJECTS[n_gen] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.ACCESS = (pgeneratoraccess)
pgenerator_closed.FRAME = eps
~((HOBJECT n_box) <- S_closed.ALLOCATIONS)
$access_generator_record_valid(S_closed, pgenerator_closed)
~$access_generator_context(S_closed, pcallcontext)
~$call_selected_valid(S_closed, pgeneratoraccess.TARGET, (pgeneratoraccess.SITE))
$outputs(S_closed.EVENTS) = $ptascii("A;G;V:3;Q:2;B;")
'''.strip().splitlines() + guards('S_closed')
    return stage, checks


def render(name, fixture, filename, expected):
    stage, checks = dict([('creation-escape-and-paused-close', creation_close),
                          ('reference-yield-running-and-paused', reference_resume)])[name]()
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET',
              'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
              r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
              'S = S_reached[.COMPLETION = NORMAL]'] + checks
    checks += ['S_zero = $drive_steps(S, 0)', 'S_zero = S[.COMPLETION = BUDGET]',
               'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET'] + guards('S_one')
    checks += ['S_done = $drive(S_one[.COMPLETION = NORMAL], 1500)',
               'S_direct = $drive(S, 1500)', 'S_done = S_direct',
               'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$outputs(S_done.EVENTS) = $ptascii("' + expected + '")'] + guards('S_done')
    text = PREFIX.replace('STAGE', stage) + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- ' + ('' if c.startswith('PhpStep: ') else 'if ') + c + '\n' for c in checks)
    return text, checks
