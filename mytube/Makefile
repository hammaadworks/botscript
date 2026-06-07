# Wgetube Master Makefile

.PHONY: help install run-tui run-download run-clip clean

help:
	@echo "Wgetube CLI/TUI Development Commands:"
	@echo "  make install         - Install all dependencies with uv"
	@echo "  make run-tui         - Start the Professional TUI Dashboard"
	@echo "  make run-download    - Start the Interactive CLI Downloader"
	@echo "  make clean           - Remove build artifacts and caches"

install:
	@echo "Installing dependencies with uv..."
	uv sync

run-tui:
	@echo "Launching Wgetube TUI..."
	uv run cli/main.py tui

run-download:
	@echo "Launching Wgetube Interactive Downloader..."
	uv run cli/main.py download

clean:
	@echo "Cleaning up..."
	rm -rf cli/__pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
