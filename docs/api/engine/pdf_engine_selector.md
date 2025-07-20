# pdf_engine_selector

PDF Engine Selector

This module provides a factory pattern for selecting and instantiating
the appropriate PDF rendering engine based on configuration.

## Classes

### PDFEngineSelector

Factory for PDF rendering engines.

#### Methods

##### __init__()

Initialize the engine selector.

##### register_engine(name, engine_class)

Register a new engine.

##### register_default_engines()

Register the default engines.

##### get_engine(name, config)

Get an instance of the specified engine.

##### get_default_engine(config)

Get the default engine based on configuration.

##### list_available_engines()

List all available engines with their capabilities.

##### validate_engine_config(engine_name, config)

Validate configuration for a specific engine.

##### compare_engines(engine1, engine2)

Compare capabilities of two engines.

## Functions

### get_engine_selector()

Get the global engine selector instance.

### get_pdf_engine(engine_name, config)

Get a PDF engine instance.

### get_default_pdf_engine(config)

Get the default PDF engine.
