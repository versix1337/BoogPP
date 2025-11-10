# Boogpp Programming Language - Master Build System
# Complete build for compiler, runtime, and standard library

.PHONY: all clean test install runtime stdlib compiler examples docs help

# Configuration
PYTHON := python3
CC := gcc
AR := ar

# Directories
RUNTIME_DIR := boogpp/runtime
STDLIB_DIR := boogpp/stdlib/windows
COMPILER_DIR := boogpp/compiler
EXAMPLES_DIR := boogpp/examples
DOCS_DIR := boogpp/docs

# Installation paths
INSTALL_PREFIX := /usr/local
INSTALL_LIB := $(INSTALL_PREFIX)/lib
INSTALL_INCLUDE := $(INSTALL_PREFIX)/include/boogpp
INSTALL_BIN := $(INSTALL_PREFIX)/bin

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m

# Default target
all: runtime stdlib compiler
	@echo "$(GREEN)✓ Boogpp build complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Built components:$(NC)"
	@echo "  - Runtime library (libboogpp_runtime.a)"
	@echo "  - Windows standard library (libboogpp_windows.a)"
	@echo "  - Boogpp compiler (Python)"
	@echo ""
	@echo "$(YELLOW)Run 'make install' to install system-wide$(NC)"
	@echo "$(YELLOW)Run 'make test' to run all tests$(NC)"

# Build runtime library
runtime:
	@echo "$(BLUE)Building runtime library...$(NC)"
	@cd $(RUNTIME_DIR) && $(MAKE) release
	@echo "$(GREEN)✓ Runtime library built$(NC)"

# Build standard library
stdlib: runtime
	@echo "$(BLUE)Building Windows standard library...$(NC)"
	@cd $(STDLIB_DIR) && $(MAKE) -f ../../Makefile.stdlib release
	@echo "$(GREEN)✓ Standard library built$(NC)"

# Install compiler (just ensure it's importable)
compiler:
	@echo "$(BLUE)Setting up Boogpp compiler...$(NC)"
	@cd boogpp && $(PYTHON) -c "from compiler import __version__; print(f'Compiler version: {__version__}')"
	@echo "$(GREEN)✓ Compiler ready (version $$(cd boogpp && $(PYTHON) -c 'from compiler import __version__; print(__version__)'))$(NC)"

# Run all tests
test: runtime stdlib
	@echo "$(BLUE)Running test suite...$(NC)"
	@echo ""
	@echo "$(YELLOW)Testing runtime library...$(NC)"
	@cd $(RUNTIME_DIR) && $(MAKE) test
	@echo ""
	@echo "$(YELLOW)Testing compiler...$(NC)"
	@cd boogpp && $(PYTHON) test_compiler.py
	@echo ""
	@echo "$(YELLOW)Testing type checker...$(NC)"
	@cd boogpp && $(PYTHON) test_phase2.py
	@echo ""
	@echo "$(GREEN)✓ All tests passed!$(NC)"

# Build example programs
examples: runtime stdlib compiler
	@echo "$(BLUE)Building example programs...$(NC)"
	@for example in $(EXAMPLES_DIR)/*.bpp; do \
		echo "  Compiling $$(basename $$example)..."; \
		$(PYTHON) -m boogpp.compiler.cli build $$example -v || true; \
	done
	@echo "$(GREEN)✓ Examples processed$(NC)"

# Generate documentation
docs:
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "Documentation files:"
	@ls -1 $(DOCS_DIR)/*.md README.md BRANCHES.md | sed 's/^/  /'
	@echo "$(GREEN)✓ Documentation ready$(NC)"

# Install system-wide
install: all
	@echo "$(BLUE)Installing Boogpp system-wide...$(NC)"
	@echo ""

	# Create directories
	@echo "Creating installation directories..."
	@mkdir -p $(INSTALL_LIB)
	@mkdir -p $(INSTALL_INCLUDE)
	@mkdir -p $(INSTALL_BIN)

	# Install runtime library
	@echo "Installing runtime library..."
	@cp $(RUNTIME_DIR)/lib/libboogpp_runtime.a $(INSTALL_LIB)/
	@cp $(RUNTIME_DIR)/include/boogpp_runtime.h $(INSTALL_INCLUDE)/

	# Install Windows standard library
	@echo "Installing Windows standard library..."
	@cp $(STDLIB_DIR)/lib/libboogpp_windows.a $(INSTALL_LIB)/
	@cp $(STDLIB_DIR)/include/boogpp_windows.h $(INSTALL_INCLUDE)/

	# Install compiler wrapper script
	@echo "Installing compiler..."
	@echo '#!/bin/bash' > $(INSTALL_BIN)/boogpp
	@echo 'BOOGPP_PATH="$(PWD)"' >> $(INSTALL_BIN)/boogpp
	@echo 'export PYTHONPATH="$$BOOGPP_PATH:$$PYTHONPATH"' >> $(INSTALL_BIN)/boogpp
	@echo 'python3 -m boogpp.compiler.cli "$$@"' >> $(INSTALL_BIN)/boogpp
	@chmod +x $(INSTALL_BIN)/boogpp

	@echo ""
	@echo "$(GREEN)✓ Installation complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Installed to:$(NC)"
	@echo "  Libraries: $(INSTALL_LIB)"
	@echo "  Headers:   $(INSTALL_INCLUDE)"
	@echo "  Compiler:  $(INSTALL_BIN)/boogpp"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  boogpp build program.bpp -o program.exe"
	@echo "  boogpp check program.bpp"
	@echo "  boogpp version"

# Uninstall
uninstall:
	@echo "$(YELLOW)Uninstalling Boogpp...$(NC)"
	@rm -f $(INSTALL_LIB)/libboogpp_runtime.a
	@rm -f $(INSTALL_LIB)/libboogpp_windows.a
	@rm -f $(INSTALL_INCLUDE)/boogpp_runtime.h
	@rm -f $(INSTALL_INCLUDE)/boogpp_windows.h
	@rm -f $(INSTALL_BIN)/boogpp
	@rmdir $(INSTALL_INCLUDE) 2>/dev/null || true
	@echo "$(GREEN)✓ Uninstallation complete$(NC)"

# Clean all build artifacts
clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@cd $(RUNTIME_DIR) && $(MAKE) clean 2>/dev/null || true
	@rm -rf $(STDLIB_DIR)/build $(STDLIB_DIR)/lib 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find $(EXAMPLES_DIR) -type f -name "*.ll" -delete
	@echo "$(GREEN)✓ Clean complete$(NC)"

# Development setup
dev-setup:
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements-dev.txt 2>/dev/null || echo "No dev requirements found"
	@echo "$(GREEN)✓ Development environment ready$(NC)"

# Quick check - verify everything is working
check: test
	@echo ""
	@echo "$(GREEN)✓ Boogpp is working correctly!$(NC)"

# Help
help:
	@echo "$(BLUE)Boogpp Build System$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  make                - Build all components (default)"
	@echo "  make runtime        - Build runtime library only"
	@echo "  make stdlib         - Build standard library only"
	@echo "  make compiler       - Setup compiler only"
	@echo "  make test           - Run all tests"
	@echo "  make examples       - Build example programs"
	@echo "  make docs           - Generate documentation"
	@echo "  make install        - Install system-wide"
	@echo "  make uninstall      - Remove system installation"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make dev-setup      - Setup development environment"
	@echo "  make check          - Quick check (runs tests)"
	@echo "  make help           - Show this help"
	@echo ""
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Version: 3.0.0"
	@echo "  Language: Boogpp"
	@echo "  License: MIT"
	@echo ""
	@echo "$(YELLOW)For more information, see README.md$(NC)"
