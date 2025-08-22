# schema_validator

Schema validation utilities for Universal IDM

## Classes

### SchemaValidationError

Raised when schema validation fails

### SchemaValidator

Validates Universal IDM schemas

#### Methods

##### __init__()

##### validate_document(data)

Validate a document against the Universal IDM schema

Returns:
    Tuple of (is_valid, list_of_errors)

##### _validate_document_structure(structure)

Validate document structure array

##### _validate_layers(layers, context)

Validate layers array

##### _validate_elements(elements, context)

Validate elements array

##### _validate_text_element(element, context)

Validate text element specific fields

##### _validate_image_element(element, context)

Validate image element specific fields

##### _validate_drawing_element(element, context)

Validate drawing element specific fields

##### _validate_bbox(bbox, context)

Validate bounding box format

##### _validate_metadata(metadata)

Validate metadata structure

##### load_and_validate_document(file_path)

Load and validate a document from file

Args:
    file_path: Path to JSON document file

Returns:
    Validated UniversalDocument instance

Raises:
    SchemaValidationError: If validation fails

## Functions

### validate_document_file(file_path)

Validate a document file

Returns:
    Tuple of (is_valid, list_of_errors)
