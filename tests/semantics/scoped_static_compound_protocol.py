"""Static compound frontiers and retained class-selection guards."""
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


def seek(state, previous, phase, steps=1000):
    return [f'{state}_reached = $scoped_seek({previous}, {phase}, {steps})',
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


DYNAMIC_CASES = [
    ('dynamic-base-and-scalar-restore', [
        'dynamic-rhs-rebind-before-capture', 'dynamic-helper-string-once']),
    ('dynamic-selected-reference-authority', [
        'dynamic-captured-reference-rebind']),
]

DYNAMIC_EXTRA = r'''
def $scoped_phase(S, 3) = true
  -- if S.TODO = (COMPOUND_APPLY CONCAT (BASE_CLASS_STATIC porigin_root ptbytes) false z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $static_compound_dynamic_name(S, porigin) = (ptbytes)
  -- if $origin_child((porigin), [PCFIELD 1]) = (porigin_right)
  -- if $compiled_read(S, porigin_right) = (PSTRING $ptascii("y"))
'''


def dynamic_selection(state, suffix, class_name):
    return [
        f'$class_named({state}.CLASSNAMES, $ptlc($ptascii("{class_name}"))) = (porigin_{suffix})',
        f'pstaticselection_{suffix}.ROOT = porigin_{suffix}',
        f'pstaticselection_{suffix}.SCOPE = eps /\\ pstaticselection_{suffix}.CALLED = eps /\\ pstaticselection_{suffix}.CLOSURE = eps',
        f'pstaticcompound_{suffix}.CLASS = porigin_{suffix}',
        f'{state}.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$static_compound_dynamic_root({state}, pstaticcompound_{suffix}.DECL, pcompoundstring_{suffix}.SITE) = (porigin_{suffix})',
    ]


def dynamic_base(row, scalar_row):
    checks = start('S_dynamic', row) + prep('S_dynamic', 'dynamic', '(POBJECT n_left_dynamic)')
    checks += dynamic_selection('S_dynamic', 'dynamic', 'DynamicRhsFirstReview19')
    checks += lines(r'''
$class_named(S_dynamic.CLASSNAMES, $ptlc($ptascii("DynamicRhsSecondReview19"))) = (porigin_dynamic_other)
S_dynamic_global = $global_table_view(S_dynamic)
$lookup(S_dynamic_global.ENV, $ptascii("class")) = (n_class_cv)
S_dynamic.STORE[n_class_cv] = DEFINED (PSTRING $ptascii("DynamicRhsSecondReview19"))
pcompoundstring_dynamic.RIGHT = KNOWN (PSTRING $ptascii("b"))
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring_dynamic (POBJECT n_left_dynamic)) = eps
~$class_static_selection_published([(porigin_dynamic_other,true)], pstaticselection_dynamic)
''') + guards('S_dynamic')
    checks += event_forgeries('S_dynamic', 'dynamic', [
        ('root', '.ROOT = porigin_dynamic_other'),
        ('scope', '.SCOPE = (porigin_dynamic)'),
        ('called', '.CALLED = (porigin_dynamic)'),
        ('site', '.SITE = pcompoundstring_dynamic.SITE'),
    ])
    checks += lines(r'''
S_dynamic_cv = S_dynamic[.STORE[n_class_cv] = DEFINED (PSTRING $ptascii("DynamicRhsFirstReview19"))]
$heap_graph(S_dynamic_cv) = $heap_graph(S_dynamic)
$compound_live_source(S_dynamic_cv, pcompoundstring_dynamic)
$static_compound_capture(S_dynamic_cv, pstaticcompound_dynamic.DECL, pcompoundstring_dynamic.SITE, pstaticcompound_dynamic.ENTRY) = (pstaticcompound_dynamic)
S_dynamic_base = S_dynamic[.BASE = BASE_CLASS_STATIC porigin_dynamic_other $ptascii("value")]
$static_compound_capture(S_dynamic_base, pstaticcompound_dynamic.DECL, pcompoundstring_dynamic.SITE, pstaticcompound_dynamic.ENTRY) = eps
~$call_task_valid(S_dynamic_base, COMPOUND_LIVE_PREP pcompoundstring_dynamic (POBJECT n_left_dynamic))
~$call_descriptors_valid(S_dynamic_base)
''')
    checks += finish('S_dynamic', row['expected_stdout'])
    checks += start('S_helper', scalar_row)
    checks += seek('S_scalar', 'S_helper', 3) + guards('S_scalar')
    checks += lines(r'''
S_scalar.TODO = (COMPOUND_APPLY CONCAT (BASE_CLASS_STATIC porigin_scalar ptbytes_scalar) false z_scalar) :: ptask_scalar*
S_scalar.BASE = BASE_VALUE (KNOWN PNULL)
S_scalar_after = $drive_steps(S_scalar, 1)
S_scalar_after.COMPLETION = BUDGET
S_scalar_after.BASE = S_scalar.BASE
S_scalar_after.RESULT = KNOWN (PSTRING $ptascii("xy"))
S_scalar_after.CLASSCONSTANTHISTORY = S_scalar.CLASSCONSTANTHISTORY
$class_static_select(S_scalar_after, porigin_scalar, ptbytes_scalar) = (ppropertydesc_scalar)
$class_static_at(S_scalar_after.CLASSSTATICS, ppropertydesc_scalar.ORIGIN) = (pclassstatic_scalar)
pclassstatic_scalar.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("xy")))
''') + guards('S_scalar_after')
    return checks + ['S_scalar_clean = S_scalar_after[.COMPLETION = NORMAL]'] + finish('S_scalar_clean', scalar_row['expected_stdout'], resume=False)


def dynamic_reference(row):
    checks = start('S_dynamic_alias', row) + prep('S_dynamic_alias', 'dynamic_alias', '(POBJECT n_left_dynamic_alias)')
    checks += dynamic_selection('S_dynamic_alias', 'dynamic_alias', 'DynamicAliasFirstReview19')
    checks += lines(r'''
pstaticcompound_dynamic_alias.CELL = (n_dynamic_old)
~pstaticcompound_dynamic_alias.VERIFY
S_dynamic_alias_global = $global_table_view(S_dynamic_alias)
$lookup(S_dynamic_alias_global.ENV, $ptascii("alias")) = (n_dynamic_old)
''') + guards('S_dynamic_alias')
    checks += seek('S_dynamic_cast', 'S_dynamic_alias', 2) + lines(r'''
S_dynamic_cast.TODO = (STRINGIFY_RESULT n_left_dynamic_alias pcompoundstring_dynamic_alias.SITE pcompoundstring_dynamic_alias.LINE) :: (COMPOUND_LIVE_LEFT pcompoundstring_dynamic_cast) :: ptask_dynamic_cast*
pcompoundstring_dynamic_cast = pcompoundstring_dynamic_alias[.SELECTED = (n_left_dynamic_alias)]
$class_static_at(S_dynamic_cast.CLASSSTATICS, pstaticcompound_dynamic_alias.DECL) = (pclassstatic_dynamic_rebound)
pclassstatic_dynamic_rebound.STATE = PROP_VALUE (ALIAS n_dynamic_replacement)
n_dynamic_replacement =/= n_dynamic_old
n_dynamic_replacement <- S_dynamic_cast.REFCELLS
(HCELL n_dynamic_replacement) <- S_dynamic_cast.ALLOCATIONS
$compound_live_source(S_dynamic_cast, pcompoundstring_dynamic_cast)
''') + guards('S_dynamic_cast')
    for label, changed in [
        ('cell', '.CELL = (n_dynamic_replacement)'),
        ('verify', '.VERIFY = true'),
    ]:
        record = f'pcompoundstring_dynamic_bad_{label}'
        bad = f'S_dynamic_bad_{label}'
        checks += [
            f'{record} = pcompoundstring_dynamic_cast[.PLACE = STATIC_COMPOUND pstaticcompound_dynamic_alias[{changed}]]',
            f'{bad} = S_dynamic_cast[.TODO = (STRINGIFY_RESULT n_left_dynamic_alias pcompoundstring_dynamic_alias.SITE pcompoundstring_dynamic_alias.LINE) :: (COMPOUND_LIVE_LEFT {record}) :: ptask_dynamic_cast*]',
            f'$heap_graph({bad}) = $heap_graph(S_dynamic_cast)',
            f'$class_constant_history_valid({bad})',
            f'~$compound_live_source({bad}, {record})',
            f'~$call_descriptors_valid({bad})',
        ]
    checks += seek('S_dynamic_raw', 'S_dynamic_cast', 1) + lines(r'''
S_dynamic_raw.STORE[n_dynamic_old] = DEFINED (PSTRING $ptascii("ab"))
S_dynamic_raw.STORE[n_dynamic_replacement] = DEFINED (PSTRING $ptascii("changed"))
S_dynamic_raw.REFCOERCIONS = [prefcoercion_dynamic]
prefcoercion_dynamic.CELL = n_dynamic_old
prefcoercion_dynamic.SITE = pcompoundstring_dynamic_alias.SITE
$reference_coercion_row_valid(S_dynamic_raw, prefcoercion_dynamic)
''') + guards('S_dynamic_raw')
    checks += seek('S_dynamic_typed', 'S_dynamic_raw', 0)
    checks += prep('S_dynamic_typed', 'dynamic_typed', '(PINT z_typed_left)')
    checks += dynamic_selection('S_dynamic_typed', 'dynamic_typed', 'DynamicTypedFirstReview19')
    checks += lines(r'''
z_typed_left = 1
pstaticcompound_dynamic_typed.CELL = (n_dynamic_typed)
pstaticcompound_dynamic_typed.VERIFY
pcompoundstring_dynamic_typed.RIGHT = KNOWN (POBJECT n_dynamic_right)
''') + guards('S_dynamic_typed')
    checks += seek('S_dynamic_verified', 'S_dynamic_typed', 1) + lines(r'''
S_dynamic_verified.STORE[n_dynamic_typed] = DEFINED (PINT 12)
S_dynamic_verified.RESULT = KNOWN (PINT 12)
S_dynamic_verified.REFCOERCIONS = S_dynamic_raw.REFCOERCIONS
$static_compound_source(S_dynamic_verified, pstaticcompound_dynamic_typed, pcompoundstring_dynamic_typed.SITE, pcompoundstring_dynamic_typed.LINE)
''') + guards('S_dynamic_verified')
    return checks + finish('S_dynamic_verified', row['expected_stdout'])

COMPUTED_CASES = [
    ('computed-name-timing-and-queued-owners', [
        'computed-property-cv-tmp-timing', 'computed-property-cold-default']),
    ('computed-selection-reference-authority', [
        'computed-property-reference-name', 'computed-property-selected-roots']),
]

COMPUTED_EXTRA = r'''
def $scoped_phase(S, 4) = true
  -- if S.TODO = (COMPOUND_STATIC_NAME pcomputedcompound) :: ptask*
def $scoped_phase(S, 5) = true
  -- if S.TODO = (COMPOUND_STATIC_READY pcomputedcompound porigin ptbytes) :: ptask*
def $scoped_phase(S, 6) = true
  -- if S.TODO = (COMPOUND_APPLY CONCAT (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) false z) :: ptask*
def $scoped_phase(S, 7) = true
  -- if S.TODO = (CLASS_CONST_STATIC poperand ptbytes z) :: (COMPOUND_STATIC_READY pcomputedcompound porigin ptbytes) :: ptask*
'''


def computed_guards(state):
    return [f'$call_descriptors_valid({state})',
            f'$class_constant_history_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def computed_start(state, row, phase=4, steps=1000):
    return [f'{state}_initial = $php_run({row["fixture"]}, 0, {row["filename"]})',
            f'{state}_initial.COMPLETION = BUDGET',
            *seek(state, f'{state}_initial[.COMPLETION = NORMAL]', phase, steps)]


def computed_name(state, suffix):
    return [f'{state}.TODO = (COMPOUND_STATIC_NAME pcomputedcompound_{suffix}) :: ptask_{suffix}*',
            f'$computed_static_valid({state}, pcomputedcompound_{suffix})',
]


def computed_live(state, suffix, value, selected=False):
    checks = [f'{state}.TODO = (COMPOUND_LIVE_PREP pcompoundstring_{suffix} {value}) :: ptask_{suffix}*',
              f'pcompoundstring_{suffix}.PLACE = STATIC_COMPOUND pstaticcompound_{suffix}',
              f'$static_compound_capture({state}, pstaticcompound_{suffix}.DECL, pcompoundstring_{suffix}.SITE, pstaticcompound_{suffix}.ENTRY) = (pstaticcompound_{suffix})']
    if selected:
        checks += [f'{state}.CLASSCONSTANTHISTORY[pstaticcompound_{suffix}.ENTRY] = CCCOMPOUNDSELECT pstaticcompound_{suffix} pstaticselection_{suffix} pcompoundstring_{suffix}.SITE pcompoundstring_{suffix}.LINE n_prefix_{suffix}']
    else:
        checks += [f'{state}.CLASSCONSTANTHISTORY[pstaticcompound_{suffix}.ENTRY] = CCCOMPOUNDENTER pstaticcompound_{suffix} pcompoundstring_{suffix}.SITE pcompoundstring_{suffix}.LINE n_prefix_{suffix}']
    return checks



def computed_finish(state, expected, resume=True):
    checks = ([f'{state}_zero = $drive_steps({state}, 0)',
               f'{state}_zero = {state}[.COMPLETION = BUDGET]',
               f'{state}_one = $drive_steps({state}, 1)',
               f'{state}_one.COMPLETION = BUDGET',
               f'{state}_done = $drive({state}_one[.COMPLETION = NORMAL], 1000)',
               f'{state}_done = $drive({state}, 1000)'] if resume else
              [f'{state}_done = $drive({state}, 1000)'])
    return checks + [f'{state}_done.COMPLETION = NORMAL',
                     f'$outputs({state}_done.EVENTS) = $ptascii("{expected}")',
                     *computed_guards(state + '_done')]

def computed_timing(row, cold_row):
    checks = computed_start('S_producer', row, 6) + computed_guards('S_producer')
    checks += seek('S_cv_name', 'S_producer', 4) + computed_name('S_cv_name', 'cv')
    checks += lines(r'''
pcomputedcompound_cv.NAME = VARIABLE $ptascii("property") z_cv_name
pcomputedcompound_cv.RIGHT = KNOWN (PSTRING $ptascii("s"))
S_cv_global = $global_table_view(S_cv_name)
$lookup(S_cv_global.ENV, $ptascii("property")) = (n_property)
S_cv_name.STORE[n_property] = DEFINED (PSTRING $ptascii("other"))
$task_nodes(COMPOUND_STATIC_NAME pcomputedcompound_cv) = eps
''') + computed_guards('S_cv_name')
    for label, change in [
        ('line', '.LINE = $(pcomputedcompound_cv.LINE + 1)'),
        ('site', '.SITE = porigin_cv_fetch'),
        ('cv_copy', '.NAME = KNOWN (PSTRING $ptascii("other"))'),
        ('rhs_cv', '.RIGHT = VARIABLE $ptascii("property") z_cv_name'),
    ]:
        if label == 'site':
            checks += ['$origin_child((pcomputedcompound_cv.SITE), [PCFIELD 0]) = (porigin_cv_fetch)']
        checks += [f'pcomputedcompound_bad_{label} = pcomputedcompound_cv[{change}]',
                   f'~$computed_static_valid(S_cv_name, pcomputedcompound_bad_{label})',
                   f'~$call_task_valid(S_cv_name, COMPOUND_STATIC_NAME pcomputedcompound_bad_{label})']
    checks += seek('S_cv_ready', 'S_cv_name', 5) + lines(r'''
S_cv_ready.TODO = (COMPOUND_STATIC_READY pcomputedcompound_cv porigin_timing $ptascii("other")) :: ptask_cv*
S_cv_ready.BASE = BASE_CLASS_STATIC porigin_timing $ptascii("other")
''') + computed_guards('S_cv_ready')
    checks += seek('S_cv_live', 'S_cv_ready', 0)
    checks += computed_live('S_cv_live', 'cv_live', '(POBJECT n_other)')
    checks += computed_guards('S_cv_live')
    checks += seek('S_cv_stored', 'S_cv_live', 1)
    checks += seek('S_tmp_name', 'S_cv_stored', 4) + computed_name('S_tmp_name', 'tmp')
    checks += lines(r'''
pcomputedcompound_tmp.NAME = KNOWN (PSTRING $ptascii("value"))
S_tmp_name.STORE[n_property] = DEFINED (PSTRING $ptascii("other"))
''') + computed_guards('S_tmp_name')
    checks += seek('S_tmp_live', 'S_tmp_name', 0)
    checks += computed_live('S_tmp_live', 'tmp_live', '(POBJECT n_value)')
    checks += computed_guards('S_tmp_live')
    checks += computed_finish('S_tmp_live', row['expected_stdout'])
    checks += computed_start('S_cold_name', cold_row) + computed_name('S_cold_name', 'cold')
    checks += computed_guards('S_cold_name')
    checks += lines(r'''
pcomputedcompound_cold.NAME = KNOWN (PSTRING $ptascii("value"))
pcomputedcompound_cold.RIGHT = KNOWN (POBJECT n_cold_rhs)
$task_nodes(COMPOUND_STATIC_NAME pcomputedcompound_cold) = [HOBJECT n_cold_rhs]
(HOBJECT n_cold_rhs) <- S_cold_name.ALLOCATIONS
$computed_static_name_compatible(S_cold_name, pcomputedcompound_cold.SITE, $ptascii("value"))
~$computed_static_name_compatible(S_cold_name, pcomputedcompound_cold.SITE, $ptascii("other"))
$scoped_selector_class(S_cold_name, pcomputedcompound_cold.CLASS) = (porigin_cold)
ptask_cold_work* = $class_constant_static_work(S_cold_name, pcomputedcompound_cold.CLASS, $ptascii("value"), pcomputedcompound_cold.LINE)
ptask_cold_work* =/= eps
S_cold_queued_step = $drive_steps(S_cold_name, 1)
S_cold_queued_step.COMPLETION = BUDGET
S_cold_queued = S_cold_queued_step[.COMPLETION = NORMAL]
S_cold_queued.TODO = ptask_cold_work* ++ [CLASS_CONST_STATIC pcomputedcompound_cold.CLASS $ptascii("value") pcomputedcompound_cold.LINE, COMPOUND_STATIC_READY pcomputedcompound_cold porigin_cold $ptascii("value")] ++ ptask_cold*
$computed_static_marker(S_cold_queued, S_cold_queued.TODO, pcomputedcompound_cold, porigin_cold, $ptascii("value"))
$task_nodes(COMPOUND_STATIC_READY pcomputedcompound_cold porigin_cold $ptascii("value")) = [HOBJECT n_cold_rhs]
S_cold_bad_queue = S_cold_queued[.TODO = ptask_cold_work* ++ [CLASS_CONST_STATIC pcomputedcompound_cold.CLASS $ptascii("value") pcomputedcompound_cold.LINE, COMPOUND_STATIC_READY pcomputedcompound_cold porigin_cold $ptascii("other")] ++ ptask_cold*]
~$computed_static_marker(S_cold_bad_queue, S_cold_bad_queue.TODO, pcomputedcompound_cold, porigin_cold, $ptascii("other"))
~$call_descriptors_valid(S_cold_bad_queue)
''') + computed_guards('S_cold_queued')
    checks += seek('S_cold_marker', 'S_cold_queued', 7) + computed_guards('S_cold_marker')
    checks += seek('S_cold_live', 'S_cold_marker', 0)
    checks += computed_live('S_cold_live', 'cold_live', '(PSTRING ptbytes_cold_left)')
    checks += lines(r'''
ptbytes_cold_left = $ptascii("a")
pcompoundstring_cold_live.RIGHT = KNOWN (POBJECT n_cold_rhs)
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring_cold_live (PSTRING ptbytes_cold_left)) = [HOBJECT n_cold_rhs]
$class_static_select(S_cold_live, pstaticcompound_cold_live.CLASS, $ptascii("other")) = (ppropertydesc_cold_other)
pstaticcompound_cold_wrong = pstaticcompound_cold_live[.DECL = ppropertydesc_cold_other.ORIGIN]
pcompoundstring_cold_wrong = pcompoundstring_cold_live[.PLACE = STATIC_COMPOUND pstaticcompound_cold_wrong]
S_cold_wrong = S_cold_live[.TODO = (COMPOUND_LIVE_PREP pcompoundstring_cold_wrong (PSTRING ptbytes_cold_left)) :: ptask_cold_live*][.CLASSCONSTANTHISTORY[pstaticcompound_cold_live.ENTRY] = CCCOMPOUNDENTER pstaticcompound_cold_wrong pcompoundstring_cold_live.SITE pcompoundstring_cold_live.LINE n_prefix_cold_live]
$static_compound_descriptor(S_cold_wrong, pstaticcompound_cold_wrong, pcompoundstring_cold_live.SITE) = eps
~$class_constant_history_valid(S_cold_wrong)
~$call_descriptors_valid(S_cold_wrong)
''') + computed_guards('S_cold_live')
    return checks + computed_finish('S_cold_live', cold_row['expected_stdout'], resume=False)


def computed_references(row, selected_row):
    checks = computed_start('S_ref_name', row) + computed_name('S_ref_name', 'name_ref')
    checks += lines(r'''
pcomputedcompound_name_ref.NAME = REFERENCE n_original_name
pcomputedcompound_name_ref.RIGHT = KNOWN (PSTRING $ptascii("b"))
$task_nodes(COMPOUND_STATIC_NAME pcomputedcompound_name_ref) = [HCELL n_original_name]
n_original_name <- S_ref_name.REFCELLS
S_ref_global = $global_table_view(S_ref_name)
$lookup(S_ref_global.ENV, $ptascii("property")) = (n_rebound_name)
n_original_name =/= n_rebound_name
S_ref_name.STORE[n_original_name] = DEFINED (PSTRING $ptascii("value"))
S_ref_name.STORE[n_rebound_name] = DEFINED (PSTRING $ptascii("other"))
''') + computed_guards('S_ref_name')
    checks += seek('S_ref_ready', 'S_ref_name', 5) + lines(r'''
S_ref_ready.TODO = (COMPOUND_STATIC_READY pcomputedcompound_name_ref porigin_reference $ptascii("value")) :: ptask_name_ref*
$call_task_valid(S_ref_ready, COMPOUND_STATIC_READY pcomputedcompound_name_ref porigin_reference $ptascii("value"))
''')
    checks += seek('S_ref_live', 'S_ref_ready', 0)
    checks += computed_live('S_ref_live', 'ref_live', '(POBJECT n_ref_left)')
    checks += lines(r'''
pstaticcompound_ref_live.CELL = (n_ref_static)
~pstaticcompound_ref_live.VERIFY
S_ref_cv_changed = S_ref_live[.STORE[n_rebound_name] = DEFINED (PSTRING $ptascii("value"))]
$compound_live_source(S_ref_cv_changed, pcompoundstring_ref_live)
''') + computed_guards('S_ref_live')
    checks += seek('S_ref_written', 'S_ref_live', 1) + lines(r'''
S_ref_written.STORE[n_ref_static] = DEFINED (PSTRING $ptascii("ab"))
$class_static_at(S_ref_written.CLASSSTATICS, pstaticcompound_ref_live.DECL) = (pclassstatic_ref_rebound)
pclassstatic_ref_rebound.STATE = PROP_VALUE (ALIAS n_ref_replacement)
n_ref_replacement =/= n_ref_static
S_ref_written.STORE[n_ref_replacement] = DEFINED (PSTRING $ptascii("changed"))
$static_compound_source(S_ref_written, pstaticcompound_ref_live, pcompoundstring_ref_live.SITE, pcompoundstring_ref_live.LINE)
''') + computed_guards('S_ref_written')
    checks += computed_finish('S_ref_written', row['expected_stdout'])
    checks += computed_start('S_root_name', selected_row) + computed_name('S_root_name', 'root_name')
    checks += lines(r'''
pcomputedcompound_root_name.CLASS = KNOWN (PSTRING $ptascii("ComputedDynamicRootReview19"))
pcomputedcompound_root_name.NAME = VARIABLE $ptascii("property") z_root_name
S_root_global = $global_table_view(S_root_name)
$lookup(S_root_global.ENV, $ptascii("class")) = (n_class_cv)
S_root_name.STORE[n_class_cv] = DEFINED (PSTRING $ptascii("ComputedDynamicDecoyReview19"))
''') + computed_guards('S_root_name')
    checks += seek('S_root_live', 'S_root_name', 0)
    checks += computed_live('S_root_live', 'root_live', '(POBJECT n_root_left)', selected=True)
    checks += lines(r'''
$class_named(S_root_live.CLASSNAMES, $ptlc($ptascii("ComputedDynamicRootReview19"))) = (porigin_dynamic_root)
$class_named(S_root_live.CLASSNAMES, $ptlc($ptascii("ComputedDynamicDecoyReview19"))) = (porigin_dynamic_decoy)
pstaticcompound_root_live.CLASS = porigin_dynamic_root
pstaticselection_root_live.ROOT = porigin_dynamic_root
pstaticselection_root_live.SCOPE = eps /\ pstaticselection_root_live.CALLED = eps
pstaticcompound_root_live.CELL = (n_root_alias)
S_root_bad_event = S_root_live[.CLASSCONSTANTHISTORY[pstaticcompound_root_live.ENTRY] = CCCOMPOUNDSELECT pstaticcompound_root_live pstaticselection_root_live[.ROOT = porigin_dynamic_decoy] pcompoundstring_root_live.SITE pcompoundstring_root_live.LINE n_prefix_root_live]
~$class_constant_history_valid(S_root_bad_event)
~$compound_live_source(S_root_bad_event, pcompoundstring_root_live)
''') + computed_guards('S_root_live')
    checks += seek('S_root_written', 'S_root_live', 1)
    checks += seek('S_keyword_live', 'S_root_written', 0)
    checks += computed_live('S_keyword_live', 'keyword_live', '(PINT z_keyword_left)', selected=True)
    checks += lines(r'''
z_keyword_left = 7
$class_named(S_keyword_live.CLASSNAMES, $ptlc($ptascii("ComputedKeywordRootReview19"))) = (porigin_keyword_base)
$class_named(S_keyword_live.CLASSNAMES, $ptlc($ptascii("ComputedKeywordChildReview19"))) = (porigin_keyword_child)
pstaticselection_keyword_live.SCOPE = (porigin_keyword_base)
pstaticselection_keyword_live.CALLED = (porigin_keyword_child)
pstaticselection_keyword_live.ROOT = porigin_keyword_child
pstaticcompound_keyword_live.CELL = eps
pstaticcompound_keyword_live.VERIFY
''') + computed_guards('S_keyword_live')
    checks += seek('S_keyword_written', 'S_keyword_live', 1) + lines(r'''
S_keyword_written.RESULT = KNOWN (PINT 72)
$class_static_at(S_keyword_written.CLASSSTATICS, pstaticcompound_keyword_live.DECL) = (pclassstatic_keyword_written)
pclassstatic_keyword_written.STATE = PROP_VALUE (DIRECT (PINT 72))
$static_compound_source(S_keyword_written, pstaticcompound_keyword_live, pcompoundstring_keyword_live.SITE, pcompoundstring_keyword_live.LINE)
''') + computed_guards('S_keyword_written')
    return checks



STRINGABLE_CASES = [
    ('stringable-name-receiver-and-cold-owners', [
        'stringable-property-name-borrowed-cv', 'stringable-property-name-cold-owners']),
    ('stringable-name-late-address-and-pending-write', [
        'stringable-property-name-slot-rebind', 'stringable-property-name-pending-masks']),
]

STRINGABLE_EXTRA = r'''
def $scoped_phase(S, 8) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (COMPOUND_STATIC_CAST pcomputedcompound n_selected porigin_root) :: ptask*
def $scoped_phase(S, 9) = true
  -- if S.TODO = (COMPOUND_STATIC_CAST pcomputedcompound n porigin_root) :: ptask*
def $scoped_phase(S, 10) = true
  -- if S.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound n porigin_root ptbytes n_pending?) :: ptask*
def $scoped_phase(S, 11) = true
  -- if S.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress) :: ptask*
  -- if pcomputedaddress.PENDING = eps
def $scoped_phase(S, 13) = true
  -- if S.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress) :: ptask*
  -- if pcomputedaddress.PENDING = (n_pending)
  -- if pcomputedaddress.NAME = $ptascii("text")
def $scoped_phase(S, 14) = true
  -- if S.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound n porigin eps (n_pending)) :: ptask*
def $scoped_phase(S, 15) = true
  -- if S.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress) :: ptask*
  -- if pcomputedaddress.PENDING = (n_pending)
  -- if pcomputedaddress.NAME = $ptascii("reference")
def $scoped_phase(S, 16) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = COMPOUND_STATIC_FETCH pcomputedcompound n porigin ptbytes n_pending?
def $scoped_phase(S, 17) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = THROW_SEARCH n_old
  -- if pdestructionoperation.PENDING =/= eps
def $scoped_phase(S, 18) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("BorrowedDoubleThrowNameReview19::__toString")
'''


def stringable_receiver(borrowed, cold):
    checks = computed_start('S_borrowed', borrowed, 8)
    checks += lines(r'''
S_borrowed.TODO = (STRINGIFY_RESULT n_borrowed porigin_borrowed_string z_borrowed_string) :: (COMPOUND_STATIC_CAST pcomputedcompound_borrowed n_borrowed porigin_borrowed) :: ptask_borrowed*
(porigin_borrowed_string, z_borrowed_string) = (pcomputedcompound_borrowed.SITE, pcomputedcompound_borrowed.LINE)
pcomputedcompound_borrowed.NAME = VARIABLE $ptascii("property") z_property
pcomputedcompound_borrowed.RIGHT = VARIABLE $ptascii("rhs") z_rhs
S_borrowed.RESULT = KNOWN (PSTRING $ptascii("value"))
$computed_static_cast_valid(S_borrowed, pcomputedcompound_borrowed, n_borrowed, porigin_borrowed)
$stringify_pairs_valid(S_borrowed, S_borrowed.TODO)
$task_nodes(COMPOUND_STATIC_CAST pcomputedcompound_borrowed n_borrowed porigin_borrowed) = eps
$heap_owners($heap_graph(S_borrowed), HOBJECT n_borrowed) = 1
S_borrowed_global = $global_table_view(S_borrowed)
$lookup(S_borrowed_global.ENV, $ptascii("property")) = (n_property)
S_borrowed.STORE[n_property] = DEFINED (PSTRING $ptascii("other"))
$lookup(S_borrowed_global.ENV, $ptascii("rhs")) = (n_rhs)
S_borrowed.STORE[n_rhs] = DEFINED (PSTRING $ptascii("after"))
~$computed_static_valid(S_borrowed, pcomputedcompound_borrowed[.NAME = KNOWN (POBJECT n_borrowed)])
~$call_task_valid(S_borrowed, COMPOUND_STATIC_CAST pcomputedcompound_borrowed[.LINE = $(pcomputedcompound_borrowed.LINE + 1)] n_borrowed porigin_borrowed)
''') + computed_guards('S_borrowed')
    checks += seek('S_borrowed_fetch', 'S_borrowed', 10) + lines(r'''
S_borrowed_fetch.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound_borrowed n_borrowed porigin_borrowed $ptascii("value") eps) :: ptask_borrowed*
~((HOBJECT n_borrowed) <- S_borrowed_fetch.ALLOCATIONS)
$ordinary_internal_string_evidence(S_borrowed_fetch, n_borrowed)
$computed_static_cast_valid(S_borrowed_fetch, pcomputedcompound_borrowed, n_borrowed, porigin_borrowed)
$task_nodes(COMPOUND_STATIC_FETCH pcomputedcompound_borrowed n_borrowed porigin_borrowed $ptascii("value") eps) = eps
S_borrowed_fetch.STORE[n_property] = DEFINED (PSTRING $ptascii("other"))
S_borrowed_fetch.STORE[n_rhs] = DEFINED (PSTRING $ptascii("retired"))
$outputs(S_borrowed_fetch.EVENTS) = $ptascii("N;B;D;")
''') + computed_guards('S_borrowed_fetch')
    checks += seek('S_borrowed_address', 'S_borrowed_fetch', 11) + lines(r'''
S_borrowed_address.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_borrowed) :: ptask_borrowed*
pcomputedaddress_borrowed.CLASS = pcomputedcompound_borrowed.CLASS
pcomputedaddress_borrowed.RIGHT = pcomputedcompound_borrowed.RIGHT
pcomputedaddress_borrowed.NAME = $ptascii("value")
S_borrowed_address.BASE = BASE_CLASS_STATIC porigin_borrowed $ptascii("value")
$task_nodes(COMPOUND_STATIC_APPLY pcomputedaddress_borrowed) = eps
$call_task_valid(S_borrowed_address, COMPOUND_STATIC_APPLY pcomputedaddress_borrowed)
pcomputedaddress_other = pcomputedaddress_borrowed[.NAME = $ptascii("other")]
$computed_static_address_valid(S_borrowed_address, pcomputedaddress_other)
~$call_task_valid(S_borrowed_address, COMPOUND_STATIC_APPLY pcomputedaddress_other)
S_borrowed_wrong = S_borrowed_address[.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_other) :: ptask_borrowed*]
~$call_descriptors_valid(S_borrowed_wrong)
~$call_task_valid(S_borrowed_address[.BASE = BASE_VALUE (KNOWN PNULL)], COMPOUND_STATIC_APPLY pcomputedaddress_borrowed)
''') + computed_guards('S_borrowed_address')
    checks += computed_finish('S_borrowed_address', borrowed['expected_stdout'])
    checks += computed_start('S_cold_pin', cold, 8) + lines(r'''
S_cold_pin.TODO = (STRINGIFY_RESULT n_cold_name porigin_cold_string z_cold_string) :: (COMPOUND_STATIC_CAST pcomputedcompound_cold_name n_cold_name porigin_cold_child) :: ptask_cold_name*
(porigin_cold_string, z_cold_string) = (pcomputedcompound_cold_name.SITE, pcomputedcompound_cold_name.LINE)
pcomputedcompound_cold_name.NAME = KNOWN (POBJECT n_cold_name)
pcomputedcompound_cold_name.RIGHT = KNOWN (POBJECT n_cold_right)
n_cold_name =/= n_cold_right
$task_nodes(COMPOUND_STATIC_CAST pcomputedcompound_cold_name n_cold_name porigin_cold_child) = [HOBJECT n_cold_name, HOBJECT n_cold_right]
$heap_owners($heap_graph(S_cold_pin), HOBJECT n_cold_name) = 2
$heap_owners($heap_graph(S_cold_pin), HOBJECT n_cold_right) = 1
~$computed_static_cast_valid(S_cold_pin, pcomputedcompound_cold_name, n_cold_right, porigin_cold_child)
''') + computed_guards('S_cold_pin')
    checks += seek('S_cold_cast', 'S_cold_pin', 9) + lines(r'''
ptask_cold_name_work* = $class_constant_static_work(S_cold_cast, pcomputedcompound_cold_name.CLASS, $ptascii("value"), pcomputedcompound_cold_name.LINE)
ptask_cold_name_work* =/= eps
S_cold_name_queued = $drive_steps(S_cold_cast, 1)[.COMPLETION = NORMAL]
S_cold_name_queued.TODO[|ptask_cold_name_work*|] = CLASS_CONST_SELECTED pstaticselection_cold_name $ptascii("value") pcomputedcompound_cold_name.LINE
S_cold_name_queued.TODO = ptask_cold_name_work* ++ [CLASS_CONST_SELECTED pstaticselection_cold_name $ptascii("value") pcomputedcompound_cold_name.LINE, COMPOUND_STATIC_FETCH pcomputedcompound_cold_name n_cold_name porigin_cold_child $ptascii("value") eps] ++ ptask_cold_name*
pstaticselection_cold_name.ROOT = porigin_cold_child
$class_static_selection_valid(S_cold_name_queued, pstaticselection_cold_name)
$computed_static_fetch_marker(S_cold_name_queued, S_cold_name_queued.TODO, pcomputedcompound_cold_name, n_cold_name, porigin_cold_child, $ptascii("value"), eps)
$computed_static_fetch_pair(S_cold_name_queued.TODO[|ptask_cold_name_work*|:2], pcomputedcompound_cold_name, n_cold_name, porigin_cold_child, $ptascii("value"), eps)
~$computed_static_fetch_pair(S_cold_name_queued.TODO[|ptask_cold_name_work*|:2], pcomputedcompound_cold_name, n_cold_name, porigin_cold_child, $ptascii("value"), (n_cold_name))
$task_nodes(COMPOUND_STATIC_FETCH pcomputedcompound_cold_name n_cold_name porigin_cold_child $ptascii("value") eps) = [HOBJECT n_cold_name, HOBJECT n_cold_right]
S_cold_marker_wrong = S_cold_name_queued[.TODO = ptask_cold_name_work* ++ [CLASS_CONST_SELECTED pstaticselection_cold_name $ptascii("value") $(pcomputedcompound_cold_name.LINE + 1), COMPOUND_STATIC_FETCH pcomputedcompound_cold_name n_cold_name porigin_cold_child $ptascii("value") eps] ++ ptask_cold_name*]
~$computed_static_fetch_marker(S_cold_marker_wrong, S_cold_marker_wrong.TODO, pcomputedcompound_cold_name, n_cold_name, porigin_cold_child, $ptascii("value"), eps)
~$call_descriptors_valid(S_cold_marker_wrong)
''') + computed_guards('S_cold_name_queued')
    checks += seek('S_cold_name_address', 'S_cold_name_queued', 11) + lines(r'''
S_cold_name_address.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_cold_name) :: ptask_cold_name*
~((HOBJECT n_cold_name) <- S_cold_name_address.ALLOCATIONS)
pcomputedaddress_cold_name.RIGHT = KNOWN (POBJECT n_cold_right)
$task_nodes(COMPOUND_STATIC_APPLY pcomputedaddress_cold_name) = [HOBJECT n_cold_right]
$heap_owners($heap_graph(S_cold_name_address), HOBJECT n_cold_right) = 1
$outputs(S_cold_name_address.EVENTS) = $ptascii("H;Q;N;D:c;")
''') + computed_guards('S_cold_name_address')
    return checks


def stringable_late_address(alias, pending):
    checks = computed_start('S_alias_fetch', alias, 10) + lines(r'''
S_alias_fetch.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound_alias_name n_alias_name porigin_alias_root $ptascii("value") eps) :: ptask_alias_name*
pcomputedcompound_alias_name.NAME = KNOWN (POBJECT n_alias_name)
$class_named(S_alias_fetch.CLASSNAMES, $ptlc($ptascii("NameRebindSlotReview19"))) = (porigin_alias_root)
$class_static_select(S_alias_fetch, porigin_alias_root, $ptascii("value")) = (ppropertydesc_alias_name)
$class_static_at(S_alias_fetch.CLASSSTATICS, ppropertydesc_alias_name.ORIGIN) = (pclassstatic_before_name)
pclassstatic_before_name.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("a")))
S_alias_global = $global_table_view(S_alias_fetch)
$lookup(S_alias_global.ENV, $ptascii("class")) = (n_class_name_cv)
S_alias_fetch.STORE[n_class_name_cv] = DEFINED (PSTRING $ptascii("NameTypedRebindSlotReview19"))
$heap_owners($heap_graph(S_alias_fetch), HOBJECT n_alias_name) = 1
''') + computed_guards('S_alias_fetch')
    checks += seek('S_alias_operation', 'S_alias_fetch', 16) + lines(r'''
S_alias_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_alias_name) :: ptask_alias_operation_tail*
S_alias_operation.DESTRUCTION.OPERATIONS = pdestructionoperation_alias_name :: pdestructionoperation_alias_tail*
~$foreach_bind_commit_tasks(S_alias_operation.TODO)
pdestructionoperation_alias_bad = pdestructionoperation_alias_name[.ORIGIN = eps]
S_alias_bad_operation = S_alias_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_alias_bad) :: ptask_alias_operation_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_alias_bad :: pdestructionoperation_alias_tail*]
~$foreach_bind_pending_filtered_tasks(S_alias_bad_operation, n_class_name_cv, false, S_alias_bad_operation.TODO)
~$destructor_operation_valid(S_alias_bad_operation, pdestructionoperation_alias_bad)
~$call_descriptors_valid(S_alias_bad_operation)
''') + computed_guards('S_alias_operation')
    checks += seek('S_alias_address', 'S_alias_operation', 11) + lines(r'''
S_alias_address.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_alias_name) :: ptask_alias_name*
pcomputedaddress_alias_name.ROOT = porigin_alias_root
~((HOBJECT n_alias_name) <- S_alias_address.ALLOCATIONS)
$class_static_at(S_alias_address.CLASSSTATICS, ppropertydesc_alias_name.ORIGIN) = (pclassstatic_after_name)
pclassstatic_after_name.STATE = PROP_VALUE (ALIAS n_alias_slot)
S_alias_address.STORE[n_alias_slot] = DEFINED (PSTRING $ptascii("old"))
$call_task_valid(S_alias_address, COMPOUND_STATIC_APPLY pcomputedaddress_alias_name)
S_alias_written = $drive_steps(S_alias_address, 1)[.COMPLETION = NORMAL]
S_alias_written.STORE[n_alias_slot] = DEFINED (PSTRING $ptascii("oldb"))
S_alias_written.RESULT = KNOWN (PSTRING $ptascii("oldb"))
''') + computed_guards('S_alias_address')
    checks += seek('S_typed_name_fetch', 'S_alias_written', 10) + lines(r'''
S_typed_name_fetch.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound_typed_name n_typed_name porigin_typed_name_root $ptascii("value") eps) :: ptask_typed_name*
$class_static_select(S_typed_name_fetch, porigin_typed_name_root, $ptascii("value")) = (ppropertydesc_typed_name)
$class_static_at(S_typed_name_fetch.CLASSSTATICS, ppropertydesc_typed_name.ORIGIN) = (pclassstatic_typed_before)
pclassstatic_typed_before.STATE = PROP_VALUE (ALIAS n_typed_original)
S_typed_name_fetch.STORE[n_typed_original] = DEFINED (PINT 1)
''')
    checks += seek('S_typed_name_address', 'S_typed_name_fetch', 11) + lines(r'''
S_typed_name_address.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_typed_name) :: ptask_typed_name*
$class_static_at(S_typed_name_address.CLASSSTATICS, ppropertydesc_typed_name.ORIGIN) = (pclassstatic_typed_after)
pclassstatic_typed_after.STATE = PROP_VALUE (ALIAS n_typed_replacement)
n_typed_original =/= n_typed_replacement
S_typed_name_address.STORE[n_typed_original] = DEFINED (PINT 1)
S_typed_name_address.STORE[n_typed_replacement] = DEFINED (PINT 7)
S_typed_name_written = $drive_steps(S_typed_name_address, 1)[.COMPLETION = NORMAL]
S_typed_name_written.STORE[n_typed_original] = DEFINED (PINT 1)
S_typed_name_written.STORE[n_typed_replacement] = DEFINED (PINT 72)
S_typed_name_written.RESULT = KNOWN (PINT 72)
''') + computed_guards('S_typed_name_address')
    # Four earlier pending operations precede this reference frontier.
    checks += computed_start('S_mask_reference', pending, 15, steps=2000) + lines(r'''
S_mask_reference.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_mask_reference) :: ptask_mask_reference*
pcomputedaddress_mask_reference.PENDING = (n_mask_reference_pending)
$class_static_select(S_mask_reference, pcomputedaddress_mask_reference.ROOT, pcomputedaddress_mask_reference.NAME) = (ppropertydesc_mask_reference)
$class_static_at(S_mask_reference.CLASSSTATICS, ppropertydesc_mask_reference.ORIGIN) = (pclassstatic_mask_reference)
pclassstatic_mask_reference.STATE = PROP_VALUE (ALIAS n_mask_reference)
S_mask_reference.STORE[n_mask_reference] = DEFINED (PINT 7)
$computed_static_pending_writer(S_mask_reference[.ORIGIN = (pcomputedaddress_mask_reference.SITE)], pcomputedaddress_mask_reference)
$propref_conversion(S_mask_reference[.ORIGIN = (pcomputedaddress_mask_reference.SITE)], ppropertydesc_mask_reference.TYPE, PSTRING $ptascii("72"), false) = TYPEREJECT
''') + computed_guards('S_mask_reference')
    checks += seek('S_mask_raw', 'S_mask_reference', 13) + lines(r'''
S_mask_raw.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_mask_raw) :: ptask_mask_raw*
pcomputedaddress_mask_raw.PENDING = (n_mask_raw_pending)
$class_static_select(S_mask_raw, pcomputedaddress_mask_raw.ROOT, pcomputedaddress_mask_raw.NAME) = (ppropertydesc_mask_raw)
$class_static_at(S_mask_raw.CLASSSTATICS, ppropertydesc_mask_raw.ORIGIN) = (pclassstatic_mask_raw)
pclassstatic_mask_raw.STATE = PROP_VALUE (ALIAS n_mask_raw)
S_mask_raw.STORE[n_mask_raw] = DEFINED (PSTRING $ptascii("a"))
n_mask_raw =/= n_mask_reference
$task_nodes(COMPOUND_STATIC_APPLY pcomputedaddress_mask_raw) = [HOBJECT n_mask_raw_pending]
S_mask_raw_place = $compound_location(S_mask_raw[.ORIGIN = (pcomputedaddress_mask_raw.SITE)], BASE_CLASS_STATIC pcomputedaddress_mask_raw.ROOT pcomputedaddress_mask_raw.NAME, pcomputedaddress_mask_raw.LINE)
$static_compound_capture(S_mask_raw_place, ppropertydesc_mask_raw.ORIGIN, pcomputedaddress_mask_raw.SITE, |S_mask_raw_place.CLASSCONSTANTHISTORY|) = (pstaticcompound_mask_raw)
pstaticcompound_mask_raw.CELL = (n_mask_raw)
~pstaticcompound_mask_raw.VERIFY
S_mask_raw_entry = S_mask_raw_place[.LOCATION = STATIC_COMPOUND pstaticcompound_mask_raw][.CLASSCONSTANTHISTORY = S_mask_raw_place.CLASSCONSTANTHISTORY ++ [$static_compound_enter_event(S_mask_raw_place, pstaticcompound_mask_raw, pcomputedaddress_mask_raw.SITE, pcomputedaddress_mask_raw.LINE)]][.RESULT = KNOWN (PSTRING $ptascii("a2"))]
$reference_coercion_admission(S_mask_raw_entry, n_mask_raw, pcomputedaddress_mask_raw.SITE, pcomputedaddress_mask_raw.LINE, $ptascii("a2"))
(HCELL n_mask_reference) <- S_mask_raw_entry.ALLOCATIONS
n_mask_reference <- S_mask_raw_entry.REFCELLS
S_mask_raw_foreign = S_mask_raw_entry[.LOCATION = STATIC_COMPOUND pstaticcompound_mask_raw[.CELL = (n_mask_reference)]]
~$reference_coercion_admission(S_mask_raw_foreign, n_mask_reference, pcomputedaddress_mask_raw.SITE, pcomputedaddress_mask_raw.LINE, $ptascii("a2"))
S_mask_raw_verify = S_mask_raw_entry[.LOCATION = STATIC_COMPOUND pstaticcompound_mask_raw[.VERIFY = true]]
~$reference_coercion_admission(S_mask_raw_verify, n_mask_raw, pcomputedaddress_mask_raw.SITE, pcomputedaddress_mask_raw.LINE, $ptascii("a2"))
S_mask_raw_no_pending = S_mask_raw_entry[.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress_mask_raw[.PENDING = eps]) :: ptask_mask_raw*]
~$reference_coercion_admission(S_mask_raw_no_pending, n_mask_raw, pcomputedaddress_mask_raw.SITE, pcomputedaddress_mask_raw.LINE, $ptascii("a2"))
S_mask_raw_zero = $drive_steps(S_mask_raw, 0)
S_mask_raw_zero = S_mask_raw[.COMPLETION = BUDGET]
S_mask_raw_step = $drive_steps(S_mask_raw, 1)
S_mask_raw_step.COMPLETION = BUDGET
S_mask_raw_written = S_mask_raw_step[.COMPLETION = NORMAL]
S_mask_raw_written.TODO = (THROW_SEARCH n_mask_raw_pending) :: ptask_mask_raw*
S_mask_raw_written.STORE[n_mask_raw] = DEFINED (PSTRING $ptascii("a2"))
$reference_coercion_at(S_mask_raw_written.REFCOERCIONS, n_mask_raw) = (prefcoercion_mask_raw)
prefcoercion_mask_raw.VALUE = $ptascii("a2")
$reference_coercion_row_valid(S_mask_raw_written, prefcoercion_mask_raw)
$proprefs_valid(S_mask_raw_written)
S_mask_raw_written.CLASSCONSTANTHISTORY = S_mask_raw.CLASSCONSTANTHISTORY ++ [$static_compound_enter_event(S_mask_raw_place, pstaticcompound_mask_raw, pcomputedaddress_mask_raw.SITE, pcomputedaddress_mask_raw.LINE), CCCOMPOUNDWRITE pstaticcompound_mask_raw pcomputedaddress_mask_raw.SITE pcomputedaddress_mask_raw.LINE $ptascii("a2") (|S_mask_raw.DECLARATIONS|)]
''') + computed_guards('S_mask_raw') + computed_guards('S_mask_raw_written')
    checks += seek('S_mask_failed_method', 'S_mask_raw_written', 18) + lines(r'''
S_mask_failed_method.CURRENT = (pcallcontext_mask_failed_method)
''')
    checks += seek('S_mask_failed_operation', 'S_mask_failed_method', 17) + lines(r'''
S_mask_failed_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_failed) :: ptask_mask_failed_operation*
S_mask_failed_operation.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_failed :: pdestructionoperation_mask_tail*
pdestructionoperation_mask_failed.SOURCE = THROW_SEARCH n_mask_cast
pdestructionoperation_mask_failed.PENDING = (n_mask_drop)
pdestructionoperation_mask_failed.COMPLETION = NORMAL
pdestructionoperation_mask_failed.VALUE = KNOWN PNULL
pdestructionoperation_mask_failed.CALLER = S_mask_failed_operation.CURRENT
pdestructionoperation_mask_failed.CALLER =/= (pcallcontext_mask_failed_method)
$destructor_operation_valid(S_mask_failed_operation, pdestructionoperation_mask_failed)
$call_task_valid(S_mask_failed_operation, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_failed)
$computed_static_throw_fetch(ptask_mask_failed_operation*, pdestructionoperation_mask_failed.ORIGIN, n_mask_cast) = (ptask_mask_cast_fetch)
ptask_mask_cast_fetch = COMPOUND_STATIC_FETCH pcomputedcompound_mask_cast n_mask_cast_receiver porigin_mask_cast_root ptbytes_mask_cast n_mask_cast_pending?
ptbytes_mask_cast = eps
n_mask_cast_pending? = (n_mask_cast)
pdestructionoperation_mask_failed.ORIGIN = $origin_child((pcomputedcompound_mask_cast.SITE), [PCFIELD 0])
$computed_static_throw_fetch((CLASS_CONST_BIND porigin_mask_cast_root) :: ptask_mask_failed_operation*, pdestructionoperation_mask_failed.ORIGIN, n_mask_cast) = (ptask_mask_cast_fetch)
$computed_static_fetch_pending([CLASS_CONST_BIND porigin_mask_cast_root, ptask_mask_cast_fetch, ORIGIN_RETURN eps], ptask_mask_cast_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_mask_cast n_mask_cast_receiver porigin_mask_cast_root eps (n_mask_drop)) = [CLASS_CONST_BIND porigin_mask_cast_root, COMPOUND_STATIC_FETCH pcomputedcompound_mask_cast n_mask_cast_receiver porigin_mask_cast_root eps (n_mask_drop), ORIGIN_RETURN eps]
ptask_mask_empty_pending* = $computed_static_fetch_pending(ptask_mask_failed_operation*, ptask_mask_cast_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_mask_cast n_mask_cast_receiver porigin_mask_cast_root eps eps)
$computed_static_throw_fetch(ptask_mask_empty_pending*, pdestructionoperation_mask_failed.ORIGIN, n_mask_cast) = eps
$computed_static_throw_fetch(ptask_mask_failed_operation*, pdestructionoperation_mask_failed.ORIGIN, n_mask_drop) = eps
$computed_static_throw_fetch(ptask_mask_failed_operation*, (pcomputedcompound_mask_cast.SITE), n_mask_cast) = eps
ptask_mask_nonempty_name* = $computed_static_fetch_pending(ptask_mask_failed_operation*, ptask_mask_cast_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_mask_cast n_mask_cast_receiver porigin_mask_cast_root $ptascii("text") (n_mask_cast))
$computed_static_throw_fetch(ptask_mask_nonempty_name*, pdestructionoperation_mask_failed.ORIGIN, n_mask_cast) = eps
S_mask_failed_cleanup = $eager_cleanup_finish(S_mask_failed_operation, pdestructionoperation_mask_failed)[.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_tail*]
S_mask_failed_caller = $destructor_pending_finish(S_mask_failed_cleanup, pdestructionoperation_mask_failed[.CALLER = (pcallcontext_mask_failed_method)], n_mask_drop, ptask_mask_failed_operation*)
S_mask_failed_caller.TODO = (THROW_SEARCH n_mask_drop) :: ptask_mask_failed_operation*
S_mask_failed_source = $destructor_pending_finish(S_mask_failed_cleanup, pdestructionoperation_mask_failed[.SOURCE = THROW_SEARCH n_mask_drop], n_mask_drop, ptask_mask_failed_operation*)
S_mask_failed_source.TODO = (THROW_SEARCH n_mask_drop) :: ptask_mask_failed_operation*
S_mask_failed_origin = $destructor_pending_finish(S_mask_failed_cleanup, pdestructionoperation_mask_failed[.ORIGIN = (pcomputedcompound_mask_cast.SITE)], n_mask_drop, ptask_mask_failed_operation*)
S_mask_failed_origin.TODO = (THROW_SEARCH n_mask_drop) :: ptask_mask_failed_operation*
$computed_static_throw_projection(S_mask_failed_operation, pdestructionoperation_mask_failed)
pdestructionoperation_mask_failed.BASE = BASE_CLASS_STATIC porigin_mask_cast_root eps
S_mask_failed_view = $call_after_origin(S_mask_failed_operation, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_failed)
S_mask_failed_view.TODO = ptask_mask_failed_operation*
S_mask_failed_view.BASE = pdestructionoperation_mask_failed.BASE
S_mask_failed_view.RESULT = S_mask_failed_operation.RESULT
S_mask_failed_view.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_tail*
$call_task_valid(S_mask_failed_view, ptask_mask_cast_fetch)
pdestructionoperation_mask_bad_base = pdestructionoperation_mask_failed[.BASE = BASE_VALUE (KNOWN PNULL)]
S_mask_failed_bad_base = S_mask_failed_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_bad_base) :: ptask_mask_failed_operation*][.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_bad_base :: pdestructionoperation_mask_tail*]
~$computed_static_throw_projection(S_mask_failed_bad_base, pdestructionoperation_mask_bad_base)
pdestructionoperation_mask_bad_source = pdestructionoperation_mask_failed[.SOURCE = THROW_SEARCH n_mask_drop]
S_mask_failed_bad_source = S_mask_failed_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_bad_source) :: ptask_mask_failed_operation*][.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_bad_source :: pdestructionoperation_mask_tail*]
~$computed_static_throw_projection(S_mask_failed_bad_source, pdestructionoperation_mask_bad_source)
pdestructionoperation_mask_bad_origin = pdestructionoperation_mask_failed[.ORIGIN = (pcomputedcompound_mask_cast.SITE)]
S_mask_failed_bad_origin = S_mask_failed_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_bad_origin) :: ptask_mask_failed_operation*][.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_bad_origin :: pdestructionoperation_mask_tail*]
~$computed_static_throw_projection(S_mask_failed_bad_origin, pdestructionoperation_mask_bad_origin)
pdestructionoperation_mask_bad_caller = pdestructionoperation_mask_failed[.CALLER = (pcallcontext_mask_failed_method)]
S_mask_failed_bad_caller = S_mask_failed_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_bad_caller) :: ptask_mask_failed_operation*][.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_bad_caller :: pdestructionoperation_mask_tail*]
~$computed_static_throw_projection(S_mask_failed_bad_caller, pdestructionoperation_mask_bad_caller)
~$computed_static_throw_projection(S_mask_failed_operation[.DESTRUCTION.OPERATIONS = pdestructionoperation_mask_tail*], pdestructionoperation_mask_failed)
~$computed_static_throw_projection(S_mask_failed_operation[.TODO = ptask_mask_failed_operation*], pdestructionoperation_mask_failed)
~$computed_static_throw_projection(S_mask_failed_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_failed) :: ptask_mask_empty_pending*], pdestructionoperation_mask_failed)
~$computed_static_throw_projection(S_mask_failed_operation[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mask_failed) :: ptask_mask_nonempty_name*], pdestructionoperation_mask_failed)
''') + computed_guards('S_mask_failed_operation')
    checks += seek('S_mask_failed_fetch', 'S_mask_failed_operation', 14) + lines(r'''
S_mask_failed_fetch.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound_mask_failed n_mask_failed porigin_mask_failed eps (n_mask_drop)) :: ptask_mask_failed*
pcomputedcompound_mask_failed.NAME = VARIABLE $ptascii("borrowedProperty") z_mask_property
~((HOBJECT n_mask_failed) <- S_mask_failed_fetch.ALLOCATIONS)
$ordinary_internal_string_evidence(S_mask_failed_fetch, n_mask_failed)
$throwable_field(S_mask_failed_fetch, n_mask_drop, "message") = PSTRING $ptascii("drop")
$throwable_previous_id(S_mask_failed_fetch, n_mask_drop) = (n_mask_cast)
$throwable_field(S_mask_failed_fetch, n_mask_cast, "message") = PSTRING $ptascii("cast")
S_mask_failed_read = $class_static_read(S_mask_failed_fetch, porigin_mask_failed, eps, pcomputedcompound_mask_failed.LINE)
S_mask_failed_error = $computed_static_pending_end(S_mask_failed_read[.TODO = eps], (n_mask_drop), ptask_mask_failed*)
S_mask_failed_error.COMPLETION = THROWING n_mask_lookup
$throwable_previous_id(S_mask_failed_error, n_mask_lookup) = (n_mask_drop)
$throwable_previous_id(S_mask_failed_error, n_mask_drop) = (n_mask_cast)
$computed_static_fetch_pair([CLASS_CONST_STATIC pcomputedcompound_mask_failed.CLASS eps pcomputedcompound_mask_failed.LINE, COMPOUND_STATIC_FETCH pcomputedcompound_mask_failed n_mask_failed porigin_mask_failed eps (n_mask_drop)], pcomputedcompound_mask_failed, n_mask_failed, porigin_mask_failed, eps, (n_mask_drop))
~$computed_static_fetch_pair([CLASS_CONST_STATIC pcomputedcompound_mask_failed.CLASS eps pcomputedcompound_mask_failed.LINE, COMPOUND_STATIC_FETCH pcomputedcompound_mask_failed n_mask_failed porigin_mask_failed eps (n_mask_drop)], pcomputedcompound_mask_failed, n_mask_failed, porigin_mask_failed, eps, (n_mask_cast))
$call_task_valid(S_mask_failed_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_mask_failed n_mask_failed porigin_mask_failed eps (n_mask_drop))
~$call_task_valid(S_mask_failed_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_mask_failed n_mask_failed porigin_mask_failed eps (|S_mask_failed_fetch.OBJECTS|))
''') + computed_guards('S_mask_failed_fetch')
    checks += computed_finish('S_mask_failed_fetch', pending['expected_stdout'])
    return checks


COLD_EXTRA = r'''
def $scoped_seek(S, n_phase, 0) = S
  -- if ~$scoped_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scoped_phase(S, 19) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ColdDoubleNameReview20::__toString")
def $scoped_phase(S, 20) = true
  -- if S.TODO = (THROW_SEARCH n_lookup) :: ptask*
  -- if $string_bytes($throwable_field(S, n_lookup, "message")) = ($ptascii("Access to undeclared static property ColdDoubleNameSlotReview20::$"))
'''


def unchanged_cold(state):
    return [f'~$class_constant_table_done({state}, porigin_cold)',
            f'$class_static_at({state}.CLASSSTATICS, ppropertydesc_cold.ORIGIN) = (pclassstatic_cold)',
            f'$class_constant_static_work({state}, pcomputedcompound_cold.CLASS, eps, pcomputedcompound_cold.LINE) = eps',
            f'$class_constant_static_work({state}, pcomputedcompound_cold.CLASS, $ptascii("value"), pcomputedcompound_cold.LINE) =/= eps']


def cold_double_throw(fixture, filename, expected):
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET']
    checks += seek('S_method', 'S_initial', 19) + lines(r'''
S_method.CURRENT = (pcallcontext_method)
pcallcontext_method.TARGET = METHOD_TARGET n_name porigin_method
pcallcontext_method.INSTANCE = eps
pcallcontext_method.RECEIVER = (n_name)
(HOBJECT n_name) <- S_method.ALLOCATIONS
$outputs(S_method.EVENTS) = $ptascii("Q;N;")
S_global = $global_table_view(S_method)
$lookup(S_global.ENV, $ptascii("name")) = (n_name_cell)
S_method.STORE[n_name_cell] = DEFINED pvalue_name
$string_bytes(pvalue_name) = ($ptascii("other"))
$lookup(S_global.ENV, $ptascii("cast")) = (n_cast_cell)
S_method.STORE[n_cast_cell] = DEFINED (POBJECT n_cast)
$lookup(S_global.ENV, $ptascii("drop")) = (n_drop_cell)
S_method.STORE[n_drop_cell] = DEFINED (POBJECT n_drop)
n_cast =/= n_drop
$throwable_previous_id(S_method, n_cast) = eps
$throwable_previous_id(S_method, n_drop) = eps
$class_named(S_method.CLASSNAMES, $ptlc($ptascii("ColdDoubleNameSlotReview20"))) = (porigin_cold)
$class_at(S_method.CLASSES, porigin_cold) = (pclassdesc_cold)
pclassdesc_cold.NAME = $ptascii("ColdDoubleNameSlotReview20")
$class_static_select(S_method, porigin_cold, $ptascii("value")) = (ppropertydesc_cold)
ppropertydesc_cold.DEFAULT = PROP_DEFERRED porigin_default
$class_static_at(S_method.CLASSSTATICS, ppropertydesc_cold.ORIGIN) = (pclassstatic_cold)
pclassstatic_cold.STATE = PROP_DEFERRED porigin_default
~$class_constant_table_done(S_method, porigin_cold)
''') + guards('S_method')
    checks += seek('S_operation', 'S_method', 17) + lines(r'''
S_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cold) :: ptask_operation*
S_operation.DESTRUCTION.OPERATIONS = pdestructionoperation_cold :: pdestructionoperation_tail*
pdestructionoperation_cold.SOURCE = THROW_SEARCH n_cast
pdestructionoperation_cold.PENDING = (n_drop)
pdestructionoperation_cold.COMPLETION = NORMAL
pdestructionoperation_cold.VALUE = KNOWN PNULL
pdestructionoperation_cold.CALLER = S_operation.CURRENT
pdestructionoperation_cold.CALLER =/= (pcallcontext_method)
$destructor_operation_valid(S_operation, pdestructionoperation_cold)
$call_task_valid(S_operation, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cold)
$computed_static_throw_fetch(ptask_operation*, pdestructionoperation_cold.ORIGIN, n_cast) = (ptask_cast_fetch)
ptask_cast_fetch = COMPOUND_STATIC_FETCH pcomputedcompound_cold n_name porigin_cold ptbytes_empty n_old_pending?
ptbytes_empty = eps
n_old_pending? = (n_cast)
pcomputedcompound_cold.NAME = VARIABLE $ptascii("name") z_name
pcomputedcompound_cold.RIGHT = KNOWN (POBJECT n_right)
n_right =/= n_name
n_right =/= n_cast
n_right =/= n_drop
$scoped_selector_class(S_operation, pcomputedcompound_cold.CLASS) = (porigin_cold)
pdestructionoperation_cold.ORIGIN = $origin_child((pcomputedcompound_cold.SITE), [PCFIELD 0])
pdestructionoperation_cold.BASE = BASE_CLASS_STATIC porigin_cold eps
~((HOBJECT n_name) <- S_operation.ALLOCATIONS)
(HOBJECT n_right) <- S_operation.ALLOCATIONS
$heap_owners($heap_graph(S_operation), HOBJECT n_right) = 1
$outputs(S_operation.EVENTS) = $ptascii("Q;N;D;")
$computed_static_throw_projection(S_operation, pdestructionoperation_cold)
S_operation_view = $call_after_origin(S_operation, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cold)
S_operation_view.TODO = ptask_operation*
S_operation_view.BASE = pdestructionoperation_cold.BASE
S_operation_view.DESTRUCTION.OPERATIONS = pdestructionoperation_tail*
$call_task_valid(S_operation_view, ptask_cast_fetch)
''') + unchanged_cold('S_operation') + guards('S_operation')
    checks += seek('S_fetch', 'S_operation', 14) + lines(r'''
S_fetch.TODO = ptask_fetch :: ptask_fetch_tail*
ptask_fetch = COMPOUND_STATIC_FETCH pcomputedcompound_cold n_name porigin_cold eps n_fetch_pending?
n_fetch_pending? = (n_drop)
S_fetch.BASE = BASE_CLASS_STATIC porigin_cold eps
~((HOBJECT n_name) <- S_fetch.ALLOCATIONS)
$ordinary_internal_string_evidence(S_fetch, n_name)
(HOBJECT n_right) <- S_fetch.ALLOCATIONS
$task_nodes(ptask_fetch) = [HOBJECT n_right, HOBJECT n_drop]
$heap_owners($heap_graph(S_fetch), HOBJECT n_right) = 1
$string_bytes($throwable_field(S_fetch, n_drop, "message")) = ($ptascii("drop"))
$throwable_previous_id(S_fetch, n_drop) = (n_cast)
$string_bytes($throwable_field(S_fetch, n_cast, "message")) = ($ptascii("cast"))
$throwable_previous_id(S_fetch, n_cast) = eps
$outputs(S_fetch.EVENTS) = $ptascii("Q;N;D;")
$computed_static_fetch_ready(S_fetch, pcomputedcompound_cold, n_name, porigin_cold, eps, (n_drop))
$call_task_valid(S_fetch, ptask_fetch)
~$call_task_valid(S_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_cold n_name porigin_cold eps eps)
~$call_task_valid(S_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_cold n_name porigin_cold eps (n_cast))
~$call_task_valid(S_fetch, COMPOUND_STATIC_FETCH pcomputedcompound_cold n_name porigin_cold $ptascii("value") (n_drop))
S_nonempty_fetch = S_fetch[.TODO = (COMPOUND_STATIC_FETCH pcomputedcompound_cold n_name porigin_cold $ptascii("value") (n_drop)) :: ptask_fetch_tail*][.BASE = BASE_CLASS_STATIC porigin_cold $ptascii("value")]
~$computed_static_fetch_ready(S_nonempty_fetch, pcomputedcompound_cold, n_name, porigin_cold, $ptascii("value"), (n_drop))
''') + unchanged_cold('S_fetch') + guards('S_fetch')
    checks += seek('S_lookup', 'S_fetch', 20) + lines(r'''
S_lookup.TODO = (THROW_SEARCH n_lookup) :: ptask_lookup_tail*
$string_bytes($throwable_field(S_lookup, n_lookup, "message")) = ($ptascii("Access to undeclared static property ColdDoubleNameSlotReview20::$"))
S_lookup.OBJECTS[n_lookup] = THROWABLE pthrowable_lookup
pthrowable_lookup.KIND = "Error"
$throwable_previous_id(S_lookup, n_lookup) = (n_drop)
$throwable_previous_id(S_lookup, n_drop) = (n_cast)
$throwable_previous_id(S_lookup, n_cast) = eps
~((HOBJECT n_name) <- S_lookup.ALLOCATIONS)
~((HOBJECT n_right) <- S_lookup.ALLOCATIONS)
$outputs(S_lookup.EVENTS) = $ptascii("Q;N;D;R;")
$call_task_valid(S_lookup, THROW_SEARCH n_lookup)
''') + unchanged_cold('S_lookup') + guards('S_lookup')
    checks += ['S_done = $drive(S_lookup, 1000)',
               'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
               'S_done.FRAMES = eps', 'S_done.TRACE = eps',
               f'$outputs(S_done.EVENTS) = $ptascii("{expected}")',
               '~((HOBJECT n_name) <- S_done.ALLOCATIONS)',
               '~((HOBJECT n_right) <- S_done.ALLOCATIONS)']
    checks += unchanged_cold('S_done') + guards('S_done')
    text = EXTRA + STRINGABLE_EXTRA + COLD_EXTRA + PREFIX.replace('STAGE', '$scoped_phase(S, 19)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks


CASES += DYNAMIC_CASES
CASES += COMPUTED_CASES
CASES += STRINGABLE_CASES
CALLABLE_CASES = [
    ('stringable-name-ordinary-live-carrier', ['stringable-name-ordinary-live-byref']),
    ('stringable-name-from-callable-live-selection', ['stringable-name-from-callable-live-byref']),
]
CASES += CALLABLE_CASES
CASES += [('stringable-name-cold-double-throw', ['stringable-property-name-cold-double-throw'])]
CASES += [('stringable-name-from-callable-instance-selection', ['stringable-name-from-callable-instance-byref'])]
CASES += [('stringable-name-captured-factory-selection', ['stringable-name-captured-factory-instance-byref'])]
CASES += [('stringable-name-explicit-factory-invoke', ['stringable-name-explicit-factory-invoke-byref'])]
CASES += [('stringable-name-factory-invoke-alias', ['stringable-name-factory-invoke-alias-byref'])]
CASES += [('from-callable-factory-getter-retirement', ['from-callable-factory-getter-live'])]
CASES += [('from-callable-factory-fiber-retirement', ['from-callable-factory-fiber-current'])]
CASES += [('from-callable-factory-bound-fiber-retirement', ['from-callable-factory-fiber-status'])]
CASES += [('from-callable-factory-static-fiber-suspension', ['from-callable-factory-fiber-suspend'])]


def render(name, sources):
    if name == 'from-callable-factory-static-fiber-suspension':
        from from_callable_suspend_fiber_review import render as render_suspend_fiber
        row = sources['from-callable-factory-fiber-suspend']
        text, checks, _, _ = render_suspend_fiber(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'from-callable-factory-bound-fiber-retirement':
        from from_callable_bound_fiber_review import render as render_bound_fiber
        row = sources['from-callable-factory-fiber-status']
        text, checks, _, _ = render_bound_fiber(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'from-callable-factory-fiber-retirement':
        from from_callable_factory_protocol import render_factory_fiber
        row = sources['from-callable-factory-fiber-current']
        text, checks, _, _ = render_factory_fiber(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'from-callable-factory-getter-retirement':
        from from_callable_factory_protocol import render_factory_getter
        row = sources['from-callable-factory-getter-live']
        text, checks, _, _ = render_factory_getter(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'stringable-name-factory-invoke-alias':
        from from_callable_factory_protocol import render_factory_alias
        row = sources['stringable-name-factory-invoke-alias-byref']
        text, checks, _, _ = render_factory_alias(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'stringable-name-explicit-factory-invoke':
        from from_callable_factory_protocol import render_factory_invoke
        row = sources['stringable-name-explicit-factory-invoke-byref']
        text, checks, _, _ = render_factory_invoke(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'stringable-name-captured-factory-selection':
        from from_callable_factory_protocol import render_factory
        row = sources['stringable-name-captured-factory-instance-byref']
        text, checks, _, _ = render_factory(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'stringable-name-from-callable-instance-selection':
        from static_name_callable_protocol import render_instance_wrapper
        row = sources['stringable-name-from-callable-instance-byref']
        text, checks, _, _ = render_instance_wrapper(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name in (case[0] for case in CALLABLE_CASES):
        from static_name_callable_protocol import render_ordinary, render_wrapper
        case = next(case for case in CALLABLE_CASES if case[0] == name)
        row = sources[case[1][0]]
        renderer = render_ordinary if name == CALLABLE_CASES[0][0] else render_wrapper
        text, checks, _, _ = renderer(row['fixture'], row['filename'], row['expected_stdout'])
        return text, checks
    if name == 'stringable-name-cold-double-throw':
        row = sources['stringable-property-name-cold-double-throw']
        return cold_double_throw(row['fixture'], row['filename'], row['expected_stdout'])
    if name == CASES[0][0]:
        checks = lexical(sources[CASES[0][1][0]])
    elif name == CASES[1][0]:
        checks = nested(sources[CASES[1][1][0]]) + captured(sources[CASES[1][1][1]])
    elif name == DYNAMIC_CASES[0][0]:
        checks = dynamic_base(sources[DYNAMIC_CASES[0][1][0]], sources[DYNAMIC_CASES[0][1][1]])
    elif name == DYNAMIC_CASES[1][0]:
        checks = dynamic_reference(sources[DYNAMIC_CASES[1][1][0]])
    elif name == COMPUTED_CASES[0][0]:
        checks = computed_timing(sources[COMPUTED_CASES[0][1][0]], sources[COMPUTED_CASES[0][1][1]])
    elif name == COMPUTED_CASES[1][0]:
        checks = computed_references(sources[COMPUTED_CASES[1][1][0]], sources[COMPUTED_CASES[1][1][1]])
    elif name == STRINGABLE_CASES[0][0]:
        checks = stringable_receiver(sources[STRINGABLE_CASES[0][1][0]], sources[STRINGABLE_CASES[0][1][1]])
    elif name == STRINGABLE_CASES[1][0]:
        checks = stringable_late_address(sources[STRINGABLE_CASES[1][1][0]], sources[STRINGABLE_CASES[1][1][1]])
    else:
        raise ValueError(name)
    text = EXTRA + DYNAMIC_EXTRA + COMPUTED_EXTRA + STRINGABLE_EXTRA + PREFIX.replace('STAGE', '$scoped_phase(S, 0)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks
