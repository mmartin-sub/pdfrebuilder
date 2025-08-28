import os
import sys
import click

# Add the project root to the Python path to allow importing from pdfrebuilder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from pdfrebuilder.engine.document_parser import parse_document
from pdfrebuilder.engine.engine_selector import get_output_engine
from pdfrebuilder.settings import configure_logging

@click.command(help="A generic script to convert a document from one format to another using the pdfrebuilder engines.")
@click.option('--input-file', required=True, type=click.Path(exists=True, dir_okay=False), help="Path to the input document.")
@click.option('--output-file', required=True, type=click.Path(dir_okay=False), help="Path for the output file.")
@click.option('--input-engine', default='auto', help="The input engine to use (e.g., 'fitz', 'wand'). Defaults to 'auto'.")
@click.option('--output-engine', required=True, help="The output engine to use (e.g., 'wand_image', 'reportlab', 'krita').")
def main(input_file, output_file, input_engine, output_engine):
    """
    Performs a document conversion using specified input and output engines.
    """
    # Configure logging to see engine output
    configure_logging()

    click.echo(f"Starting conversion...")
    click.echo(f"  Input File: {input_file}")
    click.echo(f"  Output File: {output_file}")
    click.echo(f"  Input Engine: {input_engine}")
    click.echo(f"  Output Engine: {output_engine}")

    try:
        # Step 1: Parse the input document
        click.echo("\nStep 1: Parsing input document...")
        doc = parse_document(input_file, engine=input_engine)
        click.echo("...Parsing complete.")

        # Step 2: Get the output engine
        click.echo("\nStep 2: Loading output engine...")
        # Special handling for PDF engines which have their own selector
        if output_engine in ['reportlab', 'fitz', 'pymupdf']:
            from pdfrebuilder.engine.engine_selector import get_pdf_engine_selector
            renderer = get_pdf_engine_selector().get_engine(output_engine)
        else:
            renderer = get_output_engine(output_engine)
        click.echo(f"...Loaded '{renderer.engine_name}'.")

        # Step 3: Render the document
        click.echo("\nStep 3: Rendering output document...")
        renderer.render(doc, output_file)
        click.echo("...Rendering complete.")

        if os.path.exists(output_file):
            click.secho(f"\nSuccessfully created output file at: {output_file}", fg='green')
        else:
            click.secho(f"\nError: Output file was not created at the expected location: {output_file}", fg='red')
            sys.exit(1)

    except Exception as e:
        click.secho(f"\nAn error occurred during conversion: {e}", fg='red', err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
