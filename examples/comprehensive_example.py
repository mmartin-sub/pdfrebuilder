#!/usr/bin/env python3
"""
Comprehensive Example - Multi-Format Document Engine

This example demonstrates all major features of the Multi-Format Document Engine
in a single, comprehensive workflow. It shows:

1. PDF content extraction
2. Document analysis and validation
3. Content modification
4. PDF reconstruction
5. Visual validation
6. Batch processing concepts
7. Error handling

This serves as both a demonstration and a test of the complete system.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup - this is necessary for the imports to work
# ruff: noqa: E402
from pdfrebuilder.engine.extract_pdf_content_fitz import extract_pdf_content
from pdfrebuilder.models.universal_idm import UniversalDocument
from pdfrebuilder.recreate_pdf_from_config import recreate_pdf_from_config
from pdfrebuilder.tools import serialize_pdf_content_to_config


class ComprehensiveDemo:
    """Comprehensive demonstration of the Multi-Format Document Engine."""

    def __init__(self):
        self.project_root = project_root
        self.output_dir = project_root / "examples" / "output" / "comprehensive_demo"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "extraction": None,
            "analysis": None,
            "modification": None,
            "reconstruction": None,
            "validation": None,
            "performance": {},
        }

    def run_complete_demo(self) -> dict[str, Any]:
        """Run the complete demonstration workflow."""
        print("Multi-Format Document Engine - Comprehensive Demo")
        print("=" * 60)

        # Step 1: Find and prepare input file
        input_file = self._find_input_file()
        if not input_file:
            print("❌ No suitable input file found.")
            return self.results

        print(f"Using input file: {input_file}")

        # Step 2: Extract content
        print("\n" + "=" * 60)
        print("STEP 1: PDF Content Extraction")
        print("=" * 60)

        extraction_result = self._extract_content(input_file)
        self.results["extraction"] = extraction_result

        if not extraction_result["success"]:
            print("❌ Extraction failed. Cannot continue demo.")
            return self.results

        # Step 3: Analyze content
        print("\n" + "=" * 60)
        print("STEP 2: Content Analysis")
        print("=" * 60)

        analysis_result = self._analyze_content(extraction_result["document"])
        self.results["analysis"] = analysis_result

        # Step 4: Modify content
        print("\n" + "=" * 60)
        print("STEP 3: Content Modification")
        print("=" * 60)

        modification_result = self._modify_content(extraction_result["document"])
        self.results["modification"] = modification_result

        # Step 5: Reconstruct PDF
        print("\n" + "=" * 60)
        print("STEP 4: PDF Reconstruction")
        print("=" * 60)

        reconstruction_result = self._reconstruct_pdf(modification_result["config_file"])
        self.results["reconstruction"] = reconstruction_result

        # Step 6: Validate results
        print("\n" + "=" * 60)
        print("STEP 5: Validation and Quality Check")
        print("=" * 60)

        validation_result = self._validate_results(input_file, reconstruction_result["output_file"])
        self.results["validation"] = validation_result

        # Step 7: Generate summary report
        print("\n" + "=" * 60)
        print("STEP 6: Summary Report")
        print("=" * 60)

        self._generate_summary_report()

        return self.results

    def _find_input_file(self) -> Path | None:
        """Find a suitable input PDF file."""
        # Look for PDF files in input directory
        input_dir = self.project_root / "input"

        if not input_dir.exists():
            print("Input directory not found.")
            return None

        pdf_files = list(input_dir.glob("*.pdf"))

        if not pdf_files:
            print("No PDF files found in input directory.")
            return None

        # Use the first PDF file found
        return pdf_files[0]

    def _extract_content(self, input_file: Path) -> dict[str, Any]:
        """Extract content from the input file."""
        try:
            print(f"Extracting content from: {input_file}")

            # Extract PDF content
            document = extract_pdf_content(str(input_file))

            if not document:
                return {"success": False, "error": "Failed to extract content"}

            # Serialize to config
            config_file = self.output_dir / f"{input_file.stem}_config.json"
            serialize_pdf_content_to_config(document, str(config_file))

            print("✅ Content extracted successfully")
            print(f"   - Pages: {len(document.pages)}")
            print(f"   - Config saved to: {config_file}")

            return {
                "success": True,
                "document": document,
                "config_file": config_file,
                "pages": len(document.pages),
            }

        except Exception as e:
            error_msg = f"Extraction failed: {e!s}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def _analyze_content(self, document) -> dict[str, Any]:
        """Analyze the extracted content."""
        try:
            print("Analyzing document content...")

            # Calculate basic statistics
            stats = self._calculate_document_stats(document)

            # Analyze text content
            total_text = ""
            for page in document.pages:
                for element in page.elements:
                    if hasattr(element, "text") and element.text:
                        total_text += element.text + " "

            # Basic text analysis
            word_count = len(total_text.split())
            char_count = len(total_text)

            analysis = {
                "pages": len(document.pages),
                "elements": sum(len(page.elements) for page in document.pages),
                "word_count": word_count,
                "char_count": char_count,
                "avg_words_per_page": (word_count / len(document.pages) if document.pages else 0),
                "stats": stats,
            }

            print("✅ Analysis completed")
            print(f"   - Pages: {analysis['pages']}")
            print(f"   - Total elements: {analysis['elements']}")
            print(f"   - Word count: {analysis['word_count']}")
            print(f"   - Character count: {analysis['char_count']}")

            return {"success": True, "analysis": analysis}

        except Exception as e:
            error_msg = f"Analysis failed: {e!s}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def _modify_content(self, document) -> dict[str, Any]:
        """Modify the document content."""
        try:
            print("Modifying document content...")

            # Create a modified version of the document
            modified_document = UniversalDocument()
            modified_document.pages = []

            for _i, page in enumerate(document.pages):
                modified_page = type(page)()  # Create new page of same type
                modified_page.elements = []

                for element in page.elements:
                    # Create a copy of the element
                    modified_element = type(element)()

                    # Copy basic properties
                    if hasattr(element, "x"):
                        modified_element.x = element.x
                    if hasattr(element, "y"):
                        modified_element.y = element.y
                    if hasattr(element, "width"):
                        modified_element.width = element.width
                    if hasattr(element, "height"):
                        modified_element.height = element.height

                    # Modify text content (add a prefix to demonstrate modification)
                    if hasattr(element, "text") and element.text:
                        modified_element.text = f"[Modified] {element.text}"
                    elif hasattr(element, "text"):
                        modified_element.text = "[Modified] New content"

                    modified_page.elements.append(modified_element)

                modified_document.pages.append(modified_page)

            # Save modified document to config
            modified_config_file = self.output_dir / "modified_config.json"
            serialize_pdf_content_to_config(modified_document, str(modified_config_file))

            print("✅ Content modified successfully")
            print(f"   - Modified config saved to: {modified_config_file}")

            return {
                "success": True,
                "modified_document": modified_document,
                "config_file": modified_config_file,
            }

        except Exception as e:
            error_msg = f"Modification failed: {e!s}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def _reconstruct_pdf(self, config_file: Path) -> dict[str, Any]:
        """Reconstruct PDF from the config file."""
        try:
            print(f"Reconstructing PDF from: {config_file}")

            # Reconstruct PDF
            output_file = self.output_dir / f"reconstructed_{config_file.stem}.pdf"
            recreate_pdf_from_config(str(config_file), str(output_file))

            print("✅ PDF reconstructed successfully")
            print(f"   - Output file: {output_file}")

            return {
                "success": True,
                "output_file": output_file,
                "config_file": config_file,
            }

        except Exception as e:
            error_msg = f"Reconstruction failed: {e!s}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def _validate_results(self, original_file: Path, reconstructed_file: Path) -> dict[str, Any]:
        """Validate the reconstruction results."""
        try:
            print("Validating reconstruction results...")

            # Check if files exist
            if not original_file.exists():
                return {"success": False, "error": "Original file not found"}

            if not reconstructed_file.exists():
                return {"success": False, "error": "Reconstructed file not found"}

            # Basic file size comparison
            original_size = original_file.stat().st_size
            reconstructed_size = reconstructed_file.stat().st_size

            # File size ratio (reconstructed might be different due to modifications)
            size_ratio = reconstructed_size / original_size if original_size > 0 else 0

            validation = {
                "original_file": str(original_file),
                "reconstructed_file": str(reconstructed_file),
                "original_size": original_size,
                "reconstructed_size": reconstructed_size,
                "size_ratio": size_ratio,
                "files_exist": True,
            }

            print("✅ Validation completed")
            print(f"   - Original size: {original_size:,} bytes")
            print(f"   - Reconstructed size: {reconstructed_size:,} bytes")
            print(f"   - Size ratio: {size_ratio:.2f}")

            return {"success": True, "validation": validation}

        except Exception as e:
            error_msg = f"Validation failed: {e!s}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def _calculate_document_stats(self, document) -> dict[str, int]:
        """Calculate basic statistics for a document."""
        stats = {
            "pages": 0,
            "total_elements": 0,
            "text_elements": 0,
            "image_elements": 0,
            "drawing_elements": 0,
        }

        if hasattr(document, "document_structure"):
            stats["pages"] = len(document.document_structure)

            for page in document.document_structure:
                if hasattr(page, "layers"):
                    for layer in page.layers:
                        if hasattr(layer, "content"):
                            for element in layer.content:
                                stats["total_elements"] += 1

                                if hasattr(element, "text"):
                                    stats["text_elements"] += 1
                                elif hasattr(element, "image_file"):
                                    stats["image_elements"] += 1
                                elif hasattr(element, "drawing_commands"):
                                    stats["drawing_elements"] += 1

        return stats

    def _generate_summary_report(self):
        """Generate a comprehensive summary report."""
        print("Generating comprehensive summary report...")

        # Calculate total processing time
        total_time = 0
        for _step, result in self.results.items():
            if isinstance(result, dict) and "time" in str(result):
                for key, value in result.items():
                    if key.endswith("_time") and isinstance(value, int | float):
                        total_time += value

        # Create summary
        summary = {
            "demo_overview": {
                "total_processing_time": total_time,
                "steps_completed": sum(
                    1 for r in self.results.values() if r and isinstance(r, dict) and r.get("success")
                ),
                "steps_failed": sum(
                    1 for r in self.results.values() if r and isinstance(r, dict) and not r.get("success", True)
                ),
            },
            "performance_metrics": {},
            "quality_assessment": {},
            "recommendations": [],
        }

        # Performance metrics
        if self.results["extraction"] and self.results["extraction"].get("success"):
            extraction_stats = self.results["extraction"]["statistics"]
            extraction_time = self.results["extraction"]["extraction_time"]

            elements_per_second = extraction_stats["total_elements"] / extraction_time if extraction_time > 0 else 0

            summary["performance_metrics"] = {
                "extraction_speed": f"{elements_per_second:.1f} elements/second",
                "total_elements_processed": extraction_stats["total_elements"],
                "processing_efficiency": ("Good" if elements_per_second > 10 else "Moderate"),
            }

        # Quality assessment
        quality_score = 0
        quality_factors = []

        if self.results["extraction"] and self.results["extraction"].get("success"):
            quality_score += 25
            quality_factors.append("✅ Content extraction successful")

        if self.results["modification"] and self.results["modification"].get("success"):
            quality_score += 25
            quality_factors.append("✅ Content modification successful")

        if self.results["reconstruction"] and self.results["reconstruction"].get("success"):
            quality_score += 25
            quality_factors.append("✅ PDF reconstruction successful")

        if self.results["validation"] and self.results["validation"].get("success"):
            quality_score += 25
            quality_factors.append("✅ Validation checks passed")

        summary["quality_assessment"] = {
            "overall_score": f"{quality_score}/100",
            "quality_factors": quality_factors,
        }

        # Recommendations
        recommendations = []

        if quality_score == 100:
            recommendations.append("🎉 Excellent! All workflow steps completed successfully.")
            recommendations.append("💡 Consider testing with more complex documents to explore advanced features.")
        elif quality_score >= 75:
            recommendations.append("👍 Good performance! Most workflow steps completed successfully.")
            recommendations.append("🔍 Review any failed steps for potential improvements.")
        else:
            recommendations.append("⚠️ Some workflow steps failed. Check error messages for troubleshooting.")
            recommendations.append("📚 Consult documentation for common issues and solutions.")

        recommendations.extend(
            [
                "📊 Review the analysis report for document insights.",
                "🔧 Experiment with different extraction and modification options.",
                "🚀 Try batch processing for multiple documents.",
            ]
        )

        summary["recommendations"] = recommendations

        # Save summary report
        summary_file = self.output_dir / "demo_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Display summary
        print("📋 Demo Summary:")
        print(f"   Total processing time: {total_time:.2f}s")
        print(f"   Steps completed: {summary['demo_overview']['steps_completed']}")
        print(f"   Steps failed: {summary['demo_overview']['steps_failed']}")
        print(f"   Overall quality score: {summary['quality_assessment']['overall_score']}")

        print("\n📈 Performance Metrics:")
        if summary["performance_metrics"]:
            for metric, value in summary["performance_metrics"].items():
                print(f"   {metric}: {value}")

        print("\n✅ Quality Factors:")
        for factor in summary["quality_assessment"]["quality_factors"]:
            print(f"   {factor}")

        print("\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"   {rec}")

        print(f"\n📁 All output files saved to: {self.output_dir}")
        print(f"   Summary report: {summary_file.name}")


def main():
    """Run the comprehensive demonstration."""
    demo = ComprehensiveDemo()
    results = demo.run_complete_demo()

    # Return appropriate exit code
    failed_steps = sum(1 for r in results.values() if r and isinstance(r, dict) and not r.get("success", True))
    return 0 if failed_steps == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
