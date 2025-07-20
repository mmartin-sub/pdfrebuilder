Visual Validation
=================

This guide covers visual validation techniques to ensure document reconstruction quality.

Overview
--------

Visual validation compares the original document with the reconstructed version to measure fidelity and identify potential issues.

Basic Validation
----------------

Simple Validation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator

   validator = VisualValidator()

   # Compare original and reconstructed documents
   result = validator.compare_documents(
       original="input.pdf",
       reconstructed="output.pdf"
   )

   print(f"Similarity: {result.similarity:.2%}")
   print(f"Differences found: {len(result.differences)}")

Validation Metrics
~~~~~~~~~~~~~~~~~~

The validator provides multiple metrics:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, ValidationMetrics

   validator = VisualValidator()
   result = validator.compare_documents("original.pdf", "reconstructed.pdf")

   # Access detailed metrics
   print(f"Overall similarity: {result.similarity:.2%}")
   print(f"Text accuracy: {result.text_accuracy:.2%}")
   print(f"Layout accuracy: {result.layout_accuracy:.2%}")
   print(f"Color accuracy: {result.color_accuracy:.2%}")
   print(f"Font accuracy: {result.font_accuracy:.2%}")

Advanced Validation
-------------------

Custom Thresholds
~~~~~~~~~~~~~~~~~

Configure validation thresholds for different quality levels:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, ValidationConfig

   config = ValidationConfig(
       similarity_threshold=0.95,
       text_threshold=0.98,
       layout_threshold=0.90,
       color_threshold=0.85,
       ignore_minor_differences=True
   )

   validator = VisualValidator(config=config)
   result = validator.compare_documents("original.pdf", "reconstructed.pdf")

   if result.passes_validation:
       print("✓ Document passes quality validation")
   else:
       print("✗ Document fails quality validation")
       for issue in result.quality_issues:
           print(f"  - {issue}")

Page-by-Page Validation
~~~~~~~~~~~~~~~~~~~~~~~

Validate individual pages for detailed analysis:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator

   validator = VisualValidator()

   # Validate each page separately
   page_results = validator.compare_pages(
       original="input.pdf",
       reconstructed="output.pdf"
   )

   for page_num, result in enumerate(page_results, 1):
       print(f"Page {page_num}: {result.similarity:.2%} similarity")

       if result.similarity < 0.9:
           print(f"  Issues on page {page_num}:")
           for diff in result.differences:
               print(f"    - {diff.type}: {diff.description}")

Validation Reports
------------------

Detailed Reports
~~~~~~~~~~~~~~~~

Generate comprehensive validation reports:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, ReportGenerator

   validator = VisualValidator()
   result = validator.compare_documents("original.pdf", "reconstructed.pdf")

   # Generate detailed report
   report_generator = ReportGenerator()
   report = report_generator.create_validation_report(result)

   # Save report
   report.save_html("validation_report.html")
   report.save_pdf("validation_report.pdf")
   report.save_json("validation_data.json")

Visual Diff Generation
~~~~~~~~~~~~~~~~~~~~~~

Create visual difference overlays:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, DiffGenerator

   validator = VisualValidator()
   result = validator.compare_documents("original.pdf", "reconstructed.pdf")

   # Generate visual diff
   diff_generator = DiffGenerator()
   diff_images = diff_generator.create_diff_images(result)

   # Save difference visualizations
   for page_num, diff_image in enumerate(diff_images, 1):
       diff_image.save(f"diff_page_{page_num}.png")

Automated Quality Assurance
----------------------------

Batch Validation
~~~~~~~~~~~~~~~~~

Validate multiple documents automatically:

.. code-block:: python

   from pdfrebuilder.engine import BatchValidator
   import os

   def validate_batch_processing():
       validator = BatchValidator(
           original_directory="input/",
           reconstructed_directory="output/",
           report_directory="validation_reports/"
       )

       results = validator.validate_all()

       # Summary statistics
       total_docs = len(results)
       passed = sum(1 for r in results if r.passes_validation)
       failed = total_docs - passed

       print(f"Validation Summary:")
       print(f"  Total documents: {total_docs}")
       print(f"  Passed: {passed} ({passed/total_docs:.1%})")
       print(f"  Failed: {failed} ({failed/total_docs:.1%})")

       # List failed documents
       if failed > 0:
           print("\nFailed documents:")
           for result in results:
               if not result.passes_validation:
                   print(f"  - {result.filename}: {result.similarity:.2%}")

CI/CD Integration
~~~~~~~~~~~~~~~~~

Integrate validation into continuous integration:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator
   import sys

   def ci_validation_check():
       validator = VisualValidator()

       # Validate test documents
       test_cases = [
           ("test_input_1.pdf", "test_output_1.pdf"),
           ("test_input_2.pdf", "test_output_2.pdf"),
       ]

       all_passed = True

       for original, reconstructed in test_cases:
           result = validator.compare_documents(original, reconstructed)

           if result.similarity < 0.95:
               print(f"FAIL: {original} -> {reconstructed} ({result.similarity:.2%})")
               all_passed = False
           else:
               print(f"PASS: {original} -> {reconstructed} ({result.similarity:.2%})")

       if not all_passed:
           sys.exit(1)  # Fail the CI build

       print("All validation tests passed!")

Performance Validation
-----------------------

Benchmark Validation
~~~~~~~~~~~~~~~~~~~~~

Measure validation performance:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, PerformanceProfiler
   import time

   def benchmark_validation():
       validator = VisualValidator()
       profiler = PerformanceProfiler()

       test_files = [
           ("small.pdf", "small_output.pdf"),
           ("medium.pdf", "medium_output.pdf"),
           ("large.pdf", "large_output.pdf"),
       ]

       for original, reconstructed in test_files:
           start_time = time.time()

           with profiler.profile(f"validation_{original}"):
               result = validator.compare_documents(original, reconstructed)

           duration = time.time() - start_time

           print(f"{original}:")
           print(f"  Validation time: {duration:.2f}s")
           print(f"  Similarity: {result.similarity:.2%}")
           print(f"  Memory usage: {profiler.get_peak_memory():.1f}MB")

Custom Validation Rules
-----------------------

Domain-Specific Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom validation rules for specific document types:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, CustomValidator

   class InvoiceValidator(CustomValidator):
       def validate_invoice_elements(self, original, reconstructed):
           # Custom validation for invoice documents
           issues = []

           # Check for required elements
           required_elements = ["invoice_number", "date", "total_amount"]

           for element in required_elements:
               if not self.element_exists(reconstructed, element):
                   issues.append(f"Missing required element: {element}")

           # Validate numerical accuracy
           original_total = self.extract_total(original)
           reconstructed_total = self.extract_total(reconstructed)

           if abs(original_total - reconstructed_total) > 0.01:
               issues.append(f"Total amount mismatch: {original_total} vs {reconstructed_total}")

           return issues

   # Use custom validator
   validator = InvoiceValidator()
   issues = validator.validate_invoice_elements("invoice.pdf", "invoice_output.pdf")

Quality Metrics
---------------

Statistical Analysis
~~~~~~~~~~~~~~~~~~~~

Analyze validation results statistically:

.. code-block:: python

   from pdfrebuilder.engine import ValidationAnalyzer
   import numpy as np
   import matplotlib.pyplot as plt

   def analyze_validation_results(results):
       analyzer = ValidationAnalyzer()

       similarities = [r.similarity for r in results]

       # Statistical summary
       stats = {
           'mean': np.mean(similarities),
           'median': np.median(similarities),
           'std': np.std(similarities),
           'min': np.min(similarities),
           'max': np.max(similarities)
       }

       print("Validation Statistics:")
       for metric, value in stats.items():
           print(f"  {metric}: {value:.3f}")

       # Generate histogram
       plt.figure(figsize=(10, 6))
       plt.hist(similarities, bins=20, alpha=0.7)
       plt.xlabel('Similarity Score')
       plt.ylabel('Frequency')
       plt.title('Distribution of Validation Scores')
       plt.savefig('validation_distribution.png')

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

Address common validation problems:

.. code-block:: python

   from pdfrebuilder.engine import ValidationTroubleshooter

   def diagnose_validation_issues(result):
       troubleshooter = ValidationTroubleshooter()

       if result.similarity < 0.8:
           diagnosis = troubleshooter.diagnose(result)

           print("Validation Issues Detected:")
           for issue in diagnosis.issues:
               print(f"  - {issue.type}: {issue.description}")
               print(f"    Suggested fix: {issue.suggested_fix}")

       # Common fixes
       if result.text_accuracy < 0.9:
           print("Consider:")
           print("  - Check font availability")
           print("  - Verify text encoding")
           print("  - Review manual overrides")

       if result.layout_accuracy < 0.9:
           print("Consider:")
           print("  - Enable template mode")
           print("  - Adjust positioning thresholds")
           print("  - Review element extraction")
