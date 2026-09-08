#!/usr/bin/env python3
"""Reviewed Zend nonterminal to checked syntax/field mapping; fail on additions."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GROUPS = [
    ("$accept start top_statement_list top_statement attributed_top_statement", ["program", "statement"]),
    ("inner_statement_list inner_statement statement attributed_statement", ["statement"]),
    ("reserved_non_modifiers semi_reserved identifier function_name member_name property_name", ["Identifier", "VarLikeIdentifier"]),
    ("namespace_declaration_name namespace_name legacy_namespace_name name class_name", ["name"]),
    ("ampersand is_reference is_variadic returns_ref", ["Param.byRef", "Param.variadic", "Expr_Closure.byRef", "Stmt_Function.byRef", "Stmt_ClassMethod.byRef", "Expr_ArrowFunction.byRef", "PropertyHook.byRef", "ClosureUse.byRef", "ArrayItem.byRef", "Stmt_Foreach.byRef", "Expr_AssignRef"]),
    ("attribute_decl attribute_group attribute attributes", ["Attribute", "AttributeGroup"]),
    ("use_type group_use_declaration mixed_group_use_declaration inline_use_declarations unprefixed_use_declarations use_declarations inline_use_declaration unprefixed_use_declaration use_declaration", ["Stmt_Use", "Stmt_GroupUse", "UseItem"]),
    ("possible_comma", ["ordered-list separator; spelling normalized"]),
    ("const_list", ["Stmt_Declare.declares", "DeclareItem"]),
    ("catch_list catch_name_list optional_variable", ["Stmt_Catch.types", "Stmt_Catch.var", "Stmt_TryCatch.catches"]),
    ("finally_statement", ["Stmt_TryCatch.finally", "Stmt_Finally"]),
    ("unset_variables unset_variable", ["Stmt_Unset.vars"]),
    ("function_declaration_statement", ["Stmt_Function"]),
    ("class_declaration_statement class_modifiers anonymous_class_modifiers anonymous_class_modifiers_optional class_modifier", ["Stmt_Class.flags", "Stmt_Class"]),
    ("trait_declaration_statement", ["Stmt_Trait"]),
    ("interface_declaration_statement interface_extends_list", ["Stmt_Interface"]),
    ("enum_declaration_statement enum_backing_type enum_case enum_case_expr", ["Stmt_Enum.scalarType", "Stmt_EnumCase.expr"]),
    ("extends_from implements_list", ["Stmt_Class.extends", "Stmt_Class.implements", "Stmt_Enum.implements"]),
    ("foreach_variable for_statement foreach_statement", ["Stmt_For", "Stmt_Foreach"]),
    ("declare_statement", ["Stmt_Declare.stmts"]),
    ("switch_case_list case_list", ["Stmt_Switch.cases", "Stmt_Case"]),
    ("match match_arm_list non_empty_match_arm_list match_arm match_arm_cond_list", ["Expr_Match", "MatchArm"]),
    ("while_statement", ["Stmt_While", "Stmt_Do"]),
    ("if_stmt_without_else if_stmt alt_if_stmt_without_else alt_if_stmt", ["Stmt_If", "Stmt_ElseIf", "Stmt_Else"]),
    ("parameter_list non_empty_parameter_list attributed_parameter optional_cpp_modifiers parameter optional_parameter_list", ["Param"]),
    ("optional_type_without_static type_expr type union_type_element union_type intersection_type type_expr_without_static type_without_static union_type_without_static_element union_type_without_static intersection_type_without_static return_type", ["Identifier", "name", "NullableType", "UnionType", "IntersectionType"]),
    ("argument_list non_empty_argument_list clone_argument_list non_empty_clone_argument_list argument_no_expr argument", ["Arg", "VariadicPlaceholder"]),
    ("global_var_list global_var", ["Stmt_Global.vars"]),
    ("static_var_list static_var", ["Stmt_Static.vars", "StaticVar"]),
    ("class_statement_list attributed_class_statement class_statement", ["Stmt_Class.stmts", "Stmt_ClassMethod", "Stmt_Property", "Stmt_ClassConst", "Stmt_TraitUse"]),
    ("class_name_list trait_adaptations trait_adaptation_list trait_adaptation trait_precedence trait_alias trait_method_reference absolute_trait_method_reference", ["Stmt_TraitUse", "Stmt_TraitUseAdaptation_Precedence", "Stmt_TraitUseAdaptation_Alias"]),
    ("method_body", ["Stmt_ClassMethod.stmts"]),
    ("property_modifiers method_modifiers class_const_modifiers non_empty_member_modifiers member_modifier", ["Stmt_Property.flags", "Stmt_ClassMethod.flags", "Stmt_ClassConst.flags"]),
    ("property_list property hooked_property", ["Stmt_Property", "PropertyItem"]),
    ("property_hook_list optional_property_hook_list property_hook_modifiers property_hook property_hook_body", ["PropertyHook", "Stmt_Property.hooks"]),
    ("class_const_list class_const_decl const_decl", ["Const", "Stmt_Const", "Stmt_ClassConst"]),
    ("echo_expr_list echo_expr", ["Stmt_Echo.exprs"]),
    ("for_cond_exprs for_exprs non_empty_for_exprs", ["Stmt_For.init", "Stmt_For.cond", "Stmt_For.loop"]),
    ("anonymous_class", ["Stmt_Class", "Expr_New"]),
    ("new_dereferenceable new_non_dereferenceable", ["Expr_New"]),
    ("expr", ["expression"]),
    ("inline_function fn function", ["Expr_Closure", "Expr_ArrowFunction"]),
    ("backup_doc_comment backup_fn_flags backup_lex_pos", ["metadata", "Expr_Closure.static", "Expr_ArrowFunction.static"]),
    ("lexical_vars lexical_var_list lexical_var", ["ClosureUse", "Expr_Closure.uses"]),
    ("function_call", ["Expr_FuncCall", "Expr_StaticCall"]),
    ("class_name_reference variable_class_name", ["name", "expression"]),
    ("backticks_expr", ["Expr_ShellExec.parts"]),
    ("ctor_arguments", ["Expr_New.args", "Arg"]),
    ("dereferenceable_scalar scalar constant", ["Scalar_Int", "Scalar_Float", "Scalar_String", "Scalar_InterpolatedString", "Expr_ConstFetch", "expression"]),
    ("class_constant", ["Expr_ClassConstFetch"]),
    ("optional_expr", ["Stmt_Return.expr", "Stmt_Break.num", "Stmt_Continue.num"]),
    ("fully_dereferenceable array_object_dereferenceable callable_expr callable_variable variable", ["Expr_Variable", "Expr_ArrayDimFetch", "Expr_PropertyFetch", "Expr_NullsafePropertyFetch", "Expr_StaticPropertyFetch", "Expr_MethodCall", "Expr_NullsafeMethodCall", "Expr_StaticCall", "Expr_FuncCall", "Expr_New", "expression"]),
    ("simple_variable", ["Expr_Variable.name"]),
    ("static_member", ["Expr_StaticPropertyFetch"]),
    ("new_variable", ["Expr_Variable", "Expr_ArrayDimFetch", "Expr_PropertyFetch", "Expr_StaticPropertyFetch"]),
    ("array_pair_list possible_array_pair non_empty_array_pair_list array_pair", ["Expr_Array.items", "Expr_List.items", "ArrayItem"]),
    ("encaps_list encaps_var encaps_var_offset", ["Scalar_InterpolatedString.parts", "InterpolatedStringPart", "Expr_Variable", "Expr_ArrayDimFetch", "Expr_PropertyFetch"]),
    ("internal_functions_in_yacc isset_variables isset_variable", ["Expr_Isset", "Expr_Empty", "Expr_Eval"]),
]

def main():
    grammar = json.loads((ROOT / 'coverage/grammar.json').read_text())
    schema = json.loads((ROOT / 'spec/schema.json').read_text())
    witnesses = json.loads((ROOT / 'coverage/results-targeted.summary.json').read_text())['nodes']
    mapping = {lhs: targets for names, targets in GROUPS for lhs in names.split()}
    for targets in mapping.values():
        for target in targets:
            if '.' in target:
                tag, field = target.split('.')
                assert field in {item['name'] for item in schema['nodes'][tag]['fields']}, target
            elif target not in {'program', 'statement', 'expression', 'name', 'metadata', 'ordered-list separator; spelling normalized'}:
                assert target in schema['nodes'], target
    productions = []
    for rule in grammar['productions']:
        lhs = rule['lhs']
        parents = [parent for parent in grammar['productions'] if lhs in parent['rhs']] if lhs.startswith(('@', '$@')) else []
        targets = sorted({target for parent in parents for target in mapping[parent['lhs']]}) if parents else mapping[lhs]
        productions.append({'rule': rule['rule'], 'lhs': lhs, 'rhs': rule['rhs'], 'targets': targets,
                            'source_line': rule.get('line'), 'enclosing_rules': [parent['rule'] for parent in parents], 'witnesses': rule['witnesses'], 'status': rule['status']})
    nodes = {tag: {'constructor': node['constructor'], 'declaration': node['source'],
                   'fields': {field['name']: field['domain'] for field in node['fields']},
                   'witnesses': witnesses.get(tag, [])} for tag, node in schema['nodes'].items()}
    assert all(node['witnesses'] for node in nodes.values()), 'Unwitnessed formal constructor'
    artifact = {'method': 'Reviewed nonterminal/field mapping; every alternative retains its own source trace. Category targets denote the explicit closed formal variants, not opaque nodes.',
                'implementation': {'grammar': 'vendor/php-parser-source/grammar/php.y', 'parser': 'vendor/php-parser/lib/PhpParser/Parser/Php8.php',
                    'formal_domains': 'spec/php.watsup', 'typed_field_contracts': 'spec/schema.json', 'conversion': 'adapter/main.ml'},
                'productions': productions, 'constructors': nodes}
    (ROOT / 'coverage/grammar-mapping.json').write_text(json.dumps(artifact, indent=2) + '\n')
    print(json.dumps({'mapped_productions': len(productions), 'witnessed_constructors': len(nodes)}))

if __name__ == '__main__':
    main()
