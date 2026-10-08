"""Fresh method-selected static compound frontiers and retained selection guards."""
from error_handler_protocol import PREFIX

CASES = [
    ('lexical-and-called-selection', ['scoped-inherited-self-parent-static']),
    ('nested-selection-and-captured-reference', [
        'scoped-nested-called-scope-reentry', 'scoped-static-reference-rebind']),
]

EXTRA = r'''
dec $scoped_phase(pstate, nat) : bool
def $scoped_phase(S, 0) = true
  -- if S.TODO = (COMPOUND_LIVE_PREP pcompoundstring pvalue) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
def $scoped_phase(S, 1) = true
  -- if S.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
def $scoped_phase(S, 2) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (COMPOUND_LIVE_LEFT pcompoundstring) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
def $scoped_phase(S, n) = false -- otherwise
dec $scoped_seek(pstate, nat, nat) : pstate
def $scoped_seek(S, n_phase, n) = S
  -- if $scoped_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scoped_seek(S, n_phase, n) = $scoped_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$scoped_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $scoped_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def lines(text):
    return text.strip().splitlines()


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$class_constant_history_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def start(state, row):
    return [f'{state}_initial = $php_run({row["fixture"]}, 0, {row["filename"]})',
            f'{state}_initial.COMPLETION = BUDGET',
            *seek(state, f'{state}_initial[.COMPLETION = NORMAL]', 0)]


def seek(state, previous, phase):
    return [f'{state}_reached = $scoped_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$scoped_phase({state}, {phase})']


def prep(state, suffix, value):
    return [f'{state}.TODO = (COMPOUND_LIVE_PREP pcompoundstring_{suffix} {value}) :: ptask_{suffix}*',
            f'pcompoundstring_{suffix}.PLACE = STATIC_COMPOUND pstaticcompound_{suffix}',
            f'{state}.CLASSCONSTANTHISTORY[pstaticcompound_{suffix}.ENTRY] = CCCOMPOUNDSELECT pstaticcompound_{suffix} pstaticselection_{suffix} pcompoundstring_{suffix}.SITE pcompoundstring_{suffix}.LINE n_prefix_{suffix}',
            f'$compound_live_source({state}, pcompoundstring_{suffix})',
            f'$call_task_valid({state}, COMPOUND_LIVE_PREP pcompoundstring_{suffix} {value})',
            f'$static_compound_capture({state}, pstaticcompound_{suffix}.DECL, pcompoundstring_{suffix}.SITE, pstaticcompound_{suffix}.ENTRY) = (pstaticcompound_{suffix})']


def selection(state, suffix, scope, called, root):
    return [f'pstaticselection_{suffix}.SCOPE = ({scope})',
            f'pstaticselection_{suffix}.CALLED = ({called})',
            f'pstaticselection_{suffix}.ROOT = {root}',
            f'pstaticcompound_{suffix}.CLASS = {root}',
            f'pstaticselection_{suffix}.CLOSURE = eps',
            f'$origin_child((pcompoundstring_{suffix}.SITE), [PCFIELD 0]) = (pstaticselection_{suffix}.SITE)',
            f'{state}.CURRENT = (pcallcontext_{suffix})',
            f'pcallcontext_{suffix}.LEXICAL_CLASS = ({scope})',
            f'pcallcontext_{suffix}.CALLED_CLASS = ({called})']


def event_forgeries(state, suffix, changes):
    checks = []
    for name, change in changes:
        bad = state + '_' + suffix + '_bad_' + name
        checks += [f'{bad} = {state}[.CLASSCONSTANTHISTORY[pstaticcompound_{suffix}.ENTRY] = CCCOMPOUNDSELECT pstaticcompound_{suffix} pstaticselection_{suffix}[{change}] pcompoundstring_{suffix}.SITE pcompoundstring_{suffix}.LINE n_prefix_{suffix}]',
                   f'$heap_graph({bad}) = $heap_graph({state})',
                   f'~$class_constant_history_valid({bad})',
                   f'~$compound_live_source({bad}, pcompoundstring_{suffix})',
                   f'~$call_descriptors_valid({bad})']
    return checks


def finish(state, expected, resume=True):
    checks = ([f'{state}_zero = $drive_steps({state}, 0)',
            f'{state}_zero = {state}[.COMPLETION = BUDGET]',
            f'{state}_one = $drive_steps({state}, 1)',
            f'{state}_one.COMPLETION = BUDGET',
            f'{state}_done = $drive({state}_one[.COMPLETION = NORMAL], 1000)',
            f'{state}_done = $drive({state}, 1000)'] if resume else
              [f'{state}_done = $drive({state}, 1000)'])
    return checks + [
            f'{state}_done.COMPLETION = NORMAL',
            f'{state}_done.TODO = eps', f'{state}_done.CURRENT = eps',
            f'{state}_done.FRAMES = eps',
            f'$outputs({state}_done.EVENTS) = $ptascii("{expected}")',
            *guards(state + '_done')]


def lexical(row):
    checks = start('S_self', row) + prep('S_self', 'self', '(POBJECT n_left_self)')
    checks += lines(r'''
$class_named(S_self.CLASSNAMES, $ptlc($ptascii("KeywordParentSlotReview19"))) = (porigin_base)
$class_named(S_self.CLASSNAMES, $ptlc($ptascii("KeywordChildSlotReview19"))) = (porigin_child)
$class_named(S_self.CLASSNAMES, $ptlc($ptascii("KeywordGrandSlotReview19"))) = (porigin_grand)
pstaticcompound_self.CELL = eps
pstaticcompound_self.VERIFY
''') + selection('S_self', 'self', 'porigin_base', 'porigin_grand', 'porigin_base') + guards('S_self')
    checks += lines(r'''
$class_static_selection_published([(porigin_base,true),(porigin_child,true),(porigin_grand,true)], pstaticselection_self)
~$class_static_selection_published([(porigin_base,true),(porigin_child,true)], pstaticselection_self)
''')
    checks += event_forgeries('S_self', 'self', [
        ('scope', '.SCOPE = (porigin_child)'),
        ('root', '.ROOT = porigin_grand'),
        ('site', '.SITE = pcompoundstring_self.SITE'),
        ('closure', '.CLOSURE = (CLOSURE_CALL pcompoundstring_self.SITE n_left_self n_left_self porigin_base)')])
    checks += lines(r'''
S_replayed = S_self[.CLASSCONSTANTHISTORY = S_self.CLASSCONSTANTHISTORY ++ [CCCOMPOUNDSELECT pstaticcompound_self pstaticselection_self pcompoundstring_self.SITE pcompoundstring_self.LINE n_prefix_self]]
$heap_graph(S_replayed) = $heap_graph(S_self)
~$class_constant_history_valid(S_replayed)
S_nonmethod = S_self[.CURRENT = (pcallcontext_self[.TARGET = CLOSURE_TARGET n_left_self])]
~$static_compound_method_target(CLOSURE_TARGET n_left_self)
$static_compound_capture(S_nonmethod, pstaticcompound_self.DECL, pcompoundstring_self.SITE, pstaticcompound_self.ENTRY) = eps
''')
    checks += seek('S_written', 'S_self', 1) + lines(r'''
$class_static_at(S_written.CLASSSTATICS, pstaticcompound_self.DECL) = (pclassstatic_written)
pclassstatic_written.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("as")))
S_written.RESULT = KNOWN (PSTRING $ptascii("as"))
$static_compound_source(S_written, pstaticcompound_self, pcompoundstring_self.SITE, pcompoundstring_self.LINE)
''')
    checks += seek('S_parent', '$drive_steps(S_written, 1)[.COMPLETION = NORMAL]', 0)
    checks += prep('S_parent', 'parent', '(POBJECT n_left_parent)')
    checks += selection('S_parent', 'parent', 'porigin_child', 'porigin_grand', 'porigin_base') + guards('S_parent')
    checks += seek('S_parent_written', 'S_parent', 1)
    checks += seek('S_static', '$drive_steps(S_parent_written, 1)[.COMPLETION = NORMAL]', 0)
    checks += prep('S_static', 'static', '(POBJECT n_left_static)')
    checks += selection('S_static', 'static', 'porigin_child', 'porigin_grand', 'porigin_grand') + guards('S_static')
    checks += lines(r'''
~$class_static_selection_published([(porigin_base,true),(porigin_grand,true)], pstaticselection_static)
''')
    checks += event_forgeries('S_static', 'static', [('called', '.CALLED = (porigin_child)')])
    checks += finish('S_static', row['expected_stdout'])
    return checks + lines(r'''
$static_compound_source(S_static_done, pstaticcompound_self, pcompoundstring_self.SITE, pcompoundstring_self.LINE)
$static_compound_source(S_static_done, pstaticcompound_parent, pcompoundstring_parent.SITE, pcompoundstring_parent.LINE)
$static_compound_source(S_static_done, pstaticcompound_static, pcompoundstring_static.SITE, pcompoundstring_static.LINE)
''')


def nested(row):
    checks = start('S_outer', row) + prep('S_outer', 'outer', '(POBJECT n_left_outer)')
    checks += lines(r'''
$class_named(S_outer.CLASSNAMES, $ptlc($ptascii("KeywordOuterBaseReview19"))) = (porigin_outer_base)
$class_named(S_outer.CLASSNAMES, $ptlc($ptascii("KeywordOuterChildReview19"))) = (porigin_outer_child)
$class_named(S_outer.CLASSNAMES, $ptlc($ptascii("KeywordInnerBaseReview19"))) = (porigin_inner_base)
$class_named(S_outer.CLASSNAMES, $ptlc($ptascii("KeywordInnerChildReview19"))) = (porigin_inner_child)
''') + selection('S_outer', 'outer', 'porigin_outer_base', 'porigin_outer_child', 'porigin_outer_child')
    checks += seek('S_inner', '$drive_steps(S_outer, 1)[.COMPLETION = NORMAL]', 0)
    checks += prep('S_inner', 'inner', '(PSTRING ptbytes_inner)')
    checks += selection('S_inner', 'inner', 'porigin_inner_base', 'porigin_inner_child', 'porigin_inner_child')
    checks += lines(r'''
ptbytes_inner = $ptascii("j")
pcompoundstring_inner.RIGHT = KNOWN (POBJECT n_rhs_inner)
pstaticcompound_inner.ENTRY =/= pstaticcompound_outer.ENTRY
S_inner.FRAMES = pframe_callback :: pframe_outer :: pframe_tail*
pframe_outer.TODO = (STRINGIFY_RESULT n_left_outer pcompoundstring_outer.SITE pcompoundstring_outer.LINE) :: (COMPOUND_LIVE_LEFT pcompoundstring_outer_cast) :: ptask_outer_saved*
pcompoundstring_outer_cast = pcompoundstring_outer[.SELECTED = (n_left_outer)]
pframe_outer.CONTEXT = (pcallcontext_outer)
$call_saved_context_valid(S_inner, pframe_outer)
$compound_live_source(S_inner, pcompoundstring_outer_cast)
$static_compound_capture(S_inner, pstaticcompound_outer.DECL, pcompoundstring_outer.SITE, pstaticcompound_outer.ENTRY) = eps
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring_inner (PSTRING ptbytes_inner)) = [HOBJECT n_rhs_inner]
$heap_owners($heap_graph(S_inner), HOBJECT n_rhs_inner) = 1
''') + guards('S_inner')
    checks += event_forgeries('S_inner', 'inner', [('called', '.CALLED = (porigin_outer_child)')])
    checks += event_forgeries('S_inner', 'outer', [('called', '.CALLED = (porigin_inner_child)')])
    checks += finish('S_inner', row['expected_stdout'], resume=False)
    return checks + lines(r'''
$static_compound_source(S_inner_done, pstaticcompound_outer, pcompoundstring_outer.SITE, pcompoundstring_outer.LINE)
$static_compound_source(S_inner_done, pstaticcompound_inner, pcompoundstring_inner.SITE, pcompoundstring_inner.LINE)
''')


def captured(row):
    checks = start('S_alias', row) + prep('S_alias', 'alias', '(POBJECT n_left_alias)')
    checks += lines(r'''
$class_named(S_alias.CLASSNAMES, $ptlc($ptascii("KeywordReferenceBaseReview19"))) = (porigin_ref_base)
$class_named(S_alias.CLASSNAMES, $ptlc($ptascii("KeywordReferenceChildReview19"))) = (porigin_ref_child)
pstaticcompound_alias.CELL = (n_cell)
~pstaticcompound_alias.VERIFY
S_alias_global = $global_table_view(S_alias)
$lookup(S_alias_global.ENV, $ptascii("alias")) = (n_cell)
$class_static_at(S_alias.CLASSSTATICS, pstaticcompound_alias.DECL) = (pclassstatic_alias)
pclassstatic_alias.STATE = PROP_VALUE (ALIAS n_cell)
$heap_owners($heap_graph(S_alias), HCELL n_cell) = 2
''') + selection('S_alias', 'alias', 'porigin_ref_base', 'porigin_ref_child', 'porigin_ref_child') + guards('S_alias')
    checks += seek('S_cast', 'S_alias', 2) + lines(r'''
S_cast.TODO = (STRINGIFY_RESULT n_left_alias pcompoundstring_alias.SITE pcompoundstring_alias.LINE) :: (COMPOUND_LIVE_LEFT pcompoundstring_alias_cast) :: ptask_cast*
pcompoundstring_alias_cast = pcompoundstring_alias[.SELECTED = (n_left_alias)]
S_cast.RESULT = KNOWN (PSTRING $ptascii("a"))
$class_static_at(S_cast.CLASSSTATICS, pstaticcompound_alias.DECL) = (pclassstatic_rebound)
pclassstatic_rebound.STATE = PROP_VALUE (ALIAS n_replacement)
n_replacement =/= n_cell
S_cast.STORE[n_replacement] = DEFINED (PSTRING $ptascii("changed"))
$heap_owners($heap_graph(S_cast), HCELL n_cell) = 1
$compound_live_source(S_cast, pcompoundstring_alias_cast)
$static_compound_capture(S_cast, pstaticcompound_alias.DECL, pcompoundstring_alias.SITE, pstaticcompound_alias.ENTRY) =/= (pstaticcompound_alias)
''')
    checks += seek('S_alias_written', 'S_cast', 1) + lines(r'''
S_alias_written.STORE[n_cell] = DEFINED (PSTRING $ptascii("ab"))
S_alias_written.STORE[n_replacement] = DEFINED (PSTRING $ptascii("changed"))
S_alias_written.RESULT = KNOWN (PSTRING $ptascii("ab"))
S_alias_written.REFCOERCIONS = [prefcoercion]
prefcoercion.CELL = n_cell
prefcoercion.SITE = pcompoundstring_alias.SITE
prefcoercion.LINE = pcompoundstring_alias.LINE
prefcoercion.VALUE = $ptascii("ab")
n_write = $nabs($(|S_alias_written.CLASSCONSTANTHISTORY| - 1))
S_alias_written.CLASSCONSTANTHISTORY[n_write] = CCCOMPOUNDWRITE pstaticcompound_alias pcompoundstring_alias.SITE pcompoundstring_alias.LINE $ptascii("ab") n_prefix_write
$reference_coercion_row_valid(S_alias_written, prefcoercion)
$heap_owners($heap_graph(S_alias_written), HCELL n_cell) = 1
''') + guards('S_alias_written')
    checks += event_forgeries('S_alias_written', 'alias', [('root', '.ROOT = porigin_ref_base')])
    checks += lines(r'''
S_wrong_cell = S_alias_written[.CLASSCONSTANTHISTORY[n_write] = CCCOMPOUNDWRITE pstaticcompound_alias[.CELL = (n_replacement)] pcompoundstring_alias.SITE pcompoundstring_alias.LINE $ptascii("ab") n_prefix_write]
$heap_graph(S_wrong_cell) = $heap_graph(S_alias_written)
~$class_constant_history_valid(S_wrong_cell)
~$reference_coercion_row_valid(S_wrong_cell, prefcoercion)
''')
    return checks + finish('S_alias_written', row['expected_stdout'])


def render(name, sources):
    checks = (lexical(sources[CASES[0][1][0]]) if name == CASES[0][0]
              else nested(sources[CASES[1][1][0]]) + captured(sources[CASES[1][1][1]]))
    text = EXTRA + PREFIX.replace('STAGE', '$scoped_phase(S, 0)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks
