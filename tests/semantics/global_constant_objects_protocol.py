#!/usr/bin/env python3
"""Source-derived global constant AST NEW completion, scope and ownership guards."""
import argparse,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import global_constant_callable_protocol as global_protocol
base=global_protocol.base
SOURCES={'global-new-argument-access-order': '<?php\n'
                                     'class GlobalNewNoCtor { public int $tag = 3; }\n'
                                     'class GlobalNewPrivateCtor {\n'
                                     "    private function __construct(int $value) { echo 'CTOR:'; "
                                     '}\n'
                                     '}\n'
                                     'set_error_handler(static function ($level) { echo $level, '
                                     "':'; return true; });\n"
                                     'const GLOBAL_NEW_PLAIN = new GlobalNewNoCtor(ignored: '
                                     'E_STRICT + 0);\n'
                                     "echo GLOBAL_NEW_PLAIN->tag, ':';\n"
                                     'try {\n'
                                     "    eval('const GLOBAL_NEW_DENIED = new "
                                     "GlobalNewPrivateCtor(E_STRICT + 0);');\n"
                                     "} catch (Error $e) { echo 'F:'; }\n"
                                     'restore_error_handler();\n'
                                     'try { $denied = GLOBAL_NEW_DENIED; } catch (Error $e) { echo '
                                     "'U'; }\n",
 'global-new-inherited-entry-scope': '<?php\n'
                                     'class GlobalNewScopeParent {\n'
                                     "    protected function __construct() { echo 'P:'; }\n"
                                     '}\n'
                                     'class GlobalNewScopeOwner extends GlobalNewScopeParent {\n'
                                     "    private function __construct() { echo 'O:'; }\n"
                                     '    public static function load() {\n'
                                     '        include __DIR__ . '
                                     "'/global-new-entry-scope.inc.php';\n"
                                     "        eval('const GLOBAL_NEW_EVAL = new self();');\n"
                                     '    }\n'
                                     '}\n'
                                     'class GlobalNewScopeChild extends GlobalNewScopeOwner {}\n'
                                     'GlobalNewScopeChild::load();\n'
                                     '$self = GLOBAL_NEW_SELF;\n'
                                     '$parent = GLOBAL_NEW_PARENT;\n'
                                     '$fromEval = GLOBAL_NEW_EVAL;\n'
                                     "echo $self::class, '/', $parent::class, '/', "
                                     '$fromEval::class;\n',
 'global-new-throw-escape-retry': '<?php\n'
                                  'class GlobalNewRetry {\n'
                                  '    public static int $next = 0;\n'
                                  '    public int $id = 0;\n'
                                  '    public function __construct() {\n'
                                  '        $this->id = ++self::$next;\n'
                                  "        echo 'C', $this->id, ':';\n"
                                  '        if ($this->id === 1) {\n'
                                  "            $GLOBALS['escaped'] = $this;\n"
                                  "            throw new Error('stop');\n"
                                  '        }\n'
                                  '    }\n'
                                  '    public function __destruct() {\n'
                                  "        if ($this->id === 1) { echo 'BAD:'; }\n"
                                  '    }\n'
                                  '}\n'
                                  "try { eval('const GLOBAL_NEW_RETRY = new GlobalNewRetry();'); "
                                  '}\n'
                                  "catch (Error $e) { echo 'F:'; }\n"
                                  'try { $missing = GLOBAL_NEW_RETRY; } catch (Error $e) { echo '
                                  "'U:'; }\n"
                                  "$held = $GLOBALS['escaped'];\n"
                                  "unset($GLOBALS['escaped']);\n"
                                  "echo $held->id, ':';\n"
                                  'unset($held, $e);\n'
                                  "eval('const GLOBAL_NEW_RETRY = new GlobalNewRetry();');\n"
                                  '$retry = GLOBAL_NEW_RETRY;\n'
                                  'echo $retry->id;\n'}

SOURCES['global-new-cold-table-noctor']="<?php\nclass GlobalNewColdNoCtor { public int $p = E_STRICT + 0; }\nset_error_handler(static function ($level, $message, $file, $line) { echo $level, ':', $line, ';'; return true; });\nconst GLOBAL_NEW_COLD = new GlobalNewColdNoCtor(ignored: E_STRICT + 0);\nrestore_error_handler();\necho GLOBAL_NEW_COLD->p;\n"

FILES={'global-new-inherited-entry-scope':('global-new-entry-scope.inc.php','<?php\nconst GLOBAL_NEW_SELF = new self(), GLOBAL_NEW_PARENT = new parent();\n')}
EVALS={
 'global-new-argument-access-order':['const GLOBAL_NEW_DENIED = new GlobalNewPrivateCtor(E_STRICT + 0);'],
 'global-new-inherited-entry-scope':['const GLOBAL_NEW_EVAL = new self();'],
 'global-new-throw-escape-retry':['const GLOBAL_NEW_RETRY = new GlobalNewRetry();'],
}
PREFIX=global_protocol.PREFIX+r"""
dec $global_new_test_arg_task(ptask) : bool
def $global_new_test_arg_task(DEFAULT_NEW_ARGS pdefaultnew) = true
def $global_new_test_arg_task(DEFAULT_NEW_SEND pdefaultnew) = true
def $global_new_test_arg_task(ptask) = false -- otherwise
dec $global_new_test_args(ptask*) : pdefaultnew?
def $global_new_test_args(eps) = eps
def $global_new_test_args((DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*) = (pdefaultnew)
def $global_new_test_args((DEFAULT_NEW_SEND pdefaultnew) :: ptask_tail*) = (pdefaultnew)
def $global_new_test_args(ptask :: ptask_tail*) = $global_new_test_args(ptask_tail*)
  -- if ~$global_new_test_arg_task(ptask)
def $global_test_stage(S, ptbytes, 9) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = 0
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 10) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = |pdefaultnew.ARGUMENTS|
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 11) = true
  -- if S.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_tail*
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 12) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_handler
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
  -- if $global_new_test_args(pframe.TODO) = (pdefaultnew)
  -- if $global_new_frames_busy(S.FRAMES, pdefaultnew.OBJECT)
  -- if $global_new_record(S.CONSTANTOBJECTS, pdefaultnew.OBJECT) = (pconstantobject)
  -- if pconstantobject.DECL = pconstantcontext.ORIGIN
def $global_test_stage(S, ptbytes, 13) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_tail*
  -- if pframe.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
  -- if pcallcontext.TARGET = METHOD_TARGET pdefaultctor.NEW.OBJECT pdefaultctor.FUNCTION
def $global_test_stage(S, ptbytes, 14) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $lookup(psymboltable.ENV, $ptascii("escaped")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_object)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 15) = true
  -- if S.TODO = (INSTANCE_DEFAULT_UPDATE porigin_class porigin_decl z) :: ptask_tail*
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 16) = true
  -- if S.TODO = (CLASS_CONST_CONSTRUCT ptbytes_class phpType7* true z) :: ptask_tail*
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)

"""
CHECKS={}
premises=global_protocol.premises
CHECKS['global-new-argument-access-order']=premises(r"""
ptbytes_plain = $ptascii("GLOBAL_NEW_PLAIN")
ptbytes_denied = $ptascii("GLOBAL_NEW_DENIED")
S_args = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_plain, 9, 1800)
S_args.TODO = (DEFAULT_NEW_ARGS pdefaultnew_plain) :: ptask_args*
S_args.CONSTCONTEXT = (pconstantcontext_plain)
porigin_decl_plain = pconstantcontext_plain.ORIGIN
porigin_site_plain = pdefaultnew_plain.SITE
n_plain = pdefaultnew_plain.OBJECT
$global_new_context(S_args, porigin_site_plain) = ((porigin_decl_plain, eps))
S_args.ERRORHANDLER.CALLBACK = (POBJECT n_handler)
S_args.CONSTANTOBJECTS = [pconstantobject_plain]
pconstantobject_plain = {OBJECT n_plain, SITE porigin_site_plain, DECL porigin_decl_plain, CLASS porigin_class_plain, PREFIX n_prefix, COMPLETE false}
$global_new_header(S_args, pconstantobject_plain)
$global_new_pending(S_args, pdefaultnew_plain)
$global_new_argument_owned(S_args, pdefaultnew_plain)
$default_new_valid(S_args, pdefaultnew_plain)
$call_descriptors_valid(S_args)
$heap_owners($heap_graph(S_args), HOBJECT n_plain) = 1
~$global_new_completed(S_args, pconstantobject_plain)
~$global_new_complete_phase(S_args, pdefaultnew_plain)
$global_new_value_class(S_args[.RESULT = KNOWN (POBJECT n_plain)], porigin_site_plain) = PVOBJECT
~$constant_value_class_valid(S_args, POBJECT n_plain, PVINSTANCE n_plain porigin_site_plain)
S_early = S_args[.CONSTANTOBJECTS = [pconstantobject_plain[.COMPLETE = true]]][.RESULT = KNOWN (POBJECT n_plain)]
~$global_new_records_valid(S_early, S_early.CONSTANTOBJECTS)
$global_new_value_class(S_early, porigin_site_plain) = PVOBJECT
~$constant_value_class_valid(S_early, POBJECT n_plain, PVINSTANCE n_plain porigin_site_plain)
~$global_new_header(S_args, pconstantobject_plain[.OBJECT = n_handler])
~$global_new_header(S_args, pconstantobject_plain[.DECL = porigin_site_plain])
~$global_new_header(S_args, pconstantobject_plain[.SITE = porigin_decl_plain])
~$global_new_header(S_args, pconstantobject_plain[.PREFIX = 0])
~$global_new_records_valid(S_args, [pconstantobject_plain, pconstantobject_plain])
~$default_new_valid(S_args[.CONSTANTOBJECTS = eps], pdefaultnew_plain)
~$default_new_valid(S_args, pdefaultnew_plain[.LINE = $(pdefaultnew_plain.LINE + 1)])
~$default_new_valid(S_args, pdefaultnew_plain[.INDEX = 1])
$global_new_context(S_args[.DECLARATIONS = eps], porigin_site_plain) = eps
$global_new_context(S_args[.CONSTCONTEXT = (pconstantcontext_plain[.ORIGIN = porigin_site_plain])], porigin_site_plain) = eps
S_warning = $global_test_find(S_args, ptbytes_plain, 6, 1200)
(HOBJECT n_plain) <- $prune_allocations(S_warning).ALLOCATIONS
S_handler = $global_test_find(S_warning, ptbytes_plain, 12, 1000)
$global_new_frames_busy(S_handler.FRAMES, n_plain)
~$global_new_tasks_busy(S_handler.TODO, n_plain)
S_handler_early = S_handler[.CONSTANTOBJECTS = [pconstantobject_plain[.COMPLETE = true]]][.RESULT = KNOWN (POBJECT n_plain)]
~$global_new_records_valid(S_handler_early, S_handler_early.CONSTANTOBJECTS)
$global_new_value_class(S_handler_early, porigin_site_plain) = PVOBJECT
(HOBJECT n_plain) <- $prune_allocations(S_handler).ALLOCATIONS
S_values = $global_test_find(S_handler, ptbytes_plain, 10, 1600)
S_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values) :: ptask_values*
pdefaultnew_values.OBJECT = n_plain /\ pdefaultnew_values.SITE = porigin_site_plain
pdefaultnew_values.INDEX = 1 /\ pdefaultnew_values.VALUES = [PINT 2048]
$global_test_output(S_values.EVENTS) = $ptascii("8192:")
$global_new_record(S_values.CONSTANTOBJECTS, n_plain) = (pconstantobject_plain)
$global_new_complete_phase(S_values, pdefaultnew_values)
S_complete = $global_test_next(S_values)
$global_new_record(S_complete.CONSTANTOBJECTS, n_plain) = (pconstantobject_complete)
pconstantobject_complete = pconstantobject_plain[.COMPLETE = true]
$global_new_completed(S_complete, pconstantobject_complete)
$global_new_value_class(S_complete, porigin_site_plain) = PVINSTANCE n_plain porigin_site_plain
S_bind = $global_test_find(S_complete, ptbytes_plain, 1, 800)
S_bind.RESULT = KNOWN (POBJECT n_plain)
$constant_received_class(S_bind, porigin_decl_plain) = PVINSTANCE n_plain porigin_site_plain
$constant_value_class_valid(S_bind, POBJECT n_plain, PVINSTANCE n_plain porigin_site_plain)
$global_constant_transfer_valid(S_bind, porigin_decl_plain, PVINSTANCE n_plain porigin_site_plain, S_bind.USERCONSTANTS)
~$constant_callable_foldable(PVINSTANCE n_plain porigin_site_plain)
~$constant_value_class_valid(S_bind[.RESULT = KNOWN (POBJECT n_handler)], POBJECT n_handler, PVINSTANCE n_plain porigin_site_plain)
$objectprops_at(S_bind.OBJECTPROPS, n_plain) = (ppropertyslot*)
$property_slot_at(ppropertyslot*, $ptascii("tag")) = (ppropertyslot_tag)
ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 3))
S_mutable = S_bind[.OBJECTPROPS = $objectprops_set(S_bind.OBJECTPROPS, n_plain, $property_slot_set(ppropertyslot*, $ptascii("tag"), PROP_VALUE (DIRECT (PINT 9))))]
$global_new_header(S_mutable, pconstantobject_complete)
$constant_value_class_valid(S_mutable, POBJECT n_plain, PVINSTANCE n_plain porigin_site_plain)
$global_constant_transfer_valid(S_mutable, porigin_decl_plain, PVINSTANCE n_plain porigin_site_plain, S_mutable.USERCONSTANTS)
S_denied = $global_test_find(S_bind, ptbytes_denied, 9, 2400)
S_denied.TODO = (DEFAULT_NEW_ARGS pdefaultnew_denied) :: ptask_denied*
S_denied.CONSTCONTEXT = (pconstantcontext_denied)
$global_new_record(S_denied.CONSTANTOBJECTS, pdefaultnew_denied.OBJECT) = (pconstantobject_denied)
pconstantobject_denied.DECL = pconstantcontext_denied.ORIGIN
pconstantobject_denied.DECL = PORIGIN n_unit_denied pcpath_denied
$global_test_entry_prefix(S_denied.DECLARATIONS, n_unit_denied, 0) = (n_before_entry)
~$global_new_header(S_denied, pconstantobject_denied[.PREFIX = n_before_entry])
~$global_new_header(S_denied, pconstantobject_denied[.CLASS = porigin_class_plain])
S_denied_values = $global_test_find(S_denied, ptbytes_denied, 10, 2000)
S_denied_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew_denied_values) :: ptask_denied_values*
pdefaultnew_denied_values.VALUES = [PINT 2048]
$effective_method(S_denied_values, pconstantobject_denied.CLASS, $ptascii("__construct"), |S_denied_values.CLASSES|) = (pmethoddesc_denied)
$default_new_scope(S_denied_values) = eps
~$method_accessible(S_denied_values, pmethoddesc_denied, eps)
~$global_new_complete_phase(S_denied_values, pdefaultnew_denied_values)
S_done = $global_test_finish(S_denied_values, 3000)
$global_test_output(S_done.EVENTS) = $ptascii("8192:3:8192:F:U")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_plain) = (puserconstant_plain)
puserconstant_plain.VALUE = POBJECT n_plain /\ puserconstant_plain.CLASS = PVINSTANCE n_plain porigin_site_plain
$user_constant_at(S_done.USERCONSTANTS, ptbytes_denied) = eps
$global_new_record(S_done.CONSTANTOBJECTS, pdefaultnew_denied.OBJECT) = (pconstantobject_denied)
~((HOBJECT pdefaultnew_denied.OBJECT) <- S_done.ALLOCATIONS)
$global_new_header(S_done, pconstantobject_denied)
$global_new_records_valid(S_done, S_done.CONSTANTOBJECTS)
$user_constants_valid(S_done, S_done.USERCONSTANTS)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT n_plain) <- S_roots.ALLOCATIONS
~((HOBJECT pdefaultnew_denied.OBJECT) <- S_roots.ALLOCATIONS)
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
""")
CHECKS['global-new-inherited-entry-scope']=premises(r"""
ptbytes_self = $ptascii("GLOBAL_NEW_SELF")
ptbytes_parent = $ptascii("GLOBAL_NEW_PARENT")
ptbytes_eval = $ptascii("GLOBAL_NEW_EVAL")
S_self = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_self, 9, 2600)
S_self.TODO = (DEFAULT_NEW_ARGS pdefaultnew_self) :: ptask_self*
S_self.CONSTCONTEXT = (pconstantcontext_self)
pconstantcontext_self.ORIGIN = PORIGIN n_file pcpath_self
S_self.CURRENT = (pcallcontext_loader)
$class_named(S_self.CLASSNAMES, $ptlc($ptascii("GlobalNewScopeOwner"))) = (porigin_owner)
$class_named(S_self.CLASSNAMES, $ptlc($ptascii("GlobalNewScopeChild"))) = (porigin_child)
$class_named(S_self.CLASSNAMES, $ptlc($ptascii("GlobalNewScopeParent"))) = (porigin_parent)
pcallcontext_loader.LEXICAL_CLASS = (porigin_owner) /\ pcallcontext_loader.CALLED_CLASS = (porigin_child)
$global_constant_scope(S_self, n_file) = (true, porigin_scope_file?)
porigin_scope_file? = (porigin_owner)
$global_new_context(S_self, pdefaultnew_self.SITE) = ((porigin_decl_self, porigin_entry_file?))
porigin_decl_self = pconstantcontext_self.ORIGIN
porigin_entry_file? = (porigin_owner)
$default_new_scope(S_self) = (porigin_owner)
$new_source_name(S_self, pdefaultnew_self.SITE) = ($ptascii("GlobalNewScopeOwner"))
$global_new_record(S_self.CONSTANTOBJECTS, pdefaultnew_self.OBJECT) = (pconstantobject_self)
pconstantobject_self.CLASS = porigin_owner /\ ~pconstantobject_self.COMPLETE
$global_new_header(S_self, pconstantobject_self)
$global_test_entry_prefix(S_self.DECLARATIONS, n_file, 0) = (n_before_file)
~$global_new_header(S_self, pconstantobject_self[.PREFIX = n_before_file])
~$global_new_header(S_self, pconstantobject_self[.CLASS = porigin_child])
$global_new_context(S_self[.FILEBINDINGS = eps], pdefaultnew_self.SITE) = eps
$effective_method(S_self, porigin_owner, $ptascii("__construct"), |S_self.CLASSES|) = (pmethoddesc_self)
$method_accessible(S_self, pmethoddesc_self, (porigin_owner))
~$method_accessible(S_self, pmethoddesc_self, (porigin_child))
$call_descriptors_valid(S_self)
S_self_returned = $global_test_find(S_self, ptbytes_self, 11, 1600)
S_self_returned.TODO = (DEFAULT_CTOR_RESULT pdefaultctor_self) :: ptask_self_returned*
pdefaultctor_self.NEW.OBJECT = pdefaultnew_self.OBJECT
$global_new_complete_phase(S_self_returned, pdefaultctor_self.NEW)
$global_new_record(S_self_returned.CONSTANTOBJECTS, pdefaultnew_self.OBJECT) = (pconstantobject_self)
S_self_bind = $global_test_find(S_self_returned, ptbytes_self, 1, 800)
$constant_received_class(S_self_bind, pconstantcontext_self.ORIGIN) = PVINSTANCE pdefaultnew_self.OBJECT pdefaultnew_self.SITE
$global_constant_transfer_valid(S_self_bind, pconstantcontext_self.ORIGIN, PVINSTANCE pdefaultnew_self.OBJECT pdefaultnew_self.SITE, S_self_bind.USERCONSTANTS)
S_parent = $global_test_find(S_self_bind, ptbytes_parent, 9, 1000)
S_parent.TODO = (DEFAULT_NEW_ARGS pdefaultnew_parent) :: ptask_parent*
S_parent.CONSTCONTEXT = (pconstantcontext_parent)
$global_new_record(S_parent.CONSTANTOBJECTS, pdefaultnew_parent.OBJECT) = (pconstantobject_parent)
pconstantobject_parent.CLASS = porigin_parent /\ pconstantobject_parent.DECL = pconstantcontext_parent.ORIGIN
$default_new_scope(S_parent) = (porigin_owner)
$new_source_name(S_parent, pdefaultnew_parent.SITE) = ($ptascii("GlobalNewScopeParent"))
~$global_new_header(S_parent, pconstantobject_parent[.CLASS = porigin_owner])
~$global_new_header(S_parent, pconstantobject_parent[.DECL = pconstantcontext_self.ORIGIN])
~$global_new_header(S_parent, pconstantobject_parent[.SITE = pdefaultnew_self.SITE])
$effective_method(S_parent, porigin_parent, $ptascii("__construct"), |S_parent.CLASSES|) = (pmethoddesc_parent)
$method_accessible(S_parent, pmethoddesc_parent, (porigin_owner))
S_eval = $global_test_find(S_parent, ptbytes_eval, 9, 2200)
S_eval.TODO = (DEFAULT_NEW_ARGS pdefaultnew_eval) :: ptask_eval*
S_eval.CONSTCONTEXT = (pconstantcontext_eval)
pconstantcontext_eval.ORIGIN = PORIGIN n_eval pcpath_eval
n_eval =/= n_file
$global_constant_scope(S_eval, n_eval) = (true, porigin_scope_eval?)
porigin_scope_eval? = (porigin_owner)
$global_new_context(S_eval, pdefaultnew_eval.SITE) = ((porigin_decl_eval, porigin_entry_eval?))
porigin_decl_eval = pconstantcontext_eval.ORIGIN
porigin_entry_eval? = (porigin_owner)
$default_new_scope(S_eval) = (porigin_owner)
$global_new_record(S_eval.CONSTANTOBJECTS, pdefaultnew_eval.OBJECT) = (pconstantobject_eval)
pconstantobject_eval.CLASS = porigin_owner /\ ~pconstantobject_eval.COMPLETE
$global_new_context(S_eval[.EVALBINDINGS = eps], pdefaultnew_eval.SITE) = eps
$global_test_entry_prefix(S_eval.DECLARATIONS, n_eval, 0) = (n_before_eval)
~$global_new_header(S_eval, pconstantobject_eval[.PREFIX = n_before_eval])
~$global_new_header(S_eval, pconstantobject_eval[.SITE = pdefaultnew_self.SITE])
S_done = $global_test_finish(S_eval, 3600)
$global_test_output(S_done.EVENTS) = $ptascii("O:P:O:GlobalNewScopeOwner/GlobalNewScopeParent/GlobalNewScopeOwner")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_self) = (puserconstant_self)
$user_constant_at(S_done.USERCONSTANTS, ptbytes_parent) = (puserconstant_parent)
$user_constant_at(S_done.USERCONSTANTS, ptbytes_eval) = (puserconstant_eval)
puserconstant_self.VALUE = POBJECT pdefaultnew_self.OBJECT /\ puserconstant_self.CLASS = PVINSTANCE pdefaultnew_self.OBJECT pdefaultnew_self.SITE
puserconstant_parent.VALUE = POBJECT pdefaultnew_parent.OBJECT /\ puserconstant_parent.CLASS = PVINSTANCE pdefaultnew_parent.OBJECT pdefaultnew_parent.SITE
puserconstant_eval.VALUE = POBJECT pdefaultnew_eval.OBJECT /\ puserconstant_eval.CLASS = PVINSTANCE pdefaultnew_eval.OBJECT pdefaultnew_eval.SITE
$user_constants_valid(S_done, S_done.USERCONSTANTS)
$global_new_records_valid(S_done, S_done.CONSTANTOBJECTS)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT pdefaultnew_self.OBJECT) <- S_roots.ALLOCATIONS
(HOBJECT pdefaultnew_parent.OBJECT) <- S_roots.ALLOCATIONS
(HOBJECT pdefaultnew_eval.OBJECT) <- S_roots.ALLOCATIONS
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
""")
CHECKS['global-new-throw-escape-retry']=premises(r"""
ptbytes_retry = $ptascii("GLOBAL_NEW_RETRY")
S_args = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_retry, 9, 2200)
S_args.TODO = (DEFAULT_NEW_ARGS pdefaultnew_failed) :: ptask_args*
S_args.CONSTCONTEXT = (pconstantcontext_failed)
pconstantcontext_failed.ORIGIN = PORIGIN n_failed_unit pcpath_failed
$global_new_record(S_args.CONSTANTOBJECTS, pdefaultnew_failed.OBJECT) = (pconstantobject_failed)
pconstantobject_failed.DECL = pconstantcontext_failed.ORIGIN /\ ~pconstantobject_failed.COMPLETE
$global_new_pending(S_args, pdefaultnew_failed)
S_entered = $global_test_find(S_args, ptbytes_retry, 13, 1200)
S_entered.CURRENT = (pcallcontext_ctor)
S_entered.FRAMES = pframe_ctor :: pframe_ctor_tail*
pframe_ctor.TODO = (DEFAULT_CTOR_RESULT pdefaultctor_failed) :: ptask_ctor*
pdefaultctor_failed.NEW.OBJECT = pdefaultnew_failed.OBJECT
pcallcontext_ctor.RECEIVER = (pdefaultnew_failed.OBJECT)
$global_new_frames_busy(S_entered.FRAMES, pdefaultnew_failed.OBJECT)
S_early = S_entered[.CONSTANTOBJECTS = [pconstantobject_failed[.COMPLETE = true]]][.RESULT = KNOWN (POBJECT pdefaultnew_failed.OBJECT)]
~$global_new_records_valid(S_early, S_early.CONSTANTOBJECTS)
$global_new_value_class(S_early, pdefaultnew_failed.SITE) = PVOBJECT
~$constant_value_class_valid(S_early, POBJECT pdefaultnew_failed.OBJECT, PVINSTANCE pdefaultnew_failed.OBJECT pdefaultnew_failed.SITE)
S_escaped = $global_test_find(S_entered, ptbytes_retry, 14, 1400)
S_escaped.GLOBALTABLE = (psymboltable_escaped)
$lookup(psymboltable_escaped.ENV, $ptascii("escaped")) = (n_escape_cell)
S_escaped.STORE[n_escape_cell] = DEFINED (POBJECT pdefaultnew_failed.OBJECT)
$global_new_header(S_escaped, pconstantobject_failed)
(HOBJECT pdefaultnew_failed.OBJECT) <- $prune_allocations(S_escaped).ALLOCATIONS
S_caught = $global_test_find(S_escaped, $ptascii("C1:F:"), 7, 2000)
S_caught.CONSTCONTEXT = eps
$user_constant_at(S_caught.USERCONSTANTS, ptbytes_retry) = eps
$global_new_record(S_caught.CONSTANTOBJECTS, pdefaultnew_failed.OBJECT) = (pconstantobject_failed)
S_caught.GLOBALTABLE = eps
$lookup(S_caught.ENV, $ptascii("escaped")) = (n_escape_cell)
S_caught.STORE[n_escape_cell] = DEFINED (POBJECT pdefaultnew_failed.OBJECT)
(HOBJECT pdefaultnew_failed.OBJECT) <- $prune_allocations(S_caught).ALLOCATIONS
pdefaultnew_failed.OBJECT <- S_caught.DESTRUCTION.CALLED
$global_new_header(S_caught, pconstantobject_failed)
~$constant_value_class_valid(S_caught, POBJECT pdefaultnew_failed.OBJECT, PVINSTANCE pdefaultnew_failed.OBJECT pdefaultnew_failed.SITE)
S_held = $global_test_find(S_caught, $ptascii("C1:F:U:1:"), 7, 1600)
$lookup(S_held.ENV, $ptascii("held")) = (n_held_cell)
S_held.STORE[n_held_cell] = DEFINED (POBJECT pdefaultnew_failed.OBJECT)
S_held.GLOBALTABLE = eps
$lookup(S_held.ENV, $ptascii("escaped")) = eps
(HOBJECT pdefaultnew_failed.OBJECT) <- $prune_allocations(S_held).ALLOCATIONS
S_retry = $global_test_find(S_held, ptbytes_retry, 9, 2200)
S_retry.TODO = (DEFAULT_NEW_ARGS pdefaultnew_retry) :: ptask_retry*
S_retry.CONSTCONTEXT = (pconstantcontext_retry)
pconstantcontext_retry.ORIGIN = PORIGIN n_retry_unit pcpath_retry
n_retry_unit =/= n_failed_unit
pdefaultnew_retry.OBJECT =/= pdefaultnew_failed.OBJECT
pdefaultnew_retry.SITE =/= pdefaultnew_failed.SITE
$global_new_record(S_retry.CONSTANTOBJECTS, pdefaultnew_failed.OBJECT) = (pconstantobject_failed)
$global_new_record(S_retry.CONSTANTOBJECTS, pdefaultnew_retry.OBJECT) = (pconstantobject_retry)
pconstantobject_retry.DECL = pconstantcontext_retry.ORIGIN /\ ~pconstantobject_retry.COMPLETE
~((HOBJECT pdefaultnew_failed.OBJECT) <- S_retry.ALLOCATIONS)
(HOBJECT pdefaultnew_retry.OBJECT) <- S_retry.ALLOCATIONS
$global_new_header(S_retry, pconstantobject_failed)
$global_new_records_valid(S_retry, S_retry.CONSTANTOBJECTS)
~$global_new_header(S_retry, pconstantobject_retry[.DECL = pconstantobject_failed.DECL])
~$global_new_header(S_retry, pconstantobject_retry[.SITE = pconstantobject_failed.SITE])
~$global_new_pending(S_retry[.CONSTANTOBJECTS = [pconstantobject_failed]], pdefaultnew_retry)
S_returned = $global_test_find(S_retry, ptbytes_retry, 11, 2400)
S_returned.TODO = (DEFAULT_CTOR_RESULT pdefaultctor_retry) :: ptask_returned*
pdefaultctor_retry.NEW.OBJECT = pdefaultnew_retry.OBJECT
$global_new_complete_phase(S_returned, pdefaultctor_retry.NEW)
$global_new_record(S_returned.CONSTANTOBJECTS, pdefaultnew_retry.OBJECT) = (pconstantobject_retry)
S_bind = $global_test_find(S_returned, ptbytes_retry, 1, 800)
S_bind.RESULT = KNOWN (POBJECT pdefaultnew_retry.OBJECT)
$global_new_record(S_bind.CONSTANTOBJECTS, pdefaultnew_retry.OBJECT) = (pconstantobject_complete)
pconstantobject_complete = pconstantobject_retry[.COMPLETE = true]
$constant_received_class(S_bind, pconstantcontext_retry.ORIGIN) = PVINSTANCE pdefaultnew_retry.OBJECT pdefaultnew_retry.SITE
$constant_value_class_valid(S_bind, POBJECT pdefaultnew_retry.OBJECT, PVINSTANCE pdefaultnew_retry.OBJECT pdefaultnew_retry.SITE)
~$constant_value_class_valid(S_bind, POBJECT pdefaultnew_failed.OBJECT, PVINSTANCE pdefaultnew_retry.OBJECT pdefaultnew_retry.SITE)
~$global_constant_transfer_valid(S_bind, pconstantcontext_retry.ORIGIN, PVINSTANCE pdefaultnew_failed.OBJECT pdefaultnew_failed.SITE, S_bind.USERCONSTANTS)
S_done = $global_test_finish(S_bind, 2000)
$global_test_output(S_done.EVENTS) = $ptascii("C1:F:U:1:C2:2")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_retry) = (puserconstant_retry)
puserconstant_retry.VALUE = POBJECT pdefaultnew_retry.OBJECT /\ puserconstant_retry.CLASS = PVINSTANCE pdefaultnew_retry.OBJECT pdefaultnew_retry.SITE
S_done.CONSTCONTEXT = eps
$user_constants_valid(S_done, S_done.USERCONSTANTS)
$global_new_records_valid(S_done, S_done.CONSTANTOBJECTS)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT pdefaultnew_failed.OBJECT) <- S_roots.ALLOCATIONS)
(HOBJECT pdefaultnew_retry.OBJECT) <- S_roots.ALLOCATIONS
$global_new_header(S_roots, pconstantobject_failed)
$global_new_records_valid(S_roots, S_roots.CONSTANTOBJECTS)
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
""")


CHECKS['global-new-cold-table-noctor']=premises(r"""
ptbytes_const = $ptascii("GLOBAL_NEW_COLD")
ptbytes_class = $ptascii("GlobalNewColdNoCtor")
S_table = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_const, 15, 1800)
S_table.TODO = (INSTANCE_DEFAULT_UPDATE porigin_class porigin_property z) :: ptask_table*
S_table.CONSTCONTEXT = (pconstantcontext)
S_table.ORIGIN = (porigin_site)
$global_new_context(S_table, porigin_site) = ((pconstantcontext.ORIGIN, eps))
$global_new_current(S_table)
~$new_has_ctor(S_table, ptbytes_class)
$autoload_pending(S_table, ptbytes_class) = false
$class_at(S_table.CLASSES, porigin_class) = (pclassdesc)
pclassdesc.NAME = ptbytes_class
pclassdesc.PROPERTIES = [ppropertydesc]
ppropertydesc.ORIGIN = porigin_property /\ ~ppropertydesc.STATIC
ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer
$instance_default_at(S_table.INSTANCEDEFAULTS, porigin_class, porigin_property) = (pinstancetemplate_pending)
pinstancetemplate_pending.STATE = INSTANCE_PENDING porigin_initializer
S_table.CONSTANTOBJECTS = eps
~((INSTANCE porigin_class) <- S_table.OBJECTS)
$class_constant_new_work(S_table, ptbytes_class, z) = ptask_work*
ptask_work* =/= eps
$origin_node(S_table.SOURCES, porigin_site) = (NExprNew phpType28 (SEQUENCE phpType7_arguments*) metadata)
n_work = |ptask_work*|
n_tail = $(n_work + 1)
ptask_tail* = S_table.TODO[n_tail:|S_table.TODO|]
S_table.TODO = ptask_work* ++ [CLASS_CONST_CONSTRUCT ptbytes_class phpType7_arguments* true z] ++ ptask_tail*
$class_constant_constructor_task(S_table, ptbytes_class, phpType7_arguments*, true, z)
~$class_constant_constructor_task(S_table, ptbytes_class, phpType7_arguments*, false, z)
$call_tasks_valid(S_table, S_table.TODO)
$class_constant_state_valid(S_table)
$global_test_output(S_table.EVENTS) = eps
S_ready = $global_test_find(S_table, ptbytes_const, 16, 2400)
S_ready.TODO = (CLASS_CONST_CONSTRUCT ptbytes_class phpType7_arguments* true z) :: ptask_tail*
S_ready.CONSTCONTEXT = (pconstantcontext_ready)
pconstantcontext_ready.ORIGIN = pconstantcontext.ORIGIN
S_ready.ORIGIN = (porigin_site)
$class_constant_new_work(S_ready, ptbytes_class, z) = eps
$class_constant_table_done(S_ready, porigin_class)
$instance_default_at(S_ready.INSTANCEDEFAULTS, porigin_class, porigin_property) = (pinstancetemplate_filled)
pinstancetemplate_filled.STATE = INSTANCE_VALUE (PINT 2048) PVSCALAR
S_ready.CONSTANTOBJECTS = eps
~((INSTANCE porigin_class) <- S_ready.OBJECTS)
$global_test_output(S_ready.EVENTS) = $ptascii("8192:2;")
$call_task_valid(S_ready, CLASS_CONST_CONSTRUCT ptbytes_class phpType7_arguments* true z)
~$call_task_valid(S_ready, CLASS_CONST_CONSTRUCT ptbytes_class phpType7_arguments* false z)
~$call_task_valid(S_ready, CLASS_CONST_CONSTRUCT ptbytes_class phpType7_arguments* true $(z + 1))
$call_descriptors_valid(S_ready)
S_args = $global_test_next(S_ready)
S_args.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_args*
pdefaultnew.CLASS = ptbytes_class /\ pdefaultnew.SITE = porigin_site
pdefaultnew.INDEX = 0 /\ pdefaultnew.VALUES = eps
S_args.CONSTANTOBJECTS = [pconstantobject]
pconstantobject.OBJECT = pdefaultnew.OBJECT /\ pconstantobject.CLASS = porigin_class /\ ~pconstantobject.COMPLETE
$global_new_pending(S_args, pdefaultnew)
$default_new_valid(S_args, pdefaultnew)
$objectprops_at(S_args.OBJECTPROPS, pdefaultnew.OBJECT) = (ppropertyslot*)
$property_slot_at(ppropertyslot*, $ptascii("p")) = (ppropertyslot_p)
ppropertyslot_p.STATE = PROP_VALUE (DIRECT (PINT 2048))
S_early = S_args[.CONSTANTOBJECTS = [pconstantobject[.COMPLETE = true]]]
~$global_new_records_valid(S_early, S_early.CONSTANTOBJECTS)
S_values = $global_test_find(S_args, ptbytes_const, 10, 2400)
S_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values) :: ptask_values*
pdefaultnew_values.OBJECT = pdefaultnew.OBJECT /\ pdefaultnew_values.INDEX = 1 /\ pdefaultnew_values.VALUES = [PINT 2048]
$global_test_output(S_values.EVENTS) = $ptascii("8192:2;8192:4;")
$global_new_record(S_values.CONSTANTOBJECTS, pdefaultnew.OBJECT) = (pconstantobject)
$global_new_complete_phase(S_values, pdefaultnew_values)
S_done = $global_test_finish(S_values, 2600)
$global_test_output(S_done.EVENTS) = $ptascii("8192:2;8192:4;2048")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_const) = (puserconstant)
puserconstant.VALUE = POBJECT pdefaultnew.OBJECT /\ puserconstant.CLASS = PVINSTANCE pdefaultnew.OBJECT porigin_site
$global_new_record(S_done.CONSTANTOBJECTS, pdefaultnew.OBJECT) = (pconstantobject_complete)
pconstantobject_complete = pconstantobject[.COMPLETE = true]
$global_new_records_valid(S_done, S_done.CONSTANTOBJECTS)
$user_constants_valid(S_done, S_done.USERCONSTANTS)
S_roots = $prune_allocations(S_done[.ENV = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT pdefaultnew.OBJECT) <- S_roots.ALLOCATIONS
$heap_owners($heap_graph(S_roots), HOBJECT pdefaultnew.OBJECT) = 1
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
""")

def prepare(out):
    names=('SOURCES','FILES','EVALS','PREFIX','CHECKS')
    saved={name:getattr(global_protocol,name) for name in names}
    try:
        for name in names:setattr(global_protocol,name,globals()[name])
        return global_protocol.prepare(out)
    finally:
        for name,value in saved.items():setattr(global_protocol,name,value)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only');parser.add_argument('--output')
    arguments=parser.parse_args()
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='global-constant-objects-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        watched=[Path(__file__),Path(global_protocol.__file__)]
        before={str(p):base.sha(p) for p in watched}
        original=base.prepare
        try:
            base.prepare=prepare;base.run(out)
        finally:
            base.prepare=original
        report=json.loads((out/'report.json').read_text())
        report.update(protocol_inputs=before,protocols_unchanged=before=={str(p):base.sha(p) for p in watched})
        if not report['protocols_unchanged']:report['result']='failed'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        assert report['protocols_unchanged'],'protocol changed'
    print(out)

if __name__=='__main__':
    main()
