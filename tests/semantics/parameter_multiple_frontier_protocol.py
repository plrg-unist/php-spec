#!/usr/bin/env python3
"""Genuine multi-frontier default reads, partial retry and nested warm caches."""
import argparse,tempfile
from pathlib import Path
from textwrap import dedent
import parameter_alias_causality_protocol as causal

global_protocol=causal.global_protocol
base=causal.base
ROOT=causal.ROOT
premises=causal.premises
FILES={}
PREFIX=causal.PREFIX

# The first original is byte-identical to the historical306 Unsupported source.
SOURCES={'parameter-multiple-two-frontiers':causal.SOURCES['parameter-generation-two-frontiers']}
EVALS={'parameter-multiple-two-frontiers':causal.EVALS['parameter-generation-two-frontiers'][:]}
OUTPUTS={'parameter-multiple-two-frontiers':'H1|H2|old1:new1:old2:new2:g1:l1:g2:l2'}

SOURCES['parameter-multiple-warm-repeat']=SOURCES['parameter-multiple-two-frontiers'].split('    $a = take();',1)[0]+dedent('''\
    $a = take();
    $b = take();
    echo 'warm:', $a[1] !== $b[1] ? 'fresh:' : 'wrong:';
    echo $a[4] !== $b[4] ? 'fresh:' : 'wrong:';
    echo $b[0] === ParameterGenerationMultiFirst && $b[0] === $b[2] ? 'same:' : 'wrong:';
    echo $b[3] === ParameterGenerationMultiSecond && $b[3] === $b[5] ? 'same' : 'wrong';
}
''')
EVALS['parameter-multiple-warm-repeat']=EVALS['parameter-multiple-two-frontiers'][:]
OUTPUTS['parameter-multiple-warm-repeat']='H1|H2|warm:fresh:fresh:same:same'

SOURCES['parameter-multiple-stable-prefix']=dedent('''\
<?php
namespace {
    const MultipleStableSeed = static function () { return 'global'; };
    trait MultipleStableLeft { public static function target() { return 'left'; } }
    trait MultipleStableRight { public static function target() { return 'right'; } }
}
namespace MultipleStable {
    function take($a = [MultipleStableSeed, \\MultipleStableLeft::target(...),
                       MultipleStableSeed, \\MultipleStableRight::target(...),
                       MultipleStableSeed]) { return $a; }
    $seen = 0;
    set_error_handler(function ($level, $message) use (&$seen) {
        ++$seen;
        echo 'H', $seen, '|';
        if ($seen === 1) {
            eval('namespace MultipleStable; const UnrelatedLeft = static function () { return "left"; };');
        } else {
            eval('namespace MultipleStable; const UnrelatedRight = static function () { return "right"; };');
        }
        return true;
    });
    $a = take();
    echo $a[0] === $a[2] && $a[2] === $a[4] ? 'same:' : 'wrong:';
    echo $a[0](), ':', $a[2](), ':', $a[4](), ':', $a[1](), ':', $a[3]();
}
''')
EVALS['parameter-multiple-stable-prefix']=[
    'namespace MultipleStable; const UnrelatedLeft = static function () { return "left"; };',
    'namespace MultipleStable; const UnrelatedRight = static function () { return "right"; };']
OUTPUTS['parameter-multiple-stable-prefix']='H1|H2|same:global:global:global:left:right'

SOURCES['parameter-multiple-partial-retry']=dedent('''\
<?php
namespace {
    const MultipleRetryFirst = static function () { return 'g1'; };
    const MultipleRetrySecond = static function () { return 'g2'; };
    trait MultipleRetryLeft { public static function target() { return 'left'; } }
    trait MultipleRetryRight { public static function target() { return 'right'; } }
}
namespace MultipleRetry {
    function take($a = [MultipleRetryFirst, \\MultipleRetryLeft::target(...),
                       MultipleRetryFirst, MultipleRetrySecond,
                       \\MultipleRetryRight::target(...), MultipleRetrySecond]) { return $a; }
    $seen = 0;
    set_error_handler(function ($level, $message) use (&$seen) {
        ++$seen;
        echo 'H', $seen, '|';
        if ($seen === 1) {
            eval('namespace MultipleRetry; const MultipleRetryFirst = static function () { return "l1"; };');
        } elseif ($seen === 2) {
            eval('namespace MultipleRetry; const MultipleRetrySecond = static function () { return "l2"; };');
            throw new \\Exception('stop');
        }
        return true;
    });
    try { take(); } catch (\\Exception $e) { echo 'X|'; }
    $a = take();
    echo $a[0](), ':', $a[2](), ':', $a[3](), ':', $a[5](), ':', $a[1](), ':', $a[4]();
}
''')
EVALS['parameter-multiple-partial-retry']=[
    'namespace MultipleRetry; const MultipleRetryFirst = static function () { return "l1"; };',
    'namespace MultipleRetry; const MultipleRetrySecond = static function () { return "l2"; };']
OUTPUTS['parameter-multiple-partial-retry']='H1|H2|X|H3|l1:l1:l2:l2:left:right'

SOURCES['parameter-multiple-deprecated-capture']=dedent('''\
<?php
namespace {
    const MultipleDeprecatedSeed = static function () { return 'global'; };
    trait MultipleDeprecatedTrait { public static function target() { return 'trait'; } }
}
namespace MultipleDeprecated {
    function take($a = [MultipleDeprecatedSeed, \\MultipleDeprecatedTrait::target(...),
                       MultipleDeprecatedSeed, E_STRICT, MultipleDeprecatedSeed]) { return $a; }
    $seen = 0;
    set_error_handler(function ($level, $message) use (&$seen) {
        ++$seen;
        echo 'H', $seen, '|';
        if ($seen === 1) {
            eval('namespace MultipleDeprecated; const MultipleDeprecatedSeed = static function () { return "local"; };');
        } else {
            eval('namespace MultipleDeprecated; const E_STRICT = 17;');
        }
        return true;
    });
    $a = take();
    echo $a[0](), ':', $a[2](), ':', $a[3], ':', $a[4](), '|', E_STRICT;
}
''')
EVALS['parameter-multiple-deprecated-capture']=[
    'namespace MultipleDeprecated; const MultipleDeprecatedSeed = static function () { return "local"; };',
    'namespace MultipleDeprecated; const E_STRICT = 17;']
OUTPUTS['parameter-multiple-deprecated-capture']='H1|H2|global:local:2048:local|17'

SOURCES['parameter-multiple-deprecated-preshadow']=SOURCES['parameter-multiple-deprecated-capture'].replace('MultipleDeprecated','MultiplePreshadow').replace('''        if ($seen === 1) {
            eval('namespace MultiplePreshadow; const MultiplePreshadowSeed = static function () { return "local"; };');
        } else {
            eval('namespace MultiplePreshadow; const E_STRICT = 17;');
        }''','''        eval('namespace MultiplePreshadow; const MultiplePreshadowSeed = static function () { return "local"; }; const E_STRICT = 17;');''')
EVALS['parameter-multiple-deprecated-preshadow']=[
    'namespace MultiplePreshadow; const MultiplePreshadowSeed = static function () { return "local"; }; const E_STRICT = 17;']
OUTPUTS['parameter-multiple-deprecated-preshadow']='H1|global:local:17:local|17'

SOURCES['parameter-multiple-named-hole']=SOURCES['parameter-multiple-two-frontiers'].replace(']) { return $a; }',"], $tag = 'default') { return [$a, $tag]; }").replace('$a = take();',"$x = take(tag: 'named');\n    $a = $x[0];").replace('echo $v0(),',"echo $x[1], '|';\n    echo $v0(),")
EVALS['parameter-multiple-named-hole']=EVALS['parameter-multiple-two-frontiers'][:]
OUTPUTS['parameter-multiple-named-hole']='H1|H2|old1:new1:old2:new2:named|g1:l1:g2:l2'

# Independently proposed nested original, copied verbatim before any execution.
SOURCES['parameter-multiple-nested-cache']=dedent('''\
<?php
namespace {
    const MultipleNestedSeed = static function () { return 'global'; };
    trait MultipleNestedLeft { public static function target() { return 'left'; } }
    trait MultipleNestedRight { public static function target() { return 'right'; } }
}
namespace MultipleNested {
    function take($a = [MultipleNestedSeed, \\MultipleNestedLeft::target(...),
                       MultipleNestedSeed, \\MultipleNestedRight::target(...),
                       MultipleNestedSeed]) { return $a; }
    function driver() { return take(); }
    $seen = 0;
    $inner = [];
    set_error_handler(function ($level, $message) use (&$seen, &$inner) {
        ++$seen;
        echo 'H', $seen, '|';
        eval('namespace MultipleNested; const MultipleNestedSeed = static function () { return "local"; };');
        set_error_handler(function ($level, $message) use (&$seen) {
            ++$seen;
            echo 'H', $seen, '|';
            return true;
        });
        $inner = driver();
        echo 'I:', $inner[0](), ':', $inner[2](), ':', $inner[4](), '|';
        return true;
    });
    $outer = driver();
    $warm = driver();
    echo 'O:', $outer[0](), ':', $outer[2](), ':', $outer[4](), '|';
    echo $outer[1] !== $inner[1] ? 'left-fresh:' : 'wrong:';
    echo $outer[3] !== $inner[3] ? 'right-fresh:' : 'wrong:';
    echo $warm[1] !== $outer[1] && $warm[3] !== $outer[3] ? 'warm-fresh:' : 'wrong:';
    echo $seen;
}
''')
EVALS['parameter-multiple-nested-cache']=[
    'namespace MultipleNested; const MultipleNestedSeed = static function () { return "local"; };']
OUTPUTS['parameter-multiple-nested-cache']='H1|H2|H3|I:local:local:local|O:global:local:local|left-fresh:right-fresh:warm-fresh:3'

def bind_checks(namespace,owner=1,start='S_initial[.COMPLETION = NORMAL]',named=False):
    return premises(fr'''
ptbytes_function = {causal.function_name(namespace)}
S = $causal_test_seek({start}, ptbytes_function, {1 if named else 0}, {owner}, 18000)
S.TODO = ({'NAMED_DEFAULT_BIND' if named else 'DEFAULT_BIND'} porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
S.CURRENT = (pcallcontext)
pcallcontext.DEFAULTRECEIVE = (preceiveowner)
preceiveowner.ID = {owner}
$parameter_receive_birth(S, {owner}) = (preceivebirth)
preceivebirth.ACTIVE
$parameter_multiple_order(S, preceivebirth, eps) = (preceiveorder)
|preceiveorder.EFFECTS| = 2
$parameter_multiple_unique(preceiveorder.EFFECTS)
$parameter_multiple_registrations(S, preceivebirth, {owner}, preceiveorder, S.USERCONSTANTS, 0, eps)
$parameter_multiple_facts(S, preceivebirth, {owner}, preceiveorder, pconstantcontext.FACTS)
$parameter_multiple_values(S, preceivebirth, {owner}, preceiveorder, preceiveorder.EFFECTS)
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S))
$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_receive_state_valid(S) /\ $call_descriptors_valid(S)
''')

def leaf(index):
    return f'$constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX {index}, PCFIELD 1])'

def lookup_checks(indices,owner=1):
    checks=[]
    for index,prefix in indices:
        checks+=premises(f'''
porigin_leaf{index} = {leaf(index)}
$constant_fact_at(pconstantcontext.FACTS, porigin_leaf{index}) = (pconstantfact_leaf{index})
pconstantfact_leaf{index}.LOOKUP = (pconstantlookup_leaf{index})
pconstantlookup_leaf{index}.PREFIX = {prefix}
$parameter_multiple_lookup_prefix(S, preceivebirth, {owner}, preceiveorder, porigin_leaf{index}) = ({prefix})
$global_constant_lookup_valid(S, preceivebirth.ORIGIN, pconstantfact_leaf{index}, S.USERCONSTANTS)
''')
    return checks

TWO_CUTS=premises(r'''
preceivebirth.PREFIX = 2 /\ |S.USERCONSTANTS| = 4
preceiveorder.EFFECTS = [porigin_first, porigin_second]
porigin_first = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
porigin_second = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 4, PCFIELD 1])
S.USERCONSTANTS = [puserconstant_global_first, puserconstant_global_second, puserconstant_local_first, puserconstant_local_second]
$parameter_receive_cut_at(puserconstant_local_first.RECEIVES, 1) = (preceivecut_first)
$parameter_receive_cut_at(puserconstant_local_second.RECEIVES, 1) = (preceivecut_second)
$parameter_receive_frontier_site(preceivecut_first.FRONTIER) = (porigin_first)
$parameter_receive_frontier_site(preceivecut_second.FRONTIER) = (porigin_second)
$parameter_receive_cut_valid(S, preceivebirth, porigin_first, puserconstant_local_first, preceivecut_first)
$parameter_receive_cut_valid(S, preceivebirth, porigin_second, puserconstant_local_second, preceivecut_second)
$parameter_receive_donor_source(S, puserconstant_global_first)
$parameter_receive_donor_source(S, puserconstant_local_first)
$parameter_receive_donor_source(S, puserconstant_global_second)
$parameter_receive_donor_source(S, puserconstant_local_second)
puserconstant_local_first.ORIGIN = PORIGIN n_first pcpath_first
puserconstant_local_second.ORIGIN = PORIGIN n_second pcpath_second
$eval_binding_at(S.EVALBINDINGS, n_first) = (pevalbinding_first)
$eval_binding_at(S.EVALBINDINGS, n_second) = (pevalbinding_second)
pevalbinding_first.USERPREFIX = 2 /\ pevalbinding_second.USERPREFIX = 3
$parameter_receive_ingress_valid(S, pevalbinding_first)
$parameter_receive_ingress_valid(S, pevalbinding_second)
$parameter_receive_ingress_prefix(S.EVALBINDINGS, 1, |S.USERCONSTANTS|) = 2
S_role = S[.USERCONSTANTS[2].RECEIVES = ([preceivecut_first[.FRONTIER = preceivecut_second.FRONTIER]])]
$heap_valid($heap_graph(S_role))
~$parameter_receive_cut_valid(S_role, preceivebirth, porigin_second, S_role.USERCONSTANTS[2], preceivecut_first[.FRONTIER = preceivecut_second.FRONTIER])
~$parameter_default_transfer_valid(S_role, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_owner = S[.USERCONSTANTS[2].RECEIVES = ([preceivecut_first[.OWNER = 2]])]
~$parameter_default_transfer_valid(S_owner, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_no_cut = S[.USERCONSTANTS[2].RECEIVES = eps]
S_erased = S_no_cut[.EVALBINDINGS = [pevalbinding_first[.RECEIVES = eps], pevalbinding_second]]
|S_erased.USERCONSTANTS| = 4
$constant_value_class_valid(S_erased, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S_erased))
~$parameter_receive_donor_source(S_erased, S_erased.USERCONSTANTS[2])
~$parameter_default_transfer_valid(S_erased, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
''')

CHECKS={}
first=bind_checks('ParameterGenerationMulti')+TWO_CUTS+lookup_checks([(0,2),(2,3),(3,3),(5,4)])
first+=premises(r'''
$global_test_output(S.EVENTS) = $ptascii("H1|H2|")
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_method_first)), ENTRY (KINT 2) (DIRECT (POBJECT n_local_first)), ENTRY (KINT 3) (DIRECT (POBJECT n_old_second)), ENTRY (KINT 4) (DIRECT (POBJECT n_method_second)), ENTRY (KINT 5) (DIRECT (POBJECT n_local_second))]
n_old_first =/= n_local_first /\ n_old_second =/= n_local_second
$parameter_callable_cached_method(S, porigin_first) =/= eps
$parameter_callable_cached_method(S, porigin_second) =/= eps
''')
CHECKS['parameter-multiple-two-frontiers']=first+causal.finish_checks(OUTPUTS['parameter-multiple-two-frontiers'],1)

CHECKS['parameter-multiple-warm-repeat']=first+premises(r'''
S_first_bound = $donor_test_step(S)
S_first_bound.COMPLETION = NORMAL
S_warm = $causal_test_seek(S_first_bound, ptbytes_function, 0, 2, 18000)
$parameter_receive_birth(S_warm, 1) = (preceivebirth_closed)
~preceivebirth_closed.ACTIVE
$parameter_receive_birth(S_warm, 2) = (preceivebirth_warm)
preceivebirth_warm.ACTIVE /\ preceivebirth_warm.PREFIX = 4
S_warm.RESULT = KNOWN (PARRAY n_warm)
S_warm.ARRAYS[n_warm].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_method_warm_first)), ENTRY (KINT 2) (DIRECT (POBJECT n_local_first)), ENTRY (KINT 3) (DIRECT (POBJECT n_local_second)), ENTRY (KINT 4) (DIRECT (POBJECT n_method_warm_second)), ENTRY (KINT 5) (DIRECT (POBJECT n_local_second))]
n_method_warm_first =/= n_method_first /\ n_method_warm_second =/= n_method_second
S_warm.USERCONSTANTS = S.USERCONSTANTS /\ S_warm.EVALBINDINGS = S.EVALBINDINGS
$parameter_receive_cut_at(puserconstant_local_first.RECEIVES, 2) = eps
$parameter_receive_cut_at(puserconstant_local_second.RECEIVES, 2) = eps
S_warm.CONSTCONTEXT = (pconstantcontext_warm)
$constant_fact_at(pconstantcontext_warm.FACTS, pdefault.ORIGIN) = (pconstantfact_warm_root)
$parameter_multiple_order(S_warm, preceivebirth_warm, eps) = (preceiveorder)
$parameter_multiple_registrations(S_warm, preceivebirth_warm, 2, preceiveorder, S_warm.USERCONSTANTS, 0, eps)
$parameter_multiple_facts(S_warm, preceivebirth_warm, 2, preceiveorder, pconstantcontext_warm.FACTS)
$parameter_multiple_lookup_prefix(S_warm, preceivebirth_warm, 2, preceiveorder, porigin_leaf0) = (4)
$parameter_multiple_lookup_prefix(S_warm, preceivebirth_warm, 2, preceiveorder, porigin_leaf5) = (4)
$parameter_default_transfer_valid(S_warm, pfunction, 0, PARRAY n_warm, pconstantfact_warm_root.CLASS)
$parameter_receive_state_valid(S_warm) /\ $call_descriptors_valid(S_warm)
S_warm_transplant = S_warm[.USERCONSTANTS[2].RECEIVES = ([preceivecut_first[.OWNER = 2]])]
S_warm_transplant.EVALBINDINGS = S_warm.EVALBINDINGS
$constant_value_class_valid(S_warm_transplant, PARRAY n_warm, pconstantfact_warm_root.CLASS)
$heap_valid($heap_graph(S_warm_transplant))
~$parameter_default_transfer_valid(S_warm_transplant, pfunction, 0, PARRAY n_warm, pconstantfact_warm_root.CLASS)
''')+causal.finish_checks(OUTPUTS['parameter-multiple-warm-repeat'],2,'S_warm')

CHECKS['parameter-multiple-stable-prefix']=bind_checks('MultipleStable')+lookup_checks([(0,1),(2,2),(4,3)])+premises(r'''
preceivebirth.PREFIX = 1 /\ |S.USERCONSTANTS| = 3
pconstantlookup_leaf0.DECL = pconstantlookup_leaf2.DECL /\ pconstantlookup_leaf2.DECL = pconstantlookup_leaf4.DECL
pconstantfact_leaf0.CLASS = pconstantfact_leaf2.CLASS /\ pconstantfact_leaf2.CLASS = pconstantfact_leaf4.CLASS
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_seed)), ENTRY (KINT 1) (DIRECT (POBJECT n_left)), ENTRY (KINT 2) (DIRECT (POBJECT n_seed)), ENTRY (KINT 3) (DIRECT (POBJECT n_right)), ENTRY (KINT 4) (DIRECT (POBJECT n_seed))]
pconstantfact_future = pconstantfact_leaf2[.LOOKUP = (pconstantlookup_leaf2[.PREFIX = 3])]
pconstantcontext_future = pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS, pconstantfact_future)]
S_future = S[.CONSTCONTEXT = (pconstantcontext_future)]
$global_constant_lookup_valid(S_future, preceivebirth.ORIGIN, pconstantfact_future, S_future.USERCONSTANTS)
$default_context_valid(S_future, pconstantcontext_future)
$constant_value_class_valid(S_future, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S_future))
~$parameter_multiple_facts(S_future, preceivebirth, 1, preceiveorder, pconstantcontext_future.FACTS)
~$parameter_default_transfer_valid(S_future, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
pconstantfact_stale = pconstantfact_leaf4[.LOOKUP = (pconstantlookup_leaf4[.PREFIX = 2])]
pconstantcontext_stale = pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS, pconstantfact_stale)]
S_stale = S[.CONSTCONTEXT = (pconstantcontext_stale)]
$global_constant_lookup_valid(S_stale, preceivebirth.ORIGIN, pconstantfact_stale, S_stale.USERCONSTANTS)
$default_context_valid(S_stale, pconstantcontext_stale)
$constant_value_class_valid(S_stale, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S_stale))
~$parameter_multiple_facts(S_stale, preceivebirth, 1, preceiveorder, pconstantcontext_stale.FACTS)
~$parameter_default_transfer_valid(S_stale, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S_future.USERCONSTANTS = S.USERCONSTANTS /\ S_future.EVALBINDINGS = S.EVALBINDINGS
S_stale.USERCONSTANTS = S.USERCONSTANTS /\ S_stale.EVALBINDINGS = S.EVALBINDINGS
''')+causal.finish_checks(OUTPUTS['parameter-multiple-stable-prefix'],1)

CHECKS['parameter-multiple-partial-retry']=premises(r'''
ptbytes_function = $ptascii("MultipleRetry") ++ [92] ++ $ptascii("take")
S_first = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 1, 8000)
S_first.CURRENT = (pcallcontext_first)
$function_at($all_functions(S_first), pcallcontext_first.FUNCTION) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
porigin_first = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
porigin_second = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 4, PCFIELD 1])
$parameter_callable_cached_method(S_first, porigin_first) = eps
$parameter_callable_cached_method(S_first, porigin_second) = eps
S_second = $causal_test_seek($donor_test_step(S_first), ptbytes_function, 2, 1, 10000)
$global_test_output(S_second.EVENTS) = $ptascii("H1|")
$parameter_callable_cached_method(S_second, porigin_first) = (pmethoddesc_first)
$parameter_callable_cached_method(S_second, porigin_second) = eps
|S_second.USERCONSTANTS| = 3
S_retry = $causal_test_seek($donor_test_step(S_second), ptbytes_function, 2, 2, 16000)
$global_test_output(S_retry.EVENTS) = $ptascii("H1|H2|X|")
$parameter_receive_birth(S_retry, 1) = (preceivebirth_failed)
~preceivebirth_failed.ACTIVE
$parameter_receive_birth(S_retry, 2) = (preceivebirth_retry)
preceivebirth_retry.ACTIVE /\ preceivebirth_retry.PREFIX = 4
$parameter_callable_cached_method(S_retry, porigin_first) = (pmethoddesc_first)
$parameter_callable_cached_method(S_retry, porigin_second) = eps
$constant_callable_first(S_second.CONSTANTCLOSURES, porigin_first) = (pconstantclosure_first)
$constant_callable_first(S_retry.CONSTANTCLOSURES, porigin_first) = (pconstantclosure_first)
$parameter_receive_state_valid(S_retry) /\ $call_descriptors_valid(S_retry)
''')+bind_checks('MultipleRetry',2,'S_retry')+lookup_checks([(0,4),(2,4),(3,4),(5,4)],2)+premises(r'''
preceivebirth.PREFIX = 4 /\ |S.USERCONSTANTS| = 4
S.USERCONSTANTS = [puserconstant_global_first, puserconstant_global_second, puserconstant_local_first, puserconstant_local_second]
$parameter_receive_cut_at(puserconstant_local_first.RECEIVES, 1) = (preceivecut_first)
$parameter_receive_cut_at(puserconstant_local_second.RECEIVES, 1) = (preceivecut_second)
$parameter_receive_cut_at(puserconstant_local_first.RECEIVES, 2) = eps
$parameter_receive_cut_at(puserconstant_local_second.RECEIVES, 2) = eps
$parameter_receive_donor_source(S, puserconstant_local_first)
$parameter_receive_donor_source(S, puserconstant_local_second)
$parameter_callable_cached_method(S, porigin_first) = (pmethoddesc_first)
$parameter_callable_cached_method(S, porigin_second) = (pmethoddesc_second)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_fresh_first)), ENTRY (KINT 2) (DIRECT (POBJECT n_local_first)), ENTRY (KINT 3) (DIRECT (POBJECT n_local_second)), ENTRY (KINT 4) (DIRECT (POBJECT n_fresh_second)), ENTRY (KINT 5) (DIRECT (POBJECT n_local_second))]
n_fresh_first =/= pconstantclosure_first.OBJECT
$global_test_output(S.EVENTS) = $ptascii("H1|H2|X|H3|")
''')+causal.finish_checks(OUTPUTS['parameter-multiple-partial-retry'],2)

def deprecated_checks(namespace,preshadow):
    payload=17 if preshadow else 2048
    wrong=2048 if preshadow else 17
    checks=bind_checks(namespace)+lookup_checks([(0,1),(2,3 if preshadow else 2),(4,3)])
    checks+=premises(fr'''
preceivebirth.PREFIX = 1 /\ |S.USERCONSTANTS| = 3
porigin_trait = {leaf(1)}
porigin_deprecated = {leaf(3)}
preceiveorder.EFFECTS = [porigin_trait, porigin_deprecated]
$parameter_multiple_lookup_prefix(S, preceivebirth, 1, preceiveorder, porigin_deprecated) = ({3 if preshadow else 2})
$deprecated_constant_source(S, porigin_deprecated, 0) =/= eps
$constant_fact_at(pconstantcontext.FACTS, porigin_deprecated) = (pconstantfact_scalar)
pconstantfact_scalar.VALUE = (PINT {payload}) /\ pconstantfact_scalar.CLASS = PVSCALAR
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_global)), ENTRY (KINT 1) (DIRECT (POBJECT n_trait)), ENTRY (KINT 2) (DIRECT (POBJECT n_local)), ENTRY (KINT 3) (DIRECT (PINT {payload})), ENTRY (KINT 4) (DIRECT (POBJECT n_local))]
S.USERCONSTANTS = [puserconstant_global, puserconstant_local, puserconstant_scalar]
puserconstant_scalar.VALUE = PINT 17
$parameter_receive_cut_at(puserconstant_local.RECEIVES, 1) = (preceivecut_local)
$parameter_receive_cut_at(puserconstant_scalar.RECEIVES, 1) = (preceivecut_scalar)
$parameter_receive_frontier_site(preceivecut_local.FRONTIER) = (porigin_trait)
$parameter_receive_frontier_site(preceivecut_scalar.FRONTIER) = ({'porigin_trait' if preshadow else 'porigin_deprecated'})
$parameter_multiple_effect_value(S, preceivebirth, 1, preceiveorder, porigin_deprecated)
pconstantfact_wrong = pconstantfact_scalar[.VALUE = (PINT {wrong})]
pconstantcontext_wrong = pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS, pconstantfact_wrong)]
S_wrong = S[.CONSTCONTEXT = (pconstantcontext_wrong)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_global)), ENTRY (KINT 1) (DIRECT (POBJECT n_trait)), ENTRY (KINT 2) (DIRECT (POBJECT n_local)), ENTRY (KINT 3) (DIRECT (PINT {wrong})), ENTRY (KINT 4) (DIRECT (POBJECT n_local))]]
$constant_fact_value_valid(pconstantfact_wrong)
$default_context_valid(S_wrong, pconstantcontext_wrong)
$constant_value_class_valid(S_wrong, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S_wrong))
S_wrong.USERCONSTANTS = S.USERCONSTANTS /\ S_wrong.EVALBINDINGS = S.EVALBINDINGS
~$parameter_multiple_effect_value(S_wrong, preceivebirth, 1, preceiveorder, porigin_deprecated)
~$parameter_default_transfer_valid(S_wrong, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
''')
    if preshadow:
        checks+=premises(r'''
$deprecated_constant_source(S, porigin_deprecated, 3) = eps
preceivecut_local = preceivecut_scalar
|S.EVALBINDINGS| = 1
$global_test_output(S.EVENTS) = $ptascii("H1|")
''')
    else:
        checks+=premises(r'''
$deprecated_constant_source(S, porigin_deprecated, 2) =/= eps
pconstantfact_scalar.LOOKUP = eps
|S.EVALBINDINGS| = 2
$global_test_output(S.EVENTS) = $ptascii("H1|H2|")
''')
    return checks

CHECKS['parameter-multiple-deprecated-capture']=deprecated_checks('MultipleDeprecated',False)+causal.finish_checks(OUTPUTS['parameter-multiple-deprecated-capture'],1)
CHECKS['parameter-multiple-deprecated-preshadow']=deprecated_checks('MultiplePreshadow',True)+causal.finish_checks(OUTPUTS['parameter-multiple-deprecated-preshadow'],1)

CHECKS['parameter-multiple-named-hole']=bind_checks('ParameterGenerationMulti',named=True)+TWO_CUTS+lookup_checks([(0,2),(2,3),(3,3),(5,4)])+premises(r'''
pcallcontext.HOLES = [0] /\ pcallcontext.NAMED = eps
$lookup(S.ENV, $ptascii("tag")) = (n_tag)
S.STORE[n_tag] = DEFINED (PSTRING ($ptascii("named")))
''')+causal.finish_checks(OUTPUTS['parameter-multiple-named-hole'],1)

CHECKS['parameter-multiple-nested-cache']=premises(r'''
ptbytes_function = $ptascii("MultipleNested") ++ [92] ++ $ptascii("take")
S_first = $causal_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 1, 8000)
$parameter_receive_birth(S_first, 1) = (preceivebirth_first)
preceivebirth_first.ACTIVE /\ preceivebirth_first.PARENT = eps
S_inner_warning = $causal_test_seek($donor_test_step(S_first), ptbytes_function, 2, 2, 14000)
$parameter_receive_birth(S_inner_warning, 2) = (preceivebirth_inner)
preceivebirth_inner.ACTIVE /\ preceivebirth_inner.PREFIX = 2
preceivebirth_inner.PARENT = (1) /\ preceivebirth_inner.PARENTINDEX = (3)
preceivebirth_inner.PARENTEDGE = (preceiveedge)
$parameter_receive_source_valid(S_inner_warning, preceivebirth_inner)
$parameter_receive_state_valid(S_inner_warning) /\ $call_descriptors_valid(S_inner_warning)
S_inner = $causal_test_seek(S_inner_warning, ptbytes_function, 0, 2, 14000)
S_inner.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_inner*
$function_at($all_functions(S_inner), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S_inner.RESULT = KNOWN (PARRAY n_inner)
S_inner.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (POBJECT n_inner_left)), ENTRY (KINT 2) (DIRECT (POBJECT n_local)), ENTRY (KINT 3) (DIRECT (POBJECT n_inner_right)), ENTRY (KINT 4) (DIRECT (POBJECT n_local))]
porigin_left = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
porigin_right = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 3, PCFIELD 1])
$parameter_callable_cached_method(S_inner, porigin_left) =/= eps
$parameter_callable_cached_method(S_inner, porigin_right) =/= eps
S_inner.CONSTCONTEXT = (pconstantcontext_inner)
$constant_fact_at(pconstantcontext_inner.FACTS, pdefault.ORIGIN) = (pconstantfact_inner_root)
$parameter_default_transfer_valid(S_inner, pfunction, 0, PARRAY n_inner, pconstantfact_inner_root.CLASS)
$parameter_receive_frontier_site(preceiveedge.FRONTIER) = (porigin_left)
S_inner.CURRENT = (pcallcontext_inner)
S_wrong_parent = S_inner[.PARAMETERRECEIVES = [preceivebirth_first, preceivebirth_inner[.PARENTEDGE = (preceiveedge[.HANDLER = pcallcontext_inner.FUNCTION])]]]
~$parameter_receive_source_valid(S_wrong_parent, preceivebirth_inner[.PARENTEDGE = (preceiveedge[.HANDLER = pcallcontext_inner.FUNCTION])])
~$parameter_default_transfer_valid(S_wrong_parent, pfunction, 0, PARRAY n_inner, pconstantfact_inner_root.CLASS)
S_inner_bound = $donor_test_step(S_inner)
$parameter_receive_birth(S_inner_bound, 2) = (preceivebirth_inner_closed)
~preceivebirth_inner_closed.ACTIVE
$parameter_receive_birth(S_inner_bound, 1) = (preceivebirth_outer_live)
preceivebirth_outer_live.ACTIVE
''')+bind_checks('MultipleNested',1,'S_inner_bound')+lookup_checks([(0,1),(2,2),(4,2)])+premises(r'''
S.PARAMETERSEQ = 2 /\ preceivebirth.PREFIX = 1
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_global)), ENTRY (KINT 1) (DIRECT (POBJECT n_outer_left)), ENTRY (KINT 2) (DIRECT (POBJECT n_local)), ENTRY (KINT 3) (DIRECT (POBJECT n_outer_right)), ENTRY (KINT 4) (DIRECT (POBJECT n_local))]
n_inner_left =/= n_outer_left /\ n_inner_right =/= n_outer_right
S.USERCONSTANTS = [puserconstant_global, puserconstant_local]
$parameter_receive_cut_at(puserconstant_local.RECEIVES, 1) = (preceivecut)
$parameter_receive_frontier_site(preceivecut.FRONTIER) = (porigin_left)
$parameter_receive_cut_at(puserconstant_local.RECEIVES, 2) = eps
|S.EVALBINDINGS| = 1
$global_test_output(S.EVENTS) = $ptascii("H1|H2|H3|I:local:local:local|")
''')+causal.finish_checks(OUTPUTS['parameter-multiple-nested-cache'],3)

assert set(CHECKS)==set(SOURCES)==set(OUTPUTS)

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
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='parameter-multiple-frontiers-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        original=base.prepare;original_flags=base.RUNNER_FLAGS
        try:
            base.prepare=prepare
            base.RUNNER_FLAGS={name:['--sl'] for name in SOURCES}
            base.run(out)
        finally:
            base.prepare=original;base.RUNNER_FLAGS=original_flags
    print(out)

if __name__=='__main__':main()
