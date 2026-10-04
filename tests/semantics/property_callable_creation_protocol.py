#!/usr/bin/env python3
"""Check copied property-method creator identity and nonowning retirement."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

protocol.SOURCES = {'cached-method-static-child': '<?php\n'
                               'trait Factory {\n'
                               "    private const TOKEN = 'secret';\n"
                               '    private static function maker() {\n'
                               '        return static function () {\n'
                               "            return self::class . '/' . get_called_class() . "
                               "'/' . static::class . ':' . self::TOKEN;\n"
                               '        };\n'
                               '    }\n'
                               '    public static \\Closure $f = self::maker(...);\n'
                               '}\n'
                               'class ScopeA { use Factory; }\n'
                               '$first = ScopeA::$f;\n'
                               '$firstChild = $first();\n'
                               "echo $firstChild(), ';';\n"
                               'unset($firstChild);\n'
                               'if (true) { class ScopeB { use Factory; } }\n'
                               '$maker = ScopeB::$f;\n'
                               '$child = $maker();\n'
                               '$clone = clone $maker;\n'
                               '$cloneChild = $clone();\n'
                               'ScopeA::$f = static function () {};\n'
                               'ScopeB::$f = static function () {};\n'
                               'unset($first, $maker, $clone);\n'
                               "echo $child(), ':', $cloneChild();\n",
 'cached-method-default-child': '<?php\n'
                                'trait Factory {\n'
                                '    private static function maker() {\n'
                                '        return function ($value = new self) {\n'
                                "            return self::class . '/' . get_called_class() . "
                                "'/' . $value::class;\n"
                                '        };\n'
                                '    }\n'
                                '    public static \\Closure $f = self::maker(...);\n'
                                '}\n'
                                'class ScopeA {\n'
                                '    use Factory;\n'
                                "    private function __construct() { echo 'A:'; }\n"
                                '}\n'
                                '$first = ScopeA::$f;\n'
                                'if (true) {\n'
                                '    class ScopeB {\n'
                                '        use Factory;\n'
                                "        private function __construct() { echo 'B:'; }\n"
                                '    }\n'
                                '}\n'
                                '$maker = ScopeB::$f;\n'
                                '$clone = clone $maker;\n'
                                '$child = $clone();\n'
                                '$childClone = clone $child;\n'
                                'ScopeA::$f = static function () {};\n'
                                'ScopeB::$f = static function () {};\n'
                                'unset($first, $maker, $clone, $child);\n'
                                'echo $childClone();\n'}

protocol.PREFIX = r'''
dec $property_child_test_resume(pstate) : pstate
def $property_child_test_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $property_child_test_resume(S) = S -- otherwise
dec $property_child_test_output(pevent*) : ptbytes
def $property_child_test_output(eps) = eps
def $property_child_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $property_child_test_output(pevent*)
dec $property_child_test_stage(pstate, nat) : bool
def $property_child_test_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_maker
  -- if $(n_maker < |S.OBJECTS|)
  -- if S.OBJECTS[n_maker] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site porigin_called eps)
  -- if pcallcontext.LEXICAL_CLASS = pcallcontext.CALLED_CLASS
  -- if S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
def $property_child_test_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_maker
  -- if $(n_maker < |S.OBJECTS|)
  -- if S.OBJECTS[n_maker] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site porigin_called eps)
  -- if pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS
  -- if S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
def $property_child_test_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_maker
  -- if $(n_maker < |S.OBJECTS|)
  -- if S.OBJECTS[n_maker] = METHODCLOSURE porigin_method porigin_site porigin_called eps
  -- if pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS
  -- if S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
def $property_child_test_stage(S, n_stage) = false -- otherwise
dec $property_child_test_seek(pstate, nat, nat) : pstate
def $property_child_test_seek(S, n_stage, n_limit) = S
  -- if $property_child_test_stage(S, n_stage)
def $property_child_test_seek(S, n_stage, n_limit) = $property_child_test_seek($property_child_test_resume(S_next), n_stage, n_rest)
  -- if ~$property_child_test_stage(S, n_stage)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''

def premises(text):return text.strip().splitlines()

COMMON = premises(r'''
S.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_maker
pcallcontext.LEXICAL_CLASS = (porigin_a)
pcallcontext.CALLED_CLASS = (porigin_b)
porigin_a =/= porigin_b
S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
$object_body(S.OBJECTS[n_maker]) = METHODCLOSURE pcallcontext.FUNCTION porigin_site porigin_b eps
$class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = (pmethoddesc_a)
$closure_scope_at(S.CLOSURESCOPES, n_maker) = (pclosurescope_maker)
$closure_scope_at(S.CLOSURESCOPES, n_child) = (pclosurescope_child)
$object_body(S.OBJECTS[n_child]) = REALCLOSURE porigin_child pitem* eps
$function_at(S.CLOSURETEMPLATES, porigin_child) = (pfunction_child)
pclosurescope_child.CREATION = (pclosurecreation)
pclosurecreation.EVIDENCE = (pclosurecreator)
pclosurecreator.SCOPE = CLOSURE_SCOPE pclosurescope_maker
pclosurecreation.FUNCTION = pcallcontext.FUNCTION
pclosurecreation.CALLSITE = pcallcontext.CALLSITE
pclosurecreator.CALLSITE = pcallcontext.CALLSITE
pclosurescope_child.LEXICAL = porigin_a /\ pclosurescope_child.CALLED = porigin_b
pclosurescope_child.RECEIVER = eps /\ ~pclosurecreation.RECEIVER
$closure_scope_row_valid(S, pclosurescope_maker)
$property_method_scope_valid(S, pclosurescope_maker)
$property_callable_method_owner(S, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker) = (porigin_b)
$closure_evidence_current(S) = (CLOSURE_SCOPE pclosurescope_maker)
$closure_evidence_body(S, n_maker) = (pcallcontext.FUNCTION)
$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation, pclosurecreator)
~$closure_scope_original_classes(S, porigin_child, pclosurescope_child)
$closure_scope_classes_valid(S, porigin_child, pclosurescope_child)
$closure_scope_creation_valid(S, porigin_child, pclosurescope_child)
$closure_scope_row_valid(S, pclosurescope_child)
$closure_capture_valid(S, n_child, 0)
$call_current_valid(S)
''')

RETIREMENT = premises(r'''
S_done = $drive_steps(S_last, 6000)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$closure_scope_rows_valid(S_done, S_done.CLOSURESCOPES)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
$closure_scope_at(S_done.CLOSURESCOPES, n_maker) = eps
$property_callable_method_owner(S_done, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker) = eps
$property_method_scope_valid(S_done, pclosurescope_maker)
$closure_evidence_valid(S_done, CLOSURE_SCOPE pclosurescope_maker)
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 0
''')

protocol.CHECKS = {'cached-method-static-child': premises(r'''
S_a = $property_child_test_seek(S_initial[.COMPLETION = NORMAL], 0, 6000)
S_a.CURRENT = (pcallcontext_a)
pcallcontext_a.TARGET = CLOSURE_TARGET n_first_maker
S_a.TODO = (CLOSURE_CAPTURE n_first_child 0) :: ptask_first*
$closure_scope_at(S_a.CLOSURESCOPES, n_first_child) = (pclosurescope_first)
$object_body(S_a.OBJECTS[n_first_child]) = REALCLOSURE porigin_first pitem_first* eps
pclosurescope_first.CREATION = (pclosurecreation_first)
pclosurecreation_first.EVIDENCE = (pclosurecreator_first)
$closure_scope_original_classes(S_a, porigin_first, pclosurescope_first)
$property_method_child_valid(S_a, porigin_first, pclosurescope_first)
$closure_scope_classes_valid(S_a, porigin_first, pclosurescope_first)
$closure_scope_creation_valid(S_a, porigin_first, pclosurescope_first)
$closure_scope_row_valid(S_a, pclosurescope_first)
S = $property_child_test_seek(S_a, 1, 6000)
''') + COMMON + premises(r'''
$closure_static(S, pfunction_child)
$constant_callable_record(S.CONSTANTCLOSURES, n_maker) = (pconstantclosure_maker)
$property_callable_method_receipt_owner(S, pconstantclosure_maker, pmethoddesc_a, porigin_site, porigin_b) = (porigin_b)
~$property_method_scope_valid(S, pclosurescope_maker[.LEXICAL = porigin_b])
~$property_method_scope_valid(S, pclosurescope_maker[.CALLED = porigin_a])
~$property_method_scope_valid(S, pclosurescope_maker[.OBJECT = n_child])
~$property_method_scope_valid(S, pclosurescope_maker[.RECEIVER = (n_child)])
~$property_method_child_valid(S, porigin_child, pclosurescope_child[.CREATION = eps])
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.FUNCTION = porigin_child], pclosurecreator)
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.CALLSITE = (porigin_child)], pclosurecreator)
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.RECEIVER = true], pclosurecreator)
~$closure_creator_valid(S, porigin_child, pclosurescope_child[.LEXICAL = porigin_b], pclosurecreation, pclosurecreator)
~$closure_creator_valid(S, porigin_child, pclosurescope_child[.CALLED = porigin_a], pclosurecreation, pclosurecreator)
n_sources = |S.SOURCES|
porigin_missing = PORIGIN n_sources [PCFIELD 0]
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.CALLSITE = (porigin_missing)], pclosurecreator[.CALLSITE = (porigin_missing)])
~$property_method_scope_valid(S[.CONSTANTCLOSURES = eps], pclosurescope_maker)
$effective_method(S, porigin_b, $ptascii("maker"), |S.CLASSES|) = (pmethoddesc_b)
pmethoddesc_a.FUNCTION.ORIGIN =/= pmethoddesc_b.FUNCTION.ORIGIN
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.FUNCTION = pmethoddesc_b.FUNCTION.ORIGIN], pclosurecreator)
$trait_imported_origin(pcallcontext.FUNCTION)
$origin_source(pcallcontext.FUNCTION) =/= pcallcontext.FUNCTION
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.FUNCTION = $origin_source(pcallcontext.FUNCTION)], pclosurecreator)
S_clone = $property_child_test_seek(S, 2, 6000)
S_clone.CURRENT = (pcallcontext_clone)
pcallcontext_clone.TARGET = CLOSURE_TARGET n_clone_maker
S_clone.OBJECTS[n_clone_maker] = METHODCLOSURE pcallcontext.FUNCTION porigin_site porigin_b eps
$closure_scope_at(S_clone.CLOSURESCOPES, n_clone_maker) = (pclosurescope_clone_maker)
$property_method_scope_valid(S_clone, pclosurescope_clone_maker)
$constant_callable_record(S_clone.CONSTANTCLOSURES, n_clone_maker) = eps
S_clone.TODO = (CLOSURE_CAPTURE n_clone_child 0) :: ptask_clone*
$closure_scope_at(S_clone.CLOSURESCOPES, n_clone_child) = (pclosurescope_clone_child)
$closure_scope_row_valid(S_clone, pclosurescope_clone_child)
S_last = S_clone
''') + RETIREMENT + premises(r'''
$property_child_test_output(S_done.EVENTS) = $ptascii("ScopeA/ScopeA/ScopeA:secret;ScopeA/ScopeB/ScopeB:secret:ScopeA/ScopeB/ScopeB:secret")
~((HOBJECT n_first_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_clone_maker) <- S_done.ALLOCATIONS)
$closure_scope_at(S_done.CLOSURESCOPES, n_clone_maker) = eps
$property_method_scope_valid(S_done, pclosurescope_clone_maker)
$closure_evidence_valid(S_done, CLOSURE_SCOPE pclosurescope_clone_maker)
$closure_creator_valid(S_done, porigin_child, pclosurescope_child, pclosurecreation, pclosurecreator)
$closure_scope_row_valid(S_done, pclosurescope_child)
S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN (POBJECT n_child)][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_clone_child) <- S_dead.ALLOCATIONS)
$closure_scope_row_valid(S_dead, pclosurescope_child)
$closure_evidence_valid(S_dead, CLOSURE_SCOPE pclosurescope_maker)
$heap_owners($heap_graph(S_dead), HOBJECT n_maker) = 0
$heap_owners($heap_graph(S_dead), HOBJECT n_clone_maker) = 0
$heap_owners($heap_graph(S_dead), HOBJECT n_child) = 1
'''),
'cached-method-default-child': premises(r'''
S = $property_child_test_seek(S_initial[.COMPLETION = NORMAL], 2, 6000)
''') + COMMON + premises(r'''
~$closure_static(S, pfunction_child)
~$closure_receiver_forbidden(S, porigin_child)
$closure_static_method_owner(S, porigin_child)
$closure_scope_receiver_free(S, porigin_child, pclosurescope_child)
$constant_callable_record(S.CONSTANTCLOSURES, n_maker) = eps
S_last = S
''') + RETIREMENT + premises(r'''
$property_child_test_output(S_done.EVENTS) = $ptascii("A:ScopeA/ScopeB/ScopeA")
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
$closure_scope_at(S_done.CLOSURESCOPES, n_child) = eps
$lookup(S_done.ENV, $ptascii("childClone")) = (n_cell_clone)
S_done.CELLS[n_cell_clone] = DIRECT (POBJECT n_child_clone)
$closure_scope_at(S_done.CLOSURESCOPES, n_child_clone) = (pclosurescope_child_clone)
pclosurescope_child_clone.CREATION = pclosurescope_child.CREATION
pclosurescope_child_clone.RECEIVER = eps
$closure_scope_row_valid(S_done, pclosurescope_child_clone)
$property_method_child_valid(S_done, porigin_child, pclosurescope_child_clone)
S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN (POBJECT n_child_clone)][.BASE = BASE_VALUE (KNOWN PNULL)])
$closure_scope_row_valid(S_dead, pclosurescope_child_clone)
$closure_evidence_valid(S_dead, CLOSURE_SCOPE pclosurescope_maker)
$heap_owners($heap_graph(S_dead), HOBJECT n_maker) = 0
$heap_owners($heap_graph(S_dead), HOBJECT n_child) = 0
$heap_owners($heap_graph(S_dead), HOBJECT n_child_clone) = 1
''')}

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='property-callable-creation-',dir=protocol.ROOT/'.tools'))/'run')
