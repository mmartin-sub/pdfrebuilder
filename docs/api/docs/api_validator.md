# api_validator

API reference validation system.

This module provides comprehensive validation of API references in documentation
against the actual codebase, ensuring that all documented APIs exist and are accurate.

## Classes

### APIReference

Represents an API reference found in documentation.

#### Methods

##### to_dict()

Convert to dictionary for JSON serialization.

### APIDefinition

Represents an API definition found in the codebase.

#### Methods

##### to_dict()

Convert to dictionary for JSON serialization.

### APIReferenceValidator

Validates API references against actual codebase.

#### Methods

##### __init__(project_root)

Initialize the API reference validator.

##### validate_all_api_references()

Validate all API references in documentation.

##### _scan_codebase()

Scan the codebase to build API definitions.

##### _scan_module_file(py_file)

Scan a single Python file for API definitions.

##### _scan_class_definition(class_node, module_name, py_file)

Scan a class definition for API information.

##### _scan_function_definition(func_node, module_name, py_file)

Scan a function definition for API information.

##### _scan_method_definition(method_node, class_name, py_file)

Scan a method definition for API information.

##### _get_function_signature(func_node)

Get function signature as string.

##### _validate_file_api_references(md_file)

Validate API references in a single documentation file.

##### _extract_api_references(content, file_path)

Extract API references from documentation content.

##### _extract_references_from_code(code, file_path, base_line)

Extract API references from code content.

##### _get_full_attribute_name(node)

Get the full name of an attribute access.

##### _validate_single_api_reference(reference)

Validate a single API reference.

##### _should_skip_reference(ref_name)

Check if a reference should be skipped.

##### _find_partial_matches(ref_name)

Find partial matches for a reference.

##### _is_external_reference(ref_name)

Check if a reference is to an external module.

##### get_api_coverage_report()

Generate an API coverage report.
