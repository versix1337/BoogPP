# Branch Organization

This repository uses a structured branching strategy to organize development phases and features.

## Branch Structure

### Main Branches

#### `main`
- **Purpose**: Latest stable release
- **Contains**: Complete, tested features with full rebranding to Boogpp
- **File Extension**: `.bpp`
- **Status**: Production-ready code
- **Update Policy**: Only merge from phase branches after thorough testing

#### `dev`
- **Purpose**: Active development branch
- **Contains**: Latest features being developed and tested
- **Merge From**: Feature branches and phase branches
- **Merge To**: `main` when stable
- **Status**: May contain experimental features

### Phase Branches

#### `phase-1-foundation`
- **Purpose**: Core language foundation
- **Features**:
  - Lexer (tokenization)
  - Parser (AST generation)
  - Basic Safety Checker (SAFE/UNSAFE/CUSTOM modes)
  - Basic type system definitions
  - CLI interface
- **Status**: ✅ Complete
- **Version**: 1.0.0

#### `phase-2-advanced`
- **Purpose**: Advanced type system and code generation
- **Features**:
  - Type Checker (full type inference and checking)
  - Enhanced Safety Enforcement
  - LLVM Code Generation (IR output)
  - Advanced safety rules
  - Type annotations
- **Status**: ✅ Complete
- **Version**: 2.0.0

#### Future Phases (Planned)

##### `phase-3-runtime`
- Runtime library implementation
- Memory management
- Standard library completion

##### `phase-4-windows-api`
- Complete Windows API bindings
- System hooks implementation
- Service creation utilities

##### `phase-5-optimization`
- Advanced LLVM optimizations
- Performance profiling
- Binary generation

##### `phase-6-tooling`
- Debugger integration
- IDE support (VS Code extension)
- Package manager

## Workflow

### For New Features
```bash
# Create feature branch from dev
git checkout dev
git checkout -b feature/your-feature-name

# Work on feature
# ... make changes ...

# When ready, merge back to dev
git checkout dev
git merge feature/your-feature-name
```

### For Phase Development
```bash
# Create phase branch from previous phase or main
git checkout phase-2-advanced
git checkout -b phase-3-runtime

# Develop phase features
# ... implement phase 3 ...

# When phase is complete, merge to dev
git checkout dev
git merge phase-3-runtime

# After testing in dev, merge to main
git checkout main
git merge dev
```

### For Bug Fixes
```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/issue-description

# Fix issue
# ... make fixes ...

# Merge to both main and dev
git checkout main
git merge hotfix/issue-description
git checkout dev
git merge hotfix/issue-description
```

## Branch Naming Conventions

- **Phase branches**: `phase-N-description` (e.g., `phase-3-runtime`)
- **Feature branches**: `feature/short-description` (e.g., `feature/add-string-interpolation`)
- **Bug fix branches**: `bugfix/issue-description` (e.g., `bugfix/lexer-indent-error`)
- **Hotfix branches**: `hotfix/critical-issue` (e.g., `hotfix/memory-leak`)
- **Experimental branches**: `experiment/idea-name` (e.g., `experiment/jit-compilation`)

## Current Status

| Branch | Status | Version | Last Update |
|--------|--------|---------|-------------|
| `main` | ✅ Stable | 2.0.0 | 2025-11-10 |
| `dev` | 🚧 Active | 2.0.0 | 2025-11-10 |
| `phase-1-foundation` | ✅ Complete | 1.0.0 | 2025-11-10 |
| `phase-2-advanced` | ✅ Complete | 2.0.0 | 2025-11-10 |

## Guidelines

1. **Never commit directly to `main`** - Always merge through `dev`
2. **Keep phase branches focused** - Each phase should have clear, defined goals
3. **Test before merging** - Run all tests before merging to `dev` or `main`
4. **Document changes** - Update relevant documentation with each phase
5. **Use descriptive commit messages** - Follow conventional commits format
6. **Clean up old branches** - Delete feature branches after merging

## Rebranding Note

All branches now use the **Boogpp** naming and **.bpp** file extension (formerly CustomOS/.cos).
This rebranding was completed on 2025-11-10 and affects all branches uniformly.

## Questions or Issues?

For questions about branch structure or to propose changes, please open an issue.
