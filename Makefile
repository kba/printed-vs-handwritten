PPNS ?= ppns
EXTRACT_GRP ?= TESS_LINES
CLASSIFY_GRP ?= PRINTED_VS_HANDWRITTEN
PYTHON ?= python3
JOBS ?= 4
THRESHOLD ?= 0.5
AGGREGATE_OUTPUT ?= csv

.DEFAULT_GOAL := help
.PHONY: help prepare-workspaces extract classify aggregate

help: ## Show available targets
	@awk 'BEGIN { FS = ":.*## " } /^[a-zA-Z0-9_.-]+:.*## / { printf "%-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

prepare-workspaces: ## Register DEFAULT images in each PPN workspace
	@set -eu; \
	found=0; \
	for workspace in "$(PPNS)"/PPN*; do \
		[ -d "$$workspace" ] || continue; \
		found=1; \
		[ -f "$$workspace/mets.xml" ] || { echo "Missing $$workspace/mets.xml" >&2; exit 1; }; \
		echo "Preparing $$workspace"; \
		( cd "$$workspace"; $(PYTHON) "$(abspath scripts/add_default_images.py)" ); \
	done; \
	[ "$$found" -eq 1 ] || { echo "No PPN workspaces found in $(PPNS)" >&2; exit 1; }

extract: ## Extract TESS line images into TESS_LINES
	@set -eu; \
	found=0; \
	for workspace in "$(PPNS)"/PPN*; do \
		[ -d "$$workspace" ] || continue; \
		found=1; \
		[ -f "$$workspace/mets.xml" ] || { echo "Missing $$workspace/mets.xml" >&2; exit 1; }; \
		echo "Extracting lines from $$workspace"; \
		( cd "$$workspace"; ocrd-segment-extract-lines --overwrite -P output-types '[]' -m mets.xml -I TESS -O "$(EXTRACT_GRP)" --overwrite ); \
	done; \
	[ "$$found" -eq 1 ] || { echo "No PPN workspaces found in $(PPNS)" >&2; exit 1; }

classify: ## Classify line images and register JSON results in METS
	@set -eu; \
	found=0; \
	for workspace in "$(PPNS)"/PPN*; do \
		[ -d "$$workspace" ] || continue; \
		found=1; \
		[ -f "$$workspace/mets.xml" ] || { echo "Missing $$workspace/mets.xml" >&2; exit 1; }; \
		echo "Classifying lines in $$workspace"; \
		( cd "$$workspace"; $(PYTHON) "$(abspath scripts/classify_lines.py)" \
		  "$(EXTRACT_GRP)" "$(CLASSIFY_GRP)" "$(JOBS)" ); \
	done; \
	[ "$$found" -eq 1 ] || { echo "No PPN workspaces found in $(PPNS)" >&2; exit 1; }

aggregate: ## Summarize per-line classification scores by PPN
	@$(PYTHON) "$(abspath scripts/aggregate.py)" "$(PPNS)" "$(CLASSIFY_GRP)" "$(abspath ground-truth.json)" "$(THRESHOLD)" --output "$(AGGREGATE_OUTPUT)"
