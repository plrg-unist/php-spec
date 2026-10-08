"""New329 source-reached checks; rendering alone gives no execution credit."""

from error_handler_protocol import PREFIX


CASES = [
    ('fiber-notice-ingress', 'reference-value-warning-handler-suspends-before-materialization'),
    ('raw-reference-after-handler-write', 'value-designated-raw-reference-observes-handler-write'),
    ('raw-reference-after-global-rebind', 'value-designated-raw-reference-keeps-old-cell-after-rebind'),
    ('throw-frame-owner-after-retired-receiver', 'reference-value-notice-throw-leaves-get-before-receiver-and-rv-release'),
]

RESUME = r'''
dec $value_resume_stage(pstate) : bool
def $value_resume_stage(S) = true
  -- if S.TODO = (ACCESS_REFERENCE_VALUE_RESULT porigin poperand z) :: ptask*
def $value_resume_stage(S) = false -- otherwise
dec $seek_value_resume(pstate, nat) : pstate
def $seek_value_resume(S, n) = S
  -- if $value_resume_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_value_resume(S, n) = $seek_value_resume($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$value_resume_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_value_resume(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET

dec $retired_receiver_stage(pstate) : bool
def $retired_receiver_stage(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ACCESS_REFERENCE_VALUE_RELEASE paccess poperand) :: ptask*
def $retired_receiver_stage(S) = false -- otherwise
dec $seek_retired_receiver(pstate, nat) : pstate
def $seek_retired_receiver(S, n) = S
  -- if $retired_receiver_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_retired_receiver(S, n) = $seek_retired_receiver($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$retired_receiver_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_retired_receiver(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def source(operand):
    return f'''
S.ORIGIN = (porigin)
S.CURRENT = (pcallcontext)
S.FRAMES = pframe :: pframe_tail*
pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
$access_frame(S, pcallcontext, pframe)
$access_reference_get(S, paccess)
$reference_return_used(S)
~$reference_verifies(S)
~$finally_return_pending(S)
$access_reference_value_valid(S, porigin, {operand}, z)
~$access_reference_value_valid(S, PORIGIN 0 eps, {operand}, z)
~$access_reference_value_valid(S, porigin, {operand}, $(z + 1))
pframe_forged = pframe[.TODO = (ACCESS_RESULT paccess[.LINE = $(paccess.LINE + 1)]) :: ptask_saved*]
S_forged = S[.FRAMES = pframe_forged :: pframe_tail*]
$heap_graph(S_forged) = $heap_graph(S)
~$access_reference_value_valid(S_forged, porigin, {operand}, z)
'''.strip().splitlines() + guards('S')


def ingress():
    stage = 'S.TODO = (RETURN_REF_VALUE z) :: ptask_tail*'
    checks = '''
S.TODO = (RETURN_REF_VALUE z) :: ptask_tail*
S.RESULT = KNOWN (PBOOL false)
$outputs(S.EVENTS) = $ptascii("A:G;")
$access_reference_value_pending(S)
'''.strip().splitlines() + source('S.RESULT') + '''
~$access_reference_value_valid(S, porigin, KNOWN (PBOOL true), z)
PhpStep: S ~> S_queued
S_queued.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = ACCESS_REFERENCE_VALUE_RESULT porigin (KNOWN (PBOOL false)) z
perrorcall.SITE = porigin
perrorcall.LEVEL = 8
perrorcall.LINE = z
perrorcall.MESSAGE = $ptascii("Only variable references should be returned by reference")
perrorcall.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE z
$call_task_valid(S_queued, ERROR_HANDLER_INVOKE perrorcall)
~$call_task_valid(S_queued, ERROR_HANDLER_INVOKE perrorcall[.LINE = $(z + 1)])
~$call_task_valid(S_queued, ERROR_HANDLER_INVOKE perrorcall[.LEVEL = 8192])
~$call_task_valid(S_queued, ERROR_HANDLER_INVOKE perrorcall[.MESSAGE = $ptascii("forged")])
$task_nodes(perrorcall.RESUME) = eps
S_queued.RESULT = KNOWN PNULL
S_queued.BASE = BASE_VALUE (KNOWN PNULL)
S_queued.HELD = S.HELD
S_queued.STORE = S.STORE
S_queued.ARRAYS = S.ARRAYS
S_queued.REFCELLS = S.REFCELLS
S_queued.ALLOCATIONS = S.ALLOCATIONS
S_queued.GC = S.GC
S_queued.EVENTS = S.EVENTS
'''.strip().splitlines() + guards('S_queued')
    return stage, checks


def raw(rebind):
    stage = 'S.TODO = (RETURN_REF_VALUE z) :: ptask_tail* -- if S.RESULT = REFERENCE n'
    checks = '''
S.TODO = (RETURN_REF_VALUE z) :: ptask_tail*
S.RESULT = REFERENCE n
$outputs(S.EVENTS) = $ptascii("G;")
S.STORE[n] = DEFINED (POBJECT n_old)
(HOBJECT n_old) <- S.ALLOCATIONS
$access_reference_value_pending(S)
'''.strip().splitlines()
    checks += source('REFERENCE n') + r'''
n <- S.REFCELLS
(HCELL n) <- S.ALLOCATIONS
PhpStep: S ~> S_queued
S_queued.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = ACCESS_REFERENCE_VALUE_RESULT porigin (REFERENCE n) z
S_queued.RESULT = KNOWN PNULL
S_queued.BASE = BASE_VALUE (KNOWN PNULL)
S_queued.HELD = S.HELD
S_queued.STORE = S.STORE
S_queued.ARRAYS = S.ARRAYS
S_queued.REFCELLS = S.REFCELLS
S_queued.ALLOCATIONS = S.ALLOCATIONS
S_queued.GC = S.GC
S_queued.EVENTS = S.EVENTS
S_queued.PROPREFS = S.PROPREFS
S_queued.REFCOERCIONS = S.REFCOERCIONS
S_queued.CONTAINERINITS = S.CONTAINERINITS
S_queued.PARAMETERBACKINGS = S.PARAMETERBACKINGS
$task_nodes(ACCESS_REFERENCE_VALUE_RESULT porigin (REFERENCE n) z) = [HCELL n]
$call_task_valid(S_queued, ERROR_HANDLER_INVOKE perrorcall)
S_resumed = $seek_value_resume(S_queued, 1500)
S_resumed.COMPLETION = NORMAL \/ S_resumed.COMPLETION = BUDGET
S_resume = S_resumed[.COMPLETION = NORMAL]
S_resume.TODO = (ACCESS_REFERENCE_VALUE_RESULT porigin (REFERENCE n) z) :: ptask_tail*
$call_task_valid(S_resume, ACCESS_REFERENCE_VALUE_RESULT porigin (REFERENCE n) z)
n_forged = |S_resume.STORE|
~$call_task_valid(S_resume, ACCESS_REFERENCE_VALUE_RESULT porigin (REFERENCE n_forged) z)
~$call_task_valid(S_resume[.REFCELLS = $access_reference_unwrap(S_resume.REFCELLS, n)], ACCESS_REFERENCE_VALUE_RESULT porigin (REFERENCE n) z)
'''.strip().splitlines()
    checks += guards('S_queued') + guards('S_resume')
    if rebind:
        checks += '''
S_resume.STORE[n] = DEFINED (POBJECT n_old)
(HOBJECT n_old) <- S_resume.ALLOCATIONS
$outputs(S_resume.EVENTS) = $ptascii("G;H:8;Z;")
S_resume.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("row329")) = (n_fresh)
n_fresh =/= n
S_resume.STORE[n_fresh] = DEFINED PNULL
'''.strip().splitlines()
    else:
        checks += '''
S_resume.STORE[n] = DEFINED PNULL
~((HOBJECT n_old) <- S_resume.ALLOCATIONS)
$outputs(S_resume.EVENTS) = $ptascii("G;H:8;D;Z;")
'''.strip().splitlines()
    checks += '''
PhpStep: S_resume ~> S_returned
S_returned.TODO = (RETURN_REF_UNWIND (REFERENCE n) z false porigin) :: ptask_tail*
S_returned.RESULT = KNOWN PNULL
S_returned.STORE = S_resume.STORE
S_returned.ARRAYS = S_resume.ARRAYS
S_returned.REFCELLS = S_resume.REFCELLS
S_returned.ALLOCATIONS = S_resume.ALLOCATIONS
S_returned.GC = S_resume.GC
S_returned.HELD = S_resume.HELD
S_returned.EVENTS = S_resume.EVENTS
'''.strip().splitlines() + guards('S_returned')
    return stage, checks


def thrown():
    stage = ('S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (ACCESS_RESULT paccess) :: ptask_tail* '
             '-- if pdestructionframe.PENDING = (n_throw) '
             '-- if pdestructionframe.VALUE = REFERENCE n_value')
    checks = r'''
S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (ACCESS_RESULT paccess) :: ptask_tail*
S.DESTRUCTION.FRAMES = pdestructionframe :: pdestructionframe_tail*
pdestructionframe.PENDING = (n_throw)
pdestructionframe.VALUE = REFERENCE n_value
$outputs(S.EVENTS) = $ptascii("G;H:8;L;")
$destructor_frame_valid(S, pdestructionframe)
$access_valid(S, paccess)
$access_reference_value_release_source(S, paccess)
paccess.OBJECT = (n_box)
$access_method_selected(S, paccess, METHOD_TARGET n_box pdestructionframe.FUNCTION)
$lookup(S.ENV, $ptascii("box329")) = eps
S.STORE[n_value] = DEFINED (PARRAY n_array)
$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 0) = (DIRECT (POBJECT n_token))
(HCELL n_value) <- S.ALLOCATIONS
(HARRAY n_array) <- S.ALLOCATIONS
(HOBJECT n_box) <- S.ALLOCATIONS
(HOBJECT n_token) <- S.ALLOCATIONS
$heap_owners($heap_prune($heap_graph(S)), HCELL n_value) = 1
PhpStep: S ~> S_held
S_held.TODO = [THROW_SEARCH n_throw, ACCESS_RESULT paccess, ACCESS_REFERENCE_VALUE_RELEASE paccess (REFERENCE n_value)] ++ ptask_tail*
S_held.DESTRUCTION.FRAMES = pdestructionframe_tail*
S_held.RESULT = KNOWN PNULL
S_held.HELD = eps
S_held.STORE = S.STORE
S_held.ARRAYS = S.ARRAYS
S_held.REFCELLS = S.REFCELLS
S_held.ALLOCATIONS = S.ALLOCATIONS
S_held.GC = S.GC
S_held.EVENTS = S.EVENTS
$task_nodes(ACCESS_REFERENCE_VALUE_RELEASE paccess (REFERENCE n_value)) = [HCELL n_value]
$heap_owners($heap_prune($heap_graph(S_held)), HCELL n_value) = 1
$call_task_valid(S_held, ACCESS_REFERENCE_VALUE_RELEASE paccess (REFERENCE n_value))
S_known = S_held[.TODO = [THROW_SEARCH n_throw, ACCESS_RESULT paccess, ACCESS_REFERENCE_VALUE_RELEASE paccess (KNOWN (PBOOL false)), ACCESS_REFERENCE_VALUE_RELEASE paccess (REFERENCE n_value)] ++ ptask_tail*]
$heap_graph(S_known) = $heap_graph(S_held)
~$call_task_valid(S_known, ACCESS_REFERENCE_VALUE_RELEASE paccess (KNOWN (PBOOL false)))
~$call_task_valid(S_held, ACCESS_REFERENCE_VALUE_RELEASE paccess[.LINE = $(paccess.LINE + 1)] (REFERENCE n_value))
~$call_task_valid(S_held, ACCESS_REFERENCE_VALUE_RELEASE paccess[.SITE = PORIGIN 0 eps] (REFERENCE n_value))
~$call_task_valid(S_held, ACCESS_REFERENCE_VALUE_RELEASE paccess[.OBJECT = (n_token)] (REFERENCE n_value))
S_retiring = $seek_retired_receiver(S_held, 1500)
S_retiring.COMPLETION = NORMAL \/ S_retiring.COMPLETION = BUDGET
S_retired = S_retiring[.COMPLETION = NORMAL]
S_retired.TODO = (THROW_SEARCH n_throw) :: (ACCESS_REFERENCE_VALUE_RELEASE paccess (REFERENCE n_value)) :: ptask_tail*
$outputs(S_retired.EVENTS) = $ptascii("G;H:8;L;B;")
~((HOBJECT n_box) <- S_retired.ALLOCATIONS)
(HCELL n_value) <- S_retired.ALLOCATIONS
(HARRAY n_array) <- S_retired.ALLOCATIONS
(HOBJECT n_token) <- S_retired.ALLOCATIONS
S_retired.STORE[n_value] = DEFINED (PARRAY n_array)
$access_reference_value_release_source(S_retired, paccess)
~$access_valid(S_retired, paccess)
$call_task_valid(S_retired, ACCESS_REFERENCE_VALUE_RELEASE paccess (REFERENCE n_value))
$heap_owners($heap_prune($heap_graph(S_retired)), HCELL n_value) = 1
'''.strip().splitlines() + guards('S') + guards('S_held') + guards('S_retired')
    return stage, checks


def render(name, fixture, filename, expected):
    if name == 'fiber-notice-ingress':
        stage, checks = ingress()
    elif name in ('raw-reference-after-handler-write', 'raw-reference-after-global-rebind'):
        stage, checks = raw(name.endswith('rebind'))
    elif name == 'throw-frame-owner-after-retired-receiver':
        stage, checks = thrown()
    else:
        raise ValueError(name)
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
    text = PREFIX.replace('STAGE', stage) + RESUME + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- ' + ('' if c.startswith('PhpStep: ') else 'if ') + c + '\n' for c in checks)
    return text, checks
