from error_handler_protocol import PREFIX


STAGE = ('S.TODO = (ACCESS_RESULT paccess) :: ptask_tail* '
         '-- if paccess.MODE = ACCESS_SET '
         '-- if paccess.PHASE = ACCESS_CALL $ptascii("offsetSet") '
         '-- if S.ACTIVEFIBER =/= eps')


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def conditions(fixture, filename):
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET',
              'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
              r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
              'S = S_reached[.COMPLETION = NORMAL]']
    checks += '''
S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*
paccess.MODE = ACCESS_SET
paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")
paccess.TASK = KEY_WRITE_FINISH pkeywriter
pkeywriter.BASE = BASE_RETURNED porigin_prefix n_temp
paccess.TARGET =/= porigin_prefix
paccess.BASE = pkeywriter.BASE
paccess.INPUT = KNOWN PNULL
paccess.OFFSET = PNULL
paccess.RHS = VARIABLE $ptascii("rhs18") z_rhs
paccess.VALUE = PINT 11
paccess.SELECTED = REFERENCE n_old
paccess.OBJECT = (n_child)
S.STORE[n_temp] = DEFINED (POBJECT n_child)
S.STORE[n_old] = DEFINED (PINT 25)
$lookup(S.ENV, $ptascii("rhs18")) = (n_old)
S.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("alias18")) = (n_old)
$lookup(psymboltable_global.ENV, $ptascii("rhs18")) = (n_new)
$lookup(psymboltable_global.ENV, $ptascii("new18")) = (n_new)
n_new =/= n_old
S.STORE[n_new] = DEFINED (PINT 31)
$lookup(psymboltable_global.ENV, $ptascii("g18")) = eps
S.ACTIVEFIBER = (n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
$access_valid(S, paccess)
$task_nodes(ACCESS_RESULT paccess) = [HCELL n_temp, HOBJECT n_child, HOBJECT n_child]
$outputs(S.EVENTS) = $ptascii("G;S:1:11;A:parked;Q:resumed:11;F;")
S_bad = S[.TODO = (ACCESS_RESULT paccess[.TARGET = porigin_prefix]) :: ptask_tail*]
$heap_graph(S_bad) = $heap_graph(S)
$heap_valid($heap_graph(S_bad))
~$call_descriptors_valid(S_bad)
'''.strip().splitlines()
    checks += guards('S')
    checks += ['S_zero = $drive_steps(S, 0)',
               'S_zero = S[.COMPLETION = BUDGET]',
               'S_one = $drive_steps(S, 1)',
               'S_one.COMPLETION = BUDGET'] + guards('S_one')
    checks += ['S_done = $drive(S_one[.COMPLETION = NORMAL], 1500)',
               'S_direct = $drive(S, 1500)', 'S_done = S_direct',
               'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               'S_done.ACTIVEFIBER = eps', 'S_done.FIBERCALLERS = eps',
               '$outputs(S_done.EVENTS) = $ptascii("G;S:1:11;A:parked;Q:resumed:11;F;C;R:25;E:25:31:1;")']
    return checks + guards('S_done')


def render(fixture, filename):
    checks = conditions(fixture, filename)
    return (PREFIX.replace('STAGE', STAGE) + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
