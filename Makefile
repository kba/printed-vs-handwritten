PPNS ?= ppns
EXTRACT_GRP ?= TESS-LINES
PYTHON ?= python3

.PHONY: extract
extract:
	@set -eu; \
	found=0; \
	for workspace in "$(PPNS)"/PPN*; do \
		[ -d "$$workspace" ] || continue; \
		found=1; \
		[ -f "$$workspace/mets.xml" ] || { echo "Missing $$workspace/mets.xml" >&2; exit 1; }; \
		echo "Extracting lines from $$workspace"; \
		( cd "$$workspace"; \
		  $(PYTHON) "$(abspath scripts/add_default_images.py)"; \
		  ocrd-segment-extract-lines -m mets.xml -I TESS -O "$(EXTRACT_GRP)" --overwrite ); \
	done; \
	[ "$$found" -eq 1 ] || { echo "No PPN workspaces found in $(PPNS)" >&2; exit 1; }
