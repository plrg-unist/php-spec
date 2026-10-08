"""Fresh source-reached static destination and nonowning history controls."""
from error_handler_protocol import PREFIX

SOURCE = 'static-compound-history-reentry-and-spare'
CASES = [('plain-slot-retirement-and-reentry', SOURCE),
         ('captured-reference-and-unchecked-write', SOURCE)]

EXTRA = r'''
dec $static_phase(pstate, nat) : bool
def $static_phase(S, 0) = true
  -- if S.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = eps
  -- if $outputs(S.EVENTS) = $ptascii("R1;")
def $static_phase(S, 1) = true
  -- if S.TODO = (COMPOUND_LIVE_PREP pcompoundstring pvalue) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = eps
  -- if $outputs(S.EVENTS) = $ptascii("R1;X:ab;")
def $static_phase(S, 2) = true
  -- if S.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = eps
  -- if $outputs(S.EVENTS) = $ptascii("R1;X:ab;R2;")
def $static_phase(S, 3) = true
  -- if S.TODO = (COMPOUND_LIVE_PREP pcompoundstring pvalue) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = (n)
def $static_phase(S, 4) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (COMPOUND_LIVE_RIGHT pcompoundstring ptbytes) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = (n_cell)
def $static_phase(S, 5) = true
  -- if S.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = (n)
def $static_phase(S, 6) = true
  -- if S.TODO = (COMPOUND_LIVE_DONE pcompoundstring) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
  -- if pstaticcompound.CELL = (n)
def $static_phase(S, n) = false -- otherwise
dec $static_seek(pstate, nat, nat) : pstate
def $static_seek(S, n_phase, n) = S
  -- if $static_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $static_seek(S, n_phase, n) = $static_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$static_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $static_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def lines(text):
    return text.strip().splitlines()


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$class_constant_history_valid({state})',
            f'$proprefs_valid({state})',
            f'$reference_coercions_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def seek(state, previous, phase):
    return [f'{state}_reached = $static_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$static_phase({state}, {phase})']


def task_forgeries(state, record, cap, task, tail, spare):
    checks = []
    for suffix, change in [('cell', f'.CELL = ({spare})'),
                           ('verify', f'.VERIFY = ~{cap}.VERIFY'),
                           ('entry', f'.ENTRY = |{state}.CLASSCONSTANTHISTORY|')]:
        bad_record = f'{record}[.PLACE = STATIC_COMPOUND {cap}[{change}]]'
        bad_task = task.replace(record, bad_record)
        bad_state = state + '_bad_' + suffix
        checks += [f'{bad_state} = {state}[.TODO = ({bad_task}) :: {tail}]',
                   f'$heap_graph({bad_state}) = $heap_graph({state})',
                   f'~$call_task_valid({bad_state}, {bad_task})',
                   f'~$call_descriptors_valid({bad_state})']
    return checks


def plain():
    checks = lines(r'''
S.TODO = (COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left)) :: ptask_tail*
pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
pstaticcompound.CELL = eps
~pstaticcompound.VERIFY
ptbytes_left = $ptascii("a")
pcompoundstring.RIGHT = VARIABLE $ptascii("rhs") z_rhs
~pcompoundstring.CV /\ ~pcompoundstring.SELF
pcompoundstring.SELECTED = eps
S.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDENTER pstaticcompound pcompoundstring.SITE pcompoundstring.LINE n_prefix
$static_compound_capture(S, pstaticcompound.DECL, pcompoundstring.SITE, pstaticcompound.ENTRY) = (pstaticcompound)
$compound_live_source(S, pcompoundstring)
$call_task_valid(S, COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left))
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left)) = eps
$compound_string_place_nodes(pcompoundstring.PLACE) = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("spare")) = (n_spare)
$lookup(S_global.ENV, $ptascii("spareAlias")) = (n_spare)
S.STORE[n_spare] = DEFINED (PSTRING $ptascii("12"))
n_spare <- S.REFCELLS /\ (HCELL n_spare) <- S.ALLOCATIONS
$heap_owners($heap_graph(S), HCELL n_spare) = 2
''') + guards('S')
    checks += task_forgeries('S', 'pcompoundstring', 'pstaticcompound',
                             'COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left)',
                             'ptask_tail*', 'n_spare')
    checks += lines(r'''
~$static_compound_source(S, pstaticcompound[.CLASS = PORIGIN 999 eps], pcompoundstring.SITE, pcompoundstring.LINE)
~$static_compound_source(S, pstaticcompound[.DECL = PORIGIN 999 eps], pcompoundstring.SITE, pcompoundstring.LINE)
~$static_compound_source(S, pstaticcompound, PORIGIN 999 eps, pcompoundstring.LINE)
~$static_compound_source(S, pstaticcompound, pcompoundstring.SITE, $(pcompoundstring.LINE + 1))
S_replayed = S[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [CCCOMPOUNDENTER pstaticcompound pcompoundstring.SITE pcompoundstring.LINE n_prefix]]
$heap_graph(S_replayed) = $heap_graph(S)
~$class_constant_history_valid(S_replayed)
''')
    checks += seek('S_first', 'S', 0) + lines(r'''
S_first.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring_first) :: ptask_first*
pcompoundstring_first.SELECTED = (n_rhs)
pcompoundstring_first = pcompoundstring[.SELECTED = (n_rhs)]
$class_static_at(S_first.CLASSSTATICS, pstaticcompound.DECL) = (pclassstatic_first)
pclassstatic_first.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("ab")))
S_first_global = $global_table_view(S_first)
$lookup(S_first_global.ENV, $ptascii("alias")) = (n_alias)
n_alias =/= n_spare
S_first.STORE[n_alias] = DEFINED (PSTRING $ptascii("changed1"))
$propref_at(S_first.PROPREFS, n_alias) = (ppropref_first)
ppropref_first.SOURCES = [COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_first]
S_first.CLASSCONSTANTHISTORY[n_retired_first] = CCCOMPOUNDRETIRE pstaticcompound n_alias pcompoundstring.SITE pcompoundstring.LINE n_retire_prefix_first
n_retire_prefix_first = n_prefix
$propref_source_valid(S_first, n_alias, COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_first)
~$propref_source_valid(S_first, n_spare, COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_first)
~$propref_source_valid(S_first, n_alias, COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL pstaticcompound.ENTRY)
$heap_owners($heap_graph(S_first), HCELL n_alias) = 1
$task_nodes(COMPOUND_LIVE_RELEASE pcompoundstring_first) = eps
S_future_retire = S_first[.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDRETIRE pstaticcompound[.ENTRY = n_retired_first] n_alias pcompoundstring.SITE pcompoundstring.LINE n_retire_prefix_first][.CLASSCONSTANTHISTORY[n_retired_first] = CCCOMPOUNDENTER pstaticcompound[.ENTRY = n_retired_first] pcompoundstring.SITE pcompoundstring.LINE n_prefix]
$heap_graph(S_future_retire) = $heap_graph(S_first)
~$class_constant_history_valid(S_future_retire)
''') + guards('S_first')
    checks += task_forgeries('S_first', 'pcompoundstring_first', 'pstaticcompound',
                             'COMPOUND_LIVE_RELEASE pcompoundstring_first',
                             'ptask_first*', 'n_spare')
    checks += seek('S_second', 'S_first', 1) + lines(r'''
S_second.TODO = (COMPOUND_LIVE_PREP pcompoundstring_second (PSTRING ptbytes_second)) :: ptask_second*
pcompoundstring_second.PLACE = STATIC_COMPOUND pstaticcompound_second
pstaticcompound_second.CELL = eps /\ ~pstaticcompound_second.VERIFY
pstaticcompound_second.DECL = pstaticcompound.DECL
pcompoundstring_second.SITE = pcompoundstring.SITE
pcompoundstring_second.LINE = pcompoundstring.LINE
pstaticcompound_second.ENTRY =/= pstaticcompound.ENTRY
ptbytes_second = $ptascii("ab")
S_second.CLASSCONSTANTHISTORY[pstaticcompound_second.ENTRY] = CCCOMPOUNDENTER pstaticcompound_second pcompoundstring.SITE pcompoundstring.LINE n_prefix_second
$call_task_valid(S_second, COMPOUND_LIVE_PREP pcompoundstring_second (PSTRING ptbytes_second))
''') + guards('S_second')
    checks += seek('S_twice', 'S_second', 2) + lines(r'''
$class_static_at(S_twice.CLASSSTATICS, pstaticcompound.DECL) = (pclassstatic_twice)
pclassstatic_twice.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("abb")))
S_twice.STORE[n_alias] = DEFINED (PSTRING $ptascii("changed2"))
$propref_at(S_twice.PROPREFS, n_alias) = (ppropref_twice)
ppropref_twice.SOURCES = [COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_first, COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_second]
n_retired_second =/= n_retired_first
S_twice.CLASSCONSTANTHISTORY[n_retired_second] = CCCOMPOUNDRETIRE pstaticcompound_second n_alias pcompoundstring.SITE pcompoundstring.LINE n_retire_prefix_second
$propref_source_valid(S_twice, n_alias, COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_second)
''') + guards('S_twice')
    checks += seek('S_removed', 'S_twice', 3) + lines(r'''
S_removed.STORE[n_alias] = DEFINED (PSTRING $ptascii("3"))
$propref_at(S_removed.PROPREFS, n_alias) = (ppropref_removed)
ppropref_removed.SOURCES = [COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_first, COMPOUND_CLASS_PROP_SOURCE pstaticcompound.DECL n_retired_second]
S_removed.STORE[n_spare] = DEFINED (PSTRING $ptascii("12"))
$heap_owners($heap_graph(S_removed), HCELL n_spare) = 2
''') + guards('S_removed')
    return checks


def captured():
    checks = lines(r'''
S.TODO = (COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left)) :: ptask_tail*
pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
pstaticcompound.CELL = (n_cell)
~pstaticcompound.VERIFY
ptbytes_left = $ptascii("1")
pcompoundstring.RIGHT = KNOWN (POBJECT n_rhs)
~pcompoundstring.CV /\ ~pcompoundstring.SELF
pcompoundstring.SELECTED = eps
S.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDENTER pstaticcompound pcompoundstring.SITE pcompoundstring.LINE n_prefix
$static_compound_capture(S, pstaticcompound.DECL, pcompoundstring.SITE, pstaticcompound.ENTRY) = (pstaticcompound)
$call_task_valid(S, COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left))
$class_static_at(S.CLASSSTATICS, pstaticcompound.DECL) = (pclassstatic_initial)
pclassstatic_initial.STATE = PROP_VALUE (ALIAS n_cell)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("rawAlias")) = (n_cell)
$lookup(S_global.ENV, $ptascii("spare")) = (n_spare)
$lookup(S_global.ENV, $ptascii("spareAlias")) = (n_spare)
n_cell =/= n_spare
S.STORE[n_spare] = DEFINED (PSTRING $ptascii("12"))
n_spare <- S.REFCELLS /\ (HCELL n_spare) <- S.ALLOCATIONS
$heap_owners($heap_graph(S), HCELL n_cell) = 2
$heap_owners($heap_graph(S), HCELL n_spare) = 2
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring (PSTRING ptbytes_left)) = [HOBJECT n_rhs]
$compound_string_place_nodes(pcompoundstring.PLACE) = eps
$heap_owners($heap_graph(S), HOBJECT n_rhs) = 1
$propref_at(S.PROPREFS, n_cell) = (ppropref_initial)
ppropref_initial.SOURCES = [CLASS_PROP_SOURCE pstaticcompound.DECL]
''') + guards('S')
    checks += seek('S_cast', 'S', 4) + lines(r'''
S_cast.TODO = (STRINGIFY_RESULT n_rhs pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_cast ptbytes_left) :: ptask_cast*
pcompoundstring_cast = pcompoundstring[.SELECTED = (n_rhs)]
S_cast.RESULT = KNOWN (PSTRING $ptascii("2"))
S_cast.STORE[n_cell] = DEFINED (PINT 1)
$propref_at(S_cast.PROPREFS, n_cell) = (ppropref_cast)
ppropref_cast.SOURCES = [CLASS_PROP_SOURCE pstaticcompound.DECL, CLASS_PROP_SOURCE ppropertyid_other]
$heap_owners($heap_graph(S_cast), HCELL n_cell) = 3
$stringify_consumer_receiver_valid(S_cast, n_rhs, COMPOUND_LIVE_RIGHT pcompoundstring_cast ptbytes_left)
S_forged_receiver = S_cast[.TODO = (STRINGIFY_RESULT n_rhs pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_cast[.SELECTED = eps] ptbytes_left) :: ptask_cast*]
$heap_graph(S_forged_receiver) = $heap_graph(S_cast)
~$call_descriptors_valid(S_forged_receiver)
''') + guards('S_cast')
    for suffix, change in [('cell', '.CELL = (n_spare)'),
                           ('verify', '.VERIFY = true'),
                           ('entry', '.ENTRY = |S_cast.CLASSCONSTANTHISTORY|')]:
        bad_record = f'pcompoundstring_cast[.PLACE = STATIC_COMPOUND pstaticcompound[{change}]]'
        bad_state = 'S_cast_bad_' + suffix
        checks += [f'{bad_state} = S_cast[.TODO = (STRINGIFY_RESULT n_rhs pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT {bad_record} ptbytes_left) :: ptask_cast*]',
                   f'$heap_graph({bad_state}) = $heap_graph(S_cast)',
                   f'~$compound_live_source({bad_state}, {bad_record})',
                   f'~$call_descriptors_valid({bad_state})']
    checks += seek('S_written', 'S_cast', 5) + lines(r'''
S_written.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring_cast) :: ptask_release*
S_written.STORE[n_cell] = DEFINED (PSTRING $ptascii("12"))
S_written.RESULT = KNOWN (PSTRING $ptascii("12"))
$propref_at(S_written.PROPREFS, n_cell) = (ppropref_written)
ppropref_written.SOURCES = ppropref_cast.SOURCES
S_written.REFCOERCIONS = [prefcoercion]
prefcoercion.CELL = n_cell
prefcoercion.SITE = pcompoundstring.SITE
prefcoercion.LINE = pcompoundstring.LINE
prefcoercion.VALUE = $ptascii("12")
n_write = $nabs($(|S_written.CLASSCONSTANTHISTORY| - 1))
S_written.CLASSCONSTANTHISTORY[n_write] = CCCOMPOUNDWRITE pstaticcompound pcompoundstring.SITE pcompoundstring.LINE $ptascii("12") n_write_prefix
n_write_prefix = n_prefix
$reference_coercion_row_valid(S_written, prefcoercion)
$reference_coercion_admission(S_written, n_cell, pcompoundstring.SITE, pcompoundstring.LINE, $ptascii("12"))
$static_compound_entry(S_written.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY], pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)
$propref_source_valid(S_written, n_cell, CLASS_PROP_SOURCE ppropertyid_other)
$heap_owners($heap_graph(S_written), HCELL n_cell) = 3
$task_nodes(COMPOUND_LIVE_RELEASE pcompoundstring_cast) = [HOBJECT n_rhs]
$heap_owners($heap_graph(S_written), HOBJECT n_rhs) = 1
S_without = S_written[.REFCOERCIONS = eps]
$heap_graph(S_without) = $heap_graph(S_written)
~$proprefs_valid(S_without)
~$call_descriptors_valid(S_without)
S_future_write = S_written[.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDWRITE pstaticcompound[.ENTRY = n_write] pcompoundstring.SITE pcompoundstring.LINE $ptascii("12") n_write_prefix][.CLASSCONSTANTHISTORY[n_write] = CCCOMPOUNDENTER pstaticcompound[.ENTRY = n_write] pcompoundstring.SITE pcompoundstring.LINE n_prefix]
$heap_graph(S_future_write) = $heap_graph(S_written)
~$class_constant_history_valid(S_future_write)
''') + guards('S_written')
    for suffix, change in [('cell', '.CELL = n_spare'),
                           ('line', '.LINE = $(prefcoercion.LINE + 1)'),
                           ('site', '.SITE = PORIGIN 999 eps'),
                           ('value', '.VALUE = $ptascii("wrong")')]:
        row = f'prefcoercion[{change}]'
        bad_state = 'S_row_bad_' + suffix
        checks += [f'{bad_state} = S_written[.REFCOERCIONS = [{row}]]',
                   f'$heap_graph({bad_state}) = $heap_graph(S_written)',
                   f'~$reference_coercion_row_valid({bad_state}, {row})',
                   f'~$call_descriptors_valid({bad_state})']
    checks += lines(r'''
S_bad_write = S_written[.CLASSCONSTANTHISTORY[n_write] = CCCOMPOUNDWRITE pstaticcompound[.VERIFY = true] pcompoundstring.SITE pcompoundstring.LINE $ptascii("12") n_write_prefix]
$heap_graph(S_bad_write) = $heap_graph(S_written)
~$class_constant_history_valid(S_bad_write)
~$reference_coercion_row_valid(S_bad_write, prefcoercion)
S_duplicate_row = S_written[.REFCOERCIONS = [prefcoercion,prefcoercion]]
$heap_graph(S_duplicate_row) = $heap_graph(S_written)
~$reference_coercions_valid(S_duplicate_row)
''')
    checks += seek('S_freed', 'S_written', 6) + lines(r'''
S_freed.TODO = (COMPOUND_LIVE_DONE pcompoundstring_cast) :: ptask_done*
~((HOBJECT n_rhs) <- S_freed.ALLOCATIONS)
$task_nodes(COMPOUND_LIVE_DONE pcompoundstring_cast) = eps
$compound_live_source(S_freed, pcompoundstring_cast)
~$compound_live_valid(S_freed, pcompoundstring_cast)
$call_task_valid(S_freed, COMPOUND_LIVE_DONE pcompoundstring_cast)
$reference_coercion_row_valid(S_freed, prefcoercion)
''') + guards('S_freed')
    return checks


def render(name, fixture, filename, expected):
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET',
              'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1000)',
              r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
              'S = S_reached[.COMPLETION = NORMAL]']
    checks += plain() if name == CASES[0][0] else captured()
    checks += ['S_zero = $drive_steps(S, 0)', 'S_zero = S[.COMPLETION = BUDGET]',
               'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET'] + guards('S_one')
    checks += ['S_done = $drive(S_one[.COMPLETION = NORMAL], 1000)',
               'S_direct = $drive(S, 1000)', 'S_done = S_direct',
               'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$outputs(S_done.EVENTS) = $ptascii("' + expected + '")'] + guards('S_done')
    cell = 'eps' if name == CASES[0][0] else '(n_cell)'
    stage = ('S.TODO = (COMPOUND_LIVE_PREP pcompoundstring pvalue) :: ptask*'
             ' -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound'
             ' -- if pstaticcompound.CELL = ' + cell)
    text = PREFIX.replace('STAGE', stage) + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks
