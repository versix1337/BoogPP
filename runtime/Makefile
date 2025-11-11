# Boogpp Runtime Library Makefile

# Compiler and flags
CC = gcc
AR = ar
CFLAGS = -Wall -Wextra -std=c11 -O2 -Iinclude
CFLAGS_DEBUG = -Wall -Wextra -std=c11 -g -O0 -Iinclude -DBPP_DEBUG

# Directories
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
TEST_DIR = tests
LIB_DIR = lib

# Source files
SOURCES = $(wildcard $(SRC_DIR)/*.c)
OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SOURCES))
OBJECTS_DEBUG = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%-debug.o,$(SOURCES))

# Library names
LIB_NAME = libboogpp_runtime.a
LIB_NAME_DEBUG = libboogpp_runtime_debug.a

# Test files
TEST_SOURCES = $(wildcard $(TEST_DIR)/*.c)
TEST_BINARIES = $(patsubst $(TEST_DIR)/%.c,$(BUILD_DIR)/%,$(TEST_SOURCES))

# Targets
.PHONY: all clean test debug release install

all: release

release: $(LIB_DIR)/$(LIB_NAME)

debug: $(LIB_DIR)/$(LIB_NAME_DEBUG)

# Create directories
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(LIB_DIR):
	mkdir -p $(LIB_DIR)

# Compile release objects
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Compile debug objects
$(BUILD_DIR)/%-debug.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS_DEBUG) -c $< -o $@

# Link release library
$(LIB_DIR)/$(LIB_NAME): $(OBJECTS) | $(LIB_DIR)
	$(AR) rcs $@ $^
	@echo "Built release library: $@"

# Link debug library
$(LIB_DIR)/$(LIB_NAME_DEBUG): $(OBJECTS_DEBUG) | $(LIB_DIR)
	$(AR) rcs $@ $^
	@echo "Built debug library: $@"

# Build tests
$(BUILD_DIR)/test_%: $(TEST_DIR)/test_%.c $(LIB_DIR)/$(LIB_NAME_DEBUG) | $(BUILD_DIR)
	$(CC) $(CFLAGS_DEBUG) $< -L$(LIB_DIR) -lboogpp_runtime_debug -o $@

# Run tests
test: $(TEST_BINARIES)
	@echo "Running tests..."
	@for test in $(TEST_BINARIES); do \
		echo "Running $$test..."; \
		$$test || exit 1; \
	done
	@echo "All tests passed!"

# Install library (optional)
install: $(LIB_DIR)/$(LIB_NAME)
	@echo "Installing Boogpp runtime library..."
	mkdir -p /usr/local/lib
	mkdir -p /usr/local/include
	cp $(LIB_DIR)/$(LIB_NAME) /usr/local/lib/
	cp $(INC_DIR)/boogpp_runtime.h /usr/local/include/
	@echo "Installation complete!"

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR) $(LIB_DIR)
	@echo "Cleaned build artifacts"

# Help
help:
	@echo "Boogpp Runtime Library Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make          - Build release library"
	@echo "  make release  - Build release library"
	@echo "  make debug    - Build debug library"
	@echo "  make test     - Build and run tests"
	@echo "  make install  - Install library to /usr/local"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make help     - Show this help"
