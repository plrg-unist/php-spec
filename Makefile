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
	python3 tests/dollar_curly_metadata.py
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
	python3 tests/semantics/instance_default_template_protocol.py
	python3 tests/semantics/object_property_default_protocol.py
	python3 tests/semantics/property_callable_creation_protocol.py
	python3 tests/semantics/trait_constant_callable_protocol.py
	python3 tests/semantics/global_constant_callable_protocol.py
	python3 tests/semantics/global_constant_prebind_protocol.py
	python3 tests/semantics/global_constant_objects_protocol.py
	python3 tests/semantics/parameter_constant_callable_protocol.py
	python3 tests/semantics/parameter_callable_alias_protocol.py
	python3 tests/semantics/parameter_alias_causality_protocol.py
	python3 tests/semantics/parameter_multiple_frontier_protocol.py
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
	python3 tests/semantics/destructors.py
	python3 tests/semantics/destructor_request.py
	python3 tests/semantics/destructor_review.py
	python3 tests/semantics/destructor_state.py
	python3 tests/semantics/destructor_state_review.py
	python3 tests/semantics/destruction_prune_protocol.py
	python3 tests/semantics/eager_destructor_review.py
	python3 tests/semantics/eager_destructor_state_review.py
	python3 tests/semantics/eager_fatal_review.py
	python3 tests/semantics/eager_fatal_state_review.py
	python3 tests/semantics/eager_fatal_precision_state.py
	python3 tests/semantics/eager_fiber_state.py
	python3 tests/semantics/fiber_review.py
	python3 tests/semantics/fiber_state_review.py
	python3 tests/semantics/fiber_retirement_review.py
	python3 tests/semantics/fiber_ordinary_state.py
	python3 tests/semantics/fiber_ordinary_review.py
	python3 tests/semantics/fiber_protected_state.py
	python3 tests/semantics/fiber_protected_review.py
	python3 tests/semantics/fiber_core_state.py
	python3 tests/semantics/fiber_core_review.py
	python3 tests/semantics/fiber_core_integration_protocol.py
	python3 tests/semantics/fiber_core_file_review.py
	python3 tests/semantics/fiber_core_latest_sources.py
	python3 tests/semantics/fiber_callable_sources.py
	python3 tests/semantics/fiber_callable_state.py
	python3 tests/semantics/fiber_callable_review.py
	python3 tests/semantics/fiber_callable_current_review.py
	python3 tests/semantics/fiber_static_api_sources.py
	python3 tests/semantics/fiber_static_api_state.py
	python3 tests/semantics/fiber_static_api_review.py
	python3 tests/semantics/fiber_start_traversable_sources.py
	python3 tests/semantics/fiber_start_traversable_state.py
	python3 tests/semantics/fiber_start_traversable_review.py
	python3 tests/semantics/fiber_start_nan_sources.py
	python3 tests/semantics/fiber_start_nan_review.py
	python3 tests/semantics/weak_reference_sources.py
	python3 tests/semantics/weak_reference_state.py
	python3 tests/semantics/weak_reference_review.py
	python3 tests/semantics/weak_reference_state_review.py
	python3 tests/semantics/cycle_collection_sources.py --exclude-match collector-detached-throw-has-worker-and-real-resumer-traces --exclude-match collector-residual-dtor-public-resume-preparation-25 --exclude-match collector-residual-dtor-next-internal-fiber-pass-preparation-26 --exclude-match collector-residual-dtor-next-main-pass-preparation-27 --exclude-match collector-residual-internal-callback-suspends-and-detaches-preparation-28 --exclude-match collector-residual-internal-suspension-releases-last-cache-owner-preparation-29 --exclude-match collector-public-callback-resuspends-during-internal-takeover-preparation-30 --exclude-match collector-cached-public-reentry-during-different-main-pass-preparation-31
	python3 tests/semantics/cycle_collection_state.py
	python3 tests/semantics/cycle_collection_review.py --exclude-match collector-detached-pending-review-18 --exclude-match collector-detached-quiescent-throwing-fiber-prior-error-review-19 --exclude-match collector-active-interval-bound-core-throw-review-21 --exclude-match collector-active-public-cached-core-old-pending-new-throw-review-22 --exclude-match collector-active-public-cached-core-two-identities-compact-review-22 --exclude-match collector-public-postpass-core-old-pending-new-throw-review-23 --exclude-match collector-new-fiber-pass-keeps-parked-old-error-review-24 --exclude-match collector-internal-takeover-old-error-compact-preparation-24 --exclude-match collector-residual-dtor-next-internal-old-pending-review-preparation-26 --exclude-match collector-residual-dtor-main-old-pending-review-preparation-27 --exclude-match collector-residual-internal-suspension-separates-replacement-error-review-preparation-28 --exclude-match collector-residual-last-owner-failed-finally-prior-error-review-preparation-29 --exclude-match collector-public-internal-resuspension-separates-two-finally-errors-review-preparation-30 --exclude-match collector-cached-public-throw-during-different-main-pass-prior-identity-review-preparation-31
	python3 tests/semantics/cycle_collection_state_review.py --sl
	python3 tests/semantics/exception_handler_static_default.py
	python3 tests/semantics/scoped_callables.py
	python3 tests/semantics/scoped_callables_protocol.py
	python3 tests/semantics/keyword_compound_callables.py
	python3 tests/semantics/keyword_compound_callables_protocol.py
	python3 tests/semantics/callable_receives.py
	python3 tests/semantics/callable_receive_protocol.py
	python3 tests/semantics/from_callable.py
	python3 tests/semantics/from_callable_protocol.py
	python3 tests/semantics/closure_current_binding.py
	python3 tests/semantics/closure_current_binding_protocol.py
	python3 tests/semantics/closure_real_binding.py
	python3 tests/semantics/closure_real_binding_protocol.py
	python3 tests/semantics/closure_temporary_fake_call.py
	python3 tests/semantics/closure_temporary_fake_call_protocol.py
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
	python3 tests/semantics/object_cast_sources.py
	python3 tests/semantics/object_cast_protocol.py
	python3 tests/semantics/precision_sources.py
	python3 tests/semantics/precision_protocol.py
	python3 tests/semantics/suspended_precision_sources.py
	python3 tests/semantics/suspended_precision_protocol.py
	python3 tests/semantics/source_array_sources.py
	python3 tests/semantics/source_array_protocol.py
	python3 tests/semantics/source_undefined_sources.py
	python3 tests/semantics/source_undefined_protocol.py
	python3 tests/semantics/source_undefined_review.py
	python3 tests/semantics/source_stringable_sources.py
	python3 tests/semantics/source_stringable_protocol.py
	python3 tests/semantics/source_stringable_ordering_sources.py
	python3 tests/semantics/source_stringable_ordering_protocol.py
	python3 tests/semantics/source_stringable_helper_sources.py
	python3 tests/semantics/source_stringable_helper_protocol.py
	python3 tests/semantics/source_stringable_retirement_sources.py
	python3 tests/semantics/source_stringable_retirement_protocol.py
	python3 tests/semantics/source_stringable_retirement_sources.py --case first-echo
	python3 tests/semantics/source_stringable_retirement_sources.py --case first-assignment
	python3 tests/semantics/source_stringable_retirement_sources.py --case first-eval
	python3 tests/semantics/source_stringable_retirement_protocol.py --case entry
	python3 tests/semantics/source_stringable_retirement_sources.py --case generator-source
	python3 tests/semantics/source_stringable_retirement_sources.py --case expression-cycle-direct
	python3 tests/semantics/source_expression_emission_protocol.py --case collector
	python3 tests/semantics/source_stringable_retirement_protocol.py --case composition
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
	python3 tests/semantics/instance_set_access_sources.py
	python3 tests/semantics/instance_set_access_protocol.py --group permission
	python3 tests/semantics/instance_set_access_protocol.py --group interiors
	python3 tests/semantics/instance_set_access_protocol.py --group increment
	python3 tests/semantics/instance_set_access_protocol.py --group private
	python3 tests/semantics/instance_set_access_protocol.py --group alias
	python3 tests/semantics/instance_set_access_protocol.py --group cv
	python3 tests/semantics/instance_set_access_protocol.py --group recursive
	python3 tests/semantics/dynamic_property_warning_sources.py source
	python3 tests/semantics/dynamic_property_warning_sources.py boundary
	python3 tests/semantics/dynamic_property_warning_protocol.py --group reentry
	python3 tests/semantics/dynamic_property_warning_protocol.py --group retirement
	python3 tests/semantics/dynamic_property_warning_protocol.py --group pending
	python3 tests/semantics/dynamic_property_warning_protocol.py --group resurrection
	python3 tests/semantics/dynamic_property_warning_protocol.py --group pending-resurrection
	python3 tests/semantics/dynamic_property_warning_protocol.py --group temporary-cleanup
	python3 tests/semantics/dynamic_property_warning_protocol.py --group gc-protected
	python3 tests/semantics/dynamic_property_warning_protocol.py --group exit
	python3 tests/semantics/duplicate_property_reference_protocol.py --group physical
	python3 tests/semantics/duplicate_property_reference_protocol.py --group binding
	python3 tests/semantics/duplicate_property_reference_protocol.py --group pending-binding
	python3 tests/semantics/duplicate_property_reference_protocol.py --group binding-gc
	python3 tests/semantics/duplicate_property_reference_protocol.py --group container
	python3 tests/semantics/duplicate_property_reference_protocol.py --group container-throw
	python3 tests/semantics/duplicate_property_reference_protocol.py --group descendants
	python3 tests/semantics/duplicate_property_reference_protocol.py --group descendants-throw
	python3 tests/semantics/duplicate_property_reference_protocol.py --group descendants-guard
	python3 tests/semantics/duplicate_property_reference_protocol.py --group typed-slot
	python3 tests/semantics/duplicate_property_reference_protocol.py --group typed-slot-fiber
	python3 tests/semantics/duplicate_property_reference_protocol.py --group generator-typed-slot
	python3 tests/semantics/duplicate_property_reference_protocol.py --group generator-typed-slot-fiber
	python3 tests/semantics/duplicate_property_reference_protocol.py --group wrapper
	python3 tests/semantics/duplicate_property_reference_protocol.py --group wrapper-array
	python3 tests/semantics/instance_storage_pin_protocol.py --group typed
	python3 tests/semantics/instance_storage_pin_protocol.py --group generator
	python3 tests/semantics/instance_storage_pin_protocol.py --group fiber
	python3 tests/semantics/stdinstance_storage_pin_protocol.py --group table
	python3 tests/semantics/stdinstance_storage_pin_protocol.py --group shared
	python3 tests/semantics/stdinstance_storage_pin_protocol.py --group generator
	python3 tests/semantics/instance_future_slot_read_protocol.py --group scalar
	python3 tests/semantics/instance_future_slot_read_protocol.py --group alias
	python3 tests/semantics/instance_future_heap_read_protocol.py --group alias
	python3 tests/semantics/instance_future_heap_read_protocol.py --group array
	python3 tests/semantics/instance_future_initial_read_protocol.py --group inherited
	python3 tests/semantics/instance_future_initial_read_protocol.py --group pending
	python3 tests/semantics/instance_future_unset_read_protocol.py --group dynamic
	python3 tests/semantics/instance_future_unset_read_protocol.py --group pending
	python3 tests/semantics/instance_future_quiet_read_protocol.py --group borrowed
	python3 tests/semantics/instance_future_quiet_read_protocol.py --group coalesce
	python3 tests/semantics/property_undefined_warning_protocol.py --group borrowed
	python3 tests/semantics/property_undefined_warning_protocol.py --group owned
	python3 tests/semantics/property_undefined_warning_protocol.py --group pending
	python3 tests/semantics/property_reference_warning_protocol.py --group replacement
	python3 tests/semantics/property_reference_warning_protocol.py --group pending
	python3 tests/semantics/property_reference_warning_protocol.py --group stdclass
	python3 tests/semantics/generator_request_delegation_instance_sources.py --mode full
	python3 tests/semantics/generator_request_delegation_instance_protocol.py --mode check --sl
	python3 tests/semantics/duplicate_property_reference_protocol.py --group receiver-cleanup
	python3 tests/semantics/duplicate_property_reference_protocol.py --group notice-owner
	python3 tests/semantics/duplicate_property_reference_protocol.py --group scalar-warning
	python3 tests/semantics/readonly_lifecycle_sources.py --kind normal
	python3 tests/semantics/readonly_lifecycle_sources.py --kind compiler
	python3 tests/semantics/readonly_lifecycle_sources.py --kind composition
	python3 tests/semantics/readonly_lifecycle_protocol.py --group reentry
	python3 tests/semantics/readonly_lifecycle_protocol.py --group detached
	python3 tests/semantics/readonly_lifecycle_protocol.py --group recursive
	python3 tests/semantics/readonly_lifecycle_protocol.py --group affected-reference
	python3 tests/semantics/readonly_clone_sources.py --kind normal
	python3 tests/semantics/readonly_clone_sources.py --kind compiler
	python3 tests/semantics/readonly_clone_sources.py --kind exit
	python3 tests/semantics/readonly_clone_protocol.py --group window
	python3 tests/semantics/readonly_clone_protocol.py --group borrowed
	python3 tests/semantics/readonly_clone_protocol.py --group intrinsic
	python3 tests/semantics/readonly_clone_protocol.py --group temporary
	python3 tests/semantics/readonly_clone_protocol.py --group fiber
	python3 tests/semantics/readonly_clone_updates_sources.py --kind normal
	python3 tests/semantics/readonly_clone_updates_protocol.py --group window
	python3 tests/semantics/readonly_clone_updates_protocol.py --group abrupt
	python3 tests/semantics/readonly_clone_updates_protocol.py --group stringable_guards
	python3 tests/semantics/readonly_clone_updates_protocol.py --group stringable_continuation
	python3 tests/semantics/readonly_clone_updates_protocol.py --group mutable
	python3 tests/semantics/readonly_clone_updates_protocol.py --group fiber
	python3 tests/semantics/readonly_clone_updates_protocol.py --group inherited_throw_trace
	python3 tests/semantics/readonly_clone_updates_protocol.py --group inherited_throw_frontier
	python3 tests/semantics/readonly_clone_updates_protocol.py --group alias_this
	python3 tests/semantics/readonly_clone_updates_protocol.py --group named_this
	python3 tests/semantics/readonly_clone_producer_protocol.py --group cache --sl
	python3 tests/semantics/readonly_clone_producer_protocol.py --group revisions --sl
	python3 tests/semantics/readonly_clone_selection_sources.py
	python3 tests/semantics/readonly_clone_selection_protocol.py --group consumer-birth --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group computed-name-birth --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group reused-maker-birth --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group private-manual-birth-positive --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group shared-origin-positive --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group autoload-birth --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group keyword-shutdown-birth --sl
	python3 tests/semantics/readonly_clone_selection_protocol.py --group closer-window --sl
	python3 tests/semantics/user_string_parameters.py
	python3 tests/semantics/user_string_parameters_protocol.py
	python3 tests/semantics/variadic_string_parameters.py
	python3 tests/semantics/variadic_string_parameters_protocol.py
	python3 tests/semantics/default_constructor_sources.py
	python3 tests/semantics/default_constructor_protocol.py
	python3 tests/semantics/default_constructor_api_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_constructor_selection_cases.json
	python3 tests/semantics/trait_constructor_selection_protocol.py
	python3 tests/semantics/internal_default_constructor_sources.py
	python3 tests/semantics/internal_default_constructor_protocol.py
	python3 tests/semantics/internal_default_reception_sources.py
	python3 tests/semantics/internal_default_reception_protocol.py --group owner
	python3 tests/semantics/internal_default_reception_protocol.py --group pure
	python3 tests/semantics/internal_default_reception_protocol.py --group builtin
	python3 tests/semantics/anonymous_default_new_sources.py
	python3 tests/semantics/anonymous_default_new_protocol.py --group owner
	python3 tests/semantics/anonymous_default_new_protocol.py --group recursive
	python3 tests/semantics/ordinary_constructor_sources.py
	python3 tests/semantics/ordinary_constructor_protocol.py --group string
	python3 tests/semantics/ordinary_constructor_protocol.py --group warning
	python3 tests/semantics/ordinary_constructor_protocol.py --group recursive
	python3 tests/semantics/object_class_name_sources.py
	python3 tests/semantics/object_class_name_protocol.py --group temporary
	python3 tests/semantics/object_class_name_protocol.py --group returned
	python3 tests/semantics/object_class_name_protocol.py --group thrown
	python3 tests/semantics/dynamic_new_sources.py
	python3 tests/semantics/dynamic_new_protocol.py --group retired
	python3 tests/semantics/dynamic_new_protocol.py --group recursive
	python3 tests/semantics/dynamic_new_protocol.py --group contexts
	python3 tests/semantics/dynamic_new_protocol.py --group rebound
	python3 tests/semantics/dynamic_new_protocol.py --group cached
	python3 tests/semantics/named_keyword_new_sources.py
	python3 tests/semantics/named_keyword_new_protocol.py --group cold
	python3 tests/semantics/named_keyword_new_protocol.py --group recursive
	python3 tests/semantics/named_keyword_new_protocol.py --group eval
	python3 tests/semantics/named_keyword_new_protocol.py --group constant
	python3 tests/semantics/autoload_sources.py
	python3 tests/semantics/autoload_protocol.py --group method
	python3 tests/semantics/autoload_protocol.py --group compaction_cursor
	python3 tests/semantics/autoload_protocol.py --group compaction_finish
	python3 tests/semantics/autoload_protocol.py --group recursion
	python3 tests/semantics/autoload_protocol.py --group explicit
	python3 tests/semantics/autoload_protocol.py --group traces
	python3 tests/semantics/autoload_protocol.py --group reference
	python3 tests/semantics/autoload_protocol.py --group retirement
	python3 tests/semantics/default_new_autoload_sources.py
	python3 tests/semantics/default_new_autoload_protocol.py --group lookup
	python3 tests/semantics/default_new_autoload_protocol.py --group recursive
	python3 tests/semantics/default_new_autoload_protocol.py --group retirement
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
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/missing_constructor_cases.json
	python3 tests/semantics/missing_constructor_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/constructor_promotion_cases.json
	python3 tests/semantics/constructor_promotion_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/constructor_promotion_override_cases.json
	python3 tests/semantics/constructor_promotion_override_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/compiler_publication_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/compiler_composed_retry_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/assertion_cases.json
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
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_collision_error_review_cases.json
	python3 tests/semantics/method_runtime.py --match property-error-keeps --catalogue tests/semantics/trait_data_collision_error_function_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_collision_held_primary_review_cases.json
	python3 tests/semantics/trait_collision_error_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_collision_cycle_review_cases.json
	python3 tests/semantics/trait_collision_cycle_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_cache_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_cache_review_cases.json
	python3 tests/semantics/trait_failed_cache_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_cache_error_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_cache_requestfatal_review_cases.json
	python3 tests/semantics/trait_failed_cache_error_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_trait_cache_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_trait_priority_review_cases.json
	python3 tests/semantics/trait_failed_trait_cache_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_public_object_dependency_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_public_object_foreign_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_public_object_dim_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_object_cache_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_object_error_review_cases.json
	python3 tests/semantics/trait_public_object_review_protocol.py
	python3 tests/semantics/trait_failed_object_cache_review_protocol.py
	python3 tests/semantics/trait_public_object_array_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_public_object_initializer_review_cases.json
	python3 tests/semantics/trait_public_object_initializer_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_public_object_initializer_file_review_cases.json
	python3 tests/semantics/trait_public_object_demand_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_unpublished_real_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_unpublished_real_review_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_unpublished_real_parent_cases.json
	python3 tests/semantics/trait_unpublished_real_protocol.py
	python3 tests/semantics/trait_unpublished_real_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_real_cases.json
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_failed_real_review_cases.json
	python3 tests/semantics/trait_failed_real_protocol.py
	python3 tests/semantics/trait_failed_real_review_protocol.py
	python3 tests/semantics/trait_failed_real_crossfile_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_unpublished_fcc_receipt_cases.json
	python3 tests/semantics/trait_unpublished_fcc_retired_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_data_unpublished_fcc_adaptation_cases.json
	python3 tests/semantics/trait_unpublished_fcc_adaptation_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_failed_name_cases.json
	python3 tests/semantics/trait_failed_name_protocol.py
	python3 tests/semantics/trait_failed_name_review_protocol.py
	python3 tests/semantics/trait_failed_name_early_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_real_constructor_interaction_cases.json
	python3 tests/semantics/trait_real_constructor_interaction_protocol.py
	python3 tests/semantics/eval_execution.py
	python3 tests/semantics/eval_protocol.py
	python3 tests/semantics/eval_class_scope_protocol.py
	python3 tests/semantics/eval_saved_protocol.py
	python3 tests/semantics/eval_finally_protocol.py
	python3 tests/semantics/eval_nested_trace_protocol.py
	python3 tests/semantics/eval_trace_protocol.py
	python3 tests/semantics/eval_adapter_protocol.py
	python3 tests/semantics/include_execution.py
	python3 tests/semantics/file_operand_sources.py
	python3 tests/semantics/file_operand_protocol.py
	python3 tests/semantics/interpolation_sources.py
	python3 tests/semantics/interpolation_protocol.py
	python3 tests/semantics/dollar_curly_sources.py
	python3 tests/semantics/dollar_curly_protocol.py
	python3 tests/semantics/startup_ini.py
	python3 tests/semantics/startup_ini_protocol.py
	python3 tests/semantics/display_errors.py
	python3 tests/semantics/display_errors_protocol.py
	python3 tests/semantics/include_protocol.py
	python3 tests/semantics/include_mutable_execution.py
	python3 tests/semantics/include_mutable_protocol.py
	python3 tests/semantics/include_ini_prefix_protocol.py
	python3 tests/semantics/include_chdir_protocol.py
	python3 tests/semantics/fiber_chdir_scope_protocol.py
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
	python3 tests/semantics/user_iterator.py
	python3 tests/semantics/user_iterator_protocol.py
	python3 tests/semantics/generator_effects_review.py
	python3 tests/semantics/generator_effects_review_protocol.py
	python3 tests/semantics/generator_delegation_review.py
	python3 tests/semantics/generator_delegation_protocol.py --mode check --sl
	python3 tests/semantics/generator_force_close_review.py --mode full
	python3 tests/semantics/generator_force_close_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_fresh_sources.py --mode full
	python3 tests/semantics/generator_request_fresh_peer_sources.py --mode full
	python3 tests/semantics/generator_storage_order_sources.py --mode full
	python3 tests/semantics/generator_request_fresh_protocol.py --mode check --sl
	python3 tests/semantics/generator_fresh_typed_slot_join_sources.py --mode full
	python3 tests/semantics/generator_fresh_typed_slot_join_protocol.py --mode check --sl
	python3 tests/semantics/generator_storage_order_protocol.py --mode check --sl
	python3 tests/semantics/generator_storage_pin_sources.py --mode full
	python3 tests/semantics/generator_storage_pin_peer_sources.py --mode full
	python3 tests/semantics/generator_storage_pin_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_delegation_sources.py --mode full
	python3 tests/semantics/generator_request_delegation_peer_sources.py --mode full
	python3 tests/semantics/generator_request_delegation_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_abrupt_sources.py --mode full
	python3 tests/semantics/generator_request_abrupt_peer_sources.py --mode full
	python3 tests/semantics/generator_request_abrupt_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_child_storage_peer_sources.py --mode full
	python3 tests/semantics/generator_request_child_storage_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_render_abrupt_peer_sources.py --mode full
	python3 tests/semantics/generator_request_render_abrupt_sources.py --mode full
	python3 tests/semantics/generator_request_render_abrupt_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_render_handler_peer_sources.py --mode full
	python3 tests/semantics/generator_request_render_handler_sources.py --mode full
	python3 tests/semantics/generator_request_render_handler_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_render_handler_throw_peer_sources.py --mode full
	python3 tests/semantics/generator_request_render_handler_throw_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_render_warning_throw_sources.py --mode full
	python3 tests/semantics/generator_request_render_warning_throw_protocol.py --mode check --sl
	python3 tests/semantics/generator_fiber_close_prepare.py --mode full
	python3 tests/semantics/generator_fiber_close_review.py --mode full
	python3 tests/semantics/generator_fiber_close_protocol.py --mode check --sl
	python3 tests/semantics/generator_fiber_close_review_protocol.py --sl
	python3 tests/semantics/generator_integration_review.py --mode full
	python3 tests/semantics/generator_eager_close_review_protocol.py --mode check --sl
	python3 tests/semantics/arrow_generator_prepare.py --mode full
	python3 tests/semantics/arrow_generator_review.py --mode full
	python3 tests/semantics/arrow_generator_protocol.py --mode check --sl
	python3 tests/semantics/arrow_generator_review_protocol.py --mode check --sl
	python3 tests/semantics/arrow_generator_warning_review_protocol.py --mode check --sl
	python3 tests/semantics/arrow_generator_globals_role_review_protocol.py --mode check --sl
	python3 tests/semantics/arrow_generator_integration.py --mode full
	python3 tests/semantics/arrow_generator_integration_protocol.py --mode check --sl
	python3 tests/semantics/arrow_generator_cleanup_protocol.py --mode check --sl
	python3 tests/semantics/yield_key_warning_prepare.py --mode full
	python3 tests/semantics/yield_key_warning_review.py --mode full
	python3 tests/semantics/yield_key_warning_protocol.py --mode check --sl
	python3 tests/semantics/yield_key_release_protocol.py --mode check --sl
	python3 tests/semantics/yield_key_identity_review.py --mode full
	python3 tests/semantics/yield_key_identity_protocol.py --mode check --sl
	python3 tests/semantics/iterator_declaration_notices.py
	python3 tests/semantics/eval_declaration_notices_protocol.py
	python3 tests/semantics/runtime_formatter_protocol.py
	python3 tests/semantics/destructuring_mechanism.py
	python3 tests/semantics/validate.py
