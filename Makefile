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
	python3 tests/rejected_header_service_review.py --output "$$(mktemp -d /tmp/php-spec-rejected-headers.XXXXXXXX)/service"
	python3 tests/lexical_header_service_review.py --output "$$(mktemp -d /tmp/php-spec-lexical-headers.XXXXXXXX)/service"
	python3 tests/rejected_eval_lexer_review.py --output "$$(mktemp -d /tmp/php-spec-rejected-lexer.XXXXXXXX)/service"
	python3 tests/rejected_namespace_service_review.py --output "$$(mktemp -d /tmp/php-spec-rejected-namespace.XXXXXXXX)/service"
	python3 tests/rejected_static_service_review.py --output "$$(mktemp -d /tmp/php-spec-rejected-static.XXXXXXXX)/service"
	python3 tests/rejected_method_modifier_service_review.py --output "$$(mktemp -d /tmp/php-spec-method-modifiers.XXXXXXXX)/service"
	python3 tests/rejected_constant_modifier_service_review.py --output "$$(mktemp -d /tmp/php-spec-constant-modifiers.XXXXXXXX)/service"
	python3 tests/rejected_trait_alias_modifier_service_review.py --output "$$(mktemp -d /tmp/php-spec-trait-alias-modifiers.XXXXXXXX)/service"
	python3 tests/rejected_property_hook_static_service_review.py --output "$$(mktemp -d /tmp/php-spec-property-hook-static.XXXXXXXX)/service"
	python3 tests/rejected_constant_attribute_service_review.py --output "$$(mktemp -d /tmp/php-spec-constant-attributes.XXXXXXXX)/service"
	python3 tests/rejected_anonymous_class_modifier_service_review.py --output "$$(mktemp -d /tmp/php-spec-anonymous-class-modifiers.XXXXXXXX)/service"
	python3 tests/file_provider_protocol.py
	python3 tests/encoding_mutation.py
	python3 tests/source_context_metadata.py
	python3 tests/declare_header_metadata_review.py
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
	python3 tests/property_hook_parameter_metadata.py --output "$$(mktemp -d /tmp/php-spec-hook-parameters.XXXXXXXX)/syntax"
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
	./scripts/opam-exec.sh dune build --root tests/semantics -j 1 numeric_runner.exe
	@out="$$(mktemp -d .tools/startup-float-constants-XXXXXX)" && \
	  python3 -B tests/semantics/startup_float_constants_sources.py --output "$$out/source" && \
	  python3 -B tests/semantics/startup_float_constants_compiler.py --sl --native-baseline "$$out/source" --output "$$out/compiler" && \
	  python3 -B tests/semantics/startup_float_constants_review.py --output "$$out/review"
	@out="$$(mktemp -d .tools/startup-version-constants-XXXXXX)" && \
	  python3 -B tests/semantics/startup_version_constants_sources.py --output "$$out/source" && \
	  python3 -B tests/semantics/startup_version_constants_compiler.py --sl --native-baseline "$$out/source" --output "$$out/compiler" && \
	  python3 -B tests/semantics/startup_version_constants_review.py --output "$$out/review"
	@out="$$(mktemp -d .tools/startup-bool-constants-XXXXXX)" && \
	  python3 -B tests/semantics/startup_bool_constants_sources.py --output "$$out/source" && \
	  python3 -B tests/semantics/startup_bool_constants_compiler.py --sl --native-baseline "$$out/source" --output "$$out/compiler" && \
	  python3 -B tests/semantics/startup_bool_constants_review.py --output "$$out/review"
	@out="$$(mktemp -d .tools/startup-upload-constants-XXXXXX)" && \
	  python3 -B tests/semantics/startup_upload_constants_sources.py --output "$$out/source" && \
	  python3 -B tests/semantics/startup_upload_constants_compiler.py --sl --native-baseline "$$out/source" --output "$$out/compiler" && \
	  python3 -B tests/semantics/startup_upload_constants_review.py --output "$$out/review"
	@out="$$(mktemp -d .tools/startup-zend-constants-XXXXXX)" && \
	  python3 -B tests/semantics/startup_zend_constants_sources.py --output "$$out/source" && \
	  python3 -B tests/semantics/startup_zend_constants_compiler.py --sl --native-baseline "$$out/source" --output "$$out/compiler" && \
	  python3 -B tests/semantics/startup_zend_constants_review.py --output "$$out/review"
	@out="$$(mktemp -d .tools/startup-release-string-constants-XXXXXX)" && \
	  python3 -B tests/semantics/startup_release_string_constants_sources.py --output "$$out/source" && \
	  python3 -B tests/semantics/startup_release_string_constants_review_state.py --sl --native-baseline "$$out/source" --output "$$out/compiler" && \
	  python3 -B tests/semantics/startup_release_string_constants_review.py --output "$$out/review"
	python3 tests/semantics/float_round_overflow_fastpath.py
	python3 tests/semantics/compiler_lookup_tails.py
	python3 tests/semantics/property_hook_parameter_list_sources.py --output "$$(mktemp -d /tmp/php-spec-hook-parameters.XXXXXXXX)/source"
	python3 tests/semantics/property_hook_header_presence_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-hook-parameters.XXXXXXXX)/origin"
	python3 -B tests/semantics/arrayaccess_typed_reference_get_run.py --output "$$(mktemp -d .tools/aa-typed-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_typed_reference_get_protocol.py --output "$$(mktemp -d .tools/aa-typed-state-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_scalar_reference_get_run.py --output "$$(mktemp -d .tools/aa-scalar-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_scalar_reference_get_protocol.py --output "$$(mktemp -d .tools/aa-scalar-state-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_scalar_reference_callbacks_run.py --output "$$(mktemp -d .tools/aa-scalar-callback-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_scalar_reference_callbacks_protocol.py --output "$$(mktemp -d .tools/aa-scalar-callback-state-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_void_reference_callbacks_run.py --output "$$(mktemp -d .tools/aa-void-callback-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_void_reference_callbacks_protocol.py --output "$$(mktemp -d .tools/aa-void-callback-state-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_never_reference_callbacks_run.py --output "$$(mktemp -d .tools/aa-never-callback-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_never_reference_callbacks_protocol.py --output "$$(mktemp -d .tools/aa-never-callback-state-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_void_result_callbacks_run.py --output "$$(mktemp -d .tools/aa-void-result-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_void_result_callbacks_protocol.py --output "$$(mktemp -d .tools/aa-void-result-state-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_string_reference_get_run.py --output "$$(mktemp -d .tools/aa-string-reference-get-source-XXXXXX)/run"
	python3 -B tests/semantics/arrayaccess_string_reference_get_protocol.py --output "$$(mktemp -d .tools/aa-string-reference-get-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_undefined_cv_run.py --output "$$(mktemp -d .tools/string-undefined-cv-source-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_undefined_cv_protocol.py --output "$$(mktemp -d .tools/string-undefined-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_string_cv_protocol.py --output "$$(mktemp -d .tools/string-current-string-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_request_cv_protocol.py --output "$$(mktemp -d .tools/string-current-request-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_request_cv_protocol.py --peer --output "$$(mktemp -d .tools/string-current-request-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --output "$$(mktemp -d .tools/string-current-marked-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --peer --output "$$(mktemp -d .tools/string-current-marked-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --strings --output "$$(mktemp -d .tools/string-current-marked-string-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --strings --peer --output "$$(mktemp -d .tools/string-current-marked-string-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --arrays --output "$$(mktemp -d .tools/string-current-marked-array-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --arrays --peer --output "$$(mktemp -d .tools/string-current-marked-array-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --variable-base --output "$$(mktemp -d .tools/string-variable-base-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --variable-base --peer --output "$$(mktemp -d .tools/string-variable-base-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --undefined-throw --output "$$(mktemp -d .tools/string-undefined-throw-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --undefined-throw --peer --output "$$(mktemp -d .tools/string-undefined-throw-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --variable-throw --output "$$(mktemp -d .tools/string-variable-throw-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --variable-throw --peer --output "$$(mktemp -d .tools/string-variable-throw-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-base --output "$$(mktemp -d .tools/string-request-base-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-base --peer --output "$$(mktemp -d .tools/string-request-base-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-throw --output "$$(mktemp -d .tools/string-request-throw-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-throw --peer --output "$$(mktemp -d .tools/string-request-throw-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release --output "$$(mktemp -d .tools/string-request-release-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release --peer --output "$$(mktemp -d .tools/string-request-release-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-registered --output "$$(mktemp -d .tools/string-request-release-registered-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-registered --peer --output "$$(mktemp -d .tools/string-request-release-registered-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-prior --output "$$(mktemp -d .tools/string-request-release-prior-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-prior --peer --output "$$(mktemp -d .tools/string-request-release-prior-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-distinct --output "$$(mktemp -d .tools/string-request-release-distinct-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-distinct --peer --output "$$(mktemp -d .tools/string-request-release-distinct-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-key --output "$$(mktemp -d .tools/string-request-release-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-key --peer --output "$$(mktemp -d .tools/string-request-release-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-callback --output "$$(mktemp -d .tools/string-request-release-callback-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-release-callback --peer --output "$$(mktemp -d .tools/string-request-release-callback-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-owner --output "$$(mktemp -d .tools/string-request-callback-owner-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-owner --peer --output "$$(mktemp -d .tools/string-request-callback-owner-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-cast-owner --output "$$(mktemp -d .tools/string-request-callback-cast-owner-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-cast-owner --peer --output "$$(mktemp -d .tools/string-request-callback-cast-owner-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-known-key --output "$$(mktemp -d .tools/string-request-callback-known-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-known-key --peer --output "$$(mktemp -d .tools/string-request-callback-known-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-known-key-release --output "$$(mktemp -d .tools/string-request-known-key-release-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-known-key-release --peer --output "$$(mktemp -d .tools/string-request-known-key-release-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-variable-key-release --output "$$(mktemp -d .tools/string-request-variable-key-release-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-variable-key-release --peer --output "$$(mktemp -d .tools/string-request-variable-key-release-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-rebound-key --output "$$(mktemp -d .tools/string-request-callback-rebound-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-rebound-key --peer --output "$$(mktemp -d .tools/string-request-callback-rebound-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-referenced-key --peer --output "$$(mktemp -d .tools/string-request-callback-referenced-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-late-reference --output "$$(mktemp -d .tools/string-request-callback-late-reference-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-late-reference --peer --output "$$(mktemp -d .tools/string-request-callback-late-reference-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-scalar-key --output "$$(mktemp -d .tools/string-request-callback-scalar-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-scalar-key --peer --output "$$(mktemp -d .tools/string-request-callback-scalar-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-ordinary-key --output "$$(mktemp -d .tools/string-request-callback-ordinary-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-ordinary-key --peer --output "$$(mktemp -d .tools/string-request-callback-ordinary-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-text-key --output "$$(mktemp -d .tools/string-request-callback-text-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-text-key --peer --output "$$(mktemp -d .tools/string-request-callback-text-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-old-key --output "$$(mktemp -d .tools/string-request-callback-old-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-old-key --peer --output "$$(mktemp -d .tools/string-request-callback-old-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-plain-key --output "$$(mktemp -d .tools/string-request-callback-plain-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-plain-key --peer --output "$$(mktemp -d .tools/string-request-callback-plain-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-request-key --output "$$(mktemp -d .tools/string-request-callback-request-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-request-key --peer --output "$$(mktemp -d .tools/string-request-callback-request-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-marked-request-key --output "$$(mktemp -d .tools/string-request-callback-marked-request-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-marked-request-key --peer --output "$$(mktemp -d .tools/string-request-callback-marked-request-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-marked-interned-key --output "$$(mktemp -d .tools/string-request-callback-marked-interned-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-marked-interned-key --peer --output "$$(mktemp -d .tools/string-request-callback-marked-interned-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-raw-message-key --output "$$(mktemp -d .tools/string-request-callback-raw-message-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-raw-message-key --peer --output "$$(mktemp -d .tools/string-request-callback-raw-message-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-ordinary-raw-key --output "$$(mktemp -d .tools/string-request-callback-ordinary-raw-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-ordinary-raw-key --peer --output "$$(mktemp -d .tools/string-request-callback-ordinary-raw-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-reference-raw-key --output "$$(mktemp -d .tools/string-request-callback-reference-raw-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-reference-raw-key --peer --output "$$(mktemp -d .tools/string-request-callback-reference-raw-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-raw-key-cell-owner --output "$$(mktemp -d .tools/string-request-callback-raw-key-cell-owner-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-raw-key-cell-owner --peer --output "$$(mktemp -d .tools/string-request-callback-raw-key-cell-owner-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-marked-raw-key-cell-owner --output "$$(mktemp -d .tools/string-request-callback-marked-raw-key-cell-owner-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-marked-raw-key-cell-owner --peer --output "$$(mktemp -d .tools/string-request-callback-marked-raw-key-cell-owner-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-reference-raw-key-cell-owner --output "$$(mktemp -d .tools/string-request-callback-reference-raw-key-cell-owner-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --request-callback-reference-raw-key-cell-owner --peer --output "$$(mktemp -d .tools/string-request-callback-reference-raw-key-cell-owner-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --literal-callback-raw-key --output "$$(mktemp -d .tools/string-literal-callback-raw-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --literal-callback-raw-key --peer --output "$$(mktemp -d .tools/string-literal-callback-raw-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --initial-raw-leading-key --output "$$(mktemp -d .tools/string-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --variable-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-variable-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --variable-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-variable-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --reference-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-reference-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --reference-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-reference-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --conditional-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-conditional-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --conditional-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-conditional-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --string-conditional-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-string-conditional-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --string-conditional-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-string-conditional-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --coalesce-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-coalesce-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --coalesce-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-coalesce-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --integer-conditional-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-integer-conditional-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --integer-conditional-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-integer-conditional-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --float-conditional-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-float-conditional-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --float-conditional-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-float-conditional-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --null-conditional-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-null-conditional-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --null-conditional-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-null-conditional-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --null-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-null-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --null-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-null-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --false-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-false-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --false-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-false-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --integer-zero-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-integer-zero-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --integer-zero-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-integer-zero-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --float-zero-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-float-zero-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --float-zero-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-float-zero-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --negative-zero-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-negative-zero-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --negative-zero-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-negative-zero-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --unary-plus-zero-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-unary-plus-zero-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --unary-plus-zero-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-unary-plus-zero-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-true-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-true-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-true-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-true-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-integer-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-integer-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-integer-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-integer-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-integer-unary-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-integer-unary-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-integer-unary-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-integer-unary-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-true-unary-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-true-unary-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-true-unary-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-true-unary-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-integer-arithmetic-unary-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-integer-arithmetic-unary-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-integer-arithmetic-unary-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-integer-arithmetic-unary-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-string-shorthand-base-initial-raw-leading-key --output "$$(mktemp -d .tools/string-boolean-not-string-shorthand-base-initial-raw-leading-key-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_marked_cv_protocol.py --boolean-not-string-shorthand-base-initial-raw-leading-key --peer --output "$$(mktemp -d .tools/string-boolean-not-string-shorthand-base-initial-raw-leading-key-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --output "$$(mktemp -d .tools/string-current-array-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --peer --output "$$(mktemp -d .tools/string-current-array-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --alias --output "$$(mktemp -d .tools/string-current-array-alias-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --alias --peer --output "$$(mktemp -d .tools/string-current-array-alias-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --mixed --output "$$(mktemp -d .tools/string-current-array-mixed-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --mixed --peer --output "$$(mktemp -d .tools/string-current-array-mixed-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --string-alias --output "$$(mktemp -d .tools/string-current-array-string-alias-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --string-alias --peer --output "$$(mktemp -d .tools/string-current-array-string-alias-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --child --output "$$(mktemp -d .tools/string-current-array-child-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --child --peer --output "$$(mktemp -d .tools/string-current-array-child-cv-peer-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --alias-child --output "$$(mktemp -d .tools/string-current-array-alias-child-cv-state-XXXXXX)/run"
	python3 -B tests/semantics/string_offset_current_array_cv_protocol.py --alias-child --peer --output "$$(mktemp -d .tools/string-current-array-alias-child-cv-peer-XXXXXX)/run"
	python3 tests/semantics/tick_sources.py
	python3 tests/semantics/tick_review_sources.py
	python3 tests/semantics/tick_switch_sources.py
	python3 tests/semantics/tick_switch_review_sources.py
	python3 tests/semantics/tick_state.py
	python3 tests/semantics/tick_switch_review_protocol.py
	python3 tests/semantics/tick_generator_sources.py
	python3 tests/semantics/tick_generator_review_sources.py
	python3 tests/semantics/tick_generator_review_protocol.py
	python3 tests/semantics/tick_match_sources.py
	python3 tests/semantics/tick_match_review_sources.py
	python3 tests/semantics/tick_match_review_protocol.py
	python3 tests/semantics/tick_elision_sources.py
	python3 tests/semantics/tick_elision_review_sources.py
	python3 tests/semantics/tick_elision_review_protocol.py
	python3 tests/semantics/tick_coalesce_sources.py
	python3 tests/semantics/tick_coalesce_review_sources.py
	python3 tests/semantics/tick_coalesce_review_protocol.py
	python3 tests/semantics/tick_echo_sources.py
	python3 tests/semantics/tick_echo_review_sources.py
	python3 tests/semantics/tick_echo_review_protocol.py
	python3 tests/semantics/tick_coalesce_reader_sources.py
	python3 tests/semantics/tick_key_carrier_review_sources.py
	python3 tests/semantics/tick_key_carrier_review_protocol.py
	python3 tests/semantics/tick_grouped_sources.py
	python3 tests/semantics/tick_grouped_review_sources.py
	python3 tests/semantics/tick_grouped_review_protocol.py
	python3 tests/semantics/tick_foreach_sources.py
	python3 tests/semantics/tick_foreach_review_sources.py
	python3 tests/semantics/tick_foreach_review_protocol.py
	python3 tests/semantics/tick_list_sources.py
	python3 tests/semantics/tick_list_review_sources.py
	python3 tests/semantics/tick_list_review_protocol.py
	python3 tests/semantics/tick_constant_sources.py
	python3 tests/semantics/tick_constant_review_sources.py
	python3 tests/semantics/tick_const_review_protocol.py
	python3 tests/semantics/tick_classlike_sources.py
	python3 tests/semantics/tick_classlike_review_sources.py
	python3 tests/semantics/tick_classlike_review_protocol.py
	python3 tests/semantics/tick_enum_case_sources.py
	python3 tests/semantics/tick_enum_case_review_sources.py
	python3 tests/semantics/tick_enum_case_review_protocol.py
	python3 tests/semantics/tick_class_const_sources.py
	python3 tests/semantics/tick_class_const_review_sources.py
	python3 tests/semantics/tick_class_const_review_protocol.py
	python3 tests/semantics/tick_property_sources.py
	python3 tests/semantics/tick_property_review_sources.py
	python3 tests/semantics/tick_property_review_protocol.py
	python3 tests/semantics/tick_hook_sources.py
	python3 tests/semantics/tick_hook_review_sources.py
	python3 tests/semantics/tick_hook_review_protocol.py
	python3 tests/semantics/tick_trait_use_sources.py
	python3 tests/semantics/tick_trait_use_review_sources.py
	python3 tests/semantics/tick_trait_use_review_protocol.py
	python3 tests/semantics/tick_trait_adaptation_sources.py
	python3 tests/semantics/tick_trait_adaptation_review_sources.py
	python3 tests/semantics/tick_trait_adaptation_review_protocol.py
	python3 tests/semantics/tick_namespace_sources.py
	python3 tests/semantics/tick_namespace_review_sources.py
	python3 tests/semantics/tick_namespace_review_protocol.py
	python3 tests/semantics/tick_import_sources.py
	python3 tests/semantics/tick_import_review_sources.py
	python3 tests/semantics/tick_import_review_protocol.py
	python3 tests/semantics/tick_halt_sources.py
	python3 tests/semantics/tick_halt_review_sources.py
	python3 tests/semantics/tick_halt_review_protocol.py
	python3 tests/semantics/tick_parameter_sources.py
	python3 tests/semantics/tick_parameter_review_sources.py
	python3 tests/semantics/tick_parameter_review_protocol.py
	python3 tests/semantics/tick_callable_parameter_sources.py
	python3 tests/semantics/tick_callable_parameter_review_sources.py
	python3 tests/semantics/tick_callable_parameter_review_protocol.py
	python3 tests/semantics/tick_short_get_sources.py
	python3 tests/semantics/tick_short_get_review_sources.py
	python3 tests/semantics/tick_short_get_review_protocol.py
	python3 tests/semantics/tick_trait_get_sources.py
	python3 tests/semantics/tick_trait_get_review_protocol.py
	python3 tests/semantics/output_buffer_sources.py
	python3 tests/semantics/output_buffer_state.py
	python3 tests/semantics/output_reference_warning_sources.py
	python3 tests/semantics/output_reference_warning_review_sources.py
	python3 tests/semantics/output_reference_warning_state.py --select live-prefix
	python3 tests/semantics/output_reference_warning_state.py --select retired-prefix
	python3 tests/semantics/output_vm_reference_warning_state.py
	python3 tests/semantics/output_automatic_reference_warning_review_sources.py
	python3 tests/semantics/output_automatic_reference_warning_review_state.py
	python3 tests/semantics/output_abrupt_sources.py --select reference-warning-throw,reference-warning-retired-entry,callback-exit
	python3 tests/semantics/output_deprecation_warning_sources.py
	python3 tests/semantics/output_deprecation_warning_state.py
	python3 tests/semantics/output_reference_return_sources.py
	python3 tests/semantics/output_reference_return_state.py
	python3 tests/semantics/output_reference_return_review_sources.py
	python3 tests/semantics/output_reference_return_review_state.py
	python3 tests/semantics/output_array_return_sources.py
	python3 tests/semantics/output_array_return_state.py
	python3 tests/semantics/output_object_return_sources.py
	python3 tests/semantics/output_object_return_state.py --select fresh-unique-ref-object-precast-gc,pending-deprecation-skips-cast
	python3 tests/semantics/output_object_return_state.py --select method-reference-notice-framed,method-reference-notice-unframed
	python3 tests/semantics/output_final_conversion_sources.py
	python3 tests/semantics/output_final_conversion_state.py
	python3 tests/semantics/output_final_conversion_review_sources.py
	python3 tests/semantics/output_final_conversion_review_state.py
	python3 tests/semantics/output_final_error_sources.py
	python3 tests/semantics/output_final_error_review_state.py
	python3 tests/semantics/output_final_cast_throw_sources.py
	python3 tests/semantics/output_final_cast_throw_review_state.py
	python3 tests/semantics/output_final_quiet_modulo_type_coercion_sources.py
	python3 tests/semantics/output_final_quiet_modulo_type_coercion_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-quiet-modulo-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_quiet_modulo_type_coercion_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-quiet-modulo-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_quiet_arithmetic_type_coercion_sources.py
	python3 tests/semantics/output_final_quiet_arithmetic_type_coercion_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-quiet-arithmetic-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_quiet_arithmetic_type_coercion_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-quiet-arithmetic-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_arithmetic_warning_type_error_sources.py
	python3 tests/semantics/output_final_arithmetic_warning_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-arithmetic-warning-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_arithmetic_warning_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-arithmetic-warning-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_arithmetic_warning_type_error_sources.py
	python3 tests/semantics/output_final_default_arithmetic_warning_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-arithmetic-warning-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_arithmetic_warning_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-arithmetic-warning-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_left_arithmetic_type_error_sources.py
	python3 tests/semantics/output_final_left_arithmetic_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-left-arithmetic-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_left_arithmetic_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-left-arithmetic-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_both_string_arithmetic_type_error_sources.py
	python3 tests/semantics/output_final_both_string_arithmetic_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-both-string-arithmetic-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_both_string_arithmetic_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-both-string-arithmetic-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_leading_right_arithmetic_type_error_sources.py
	python3 tests/semantics/output_final_leading_right_arithmetic_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-leading-right-arithmetic-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_leading_right_arithmetic_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-leading-right-arithmetic-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_swapped_arithmetic_warning_type_error_sources.py
	python3 tests/semantics/output_final_swapped_arithmetic_warning_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-swapped-arithmetic-warning-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_swapped_arithmetic_warning_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-swapped-arithmetic-warning-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_swapped_left_arithmetic_type_error_sources.py
	python3 tests/semantics/output_final_swapped_left_arithmetic_type_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-swapped-left-arithmetic-type.XXXXXXXX)/state"
	python3 tests/semantics/output_final_swapped_left_arithmetic_type_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-swapped-left-arithmetic-type.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_division_warning_error_sources.py
	python3 tests/semantics/output_final_default_division_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-division-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_division_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-division-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_null_division_warning_error_sources.py
	python3 tests/semantics/output_final_default_null_division_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-null-division-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_null_division_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-null-division-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_scalar_zero_division_warning_error_sources.py
	python3 tests/semantics/output_final_default_scalar_zero_division_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-scalar-zero-division-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_scalar_zero_division_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-scalar-zero-division-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_cv_zero_division_warning_error_sources.py
	python3 tests/semantics/output_final_default_cv_zero_division_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-cv-zero-division-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_cv_zero_division_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-cv-zero-division-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_division_operand_warning_error_sources.py
	python3 tests/semantics/output_final_default_division_operand_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-division-operand-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_division_operand_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-division-operand-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_constant_left_division_warning_error_sources.py
	python3 tests/semantics/output_final_default_constant_left_division_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-constant-left-division-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_constant_left_division_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-constant-left-division-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_constant_pair_division_warning_error_sources.py
	python3 tests/semantics/output_final_default_constant_pair_division_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-constant-pair-division-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_constant_pair_division_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-constant-pair-division-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_constant_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_constant_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-constant-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_constant_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-constant-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_quiet_zero_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_quiet_zero_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-quiet-zero-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_quiet_zero_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-quiet-zero-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_cv_zero_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_cv_zero_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-cv-zero-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_cv_zero_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-cv-zero-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_left_cv_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_left_cv_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-cv-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_left_cv_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-cv-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_cv_pair_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_cv_pair_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-cv-pair-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_cv_pair_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-cv-pair-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_fractional_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_fractional_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_fractional_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_fractional_cv_zero_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_fractional_cv_zero_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-cv-zero-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_fractional_cv_zero_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-cv-zero-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_fractional_left_cv_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_fractional_left_cv_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-left-cv-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_fractional_left_cv_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-left-cv-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_fractional_cv_pair_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_fractional_cv_pair_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-cv-pair-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_fractional_cv_pair_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-fractional-cv-pair-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_masked_fractional_modulo_warning_error_sources.py
	python3 tests/semantics/output_final_default_masked_fractional_modulo_warning_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-masked-fractional-modulo-warning-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_masked_fractional_modulo_warning_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-masked-fractional-modulo-warning-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_right_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_right_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-right-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_right_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-right-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_both_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_both_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_both_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_right_cv_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_right_cv_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-right-cv-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_right_cv_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-right-cv-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_both_left_cv_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_both_left_cv_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-left-cv-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_both_left_cv_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-left-cv-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_both_right_cv_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_both_right_cv_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-right-cv-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_both_right_cv_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-right-cv-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_both_cv_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_both_cv_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-cv-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_both_cv_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-both-cv-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_quiet_left_cv_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_quiet_left_cv_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-quiet-left-cv-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_quiet_left_cv_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-quiet-left-cv-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_left_modulo_deprecation_error_sources.py
	python3 tests/semantics/output_final_default_left_modulo_deprecation_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-modulo-deprecation-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_left_modulo_deprecation_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-modulo-deprecation-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_left_modulo_range_error_sources.py
	python3 tests/semantics/output_final_default_left_modulo_range_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-modulo-range-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_left_modulo_range_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-modulo-range-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_left_modulo_nan_error_sources.py
	python3 tests/semantics/output_final_default_left_modulo_nan_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-modulo-nan-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_left_modulo_nan_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-left-modulo-nan-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_unrelated_handler_modulo_error_sources.py
	python3 tests/semantics/output_final_default_unrelated_handler_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_unrelated_handler_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_unrelated_warning_handler_modulo_error_sources.py
	python3 tests/semantics/output_final_default_unrelated_warning_handler_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-warning-handler-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_unrelated_warning_handler_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-warning-handler-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_selected_handlers_quiet_modulo_error_sources.py
	python3 tests/semantics/output_final_default_selected_handlers_quiet_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-selected-handlers-quiet-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_selected_handlers_quiet_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-selected-handlers-quiet-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_unrelated_handler_left_modulo_range_error_sources.py
	python3 tests/semantics/output_final_default_unrelated_handler_left_modulo_range_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-left-modulo-range-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_unrelated_handler_left_modulo_range_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-left-modulo-range-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_unrelated_handler_right_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_unrelated_handler_right_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-right-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_unrelated_handler_right_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-right-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_default_unrelated_handler_both_modulo_conversion_error_sources.py
	python3 tests/semantics/output_final_default_unrelated_handler_both_modulo_conversion_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-both-modulo-conversion-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_default_unrelated_handler_both_modulo_conversion_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-default-unrelated-handler-both-modulo-conversion-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_warning_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_warning_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-warning-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_warning_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-warning-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_left_warning_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_left_warning_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-left-warning-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_left_warning_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-left-warning-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_both_warning_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_both_warning_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-both-warning-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_both_warning_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-both-warning-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_left_deprecated_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_left_deprecated_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-left-deprecated-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_left_deprecated_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-left-deprecated-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_precision_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_precision_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-precision-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_precision_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-precision-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_mixed_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_mixed_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-mixed-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_mixed_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-mixed-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_both_mask_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_both_mask_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-both-mask-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_both_mask_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-both-mask-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_both_mask_modulo_error_review_state.py --affected --output "$$(mktemp -d /tmp/php-spec-output-final-selected-both-mask-modulo-error.XXXXXXXX)/affected"
	python3 tests/semantics/output_final_selected_explicit_null_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_explicit_null_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-explicit-null-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_explicit_null_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-explicit-null-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_bare_return_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_bare_return_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-bare-return-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_bare_return_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-bare-return-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_true_return_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_true_return_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-true-return-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_true_return_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-true-return-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_zero_return_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_zero_return_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-zero-return-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_zero_return_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-zero-return-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_false_return_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_false_return_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-false-return-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_false_return_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-false-return-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_integer_return_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_integer_return_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-integer-return-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_integer_return_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-integer-return-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_final_selected_float_return_modulo_error_sources.py
	python3 tests/semantics/output_final_selected_float_return_modulo_error_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-float-return-modulo-error.XXXXXXXX)/state"
	python3 tests/semantics/output_final_selected_float_return_modulo_error_review_state.py --output "$$(mktemp -d /tmp/php-spec-output-final-selected-float-return-modulo-error.XXXXXXXX)/peer"
	python3 tests/semantics/output_object_conversion_review_sources.py
	python3 tests/semantics/output_object_conversion_review_state.py
	python3 tests/semantics/output_array_conversion_review_sources.py
	python3 tests/semantics/output_array_conversion_review_state.py
	python3 tests/semantics/output_deprecation_warning_review_sources.py
	python3 tests/semantics/output_deprecation_warning_review_state.py
	python3 tests/semantics/output_request_end_sources.py
	python3 tests/semantics/output_final_protocol.py
	python3 tests/semantics/output_final_review_protocol.py
	python3 tests/semantics/output_final_throw_sources.py
	python3 tests/semantics/output_final_throw_protocol.py
	python3 tests/semantics/output_final_throw_review_protocol.py
	python3 tests/semantics/output_pending_release_sources.py
	python3 tests/semantics/output_pending_release_protocol.py
	python3 tests/semantics/output_pending_release_review_protocol.py
	python3 tests/semantics/output_final_exception_sources.py
	python3 tests/semantics/output_final_exception_protocol.py
	python3 tests/semantics/output_final_exception_review_protocol.py
	python3 tests/semantics/output_executor_nonfast_sources.py
	python3 tests/semantics/output_executor_nonfast_protocol.py
	python3 tests/semantics/output_executor_nonfast_review_protocol.py
	python3 tests/semantics/output_executor_post_deactivate_sources.py
	python3 tests/semantics/output_executor_post_deactivate_boundaries.py
	python3 tests/semantics/output_executor_post_deactivate_state.py
	python3 tests/semantics/output_executor_retval_sources.py
	python3 tests/semantics/output_executor_retval_state.py
	python3 tests/semantics/output_executor_explicit_sources.py
	python3 tests/semantics/output_executor_explicit_state.py
	python3 tests/semantics/output_executor_reception_sources.py
	python3 tests/semantics/output_executor_reception_state.py
	python3 tests/semantics/output_executor_reception_review_sources.py
	python3 tests/semantics/output_executor_reception_review_state.py
	python3 tests/semantics/output_executor_creation_sources.py
	python3 tests/semantics/output_executor_creation_state.py
	python3 tests/semantics/output_executor_creation_review_sources.py
	python3 tests/semantics/output_executor_creation_review_state.py
	python3 tests/semantics/output_executor_invalid_sources.py
	python3 tests/semantics/output_executor_invalid_state.py
	python3 tests/semantics/output_executor_invalid_review_sources.py
	python3 tests/semantics/output_executor_invalid_review_state.py
	python3 tests/semantics/output_executor_notice_discard_sources.py
	python3 tests/semantics/output_executor_notice_discard_state.py
	python3 tests/semantics/output_executor_notice_discard_review_sources.py
	python3 tests/semantics/output_executor_notice_discard_review_state.py
	python3 tests/semantics/output_executor_notice_retval_throw_sources.py
	python3 tests/semantics/output_executor_notice_retval_throw_state.py
	python3 tests/semantics/output_executor_notice_retval_throw_review_sources.py
	python3 tests/semantics/output_executor_notice_retval_throw_review_state.py
	python3 tests/semantics/output_executor_notice_retval_throw_offkind.py
	python3 tests/semantics/output_executor_notice_retval_throw_offkind_state.py
	python3 tests/semantics/output_executor_warning_retval_nested_sources.py
	python3 tests/semantics/output_executor_warning_retval_nested_state.py
	python3 tests/semantics/output_executor_warning_retval_nested_review_sources.py
	python3 tests/semantics/request_provider.py
	python3 tests/semantics/evidence.py
	python3 tests/semantics/source_occurrences.py
	python3 tests/semantics/source_context.py
	python3 tests/semantics/truth_compiler.py
	python3 tests/semantics/truth_expressions.py
	python3 tests/semantics/comparison_compiler.py
	python3 tests/semantics/comparison.py
	python3 tests/semantics/gc_identity_source.py
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
	@out="$$(mktemp -d .tools/a56-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_data_destructor_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/array_iterator_data_destructor_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_data_destructor_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/array_iterator_data_destructor_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	python3 tests/semantics/array_iterator_byval_fields_cleanup_sources.py
	@out="$$(mktemp -d .tools/a57-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_traversable_reference_cache_sources.py --output "$$out/iterator-source" && \
		python3 tests/semantics/array_traversable_reference_cache_state.py --source-report "$$out/iterator-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_traversable_reference_cache_state_review.py --source-report "$$out/iterator-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/array_traversable_reference_aggregate_sources.py --output "$$out/aggregate-source"
	@out="$$(mktemp -d .tools/a58-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_generator_reference_cache_sources.py --output "$$out/generator-source" && \
		python3 tests/semantics/array_generator_reference_cache_state.py --source-report "$$out/generator-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_generator_reference_cache_state_review.py --source-report "$$out/generator-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/array_generator_reference_aggregate_sources.py --output "$$out/aggregate-source"
	@out="$$(mktemp -d .tools/a59-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_generator_byref_reference_cache_sources.py --output "$$out/generator-source" && \
		python3 tests/semantics/array_generator_byref_reference_cache_state.py --source-report "$$out/generator-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_generator_byref_reference_cache_state_review.py --source-report "$$out/generator-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/array_generator_byref_reference_aggregate_sources.py --output "$$out/aggregate-source"
	@out="$$(mktemp -d .tools/a60-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_byref_reference_cache_sources.py --output "$$out/iterator-source" && \
		python3 tests/semantics/array_iterator_byref_reference_cache_state.py --source-report "$$out/iterator-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_byref_reference_cache_state_review.py --source-report "$$out/iterator-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/array_iterator_byref_reference_aggregate_sources.py --output "$$out/aggregate-source"
	@out="$$(mktemp -d .tools/a61-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_byref_destructor_sources.py --output "$$out/iterator-source" && \
		python3 tests/semantics/array_iterator_byref_destructor_state.py --source-report "$$out/iterator-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_byref_destructor_state_review.py --source-report "$$out/iterator-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/array_iterator_byref_destructor_aggregate_sources.py --output "$$out/aggregate-source"
	@out="$$(mktemp -d .tools/a62-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_owned_field_sources.py --output "$$out/iterator-source" && \
		python3 tests/semantics/array_iterator_owned_field_state.py --source-report "$$out/iterator-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_owned_field_state_review.py --source-report "$$out/iterator-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/array_iterator_owned_field_aggregate_sources.py --output "$$out/aggregate-source" && \
		python3 tests/semantics/array_iterator_owned_field_next_throw_sources.py --output "$$out/next-throw-source" && \
		python3 tests/semantics/array_iterator_owned_field_independent_sources.py --output "$$out/independent-source"
	@out="$$(mktemp -d .tools/a63-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_pooled_field_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/array_iterator_pooled_field_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_pooled_field_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/array_iterator_pooled_field_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a64-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_fields_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/array_iterator_fields_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_fields_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/array_iterator_fields_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a65-test-semantics-XXXXXX)" && \
		python3 tests/semantics/array_iterator_byval_fields_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/array_iterator_byval_fields_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/array_iterator_byval_fields_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/array_iterator_byval_fields_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a66-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_iterator_reference_current_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_iterator_reference_current_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_iterator_reference_current_cleanup_sources.py --output "$$out/cleanup-source" && \
		python3 tests/semantics/config_iterator_reference_current_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_iterator_reference_current_state_review.py --source-report "$$out/peer-source/report.json" --source-report "$$out/cleanup-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a67-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_iterator_typed_current_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_iterator_values_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_iterator_reference_current_sources.py --case config-reference-current-typed-cell-boundary --output "$$out/promoted-source" && \
		python3 tests/semantics/config_iterator_typed_current_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_iterator_typed_current_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a68-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_iterator_scalar_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_iterator_scalar_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_iterator_scalar_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_iterator_scalar_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a69-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_iterator_argument_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_iterator_argument_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_iterator_argument_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_iterator_argument_state_review.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/config_iterator_argument_abort_sources.py --output "$$out/invalid-key-source"
	@out="$$(mktemp -d .tools/a70-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_iterator_input_finalizer_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_iterator_input_finalizer_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_iterator_input_finalizer_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_iterator_input_finalizer_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a71-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_scalar_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_scalar_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_scalar_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_scalar_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a72-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_scalar_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_scalar_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_scalar_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_scalar_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a73-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_sole_data_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_sole_data_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_closed_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_closed_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a74-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_outside_alias_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_outside_alias_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_outside_alias_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_outside_alias_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a75-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_temporary_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_temporary_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_temporary_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_temporary_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a76-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_factory_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_factory_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_factory_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_factory_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a77-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_owning_value_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_owning_value_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_owning_value_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_owning_value_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/config_generator_owning_key_control.py --source-report "$$out/peer-source/report.json" --output "$$out/key-control"
	@out="$$(mktemp -d .tools/a78-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_owning_temporary_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_owning_temporary_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_owning_temporary_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_owning_temporary_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a79-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_owning_cache_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_owning_cache_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_owning_cache_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_owning_cache_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a80-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_two_owning_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_two_owning_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_two_owning_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_two_owning_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state" && \
		python3 tests/semantics/config_generator_two_owning_array_sources.py --output "$$out/array-source"
	@out="$$(mktemp -d .tools/a81-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_owning_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_owning_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_owning_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_owning_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a82-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_owning_cache_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_owning_cache_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_owning_cache_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_owning_cache_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a83-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_owning_live_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_owning_live_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_owning_live_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_owning_live_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a84-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_owning_alias_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_owning_alias_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_owning_alias_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_owning_alias_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a85-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_temporary_owning_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_temporary_owning_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_temporary_owning_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_temporary_owning_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a86-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_temporary_owning_alias_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_temporary_owning_alias_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_temporary_owning_alias_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_temporary_owning_alias_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a87-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_factory_owning_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_factory_owning_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_factory_owning_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_factory_owning_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a88-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_factory_owning_alias_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_factory_owning_alias_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_factory_owning_alias_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_factory_owning_alias_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a89-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_temporary_first_owning_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_temporary_first_owning_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-terminal-state" && \
		python3 tests/semantics/config_generator_temporary_first_owning_reference_early_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-early-state" && \
		python3 tests/semantics/config_generator_temporary_first_owning_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_temporary_first_owning_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a90-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_temporary_two_owning_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_temporary_two_owning_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_temporary_two_owning_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_temporary_two_owning_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a91-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_factory_first_owning_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_factory_first_owning_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_factory_first_owning_reference_early_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-early-state" && \
		python3 tests/semantics/config_generator_factory_first_owning_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_factory_first_owning_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a92-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_factory_two_owning_reference_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_factory_two_owning_reference_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_factory_two_owning_reference_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_factory_two_owning_reference_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/a93-test-semantics-XXXXXX)" && \
		python3 tests/semantics/config_generator_reference_two_owning_sources.py --output "$$out/author-source" && \
		python3 tests/semantics/config_generator_reference_two_owning_state.py --source-report "$$out/author-source/report.json" --output "$$out/author-state" && \
		python3 tests/semantics/config_generator_reference_two_owning_review_sources.py --output "$$out/peer-source" && \
		python3 tests/semantics/config_generator_reference_two_owning_review_state.py --source-report "$$out/peer-source/report.json" --output "$$out/peer-state"
	@out="$$(mktemp -d .tools/config-generator-bounded-ownership-XXXXXX)" && \
		python3 tests/semantics/config_generator_bounded_ownership_sources.py --output "$$out/source" && \
		python3 tests/semantics/config_generator_bounded_ownership_state.py --source-report "$$out/source/report.json" --output "$$out/state" && \
		python3 tests/semantics/config_generator_bounded_ownership_refusals.py --output "$$out/refusals"
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
	@strict_float_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-strict-float-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_strict_float_sources.py --output "$$strict_float_out/source" && \
		python3 tests/semantics/string_offset_strict_float_protocol.py --source-report "$$strict_float_out/source/report.json" --output "$$strict_float_out/author-state" && \
		python3 tests/semantics/string_offset_strict_float_review_state.py --source-report "$$strict_float_out/source/report.json" --output "$$strict_float_out/review-state"
	@nested_unset_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-nested-unset-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_nested_unset_sources.py --output "$$nested_unset_out/source" && \
		python3 tests/semantics/string_offset_nested_unset_protocol.py --source-report "$$nested_unset_out/source/report.json" --output "$$nested_unset_out/author-state" && \
		python3 tests/semantics/string_offset_nested_unset_review_state.py --source-report "$$nested_unset_out/source/report.json" --output "$$nested_unset_out/review-state"
	@aa_exists_out="$$(mktemp -d "$(CURDIR)/.tools/aa-exists-test-XXXXXX")" && \
		python3 -B tests/semantics/arrayaccess_reference_exists_run.py --output "$$aa_exists_out/source" && \
		python3 -B tests/semantics/arrayaccess_reference_exists_protocol.py --output "$$aa_exists_out/state"
	@aa_discard_out="$$(mktemp -d "$(CURDIR)/.tools/aa-discard-test-XXXXXX")" && \
		python3 -B tests/semantics/arrayaccess_reference_discard_run.py --output "$$aa_discard_out/source" && \
		python3 -B tests/semantics/arrayaccess_reference_discard_protocol.py set --output "$$aa_discard_out/set" && \
		python3 -B tests/semantics/arrayaccess_reference_discard_protocol.py unset --output "$$aa_discard_out/unset"
	@aa_literal_out="$$(mktemp -d "$(CURDIR)/.tools/aa-literal-test-XXXXXX")" && \
		python3 -B tests/semantics/arrayaccess_literal_key_run.py --output "$$aa_literal_out/source" && \
		python3 -B tests/semantics/arrayaccess_literal_key_protocol.py --output "$$aa_literal_out/state"
	@string_literal_out="$$(mktemp -d "$(CURDIR)/.tools/string-literal-base-test-XXXXXX")" && \
		python3 -B tests/semantics/string_literal_base_run.py --output "$$string_literal_out/source" && \
		python3 -B tests/semantics/string_literal_base_protocol.py --output "$$string_literal_out/state"
	python3 -B tests/semantics/multi_static_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/object_property_source_order_sources.py
	python3 -B tests/semantics/multi_property_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/same_owner_property_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/mixed_property_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/same_class_static_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/grouped_static_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/same_class_mixed_property_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/same_class_mixed_hole_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/static_only_mixed_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/grouped_unused_mixed_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/direct_sibling_property_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/same_class_mixed_direct_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/static_direct_sibling_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/class_int_constant_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/class_negative_int_constant_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/namespaced_class_int_constant_alias_stdclass_reference_notice_run.py
	python3 -B tests/semantics/namespaced_primary_producer_reference_notice_run.py
	python3 -B tests/semantics/array_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/array_byref_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/array_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/untyped_array_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/nullable_array_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/union_array_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/int_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/scalar_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/request_string_return_producer_cv_reference_notice_run.py
	python3 -B tests/semantics/request_string_array_leaf_reference_notice_run.py
	python3 -B tests/semantics/request_string_object_field_reference_notice_run.py
	python3 -B tests/semantics/stdclass_alias_scalar_field_reference_notice_run.py
	python3 -B tests/semantics/stdclass_alias_array_field_reference_notice_run.py
	python3 -B tests/semantics/stdclass_direct_array_field_reference_notice_run.py
	python3 -B tests/semantics/stdclass_direct_object_field_reference_notice_run.py
	python3 -B tests/semantics/stdclass_alias_object_field_reference_notice_run.py
	python3 -B tests/semantics/mixed_object_array_field_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_array_return_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_scalar_return_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_nullable_array_return_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_union_array_return_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_nullable_scalar_return_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_union_scalar_return_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_array_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_scalar_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/multi_cv_nullable_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/singleton_cv_typed_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/singleton_cv_nullable_scalar_return_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_union_null_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_distinct_builtin_union_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_primitive_union_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_distinct_builtin_union_return_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_primitive_union_return_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_null_return_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_mixed_return_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_mixed_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_null_formal_producer_reference_notice_run.py
	python3 -B tests/semantics/cv_literal_bool_formal_producer_reference_notice_run.py
	@terminal_unset_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-terminal-unset-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_terminal_unset_sources.py --output "$$terminal_unset_out/source" && \
		python3 tests/semantics/string_offset_terminal_unset_protocol.py --source-report "$$terminal_unset_out/source/report.json" --output "$$terminal_unset_out/author-state" && \
		python3 tests/semantics/string_offset_terminal_unset_review_state.py --source-report "$$terminal_unset_out/source/report.json" --output "$$terminal_unset_out/review-state"
	@retained_carrier_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-retained-carrier-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_retained_carrier_sources.py --output "$$retained_carrier_out/source" && \
		python3 tests/semantics/string_offset_retained_carrier_protocol.py --source-report "$$retained_carrier_out/source/report.json" --output "$$retained_carrier_out/author-state" && \
		python3 tests/semantics/string_offset_retained_carrier_review_state.py --source-report "$$retained_carrier_out/source/report.json" --output "$$retained_carrier_out/review-state"
	@leading_text_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-leading-text-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_leading_text_sources.py --output "$$leading_text_out/source" && \
		python3 tests/semantics/string_offset_leading_text_protocol.py --source-report "$$leading_text_out/source/report.json" --output "$$leading_text_out/author-state" && \
		python3 tests/semantics/string_offset_leading_text_review_state.py --source-report "$$leading_text_out/source/report.json" --output "$$leading_text_out/review-state"
	@reference_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-reference-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_reference_key_sources.py --output "$$reference_key_out/source" && \
		python3 tests/semantics/string_offset_reference_key_protocol.py --source-report "$$reference_key_out/source/report.json" --output "$$reference_key_out/author-state" && \
		python3 tests/semantics/string_offset_reference_key_review_state.py --source-report "$$reference_key_out/source/report.json" --output "$$reference_key_out/review-state"
	@reference_base_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-reference-base-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_reference_base_sources.py --output "$$reference_base_out/source" && \
		python3 tests/semantics/string_offset_reference_base_protocol.py --source-report "$$reference_base_out/source/report.json" --output "$$reference_base_out/author-state" && \
		python3 tests/semantics/string_offset_reference_base_review_state.py --source-report "$$reference_base_out/source/report.json" --output "$$reference_base_out/review-state"
	@reference_request_base_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-reference-request-base-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_reference_request_base_sources.py --output "$$reference_request_base_out/source" && \
		python3 tests/semantics/string_offset_reference_request_base_protocol.py --source-report "$$reference_request_base_out/source/report.json" --output "$$reference_request_base_out/author-state" && \
		python3 tests/semantics/string_offset_reference_request_base_review_state.py --source-report "$$reference_request_base_out/source/report.json" --output "$$reference_request_base_out/review-state"
	@reference_alias_keeper_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-reference-alias-keeper-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_reference_alias_keeper_sources.py --output "$$reference_alias_keeper_out/source" && \
		python3 tests/semantics/string_offset_reference_alias_keeper_protocol.py --source-report "$$reference_alias_keeper_out/source/report.json" --output "$$reference_alias_keeper_out/author-state" && \
		python3 tests/semantics/string_offset_reference_alias_keeper_review_state.py --source-report "$$reference_alias_keeper_out/source/report.json" --output "$$reference_alias_keeper_out/review-state"
	@reference_leading_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-reference-leading-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_reference_leading_key_sources.py --output "$$reference_leading_key_out/source" && \
		python3 tests/semantics/string_offset_reference_leading_key_protocol.py --source-report "$$reference_leading_key_out/source/report.json" --output "$$reference_leading_key_out/author-state" && \
		python3 tests/semantics/string_offset_reference_leading_key_review_state.py --source-report "$$reference_leading_key_out/source/report.json" --output "$$reference_leading_key_out/review-state"
	@request_leading_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-leading-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_leading_key_sources.py --output "$$request_leading_key_out/source" && \
		python3 tests/semantics/string_offset_request_leading_key_protocol.py --source-report "$$request_leading_key_out/source/report.json" --output "$$request_leading_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_leading_key_review_state.py --source-report "$$request_leading_key_out/source/report.json" --output "$$request_leading_key_out/review-state"
	@reference_request_leading_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-reference-request-leading-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_reference_request_leading_key_sources.py --output "$$reference_request_leading_key_out/source" && \
		python3 tests/semantics/string_offset_reference_request_leading_key_protocol.py --source-report "$$reference_request_leading_key_out/source/report.json" --output "$$reference_request_leading_key_out/author-state" && \
		python3 tests/semantics/string_offset_reference_request_leading_key_review_state.py --source-report "$$reference_request_leading_key_out/source/report.json" --output "$$reference_request_leading_key_out/review-state"
	@request_leading_base_retainer_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-leading-base-retainer-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_leading_base_retainer_sources.py --output "$$request_leading_base_retainer_out/source" && \
		python3 tests/semantics/string_offset_request_leading_base_retainer_protocol.py --source-report "$$request_leading_base_retainer_out/source/report.json" --output "$$request_leading_base_retainer_out/author-state" && \
		python3 tests/semantics/string_offset_request_leading_base_retainer_review_state.py --source-report "$$request_leading_base_retainer_out/source/report.json" --output "$$request_leading_base_retainer_out/review-state"
	@request_leading_matrix_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-leading-carrier-matrix-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_leading_carrier_matrix_sources.py --output "$$request_leading_matrix_out/source" && \
		python3 tests/semantics/string_offset_request_leading_carrier_matrix_protocol.py --source-report "$$request_leading_matrix_out/source/report.json" --output "$$request_leading_matrix_out/author-state" && \
		python3 tests/semantics/string_offset_request_leading_carrier_matrix_review_state.py --source-report "$$request_leading_matrix_out/source/report.json" --output "$$request_leading_matrix_out/review-state"
	@request_literal_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-base-literal-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_base_literal_leading_key_sources.py --output "$$request_literal_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_literal_leading_key_protocol.py --source-report "$$request_literal_key_out/source/report.json" --output "$$request_literal_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_literal_leading_key_review_state.py --source-report "$$request_literal_key_out/source/report.json" --output "$$request_literal_key_out/review-state"
	@request_concat_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-base-concat-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_base_concat_leading_key_sources.py --output "$$request_concat_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_concat_leading_key_protocol.py --source-report "$$request_concat_key_out/source/report.json" --output "$$request_concat_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_concat_leading_key_review_state.py --source-report "$$request_concat_key_out/source/report.json" --output "$$request_concat_key_out/review-state"
	@request_numeric_concat_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-base-numeric-concat-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_base_numeric_concat_leading_key_sources.py --output "$$request_numeric_concat_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_numeric_concat_leading_key_protocol.py --source-report "$$request_numeric_concat_key_out/source/report.json" --output "$$request_numeric_concat_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_numeric_concat_leading_key_review_state.py --source-report "$$request_numeric_concat_key_out/source/report.json" --output "$$request_numeric_concat_key_out/review-state"
	@request_special_concat_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-base-special-concat-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_base_special_concat_leading_key_sources.py --output "$$request_special_concat_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_special_concat_leading_key_protocol.py --source-report "$$request_special_concat_key_out/source/report.json" --output "$$request_special_concat_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_special_concat_leading_key_review_state.py --source-report "$$request_special_concat_key_out/source/report.json" --output "$$request_special_concat_key_out/review-state"
	@request_integer_special_key_out="$$(mktemp -d "$(CURDIR)/.tools/string-offset-request-base-integer-special-key-test-XXXXXX")" && \
		python3 tests/semantics/string_offset_request_base_integer_special_concat_leading_key_sources.py --output "$$request_integer_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_special_concat_leading_key_protocol.py --source-report "$$request_integer_special_key_out/source/report.json" --output "$$request_integer_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_special_concat_leading_key_review_state.py --source-report "$$request_integer_special_key_out/source/report.json" --output "$$request_integer_special_key_out/review-state"
	@request_float_special_key_out=$$(mktemp -d .tools/float-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_float_special_concat_leading_key_sources.py --output "$$request_float_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_float_special_concat_leading_key_protocol.py --source-report "$$request_float_special_key_out/source/report.json" --output "$$request_float_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_float_special_concat_leading_key_review_state.py --source-report "$$request_float_special_key_out/source/report.json" --output "$$request_float_special_key_out/review-state"
	@request_unary_numeric_special_key_out=$$(mktemp -d .tools/unary-numeric-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_unary_numeric_special_concat_leading_key_sources.py --output "$$request_unary_numeric_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_unary_numeric_special_concat_leading_key_protocol.py --source-report "$$request_unary_numeric_special_key_out/source/report.json" --output "$$request_unary_numeric_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_unary_numeric_special_concat_leading_key_review_state.py --source-report "$$request_unary_numeric_special_key_out/source/report.json" --output "$$request_unary_numeric_special_key_out/review-state"
	@request_nested_unary_numeric_special_key_out=$$(mktemp -d .tools/nested-unary-numeric-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_nested_unary_numeric_special_concat_leading_key_sources.py --output "$$request_nested_unary_numeric_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_nested_unary_numeric_special_concat_leading_key_protocol.py --source-report "$$request_nested_unary_numeric_special_key_out/source/report.json" --output "$$request_nested_unary_numeric_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_nested_unary_numeric_special_concat_leading_key_review_state.py --source-report "$$request_nested_unary_numeric_special_key_out/source/report.json" --output "$$request_nested_unary_numeric_special_key_out/review-state"
	@request_numeric_string_unary_special_key_out=$$(mktemp -d .tools/numeric-string-unary-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_numeric_string_unary_special_concat_leading_key_sources.py --output "$$request_numeric_string_unary_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_numeric_string_unary_special_concat_leading_key_protocol.py --source-report "$$request_numeric_string_unary_special_key_out/source/report.json" --output "$$request_numeric_string_unary_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_numeric_string_unary_special_concat_leading_key_review_state.py --source-report "$$request_numeric_string_unary_special_key_out/source/report.json" --output "$$request_numeric_string_unary_special_key_out/review-state"
	@request_integer_const_special_key_out=$$(mktemp -d .tools/integer-const-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_const_special_concat_leading_key_sources.py --output "$$request_integer_const_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_const_special_concat_leading_key_protocol.py --source-report "$$request_integer_const_special_key_out/source/report.json" --output "$$request_integer_const_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_const_special_concat_leading_key_review_state.py --source-report "$$request_integer_const_special_key_out/source/report.json" --output "$$request_integer_const_special_key_out/review-state"
	@request_arithmetic_special_key_out=$$(mktemp -d .tools/arithmetic-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_arithmetic_special_concat_leading_key_sources.py --output "$$request_arithmetic_special_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_arithmetic_special_concat_leading_key_protocol.py --source-report "$$request_arithmetic_special_key_out/source/report.json" --output "$$request_arithmetic_special_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_arithmetic_special_concat_leading_key_review_state.py --source-report "$$request_arithmetic_special_key_out/source/report.json" --output "$$request_arithmetic_special_key_out/review-state"
	@request_unary_const_arithmetic_key_out=$$(mktemp -d .tools/unary-const-arithmetic-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_unary_const_arithmetic_special_concat_leading_key_sources.py --output "$$request_unary_const_arithmetic_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_unary_const_arithmetic_special_concat_leading_key_protocol.py --sl --source-report "$$request_unary_const_arithmetic_key_out/source/report.json" --output "$$request_unary_const_arithmetic_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_unary_const_arithmetic_special_concat_leading_key_review_state.py --sl --source-report "$$request_unary_const_arithmetic_key_out/source/report.json" --output "$$request_unary_const_arithmetic_key_out/review-state"
	@request_bool_null_unary_key_out=$$(mktemp -d .tools/bool-null-unary-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_bool_null_unary_special_concat_leading_key_sources.py --output "$$request_bool_null_unary_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol.py --sl --source-report "$$request_bool_null_unary_key_out/source/report.json" --output "$$request_bool_null_unary_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state.py --sl --source-report "$$request_bool_null_unary_key_out/source/report.json" --output "$$request_bool_null_unary_key_out/review-state"
	@request_numeric_concat_unary_key_out=$$(mktemp -d .tools/numeric-concat-unary-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_sources.py --output "$$request_numeric_concat_unary_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_protocol.py --sl --source-report "$$request_numeric_concat_unary_key_out/source/report.json" --output "$$request_numeric_concat_unary_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_review_state.py --sl --source-report "$$request_numeric_concat_unary_key_out/source/report.json" --output "$$request_numeric_concat_unary_key_out/review-state"
	@request_boolnot_key_out=$$(mktemp -d .tools/boolnot-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_boolnot_special_concat_leading_key_sources.py --output "$$request_boolnot_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_boolnot_special_concat_leading_key_protocol.py --sl --source-report "$$request_boolnot_key_out/source/report.json" --output "$$request_boolnot_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_boolnot_special_concat_leading_key_review_state.py --sl --source-report "$$request_boolnot_key_out/source/report.json" --output "$$request_boolnot_key_out/review-state"
	@request_identity_key_out=$$(mktemp -d .tools/identity-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_identity_special_concat_leading_key_sources.py --output "$$request_identity_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_identity_special_concat_leading_key_protocol.py --sl --source-report "$$request_identity_key_out/source/report.json" --output "$$request_identity_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_identity_special_concat_leading_key_review_state.py --sl --source-report "$$request_identity_key_out/source/report.json" --output "$$request_identity_key_out/review-state"
	@request_xor_key_out=$$(mktemp -d .tools/xor-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_xor_special_concat_leading_key_sources.py --output "$$request_xor_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_xor_special_concat_leading_key_protocol.py --sl --source-report "$$request_xor_key_out/source/report.json" --output "$$request_xor_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_xor_special_concat_leading_key_review_state.py --sl --source-report "$$request_xor_key_out/source/report.json" --output "$$request_xor_key_out/review-state"
	@request_relational_key_out=$$(mktemp -d .tools/integer-relational-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_relational_special_concat_leading_key_sources.py --output "$$request_relational_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_relational_special_concat_leading_key_protocol.py --sl --source-report "$$request_relational_key_out/source/report.json" --output "$$request_relational_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_relational_special_concat_leading_key_review_state.py --sl --source-report "$$request_relational_key_out/source/report.json" --output "$$request_relational_key_out/review-state"
	@request_bitnot_key_out=$$(mktemp -d .tools/integer-bitnot-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_bitnot_special_concat_leading_key_sources.py --output "$$request_bitnot_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_bitnot_special_concat_leading_key_protocol.py --sl --source-report "$$request_bitnot_key_out/source/report.json" --output "$$request_bitnot_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_bitnot_special_concat_leading_key_review_state.py --sl --source-report "$$request_bitnot_key_out/source/report.json" --output "$$request_bitnot_key_out/review-state"
	@request_bitwise_key_out=$$(mktemp -d .tools/integer-bitwise-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_bitwise_special_concat_leading_key_sources.py --output "$$request_bitwise_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_bitwise_special_concat_leading_key_protocol.py --sl --source-report "$$request_bitwise_key_out/source/report.json" --output "$$request_bitwise_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_bitwise_special_concat_leading_key_review_state.py --sl --source-report "$$request_bitwise_key_out/source/report.json" --output "$$request_bitwise_key_out/review-state"
	@request_modulo_key_out=$$(mktemp -d .tools/integer-modulo-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_modulo_special_concat_leading_key_sources.py --output "$$request_modulo_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_modulo_special_concat_leading_key_protocol.py --sl --source-report "$$request_modulo_key_out/source/report.json" --output "$$request_modulo_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_modulo_special_concat_leading_key_review_state.py --sl --source-report "$$request_modulo_key_out/source/report.json" --output "$$request_modulo_key_out/review-state"
	@request_shift_key_out=$$(mktemp -d .tools/integer-shift-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_shift_special_concat_leading_key_sources.py --output "$$request_shift_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_shift_special_concat_leading_key_protocol.py --sl --source-report "$$request_shift_key_out/source/report.json" --output "$$request_shift_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_shift_special_concat_leading_key_review_state.py --sl --source-report "$$request_shift_key_out/source/report.json" --output "$$request_shift_key_out/review-state"
	@request_equality_key_out=$$(mktemp -d .tools/integer-equality-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_equality_special_concat_leading_key_sources.py --output "$$request_equality_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_equality_special_concat_leading_key_protocol.py --sl --source-report "$$request_equality_key_out/source/report.json" --output "$$request_equality_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_equality_special_concat_leading_key_review_state.py --sl --source-report "$$request_equality_key_out/source/report.json" --output "$$request_equality_key_out/review-state"
	@request_short_key_out=$$(mktemp -d .tools/short-circuit-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_short_circuit_special_concat_leading_key_sources.py --output "$$request_short_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_short_circuit_special_concat_leading_key_protocol.py --sl --source-report "$$request_short_key_out/source/report.json" --output "$$request_short_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_short_circuit_special_concat_leading_key_review_state.py --sl --source-report "$$request_short_key_out/source/report.json" --output "$$request_short_key_out/review-state"
	@request_power_key_out=$$(mktemp -d .tools/integer-power-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_integer_power_special_concat_leading_key_sources.py --output "$$request_power_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_integer_power_special_concat_leading_key_protocol.py --sl --source-report "$$request_power_key_out/source/report.json" --output "$$request_power_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_integer_power_special_concat_leading_key_review_state.py --sl --source-report "$$request_power_key_out/source/report.json" --output "$$request_power_key_out/review-state"
	@request_byte_key_out=$$(mktemp -d .tools/string-bitwise-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_string_bitwise_special_concat_leading_key_sources.py --output "$$request_byte_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_string_bitwise_special_concat_leading_key_protocol.py --sl --source-report "$$request_byte_key_out/source/report.json" --output "$$request_byte_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_string_bitwise_special_concat_leading_key_review_state.py --sl --source-report "$$request_byte_key_out/source/report.json" --output "$$request_byte_key_out/review-state"
	@request_numeric_cmp_key_out=$$(mktemp -d .tools/numeric-comparison-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_numeric_comparison_special_concat_leading_key_sources.py --output "$$request_numeric_cmp_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol.py --sl --source-report "$$request_numeric_cmp_key_out/source/report.json" --output "$$request_numeric_cmp_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state.py --sl --source-report "$$request_numeric_cmp_key_out/source/report.json" --output "$$request_numeric_cmp_key_out/review-state"
	@request_nan_cmp_key_out=$$(mktemp -d .tools/nan-comparison-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_nan_comparison_special_concat_leading_key_sources.py --output "$$request_nan_cmp_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_nan_comparison_special_concat_leading_key_protocol.py --sl --source-report "$$request_nan_cmp_key_out/source/report.json" --output "$$request_nan_cmp_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_nan_comparison_special_concat_leading_key_review_state.py --sl --source-report "$$request_nan_cmp_key_out/source/report.json" --output "$$request_nan_cmp_key_out/review-state"
	@request_float_logical_key_out=$$(mktemp -d .tools/float-logical-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_float_logical_special_concat_leading_key_sources.py --output "$$request_float_logical_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_float_logical_special_concat_leading_key_protocol.py --sl --source-report "$$request_float_logical_key_out/source/report.json" --output "$$request_float_logical_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_float_logical_special_concat_leading_key_review_state.py --sl --source-report "$$request_float_logical_key_out/source/report.json" --output "$$request_float_logical_key_out/review-state"
	@request_string_cmp_key_out=$$(mktemp -d .tools/string-comparison-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_string_comparison_special_concat_leading_key_sources.py --output "$$request_string_cmp_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_string_comparison_special_concat_leading_key_protocol.py --sl --source-report "$$request_string_cmp_key_out/source/report.json" --output "$$request_string_cmp_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_string_comparison_special_concat_leading_key_review_state.py --sl --source-report "$$request_string_cmp_key_out/source/report.json" --output "$$request_string_cmp_key_out/review-state"
	@request_mixed_cmp_key_out=$$(mktemp -d .tools/number-string-comparison-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_number_string_comparison_special_concat_leading_key_sources.py --output "$$request_mixed_cmp_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_number_string_comparison_special_concat_leading_key_protocol.py --sl --source-report "$$request_mixed_cmp_key_out/source/report.json" --output "$$request_mixed_cmp_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_number_string_comparison_special_concat_leading_key_review_state.py --sl --source-report "$$request_mixed_cmp_key_out/source/report.json" --output "$$request_mixed_cmp_key_out/review-state"
	@request_bool_cmp_key_out=$$(mktemp -d .tools/bool-null-comparison-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_bool_null_comparison_special_concat_leading_key_sources.py --output "$$request_bool_cmp_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_bool_null_comparison_special_concat_leading_key_protocol.py --sl --source-report "$$request_bool_cmp_key_out/source/report.json" --output "$$request_bool_cmp_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_bool_null_comparison_special_concat_leading_key_review_state.py --sl --source-report "$$request_bool_cmp_key_out/source/report.json" --output "$$request_bool_cmp_key_out/review-state"
	@request_nan_scalar_key_out=$$(mktemp -d .tools/nan-scalar-comparison-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_nan_scalar_comparison_special_concat_leading_key_sources.py --output "$$request_nan_scalar_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_nan_scalar_comparison_special_concat_leading_key_protocol.py --sl --source-report "$$request_nan_scalar_key_out/source/report.json" --output "$$request_nan_scalar_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_nan_scalar_comparison_special_concat_leading_key_review_state.py --sl --source-report "$$request_nan_scalar_key_out/source/report.json" --output "$$request_nan_scalar_key_out/review-state"
	@request_nan_identity_key_out=$$(mktemp -d .tools/nan-identity-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_nan_identity_special_concat_leading_key_sources.py --output "$$request_nan_identity_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_nan_identity_special_concat_leading_key_protocol.py --sl --source-report "$$request_nan_identity_key_out/source/report.json" --output "$$request_nan_identity_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_nan_identity_special_concat_leading_key_review_state.py --sl --source-report "$$request_nan_identity_key_out/source/report.json" --output "$$request_nan_identity_key_out/review-state"
	@request_float_const_key_out=$$(mktemp -d .tools/float-const-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_float_const_special_concat_leading_key_sources.py --output "$$request_float_const_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_float_const_special_concat_leading_key_protocol.py --sl --source-report "$$request_float_const_key_out/source/report.json" --output "$$request_float_const_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_float_const_special_concat_leading_key_review_state.py --sl --source-report "$$request_float_const_key_out/source/report.json" --output "$$request_float_const_key_out/review-state"
	@request_arithmetic_nan_key_out=$$(mktemp -d .tools/arithmetic-nan-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_arithmetic_nan_special_concat_leading_key_sources.py --output "$$request_arithmetic_nan_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_arithmetic_nan_special_concat_leading_key_protocol.py --sl --source-report "$$request_arithmetic_nan_key_out/source/report.json" --output "$$request_arithmetic_nan_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_arithmetic_nan_special_concat_leading_key_review_state.py --sl --source-report "$$request_arithmetic_nan_key_out/source/report.json" --output "$$request_arithmetic_nan_key_out/review-state"
	@request_unary_nan_key_out=$$(mktemp -d .tools/unary-nan-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_unary_nan_special_concat_leading_key_sources.py --output "$$request_unary_nan_key_out/source" && \
		python3 tests/semantics/string_offset_request_base_unary_nan_special_concat_leading_key_protocol.py --sl --source-report "$$request_unary_nan_key_out/source/report.json" --output "$$request_unary_nan_key_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_unary_nan_special_concat_leading_key_review_state.py --sl --source-report "$$request_unary_nan_key_out/source/report.json" --output "$$request_unary_nan_key_out/review-state"
	@request_nan_child_arithmetic_out=$$(mktemp -d .tools/nan-child-arithmetic-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_sources.py --output "$$request_nan_child_arithmetic_out/source" && \
		python3 tests/semantics/string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_protocol.py --sl --source-report "$$request_nan_child_arithmetic_out/source/report.json" --output "$$request_nan_child_arithmetic_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_review_state.py --sl --source-report "$$request_nan_child_arithmetic_out/source/report.json" --output "$$request_nan_child_arithmetic_out/review-state"
	@request_coercive_arithmetic_nan_out=$$(mktemp -d .tools/coercive-arithmetic-nan-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_coercive_arithmetic_nan_special_concat_leading_key_sources.py --output "$$request_coercive_arithmetic_nan_out/source" && \
		python3 tests/semantics/string_offset_request_base_coercive_arithmetic_nan_special_concat_leading_key_protocol.py --sl --source-report "$$request_coercive_arithmetic_nan_out/source/report.json" --output "$$request_coercive_arithmetic_nan_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_coercive_arithmetic_nan_special_concat_leading_key_review_state.py --sl --source-report "$$request_coercive_arithmetic_nan_out/source/report.json" --output "$$request_coercive_arithmetic_nan_out/review-state"
	@request_power_nan_out=$$(mktemp -d .tools/power-nan-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_power_nan_special_concat_leading_key_sources.py --output "$$request_power_nan_out/source" && \
		python3 tests/semantics/string_offset_request_base_power_nan_special_concat_leading_key_protocol.py --sl --source-report "$$request_power_nan_out/source/report.json" --output "$$request_power_nan_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_power_nan_special_concat_leading_key_review_state.py --sl --source-report "$$request_power_nan_out/source/report.json" --output "$$request_power_nan_out/review-state"
	@request_power_float_out=$$(mktemp -d .tools/power-float-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_power_float_special_concat_leading_key_sources.py --output "$$request_power_float_out/source" && \
		python3 tests/semantics/string_offset_request_base_power_float_special_concat_leading_key_protocol.py --sl --source-report "$$request_power_float_out/source/report.json" --output "$$request_power_float_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_power_float_special_concat_leading_key_review_state.py --sl --source-report "$$request_power_float_out/source/report.json" --output "$$request_power_float_out/review-state"
	@request_coercive_integer_power_out=$$(mktemp -d .tools/coercive-integer-power-special-concat-key-XXXXXX); \
		python3 tests/semantics/string_offset_request_base_coercive_integer_power_special_concat_leading_key_sources.py --output "$$request_coercive_integer_power_out/source" && \
		python3 tests/semantics/string_offset_request_base_coercive_integer_power_special_concat_leading_key_protocol.py --sl --source-report "$$request_coercive_integer_power_out/source/report.json" --output "$$request_coercive_integer_power_out/author-state" && \
		python3 tests/semantics/string_offset_request_base_coercive_integer_power_special_concat_leading_key_review_state.py --sl --source-report "$$request_coercive_integer_power_out/source/report.json" --output "$$request_coercive_integer_power_out/review-state"
	@request_float_boolnot_out=$$(mktemp -d .tools/float-boolnot-runtime-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_float_boolnot_special_concat_leading_key_sources.py --output "$$request_float_boolnot_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_float_boolnot_special_concat_leading_key_protocol.py --sl --source-report "$$request_float_boolnot_out/source/report.json" --output "$$request_float_boolnot_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_float_boolnot_special_concat_leading_key_review_state.py --sl --source-report "$$request_float_boolnot_out/source/report.json" --output "$$request_float_boolnot_out/review-state"
	@request_nested_float_boolnot_out=$$(mktemp -d .tools/nested-float-boolnot-runtime-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_nested_float_boolnot_special_concat_leading_key_sources.py --output "$$request_nested_float_boolnot_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_nested_float_boolnot_special_concat_leading_key_protocol.py --sl --source-report "$$request_nested_float_boolnot_out/source/report.json" --output "$$request_nested_float_boolnot_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_nested_float_boolnot_special_concat_leading_key_review_state.py --sl --source-report "$$request_nested_float_boolnot_out/source/report.json" --output "$$request_nested_float_boolnot_out/review-state"
	@request_runtime_unary_integer_out=$$(mktemp -d .tools/runtime-unary-integer-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_unary_integer_special_concat_leading_key_sources.py --output "$$request_runtime_unary_integer_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_unary_integer_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_unary_integer_out/source/report.json" --output "$$request_runtime_unary_integer_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_unary_integer_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_unary_integer_out/source/report.json" --output "$$request_runtime_unary_integer_out/review-state"
	@request_runtime_integer_operator_out=$$(mktemp -d .tools/runtime-integer-operator-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_operator_special_concat_leading_key_sources.py --output "$$request_runtime_integer_operator_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_integer_operator_out/source/report.json" --output "$$request_runtime_integer_operator_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_operator_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_integer_operator_out/source/report.json" --output "$$request_runtime_integer_operator_out/review-state"
	@request_runtime_integer_binary_out=$$(mktemp -d .tools/runtime-integer-binary-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_binary_special_concat_leading_key_sources.py --output "$$request_runtime_integer_binary_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_binary_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_integer_binary_out/source/report.json" --output "$$request_runtime_integer_binary_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_binary_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_integer_binary_out/source/report.json" --output "$$request_runtime_integer_binary_out/review-state"
	@request_runtime_integer_division_out=$$(mktemp -d .tools/runtime-integer-division-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_division_special_concat_leading_key_sources.py --output "$$request_runtime_integer_division_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_division_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_integer_division_out/source/report.json" --output "$$request_runtime_integer_division_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_integer_division_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_integer_division_out/source/report.json" --output "$$request_runtime_integer_division_out/review-state"
	@request_runtime_identity_out=$$(mktemp -d .tools/runtime-identity-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_identity_special_concat_leading_key_sources.py --output "$$request_runtime_identity_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_identity_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_identity_out/source/report.json" --output "$$request_runtime_identity_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_identity_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_identity_out/source/report.json" --output "$$request_runtime_identity_out/review-state"
	@request_runtime_equality_out=$$(mktemp -d .tools/runtime-equality-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_equality_special_concat_leading_key_sources.py --output "$$request_runtime_equality_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_equality_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_equality_out/source/report.json" --output "$$request_runtime_equality_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_equality_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_equality_out/source/report.json" --output "$$request_runtime_equality_out/review-state"
	@request_runtime_order_out=$$(mktemp -d .tools/runtime-order-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_order_special_concat_leading_key_sources.py --output "$$request_runtime_order_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_order_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_order_out/source/report.json" --output "$$request_runtime_order_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_order_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_order_out/source/report.json" --output "$$request_runtime_order_out/review-state"
	@request_runtime_xor_out=$$(mktemp -d .tools/runtime-xor-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_xor_special_concat_leading_key_sources.py --output "$$request_runtime_xor_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_xor_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_xor_out/source/report.json" --output "$$request_runtime_xor_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_xor_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_xor_out/source/report.json" --output "$$request_runtime_xor_out/review-state"
	@request_runtime_short_out=$$(mktemp -d .tools/runtime-short-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_short_special_concat_leading_key_sources.py --output "$$request_runtime_short_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_short_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_short_out/source/report.json" --output "$$request_runtime_short_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_short_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_short_out/source/report.json" --output "$$request_runtime_short_out/review-state"
	@request_runtime_float_arithmetic_out=$$(mktemp -d .tools/runtime-float-arithmetic-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_sources.py --output "$$request_runtime_float_arithmetic_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_float_arithmetic_out/source/report.json" --output "$$request_runtime_float_arithmetic_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_float_arithmetic_out/source/report.json" --output "$$request_runtime_float_arithmetic_out/review-state"
	@request_runtime_float_unary_out=$$(mktemp -d .tools/runtime-float-unary-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_float_unary_special_concat_leading_key_sources.py --output "$$request_runtime_float_unary_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_float_unary_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_float_unary_out/source/report.json" --output "$$request_runtime_float_unary_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_float_unary_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_float_unary_out/source/report.json" --output "$$request_runtime_float_unary_out/review-state"
	@request_runtime_scalar_cast_out=$$(mktemp -d .tools/runtime-scalar-cast-key-XXXXXX); \
		python3 -B tests/semantics/string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_sources.py --output "$$request_runtime_scalar_cast_out/source" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_protocol.py --sl --source-report "$$request_runtime_scalar_cast_out/source/report.json" --output "$$request_runtime_scalar_cast_out/author-state" && \
		python3 -B tests/semantics/string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_review_state.py --sl --source-report "$$request_runtime_scalar_cast_out/source/report.json" --output "$$request_runtime_scalar_cast_out/review-state"
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
	python3 tests/semantics/supplied_integer_reception.py
	python3 tests/semantics/supplied_integer_reception_protocol.py
	python3 tests/semantics/supplied_reference_integer_reception.py
	python3 tests/semantics/supplied_reference_integer_reception_protocol.py
	python3 tests/semantics/supplied_positional_integer_reception.py
	python3 tests/semantics/supplied_positional_integer_reception_protocol.py
	python3 tests/semantics/supplied_positional_reference_integer_reception.py
	python3 tests/semantics/supplied_positional_reference_integer_reception_protocol.py
	python3 tests/semantics/supplied_mixed_integer_reception.py
	python3 tests/semantics/supplied_mixed_integer_reception_protocol.py
	python3 tests/semantics/supplied_named_mixed_integer_reception.py
	python3 tests/semantics/supplied_named_mixed_integer_reception_protocol.py
	python3 tests/semantics/optional_integer_tail_reception.py
	python3 tests/semantics/optional_integer_tail_reception_protocol.py
	python3 tests/semantics/optional_integer_tail_reception_review_protocol.py
	python3 tests/semantics/homogeneous_optional_integer_reception.py
	python3 tests/semantics/homogeneous_optional_integer_reception_protocol.py
	python3 tests/semantics/homogeneous_optional_integer_reception_review_protocol.py
	python3 tests/semantics/homogeneous_named_required_integer_reception.py
	python3 tests/semantics/homogeneous_named_required_integer_reception_protocol.py
	python3 tests/semantics/homogeneous_named_required_integer_reception_review_protocol.py
	python3 tests/semantics/all_optional_integer_reception.py
	python3 tests/semantics/all_optional_integer_reception_protocol.py
	python3 tests/semantics/all_optional_integer_reception_review_protocol.py
	python3 tests/semantics/mixed_cv_integer_reception.py
	python3 tests/semantics/mixed_cv_integer_reception_protocol.py
	python3 tests/semantics/mixed_cv_integer_reception_review_protocol.py
	python3 tests/semantics/signed_integer_default_reception.py
	python3 tests/semantics/signed_integer_default_reception_protocol.py
	python3 tests/semantics/signed_integer_default_reception_review_protocol.py
	python3 tests/semantics/binary_integer_default_reception.py
	python3 tests/semantics/binary_integer_default_reception_protocol.py
	python3 tests/semantics/binary_integer_default_reception_review_protocol.py
	python3 tests/semantics/additive_integer_default_reception.py
	python3 tests/semantics/additive_integer_default_reception_protocol.py
	python3 tests/semantics/additive_integer_default_reception_review_protocol.py
	python3 tests/semantics/product_integer_default_reception.py
	python3 tests/semantics/product_integer_default_reception_protocol.py
	python3 tests/semantics/product_integer_default_reception_review_protocol.py
	python3 tests/semantics/division_integer_default_reception.py
	python3 tests/semantics/division_integer_default_reception_protocol.py
	python3 tests/semantics/division_integer_default_reception_review_protocol.py
	python3 tests/semantics/integer_operator_default_reception.py
	python3 tests/semantics/integer_operator_default_reception_protocol.py
	python3 tests/semantics/integer_operator_default_reception_review_protocol.py
	python3 tests/semantics/power_integer_default_reception.py
	python3 tests/semantics/power_integer_default_reception_protocol.py
	python3 tests/semantics/power_integer_default_reception_review_protocol.py
	python3 tests/semantics/integer_selection_default_reception.py
	python3 tests/semantics/integer_selection_default_reception_protocol.py
	python3 tests/semantics/integer_selection_default_reception_review_protocol.py
	python3 tests/semantics/boolean_condition_default_reception.py
	python3 tests/semantics/boolean_condition_default_reception_protocol.py
	python3 tests/semantics/boolean_condition_default_reception_review_protocol.py
	python3 tests/semantics/comparison_integer_default_reception.py
	python3 tests/semantics/comparison_integer_default_reception_protocol.py
	python3 tests/semantics/comparison_integer_default_reception_review_protocol.py
	python3 tests/semantics/scalar_integer_cast_default_reception.py
	python3 tests/semantics/scalar_integer_cast_default_reception_protocol.py
	python3 tests/semantics/scalar_integer_cast_default_reception_review_protocol.py
	python3 tests/semantics/boolean_integer_cast_default_reception.py
	python3 tests/semantics/boolean_integer_cast_default_reception_protocol.py
	python3 tests/semantics/boolean_integer_cast_default_reception_review_protocol.py
	python3 tests/semantics/selection_integer_cast_default_reception.py
	python3 tests/semantics/selection_integer_cast_default_reception_protocol.py
	python3 tests/semantics/selection_integer_cast_default_reception_review_protocol.py
	python3 tests/semantics/scalar_truth_default_reception.py
	python3 tests/semantics/scalar_truth_default_reception_protocol.py
	python3 tests/semantics/scalar_truth_default_reception_review_protocol.py
	python3 tests/semantics/boolean_cast_default_reception.py
	python3 tests/semantics/boolean_cast_default_reception_protocol.py
	python3 tests/semantics/boolean_cast_default_reception_review_protocol.py
	python3 tests/semantics/ternary_truth_default_reception.py
	python3 tests/semantics/ternary_truth_default_reception_protocol.py
	python3 tests/semantics/ternary_truth_default_reception_review_protocol.py
	python3 tests/semantics/coalesce_truth_default_reception.py
	python3 tests/semantics/coalesce_truth_default_reception_protocol.py
	python3 tests/semantics/coalesce_truth_default_reception_review_protocol.py
	python3 tests/semantics/float_cast_truth_default_reception.py
	python3 tests/semantics/float_cast_truth_default_reception_protocol.py
	python3 tests/semantics/float_cast_truth_default_reception_review_protocol.py
	python3 tests/semantics/concat_string_default_reception.py
	python3 tests/semantics/concat_string_default_reception_protocol.py
	python3 tests/semantics/concat_string_default_reception_review_protocol.py
	python3 tests/semantics/bitnot_string_default_reception.py
	python3 tests/semantics/bitnot_string_default_reception_protocol.py
	python3 tests/semantics/bitnot_string_default_reception_review_protocol.py
	python3 tests/semantics/bitwise_string_default_reception.py
	python3 tests/semantics/bitwise_string_default_reception_protocol.py
	python3 tests/semantics/bitwise_string_default_reception_review_protocol.py
	python3 tests/semantics/index_string_default_reception.py
	python3 tests/semantics/index_string_default_reception_protocol.py
	python3 tests/semantics/index_string_default_reception_review_protocol.py
	python3 tests/semantics/string_selector_default_reception.py
	python3 tests/semantics/string_selector_default_reception_protocol.py
	python3 tests/semantics/string_selector_default_reception_review_protocol.py
	python3 tests/semantics/integer_string_cast_default_reception.py
	python3 tests/semantics/integer_string_cast_default_reception_protocol.py
	python3 tests/semantics/integer_string_cast_default_reception_review_protocol.py
	python3 tests/semantics/contextual_string_cast_default_reception.py
	python3 tests/semantics/contextual_string_cast_default_reception_protocol.py
	python3 tests/semantics/contextual_string_cast_default_reception_review_protocol.py
	python3 tests/semantics/computed_index_string_default_reception.py
	python3 tests/semantics/computed_index_string_default_reception_protocol.py
	python3 tests/semantics/computed_index_string_default_reception_review_protocol.py
	python3 tests/semantics/selection_string_cast_default_reception.py
	python3 tests/semantics/selection_string_cast_default_reception_protocol.py
	python3 tests/semantics/selection_string_cast_default_reception_review_protocol.py
	python3 tests/semantics/computed_float_integer_cast_default_reception.py
	python3 tests/semantics/computed_float_integer_cast_default_reception_protocol.py
	python3 tests/semantics/computed_float_integer_cast_default_reception_review_protocol.py
	python3 tests/semantics/unary_computed_float_integer_cast_default_reception.py
	python3 tests/semantics/unary_computed_float_integer_cast_default_reception_protocol.py
	python3 tests/semantics/unary_computed_float_integer_cast_default_reception_review_protocol.py
	python3 tests/semantics/computed_float_truth_default_reception.py
	python3 tests/semantics/computed_float_truth_default_reception_protocol.py
	python3 tests/semantics/computed_float_truth_default_reception_review_protocol.py
	python3 tests/semantics/selected_float_numeric_default_reception.py
	python3 tests/semantics/selected_float_numeric_default_reception_protocol.py
	python3 tests/semantics/selected_float_numeric_default_reception_review_protocol.py
	python3 tests/semantics/numeric_float_cast_default_reception.py
	python3 tests/semantics/numeric_float_cast_default_reception_protocol.py
	python3 tests/semantics/numeric_float_cast_default_reception_review_protocol.py
	python3 tests/semantics/scalar_float_cast_default_reception.py
	python3 tests/semantics/scalar_float_cast_default_reception_protocol.py
	python3 tests/semantics/scalar_float_cast_default_reception_review_protocol.py
	python3 tests/semantics/selected_scalar_float_cast_default_reception.py
	python3 tests/semantics/selected_scalar_float_cast_default_reception_protocol.py
	python3 tests/semantics/selected_scalar_float_cast_default_reception_review_protocol.py
	python3 tests/semantics/numeric_comparison_default_reception.py
	python3 tests/semantics/numeric_comparison_default_reception_protocol.py
	python3 tests/semantics/numeric_comparison_default_reception_review_protocol.py
	python3 tests/semantics/builtin_float_constant_default_reception.py
	python3 tests/semantics/builtin_float_constant_default_reception_protocol.py
	python3 tests/semantics/builtin_float_constant_default_reception_review_protocol.py
	python3 tests/semantics/deferred_float_default_type_error_reception.py
	python3 tests/semantics/deferred_float_default_type_error_reception_protocol.py
	python3 tests/semantics/deferred_float_default_type_error_reception_review_protocol.py
	python3 tests/semantics/quiet_fitting_float_default_reception.py
	python3 tests/semantics/quiet_fitting_float_default_reception_protocol.py
	python3 tests/semantics/quiet_fitting_float_default_reception_review_protocol.py
	python3 tests/semantics/fractional_float_default_reception.py
	python3 tests/semantics/fractional_float_default_reception_protocol.py
	python3 tests/semantics/fractional_float_default_reception_review_protocol.py
	python3 tests/semantics/immutable_integer_default_reception.py
	python3 tests/semantics/immutable_integer_default_reception_protocol.py
	python3 tests/semantics/immutable_integer_default_reception_review_protocol.py
	python3 tests/semantics/immutable_integer_truth_default_reception.py
	python3 tests/semantics/immutable_integer_truth_default_reception_protocol.py
	python3 tests/semantics/immutable_integer_truth_default_reception_review_protocol.py
	python3 tests/semantics/selected_integer_default_reception.py
	python3 tests/semantics/selected_integer_default_reception_protocol.py
	python3 tests/semantics/selected_integer_default_reception_review_protocol.py
	python3 tests/semantics/folded_boolean_ternary_default_reception.py
	python3 tests/semantics/folded_boolean_ternary_default_reception_protocol.py
	python3 tests/semantics/folded_boolean_ternary_default_reception_review_protocol.py
	python3 tests/semantics/computed_boolean_ternary_default_reception.py
	python3 tests/semantics/computed_boolean_ternary_default_reception_protocol.py
	python3 tests/semantics/computed_boolean_ternary_default_reception_review_protocol.py
	python3 tests/semantics/lazy_boolean_condition_default_reception.py
	python3 tests/semantics/lazy_boolean_condition_default_reception_protocol.py
	python3 tests/semantics/lazy_boolean_condition_default_reception_review_protocol.py
	python3 tests/semantics/float_platform_default_reception.py
	python3 tests/semantics/float_platform_default_reception_protocol.py
	python3 tests/semantics/float_platform_default_reception_review_protocol.py
	python3 tests/semantics/numeric_integer_cast_default_reception.py
	python3 tests/semantics/numeric_integer_cast_default_reception_protocol.py
	python3 tests/semantics/numeric_integer_cast_default_reception_review_protocol.py
	python3 tests/semantics/version_integer_default_reception.py
	python3 tests/semantics/version_integer_default_reception_protocol.py
	python3 tests/semantics/version_integer_default_reception_review_protocol.py
	python3 tests/semantics/diagnostic_integer_default_reception.py
	python3 tests/semantics/diagnostic_integer_default_reception_protocol.py
	python3 tests/semantics/diagnostic_integer_default_reception_review_protocol.py
	python3 tests/semantics/numeric_bitwise_default_reception.py
	python3 tests/semantics/numeric_bitwise_default_reception_protocol.py
	python3 tests/semantics/numeric_bitwise_default_reception_review_protocol.py
	python3 tests/semantics/numeric_integer_operator_default_reception.py
	python3 tests/semantics/numeric_integer_operator_default_reception_protocol.py
	python3 tests/semantics/numeric_integer_operator_default_reception_review_protocol.py
	python3 tests/semantics/numeric_power_default_reception.py
	python3 tests/semantics/numeric_power_default_reception_protocol.py
	python3 tests/semantics/numeric_power_default_reception_review_protocol.py
	python3 tests/semantics/numeric_float_power_default_reception.py
	python3 tests/semantics/numeric_float_power_default_reception_protocol.py
	python3 tests/semantics/numeric_float_power_default_reception_review_protocol.py
	python3 tests/semantics/numeric_general_power_default_reception.py
	python3 tests/semantics/numeric_general_power_default_reception_protocol.py
	python3 tests/semantics/numeric_general_power_default_reception_review_protocol.py
	python3 tests/semantics/numeric_coercive_power_default_reception.py
	python3 tests/semantics/numeric_coercive_power_default_reception_protocol.py
	python3 tests/semantics/numeric_coercive_power_default_reception_review_protocol.py
	python3 tests/semantics/numeric_coercive_arithmetic_default_reception.py
	python3 tests/semantics/numeric_coercive_arithmetic_default_reception_protocol.py
	python3 tests/semantics/numeric_coercive_arithmetic_default_reception_review_protocol.py
	python3 tests/semantics/computed_boolean_operand_default_reception.py
	python3 tests/semantics/computed_boolean_operand_default_reception_protocol.py
	python3 tests/semantics/computed_boolean_operand_default_reception_review_protocol.py
	python3 tests/semantics/callable_returns.py
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
	python3 tests/semantics/fiber_start_aggregate_sources.py
	python3 tests/semantics/fiber_start_aggregate_review.py
	python3 tests/semantics/fiber_start_nested_aggregate_sources.py
	python3 tests/semantics/fiber_start_nested_aggregate_review.py
	python3 tests/semantics/foreach_aggregate_sources.py
	python3 tests/semantics/foreach_aggregate_review.py
	python3 tests/semantics/foreach_valid_nan_sources.py
	python3 tests/semantics/foreach_valid_nan_review.py
	python3 tests/semantics/foreach_rebound_operand_sources.py
	python3 tests/semantics/foreach_rebound_operand_review.py
	python3 tests/semantics/foreach_source_compare_sources.py
	python3 tests/semantics/foreach_source_compare_review.py
	python3 tests/semantics/yield_from_aggregate_sources.py
	python3 tests/semantics/yield_from_aggregate_review.py
	python3 tests/semantics/yield_from_valid_nan_sources.py
	python3 tests/semantics/yield_from_valid_nan_review.py
	python3 tests/semantics/yield_from_rebound_operand_sources.py
	python3 tests/semantics/yield_from_rebound_operand_review.py
	python3 tests/semantics/yield_from_source_compare_sources.py
	python3 tests/semantics/yield_from_source_compare_review.py
	python3 tests/semantics/iterator_call_unpack_sources.py
	python3 tests/semantics/iterator_call_unpack_review.py
	python3 tests/semantics/method_iterator_unpack_sources.py
	python3 tests/semantics/method_iterator_unpack_clean_sources.py
	python3 tests/semantics/method_iterator_unpack_protocol.py
	python3 tests/semantics/owned_iterator_unpack_sources.py
	python3 tests/semantics/owned_iterator_unpack_protocol.py
	python3 tests/semantics/computed_callee_unpack_sources.py
	python3 tests/semantics/computed_callee_unpack_protocol.py
	python3 tests/semantics/magic_iterator_unpack_sources.py
	python3 tests/semantics/magic_iterator_unpack_protocol.py
	python3 tests/semantics/magic_producer_unpack_sources.py
	python3 tests/semantics/magic_producer_unpack_protocol.py
	python3 tests/semantics/aggregate_call_unpack_sources.py
	python3 tests/semantics/aggregate_call_unpack_protocol.py
	python3 tests/semantics/aggregate_call_unpack_review_protocol.py
	python3 tests/semantics/array_callable_iterator_unpack_sources.py
	python3 tests/semantics/array_callable_iterator_unpack_protocol.py
	python3 tests/semantics/closure_iterator_unpack_sources.py
	python3 tests/semantics/closure_iterator_unpack_protocol.py
	python3 tests/semantics/iterator_call_unpack_nan_sources.py
	python3 tests/semantics/iterator_call_unpack_nan_review.py
	python3 tests/semantics/iterator_call_unpack_string_sources.py
	python3 tests/semantics/iterator_call_unpack_string_review.py
	python3 tests/semantics/iterator_call_unpack_interned_ref_sources.py
	python3 tests/semantics/iterator_call_unpack_interned_ref_review.py
	python3 tests/semantics/iterator_call_unpack_object_sources.py
	python3 tests/semantics/iterator_call_unpack_object_review.py
	python3 tests/semantics/iterator_call_unpack_object_sent_sources.py
	python3 tests/semantics/iterator_call_unpack_object_sent_review.py
	python3 tests/semantics/iterator_call_unpack_object_extra_named_sources.py
	python3 tests/semantics/iterator_call_unpack_object_extra_named_review.py
	python3 tests/semantics/iterator_call_unpack_object_extra_extra_sources.py
	python3 tests/semantics/iterator_call_unpack_object_extra_extra_review.py
	python3 tests/semantics/iterator_call_unpack_object_positional_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_object_positional_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_object_typed_positional_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_object_typed_positional_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_object_typed_named_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_object_typed_named_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_array_sources.py
	python3 tests/semantics/iterator_call_unpack_array_review.py
	python3 tests/semantics/iterator_call_unpack_array_sent_sources.py
	python3 tests/semantics/iterator_call_unpack_array_sent_review.py
	python3 tests/semantics/iterator_call_unpack_array_positional_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_array_positional_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_array_typed_positional_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_array_typed_positional_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_array_typed_named_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_array_typed_named_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_array_named_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_array_named_variadic_review.py
	python3 tests/semantics/iterator_call_unpack_reference_object_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_object_review.py
	python3 tests/semantics/iterator_call_unpack_reference_array_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_array_review.py
	python3 tests/semantics/iterator_call_unpack_named_reference_sources.py
	python3 tests/semantics/iterator_call_unpack_named_reference_state.py
	python3 tests/semantics/iterator_call_unpack_named_reference_review_sources.py
	python3 tests/semantics/iterator_call_unpack_named_reference_independent_state.py
	python3 tests/semantics/iterator_call_unpack_later_fixed_reference_sources.py
	python3 tests/semantics/iterator_call_unpack_later_fixed_reference_state.py
	python3 tests/semantics/iterator_call_unpack_reference_holes_review_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_holes_review_state.py
	python3 tests/semantics/iterator_call_unpack_typed_fixed_reference_sources.py
	python3 tests/semantics/iterator_call_unpack_typed_fixed_reference_state.py
	python3 tests/semantics/iterator_call_unpack_typed_reference_review_sources.py
	python3 tests/semantics/iterator_call_unpack_typed_reference_review_state.py
	python3 tests/semantics/iterator_call_unpack_noninitial_fixed_reference_sources.py
	python3 tests/semantics/iterator_call_unpack_noninitial_fixed_reference_state.py
	python3 tests/semantics/iterator_call_unpack_noninitial_reference_review_sources.py
	python3 tests/semantics/iterator_call_unpack_noninitial_reference_review_state.py
	python3 tests/semantics/iterator_call_unpack_noninitial_array_reference_sources.py
	python3 tests/semantics/iterator_call_unpack_noninitial_array_reference_state.py
	python3 tests/semantics/iterator_call_unpack_noninitial_array_review_sources.py
	python3 tests/semantics/iterator_call_unpack_noninitial_array_review_state.py
	python3 tests/semantics/iterator_call_unpack_noninitial_typed_reference_sources.py
	python3 tests/semantics/iterator_call_unpack_noninitial_typed_reference_state.py
	python3 tests/semantics/iterator_call_unpack_noninitial_typed_reference_review_sources.py
	python3 tests/semantics/iterator_call_unpack_noninitial_typed_reference_review_state.py
	python3 tests/semantics/iterator_call_unpack_reference_positional_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_positional_variadic_state.py
	python3 tests/semantics/iterator_call_unpack_reference_positional_variadic_review_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_positional_variadic_review_state.py
	python3 tests/semantics/iterator_call_unpack_reference_typed_positional_variadic_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_typed_positional_variadic_state.py
	python3 tests/semantics/iterator_call_unpack_reference_typed_positional_variadic_review_sources.py
	python3 tests/semantics/iterator_call_unpack_reference_typed_positional_variadic_review_state.py
	python3 tests/semantics/generator_call_unpack_sources.py
	python3 tests/semantics/generator_call_unpack_state.py
	python3 tests/semantics/generator_call_unpack_review_sources.py
	python3 tests/semantics/generator_call_unpack_review_state.py
	python3 tests/semantics/generator_byref_sink_sources.py
	python3 tests/semantics/generator_byref_sink_scalar_sources.py
	python3 tests/semantics/generator_byref_sink_negative_sources.py
	python3 tests/semantics/generator_byref_sink_review_state.py
	python3 tests/semantics/generator_reference_sink_sources.py
	python3 tests/semantics/generator_reference_sink_review_sources.py
	python3 tests/semantics/generator_reference_sink_state.py
	python3 tests/semantics/generator_reference_sink_review_state.py
	python3 tests/semantics/generator_captured_cell_sink_sources.py
	python3 tests/semantics/generator_captured_cell_sink_review_sources.py
	python3 tests/semantics/generator_captured_cell_sink_state.py
	python3 tests/semantics/generator_captured_cell_sink_review_state.py
	python3 tests/semantics/generator_call_unpack_array_delegation_sources.py
	python3 tests/semantics/generator_call_unpack_array_delegation_state.py
	python3 tests/semantics/generator_call_unpack_array_delegation_review_sources.py
	python3 tests/semantics/generator_call_unpack_array_delegation_review_state.py
	python3 tests/semantics/generator_call_unpack_generator_delegation_sources.py
	python3 tests/semantics/generator_call_unpack_generator_delegation_state.py
	python3 tests/semantics/generator_call_unpack_generator_delegation_review_sources.py
	python3 tests/semantics/generator_call_unpack_generator_delegation_review_state.py
	python3 tests/semantics/generator_call_unpack_detached_child_sources.py
	python3 tests/semantics/generator_call_unpack_detached_child_state.py
	python3 tests/semantics/generator_call_unpack_detached_child_review_sources.py
	python3 tests/semantics/generator_call_unpack_detached_child_review_state.py
	python3 tests/semantics/generator_call_unpack_iterator_delegation_sources.py
	python3 tests/semantics/generator_call_unpack_iterator_delegation_state.py
	python3 tests/semantics/generator_call_unpack_iterator_delegation_review_sources.py
	python3 tests/semantics/generator_call_unpack_iterator_delegation_review_state.py
	python3 tests/semantics/generator_call_unpack_acquired_iterator_sources.py
	python3 tests/semantics/generator_call_unpack_acquired_iterator_state.py
	python3 tests/semantics/generator_call_unpack_acquired_iterator_review_sources.py
	python3 tests/semantics/generator_call_unpack_acquired_iterator_review_state.py
	python3 tests/semantics/generator_call_unpack_acquired_generator_sources.py
	python3 tests/semantics/generator_call_unpack_acquired_generator_state.py
	python3 tests/semantics/generator_call_unpack_acquired_generator_review_sources.py
	python3 tests/semantics/generator_call_unpack_acquired_generator_review_state.py
	python3 tests/semantics/generator_call_unpack_nested_detached_sources.py
	python3 tests/semantics/generator_call_unpack_nested_detached_state.py
	python3 tests/semantics/generator_call_unpack_nested_detached_review_sources.py
	python3 tests/semantics/generator_call_unpack_nested_detached_review_state.py
	python3 tests/semantics/generator_pending_init_send_sources.py
	python3 tests/semantics/generator_pending_init_send_state.py
	python3 tests/semantics/generator_pending_init_send_review_sources.py
	python3 tests/semantics/generator_pending_init_send_review_state.py
	python3 tests/semantics/generator_pending_shared_send_sources.py
	python3 tests/semantics/generator_pending_shared_send_state.py
	python3 tests/semantics/generator_pending_shared_send_review_sources.py
	python3 tests/semantics/generator_pending_shared_send_review_state.py
	python3 tests/semantics/generator_pending_unused_send_sources.py
	python3 tests/semantics/generator_pending_unused_send_state.py
	python3 tests/semantics/generator_pending_unused_send_review_sources.py
	python3 tests/semantics/generator_pending_unused_send_review_state.py
	python3 tests/semantics/generator_buffered_throw_sources.py
	python3 tests/semantics/generator_buffered_throw_state.py
	python3 tests/semantics/generator_buffered_throw_callback_state.py
	python3 tests/semantics/generator_buffered_throw_review_sources.py
	python3 tests/semantics/generator_buffered_throw_review_state.py
	python3 tests/semantics/generator_pending_throw_sources.py
	python3 tests/semantics/generator_pending_throw_state.py
	python3 tests/semantics/generator_pending_throw_review_sources.py
	python3 tests/semantics/generator_pending_throw_review_state.py
	python3 tests/semantics/generator_pending_buffered_throw_sources.py
	python3 tests/semantics/generator_pending_buffered_throw_review_sources.py
	python3 tests/semantics/generator_pending_buffered_throw_state.py
	python3 tests/semantics/generator_pending_buffered_throw_review_state.py
	python3 tests/semantics/generator_pending_foreach_throw_sources.py
	python3 tests/semantics/generator_pending_foreach_throw_review_sources.py
	python3 tests/semantics/generator_pending_foreach_throw_state.py
	python3 tests/semantics/generator_pending_foreach_throw_review_state.py
	python3 tests/semantics/generator_pending_buffered_foreach_throw_sources.py
	python3 tests/semantics/generator_pending_buffered_foreach_throw_review_sources.py
	python3 tests/semantics/generator_pending_buffered_foreach_throw_state.py
	python3 tests/semantics/generator_pending_buffered_foreach_throw_review_state.py
	python3 tests/semantics/generator_pending_reference_foreach_throw_sources.py
	python3 tests/semantics/generator_pending_reference_foreach_throw_review_sources.py
	python3 tests/semantics/generator_pending_reference_foreach_throw_state.py
	python3 tests/semantics/generator_pending_reference_foreach_throw_review_state.py
	python3 tests/semantics/generator_pending_buffered_reference_foreach_throw_sources.py
	python3 tests/semantics/generator_pending_buffered_reference_foreach_throw_review_sources.py
	python3 tests/semantics/generator_pending_buffered_reference_foreach_throw_state.py
	python3 tests/semantics/generator_pending_buffered_reference_foreach_throw_review_state.py
	python3 tests/semantics/generator_owning_detached_return_sources.py
	python3 tests/semantics/generator_owning_detached_return_review_sources.py
	python3 tests/semantics/generator_owning_detached_return_state.py
	python3 tests/semantics/generator_owning_detached_return_review_state.py
	python3 tests/semantics/generator_pending_owning_return_send_sources.py
	python3 tests/semantics/generator_pending_owning_return_send_review_sources.py
	python3 tests/semantics/generator_pending_owning_return_send_state.py
	python3 tests/semantics/generator_pending_owning_return_send_review_state.py
	python3 tests/semantics/generator_pending_owning_return_throw_sources.py
	python3 tests/semantics/generator_pending_owning_return_throw_review_sources.py
	python3 tests/semantics/generator_pending_owning_return_throw_state.py
	python3 tests/semantics/generator_pending_owning_return_throw_review_state.py
	python3 tests/semantics/generator_owning_chain_unpack_sources.py
	python3 tests/semantics/generator_owning_chain_unpack_review_sources.py
	python3 tests/semantics/generator_owning_chain_unpack_state.py
	python3 tests/semantics/generator_owning_chain_unpack_review_state.py
	python3 tests/semantics/generator_pending_owning_chain_send_sources.py
	python3 tests/semantics/generator_pending_owning_chain_send_review_sources.py
	python3 tests/semantics/generator_pending_owning_chain_send_state.py
	python3 tests/semantics/generator_pending_owning_chain_send_review_state.py
	python3 tests/semantics/generator_pending_owning_chain_throw_sources.py
	python3 tests/semantics/generator_pending_owning_chain_throw_review_sources.py
	python3 tests/semantics/generator_pending_owning_chain_throw_state.py
	python3 tests/semantics/generator_pending_owning_chain_throw_review_state.py
	python3 tests/semantics/generator_repeated_pending_owning_throw_sources.py
	python3 tests/semantics/generator_repeated_pending_owning_throw_review_sources.py
	python3 tests/semantics/generator_repeated_pending_owning_throw_state.py
	python3 tests/semantics/generator_repeated_pending_owning_throw_review_state.py
	python3 tests/semantics/generator_parked_pending_owning_send_sources.py
	python3 tests/semantics/generator_parked_pending_owning_send_review_sources.py
	python3 tests/semantics/generator_parked_pending_owning_send_state.py
	python3 tests/semantics/generator_parked_pending_owning_send_review_state.py
	python3 tests/semantics/generator_parked_pending_owning_next_sources.py
	python3 tests/semantics/generator_parked_pending_owning_next_review_sources.py
	python3 tests/semantics/generator_parked_pending_owning_next_state.py
	python3 tests/semantics/generator_parked_pending_owning_next_review_state.py
	python3 tests/semantics/generator_parked_pending_buffered_next_sources.py
	python3 tests/semantics/generator_parked_pending_buffered_next_review_sources.py
	python3 tests/semantics/generator_parked_pending_buffered_next_state.py
	python3 tests/semantics/generator_parked_pending_buffered_next_review_state.py
	python3 tests/semantics/generator_parked_pending_buffered_send_sources.py
	python3 tests/semantics/generator_parked_pending_buffered_send_review_sources.py
	python3 tests/semantics/generator_parked_pending_buffered_send_state.py
	python3 tests/semantics/generator_parked_pending_buffered_send_review_state.py
	python3 tests/semantics/generator_repeated_pending_buffered_throw_sources.py
	python3 tests/semantics/generator_repeated_pending_buffered_throw_review_sources.py
	python3 tests/semantics/generator_repeated_pending_buffered_throw_state.py
	python3 tests/semantics/generator_repeated_pending_buffered_throw_review_state.py
	python3 tests/semantics/generator_unused_pending_send_sources.py
	python3 tests/semantics/generator_unused_pending_send_review_sources.py
	python3 tests/semantics/generator_unused_pending_send_state.py
	python3 tests/semantics/generator_unused_pending_send_review_state.py
	python3 tests/semantics/generator_unused_pending_send_alias_sources.py
	python3 tests/semantics/generator_unused_pending_send_alias_review_sources.py
	python3 tests/semantics/generator_unused_pending_send_alias_state.py
	python3 tests/semantics/generator_unused_pending_send_alias_review_state.py
	python3 tests/semantics/generator_unused_detached_send_sources.py
	python3 tests/semantics/generator_unused_detached_send_state.py
	python3 tests/semantics/generator_unused_detached_send_review_sources.py
	python3 tests/semantics/generator_unused_detached_send_review_state.py
	python3 tests/semantics/generator_unused_direct_detached_send_sources.py
	python3 tests/semantics/generator_unused_direct_detached_send_state.py
	python3 tests/semantics/generator_unused_direct_detached_send_review_sources.py
	python3 tests/semantics/generator_unused_direct_detached_send_review_state.py
	python3 tests/semantics/generator_unused_direct_refresh_send_sources.py
	python3 tests/semantics/generator_unused_direct_refresh_send_state.py
	python3 tests/semantics/generator_unused_direct_refresh_send_review_sources.py
	python3 tests/semantics/generator_unused_direct_refresh_send_review_state.py
	python3 tests/semantics/generator_unused_scalar_return_send_sources.py
	python3 tests/semantics/generator_unused_scalar_return_send_state.py
	python3 tests/semantics/generator_unused_scalar_return_send_review_sources.py
	python3 tests/semantics/generator_unused_scalar_return_send_review_state.py
	python3 tests/semantics/generator_unused_scalar_refresh_send_sources.py
	python3 tests/semantics/generator_unused_scalar_refresh_send_state.py
	python3 tests/semantics/generator_unused_scalar_refresh_send_review_sources.py
	python3 tests/semantics/generator_unused_scalar_refresh_send_review_state.py
	python3 tests/semantics/generator_unused_bare_yield_send_sources.py
	python3 tests/semantics/generator_unused_bare_yield_send_state.py
	python3 tests/semantics/generator_unused_bare_yield_send_review_sources.py
	python3 tests/semantics/generator_unused_bare_yield_send_review_state.py
	python3 tests/semantics/generator_nodefree_ancestor_send_sources.py
	python3 tests/semantics/generator_nodefree_ancestor_send_state.py
	python3 tests/semantics/generator_nodefree_ancestor_send_review_sources.py
	python3 tests/semantics/generator_nodefree_ancestor_send_review_state.py
	python3 tests/semantics/generator_unused_current_sources.py
	python3 tests/semantics/generator_unused_current_state.py
	python3 tests/semantics/generator_unused_current_review_sources.py
	python3 tests/semantics/generator_unused_current_review_state.py
	python3 tests/semantics/generator_abrupt_argument_send_sources.py
	python3 tests/semantics/generator_abrupt_argument_send_state.py
	python3 tests/semantics/generator_abrupt_argument_send_review_sources.py
	python3 tests/semantics/generator_abrupt_argument_send_review_state.py
	python3 tests/semantics/generator_ancestor_abrupt_argument_send_sources.py
	python3 tests/semantics/generator_ancestor_abrupt_argument_send_state.py
	python3 tests/semantics/generator_ancestor_abrupt_argument_send_review_sources.py
	python3 tests/semantics/generator_ancestor_abrupt_argument_send_review_state.py
	python3 tests/semantics/generator_pending_unused_current_sources.py
	python3 tests/semantics/generator_pending_unused_current_state.py
	python3 tests/semantics/generator_pending_unused_current_review_sources.py
	python3 tests/semantics/generator_pending_unused_current_review_state.py
	python3 tests/semantics/generator_refresh_unused_current_sources.py
	python3 tests/semantics/generator_refresh_unused_current_state.py
	python3 tests/semantics/generator_refresh_unused_current_review_sources.py
	python3 tests/semantics/generator_refresh_unused_current_review_state.py
	python3 tests/semantics/generator_fiber_transfer_sources.py
	python3 tests/semantics/generator_fiber_transfer_state.py
	python3 tests/semantics/generator_fiber_transfer_review_sources.py
	python3 tests/semantics/generator_fiber_transfer_review_state.py
	python3 tests/semantics/generator_fiber_helper_transfer_sources.py
	python3 tests/semantics/generator_fiber_helper_transfer_state.py
	python3 tests/semantics/generator_fiber_helper_transfer_review_sources.py
	python3 tests/semantics/generator_fiber_helper_transfer_review_state.py
	python3 tests/semantics/generator_fiber_delegation_transfer_sources.py
	python3 tests/semantics/generator_fiber_delegation_transfer_state.py
	python3 tests/semantics/generator_fiber_delegation_transfer_review_sources.py
	python3 tests/semantics/generator_fiber_delegation_transfer_review_state.py
	python3 tests/semantics/generator_fiber_send_transfer_sources.py
	python3 tests/semantics/generator_fiber_send_transfer_state.py
	python3 tests/semantics/generator_fiber_send_transfer_review_sources.py
	python3 tests/semantics/generator_fiber_send_transfer_review_state.py
	python3 tests/semantics/generator_fiber_closure_transfer_sources.py
	python3 tests/semantics/generator_fiber_closure_transfer_state.py
	python3 tests/semantics/generator_fiber_closure_transfer_review_sources.py --peer-budget-180
	python3 tests/semantics/generator_fiber_closure_transfer_review_state.py
	python3 tests/semantics/generator_fiber_method_transfer_sources.py
	python3 tests/semantics/generator_fiber_method_transfer_state.py
	python3 tests/semantics/generator_fiber_method_transfer_review_sources.py
	python3 tests/semantics/generator_fiber_method_transfer_review_state.py
	python3 tests/semantics/generator_fiber_reference_transfer_sources.py
	python3 tests/semantics/generator_fiber_reference_transfer_state.py
	python3 tests/semantics/generator_fiber_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_fresh_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_reference_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_reference_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_method_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_method_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_closure_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_closure_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_closure_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_fresh_closure_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_closure_reference_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_closure_reference_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_closure_reference_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_fresh_closure_reference_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_method_reference_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_method_reference_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_method_reference_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_fresh_method_reference_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_method_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_fresh_method_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_reference_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_fresh_reference_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_static_throw_transfer_sources.py
	python3 tests/semantics/generator_fiber_static_throw_transfer_state.py
	python3 tests/semantics/generator_fiber_static_transfer_sources.py
	python3 tests/semantics/generator_fiber_static_transfer_state.py
	python3 tests/semantics/generator_fiber_fresh_advance_sources.py
	python3 tests/semantics/generator_fiber_fresh_advance_state.py
	python3 tests/semantics/generator_keyword_creation_sources.py
	python3 tests/semantics/generator_keyword_creation_state.py
	python3 tests/semantics/generator_keyword_chain_sources.py
	python3 tests/semantics/generator_keyword_chain_state.py
	python3 tests/semantics/generator_keyword_receiver_sources.py
	python3 tests/semantics/generator_keyword_receiver_state.py
	python3 tests/semantics/generator_closure_factory_sources.py
	python3 tests/semantics/generator_closure_factory_state.py
	python3 tests/semantics/generator_closure_method_sources.py
	python3 tests/semantics/generator_closure_method_state.py
	python3 tests/semantics/generator_captured_factory_sources.py
	python3 tests/semantics/generator_captured_factory_state.py
	python3 tests/semantics/generator_array_string_factory_sources.py
	python3 tests/semantics/generator_array_string_factory_state.py
	python3 tests/semantics/generator_array_string_factory_review_state.py
	python3 tests/semantics/generator_bound_factory_sources.py
	python3 tests/semantics/generator_bound_factory_state.py
	python3 tests/semantics/generator_bound_factory_review_state.py
	python3 tests/semantics/generator_invokable_factory_sources.py
	python3 tests/semantics/generator_invokable_factory_state.py
	python3 tests/semantics/generator_invokable_factory_review_state.py
	python3 tests/semantics/generator_magic_factory_sources.py
	python3 tests/semantics/generator_magic_factory_state.py
	python3 tests/semantics/generator_magic_factory_review_state.py
	python3 tests/semantics/generator_direct_magic_sources.py
	python3 tests/semantics/generator_direct_magic_state.py
	python3 tests/semantics/generator_direct_magic_review_state.py
	python3 tests/semantics/generator_captured_method_body_sources.py
	python3 tests/semantics/generator_captured_method_body_state.py
	python3 tests/semantics/generator_captured_method_body_review_state.py
	python3 tests/semantics/generator_raw_method_factory_sources.py
	python3 tests/semantics/generator_raw_method_factory_state.py
	python3 tests/semantics/generator_raw_method_factory_review_state.py
	python3 tests/semantics/generator_raw_method_cache_sources.py
	python3 tests/semantics/generator_raw_method_cache_state.py
	python3 tests/semantics/generator_raw_method_cache_review_state.py
	python3 tests/semantics/generator_captured_method_throw_sources.py
	python3 tests/semantics/generator_captured_method_throw_state.py
	python3 tests/semantics/generator_captured_method_throw_review_state.py
	python3 tests/semantics/generator_direct_magic_throw_sources.py
	python3 tests/semantics/generator_direct_magic_throw_state.py
	python3 tests/semantics/generator_direct_magic_throw_review_state.py
	python3 tests/semantics/generator_string_method_closure_sources.py
	python3 tests/semantics/generator_string_method_closure_state.py
	python3 tests/semantics/generator_string_method_closure_review_state.py
	python3 tests/semantics/generator_call_copy_sources.py
	python3 tests/semantics/generator_call_copy_state.py
	python3 tests/semantics/generator_call_copy_review_state.py
	python3 tests/semantics/generator_call_reference_sources.py
	python3 tests/semantics/generator_call_reference_state.py
	python3 tests/semantics/generator_call_reference_review_state.py
	python3 tests/semantics/generator_fake_call_copy_sources.py
	python3 tests/semantics/generator_fake_call_copy_state.py
	python3 tests/semantics/generator_fake_call_copy_review_state.py
	python3 tests/semantics/generator_fake_string_call_sources.py
	python3 tests/semantics/generator_fake_string_call_state.py
	python3 tests/semantics/generator_fake_string_call_review_state.py
	python3 tests/semantics/generator_folded_string_call_sources.py
	python3 tests/semantics/generator_folded_string_call_state.py
	python3 tests/semantics/generator_folded_string_call_review_state.py
	python3 tests/semantics/generator_call_warning_fiber_sources.py
	python3 tests/semantics/generator_call_warning_fiber_state.py
	python3 tests/semantics/generator_call_warning_fiber_review_state.py
	python3 tests/semantics/generator_call_warning_retval_sources.py
	python3 tests/semantics/generator_call_warning_retval_state.py
	python3 tests/semantics/generator_call_warning_retval_review_state.py
	python3 tests/semantics/generator_call_cancellation_sources.py
	python3 tests/semantics/generator_call_cancellation_state.py
	python3 tests/semantics/generator_call_cancellation_review_state.py
	python3 tests/semantics/generator_call_mapping_sources.py
	python3 tests/semantics/generator_call_mapping_state.py
	python3 tests/semantics/generator_call_mapping_review_state.py
	python3 tests/semantics/generator_call_receive_sources.py
	python3 tests/semantics/generator_call_receive_state.py
	python3 tests/semantics/generator_call_receive_review_state.py
	python3 tests/semantics/generator_call_exit_sources.py
	python3 tests/semantics/generator_call_exit_state.py
	python3 tests/semantics/generator_call_exit_review_state.py
	python3 tests/semantics/generator_call_cleanup_exit_sources.py
	python3 tests/semantics/generator_call_cleanup_exit_state.py
	python3 tests/semantics/generator_call_cleanup_exit_review_state.py
	python3 tests/semantics/generator_call_cleanup_throw_sources.py
	python3 tests/semantics/generator_call_cleanup_throw_review_state.py
	python3 tests/semantics/generator_call_repeated_cleanup_exit_sources.py
	python3 tests/semantics/generator_call_repeated_cleanup_exit_state.py
	python3 tests/semantics/generator_call_repeated_cleanup_exit_review_state.py
	python3 tests/semantics/generator_call_cleanup_return_sources.py
	python3 tests/semantics/generator_call_cleanup_return_state.py
	python3 tests/semantics/generator_call_cleanup_return_review_state.py
	python3 tests/semantics/generator_call_array_pack_sources.py
	python3 tests/semantics/generator_call_array_pack_review_sources.py
	python3 tests/semantics/generator_call_array_pack_review_state.py
	python3 tests/semantics/generator_method_argument_sources.py
	python3 tests/semantics/generator_method_arguments_review_sources.py
	python3 tests/semantics/generator_method_arguments_review_state.py
	python3 tests/semantics/generator_nullsafe_method_sources.py
	python3 tests/semantics/generator_nullsafe_method_review_sources.py
	python3 tests/semantics/generator_nullsafe_method_review_state.py
	python3 tests/semantics/generator_computed_method_sources.py
	python3 tests/semantics/generator_computed_method_review_sources.py
	python3 tests/semantics/generator_computed_method_review_state.py
	python3 tests/semantics/generator_api_capture_sources.py
	python3 tests/semantics/generator_api_capture_review_sources.py
	python3 tests/semantics/generator_api_capture_review_state.py
	python3 tests/semantics/generator_explicit_invoke_sources.py
	python3 tests/semantics/generator_explicit_invoke_review_sources.py
	python3 tests/semantics/generator_explicit_invoke_review_state.py
	python3 tests/semantics/generator_api_binding_sources.py
	python3 tests/semantics/generator_api_binding_review_sources.py
	python3 tests/semantics/generator_api_binding_review_state.py
	python3 tests/semantics/generator_api_call_sources.py
	python3 tests/semantics/generator_api_call_review_sources.py
	python3 tests/semantics/generator_api_call_review_state.py
	python3 tests/semantics/generator_method_iterator_pack_sources.py
	python3 tests/semantics/generator_method_iterator_pack_review_sources.py
	python3 tests/semantics/generator_method_iterator_pack_review_state.py
	python3 tests/semantics/generator_send_body_throw_sources.py
	python3 tests/semantics/generator_send_body_throw_review_sources.py
	python3 tests/semantics/generator_send_body_throw_review_state.py
	python3 tests/semantics/generator_computed_send_body_throw_review_sources.py
	python3 tests/semantics/generator_computed_send_body_throw_review_state.py
	python3 tests/semantics/generator_nullsafe_send_body_throw_review_sources.py
	python3 tests/semantics/generator_nullsafe_send_body_throw_review_state.py
	python3 tests/semantics/generator_reference_send_body_throw_review_sources.py
	python3 tests/semantics/generator_reference_send_body_throw_review_state.py
	python3 tests/semantics/generator_reference_snapshot_send_body_throw_review_sources.py
	python3 tests/semantics/generator_reference_snapshot_send_body_throw_review_state.py
	python3 tests/semantics/weak_reference_sources.py
	python3 tests/semantics/weak_reference_state.py
	python3 tests/semantics/weak_reference_review.py
	python3 tests/semantics/weak_reference_state_review.py
	python3 tests/semantics/cycle_collection_sources.py --exclude-match collector-detached-throw-has-worker-and-real-resumer-traces --exclude-match collector-residual-dtor-public-resume-preparation-25 --exclude-match collector-residual-dtor-next-internal-fiber-pass-preparation-26 --exclude-match collector-residual-dtor-next-main-pass-preparation-27 --exclude-match collector-residual-internal-callback-suspends-and-detaches-preparation-28 --exclude-match collector-residual-internal-suspension-releases-last-cache-owner-preparation-29 --exclude-match collector-public-callback-resuspends-during-internal-takeover-preparation-30 --exclude-match collector-cached-public-reentry-during-different-main-pass-preparation-31 --exclude-match collector-fiber-mixed-residual-tags-and-fresh-eligible-overlap-preparation-36 --exclude-match collector-fiber-array-edge-residual-overlap-preparation-37 --exclude-match collector-fiber-reference-edge-residual-overlap-preparation-38 --exclude-match collector-fiber-residual-self-reference-overlap-preparation-39 --exclude-match collector-fiber-residual-array-overlap-preparation-40 --exclude-match collector-fiber-outside-residual-reference-overlap-preparation-41
	python3 tests/semantics/cycle_collection_state.py
	python3 tests/semantics/cycle_collection_review.py --exclude-match collector-detached-pending-review-18 --exclude-match collector-detached-quiescent-throwing-fiber-prior-error-review-19 --exclude-match collector-active-interval-bound-core-throw-review-21 --exclude-match collector-active-public-cached-core-old-pending-new-throw-review-22 --exclude-match collector-active-public-cached-core-two-identities-compact-review-22 --exclude-match collector-public-postpass-core-old-pending-new-throw-review-23 --exclude-match collector-new-fiber-pass-keeps-parked-old-error-review-24 --exclude-match collector-internal-takeover-old-error-compact-preparation-24 --exclude-match collector-residual-dtor-next-internal-old-pending-review-preparation-26 --exclude-match collector-residual-dtor-main-old-pending-review-preparation-27 --exclude-match collector-residual-internal-suspension-separates-replacement-error-review-preparation-28 --exclude-match collector-residual-last-owner-failed-finally-prior-error-review-preparation-29 --exclude-match collector-public-internal-resuspension-separates-two-finally-errors-review-preparation-30 --exclude-match collector-cached-public-throw-during-different-main-pass-prior-identity-review-preparation-31
	python3 tests/semantics/cycle_collection_state_review.py --sl
	python3 tests/semantics/weak_map_scalar_replacement_state.py --case object-to-scalar
	python3 tests/semantics/weak_map_scalar_replacement_state.py --case scalar-to-object
	python3 tests/semantics/exception_handler_static_default.py
	python3 tests/semantics/scoped_callables.py
	python3 tests/semantics/scoped_callables_protocol.py
	python3 tests/semantics/keyword_compound_callables.py
	python3 tests/semantics/keyword_compound_callables_protocol.py
	python3 tests/semantics/callable_receives.py
	python3 tests/semantics/callable_receive_protocol.py
	python3 tests/semantics/from_callable.py
	python3 tests/semantics/from_callable_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_static_array_cv_callable_producer_magic_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_static_array_cv_callable_producer_magic_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_static_array_cv_callable_producer_magic_independent_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_static_array_cv_callable_producer_magic_independent_state.py
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
	python3 tests/semantics/pipe_array.py
	python3 tests/semantics/pipe_array_protocol.py
	python3 tests/semantics/pipe_static_string.py
	python3 tests/semantics/pipe_static_string_protocol.py
	python3 tests/semantics/pipe_named_carrier.py
	python3 tests/semantics/pipe_named_carrier_protocol.py
	python3 tests/semantics/pipe_optimized_static.py
	python3 tests/semantics/pipe_optimized_static_protocol.py
	python3 tests/semantics/pipe_object.py
	python3 tests/semantics/pipe_object_protocol.py
	python3 tests/semantics/pipe_nonpublic_object.py
	python3 tests/semantics/pipe_nonpublic_object_protocol.py
	python3 tests/semantics/pipe_protocol.py
	python3 tests/semantics/enum_pipe.py
	python3 tests/semantics/enum_pipe_protocol.py
	python3 tests/semantics/enum_is_callable.py
	python3 tests/semantics/enum_included_constant_method_cache.py
	python3 tests/semantics/enum_scoped_included_constant_method_cache.py
	python3 tests/semantics/enum_static_producer_constant_method_cache.py
	python3 tests/semantics/enum_is_callable_protocol.py
	python3 tests/semantics/enum_is_callable_shape_protocol.py
	python3 tests/semantics/enum_is_callable_magic_protocol.py
	python3 tests/semantics/enum_is_callable_case_method_protocol.py
	python3 tests/semantics/enum_is_callable_wide_shape_protocol.py
	python3 tests/semantics/enum_is_callable_output_protocol.py
	python3 tests/semantics/enum_is_callable_output_false_protocol.py
	python3 tests/semantics/enum_is_callable_output_array_protocol.py
	python3 tests/semantics/enum_is_callable_output_spelling_protocol.py
	python3 tests/semantics/enum_is_callable_output_scalar_protocol.py
	python3 tests/semantics/enum_is_callable_output_string_spelling_protocol.py
	python3 tests/semantics/enum_is_callable_output_variable_protocol.py
	python3 tests/semantics/enum_is_callable_output_alias_protocol.py
	python3 tests/semantics/enum_is_callable_saved_input_protocol.py
	python3 tests/semantics/enum_is_callable_output_retained_protocol.py
	python3 tests/semantics/enum_is_callable_output_unique_protocol.py
	python3 tests/semantics/enum_is_callable_output_exit_protocol.py
	python3 tests/semantics/enum_is_callable_output_cleanup_protocol.py
	python3 tests/semantics/enum_is_callable_output_reexit_protocol.py --group own
	python3 tests/semantics/enum_is_callable_output_reexit_protocol.py --group nested
	python3 tests/semantics/enum_is_callable_output_reexit_protocol.py --group alias
	python3 tests/semantics/enum_is_callable_output_reexit_protocol.py --group thrown
	python3 tests/semantics/enum_is_callable_output_reexit_protocol.py --group roots
	python3 tests/semantics/enum_is_callable_variable_array_protocol.py --group direct
	python3 tests/semantics/enum_is_callable_variable_array_protocol.py --group rebind
	python3 tests/semantics/enum_is_callable_variable_array_protocol.py --group alias
	python3 tests/semantics/enum_is_callable_variable_array_cleanup_protocol.py
	python3 tests/semantics/enum_is_callable_array_alias_rebound_protocol.py --group raw
	python3 tests/semantics/enum_is_callable_array_alias_rebound_protocol.py --group case
	python3 tests/semantics/enum_is_callable_array_alias_rebound_protocol.py --group retained
	python3 tests/semantics/enum_is_callable_array_alias_rebound_protocol.py --group throw
	python3 tests/semantics/enum_is_callable_array_alias_rebound_protocol.py --group last_owner
	python3 tests/semantics/enum_is_callable_array_alias_owning_protocol.py --group retained
	python3 tests/semantics/enum_is_callable_array_alias_owning_protocol.py --group throw
	python3 tests/semantics/enum_is_callable_array_alias_retained_child_protocol.py --group held
	python3 tests/semantics/enum_is_callable_array_alias_retained_child_protocol.py --group released
	python3 tests/semantics/enum_is_callable_reference_array_protocol.py --group alias
	python3 tests/semantics/enum_is_callable_reference_array_protocol.py --group throw
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
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/instanceof_dynamic_cases.json
	python3 tests/semantics/instanceof_dynamic_protocol.py --revision "$$(git rev-parse HEAD)"
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
	python3 tests/semantics/property_reference_argument_warning_protocol.py --group replacement
	python3 tests/semantics/property_reference_argument_warning_protocol.py --group parameter
	python3 tests/semantics/property_reference_argument_warning_protocol.py --group pending
	python3 tests/semantics/property_reference_argument_warning_protocol.py --group samecell
	python3 tests/semantics/property_reference_argument_warning_protocol.py --group alias
	python3 tests/semantics/property_reference_named_warning_protocol.py --group samecell
	python3 tests/semantics/property_reference_named_warning_protocol.py --group quiet
	python3 tests/semantics/property_reference_named_warning_protocol.py --group warning
	python3 tests/semantics/property_reference_named_warning_protocol.py --group default
	python3 tests/semantics/property_reference_named_warning_protocol.py --group pending
	python3 tests/semantics/property_reference_two_cv_warning_protocol.py --group mutation
	python3 tests/semantics/property_reference_two_cv_warning_protocol.py --group unset
	python3 tests/semantics/property_reference_two_cv_warning_protocol.py --group samecell
	python3 tests/semantics/property_reference_two_cv_warning_protocol.py --group leave
	python3 tests/semantics/property_reference_two_cv_warning_protocol.py --group sendthrow
	python3 tests/semantics/property_reference_two_cv_warning_protocol.py --group pending
	python3 tests/semantics/property_reference_two_named_warning_protocol.py --group first
	python3 tests/semantics/property_reference_two_named_warning_protocol.py --group samecell
	python3 tests/semantics/property_reference_two_named_warning_protocol.py --group leave
	python3 tests/semantics/property_reference_two_named_warning_protocol.py --group priority
	python3 tests/semantics/property_reference_two_named_warning_protocol.py --group pending
	python3 tests/semantics/property_reference_mixed_warning_protocol.py --group first
	python3 tests/semantics/property_reference_mixed_warning_protocol.py --group samecell
	python3 tests/semantics/property_reference_mixed_warning_protocol.py --group leave
	python3 tests/semantics/property_reference_mixed_warning_protocol.py --group priority
	python3 tests/semantics/property_reference_mixed_warning_protocol.py --group pending
	python3 tests/semantics/magic_property_get_protocol.py --group reference
	python3 tests/semantics/magic_property_get_protocol.py --group readonly
	python3 tests/semantics/magic_property_get_protocol.py --group type-error
	python3 tests/semantics/magic_property_get_protocol.py --group initial
	python3 tests/semantics/magic_property_get_protocol.py --group value
	python3 tests/semantics/magic_property_get_protocol.py --group getter-throw
	python3 tests/semantics/magic_property_get_protocol.py --group returned-throw
	python3 tests/semantics/magic_property_get_protocol.py --group discarded
	python3 tests/semantics/magic_property_denied_protocol.py --group reference
	python3 tests/semantics/magic_property_denied_protocol.py --group private-initial
	python3 tests/semantics/magic_property_denied_protocol.py --group protected-initial
	python3 tests/semantics/magic_property_denied_protocol.py --group allowed-value
	python3 tests/semantics/magic_property_denied_protocol.py --group getter-throw
	python3 tests/semantics/magic_property_denied_protocol.py --group returned-throw
	python3 tests/semantics/magic_property_owned_protocol.py --group reference
	python3 tests/semantics/magic_property_owned_protocol.py --group readonly
	python3 tests/semantics/magic_property_owned_protocol.py --group initial-reject
	python3 tests/semantics/magic_property_owned_protocol.py --group getter-throw
	python3 tests/semantics/magic_property_owned_protocol.py --group returned-throw
	python3 tests/semantics/magic_property_owned_protocol.py --group discarded
	python3 tests/semantics/magic_property_owned_protocol.py --group value
	python3 tests/semantics/magic_property_integer_protocol.py --group reference-kept
	python3 tests/semantics/magic_property_integer_protocol.py --group reference-drop
	python3 tests/semantics/magic_property_integer_protocol.py --group value
	python3 tests/semantics/magic_property_integer_protocol.py --group owned-reference
	python3 tests/semantics/magic_property_integer_protocol.py --group weak-getter
	python3 tests/semantics/magic_property_integer_protocol.py --group strict-getter
	python3 tests/semantics/magic_property_reference_protocol.py --group exact-kept
	python3 tests/semantics/magic_property_reference_protocol.py --group conflict
	python3 tests/semantics/magic_property_reference_protocol.py --group reject
	python3 tests/semantics/magic_property_reference_protocol.py --group owned-object
	python3 tests/semantics/magic_property_reference_protocol.py --group strict
	python3 tests/semantics/magic_property_reference_protocol.py --group first-source
	python3 tests/semantics/magic_property_float_protocol.py --group reference-kept
	python3 tests/semantics/magic_property_float_protocol.py --group reference-drop
	python3 tests/semantics/magic_property_float_protocol.py --group value
	python3 tests/semantics/magic_property_float_protocol.py --group owned
	python3 tests/semantics/magic_property_float_protocol.py --group source-conflict
	python3 tests/semantics/magic_property_float_protocol.py --group source-exact
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
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/dynamic_new_selector_cases.json
	python3 tests/semantics/dynamic_new_selector_protocol.py --revision $$(git rev-parse HEAD)
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
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/parameter_override_cases.json
	python3 tests/semantics/parameter_override_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/nodiscard_sources.py
	python3 tests/semantics/nodiscard_protocol.py
	python3 tests/semantics/deprecated_sources.py
	python3 tests/semantics/deprecated_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/sensitive_parameter_cases.json
	python3 tests/semantics/sensitive_parameter_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/constructor_sensitive_promotion_cases.json
	python3 tests/semantics/constructor_sensitive_promotion_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/sensitive_value_constructor_cases.json
	python3 tests/semantics/sensitive_value_constructor_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/sensitive_value_getter_cases.json
	python3 tests/semantics/sensitive_value_getter_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/sensitive_value_constructor_callable_cases.json
	python3 tests/semantics/sensitive_value_constructor_callable_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/allow_dynamic_properties_cases.json
	python3 tests/semantics/allow_dynamic_properties_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/backed_get_hook_cases.json
	python3 tests/semantics/backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/reference_get_hook_cases.json
	python3 tests/semantics/reference_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group backing-alias
	python3 tests/semantics/reference_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group forbidden-rebind
	python3 tests/semantics/untyped_reference_get_hook_protocol.py
	python3 tests/semantics/inherited_reference_get_hook_protocol.py
	python3 tests/semantics/plain_child_reference_get_hook_protocol.py
	python3 tests/semantics/untyped_plain_child_reference_get_hook_protocol.py
	python3 tests/semantics/grandchild_reference_get_hook_protocol.py
	python3 tests/semantics/reference_get_chain_protocol.py
	python3 tests/semantics/reference_get_memberful_protocol.py
	python3 tests/semantics/reference_get_parented_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/expression_get_hook_cases.json
	python3 tests/semantics/expression_get_hook_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_get_hook_cases.json
	python3 tests/semantics/virtual_get_hook_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/backed_get_hook_addassign_cases.json
	python3 tests/semantics/backed_get_hook_addassign_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/backed_get_hook_override_cases.json
	python3 tests/semantics/backed_get_hook_override_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/effective_backed_get_hook_cases.json
	python3 tests/semantics/effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group scalar
	python3 tests/semantics/effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/repeated_effective_backed_get_hook_cases.json
	python3 tests/semantics/repeated_effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/repeated_effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/repeated_effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/repeated_effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/repeated_effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group untyped
	python3 tests/semantics/repeated_effective_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_get_hook_override_cases.json
	python3 tests/semantics/virtual_get_hook_override_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/virtual_get_hook_override_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/virtual_get_hook_override_protocol.py --revision "$$(git rev-parse HEAD)" --group writes
	python3 tests/semantics/virtual_get_hook_override_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_get_hook_covariance_cases.json
	python3 tests/semantics/virtual_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/virtual_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/virtual_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/virtual_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group invalid
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_get_hook_type_presence_cases.json
	python3 tests/semantics/virtual_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/virtual_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/virtual_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/virtual_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/backed_get_hook_type_presence_cases.json
	python3 tests/semantics/backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_backed_get_hook_type_presence_cases.json
	python3 tests/semantics/virtual_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/virtual_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/virtual_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/virtual_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/virtual_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/backed_parent_unbacked_get_hook_type_presence_cases.json
	python3 tests/semantics/backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/effective_backed_parent_unbacked_get_hook_type_presence_cases.json
	python3 tests/semantics/effective_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/effective_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/effective_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/effective_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/effective_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/effective_backed_parent_backed_get_hook_type_presence_cases.json
	python3 tests/semantics/effective_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/effective_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/effective_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/effective_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/effective_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_backed_get_hook_cases.json
	python3 tests/semantics/virtual_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/virtual_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/virtual_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/virtual_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_backed_get_hook_covariance_cases.json
	python3 tests/semantics/virtual_parent_backed_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/virtual_parent_backed_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/virtual_parent_backed_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/virtual_parent_backed_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/virtual_parent_backed_get_hook_covariance_protocol.py --revision "$$(git rev-parse HEAD)" --group invalid
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/ordinary_parent_backed_get_hook_cases.json
	python3 tests/semantics/ordinary_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/ordinary_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/ordinary_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/ordinary_parent_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/ordinary_parent_unbacked_get_hook_cases.json
	python3 tests/semantics/ordinary_parent_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/ordinary_parent_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/ordinary_parent_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/ordinary_parent_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group untyped
	python3 tests/semantics/ordinary_parent_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/repeated_ordinary_unbacked_get_hook_cases.json
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group cv_metadata
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group cv
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group untyped_metadata
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group untyped_read
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group untyped_write
	python3 tests/semantics/repeated_ordinary_unbacked_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group lifetime
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/ordinary_backed_parent_unbacked_get_hook_type_presence_cases.json
	python3 tests/semantics/ordinary_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/ordinary_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/ordinary_backed_parent_unbacked_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group control
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/ordinary_backed_parent_backed_get_hook_type_presence_cases.json
	python3 tests/semantics/ordinary_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/ordinary_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/ordinary_backed_parent_backed_get_hook_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group control
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/plain_child_inherited_backed_get_hook_cases.json
	python3 tests/semantics/plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/repeated_plain_child_inherited_backed_get_hook_cases.json
	python3 tests/semantics/repeated_plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/repeated_plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/repeated_plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group this
	python3 tests/semantics/repeated_plain_child_inherited_backed_get_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/ordinary_backed_parent_plain_inherited_getter_cases.json
	python3 tests/semantics/ordinary_backed_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/ordinary_backed_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/ordinary_backed_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/inherited_backed_parent_plain_inherited_getter_cases.json
	python3 tests/semantics/inherited_backed_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/inherited_backed_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/inherited_backed_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_plain_inherited_getter_cases.json
	python3 tests/semantics/virtual_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/virtual_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/virtual_parent_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_covariant_plain_inherited_getter_cases.json
	python3 tests/semantics/virtual_parent_covariant_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/virtual_parent_covariant_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/virtual_parent_covariant_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/virtual_parent_covariant_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group invalid
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_protected_set_plain_inherited_getter_cases.json
	python3 tests/semantics/virtual_parent_protected_set_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/virtual_parent_protected_set_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group denied
	python3 tests/semantics/virtual_parent_protected_set_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group child_write
	python3 tests/semantics/virtual_parent_protected_set_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group parent_write
	python3 tests/semantics/virtual_parent_protected_set_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group backed
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_parent_plain_type_presence_cases.json
	python3 tests/semantics/virtual_parent_plain_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group remove
	python3 tests/semantics/virtual_parent_plain_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group add
	python3 tests/semantics/virtual_parent_plain_type_presence_protocol.py --revision "$$(git rev-parse HEAD)" --group control
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/repeated_protected_plain_inherited_getter_cases.json
	python3 tests/semantics/repeated_protected_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/repeated_protected_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/repeated_protected_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/repeated_protected_plain_inherited_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group narrow
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_backed_getter_cases.json
	python3 tests/semantics/trait_imported_backed_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/trait_imported_backed_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/trait_imported_backed_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/trait_imported_backed_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group collision
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_virtual_getter_cases.json
	python3 tests/semantics/trait_imported_virtual_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/trait_imported_virtual_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/trait_imported_virtual_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group denied
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_expression_getter_cases.json
	python3 tests/semantics/trait_imported_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/trait_imported_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/trait_imported_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_virtual_expression_getter_cases.json
	python3 tests/semantics/trait_imported_virtual_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/trait_imported_virtual_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/trait_imported_virtual_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group denied
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/parented_trait_expression_getter_cases.json
	python3 tests/semantics/parented_trait_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/parented_trait_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/parented_trait_expression_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/inherited_overlap_trait_getter_cases.json
	python3 tests/semantics/inherited_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/inherited_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group entry
	python3 tests/semantics/inherited_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/inherited_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group invalid
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/private_overlap_trait_getter_cases.json
	python3 tests/semantics/private_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/private_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group read
	python3 tests/semantics/private_overlap_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/nested_trait_getter_cases.json
	python3 tests/semantics/nested_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/nested_trait_getter_protocol.py --revision "$$(git rev-parse HEAD)" --group write
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/backed_set_only_hook_cases.json
	python3 tests/semantics/backed_set_only_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/backed_set_only_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group backing
	python3 tests/semantics/backed_set_only_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group error
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/paired_backed_get_set_hook_cases.json
	python3 tests/semantics/paired_backed_get_set_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group get
	python3 tests/semantics/paired_backed_get_set_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group set
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/explicit_setter_parameter_cases.json
	python3 tests/semantics/explicit_setter_parameter_protocol.py --revision "$$(git rev-parse HEAD)" --group receive
	python3 tests/semantics/explicit_setter_parameter_protocol.py --revision "$$(git rev-parse HEAD)" --group error
	python3 tests/semantics/explicit_setter_parameter_protocol.py --revision "$$(git rev-parse HEAD)" --group narrow
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_backed_set_hook_cases.json
	python3 tests/semantics/trait_imported_backed_set_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/trait_imported_backed_set_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group set
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_explicit_set_hook_cases.json
	python3 tests/semantics/trait_imported_explicit_set_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group controls
	python3 tests/semantics/trait_imported_explicit_set_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group set
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_imported_paired_hooks_cases.json
	python3 tests/semantics/trait_imported_paired_hooks_protocol.py --revision "$$(git rev-parse HEAD)" --group get
	python3 tests/semantics/trait_imported_paired_hooks_protocol.py --revision "$$(git rev-parse HEAD)" --group set
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/virtual_set_only_hook_cases.json
	python3 tests/semantics/virtual_set_only_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group set
	python3 tests/semantics/virtual_set_only_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group errors
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/active_virtual_set_alias_cases.json
	python3 tests/semantics/active_virtual_set_alias_protocol.py --revision "$$(git rev-parse HEAD)" --group error
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/protected_set_backed_hook_cases.json
	python3 tests/semantics/protected_set_backed_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group receive
	python3 tests/semantics/protected_set_backed_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group errors
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/private_set_backed_hook_cases.json
	python3 tests/semantics/private_set_backed_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group receive
	python3 tests/semantics/private_set_backed_hook_protocol.py --revision "$$(git rev-parse HEAD)" --group errors
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_unset_cases.json
	python3 tests/semantics/magic_unset_protocol.py --revision "$$(git rev-parse HEAD)" --group magic
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_unset_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_unset_protocol.py
	python3 tests/semantics/anonymous_missing_unset_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/public_unset_cases.json
	python3 tests/semantics/public_unset_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_isset_cases.json
	python3 tests/semantics/magic_isset_protocol.py --revision "$$(git rev-parse HEAD)" --group magic
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_isset_pair_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_isset_pair_protocol.py
	python3 tests/semantics/anonymous_missing_isset_pair_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_isset_cv_pair_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_isset_cv_pair_protocol.py
	python3 tests/semantics/anonymous_missing_isset_cv_pair_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/terminal_isset_rv_cases.json
	python3 tests/semantics/terminal_isset_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_coalesce_cases.json
	python3 tests/semantics/magic_coalesce_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_coalesce_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_coalesce_protocol.py
	python3 tests/semantics/anonymous_missing_coalesce_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_coalesce_cv_pair_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_coalesce_cv_pair_protocol.py
	python3 tests/semantics/anonymous_missing_coalesce_cv_pair_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_empty_name_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_empty_name_protocol.py
	python3 tests/semantics/anonymous_missing_empty_name_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_typed_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_typed_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_typed_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_typed_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_compatible_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_compatible_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_compatible_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_compatible_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_typed_get_member_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_typed_get_member_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_typed_get_member_review_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_typed_get_member_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_string_compatible_get_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_string_compatible_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_string_compatible_get_review_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_string_compatible_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_read_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_read_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_read_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_read_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_echo_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_echo_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_echo_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_echo_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_compatible_read_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_compatible_read_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_compatible_read_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_string_compatible_read_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_primitive_read_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_primitive_read_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_primitive_read_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_primitive_read_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_scalar_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_scalar_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_scalar_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_scalar_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_scalar_return_get_error_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_nullable_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_nullable_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_int_string_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_int_string_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_int_string_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_int_string_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_literal_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_literal_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_literal_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_literal_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_union_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_nullable_union_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_union_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_nullable_union_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_literal_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_nullable_literal_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_literal_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_nullable_literal_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_scalar_union_return_get_split_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_scalar_union_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_scalar_union_return_get_split_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_scalar_union_return_get_split_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_untyped_name_return_get_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_untyped_name_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_untyped_name_typed_return_get_review_cases.json --model-timeout 300
	python3 tests/semantics/magic_property_untyped_name_typed_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_void_never_return_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_void_never_return_get_protocol.py
	python3 tests/semantics/magic_property_void_never_return_get_exit_protocol.py
	python3 tests/semantics/magic_property_void_never_return_get_compiler.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_void_never_return_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_void_never_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_array_return_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_array_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_array_return_get_review_cases.json --model-timeout 280
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_array_return_get_pending_review_cases.json --model-timeout 280
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_array_return_get_absent_return_review_cases.json --model-timeout 280
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_array_return_get_catch_scope_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_array_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_object_return_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_object_return_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_object_return_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_object_return_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_int_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_int_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_int_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_int_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_unselected_typed_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_unselected_typed_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_unselected_typed_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_unselected_typed_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_bool_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_bool_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_bool_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_bool_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_float_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_float_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_float_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_float_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nan_cv_isset_reentry_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_nan_cv_isset_reentry_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nan_cv_isset_reentry_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_nan_cv_isset_reentry_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_quiet_get_stringable_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_string_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_string_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_string_quiet_get_conversion_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_string_quiet_get_conversion_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_null_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_null_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_null_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_null_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_union_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_nullable_union_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_nullable_union_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_nullable_union_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_void_never_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_void_never_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_void_never_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_void_never_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_mixed_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_mixed_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_mixed_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_mixed_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_owning_quiet_empty_get_cases.json --case array-cv-empty-immutable-before-receiver --case array-cv-empty-shared-payload-retires-later --case object-cv-empty-std-storage-child-before-receiver --case literal-object-coalesce-transfers-owning-return --case array-cv-coalesce-type-error-before-result-fence --model-timeout 280
	python3 tests/semantics/magic_property_owning_quiet_empty_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_owning_quiet_empty_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_owning_quiet_empty_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_owning_quiet_coalesce_get_cases.json --case object-cv-coalesce-std-result-from-saved-control --case array-cv-coalesce-empty-and-false-isset --case mixed-cv-coalesce-shared-array-cow --model-timeout 280
	python3 tests/semantics/magic_property_owning_quiet_coalesce_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_owning_quiet_coalesce_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_owning_quiet_coalesce_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_owning_quiet_coalesce_assignment_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_owning_quiet_coalesce_assignment_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_owning_quiet_coalesce_assignment_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_owning_quiet_coalesce_assignment_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_enum_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_enum_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_enum_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_enum_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_weakmap_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_weakmap_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_weakmap_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_weakmap_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_weakreference_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_weakreference_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_weakreference_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_weakreference_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_realclosure_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_realclosure_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_realclosure_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_realclosure_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_arrow_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_arrow_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_arrow_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_arrow_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_clone_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_clone_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_clone_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_clone_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_namedclosure_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_namedclosure_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_namedclosure_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_namedclosure_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_namedclosure_clone_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_namedclosure_clone_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_namedclosure_clone_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_namedclosure_clone_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_clone_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_clone_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_clone_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_clone_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_named_selector_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_named_selector_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_named_selector_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_named_selector_quiet_get_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_empty_parent_quiet_get_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_empty_parent_quiet_get_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/magic_property_methodclosure_static_empty_parent_quiet_get_review_cases.json --model-timeout 280
	python3 tests/semantics/magic_property_methodclosure_static_empty_parent_quiet_get_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_coalesce_no_get_cases.json
	python3 tests/semantics/magic_coalesce_no_get_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_coalesce_assignment_cases.json
	python3 tests/semantics/magic_coalesce_assignment_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_cases.json
	python3 tests/semantics/magic_empty_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_empty_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_empty_protocol.py
	python3 tests/semantics/anonymous_missing_empty_review_protocol.py
	python3 tests/semantics/anonymous_owner_factory_sources.py --catalogue tests/semantics/anonymous_missing_empty_cv_pair_cases.json --model-timeout 300
	python3 tests/semantics/anonymous_missing_empty_cv_pair_protocol.py
	python3 tests/semantics/anonymous_missing_empty_cv_pair_review_protocol.py
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_scalar_cases.json
	python3 tests/semantics/magic_empty_scalar_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_float_cases.json
	python3 tests/semantics/magic_empty_float_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_nan_cases.json
	python3 tests/semantics/magic_empty_nan_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_object_rv_cases.json
	python3 tests/semantics/magic_empty_object_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_std_rv_cases.json
	python3 tests/semantics/magic_empty_std_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_array_rv_cases.json
	python3 tests/semantics/magic_empty_array_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_mutable_array_rv_cases.json
	python3 tests/semantics/magic_empty_mutable_array_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_weakmap_rv_cases.json
	python3 tests/semantics/magic_empty_weakmap_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_closure_rv_cases.json
	python3 tests/semantics/magic_empty_closure_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_isset_rv_cases.json
	python3 tests/semantics/magic_empty_isset_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_isset_array_rv_cases.json
	python3 tests/semantics/magic_empty_isset_array_rv_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_setter_cases.json
	python3 tests/semantics/magic_setter_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_call_cases.json
	python3 tests/semantics/magic_call_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_named_call_cases.json
	python3 tests/semantics/magic_named_call_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_property_addassign_cases.json
	python3 tests/semantics/magic_property_addassign_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_property_incdec_cases.json
	python3 tests/semantics/magic_property_incdec_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_static_call_cases.json
	python3 tests/semantics/magic_static_call_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_scoped_call_cases.json
	python3 tests/semantics/magic_scoped_call_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/parent_get_hook_cases.json
	python3 tests/semantics/parent_get_hook_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/parent_set_hook_cases.json
	python3 tests/semantics/parent_set_hook_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_isset_only_cases.json
	python3 tests/semantics/magic_empty_isset_only_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/magic_empty_get_only_cases.json
	python3 tests/semantics/magic_empty_get_only_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/quiet_public_nan_cases.json
	python3 tests/semantics/quiet_public_nan_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/quiet_public_reference_nan_cases.json
	python3 tests/semantics/quiet_public_reference_nan_protocol.py --revision "$$(git rev-parse HEAD)"
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
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/cached_property_clone_cases.json
	python3 tests/semantics/cached_property_clone_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/cached_clone_callback_cases.json
	python3 tests/semantics/cached_clone_callback_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/mixed_cached_clone_cases.json
	python3 tests/semantics/mixed_cached_clone_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/method_runtime.py --catalogue tests/semantics/mixed_cached_clone_callback_cases.json
	python3 tests/semantics/mixed_cached_clone_callback_protocol.py --revision "$$(git rev-parse HEAD)"
	python3 tests/semantics/dynamic_only_cached_clone_sources.py
	python3 tests/semantics/dynamic_only_cached_clone_state.py
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
	python3 tests/semantics/rejected_encoding_sources.py --output "$$(mktemp -d /tmp/php-spec-rejected-encoding.XXXXXXXX)/sources"
	python3 tests/semantics/lexical_header_sources.py --output "$$(mktemp -d /tmp/php-spec-lexical-headers.XXXXXXXX)/sources"
	python3 tests/semantics/unicode_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-rejected-unicode.XXXXXXXX)/sources"
	python3 tests/semantics/rejected_eval_unicode_review_state.py --output "$$(mktemp -d /tmp/php-spec-rejected-unicode.XXXXXXXX)/state"
	python3 tests/semantics/namespace_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-rejected-namespace.XXXXXXXX)/sources"
	python3 tests/semantics/namespace_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-rejected-namespace.XXXXXXXX)/main"
	python3 tests/semantics/rejected_namespace_review_state.py --output "$$(mktemp -d /tmp/php-spec-rejected-namespace.XXXXXXXX)/state"
	python3 tests/semantics/static_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-rejected-static.XXXXXXXX)/sources"
	python3 tests/semantics/static_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-rejected-static.XXXXXXXX)/main"
	python3 tests/semantics/rejected_static_review_state.py --output "$$(mktemp -d /tmp/php-spec-rejected-static.XXXXXXXX)/state"
	python3 tests/semantics/method_modifier_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-method-modifiers.XXXXXXXX)/sources"
	python3 tests/semantics/method_modifier_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-method-modifiers.XXXXXXXX)/main"
	python3 tests/semantics/rejected_method_modifier_review_state.py --output "$$(mktemp -d /tmp/php-spec-method-modifiers.XXXXXXXX)/state"
	python3 tests/semantics/constant_modifier_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-constant-modifiers.XXXXXXXX)/sources"
	python3 tests/semantics/constant_modifier_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-constant-modifiers.XXXXXXXX)/main"
	python3 tests/semantics/rejected_constant_modifier_review_state.py --output "$$(mktemp -d /tmp/php-spec-constant-modifiers.XXXXXXXX)/state"
	python3 tests/semantics/trait_alias_modifier_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-trait-alias-modifiers.XXXXXXXX)/sources"
	python3 tests/semantics/trait_alias_modifier_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-trait-alias-modifiers.XXXXXXXX)/main"
	python3 tests/semantics/rejected_trait_alias_modifier_review_state.py --output "$$(mktemp -d /tmp/php-spec-trait-alias-modifiers.XXXXXXXX)/state"
	python3 tests/semantics/property_hook_static_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-property-hook-static.XXXXXXXX)/sources"
	python3 tests/semantics/property_hook_static_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-property-hook-static.XXXXXXXX)/main"
	python3 tests/semantics/rejected_property_hook_static_review_state.py --output "$$(mktemp -d /tmp/php-spec-property-hook-static.XXXXXXXX)/state"
	python3 tests/semantics/multiproperty_hook_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-multiproperty-hook.XXXXXXXX)/sources"
	python3 tests/semantics/multiproperty_hook_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-multiproperty-hook.XXXXXXXX)/main"
	python3 tests/semantics/constant_attribute_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-constant-attributes.XXXXXXXX)/sources"
	python3 tests/semantics/constant_attribute_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-constant-attributes.XXXXXXXX)/main"
	python3 tests/semantics/anonymous_class_modifier_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-anonymous-class-modifiers.XXXXXXXX)/sources"
	python3 tests/semantics/anonymous_class_modifier_main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-anonymous-class-modifiers.XXXXXXXX)/main"
	python3 tests/semantics/attributed_constant_compile_sources.py --output "$$(mktemp -d /tmp/php-spec-attributed-constant-compile.XXXXXXXX)/sources"
	python3 tests/semantics/attributed_constant_compile_protocol.py --output "$$(mktemp -d /tmp/php-spec-attributed-constant-compile.XXXXXXXX)/protocol"
	python3 tests/semantics/single_attributed_constant_sources.py --output "$$(mktemp -d /tmp/php-spec-single-attributed-constant.XXXXXXXX)/sources"
	python3 tests/semantics/single_attributed_constant_protocol.py --output "$$(mktemp -d /tmp/php-spec-single-attributed-constant.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_global_constant_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-global-constant.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_global_constant_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-global-constant.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_owned_constant_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-owned-constant.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_parameter_default_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-parameter-default.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_method_default_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-method-default.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_method_default_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-method-default-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_this_class_constant_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-this-class-constant.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_this_owner_notice_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-this-owner-notice-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_this_class_constant_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-this-class-constant.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_this_owner_notice_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-this-owner-notice-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_object_rvalue_class_constant_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-rvalue-class-constant.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_object_selector_notice_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-selector-notice-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_object_rvalue_class_constant_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-rvalue-class-constant.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_object_selector_notice_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-selector-notice-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_object_class_computed_member_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-class-computed-member.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_object_member_notice_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-member-notice-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_object_class_computed_member_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-class-computed-member.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_object_member_notice_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-object-member-notice-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_class_string_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-class-string.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_selector_notice_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-selector-notice-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_class_string_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-class-string.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_selector_notice_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-selector-notice-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_class_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-class.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_notice_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-notice-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_class_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-class.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_notice_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-notice-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_string_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-string.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_string_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-string-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_string_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-string.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_string_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-string-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_string_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-string.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_string_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-string-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_string_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-string.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_string_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-string-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_float_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-float.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_float_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-float-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_float_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-float.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_float_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-float-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_int_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-int.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_int_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-int-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_int_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-int.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_int_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-int-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_bool_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-bool.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_bool_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-bool-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_bool_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-bool.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_bool_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-bool-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_false_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-false.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_false_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-false-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_false_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-false.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_false_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-false-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_true_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-true.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_true_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-true-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_true_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-true.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_true_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-true-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_null_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-null.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_null_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-null-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_null_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-null.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_null_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-null-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_nullable_primitive_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nullable-primitive.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_nullable_primitive_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nullable-primitive-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_nullable_primitive_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nullable-primitive.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_nullable_primitive_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nullable-primitive-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_primitive_union_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-primitive-union.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_primitive_union_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-primitive-union-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_primitive_union_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-primitive-union.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_primitive_union_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-primitive-union-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_class_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-class.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_class_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-class-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_typed_class_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-class.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_typed_class_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-typed-class-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_class_union_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-class-union.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_class_union_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-class-union-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_class_union_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-class-union.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_class_union_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-class-union-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_object_mixed_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-object-mixed.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_object_mixed_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-object-mixed-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_object_mixed_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-object-mixed.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_object_mixed_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-object-mixed-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_nominal_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nominal.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_nominal_dnf_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nominal-dnf-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_nominal_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nominal.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_nominal_dnf_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nominal-dnf-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_readonly_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-readonly.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_readonly_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-readonly-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_readonly_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-readonly.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_readonly_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-readonly-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_nonpublic_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nonpublic.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_nonpublic_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nonpublic-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_nonpublic_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nonpublic.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_nonpublic_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-nonpublic-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_modifiers_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-modifiers.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_modifiers_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-modifiers-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_modifiers_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-modifiers.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_modifiers_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-modifiers-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_hooks_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-hooks.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_backed_hook_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-backed-hook-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_hooks_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-hooks.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_backed_hook_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-backed-hook-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_short_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-short-set.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_short_set_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-short-set-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_short_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-short-set.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_short_set_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-short-set-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_get_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-get-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_get_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-get-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_explicit_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set-explicit.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_explicit_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set-explicit-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_explicit_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set-explicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_short_set_explicit_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-short-set-explicit-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_explicit_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-explicit.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_explicit_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-explicit-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_explicit_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-explicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_explicit_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-explicit-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_set_explicit_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-set-explicit.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_set_explicit_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-set-explicit-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_set_explicit_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-set-explicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_set_explicit_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-set-explicit-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_short_set_explicit_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-short-set-explicit.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_short_set_explicit_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-short-set-explicit-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_short_set_explicit_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-short-set-explicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_short_set_explicit_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-short-set-explicit-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-set.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_set_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-set-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-set.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_set_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-set-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_short_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-short-set.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_short_set_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-short-set-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_short_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-short-set.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_implicit_short_set_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-implicit-short-set-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_implicit_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-implicit-set-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/property_hook_pair_parameter_list_sources.py --output "$$(mktemp -d /tmp/php-spec-property-hook-pair-parameter-list-sources.XXXXXXXX)/source"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_implicit_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-implicit-set-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_pair_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-pair-review-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_implicit_default_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-implicit-default-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_pair_no_default_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-pair-no-default-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_implicit_default_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-implicit-default-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_pair_no_default_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-pair-no-default-review-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_short_set_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-short-set-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_short_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-short-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_short_set_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-short-set-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_short_pair_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-short-pair-review-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_short_get_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-short-get-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_both_short_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-both-short-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_short_get_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-short-get-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_short_get_protocol.py --kind block --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-short-get-block-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_short_get_protocol.py --kind short --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-short-get-short-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_short_get_pair_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-short-get-pair-review-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_actual_set_param_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-actual-set-param-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_actual_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-actual-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_actual_set_param_protocol.py --kind block --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-actual-set-param-protocol-block.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_pair_actual_set_param_protocol.py --kind short --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-pair-actual-set-param-protocol-short.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_hook_actual_pair_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-hook-actual-pair-review-protocol.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_trait_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-trait-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_trait_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-trait-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_trait_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-trait-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_trait_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-trait-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_trait_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-trait-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_trait_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-trait-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_trait_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-trait-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_repeated_trait_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-repeated-trait-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_repeated_trait_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-repeated-trait-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_repeated_trait_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-repeated-trait-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_repeated_trait_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-repeated-trait-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_repeated_trait_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-repeated-trait-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_repeated_trait_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-repeated-trait-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_trait_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-trait-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_trait_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-trait-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_trait_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-trait-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_trait_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-trait-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_trait_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-trait-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_trait_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-trait-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_class_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-class-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_class_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-class-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_class_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-class-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_class_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-class-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_class_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-class-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_set_backed_class_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-set-backed-class-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_trait_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-trait-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_trait_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-trait-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_trait_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-trait-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_trait_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-trait-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_trait_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-trait-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_trait_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-trait-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_class_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-class-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_class_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-class-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_class_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-class-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_class_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-class-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_class_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-class-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_automatic_short_set_class_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-automatic-short-set-class-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_class_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-class-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_class_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-class-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_class_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-class-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_class_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-class-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_class_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-class-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_parented_class_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-parented-class-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_same_name_parent_class_pairs_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-same-name-parent-class-pairs-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_same_name_parent_class_hook_pair_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-same-name-parent-class-hook-pair-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_untyped_same_name_parent_class_pairs_protocol.py --kind implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-same-name-parent-class-pairs-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_same_name_parent_class_pairs_protocol.py --kind actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-same-name-parent-class-pairs-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_same_name_parent_class_hook_pair_review_protocol.py --form implicit --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-same-name-parent-class-hook-pair-review-protocol-implicit.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_untyped_same_name_parent_class_hook_pair_review_protocol.py --form actual --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-untyped-same-name-parent-class-hook-pair-review-protocol-actual.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_unbacked_get_child_slots_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-unbacked-get-child-slots-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_unbacked_get_child_slot_review_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-unbacked-get-child-slot-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_unbacked_get_child_slots_protocol.py --kind short --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-unbacked-get-child-slots-protocol-short.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_unbacked_get_child_slots_protocol.py --kind block --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-unbacked-get-child-slots-protocol-block.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_unbacked_get_child_slot_review_protocol.py --form short --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-unbacked-get-child-slot-review-protocol-short.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_unbacked_get_child_slot_review_protocol.py --form block --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-unbacked-get-child-slot-review-protocol-block.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_get_child_slots_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-get-child-slots-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_backed_get_child_slot_review_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-get-child-slot-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_backed_get_child_slots_protocol.py --kind short --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-get-child-slots-protocol-short.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_get_child_slots_protocol.py --kind block --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-get-child-slots-protocol-block.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_get_child_slot_review_protocol.py --form short --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-get-child-slot-review-protocol-short.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_get_child_slot_review_protocol.py --form block --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-get-child-slot-review-protocol-block.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_reference_get_child_slots_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-reference-get-child-slots-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_backed_reference_get_child_slot_review_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-reference-get-child-slot-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_backed_reference_get_child_slots_protocol.py --kind initialized --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-reference-get-child-slots-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_reference_get_child_slots_protocol.py --kind null --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-reference-get-child-slots-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_reference_get_child_slot_review_protocol.py --form initialized --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-reference-get-child-slot-review-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_backed_reference_get_child_slot_review_protocol.py --form null --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-backed-reference-get-child-slot-review-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_sources.py --output "$$(mktemp -d /tmp/php-spec-parentless-short-reference-get-hook-sources.XXXXXXXX)/sources"
	python3 tests/semantics/parentless_short_reference_get_hook_review_sources.py --output "$$(mktemp -d /tmp/php-spec-parentless-short-reference-get-hook-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/parentless_short_reference_get_hook_protocol.py --form initialized --output "$$(mktemp -d /tmp/php-spec-parentless-short-reference-get-hook-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_protocol.py --form null --output "$$(mktemp -d /tmp/php-spec-parentless-short-reference-get-hook-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --form initialized --output "$$(mktemp -d /tmp/php-spec-parentless-short-reference-get-hook-review-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --form null --output "$$(mktemp -d /tmp/php-spec-parentless-short-reference-get-hook-review-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_literal_short_reference_get_hook_sources.py --output "$$(mktemp -d /tmp/php-spec-parentless-literal-short-reference-get-hook-sources.XXXXXXXX)/sources"
	python3 tests/semantics/parentless_literal_short_reference_get_hook_review_sources.py --output "$$(mktemp -d /tmp/php-spec-parentless-literal-short-reference-get-hook-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/parentless_short_reference_get_hook_protocol.py --body literal --form initialized --output "$$(mktemp -d /tmp/php-spec-parentless-literal-short-reference-get-hook-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_protocol.py --body literal --form null --output "$$(mktemp -d /tmp/php-spec-parentless-literal-short-reference-get-hook-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --form initialized --output "$$(mktemp -d /tmp/php-spec-parentless-literal-short-reference-get-hook-review-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --form null --output "$$(mktemp -d /tmp/php-spec-parentless-literal-short-reference-get-hook-review-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/ordinary_parent_short_reference_get_hook_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-sources.XXXXXXXX)/sources"
	python3 tests/semantics/ordinary_parent_short_reference_get_hook_review_sources.py --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-sources.XXXXXXXX)/sources"
	python3 tests/semantics/parentless_short_reference_get_hook_protocol.py --parented --form initialized --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-protocol-initialized.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_protocol.py --parented --form null --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-protocol-null.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --parented --form initialized --budget-part return --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-protocol-initialized-return.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --parented --form initialized --budget-part fetch --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-protocol-initialized-fetch.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --parented --form initialized --budget-part cleanup --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-protocol-initialized-cleanup.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --parented --form null --budget-part return --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-protocol-null-return.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --parented --form null --budget-part fetch --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-protocol-null-fetch.XXXXXXXX)/protocol"
	python3 tests/semantics/parentless_short_reference_get_hook_review_protocol.py --body literal --parented --form null --budget-part cleanup --output "$$(mktemp -d /tmp/php-spec-ordinary-parent-short-reference-get-hook-review-protocol-null-cleanup.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_float_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-float.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_float_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-float-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_float_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-float.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_float_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-float-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_property_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-property.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_property_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-property-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_property_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-property.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_property_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-property-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_scalar_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-scalar.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_scalar_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-scalar-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_scalar_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-scalar.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_scalar_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-scalar-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_fields_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-fields.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_fields_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-fields-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_fields_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-fields.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_fields_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-fields-review.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_graph_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-graph.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_graph_review_sources.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-graph-review.XXXXXXXX)/sources"
	python3 tests/semantics/deprecated_reference_object_graph_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-graph.XXXXXXXX)/protocol"
	python3 tests/semantics/deprecated_reference_object_graph_review_protocol.py --output "$$(mktemp -d /tmp/php-spec-deprecated-reference-object-graph-review.XXXXXXXX)/protocol"
	python3 tests/semantics/main_rejected_sources.py --output "$$(mktemp -d /tmp/php-spec-main-rejected.XXXXXXXX)/sources"
	python3 tests/main_rejected_source_review.py --output "$$(mktemp -d /tmp/php-spec-main-rejected.XXXXXXXX)/service"
	python3 tests/semantics/main_rejected_review_state.py --output "$$(mktemp -d /tmp/php-spec-main-rejected.XXXXXXXX)/state"
	python3 tests/semantics/rejected_encoding_state.py --output "$$(mktemp -d /tmp/php-spec-rejected-encoding.XXXXXXXX)/state"
	python3 tests/semantics/rejected_header_review_state.py --output "$$(mktemp -d /tmp/php-spec-rejected-encoding.XXXXXXXX)/review-state"
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
	python3 tests/semantics/generator_request_instance_child_sources.py --mode full
	python3 tests/semantics/generator_request_instance_child_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_reference_child_sources.py --mode full
	python3 tests/semantics/generator_request_reference_child_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_array_child_sources.py --mode full
	python3 tests/semantics/generator_request_array_child_protocol.py --mode check --sl
	python3 tests/semantics/generator_request_array_reference_child_sources.py --mode full
	python3 tests/semantics/generator_request_array_reference_child_protocol.py --mode check --sl
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
