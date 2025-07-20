# coverage_reporter

Documentation coverage reporting system.

This module provides comprehensive reporting on documentation coverage,
including API documentation, code examples, and guide completeness.

## Classes

### CoverageMetrics

Documentation coverage metrics.

#### Methods

##### to_dict()

Convert to dictionary for JSON serialization.

### ModuleCoverage

Coverage information for a single module.

#### Methods

##### to_dict()

Convert to dictionary for JSON serialization.

### DocumentationCoverageReporter

Generates comprehensive documentation coverage reports.

#### Methods

##### __init__(project_root)

Initialize the coverage reporter.

##### generate_coverage_report()

Generate a comprehensive coverage report.

##### _analyze_api_coverage()

Analyze API documentation coverage.

##### _analyze_module_coverage(py_file)

Analyze coverage for a single module.

##### _analyze_class_coverage(class_node)

Analyze documentation coverage for a class.

##### _analyze_function_coverage(func_node, is_method)

Analyze documentation coverage for a function or method.

##### _calculate_module_coverage_score(has_module_docstring, classes, functions)

Calculate coverage score for a module.

##### _analyze_docs_completeness()

Analyze completeness of documentation files.

##### _analyze_examples_coverage()

Analyze code examples coverage.

##### _extract_code_examples_for_coverage(content)

Extract code examples for coverage analysis.

##### _calculate_overall_metrics(api_coverage)

Calculate overall coverage metrics.

##### _generate_recommendations(metrics, api_coverage)

Generate recommendations for improving documentation coverage.

##### export_coverage_report(output_path, report)

Export coverage report to JSON file.

##### print_coverage_summary(report)

Print a summary of the coverage report.
