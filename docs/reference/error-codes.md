# Error Codes Reference

This document provides a comprehensive reference for error codes and messages in the Multi-Format Document Engine.

## Table of Contents

- [Overview](#overview)
- [Error Categories](#error-categories)
- [PDF Processing Errors (PDF_*)](#pdf-processing-errors-pdf_)
- [PSD Processing Errors (PSD_*)](#psd-processing-errors-psd_)
- [Configuration Errors (CONFIG_*)](#configuration-errors-config_)
- [Validation Errors (VALID_*)](#validation-errors-valid_)
- [Font Management Errors (FONT_*)](#font-management-errors-font_)
- [File System Errors (FS_*)](#file-system-errors-fs_)
- [Memory and Performance Errors (MEM_*)](#memory-and-performance-errors-mem_)

## Overview

The Multi-Format Document Engine uses structured error codes to help identify and resolve issues quickly. Error codes follow the format `CATEGORY_SPECIFIC_CODE` where:

- `CATEGORY` indicates the general area (PDF, PSD, CONFIG, etc.)
- `SPECIFIC_CODE` provides detailed information about the specific error

## Error Categories

### PDF Processing Errors (PDF_*) {#pdf-processing-errors-pdf_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `PDF_PARSE_001` | Failed to open PDF file | PDF file is corrupted or inaccessible | Verify file integrity and permissions |
| `PDF_PARSE_002` | Invalid PDF structure | PDF has malformed internal structure | Try with a different PDF or repair the file |
| `PDF_PARSE_003` | Unsupported PDF version | PDF version is not supported | Convert to a supported PDF version |
| `PDF_EXTRACT_001` | Text extraction failed | Unable to extract text from PDF | Check if PDF has text layer or is image-based |
| `PDF_EXTRACT_002` | Image extraction failed | Unable to extract images from PDF | Verify PDF contains extractable images |
| `PDF_EXTRACT_003` | Font extraction failed | Unable to extract font information | PDF may use embedded or system fonts |
| `PDF_RENDER_001` | PDF generation failed | Unable to create output PDF | Check output directory permissions |
| `PDF_RENDER_002` | Font rendering error | Font not available for rendering | Install required fonts or use font substitution |

### PSD Processing Errors (PSD_*) {#psd-processing-errors-psd_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `PSD_PARSE_001` | Failed to open PSD file | PSD file is corrupted or inaccessible | Verify file integrity and permissions |
| `PSD_PARSE_002` | Unsupported PSD version | PSD version is not supported | Save PSD in compatible format |
| `PSD_LAYER_001` | Layer extraction failed | Unable to extract layer information | Check PSD layer structure |
| `PSD_TEXT_001` | Text layer processing failed | Unable to process text layers | Verify text layers are not rasterized |
| `PSD_EFFECT_001` | Layer effect not supported | Layer effect cannot be processed | Simplify layer effects or rasterize |

### Configuration Errors (CONFIG_*) {#configuration-errors-config_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `CONFIG_PARSE_001` | Invalid JSON configuration | Configuration file has syntax errors | Validate JSON syntax |
| `CONFIG_PARSE_002` | Missing required configuration | Required configuration keys are missing | Add missing configuration keys |
| `CONFIG_VALIDATE_001` | Invalid configuration value | Configuration value is out of range or invalid | Check configuration documentation |
| `CONFIG_SCHEMA_001` | Schema validation failed | Configuration doesn't match expected schema | Update configuration to match schema |

### Validation Errors (VALID_*) {#validation-errors-valid_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `VALID_COMPARE_001` | Visual comparison failed | Unable to compare documents visually | Check input files and comparison settings |
| `VALID_THRESHOLD_001` | Validation threshold exceeded | Document differences exceed threshold | Adjust threshold or investigate differences |
| `VALID_METRIC_001` | Invalid validation metric | Validation metric is not supported | Use supported validation metrics |
| `VALID_REPORT_001` | Validation report generation failed | Unable to generate validation report | Check output directory permissions |

### Font Management Errors (FONT_*) {#font-management-errors-font_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `FONT_LOAD_001` | Font file not found | Specified font file doesn't exist | Verify font file path |
| `FONT_LOAD_002` | Invalid font format | Font file format is not supported | Use supported font formats (TTF, OTF) |
| `FONT_REGISTER_001` | Font registration failed | Unable to register font with system | Check font file permissions |
| `FONT_SUBSTITUTE_001` | Font substitution failed | Unable to find suitable font substitute | Install required fonts |
| `FONT_DOWNLOAD_001` | Font download failed | Unable to download font from source | Check internet connection |

### File System Errors (FS_*) {#file-system-errors-fs_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `FS_READ_001` | File read permission denied | Insufficient permissions to read file | Check file permissions |
| `FS_WRITE_001` | File write permission denied | Insufficient permissions to write file | Check directory permissions |
| `FS_SPACE_001` | Insufficient disk space | Not enough disk space for operation | Free up disk space |
| `FS_PATH_001` | Invalid file path | File path contains invalid characters | Use valid file path |
| `FS_LOCK_001` | File is locked | File is being used by another process | Close other applications using the file |

### Memory and Performance Errors (MEM_*) {#memory-and-performance-errors-mem_}

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `MEM_LIMIT_001` | Memory limit exceeded | Operation requires more memory than available | Increase memory limit or process smaller files |
| `MEM_ALLOC_001` | Memory allocation failed | Unable to allocate required memory | Close other applications or restart |
| `PERF_TIMEOUT_001` | Operation timeout | Operation took longer than allowed | Increase timeout or optimize operation |
| `PERF_SIZE_001` | File size limit exceeded | File is larger than maximum allowed size | Use smaller files or increase size limit |

## Error Handling Best Practices

### For Users

1. **Check Error Code**: Look up the specific error code in this reference
2. **Verify Prerequisites**: Ensure all requirements are met (files exist, permissions, etc.)
3. **Check Configuration**: Validate configuration files and settings
4. **Review Logs**: Check detailed logs for additional context
5. **Try Alternatives**: Use alternative approaches when available

### For Developers

1. **Catch Specific Exceptions**: Handle specific error types appropriately
2. **Provide Context**: Include relevant context in error messages
3. **Log Appropriately**: Use appropriate log levels for different error types
4. **Graceful Degradation**: Implement fallback mechanisms where possible
5. **User-Friendly Messages**: Translate technical errors to user-friendly messages

## Common Error Scenarios

### Scenario 1: PDF Processing Fails

```
Error: PDF_PARSE_001 - Failed to open PDF file
```

**Troubleshooting Steps:**

1. Verify the PDF file exists and is accessible
2. Check file permissions
3. Try opening the PDF in a PDF viewer to verify it's not corrupted
4. Ensure the file path is correct

### Scenario 2: Font Not Available

```
Error: FONT_LOAD_001 - Font file not found
```

**Troubleshooting Steps:**

1. Check if the font file exists in the specified location
2. Verify font file permissions
3. Install the required font system-wide
4. Use font substitution if the exact font is not available

### Scenario 3: Configuration Invalid

```
Error: CONFIG_VALIDATE_001 - Invalid configuration value
```

**Troubleshooting Steps:**

1. Validate the configuration file syntax
2. Check that all required fields are present
3. Verify configuration values are within valid ranges
4. Refer to the configuration documentation

## Getting Help

If you encounter an error not covered in this reference:

1. **Check Logs**: Review detailed logs for additional context
2. **Search Documentation**: Look through the troubleshooting guide
3. **Community Support**: Check community forums and discussions
4. **Report Issues**: Report bugs with error codes and context

## Related Documentation

- [Troubleshooting Guide](../guides/troubleshooting.md)
- [Configuration Reference](configuration.md)
- [API Documentation](../api/README.md)
- [Installation Guide](../INSTALLATION.md)
