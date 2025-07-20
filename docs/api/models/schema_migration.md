# schema_migration

Schema migration utilities for Universal IDM

This module provides utilities for migrating between different versions of the Universal IDM schema.

## Classes

### SchemaMigrationError

Raised when schema migration fails

## Functions

### get_schema_version(data)

Get the schema version from a document

### migrate_v0_to_v1(data)

Migrate from legacy schema (v0) to Universal IDM v1.0

This handles the migration from the original PDF-only schema to the Universal IDM schema.

### migrate_schema(data, target_version)

Migrate a document schema to the target version

Args:
    data: Document data to migrate
    target_version: Target schema version

Returns:
    Migrated document data

Raises:
    SchemaMigrationError: If migration fails

### adapt_to_v1(data)

Adapt a document to v1.0 schema by adding missing fields

This is a best-effort approach when no specific migration path exists.

### load_and_migrate(file_path, target_version)

Load a document from file and migrate it to the target version

Args:
    file_path: Path to the document file
    target_version: Target schema version

Returns:
    Migrated document data

Raises:
    SchemaMigrationError: If migration fails

### save_migrated(data, file_path)

Save migrated document data to file

Args:
    data: Document data to save
    file_path: Path to save the document

Raises:
    SchemaMigrationError: If saving fails

### migrate_document_file(input_path, output_path, target_version)

Migrate a document file to the target version and save it

Args:
    input_path: Path to the input document file
    output_path: Path to save the migrated document
    target_version: Target schema version

Raises:
    SchemaMigrationError: If migration fails
