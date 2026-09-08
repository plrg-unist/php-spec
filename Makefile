.PHONY: deps build schema

deps:
	./scripts/build-deps.sh

build:
	./scripts/opam-exec.sh dune build

schema:
	.tools/php/bin/php -n scripts/node-inventory.php > spec/nodes.json
	python3 scripts/generate-schema.py
