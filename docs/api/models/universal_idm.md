# universal_idm

Universal Intermediate Document Model (IDM) Schema v1.0

This module defines the comprehensive data structures for the Multi-Format Document Engine,
supporting both PDF and PSD formats with extensibility for future formats.

## Classes

### DocumentType

Document unit types for different formats

### LayerType

Layer types for different content organization

### ElementType

Element types for content within layers

### BlendMode

Standard blend modes supported across formats

### BoundingBox

Standardized bounding box representation

#### Methods

##### to_list()

Convert to list format for JSON serialization

##### from_list(cls, bbox_list)

Create from list format

##### width()

##### height()

### Color

Universal color representation supporting multiple formats

#### Methods

##### to_rgb_tuple()

Convert to RGB tuple

##### to_rgba_tuple()

Convert to RGBA tuple

##### to_hex()

Convert to hex string

##### from_rgb_tuple(cls, rgb)

Create from RGB tuple

##### from_rgba_tuple(cls, rgba)

Create from RGBA tuple

##### from_hex(cls, hex_str)

Create from hex string

### FontDetails

Comprehensive font information

### DrawingCommand

Standardized drawing command

### Element

Base class for all document elements

#### Methods

##### __init__(id, bbox, z_index)

##### to_dict()

Convert element to dictionary for serialization

##### from_dict(cls, data)

Create element from dictionary

### TextElement

Text element with comprehensive formatting

#### Methods

##### __init__(id, bbox, raw_text, text, font_details, z_index, writing_mode, writing_direction, align, adjust_spacing, background_color)

##### to_dict()

##### from_dict(cls, data)

### ImageElement

Image element with metadata

#### Methods

##### __init__(id, bbox, image_file, z_index, original_format, dpi, color_space, has_transparency, transformation_matrix)

##### to_dict()

##### from_dict(cls, data)

### DrawingElement

Drawing/vector element with comprehensive styling

#### Methods

##### __init__(id, bbox, z_index, color, fill, width, drawing_commands, original_shape_type)

##### to_dict()

##### from_dict(cls, data)

### Layer

Universal layer representation

#### Methods

##### __init__(layer_id, layer_name, layer_type, bbox, visibility, opacity, blend_mode, children, content, clipping_mask, layer_effects)

##### to_dict()

##### from_dict(cls, data)

### DocumentUnit

Base class for document units (pages or canvas)

#### Methods

##### __init__(size, background_color, layers)

##### to_dict()

### PageUnit

Page-based document unit (PDF, Word, etc.)

#### Methods

##### __init__(size, background_color, layers, page_number)

##### type()

Return the document type for this unit

##### to_dict()

##### from_dict(cls, data)

### CanvasUnit

Canvas-based document unit (PSD, Illustrator, etc.)

#### Methods

##### __init__(size, background_color, layers, canvas_name)

##### to_dict()

##### from_dict(cls, data)

### DocumentMetadata

Universal document metadata

#### Methods

##### __init__(format, title, author, subject, keywords, creator, producer, creation_date, modification_date, custom_properties)

##### to_dict()

##### from_dict(cls, data)

### UniversalDocument

Top-level Universal Document Model

#### Methods

##### __init__(version, engine, engine_version, metadata, document_structure)

##### to_dict()

Convert the UniversalDocument to a dictionary representation for serialization.

##### from_dict(cls, data)

##### to_json(indent)

Convert to JSON string

##### from_json(cls, json_str)

Create from JSON string

## Functions

### validate_schema_version(data)

Validate that the schema version is supported

### migrate_schema(data, target_version)

Migrate schema to target version (placeholder for future migrations)
