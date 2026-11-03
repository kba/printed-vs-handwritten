PPNS ?= ppns
EXTRACT_GRP ?= TESS_LINES
CLASSIFY_GRP ?= PRINTED_VS_HANDWRITTEN
PYTHON ?= python3

.PHONY: prepare-workspaces extract classify
prepare-workspaces:
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

extract:
	@set -eu; \
	found=0; \
	for workspace in "$(PPNS)"/PPN*; do \
		[ -d "$$workspace" ] || continue; \
		found=1; \
		[ -f "$$workspace/mets.xml" ] || { echo "Missing $$workspace/mets.xml" >&2; exit 1; }; \
		echo "Extracting lines from $$workspace"; \
		( cd "$$workspace"; ocrd-segment-extract-lines -m mets.xml -I TESS -O "$(EXTRACT_GRP)" --overwrite ); \
	done; \
	[ "$$found" -eq 1 ] || { echo "No PPN workspaces found in $(PPNS)" >&2; exit 1; }

classify:
	@set -eu; \
	found=0; \
	for workspace in "$(PPNS)"/PPN*; do \
		[ -d "$$workspace" ] || continue; \
		found=1; \
		[ -f "$$workspace/mets.xml" ] || { echo "Missing $$workspace/mets.xml" >&2; exit 1; }; \
		echo "Classifying lines in $$workspace"; \
		( cd "$$workspace"; $(PYTHON) "$(abspath scripts/classify_lines.py)" \
		  "$(EXTRACT_GRP)" "$(CLASSIFY_GRP)" ); \
	done; \
	[ "$$found" -eq 1 ] || { echo "No PPN workspaces found in $(PPNS)" >&2; exit 1; }
