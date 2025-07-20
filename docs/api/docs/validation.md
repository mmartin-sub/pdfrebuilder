# validation

Documentation validation framework for the Multi-Format Document Engine.

This module provides tools to validate documentation accuracy against the current codebase,
including code example execution, API reference validation, and configuration verification.

## Classes

### ValidationStatus

Status of validation results.

### ValidationResult

Result of a validation operation.

### CodeExample

Code example with validation metadata.

### SecureCodeExecutor

Secure code execution environment with sandboxing.

#### Methods

##### __init__()

##### validate_code_safety(code)

Validate that code doesn't contain dangerous operations.

##### create_safe_globals()

Create a safe globals dictionary with restricted access.

##### execute_safely(code, timeout)

Execute code in a safe environment.

### DocumentationValidator

Validates documentation content for correctness and safety.

#### Methods

##### __init__(project_root)

Initialize the validator.

##### _load_validation_config()

Load validation configuration from config file.

##### validate_code_examples(doc_path)

Validate code examples in documentation files.

##### validate_api_references(doc_path)

Validate that API references match actual implementation.

Args:
    doc_path: Path to documentation file

Returns:
    List of validation results

##### validate_configuration_examples(doc_path)

Validate that configuration examples are valid.

Args:
    doc_path: Path to documentation file

Returns:
    List of validation results

##### _extract_code_examples(content, file_path)

Extract code examples from markdown content.

##### _validate_single_example(example)

Validate a single code example.

##### _extract_api_references(content)

Extract API references from documentation content.

##### _validate_api_reference(api_ref, file_path)

Validate a single API reference.

##### _extract_configuration_examples(content)

Extract configuration examples from documentation content.

##### _validate_configuration_example(config_example, file_path)

Validate a single configuration example.

### DocumentationBuilder

Builds complete documentation from sources.

#### Methods

##### __init__(project_root)

Initialize builder with project root directory.

##### build_api_docs()

Generate API documentation from source code.

##### build_user_guides()

Process and validate user guide content.

##### build_examples()

Generate and validate example code.

##### build_complete_docs()

Build complete documentation set.

##### _extract_module_documentation(py_file)

Extract documentation from a Python module.

##### _generate_api_doc_file(py_file, module_doc)

Generate API documentation file from module documentation.

##### _generate_api_markdown(module_doc)

Generate markdown content for API documentation.

##### _generate_basic_examples()

Generate basic code examples.

## Functions

### main()

Main entry point for documentation validation.
