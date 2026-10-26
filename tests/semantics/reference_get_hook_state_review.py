"""Source-reached review conditions for backed reference Get rebinding."""
import base64
import json

import backed_get_hook_protocol as hook

PREFIX = hook.PREFIX + r'''
def $bh_stage(S,20) = true
  -- if S.TODO = (PROPERTY_PREP phpType20 12) :: (ORIGIN_RETURN porigin?) :: (PROPERTY_REF_PREP expression 12) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,21) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "bind") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,22) = true
  -- if $bh_output(S.EVENTS) = $ptascii("R:G|blocked|line|file|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,23) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("object")
  -- if $bh_output(S.EVENTS) = $ptascii("R:G|blocked|line|file|G|kept7|G|separate7|rhs13|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''

def clauses(text):
    return [line.strip() for line in text.strip().splitlines() if line.strip()]

def seek(start, stage, finish):
    return [
        f"{finish}_found = $bh_seek({start},{stage},3000)",
        rf"{finish}_found.COMPLETION = NORMAL \/ {finish}_found.COMPLETION = BUDGET",
        f"{finish} = {finish}_found[.COMPLETION = NORMAL]",
        f"$bh_stage({finish},{stage})",
    ]

def budget(start, wrapped, label):
    return [
        f"{label}_zero = $drive_steps({start},0)",
        f"{label}_zero = {start}[.COMPLETION = BUDGET]",
        f"{label}_one = $drive_steps({start},1)",
        f"{label}_one = $drive_steps({wrapped},0)",
        f"{label}_two = $drive_steps({start},2)",
        f"{label}_split = $drive_steps({label}_one[.COMPLETION = NORMAL],1)",
        f"{label}_split = {label}_two",
    ]

def conditions(program, path):
    checks = [
        f"S_initial = $php_run({program},0,{json.dumps(base64.b64encode(str(path).encode()).decode())})",
        "S_initial.COMPLETION = BUDGET",
    ]
    checks += seek("S_initial", 20, "S_front") + clauses(r'''
    $property_hook_ref_plan(S_front) = ((ppropertyhook,"bind"))
    S_front.TODO = (PROPERTY_PREP phpType20 12) :: ptask_tail*
    ppropertyhook.LINE = 12
    $property_hook_ref_tail(S_front,ppropertyhook,"bind",ptask_tail*)
    $property_hook_ref_input(S_front,"bind",ptask_tail*)
    ~$property_hook_ref_tail(S_front,ppropertyhook,"fetch",ptask_tail*)
    $lookup(S_front.ENV,$ptascii("object")) = (n_object_cell)
    S_front.STORE[n_object_cell] = DEFINED (POBJECT n_object)
    ppropertyhook.OBJECT = n_object
    $lookup(S_front.ENV,$ptascii("replacement")) = (n_rhs)
    S_front.STORE[n_rhs] = DEFINED (PINT 11)
    $property_effective_desc(S_front,n_object,$ptascii("value")) = (ppropertydesc)
    $property_hook_reference_decl(S_front,ppropertydesc)
    $bh_slot(S_front,n_object,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7)))
    $property_hook_function(S_front,ppropertyhook) = (pfunction_hook)
    pfunction_hook.SIGNATURE.BYREF
    $task_nodes(PROPERTY_HOOK_REF_RESULT ppropertyhook "bind") = eps
    $heap_owners($heap_graph(S_front),HOBJECT n_object) = 1
    $bh_output(S_front.EVENTS) = $ptascii("R:")
    $bh_guard(S_front)
    PhpStep: S_front ~> S_begin_raw
    S_begin_raw = S_front[.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) 12),PROPERTY_HOOK_REF_RESULT ppropertyhook "bind"] ++ ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
    S_begin = $bh_after(S_front,S_begin_raw)
    $property_hook_pending_call(S_begin,ppropertyhook)
    $heap_owners($heap_graph(S_begin),HOBJECT n_object) = 2
    $bh_guard(S_begin)
    ''')
    checks += budget("S_front", "S_begin", "S_entry_budget")
    checks += seek("S_begin", 21, "S_result") + clauses(r'''
    S_result.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "bind") :: ptask_result_tail*
    S_result.RESULT = REFERENCE n_value
    n_value =/= n_rhs
    S_result.STORE[n_value] = DEFINED (PINT 7)
    S_result.STORE[n_rhs] = DEFINED (PINT 11)
    $bh_slot(S_result,n_object,$ptascii("value")) = (PROP_VALUE (ALIAS n_value))
    $propref_at(S_result.PROPREFS,n_value) = (ppropref)
    ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("value")) ppropertydesc.ORIGIN]
    $propref_at(S_result.PROPREFS,n_rhs) = eps
    $call_reference_operand_valid(S_result,S_result.RESULT)
    $property_hook_result_tail(S_result,ppropertyhook,S_result.TODO)
    $heap_owners($heap_graph(S_result),HOBJECT n_object) = 1
    $heap_owners($heap_graph(S_result),HCELL n_value) = 2
    $bh_output(S_result.EVENTS) = $ptascii("R:G|")
    $bh_guard(S_result)
    S_wrong = S_result[.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: ptask_result_tail*]
    $heap_graph(S_wrong) = $heap_graph(S_result)
    $heap_valid($heap_prune($heap_graph(S_wrong)))
    ~$property_hook_result_tail(S_wrong,ppropertyhook,S_wrong.TODO)
    ~$call_descriptors_valid(S_wrong)
    S_refused = $drive(S_wrong,1)
    S_refused.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
    PhpStep: S_result ~> S_error_raw
    S_error_raw = S_result[.COMPLETION = THROWN "Error" ($ptascii("Cannot assign by reference to overloaded object")) 12]
    S_error = $bh_after(S_result,S_error_raw)
    ''')
    checks += budget("S_result", "S_error", "S_error_budget")
    checks += seek("S_error", 22, "S_caught") + clauses(r'''
    $lookup(S_caught.ENV,$ptascii("error")) = (n_error_cv)
    S_caught.STORE[n_error_cv] = DEFINED (POBJECT n_error)
    S_caught.OBJECTS[n_error] = THROWABLE pthrowable
    pthrowable.KIND = "Error"
    $string_bytes($throwable_field(S_caught,n_error,"message")) = ($ptascii("Cannot assign by reference to overloaded object"))
    $throwable_field(S_caught,n_error,"line") = PINT 12
    $string_bytes($throwable_field(S_caught,n_error,"file")) = ($call_sourcefile(S_caught.FILES,ppropertyhook.SITE))
    S_caught.STORE[n_rhs] = DEFINED (PINT 11)
    S_caught.STORE[n_value] = DEFINED (PINT 7)
    $bh_slot(S_caught,n_object,$ptascii("value")) = (PROP_VALUE (ALIAS n_value))
    $propref_at(S_caught.PROPREFS,n_value) = (ppropref)
    $heap_owners($heap_graph(S_caught),HCELL n_value) = 1
    $bh_guard(S_caught)
    ''')
    checks += seek("S_caught", 23, "S_drop") + clauses(r'''
    S_drop.STORE[n_rhs] = DEFINED (PINT 13)
    S_drop.STORE[n_value] = DEFINED (PINT 7)
    $bh_slot(S_drop,n_object,$ptascii("value")) = (PROP_VALUE (ALIAS n_value))
    $propref_at(S_drop.PROPREFS,n_value) = (ppropref)
    $propref_at(S_drop.PROPREFS,n_rhs) = eps
    $bh_guard(S_drop)
    S_end = $drive(S_drop,4000)
    S_end.COMPLETION = NORMAL
    S_end.EXITSTATUS = 0
    S_end.TODO = eps
    S_end.FRAMES = eps
    S_end.CURRENT = eps
    ~((HOBJECT n_object) <- S_end.ALLOCATIONS)
    ~((HCELL n_value) <- S_end.ALLOCATIONS)
    S_end.STORE[n_rhs] = DEFINED (PINT 13)
    $propref_at(S_end.PROPREFS,n_value) = eps
    $bh_output(S_end.EVENTS) = $ptascii("R:G|blocked|line|file|G|kept7|G|separate7|rhs13|D|Z|")
    $bh_guard(S_end)
    ''')
    return checks
