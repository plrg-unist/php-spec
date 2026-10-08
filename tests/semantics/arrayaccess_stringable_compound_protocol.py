"""Focused334 controls from genuine maintained-source states; rendering is not execution."""

from error_handler_protocol import PREFIX


CASES = [
    ('reference-carrier-admission', 'compound-reference-referent-replaced-during-set'),
    ('left-write-and-current-rhs', 'left-stringable-write-and-current-rhs-conversion'),
    ('cast-owner-in-parked-fiber', 'stringable-cast-owner-survives-fiber-park-after-cell-write'),
    ('computed-key-and-base-owner-order', 'computed-base-owner-survives-through-final-computed-key-release'),
    ('undefined-key-required-preflight', 'stringable-key-unset-required-set-argument'),
    ('undefined-key-new-default-owner', 'stringable-key-unset-new-set-default-argview'),
]

COMPILER_CASES = [
    ('direct-call-update', '<?php function f334() { return 1; } f334() .= missing334();',
     "Can't use function return value in write context"),
    ('builtin-result-update', "<?php strlen('x')[0] .= missing334();",
     'Cannot use result of built-in function in write context'),
    ('scalar-temporary-update', '<?php (1)[0] .= missing334();',
     'Cannot use temporary expression in write context'),
]

EXTRA = r'''
dec $right_stage(pstate) : bool
def $right_stage(S) = true
  -- if S.TODO = (ACCESS_STRING_PREP paccess poperand (ptbytes_left)) :: ptask*
def $right_stage(S) = false -- otherwise
dec $seek_right(pstate, nat) : pstate
def $seek_right(S, n) = S
  -- if $right_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_right(S, n) = $seek_right($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$right_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_right(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET

dec $park_stage(pstate, nat) : bool
def $park_stage(S, n) = true
  -- if $fiber_at(S, n) = (pfiber)
  -- if pfiber.STATUS = FIBER_SUSPENDED
  -- if pfiber.VM = (pfibervm)
def $park_stage(S, n) = false -- otherwise
dec $seek_park(pstate, nat, nat) : pstate
def $seek_park(S, n_fiber, n) = S
  -- if $park_stage(S, n_fiber)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_park(S, n_fiber, n) = $seek_park($drive_steps(S[.COMPLETION = NORMAL], 1), n_fiber, $nabs($(n - 1)))
  -- if ~$park_stage(S, n_fiber)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_park(S, n_fiber, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $hole_default_stage(pstate) : bool
def $hole_default_stage(S) = true
  -- if S.TODO = [NAMED_PREFLIGHT porigin 1]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.HOLES = [0]
def $hole_default_stage(S) = false -- otherwise
dec $seek_hole_default(pstate, nat) : pstate
def $seek_hole_default(S, n) = S
  -- if $hole_default_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_hole_default(S, n) = $seek_hole_default($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$hole_default_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_hole_default(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET

'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def reference_entry():
    return r'''
S.TODO = (ACCESS_STRING_PREP paccess (REFERENCE n) eps) :: ptask_tail*
paccess.MODE = ACCESS_COMPOUND CONCAT PNULL
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
paccess.OBJECT = (n_box)
S.STORE[n] = DEFINED (POBJECT n_left)
n <- S.REFCELLS
(HCELL n) <- S.ALLOCATIONS
(HOBJECT n_left) <- S.ALLOCATIONS
(HOBJECT n_box) <- S.ALLOCATIONS
$access_valid(S, paccess)
$access_reference_get(S, paccess)
$access_string_source(S, paccess, REFERENCE n)
$call_task_valid(S, ACCESS_STRING_PREP paccess (REFERENCE n) eps)
~$call_task_valid(S, ACCESS_STRING_PREP paccess (KNOWN PNULL) eps)
~$access_string_source(S, paccess, KNOWN (POBJECT n_left))
~$call_task_valid(S, ACCESS_STRING_PREP paccess[.SITE = PORIGIN 0 eps] (REFERENCE n) eps)
~$call_task_valid(S, ACCESS_STRING_PREP paccess[.LINE = $(paccess.LINE + 1)] (REFERENCE n) eps)
~$call_task_valid(S, ACCESS_STRING_PREP paccess[.MODE = ACCESS_COMPOUND ADD PNULL] (REFERENCE n) eps)
~$call_task_valid(S, ACCESS_STRING_PREP paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")] (REFERENCE n) eps)
~$call_task_valid(S, ACCESS_STRING_PREP paccess[.OBJECT = (|S.OBJECTS|)] (REFERENCE n) eps)
~$call_task_valid(S, ACCESS_STRING_PREP paccess (REFERENCE (|S.STORE|)) eps)
S_unmarked = S[.REFCELLS = $access_reference_unwrap(S.REFCELLS, n)]
~$call_task_valid(S_unmarked, ACCESS_STRING_PREP paccess (REFERENCE n) eps)
$task_nodes(ACCESS_STRING_PREP paccess (REFERENCE n) eps) = [HCELL n, HOBJECT n_box]
$task_nodes(ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left) = [HCELL n, HOBJECT n_box]
$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_left) = 1
S.RESULT = KNOWN PNULL
S.BASE = BASE_VALUE (KNOWN PNULL)
$outputs(S.EVENTS) = $ptascii("G;")
'''.strip().splitlines() + guards('S')


def admission():
    stage = 'S.TODO = (ACCESS_STRING_PREP paccess (REFERENCE n) eps) :: ptask_tail*'
    checks = reference_entry() + r'''
PhpStep: S ~> S_call
S_call.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (paccess.SITE) paccess.LINE) :: (STRINGIFY_RESULT n_left paccess.SITE paccess.LINE) :: (ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left) :: ptask_tail*
$call_task_valid(S_call, ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left)
$stringify_source(S_call, paccess.SITE, paccess.LINE, ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left)
~$stringify_source(S_call, paccess.SITE, $(paccess.LINE + 1), ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left)
$stringify_consumer_receiver_valid(S_call, n_left, ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left)
~$stringify_consumer_receiver_valid(S_call, n_left, ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_box)
S_call.STORE = S.STORE
S_call.ARRAYS = S.ARRAYS
S_call.REFCELLS = S.REFCELLS
S_call.ALLOCATIONS = S.ALLOCATIONS
S_call.GC = S.GC
S_call.HELD = S.HELD
S_call.EVENTS = S.EVENTS
'''.strip().splitlines() + guards('S_call')
    return stage, checks


def current_rhs():
    stage = 'S.TODO = (ACCESS_STRING_PREP paccess (REFERENCE n) eps) :: ptask_tail*'
    checks = reference_entry() + r'''
paccess.SELECTED = VARIABLE $ptascii("right334") z_rhs
S_rhs = $quiet_operand(S, paccess.SELECTED)
S_rhs.RESULT = KNOWN (POBJECT n_old_right)
(HOBJECT n_old_right) <- S.ALLOCATIONS
S_right_reached = $seek_right(S, 1500)
S_right_reached.COMPLETION = NORMAL \/ S_right_reached.COMPLETION = BUDGET
S_right = S_right_reached[.COMPLETION = NORMAL]
S_right.TODO = (ACCESS_STRING_PREP paccess (REFERENCE n) (ptbytes_left)) :: ptask_tail*
ptbytes_left = $ptascii("a")
S_right.STORE[n] = DEFINED PNULL
~((HOBJECT n_left) <- S_right.ALLOCATIONS)
~((HOBJECT n_old_right) <- S_right.ALLOCATIONS)
(HCELL n) <- S_right.ALLOCATIONS
n <- S_right.REFCELLS
$outputs(S_right.EVENTS) = $ptascii("G;T;O;Z;D;")
$lookup(S_right.ENV, $ptascii("right334")) = (n_right_cell)
S_right.STORE[n_right_cell] = DEFINED (POBJECT n_new_right)
n_new_right =/= n_old_right
(HOBJECT n_new_right) <- S_right.ALLOCATIONS
S_selected = $access_string_value(S_right, paccess, REFERENCE n, (ptbytes_left))
S_selected.RESULT = KNOWN (POBJECT n_new_right)
$call_task_valid(S_right, ACCESS_STRING_PREP paccess (REFERENCE n) (ptbytes_left))
$task_nodes(ACCESS_STRING_PREP paccess (REFERENCE n) (ptbytes_left)) = [HCELL n, HOBJECT n_box]
PhpStep: S_right ~> S_right_call
S_right_call.TODO = (CALL_ARGS (METHOD_TARGET n_new_right porigin_right_method) eps 0 eps (paccess.SITE) paccess.LINE) :: (STRINGIFY_RESULT n_new_right paccess.SITE paccess.LINE) :: (ACCESS_STRING_RESULT paccess (REFERENCE n) (ptbytes_left) n_new_right) :: ptask_tail*
$stringify_consumer_receiver_valid(S_right_call, n_new_right, ACCESS_STRING_RESULT paccess (REFERENCE n) (ptbytes_left) n_new_right)
~$stringify_consumer_receiver_valid(S_right_call, n_new_right, ACCESS_STRING_RESULT paccess (REFERENCE n) (ptbytes_left) n_old_right)
'''.strip().splitlines() + guards('S_right') + guards('S_right_call')
    return stage, checks


def fiber_owner():
    stage = 'S.TODO = (ACCESS_STRING_PREP paccess (REFERENCE n) eps) :: ptask_tail*'
    checks = reference_entry() + r'''
S.ACTIVEFIBER = (n_fiber)
$fiber_at(S, n_fiber) = (pfiber_running)
pfiber_running.STATUS = FIBER_RUNNING
S_parked_reached = $seek_park(S, n_fiber, 1500)
S_parked_reached.COMPLETION = NORMAL \/ S_parked_reached.COMPLETION = BUDGET
S_parked = S_parked_reached[.COMPLETION = NORMAL]
S_parked.ACTIVEFIBER = eps
S_parked.FIBERCALLERS = eps
$fiber_at(S_parked, n_fiber) = (pfiber_parked)
pfiber_parked.STATUS = FIBER_SUSPENDED
pfiber_parked.VM = (pfibervm)
pfibervm.FRAMES = pframe_cast :: pframe_tail*
pframe_cast.TODO = (STRINGIFY_RESULT n_left paccess.SITE paccess.LINE) :: (ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_left) :: ptask_tail*
S_parked.STORE[n] = DEFINED PNULL
(HCELL n) <- S_parked.ALLOCATIONS
(HOBJECT n_left) <- S_parked.ALLOCATIONS
$($heap_owners($heap_prune($heap_graph(S_parked)), HOBJECT n_left) > 0)
$outputs(S_parked.EVENTS) = $ptascii("G;T;Z;")
$fiber_vm_valid(S_parked, pfibervm, (n_fiber), eps)
pframe_forged = pframe_cast[.TODO = (STRINGIFY_RESULT n_left paccess.SITE paccess.LINE) :: (ACCESS_STRING_RESULT paccess (REFERENCE n) eps n_box) :: ptask_tail*]
pfibervm_forged = pfibervm[.FRAMES = pframe_forged :: pframe_tail*]
S_forged = S_parked[.OBJECTS[n_fiber] = FIBER pfiber_parked[.VM = (pfibervm_forged)]]
$heap_graph(S_forged) = $heap_graph(S_parked)
$heap_valid($heap_graph(S_forged))
~$fiber_vm_valid(S_forged, pfibervm_forged, (n_fiber), eps)
~$call_descriptors_valid(S_forged)
'''.strip().splitlines() + guards('S_parked')
    return stage, checks


def computed_owners():
    stage = ('S.TODO = (ACCESS_RESULT paccess) :: ptask_tail* '
             '-- if paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")')
    checks = r'''
S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*
paccess.MODE = ACCESS_COMPOUND CONCAT (POBJECT n_left)
paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")
paccess.OBJECT = (n_box)
paccess.BASE = BASE_VALUE (KNOWN (POBJECT n_box))
paccess.INPUT = KNOWN (POBJECT n_key)
paccess.OFFSET = POBJECT n_key
paccess.RHS = KNOWN (POBJECT n_right)
paccess.VALUE = PSTRING $ptascii("ab")
paccess.OUTER
$access_valid(S, paccess)
$call_task_valid(S, ACCESS_RESULT paccess)
$access_string_set_operand(paccess) = (KNOWN (POBJECT n_left))
$task_nodes(ACCESS_RESULT paccess) = [HOBJECT n_box, HOBJECT n_key, HOBJECT n_left, HOBJECT n_right, HOBJECT n_box, HOBJECT n_key, HOBJECT n_box]
$access_roots(paccess, false) = [HOBJECT n_left, HOBJECT n_right, HOBJECT n_box, HOBJECT n_key, HOBJECT n_box]
$access_string_set_operand(paccess[.PHASE = ACCESS_CALL $ptascii("offsetGet")]) = eps
$access_string_set_operand(paccess[.MODE = ACCESS_COMPOUND ADD (POBJECT n_left)]) = eps
(HOBJECT n_left) <- S.ALLOCATIONS
(HOBJECT n_right) <- S.ALLOCATIONS
(HOBJECT n_key) <- S.ALLOCATIONS
(HOBJECT n_box) <- S.ALLOCATIONS
$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_left) = 1
$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_right) = 1
$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_key) = 2
$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_box) = 3
$outputs(S.EVENTS) = $ptascii("G;L;R;S:ab;Z;")
S_site = S[.TODO = (ACCESS_RESULT paccess[.SITE = PORIGIN 0 eps]) :: ptask_tail*]
$heap_graph(S_site) = $heap_graph(S)
~$call_descriptors_valid(S_site)
$origin_node(S.SOURCES, paccess.TARGET) = (NExprArrayDimFetch expression_call phpType5 metadata_dim)
$ppbasemode(expression_call, PPRW) = PPR
$ppbasemode(expression_call, PPW) = PPR
P = $ppstart(0, PROGRAM eps, $ptascii("review334.php"))
P.COMPLETION = PPCNORMAL
P_stop = $ppupdatecheck(P, expression_call)
P_stop = P[.COMPLETION = PPCABRUPT (STATICERROR "Can't use function return value in write context" 1)]
$ppassignright(P_stop, eps, expression_call, NScalarInt (INTEGER 1) eps, false) = P_stop
$ppbasemode(NScalarInt (INTEGER 1) eps, PPRW) = PPRW
$ppdispatch(P, eps, NScalarInt (INTEGER 1) eps, PPRW) = P[.COMPLETION = PPCABRUPT (STATICERROR "Cannot use temporary expression in write context" 1)]
'''.strip().splitlines() + guards('S')
    return stage, checks


def key_hole_entry():
    return r'''
S.TODO = (ACCESS_SET_ENTER paccess) :: ptask_tail*
paccess.KEYHOLE
~paccess.LATCH
paccess.MODE = ACCESS_COMPOUND CONCAT (POBJECT n_left)
paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")
paccess.OBJECT = (n_box)
paccess.BASE = BASE_VALUE (VARIABLE $ptascii("boxReview19") z_box)
paccess.INPUT = VARIABLE $ptascii("keyReview19") z_key
paccess.OFFSET = PNULL
paccess.RHS = KNOWN (PSTRING $ptascii("b"))
paccess.VALUE = PSTRING $ptascii("ab")
paccess.OUTER
$error_missing_operand(S, paccess.INPUT)
$access_valid(S, paccess)
$access_holes(paccess) = [0]
$access_holes(paccess[.KEYHOLE = false]) = eps
$access_set_hole_target(S, paccess) = (METHOD_TARGET n_box porigin_method)
$target_function(S, METHOD_TARGET n_box porigin_method) = (pfunction)
pfunction.SIGNATURE.PARAMETERS[0].NAME = $ptascii("key")
pfunction.SIGNATURE.PARAMETERS[1].NAME = $ptascii("value")
$call_task_valid(S, ACCESS_SET_ENTER paccess)
S_restored = $write_name(S, $ptascii("keyReview19"), PSTRING $ptascii("restored"))
~$error_missing_operand(S_restored, paccess.INPUT)
$access_valid(S_restored, paccess)
$heap_valid($heap_graph(S_restored))
~$call_task_valid(S_restored, ACCESS_SET_ENTER paccess)
~$call_task_valid(S, ACCESS_SET_ENTER paccess[.KEYHOLE = false])
~$call_task_valid(S, ACCESS_SET_ENTER paccess[.LATCH = true])
~$call_task_valid(S, ACCESS_SET_ENTER paccess[.OFFSET = PSTRING $ptascii("before")])
~$call_task_valid(S, ACCESS_SET_ENTER paccess[.SITE = PORIGIN 0 eps])
~$call_task_valid(S, ACCESS_SET_ENTER paccess[.LINE = $(paccess.LINE + 1)])
~$call_task_valid(S, ACCESS_SET_ENTER paccess[.OBJECT = (|S.OBJECTS|)])
$task_nodes(ACCESS_SET_ENTER paccess) = [HOBJECT n_box, HOBJECT n_left, HOBJECT n_box]
$task_nodes(ACCESS_SET_ENTER paccess) = $task_nodes(ACCESS_RESULT paccess)
(HOBJECT n_left) <- S.ALLOCATIONS
(HOBJECT n_box) <- S.ALLOCATIONS
$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_left) = 1
$outputs(S.EVENTS) = $ptascii("G:before;L;")
S_forged = S[.TODO = (ACCESS_SET_ENTER paccess[.KEYHOLE = false]) :: ptask_tail*]
$heap_graph(S_forged) = $heap_graph(S)
$heap_valid($heap_graph(S_forged))
~$call_descriptors_valid(S_forged)
PhpStep: S ~> S_enter
S_enter.TODO = [NAMED_PREFLIGHT porigin_method 0]
S_enter.CURRENT = (pcallcontext)
pcallcontext.TARGET = METHOD_TARGET n_box porigin_method
pcallcontext.CALLSITE = (paccess.SITE)
pcallcontext.LINE = paccess.LINE
pcallcontext.ARGC = 2
pcallcontext.HOLES = [0]
pcallcontext.NAMED = eps
pcallcontext.WRAPPER = eps
S_enter.FRAMES = pframe :: pframe_tail*
pframe.TODO = (ACCESS_RESULT paccess) :: ptask_tail*
$access_set_hole_context(S_enter, pcallcontext)
$access_frame(S_enter, pcallcontext, pframe)
~$named_defined(S_enter, $ptascii("key"))
$named_defined(S_enter, $ptascii("value"))
$named_call_shape(S_enter, METHOD_TARGET n_box porigin_method, (paccess.SITE)) = {SLOTS ([NAMED_HOLE, NAMED_SENT (KNOWN PNULL)]), NAMED eps}
$named_preflight_valid(S_enter, porigin_method, 0)
$call_holes_valid(S_enter, pcallcontext)
S_enter.EVENTS = S.EVENTS
S_no_hole = S_enter[.CURRENT = (pcallcontext[.HOLES = eps])]
$heap_graph(S_no_hole) = $heap_graph(S_enter)
$heap_valid($heap_graph(S_no_hole))
~$call_descriptors_valid(S_no_hole)
S_no_source = S_enter[.FRAMES = pframe[.TODO = (ACCESS_RESULT paccess[.KEYHOLE = false]) :: ptask_tail*] :: pframe_tail*]
$heap_graph(S_no_source) = $heap_graph(S_enter)
~$call_descriptors_valid(S_no_source)
'''.strip().splitlines() + guards('S') + guards('S_enter')


def key_hole_required():
    stage = 'S.TODO = (ACCESS_SET_ENTER paccess) :: ptask_tail*'
    checks = key_hole_entry() + r'''
$default_at(pfunction.DEFAULTS, 0) = eps
PhpStep: S_enter ~> S_error
S_error = S_enter[.COMPLETION = THROWN "ArgumentCountError" $ptascii("UnsetKeyBoxReview19::offsetSet(): Argument #1 ($key) not passed") $default_parameter_line(S_enter, porigin_method, 0)]
S_error.EVENTS = S_enter.EVENTS
'''.strip().splitlines()
    return stage, checks


def key_hole_default():
    stage = 'S.TODO = (ACCESS_SET_ENTER paccess) :: ptask_tail*'
    checks = key_hole_entry() + r'''
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
pdefault.KIND = PDDEFERRED
$default_cache_at(S_enter.DEFAULTCACHE, pdefault.ORIGIN) = eps
S_default_reached = $seek_hole_default(S_enter, 100)
S_default_reached.COMPLETION = NORMAL \/ S_default_reached.COMPLETION = BUDGET
S_default = S_default_reached[.COMPLETION = NORMAL]
S_default.TODO = [NAMED_PREFLIGHT porigin_method 1]
S_default.CURRENT = (pcallcontext)
$lookup(S_default.ENV, $ptascii("key")) = (n_default_cell)
S_default.STORE[n_default_cell] = DEFINED (POBJECT n_default)
n_default =/= n_left
(HOBJECT n_default) <- S_default.ALLOCATIONS
(HOBJECT n_left) <- S_default.ALLOCATIONS
$heap_owners($heap_prune($heap_graph(S_default)), HOBJECT n_default) = 1
$heap_owners($heap_prune($heap_graph(S_default)), HOBJECT n_left) = 1
$default_cache_at(S_default.DEFAULTCACHE, pdefault.ORIGIN) = eps
$named_preflight_valid(S_default, porigin_method, 1)
$call_holes_valid(S_default, pcallcontext)
$outputs(S_default.EVENTS) = $ptascii("G:before;L;")
'''.strip().splitlines() + guards('S_default')
    return stage, checks


def render(name, fixture, filename, expected):
    stage, checks = {
        'reference-carrier-admission': admission,
        'left-write-and-current-rhs': current_rhs,
        'cast-owner-in-parked-fiber': fiber_owner,
        'computed-key-and-base-owner-order': computed_owners,
        'undefined-key-required-preflight': key_hole_required,
        'undefined-key-new-default-owner': key_hole_default,
    }[name]()
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
