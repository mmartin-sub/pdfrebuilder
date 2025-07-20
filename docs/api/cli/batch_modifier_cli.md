# batch_modifier_cli

CLI interface for batch modification operations.

Provides command-line access to batch text replacement, variable substitution,
and font validation capabilities.

## Functions

### create_batch_modifier_parser()

Create the argument parser for batch modification commands.

### parse_replacements(replacements)

Parse replacement strings into tuples.

### parse_variables(variables)

Parse variable strings into VariableSubstitution objects.

### load_document(input_path)

Load document from JSON file.

### save_document(document, output_path)

Save document to JSON file.

### handle_replace_command(args)

Handle the replace command.

### handle_substitute_command(args)

Handle the substitute command.

### handle_validate_command(args)

Handle the validate command.

### handle_stats_command(args)

Handle the stats command.

### main()

Main entry point for the batch modifier CLI.
