"""Source-reached borrowed and evaluated compound operand controls."""
from error_handler_protocol import PREFIX

CASES = [
    ('borrowed-cv-and-entry-flags', 'compound-concat-rhs-object-replacement'),
    ('owned-tmp-reference-and-release', 'compound-concat-rhs-object-temp-owner'),
]
REFERENCE = 'compound-concat-rhs-reference-return-owner'

EXTRA = r'''
dec $live_phase(pstate, nat) : bool
def $live_phase(S, 0) = true
  -- if $outputs(S.EVENTS) = $ptascii("L;D:before;P;")
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin z) :: (COMPOUND_LIVE_LEFT pcompoundstring) :: ptask*
def $live_phase(S, 1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (COMPOUND_LIVE_RIGHT pcompoundstring ptbytes) :: ptask*
def $live_phase(S, 2) = true
  -- if S.TODO = (COMPOUND_LIVE_RIGHT pcompoundstring ptbytes) :: ptask*
def $live_phase(S, 3) = true
  -- if S.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring) :: ptask*
def $live_phase(S, 4) = true
  -- if S.TODO = (COMPOUND_LIVE_DONE pcompoundstring) :: ptask*
def $live_phase(S, n) = false -- otherwise
dec $live_seek(pstate, nat, nat) : pstate
def $live_seek(S, n_phase, n) = S
  -- if $live_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $live_seek(S, n_phase, n) = $live_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$live_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $live_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def lines(text):
    return text.strip().splitlines()


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def seek(state, previous, phase):
    return [f'{state}_reached = $live_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$live_phase({state}, {phase})']


def borrowed():
    checks = lines(r'''
S.TODO = (COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left)) :: ptask_tail*
pcompoundstring.RIGHT = VARIABLE $ptascii("rhs") z_rhs
pcompoundstring.PLACE = ROOT n_target
pcompoundstring.CV
~pcompoundstring.SELF
pcompoundstring.SELECTED = eps
$lookup(S.ENV, $ptascii("target")) = (n_target)
$lookup(S.ENV, $ptascii("rhs")) = (n_rhs_cell)
S.STORE[n_rhs_cell] = DEFINED (POBJECT n_rhs)
~(n_target <- S.REFCELLS)
$compound_live_valid(S, pcompoundstring)
$compound_live_initial_user(S, pcompoundstring, POBJECT n_left)
$call_task_valid(S, COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left))
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left)) = eps
$task_nodes(COMPOUND_LIVE_LEFT pcompoundstring[.SELECTED = (n_left)]) = eps
$heap_owners($heap_graph(S), HOBJECT n_rhs) = 1
$heap_owners($heap_graph(S), HOBJECT n_left) = 1
''') + guards('S')
    for suffix, change in [
            ('site', '.SITE = PORIGIN 999 eps'),
            ('line', '.LINE = $(pcompoundstring.LINE + 1)'),
            ('name', '.RIGHT = VARIABLE $ptascii("target") z_rhs'),
            ('cv', '.CV = false'),
            ('self', '.SELF = true'),
            ('selected', '.SELECTED = (n_rhs)'),
            ('place', '.PLACE = ROOT n_rhs_cell')]:
        record = f'pcompoundstring[{change}]'
        task = f'COMPOUND_LIVE_PREP {record} (POBJECT n_left)'
        state = 'S_bad_' + suffix
        checks += [f'{state} = S[.TODO = ({task}) :: ptask_tail*]',
                   f'$heap_graph({state}) = $heap_graph(S)',
                   f'~$call_task_valid({state}, {task})',
                   f'~$call_descriptors_valid({state})']
    checks += lines(r'''
~$compound_live_source(S, pcompoundstring[.RIGHT = REFERENCE n_rhs_cell])
S_scalar = S[.STORE[n_target] = DEFINED PNULL][.STORE[n_rhs_cell] = DEFINED (PSTRING $ptascii("x"))]
~$compound_live_initial_user(S_scalar, pcompoundstring, PNULL)
~$call_task_valid(S_scalar, COMPOUND_LIVE_PREP pcompoundstring PNULL)
''')
    checks += seek('S_changed', 'S', 0) + lines(r'''
S_changed.FRAMES = pframe :: pframe_tail*
pframe.TODO = (STRINGIFY_RESULT n_left pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_LEFT pcompoundstring_selected) :: ptask_saved*
pcompoundstring_selected = pcompoundstring[.SELECTED = (n_left)]
S_global = $global_table_view(S_changed)
$lookup(S_global.ENV, $ptascii("rhs")) = (n_new_cell)
S_changed.STORE[n_new_cell] = DEFINED (POBJECT n_new)
n_new =/= n_rhs
~((HOBJECT n_rhs) <- S_changed.ALLOCATIONS)
$task_nodes(COMPOUND_LIVE_LEFT pcompoundstring_selected) = eps
$stringify_consumer_receiver_valid(S_changed, n_left, COMPOUND_LIVE_LEFT pcompoundstring_selected)
~$stringify_consumer_receiver_valid(S_changed, n_new, COMPOUND_LIVE_LEFT pcompoundstring_selected)
S_bad_saved = S_changed[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_left pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_LEFT pcompoundstring_selected[.SELECTED = (n_new)]) :: ptask_saved*] :: pframe_tail*]
$heap_graph(S_bad_saved) = $heap_graph(S_changed)
~$call_frames_valid(S_bad_saved, S_bad_saved.FRAMES)
~$call_descriptors_valid(S_bad_saved)
''') + guards('S_changed')
    return checks


def owned(reference):
    checks = lines(r'''
S.TODO = (COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left)) :: ptask_tail*
pcompoundstring.RIGHT = KNOWN (POBJECT n_rhs)
pcompoundstring.PLACE = ROOT n_target
pcompoundstring.CV
~pcompoundstring.SELF
pcompoundstring.SELECTED = eps
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left)) = [HOBJECT n_rhs]
$heap_owners($heap_graph(S), HOBJECT n_rhs) = 2
$call_task_valid(S, COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left))
''') + guards('S')
    checks += seek('S_cast', 'S', 1) + lines(r'''
S_cast.TODO = (STRINGIFY_RESULT n_rhs pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_cast ptbytes_left) :: ptask_cast*
pcompoundstring_cast = pcompoundstring[.SELECTED = (n_rhs)]
ptbytes_left = $ptascii("a")
S_cast.RESULT = KNOWN (PSTRING $ptascii("before"))
$outputs(S_cast.EVENTS) = $ptascii("Q;L;P;O;")
$stringify_consumer_receiver_valid(S_cast, n_rhs, COMPOUND_LIVE_RIGHT pcompoundstring_cast ptbytes_left)
S_wrong_receiver = S_cast[.TODO = (STRINGIFY_RESULT n_rhs pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_cast[.SELECTED = (n_left)] ptbytes_left) :: ptask_cast*]
$heap_graph(S_wrong_receiver) = $heap_graph(S_cast)
~$call_descriptors_valid(S_wrong_receiver)
''') + guards('S_cast')
    checks += seek('S_write', 'S_cast', 2) + lines(r'''
$task_nodes(COMPOUND_LIVE_RIGHT pcompoundstring_cast ptbytes_left) = [HOBJECT n_rhs]
$heap_owners($heap_graph(S_write), HOBJECT n_rhs) = 1
S_write.STORE[n_target] = DEFINED (POBJECT n_left)
''')
    checks += seek('S_release', 'S_write', 3) + lines(r'''
S_release.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring_cast) :: ptask_release*
S_release.STORE[n_target] = DEFINED (PSTRING $ptascii("abefore"))
$outputs(S_release.EVENTS) = $ptascii("Q;L;P;O;D:left;")
(HOBJECT n_rhs) <- S_release.ALLOCATIONS
$heap_owners($heap_graph(S_release), HOBJECT n_rhs) = 1
$task_nodes(COMPOUND_LIVE_RELEASE pcompoundstring_cast) = [HOBJECT n_rhs]
''') + guards('S_release')
    checks += seek('S_freed', 'S_release', 4) + lines(r'''
S_freed.TODO = (COMPOUND_LIVE_DONE pcompoundstring_cast) :: ptask_freed*
$outputs(S_freed.EVENTS) = $ptascii("Q;L;P;O;D:left;D:before;")
~((HOBJECT n_rhs) <- S_freed.ALLOCATIONS)
$task_nodes(COMPOUND_LIVE_DONE pcompoundstring_cast) = eps
$compound_live_source(S_freed, pcompoundstring_cast)
~$compound_live_valid(S_freed, pcompoundstring_cast)
$call_task_valid(S_freed, COMPOUND_LIVE_DONE pcompoundstring_cast)
''') + guards('S_freed')
    checks += [f'S_ref_initial = $php_run({reference["fixture"]}, 0, {reference["filename"]})',
               'S_ref_initial.COMPLETION = BUDGET',
               'S_ref_reached = $seek(S_ref_initial[.COMPLETION = NORMAL], 1000)',
               r'S_ref_reached.COMPLETION = NORMAL \/ S_ref_reached.COMPLETION = BUDGET',
               'S_ref = S_ref_reached[.COMPLETION = NORMAL]']
    checks += lines(r'''
S_ref.TODO = (COMPOUND_LIVE_PREP pcompoundstring_ref (POBJECT n_left_ref)) :: ptask_ref*
pcompoundstring_ref.RIGHT = REFERENCE n_ref
pcompoundstring_ref.PLACE = ROOT n_target_ref
$lookup(S_ref.ENV, $ptascii("rhs")) = (n_ref)
S_ref.STORE[n_ref] = DEFINED (PSTRING $ptascii("before"))
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring_ref (POBJECT n_left_ref)) = [HCELL n_ref]
$heap_owners($heap_graph(S_ref), HCELL n_ref) = 2
''') + guards('S_ref')
    checks += seek('S_ref_write', 'S_ref', 2) + lines(r'''
S_ref_write.TODO = (COMPOUND_LIVE_RIGHT pcompoundstring_ref_write ptbytes_ref_left) :: ptask_ref_write*
pcompoundstring_ref_write.RIGHT = REFERENCE n_ref
pcompoundstring_ref_write.SELECTED = eps
$lookup(S_ref_write.ENV, $ptascii("rhs")) = (n_ref_new)
n_ref_new =/= n_ref
S_ref_write.STORE[n_ref] = DEFINED (PSTRING $ptascii("before"))
S_ref_write.STORE[n_ref_new] = DEFINED (PSTRING $ptascii("after"))
$heap_owners($heap_graph(S_ref_write), HCELL n_ref) = 1
''')
    checks += seek('S_ref_freed', 'S_ref_write', 4) + lines(r'''
S_ref_freed.TODO = (COMPOUND_LIVE_DONE pcompoundstring_ref_write) :: ptask_ref_freed*
~((HCELL n_ref) <- S_ref_freed.ALLOCATIONS)
$compound_live_source(S_ref_freed, pcompoundstring_ref_write)
~$compound_live_valid(S_ref_freed, pcompoundstring_ref_write)
$call_task_valid(S_ref_freed, COMPOUND_LIVE_DONE pcompoundstring_ref_write)
''') + guards('S_ref_freed')
    checks += ['S_ref_done = $drive(S_ref_freed, 1000)',
               'S_ref_done.COMPLETION = NORMAL', 'S_ref_done.TODO = eps',
               '$outputs(S_ref_done.EVENTS) = $ptascii("' + reference['expected'] + '")']
    return checks


def render(name, fixture, filename, expected, reference=None):
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET',
              'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1000)',
              r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
              'S = S_reached[.COMPLETION = NORMAL]']
    checks += borrowed() if name == 'borrowed-cv-and-entry-flags' else owned(reference)
    checks += ['S_zero = $drive_steps(S, 0)', 'S_zero = S[.COMPLETION = BUDGET]',
               'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET'] + guards('S_one')
    checks += ['S_done = $drive(S_one[.COMPLETION = NORMAL], 1000)',
               'S_direct = $drive(S, 1000)', 'S_done = S_direct',
               'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$outputs(S_done.EVENTS) = $ptascii("' + expected + '")'] + guards('S_done')
    stage = 'S.TODO = (COMPOUND_LIVE_PREP pcompoundstring (POBJECT n_left)) :: ptask*'
    text = PREFIX.replace('STAGE', stage) + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep: ') else 'if ') + check + '\n' for check in checks)
    return text, checks
