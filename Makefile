.PHONY: deps build schema test validate inventory

deps:
	./scripts/build-deps.sh

build:
	./scripts/build-file-helper.sh
	./scripts/opam-exec.sh dune build

schema:
	.tools/php/bin/php -n scripts/node-inventory.php > spec/nodes.json
	python3 scripts/generate-schema.py
	python3 scripts/encoding-inventory.py

test: build
	.tools/php/bin/php -n -d extension=$(CURDIR)/.tools/php-file.so -d zend.multibyte=1 -d internal_encoding=UTF-8 tests/native-file.php
	python3 tests/validate_extraction.py
	python3 tests/malformed.py
	python3 tests/wire_negative.py
	python3 tests/encoding_mutation.py
	python3 tests/validate.py --elaborate --lint-all
	python3 tests/validate.py --generated --output coverage/results-generated.jsonl
	python3 tests/validate.py --corpus --match stack_limit_013 --output coverage/results-deep.jsonl

validate: build
	python3 tests/validate.py --corpus --lint-all --output coverage/results-corpus.jsonl

inventory: build
	python3 tests/build_coverage.py
	python3 tests/grammar_coverage.py
	python3 scripts/grammar-mapping.py
	python3 scripts/scanner-mapping.py
