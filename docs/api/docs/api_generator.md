# api_generator

API Documentation Generator for Multi-Format Document Engine

This module provides automated generation of API documentation from Python source code,
extracting docstrings, type annotations, and generating markdown documentation.

## Classes

### ParameterInfo

Information about a function/method parameter

### MethodInfo

Information about a class method

#### Methods

##### __post_init__()

### ClassInfo

Information about a Python class

#### Methods

##### __post_init__()

### FunctionInfo

Information about a standalone function

#### Methods

##### __post_init__()

### ModuleInfo

Information about a Python module

#### Methods

##### __post_init__()

### APIDocumentationGenerator

Generates API documentation from Python source code

#### Methods

##### __init__(source_root)

##### extract_module_info(module_path)

Extract comprehensive information from a Python module

##### _get_module_name(module_path)

Get the module name from its path

##### _extract_class_info(node)

Extract information from a class definition

##### _extract_method_info(node)

Extract information from a method definition

##### _extract_function_info(node)

Extract information from a function definition

##### _extract_parameters(node)

Extract parameter information from a function/method

##### _extract_constants(node)

Extract constants from assignment nodes

##### _extract_imports(node)

Extract import statements

##### _get_annotation_string(annotation)

Convert an AST annotation to a string

##### _get_default_value_string(default)

Convert a default value AST to a string

##### _get_value_string(value)

Convert a value AST to a string

##### _get_name(node)

Get name from an AST node

##### _is_method(node, tree)

Check if a function is a method (inside a class)

##### _is_abstract_class(node)

Check if a class is abstract

##### _has_decorator(node, decorator_name)

Check if a function has a specific decorator

##### generate_markdown_documentation(module_info)

Generate markdown documentation for a module

##### _generate_class_documentation(class_info)

Generate documentation for a class

##### _generate_method_documentation(method_info, is_property)

Generate documentation for a method

##### _generate_function_documentation(function_info)

Generate documentation for a standalone function

##### generate_api_documentation(output_dir)

Generate complete API documentation for all modules

##### _generate_index_files()

Generate index files for API documentation

##### _generate_main_api_index()

Generate the main API documentation index

##### _generate_category_index(category)

Generate index for a specific category
