# Wgetube Master Makefile

.PHONY: help install run-tui run-web build-web clean

help:
	@echo "Wgetube Development Commands:"
	@echo "  make install    - Install all dependencies (CLI & Web)"
	@echo "  make run-tui    - Start the Pro TUI Dashboard"
	@echo "  make run-web    - Start the Web GUI (Development)"
	@echo "  make build-web  - Build the Web GUI for production"
	@echo "  make clean      - Remove build artifacts and caches"

install:
	@echo "Installing CLI dependencies with uv..."
	uv sync
	@echo "Installing Web dependencies with pnpm..."
	cd web && pnpm install

run-tui:
	@echo "Launching Wgetube TUI..."
	uv run cli/main.py tui

run-interactive:
	@echo "Launching Wgetube Interactive Downloader..."
	uv run cli/main.py interactive

run-web:
	@echo "Launching Web App at http://localhost:5173..."
	cd web && pnpm dev

build-web:
	@echo "Building Web App for production..."
	cd web && pnpm build

clean:
	@echo "Cleaning up..."
	rm -rf web/dist
	rm -rf cli/__pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
