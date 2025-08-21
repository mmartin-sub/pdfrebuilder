# Multi-Format Document Engine Makefile

.PHONY: help docs docs-validate docs-test docs-build docs-clean test lint format

help:  ## Show this help message
	@echo "Multi-Format Document Engine - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Documentation targets
docs: docs-validate docs-test  ## Run all documentation tasks

docs-validate:  ## Validate documentation accuracy
	@echo "Validating documentation..."
	hatch run python scripts/validate_docs.py --all --verbose

docs-validate-examples:  ## Validate only code examples
	@echo "Validating code examples..."
	hatch run python scripts/validate_docs.py --examples --verbose

docs-validate-api:  ## Validate only API references
	@echo "Validating API references..."
	hatch run python scripts/validate_docs.py --api-refs --verbose

docs-validate-config:  ## Validate only configuration examples
	@echo "Validating configuration examples..."
	hatch run python scripts/validate_docs.py --config --verbose

docs-test:  ## Run documentation validation tests
	@echo "Running documentation tests..."
	hatch run pytest tests/test_documentation_validation.py tests/test_documentation_builder.py -v

docs-test-framework:  ## Run comprehensive documentation testing framework
	@echo "Running comprehensive documentation testing..."
	hatch run python scripts/test_docs_framework.py

docs-build:  ## Build complete documentation
	@echo "Building documentation..."
	hatch run python -c "from src.docs.validation import DocumentationBuilder; builder = DocumentationBuilder(); results = builder.build_complete_docs(); print('Documentation build completed')"

docs-workflow:  ## Run complete documentation workflow
	@echo "Running complete documentation workflow..."
	$(MAKE) docs-validate
	$(MAKE) docs-test
	$(MAKE) docs-build
	@echo "✅ Documentation workflow completed successfully"

docs-clean:  ## Clean generated documentation files
	@echo "Cleaning documentation artifacts..."
	find docs/ -name "*.tmp" -delete
	find docs/ -name "*.bak" -delete

# Development targets
test:  ## Run all tests
	hatch run pytest

test-docs:  ## Run only documentation-related tests
	hatch run pytest tests/test_documentation_validation.py -v

lint:  ## Run linting
	hatch run ruff check .

format:  ## Format code
	hatch run black .

ci:  ## Run all CI checks locally
	./scripts/ci.sh

# Installation and setup
install:  ## Install project dependencies
	hatch env create

clean:  ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Security testing targets
.PHONY: security-scan security-test security-validate security-all

security-scan:
	@echo "Running bandit security scan..."
	hatch run security-scan

security-test:
	@echo "Running security validation tests..."
	hatch run security-test

security-validate:
	@echo "Validating security configuration..."
	hatch run security-config-validate

security-all: security-scan security-test security-validate
	@echo "All security checks completed"

security-report:
	@echo "Generating security report..."
	mkdir -p reports
	hatch run security-scan-json
	@echo "Security report generated: reports/bandit_results.json"
