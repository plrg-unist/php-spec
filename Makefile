.PHONY: deps build schema test validate inventory test-semantics

deps:
	./scripts/build-deps.sh

build:
	./scripts/build-file-helper.sh
	./scripts/build-request-provider.sh
	./scripts/opam-exec.sh dune build

schema:
	.tools/php/bin/php -n scripts/node-inventory.php > spec/nodes.json
	python3 scripts/generate-schema.py
	python3 scripts/generate-occurrences.py
	python3 scripts/encoding-inventory.py

test: build
	.tools/php/bin/php -n -d extension=$(CURDIR)/.tools/php-file.so -d zend.multibyte=1 -d internal_encoding=UTF-8 tests/native-file.php
	python3 tests/validate_extraction.py
	python3 tests/malformed.py
	python3 tests/wire_negative.py
	python3 tests/eval_source_service.py
	python3 tests/include_source_service.py
	python3 tests/file_provider_protocol.py
	python3 tests/encoding_mutation.py
	python3 tests/source_context_metadata.py
	python3 tests/namespace_placement.py
	python3 tests/ternary_metadata.py
	python3 tests/destructuring_metadata.py
	python3 tests/foreach_targets.py
	python3 tests/list_line_metadata.py
	python3 tests/list_target_metadata.py
	python3 tests/callable_line_metadata.py
	python3 tests/pipe_parentheses.py
	python3 tests/switch_case_separator.py
	python3 tests/class_keyword_metadata.py
	python3 tests/method_keyword_metadata.py
	python3 tests/array_omission_metadata.py
	python3 tests/concat_line_metadata.py
	python3 tests/nullary_line_metadata.py
	python3 tests/clone_line_metadata.py
	python3 tests/phase_ledger.py
	python3 tests/parallel_validation_test.py
	python3 tests/validate.py --elaborate --lint-all
	python3 tests/validate.py --generated --output coverage/results-generated.jsonl
	python3 tests/validate.py --corpus --match stack_limit_013 --output coverage/results-deep.jsonl

validate: build
	python3 tests/parallel_validate.py --corpus --lint-all --output coverage/results-corpus.jsonl

inventory: build
	python3 tests/build_coverage.py
	python3 tests/grammar_coverage.py
	python3 scripts/grammar-mapping.py
	python3 scripts/scanner-mapping.py
	python3 scripts/encoding-spellings.py

test-semantics: build
	python3 tests/semantics/request_provider.py
	python3 tests/semantics/evidence.py
	python3 tests/semantics/source_occurrences.py
	python3 tests/semantics/source_context.py
	python3 tests/semantics/truth_compiler.py
	python3 tests/semantics/truth_expressions.py
	python3 tests/semantics/comparison_compiler.py
	python3 tests/semantics/comparison.py
	python3 tests/semantics/reference_wrappers.py
	python3 tests/semantics/write_fetch.py
	python3 tests/semantics/incdec.py
	python3 tests/semantics/incdec_compiler.py
	python3 tests/semantics/compound.py
	python3 tests/semantics/ordinary.py
	python3 tests/semantics/compound_compiler.py
	python3 tests/semantics/array_omissions.py
	python3 tests/semantics/array_unpack.py
	python3 tests/semantics/array_unpack_compiler.py
	python3 tests/semantics/destructuring.py
	python3 tests/semantics/destructuring_compiler.py
	python3 tests/semantics/globals_compiler.py
	python3 tests/semantics/magic_constants_compiler.py
	python3 tests/semantics/request_adapter.py
	python3 tests/semantics/request_environment.py
	python3 tests/semantics/request_environment_protocol.py
	python3 tests/semantics/request_environment_state.py
	python3 tests/semantics/isset_empty.py
	python3 tests/semantics/isset_empty_compiler.py
	python3 tests/semantics/function_compiler.py
	python3 tests/semantics/function_argument_compiler.py
	python3 tests/semantics/function_calls.py
	python3 tests/semantics/function_call_state.py
	python3 tests/semantics/function_call_protocol.py
	python3 tests/semantics/function_reference_compiler.py
	python3 tests/semantics/function_reference_send_compiler.py
	python3 tests/semantics/builtin_write_compiler.py
	python3 tests/semantics/function_references.py
	python3 tests/semantics/function_reference_state.py
	python3 tests/semantics/function_reference_protocol.py
	python3 tests/semantics/user_constant_compiler.py
	python3 tests/semantics/constant_class_compiler.py
	python3 tests/semantics/user_constants.py
	python3 tests/semantics/user_constant_protocol.py
	python3 tests/semantics/user_constant_context_protocol.py
	python3 tests/semantics/user_constant_branch_protocol.py
	python3 tests/semantics/user_constant_state.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/class_constant_cases.json
	python3 tests/semantics/class_constant_protocol.py
	python3 tests/semantics/constant_callable_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/deferred_static_default_cases.json
	python3 tests/semantics/deferred_static_default_protocol.py
	python3 tests/semantics/cold_static_reference_protocol.py
	python3 tests/semantics/cold_closure_static_protocol.py
	python3 tests/semantics/closure_call_creation_protocol.py
	python3 tests/semantics/default_parameter_compiler.py
	python3 tests/semantics/default_parameters.py
	python3 tests/semantics/default_parameter_protocol.py
	python3 tests/semantics/default_readiness_protocol.py
	python3 tests/semantics/default_parameter_state.py
	python3 tests/semantics/strict_declaration_compiler.py
	python3 tests/semantics/strict_declarations.py
	python3 tests/semantics/strict_declaration_protocol.py
	python3 tests/semantics/strict_declaration_state.py
	python3 tests/semantics/typed_function_compiler.py
	python3 tests/semantics/typed_functions.py
	python3 tests/semantics/typed_function_protocol.py
	python3 tests/semantics/typed_function_state.py
	python3 tests/semantics/callable_string.py
	python3 tests/semantics/callable_string_protocol.py
	python3 tests/semantics/array_callables.py
	python3 tests/semantics/array_callables_protocol.py
	python3 tests/semantics/class_method_strings.py
	python3 tests/semantics/class_method_strings_protocol.py
	python3 tests/semantics/error_handler_callables.py
	python3 tests/semantics/error_handler_callables_protocol.py
	python3 tests/semantics/exception_handlers.py
	python3 tests/semantics/exception_handler_state.py
	python3 tests/semantics/exception_handler_review.py
	python3 tests/semantics/exception_handler_state_review.py
	python3 tests/semantics/exception_handler_boundaries.py
	python3 tests/semantics/shutdown_functions.py
	python3 tests/semantics/shutdown_render_state.py
	python3 tests/semantics/shutdown_review.py
	python3 tests/semantics/shutdown_state_review.py
	python3 tests/semantics/exception_handler_static_default.py
	python3 tests/semantics/scoped_callables.py
	python3 tests/semantics/scoped_callables_protocol.py
	python3 tests/semantics/keyword_compound_callables.py
	python3 tests/semantics/keyword_compound_callables_protocol.py
	python3 tests/semantics/from_callable.py
	python3 tests/semantics/from_callable_protocol.py
	python3 tests/semantics/invoke_publication.py
	python3 tests/semantics/invoke_publication_protocol.py
	python3 tests/semantics/callable_string_ini.py
	python3 tests/semantics/callable_string_ini_protocol.py
	python3 tests/semantics/call_reference_compiler.py
	python3 tests/semantics/call_reference_acquisition.py
	python3 tests/semantics/call_reference_protocol.py
	python3 tests/semantics/call_reference_acquisition_state.py
	python3 tests/semantics/reference_return_compiler.py
	python3 tests/semantics/reference_returns.py
	python3 tests/semantics/reference_return_demand.py
	python3 tests/semantics/reference_return_protocol.py
	python3 tests/semantics/reference_return_state.py
	python3 tests/semantics/suppression_compiler.py
	python3 tests/semantics/suppression.py
	python3 tests/semantics/suppression_reporting.py
	python3 tests/semantics/error_suppression_protocol.py
	python3 tests/semantics/suppression_state.py
	python3 tests/semantics/variadic_compiler.py
	python3 tests/semantics/variadic.py
	python3 tests/semantics/variadic_protocol.py
	python3 tests/semantics/variadic_state.py
	python3 tests/semantics/named_compiler.py
	python3 tests/semantics/builtin_named_modes.py
	python3 tests/semantics/builtin_named_compiler.py
	python3 tests/semantics/named.py
	python3 tests/semantics/named_regression.py
	python3 tests/semantics/named_protocol.py
	python3 tests/semantics/named_state.py
	python3 tests/semantics/call_unpack_compiler.py
	python3 tests/semantics/call_unpack.py
	python3 tests/semantics/call_unpack_regression.py
	python3 tests/semantics/call_unpack_protocol.py
	python3 tests/semantics/call_unpack_state.py
	python3 tests/semantics/dynamic_call_compiler.py
	python3 tests/semantics/dynamic_call.py
	python3 tests/semantics/dynamic_call_regression.py
	python3 tests/semantics/dynamic_call_protocol.py
	python3 tests/semantics/dynamic_call_state.py
	python3 tests/semantics/function_static_compiler.py
	python3 tests/semantics/function_statics.py
	python3 tests/semantics/function_statics_regression.py
	python3 tests/semantics/function_statics_protocol.py
	python3 tests/semantics/function_statics_state.py
	python3 tests/semantics/main_static_compiler.py
	python3 tests/semantics/main_statics.py
	python3 tests/semantics/main_statics_regression.py
	python3 tests/semantics/main_statics_protocol.py
	python3 tests/semantics/main_statics_state.py
	python3 tests/semantics/closure_compiler.py
	python3 tests/semantics/closures.py
	python3 tests/semantics/closures_regression.py
	python3 tests/semantics/closures_protocol.py
	python3 tests/semantics/closures_state.py
	python3 tests/semantics/arrow_compiler.py
	python3 tests/semantics/arrows.py
	python3 tests/semantics/first_class_compiler.py
	python3 tests/semantics/first_class.py
	python3 tests/semantics/first_class_protocol.py
	python3 tests/semantics/pipe.py
	python3 tests/semantics/pipe_protocol.py
	python3 tests/semantics/switch_compiler.py
	python3 tests/semantics/switch_bool_compiler.py
	python3 tests/semantics/switch.py
	python3 tests/semantics/switch_protocol.py
	python3 tests/semantics/object_classes_catalogue.py
	python3 tests/semantics/object_classes.py
	python3 tests/semantics/object_classes_protocol.py
	python3 tests/semantics/goto_compiler.py
	python3 tests/semantics/goto.py --match runtime-
	python3 tests/semantics/goto_protocol.py
	python3 tests/semantics/stdclass.py
	python3 tests/semantics/stdclass_protocol.py
	python3 tests/semantics/noctor_compiler.py
	python3 tests/semantics/noctor_args.py
	python3 tests/semantics/noctor_args_protocol.py
	python3 tests/semantics/noctor_unpack_protocol.py
	python3 tests/semantics/inheritance_compiler.py
	python3 tests/semantics/inheritance.py
	python3 tests/semantics/inheritance_protocol.py
	python3 tests/semantics/property_compiler.py
	python3 tests/semantics/properties.py
	python3 tests/semantics/properties_task_protocol.py
	python3 tests/semantics/property_reference_compiler.py
	python3 tests/semantics/property_references.py
	python3 tests/semantics/property_reference_protocol.py
	python3 tests/semantics/property_reference_incdec_protocol.py
	python3 tests/semantics/reference_coercion_protocol.py
	python3 tests/semantics/reference_coercion_default_cache_protocol.py
	python3 tests/semantics/property_visibility.py
	python3 tests/semantics/property_visibility_compiler.py
	python3 tests/semantics/property_visibility_protocol.py
	python3 tests/semantics/property_visibility_scope_protocol.py
	python3 tests/semantics/property_private.py
	python3 tests/semantics/property_private_compiler.py
	python3 tests/semantics/property_private_protocol.py
	python3 tests/semantics/private_property_scope_protocol.py
	python3 tests/semantics/class_static_properties.py
	python3 tests/semantics/class_static_references.py
	python3 tests/semantics/class_static_merged_bridge.py
	python3 tests/semantics/class_static_closure_call_bridge.py
	python3 tests/semantics/class_static_stringable_chdir_bridge.py
	python3 tests/semantics/property_scalar_alias.py
	python3 tests/semantics/property_scalar_alias_protocol.py
	python3 tests/semantics/typed_static_string_assignment.py
	python3 tests/semantics/typed_static_string_protocol.py
	python3 tests/semantics/typed_static_callable.py
	python3 tests/semantics/typed_static_restore.py
	python3 tests/semantics/static_set_compiler.py
	python3 tests/semantics/static_set_access.py
	python3 tests/semantics/static_set_access_protocol.py
	python3 tests/semantics/user_string_parameters.py
	python3 tests/semantics/user_string_parameters_protocol.py
	python3 tests/semantics/variadic_string_parameters.py
	python3 tests/semantics/variadic_string_parameters_protocol.py
	python3 tests/semantics/default_constructor_sources.py
	python3 tests/semantics/default_constructor_protocol.py
	python3 tests/semantics/default_constructor_api_protocol.py
	python3 tests/semantics/internal_default_constructor_sources.py
	python3 tests/semantics/internal_default_constructor_protocol.py
	python3 tests/semantics/internal_default_reception_sources.py
	python3 tests/semantics/internal_default_reception_protocol.py --group owner
	python3 tests/semantics/internal_default_reception_protocol.py --group pure
	python3 tests/semantics/internal_default_reception_protocol.py --group builtin
	python3 tests/semantics/anonymous_default_new_sources.py
	python3 tests/semantics/anonymous_default_new_protocol.py --group owner
	python3 tests/semantics/anonymous_default_new_protocol.py --group recursive
	python3 tests/semantics/class_static_selector_variants_protocol.py
	python3 tests/semantics/class_static_selector_unwind_protocol.py
	python3 tests/semantics/class_static_reference_protocol.py
	python3 tests/semantics/class_static_reference_auth_protocol.py
	python3 tests/semantics/class_static_reference_conflict_protocol.py
	python3 tests/semantics/class_static_interface_protocol.py
	python3 tests/semantics/class_static_interface_failure_protocol.py
	python3 tests/semantics/nullsafe_compiler.py
	python3 tests/semantics/nullsafe_properties.py
	python3 tests/semantics/nullsafe_properties_protocol.py
	python3 tests/semantics/method_compiler.py
	python3 tests/semantics/method_runtime.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/compiler_publication_cases.json
	python3 tests/semantics/compiler_publication_protocol.py
	python3 tests/semantics/compiler_method_modifier_guards.py
	python3 tests/semantics/compiler_ini_publication_guards.py
	python3 tests/semantics/method_visibility_frontend.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/method_visibility_cases.json
	python3 tests/semantics/method_visibility_protocol.py
	python3 tests/semantics/method_wrapper_protocol.py
	python3 tests/semantics/match_compiler.py
	python3 tests/semantics/match_expressions.py
	python3 tests/semantics/match_protocol.py
	python3 tests/semantics/exit_compiler.py
	python3 tests/semantics/exit_expressions.py
	python3 tests/semantics/throwable_expressions.py
	python3 tests/semantics/throwable_compiler.py
	python3 tests/semantics/throwable_protocol.py
	python3 tests/semantics/throwable_accessors.py
	python3 tests/semantics/throwable_getter_protocol.py
	python3 tests/semantics/throwable_constructors.py
	python3 tests/semantics/throwable_constructor_protocol.py
	python3 tests/semantics/throwable_traces.py
	python3 tests/semantics/throwable_trace_protocol.py
	python3 tests/semantics/throwable_error_exception.py
	python3 tests/semantics/throwable_error_exception_protocol.py
	python3 tests/semantics/throwable_subclass_storage_protocol.py
	python3 tests/semantics/throwable_terminal_protocol.py
	python3 tests/semantics/throwable_subclass_callable_protocol.py
	python3 tests/semantics/throwable_subclasses.py
	python3 tests/semantics/exit_protocol.py
	python3 tests/semantics/exit_controls.py
	python3 tests/semantics/clone_compiler.py
	python3 tests/semantics/clone_expressions.py
	python3 tests/semantics/clone_protocol.py
	python3 tests/semantics/clone_controls.py
	python3 tests/semantics/get_class_intrinsic.py
	python3 tests/semantics/get_class_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/called_class_cases.json
	python3 tests/semantics/called_class_protocol.py
	python3 tests/semantics/called_class_controls.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/called_class_review_cases.json
	python3 tests/semantics/called_class_review_protocol.py
	python3 tests/semantics/called_class_review_boundaries.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_default_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_warning_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_abstract_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_capture_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_finally_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_direct_default_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_cold_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_ctor_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_interface_file_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_closure_cold_review_cases.json
	python3 tests/semantics/trait_method_review_protocol.py
	python3 tests/semantics/trait_method_default_review_protocol.py
	python3 tests/semantics/trait_method_ctor_review_protocol.py
	python3 tests/semantics/trait_method_cold_review_protocol.py
	python3 tests/semantics/trait_method_closure_cold_review_protocol.py
	python3 tests/semantics/eval_execution.py
	python3 tests/semantics/eval_protocol.py
	python3 tests/semantics/eval_class_scope_protocol.py
	python3 tests/semantics/eval_saved_protocol.py
	python3 tests/semantics/eval_finally_protocol.py
	python3 tests/semantics/eval_nested_trace_protocol.py
	python3 tests/semantics/eval_trace_protocol.py
	python3 tests/semantics/eval_adapter_protocol.py
	python3 tests/semantics/include_execution.py
	python3 tests/semantics/startup_ini.py
	python3 tests/semantics/startup_ini_protocol.py
	python3 tests/semantics/display_errors.py
	python3 tests/semantics/display_errors_protocol.py
	python3 tests/semantics/include_protocol.py
	python3 tests/semantics/include_mutable_execution.py
	python3 tests/semantics/include_mutable_protocol.py
	python3 tests/semantics/include_ini_prefix_protocol.py
	python3 tests/semantics/include_chdir_protocol.py
	python3 tests/semantics/include_chdir_pipe_protocol.py
	python3 tests/semantics/include_chdir_warning_protocol.py
	python3 tests/semantics/include_chdir_adapter_protocol.py
	python3 tests/semantics/include_saved_protocol.py
	python3 tests/semantics/include_adapter_protocol.py
	python3 tests/semantics/print_expressions.py
	python3 tests/semantics/print_compiler.py
	python3 tests/semantics/print_protocol.py
	python3 tests/semantics/print_controls.py
	python3 tests/semantics/arrows_regression.py
	python3 tests/semantics/arrows_protocol.py
	python3 tests/semantics/arrows_state.py
	python3 tests/semantics/function_scope_state.py
	python3 tests/semantics/coalesce_assignment.py
	python3 tests/semantics/coalesce_assignment_compiler.py
	python3 tests/semantics/quiet_access.py
	python3 tests/semantics/quiet_access_compiler.py
	python3 tests/semantics/foreach.py
	python3 tests/semantics/foreach_compiler.py
	python3 tests/semantics/foreach_source_compiler.py
	python3 tests/semantics/destructuring_mechanism.py
	python3 tests/semantics/validate.py
