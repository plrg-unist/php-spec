"""Inherited static computed-name calls, live carriers and saved wrapper authority."""

from error_handler_protocol import PREFIX

from scoped_static_compound_protocol import EXTRA, STRINGABLE_EXTRA, computed_start, guards, lines, seek

TOTAL = r'''
def $scoped_seek(S, n_phase, 0) = S
  -- if ~$scoped_phase(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

RIGHT_PHASE = r'''
def $scoped_phase(S, 21) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (COMPOUND_LIVE_RIGHT pcompoundstring ptbytes) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
def $scoped_phase(S, 22) = true
  -- if S.TODO = (COMPOUND_LIVE_RIGHT pcompoundstring ptbytes) :: ptask*
  -- if pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
'''

CALLBACK_PHASE = r'''
def $scoped_phase(S, 23) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("FromStaticRightReview20::__toString")
'''

def _ordinary_start(fixture, filename):
    row = {'fixture': fixture, 'filename': filename}
    checks = computed_start('S_name', row, 8)
    checks += lines(r'''
S_name.TODO = (STRINGIFY_RESULT n_name porigin_name z_name) :: (COMPOUND_STATIC_CAST pcomputedcompound n_name porigin_child) :: ptask_name*
(porigin_name, z_name) = (pcomputedcompound.SITE, pcomputedcompound.LINE)
pcomputedcompound.NAME = VARIABLE $ptascii("property") z_property
pcomputedcompound.RIGHT = VARIABLE $ptascii("rhs") z_rhs
S_name.RESULT = KNOWN pvalue_name_result
$string_bytes(pvalue_name_result) = ($ptascii("value"))
$class_named(S_name.CLASSNAMES, $ptlc($ptascii("FromStaticNameBaseReview20"))) = (porigin_base)
$class_named(S_name.CLASSNAMES, $ptlc($ptascii("FromStaticNameChildReview20"))) = (porigin_child)
porigin_base =/= porigin_child
S_name.CURRENT = (pcallcontext_append)
pcallcontext_append.LEXICAL_CLASS = (porigin_base)
pcallcontext_append.CALLED_CLASS = (porigin_child)
~$from_current(S_name)
$computed_static_cast_valid(S_name, pcomputedcompound, n_name, porigin_child)
$heap_owners($heap_graph(S_name), HOBJECT n_name) = 1
S_name_global = $global_table_view(S_name)
$lookup(S_name_global.ENV, $ptascii("property")) = (n_property)
S_name.STORE[n_property] = DEFINED pvalue_property
$string_bytes(pvalue_property) = ($ptascii("other"))
$lookup(S_name_global.ENV, $ptascii("rhs")) = (n_rhs)
S_name.STORE[n_rhs] = DEFINED pvalue_before
$string_bytes(pvalue_before) = ($ptascii("before"))
$outputs(S_name.EVENTS) = $ptascii("H;N;")
''') + guards('S_name')
    checks += seek('S_live', 'S_name', 0) + lines(r'''
S_live.TODO = (COMPOUND_LIVE_PREP pcompoundstring pvalue_left) :: ptask_live*
pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
pcompoundstring.SITE = pcomputedcompound.SITE
pcompoundstring.RIGHT = pcomputedcompound.RIGHT
pcompoundstring.SELECTED = eps
~pcompoundstring.CV /\ ~pcompoundstring.SELF
pstaticcompound.CLASS = porigin_child
pstaticcompound.CELL = eps
~pstaticcompound.VERIFY
S_live.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDSELECT pstaticcompound pstaticselection pcompoundstring.SITE pcompoundstring.LINE n_prefix
pstaticselection.ROOT = porigin_child
pstaticselection.SCOPE = (porigin_base)
pstaticselection.CALLED = (porigin_child)
pstaticselection.CLOSURE = eps
$class_static_selection_valid(S_live, pstaticselection)
$static_compound_capture(S_live, pstaticcompound.DECL, pcompoundstring.SITE, pstaticcompound.ENTRY) = (pstaticcompound)
$compound_live_source(S_live, pcompoundstring)
$call_task_valid(S_live, COMPOUND_LIVE_PREP pcompoundstring pvalue_left)
$string_bytes(pvalue_left) = ($ptascii("d"))
~$user_string_value(S_live, pvalue_left)
S_live.STORE[n_rhs] = DEFINED (POBJECT n_right)
S_right = $quiet_operand(S_live, pcompoundstring.RIGHT)
S_right.RESULT = KNOWN (POBJECT n_right)
$stringable_instance(S_live, n_right)
$user_string_value(S_live, POBJECT n_right)
~((HOBJECT n_name) <- S_live.ALLOCATIONS)
(HOBJECT n_right) <- S_live.ALLOCATIONS
$heap_owners($heap_graph(S_live), HOBJECT n_right) = 1
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring pvalue_left) = eps
$outputs(S_live.EVENTS) = $ptascii("H;N;D;")
''') + guards('S_live')
    checks += lines(r'''
S_one = $drive_steps(S_live, 1)
S_one.COMPLETION = BUDGET
S_left = S_one[.COMPLETION = NORMAL]
S_left.TODO = (COMPOUND_LIVE_LEFT pcompoundstring) :: ptask_live*
S_left.RESULT = KNOWN pvalue_left
pvalue_left = PSTRING_CARRIER INTERNED_STRING $ptascii("d")
S_left.RESULT =/= KNOWN (PSTRING $ptascii("d"))
$string_bytes(pvalue_left) = ($ptascii("d"))
$call_task_valid(S_left, COMPOUND_LIVE_LEFT pcompoundstring)
$outputs(S_left.EVENTS) = $ptascii("H;N;D;")
''') + guards('S_left')
    text = EXTRA + STRINGABLE_EXTRA + TOTAL + PREFIX.replace('STAGE', '$scoped_phase(S, 8)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks

def _wrapper_start(fixture, filename):
    checks = computed_start('S_name', {'fixture': fixture, 'filename': filename}, 8)
    checks += lines(r'''
S_name.TODO = (STRINGIFY_RESULT n_name porigin_name z_name) :: (COMPOUND_STATIC_CAST pcomputedcompound n_name porigin_child) :: ptask_name*
(porigin_name, z_name) = (pcomputedcompound.SITE, pcomputedcompound.LINE)
pcomputedcompound.NAME = VARIABLE $ptascii("property") z_property
pcomputedcompound.RIGHT = VARIABLE $ptascii("rhs") z_rhs
S_name.RESULT = KNOWN pvalue_name
$string_bytes(pvalue_name) = ($ptascii("value"))
$class_named(S_name.CLASSNAMES, $ptlc($ptascii("FromStaticNameBaseReview20"))) = (porigin_base)
$class_named(S_name.CLASSNAMES, $ptlc($ptascii("FromStaticNameChildReview20"))) = (porigin_child)
porigin_base =/= porigin_child
S_name.CURRENT = (pcallcontext_append)
pcallcontext_append.TARGET = CLOSURE_TARGET n_closure
pcallcontext_append.LEXICAL_CLASS = (porigin_base)
pcallcontext_append.CALLED_CLASS = (porigin_child)
$from_current(S_name)
S_name.OBJECTS[n_closure] = FROMCALLABLECLOSURE pfrommethod
pfrommethod.STATIC
pfrommethod.FUNCTION = pcallcontext_append.FUNCTION
$from_valid(S_name, pfrommethod)
$class_method_origin(S_name.CLASSES, pfrommethod.FUNCTION) = (pmethoddesc_append)
pmethoddesc_append.OWNER = porigin_base
$closure_evidence_current(S_name) = (CLOSURE_SCOPE pclosurescope)
pclosurescope.OBJECT = n_closure
pclosurescope.LEXICAL = (porigin_base)
pclosurescope.CALLED = (porigin_child)
pclosurescope.RECEIVER = eps
pclosurescope.CREATION = eps
$closure_scope_row_valid(S_name, pclosurescope)
$closure_evidence_valid(S_name, CLOSURE_SCOPE pclosurescope)
$closure_evidence_body(S_name, n_closure) = (pfrommethod.FUNCTION)
(HOBJECT n_closure) <- S_name.ALLOCATIONS
S_name_global = $global_table_view(S_name)
$lookup(S_name_global.ENV, $ptascii("closure")) = (n_closure_cell)
S_name.STORE[n_closure_cell] = DEFINED (POBJECT n_closure)
$heap_owners($heap_graph(S_name), HOBJECT n_name) = 1
$computed_static_cast_valid(S_name, pcomputedcompound, n_name, porigin_child)
$outputs(S_name.EVENTS) = $ptascii("H;N;")
''') + guards('S_name')
    checks += seek('S_apply', 'S_name', 11) + lines(r'''
S_apply.TODO = (COMPOUND_STATIC_APPLY pcomputedaddress) :: ptask_apply*
S_apply.CURRENT = (pcallcontext_append)
pcomputedaddress.SITE = pcomputedcompound.SITE
pcomputedaddress.LINE = pcomputedcompound.LINE
pcomputedaddress.RIGHT = pcomputedcompound.RIGHT
pcomputedaddress.ROOT = porigin_child
pcomputedaddress.NAME = $ptascii("value")
pcomputedaddress.PENDING = eps
S_apply.BASE = BASE_CLASS_STATIC porigin_child $ptascii("value")
$call_task_valid(S_apply, COMPOUND_STATIC_APPLY pcomputedaddress)
$task_nodes(COMPOUND_STATIC_APPLY pcomputedaddress) = eps
~((HOBJECT n_name) <- S_apply.ALLOCATIONS)
(HOBJECT n_closure) <- S_apply.ALLOCATIONS
$closure_evidence_current(S_apply) = (CLOSURE_SCOPE pclosurescope)
$closure_scope_row_valid(S_apply, pclosurescope)
$outputs(S_apply.EVENTS) = $ptascii("H;N;D;")
S_apply_global = $global_table_view(S_apply)
$lookup(S_apply_global.ENV, $ptascii("property")) = (n_property)
S_apply.STORE[n_property] = DEFINED pvalue_property
$string_bytes(pvalue_property) = ($ptascii("other"))
$lookup(S_apply_global.ENV, $ptascii("rhs")) = (n_rhs)
S_apply.STORE[n_rhs] = DEFINED (POBJECT n_right)
S_right = $quiet_operand(S_apply, pcomputedaddress.RIGHT)
S_right.RESULT = KNOWN (POBJECT n_right)
$stringable_instance(S_apply, n_right)
$user_string_value(S_apply, POBJECT n_right)
$heap_owners($heap_graph(S_apply), HOBJECT n_right) = 1
$class_at(S_apply.CLASSES, porigin_child) = (pclassdesc_child)
$class_static_select(S_apply, porigin_child, $ptascii("value")) = (ppropertydesc)
$property_declaring_class(S_apply.CLASSES, ppropertydesc.ORIGIN) = (porigin_child)
$class_static_at(S_apply.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)
pclassstatic.STATE = PROP_VALUE (DIRECT pvalue_left)
$string_bytes(pvalue_left) = ($ptascii("d"))
$origin_child((pcomputedaddress.SITE), [PCFIELD 0]) = (porigin_fetch)
S_selection = S_apply[.ORIGIN = (porigin_fetch)]
$class_static_selection(S_selection, KNOWN (PSTRING pclassdesc_child.NAME)) = (pstaticselection)
pstaticselection.SITE = porigin_fetch
pstaticselection.ROOT = porigin_child
pstaticselection.SCOPE = (porigin_base)
pstaticselection.CALLED = (porigin_child)
pstaticselection.CLOSURE = (CLOSURE_SCOPE pclosurescope)
$class_static_selection_valid(S_apply, pstaticselection)
S_capture = S_apply[.ORIGIN = (pcomputedaddress.SITE)]
$computed_static_base(S_capture, ppropertydesc.ORIGIN, pcomputedaddress.SITE) = ((porigin_child, $ptascii("value")))
''')
    return checks

def render_ordinary(fixture, filename, expected):
    prefix, checks = _ordinary_start(fixture, filename)
    prefix = prefix.split('\ndec $main()')[0] + RIGHT_PHASE
    # These checkpoints continue the authentic ordinary execution.
    checks += seek('S_right_return', 'S_left', 21) + lines(r'''
S_right_return.TODO = (STRINGIFY_RESULT n_right pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d")) :: ptask_live*
pcompoundstring_right = pcompoundstring[.SELECTED = (n_right)]
S_right_return.RESULT = KNOWN pvalue_right_return
$string_bytes(pvalue_right_return) = ($ptascii("retired"))
$stringify_pairs_valid(S_right_return, S_right_return.TODO)
$heap_owners($heap_graph(S_right_return), HOBJECT n_right) = 2
~((HOBJECT n_name) <- S_right_return.ALLOCATIONS)
$outputs(S_right_return.EVENTS) = $ptascii("H;N;D;B;")
''') + seek('S_before_store', 'S_right_return', 22) + lines(r'''
S_before_store.TODO = (COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d")) :: ptask_live*
S_before_store.RESULT = KNOWN pvalue_right_return
$call_task_valid(S_before_store, COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d"))
$heap_owners($heap_graph(S_before_store), HOBJECT n_right) = 1
S_written_budget = $drive_steps(S_before_store, 1)
S_written_budget.COMPLETION = BUDGET
S_written = S_written_budget[.COMPLETION = NORMAL]
S_written.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring_right) :: ptask_live*
S_written.RESULT = KNOWN pvalue_written
pvalue_written = PSTRING_CARRIER (REQUEST_STRING n_written) $ptascii("dretired")
n_written = |S_before_store.STRINGDATA|
S_written.STRINGDATA = S_before_store.STRINGDATA ++ [$ptascii("dretired")]
$string_carrier_valid(S_written, pvalue_written)
$class_static_at(S_written.CLASSSTATICS, pstaticcompound.DECL) = (pclassstatic_written)
pclassstatic_written.STATE = PROP_VALUE (DIRECT pvalue_written)
$static_compound_source(S_written, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)
''') + guards('S_right_return') + guards('S_before_store') + guards('S_written')
    checks += ['S_done = $drive(S_written, 1000)', 'S_done.COMPLETION = NORMAL',
               'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               'S_done.TRACE = eps', f'$outputs(S_done.EVENTS) = $ptascii("{expected}")',
               '~((HOBJECT n_name) <- S_done.ALLOCATIONS)',
               '~((HOBJECT n_right) <- S_done.ALLOCATIONS)'] + guards('S_done')
    reached = len(checks)
    # Constructed variants test representation and empty branches independently.
    checks += lines(r'''
S_legacy_left = S_left[.RESULT = KNOWN (PSTRING $ptascii("d"))]
PhpStep: S_left ~> S_interned_next
PhpStep: S_legacy_left ~> S_legacy_next
S_interned_next = S_legacy_next
S_interned_next.TODO = (CALL_ARGS (METHOD_TARGET n_right porigin_right_method) eps 0 eps (pcompoundstring.SITE) pcompoundstring.LINE) :: (STRINGIFY_RESULT n_right pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d")) :: ptask_live*
S_request_left = $string_request(S_left, $ptascii("d"))
PhpStep: S_request_left ~> S_request_next
S_request_next = S_interned_next[.STRINGDATA = S_request_left.STRINGDATA]
S_empty_left = S_left[.RESULT = KNOWN (PSTRING eps)]
PhpStep: S_empty_left ~> S_empty_next
S_empty_next.TODO = (CALL_ARGS (METHOD_TARGET n_right porigin_right_method) eps 0 eps (pcompoundstring.SITE) pcompoundstring.LINE) :: (STRINGIFY_RESULT n_right pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_right eps) :: ptask_live*
$string_bytes(PSTRING eps) = (eps)
$string_bytes(PSTRING_CARRIER INTERNED_STRING eps) = (eps)
$string_bytes(PNULL) = eps
$string_bytes(PINT 0) = eps
$string_bytes(PBOOL false) = eps
$string_bytes(POBJECT n_right) = eps
S_legacy_right = S_before_store[.RESULT = KNOWN (PSTRING $ptascii("retired"))]
PhpStep: S_legacy_right ~> S_legacy_written
S_legacy_written = S_written
S_request_right = $string_request(S_before_store, $ptascii("retired"))
PhpStep: S_request_right ~> S_request_written
S_request_written.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_request_written) $ptascii("dretired"))
n_request_written = |S_request_right.STRINGDATA|
S_request_written.STRINGDATA = S_request_right.STRINGDATA ++ [$ptascii("dretired")]
S_empty_right = S_before_store[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)]
PhpStep: S_empty_right ~> S_empty_written
S_empty_written.RESULT = KNOWN (PSTRING $ptascii("d"))
S_empty_written.STRINGDATA = S_before_store.STRINGDATA
$string_same(PSTRING $ptascii("d"), PSTRING_CARRIER INTERNED_STRING $ptascii("d")) = eps
S_empty_left_store = S_before_store[.TODO = (COMPOUND_LIVE_RIGHT pcompoundstring_right eps) :: ptask_live*]
PhpStep: S_empty_left_store ~> S_empty_left_written
S_empty_left_written.RESULT = KNOWN (PSTRING $ptascii("retired"))
S_empty_left_written.STRINGDATA = S_before_store.STRINGDATA
''')
    for state in ('S_interned_next', 'S_request_next', 'S_empty_next', 'S_request_written',
                  'S_empty_written', 'S_empty_left_written'):
        checks += guards(state)
    text = prefix + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep: ') else 'if ')
                    + check + '\n' for check in checks)
    return text, checks, reached, len(checks) - reached

def render_wrapper(fixture, filename, expected):
    checks = _wrapper_start(fixture, filename)
    checks += lines(r'''
$computed_static_selection_closure(S_capture, (CLOSURE_SCOPE pclosurescope))
$computed_static_selection_allowed(S_capture, pcomputedaddress.SITE)
$static_compound_scoped_selection(S_capture, ppropertydesc.ORIGIN, pcomputedaddress.SITE) = ((pstaticselection, ppropertydesc))
''') + guards('S_apply')
    checks += seek('S_live', 'S_apply', 0) + lines(r'''
S_live.TODO = (COMPOUND_LIVE_PREP pcompoundstring pvalue_left) :: ptask_live*
pcompoundstring.PLACE = STATIC_COMPOUND pstaticcompound
pcompoundstring.SITE = pcomputedaddress.SITE
pcompoundstring.LINE = pcomputedaddress.LINE
pcompoundstring.RIGHT = pcomputedaddress.RIGHT
pcompoundstring.SELECTED = eps
~pcompoundstring.CV /\ ~pcompoundstring.SELF
pstaticcompound.CLASS = porigin_child
pstaticcompound.DECL = ppropertydesc.ORIGIN
pstaticcompound.CELL = eps
~pstaticcompound.VERIFY
pstaticcompound.ENTRY = |S_apply.CLASSCONSTANTHISTORY|
n_prefix = |S_live.DECLARATIONS|
S_live.CLASSCONSTANTHISTORY = S_apply.CLASSCONSTANTHISTORY ++ [CCCOMPOUNDSELECT pstaticcompound pstaticselection pcompoundstring.SITE pcompoundstring.LINE n_prefix]
pstaticselection.CLOSURE = (CLOSURE_SCOPE pclosurescope)
$static_compound_selected_descriptor(S_live, pstaticcompound, pstaticselection, pcompoundstring.SITE) = (ppropertydesc)
$static_compound_descriptor(S_live, pstaticcompound, pcompoundstring.SITE) = (ppropertydesc)
$static_compound_source(S_live, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)
$static_compound_capture(S_live, pstaticcompound.DECL, pcompoundstring.SITE, pstaticcompound.ENTRY) = (pstaticcompound)
$compound_live_source(S_live, pcompoundstring)
$call_task_valid(S_live, COMPOUND_LIVE_PREP pcompoundstring pvalue_left)
pvalue_left = PSTRING_CARRIER INTERNED_STRING $ptascii("d")
S_live.STORE[n_rhs] = DEFINED (POBJECT n_right)
~((HOBJECT n_name) <- S_live.ALLOCATIONS)
$heap_owners($heap_graph(S_live), HOBJECT n_right) = 1
pcallcontext_append.INSTANCE = (n_closure)
$heap_owners($heap_graph(S_live), HOBJECT n_closure) = 2
$task_nodes(COMPOUND_LIVE_PREP pcompoundstring pvalue_left) = eps
$outputs(S_live.EVENTS) = $ptascii("H;N;D;")
''') + guards('S_live')
    checks += seek('S_callback', 'S_live', 23) + lines(r'''
S_callback.CURRENT = (pcallcontext_right)
pcallcontext_right.TARGET = METHOD_TARGET n_right porigin_right_method
pcallcontext_right.TARGET =/= pcallcontext_append.TARGET
pcallcontext_right.FUNCTION = porigin_right_method
pcallcontext_right.INSTANCE = eps
pcallcontext_right.RECEIVER = (n_right)
S_callback.STORE[n_rhs] = DEFINED (POBJECT n_right)
pframe_callback = S_callback.FRAMES[0]
pframe_callback.CONTEXT = (pcallcontext_append)
pframe_callback.TODO = (STRINGIFY_RESULT n_right pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d")) :: ptask_live*
pcompoundstring_right = pcompoundstring[.SELECTED = (n_right)]
$task_nodes(STRINGIFY_RESULT n_right pcompoundstring.SITE pcompoundstring.LINE) = [HOBJECT n_right]
~$from_current(S_callback)
$closure_evidence_current(S_callback) = eps
S_callback.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDSELECT pstaticcompound pstaticselection pcompoundstring.SITE pcompoundstring.LINE n_prefix
$closure_evidence_valid(S_callback, CLOSURE_SCOPE pclosurescope)
$computed_static_selection_closure(S_callback, pstaticselection.CLOSURE)
$class_static_selection_valid(S_callback, pstaticselection)
$static_compound_selected_descriptor(S_callback, pstaticcompound, pstaticselection, pcompoundstring.SITE) = (ppropertydesc)
$static_compound_descriptor(S_callback, pstaticcompound, pcompoundstring.SITE) = (ppropertydesc)
$static_compound_source(S_callback, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)
$heap_owners($heap_graph(S_callback), HOBJECT n_right) = 3
$heap_owners($heap_graph(S_callback), HOBJECT n_closure) = 2
$outputs(S_callback.EVENTS) = $ptascii("H;N;D;")
''') + guards('S_callback')
    checks += seek('S_right_return', 'S_callback', 21) + lines(r'''
S_right_return.TODO = (STRINGIFY_RESULT n_right pcompoundstring.SITE pcompoundstring.LINE) :: (COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d")) :: ptask_live*
pcompoundstring_right = pcompoundstring[.SELECTED = (n_right)]
S_right_return.CURRENT = (pcallcontext_append)
S_right_return.RESULT = KNOWN pvalue_right_return
$string_bytes(pvalue_right_return) = ($ptascii("retired"))
$stringify_pairs_valid(S_right_return, S_right_return.TODO)
$heap_owners($heap_graph(S_right_return), HOBJECT n_right) = 2
$outputs(S_right_return.EVENTS) = $ptascii("H;N;D;B;")
''') + guards('S_right_return')
    checks += seek('S_before_store', 'S_right_return', 22) + lines(r'''
S_before_store.TODO = (COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d")) :: ptask_live*
S_before_store.RESULT = KNOWN pvalue_right_return
$call_task_valid(S_before_store, COMPOUND_LIVE_RIGHT pcompoundstring_right $ptascii("d"))
$heap_owners($heap_graph(S_before_store), HOBJECT n_right) = 1
S_written_budget = $drive_steps(S_before_store, 1)
S_written_budget.COMPLETION = BUDGET
S_written = S_written_budget[.COMPLETION = NORMAL]
S_written.TODO = (COMPOUND_LIVE_RELEASE pcompoundstring_right) :: ptask_live*
S_written.RESULT = KNOWN pvalue_written
pvalue_written = PSTRING_CARRIER (REQUEST_STRING n_written) $ptascii("dretired")
n_written = |S_before_store.STRINGDATA|
S_written.STRINGDATA = S_before_store.STRINGDATA ++ [$ptascii("dretired")]
$string_carrier_valid(S_written, pvalue_written)
$class_static_at(S_written.CLASSSTATICS, pstaticcompound.DECL) = (pclassstatic_written)
pclassstatic_written.STATE = PROP_VALUE (DIRECT pvalue_written)
S_written.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDSELECT pstaticcompound pstaticselection pcompoundstring.SITE pcompoundstring.LINE n_prefix
$static_compound_source(S_written, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)
''') + guards('S_before_store') + guards('S_written')
    checks += lines(r'''
S_done = $drive(S_written, 1000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.TRACE = eps
~((HOBJECT n_name) <- S_done.ALLOCATIONS)
~((HOBJECT n_right) <- S_done.ALLOCATIONS)
~((HOBJECT n_closure) <- S_done.ALLOCATIONS)
$static_compound_selected_descriptor(S_done, pstaticcompound, pstaticselection, pcompoundstring.SITE) = (ppropertydesc)
$static_compound_source(S_done, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    reached = len(checks)

    # These are constructed authority controls, not additional reached executions.
    checks += lines(r'''
S_no_current_scope = S_capture[.CLOSURESCOPES = eps]
$closure_evidence_current(S_no_current_scope) = eps
~$computed_static_selection_allowed(S_no_current_scope, pcomputedaddress.SITE)
$static_compound_capture(S_no_current_scope, ppropertydesc.ORIGIN, pcomputedaddress.SITE, |S_no_current_scope.CLASSCONSTANTHISTORY|) = eps
S_saved = S_callback[.CURRENT = eps][.CLOSURESCOPES = eps]
$computed_static_selection_closure(S_saved, pstaticselection.CLOSURE)
$class_static_selection_valid(S_saved, pstaticselection)
$static_compound_selected_descriptor(S_saved, pstaticcompound, pstaticselection, pcompoundstring.SITE) = (ppropertydesc)
pstaticselection_ordinary = pstaticselection[.CLOSURE = eps]
$computed_static_selection_closure(S_live, eps)
$class_static_selection_valid(S_live, pstaticselection_ordinary)
$static_compound_selected_descriptor(S_live, pstaticcompound, pstaticselection_ordinary, pcompoundstring.SITE) = (ppropertydesc)
pstaticcompound_bad_entry = pstaticcompound[.ENTRY = |S_live.CLASSCONSTANTHISTORY|]
~$static_compound_source(S_live, pstaticcompound_bad_entry, pcompoundstring.SITE, pcompoundstring.LINE)
~$call_task_valid(S_live, COMPOUND_LIVE_PREP pcompoundstring[.PLACE = STATIC_COMPOUND pstaticcompound_bad_entry] pvalue_left)
''')
    for label, change in [
        ('target', '.TARGET = CLOSURE_TARGET n_right'),
        ('body', '.FUNCTION = porigin_right_method'),
        ('lexical', '.LEXICAL_CLASS = (porigin_child)'),
        ('called', '.CALLED_CLASS = (porigin_base)'),
    ]:
        checks += [f'S_current_bad_{label} = S_capture[.CURRENT = (pcallcontext_append[{change}])]',
                   f'$closure_evidence_current(S_current_bad_{label}) = eps',
                   f'~$computed_static_selection_allowed(S_current_bad_{label}, pcomputedaddress.SITE)',
                   f'$static_compound_capture(S_current_bad_{label}, ppropertydesc.ORIGIN, pcomputedaddress.SITE, |S_current_bad_{label}.CLASSCONSTANTHISTORY|) = eps']
    for label, change in [
        ('root', '.ROOT = porigin_base'),
        ('scope', '.SCOPE = (porigin_child)'),
        ('called', '.CALLED = (porigin_base)'),
        ('site', '.SITE = pcompoundstring.SITE'),
        ('object', '.CLOSURE = (CLOSURE_SCOPE pclosurescope[.OBJECT = n_name])'),
        ('absent_object', '.CLOSURE = (CLOSURE_SCOPE pclosurescope[.OBJECT = |S_live.OBJECTS|])'),
        ('closure_lexical', '.CLOSURE = (CLOSURE_SCOPE pclosurescope[.LEXICAL = porigin_child])'),
        ('closure_called', '.CLOSURE = (CLOSURE_SCOPE pclosurescope[.CALLED = porigin_base])'),
        ('receiver', '.CLOSURE = (CLOSURE_SCOPE pclosurescope[.RECEIVER = (n_right)])'),
        ('creation', '.CLOSURE = (CLOSURE_SCOPE pclosurescope[.CREATION = ({FUNCTION pcallcontext_append.FUNCTION, CALLSITE pcallcontext_append.CALLSITE, RECEIVER false, EVIDENCE eps})])'),
        ('other_family', '.CLOSURE = (CLOSURE_CALL pcompoundstring.SITE n_closure n_right porigin_child)'),
    ]:
        checks += [f'pstaticselection_bad_{label} = pstaticselection[{change}]',
                   f'$static_compound_selected_descriptor(S_live, pstaticcompound, pstaticselection_bad_{label}, pcompoundstring.SITE) = eps',
                   f'S_event_bad_{label} = S_live[.CLASSCONSTANTHISTORY[pstaticcompound.ENTRY] = CCCOMPOUNDSELECT pstaticcompound pstaticselection_bad_{label} pcompoundstring.SITE pcompoundstring.LINE n_prefix]',
                   f'~$static_compound_source(S_event_bad_{label}, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)',
                   f'~$call_task_valid(S_event_bad_{label}, COMPOUND_LIVE_PREP pcompoundstring pvalue_left)',
                   f'~$call_descriptors_valid(S_event_bad_{label})',
                   f'~$class_constant_history_valid(S_event_bad_{label})']
    for label, change in [('body', '.FUNCTION = porigin_right_method'),
                          ('nonstatic', '.STATIC = false'),
                          ('creation_site', '.SITE = pcompoundstring.SITE')]:
        checks += [f'S_object_bad_{label} = S_live[.OBJECTS[n_closure] = FROMCALLABLECLOSURE pfrommethod[{change}]]',
                   f'~$computed_static_selection_closure(S_object_bad_{label}, pstaticselection.CLOSURE)',
                   f'$static_compound_selected_descriptor(S_object_bad_{label}, pstaticcompound, pstaticselection, pcompoundstring.SITE) = eps',
                   f'~$static_compound_source(S_object_bad_{label}, pstaticcompound, pcompoundstring.SITE, pcompoundstring.LINE)']
    prefix = EXTRA + STRINGABLE_EXTRA + TOTAL + RIGHT_PHASE + CALLBACK_PHASE
    prefix += PREFIX.replace('STAGE', '$scoped_phase(S, 8)')
    text = prefix + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, reached, len(checks) - reached
