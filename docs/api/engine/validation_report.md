# validation_report

Validation report module for the Multi-Format Document Engine.

This module provides functionality for generating validation reports
when comparing original and regenerated documents. It includes comprehensive
metrics, failure analysis, and machine-readable output for CI/CD integration.

## Classes

### XMLSecurityConfig

Configuration for XML security settings

### XMLSecurityAuditEntry

Audit log entry for XML security events

#### Methods

##### to_dict()

Convert to dictionary for JSON serialization

### XMLSecurityError

Raised when XML security issues are detected

### XMLParsingError

Raised when XML parsing fails due to security restrictions

### ValidationResult

Validation result for document comparison with comprehensive metrics and analysis

#### Methods

##### __init__(passed, ssim_score, threshold, original_path, generated_path, diff_image_path, details, failure_analysis, additional_metrics)

##### _generate_failure_analysis()

Generate failure analysis based on available metrics

##### _determine_failure_reason()

Determine the reason for validation failure

##### _calculate_failure_severity()

Calculate the severity of the validation failure

##### _generate_recommendations()

Generate recommendations based on failure analysis

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

##### save_report(output_path)

Save validation report to file

##### load_report(cls, file_path)

Load validation report from file

##### get_exit_code()

Get exit code for CI/CD integration (0 = success, 1 = failure)

### ValidationReport

Comprehensive validation report for document comparison with CI/CD integration

#### Methods

##### __init__(document_name, results, metadata, report_id)

##### to_dict()

Convert to dictionary

##### _generate_failure_summary()

Generate a summary of failures

##### from_dict(cls, data)

Create from dictionary

##### save_report(output_path)

Save validation report to file

##### load_report(cls, file_path)

Load validation report from file

##### get_summary()

Get summary of validation results

##### get_exit_code()

Get exit code for CI/CD integration (0 = success, 1 = failure)

##### generate_html_report(output_path)

Generate HTML validation report

##### _generate_font_validation_html(font_validation)

Generate HTML section for font validation information

##### generate_junit_report(output_path)

Generate JUnit XML report for CI/CD integration with secure XML parsing

Args:
    output_path: Path to save the JUnit XML report

Raises:
    XMLSecurityError: When XML security violations are detected
    XMLParsingError: When XML parsing fails

##### generate_markdown_report(output_path)

Generate Markdown report

Args:
    output_path: Path to save the Markdown report

## Functions

### html_escape(text)

Escape HTML special characters to prevent XSS attacks

### _check_fallback_security_constraints(xml_content)

Basic security checks when defusedxml is not available

This function provides basic security validation for XML content when
the secure defusedxml library is not available. It checks for common
attack patterns and provides warnings.

Args:
    xml_content: XML content to check

Returns:
    List of security warnings/issues found

### configure_xml_security(config)

Configure defusedxml with security settings

Args:
    config: XMLSecurityConfig instance, uses global config if None

### secure_xml_parse(xml_content)

Securely parse XML content with comprehensive error handling

Args:
    xml_content: XML content as string

Returns:
    Parsed XML element

Raises:
    XMLSecurityError: When malicious XML content is detected
    XMLParsingError: When XML parsing fails

### secure_xml_pretty_print(element)

Securely pretty print XML with comprehensive error handling and fallback mechanisms

Args:
    element: XML element to pretty print

Returns:
    Pretty-printed XML string

Raises:
    XMLParsingError: When XML pretty printing fails completely

### _manual_xml_serialization(element)

Manual XML serialization as a last resort fallback

Args:
    element: XML element to serialize

Returns:
    Basic XML string representation

### log_xml_security_event(event_type, details, severity)

Log XML security events for monitoring

Args:
    event_type: Type of security event (e.g., "blocked_xxe", "blocked_bomb", "parsing_error")
    details: Dictionary containing event details
    severity: Severity level ("low", "medium", "high", "critical")

### _write_security_audit_log(audit_entry)

Write security audit entry to dedicated security log file

Args:
    audit_entry: The security audit entry to log

### get_xml_security_status()

Get current XML security status and configuration

Returns:
    Dictionary containing security status information

### validate_xml_security_environment()

Validate the XML security environment and return status with any issues

Returns:
    Tuple of (is_secure, list_of_issues)

### get_informative_security_error_message(error_type, error_details)

Generate informative error messages for XML security violations

Args:
    error_type: Type of security error
    error_details: Details about the error

Returns:
    Informative error message for users

### create_validation_result(ssim_score, threshold, original_path, generated_path, diff_image_path, details, failure_analysis, additional_metrics)

Create a validation result with comprehensive metrics and analysis

Args:
    ssim_score: SSIM score (0.0-1.0)
    threshold: SSIM threshold for passing
    original_path: Path to original document
    generated_path: Path to generated document
    diff_image_path: Path to difference image
    details: Additional details
    failure_analysis: Detailed analysis of validation failures
    additional_metrics: Additional numerical metrics

Returns:
    ValidationResult object

### create_validation_report(document_name, results, metadata, report_id)

Create a comprehensive validation report with CI/CD integration

Args:
    document_name: Name of the document
    results: List of validation results
    metadata: Additional metadata
    report_id: Unique identifier for the report

Returns:
    ValidationReport object

### generate_validation_report(original_path, generated_path, validation_result, output_dir, report_formats, font_validation_result)

Generate comprehensive validation reports in multiple formats.

Args:
    original_path: Path to the original document
    generated_path: Path to the generated document
    validation_result: Validation result object
    output_dir: Directory to save reports
    report_formats: List of report formats to generate (json, html, ci)
    font_validation_result: Optional font validation result to include in reports

Returns:
    Dictionary mapping report formats to their file paths
