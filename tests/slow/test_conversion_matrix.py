import glob
import os

import pytest
from click.testing import CliRunner

from scripts.run_conversion import main as run_conversion_main
from tests.config import get_sample_input_path, get_test_output_path

# Discover all PDF files in the sample directory
PDF_SAMPLES = glob.glob(os.path.join(get_sample_input_path(""), "*.pdf"))


def run_conversion_test(pdf_path, output_engine):
    """
    Helper function to run a single conversion test.
    """
    base_name = os.path.basename(pdf_path)
    test_name = f"matrix_{base_name}_{output_engine}"

    # PDFs are page-based and cannot be converted to canvas-based formats like Krita.
    if "pdf" in base_name.lower() and output_engine == "krita":
        pytest.skip("PDF to Krita conversion is not a supported workflow.")

    # Define the output file extension based on the engine
    if output_engine == "reportlab":
        ext = ".pdf"
    elif output_engine == "wand_image":
        ext = ".png"
    elif output_engine == "krita":
        ext = ".kra"
    else:
        # Default for any other case
        ext = ".out"

    output_path = get_test_output_path(test_name, ext=ext)

    runner = CliRunner()
    result = runner.invoke(
        run_conversion_main,
        [
            "--input-file",
            pdf_path,
            "--output-file",
            output_path,
            "--output-engine",
            output_engine,
        ],
    )

    assert result.exit_code == 0, f"Script failed for {base_name} -> {output_engine}:\\n{result.output}"
    assert os.path.exists(output_path), f"Output file was not created for {base_name} -> {output_engine}"

    # Clean up the generated file
    if os.path.exists(output_path):
        os.remove(output_path)


@pytest.mark.parametrize("pdf_path", PDF_SAMPLES)
def test_conversion_matrix_reportlab(pdf_path):
    run_conversion_test(pdf_path, "reportlab")


@pytest.mark.parametrize("pdf_path", PDF_SAMPLES)
def test_conversion_matrix_wand_image(pdf_path):
    run_conversion_test(pdf_path, "wand_image")


@pytest.mark.parametrize("pdf_path", PDF_SAMPLES)
def test_conversion_matrix_krita(pdf_path):
    run_conversion_test(pdf_path, "krita")
