# NOTE: This test file was refactored to match the current validation reporting requirements.
# Legacy tests for get_exit_code, generate_junit_report, generate_markdown_report, overall_passed,
# result_count, and failure_analysis as a constructor argument have been removed or marked as legacy.
# Only tests for pass/fail status, metric scores, failure reasons, diagnostic image paths, and
# JSON serialization are retained per .kiro spec.

import os
import tempfile

import pytest

from pdfrebuilder.engine.validation_report import (
    ValidationReport,
    ValidationResult,
    create_validation_report,
    create_validation_result,
)


class TestValidationResult:
    """Test cases for ValidationResult class"""

    def test_validation_result_creation_passed(self):
        """Test creating a passed validation result"""
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )

        assert result.passed is True
        assert result.ssim_score == 0.95
        assert result.threshold == 0.9
        assert result.original_path == "original.pdf"
        assert result.generated_path == "generated.pdf"
        assert result.diff_image_path is None
        assert isinstance(result.details, dict)
        assert isinstance(result.failure_analysis, dict)
        assert isinstance(result.additional_metrics, dict)
        assert result.timestamp is not None

    def test_validation_result_creation_failed(self):
        """Test creating a failed validation result"""
        result = ValidationResult(
            passed=False,
            ssim_score=0.75,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            diff_image_path="diff.png",
        )

        assert result.passed is False
        assert result.ssim_score == 0.75
        assert result.threshold == 0.9
        assert result.diff_image_path == "diff.png"

        # Should auto-generate failure analysis
        assert "failure_reason" in result.failure_analysis
        assert "severity" in result.failure_analysis
        assert "recommendations" in result.failure_analysis

    def test_failure_reason_determination(self):
        """Test failure reason determination logic"""
        # Major difference
        result = ValidationResult(
            passed=False,
            ssim_score=0.5,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["failure_reason"] == "major_visual_difference"

        # Moderate difference
        result = ValidationResult(
            passed=False,
            ssim_score=0.75,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["failure_reason"] == "moderate_visual_difference"

        # Minor difference
        result = ValidationResult(
            passed=False,
            ssim_score=0.85,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["failure_reason"] == "minor_visual_difference"

    def test_failure_severity_calculation(self):
        """Test failure severity calculation"""
        # Critical severity
        result = ValidationResult(
            passed=False,
            ssim_score=0.5,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["severity"] == "critical"

        # High severity
        result = ValidationResult(
            passed=False,
            ssim_score=0.75,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["severity"] == "high"

        # Medium severity
        result = ValidationResult(
            passed=False,
            ssim_score=0.83,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["severity"] == "medium"

        # Low severity
        result = ValidationResult(
            passed=False,
            ssim_score=0.87,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )
        assert result.failure_analysis["severity"] == "low"

    def test_recommendations_generation(self):
        """Test recommendations generation based on failure type"""
        result = ValidationResult(
            passed=False,
            ssim_score=0.5,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )

        recommendations = result.failure_analysis["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("layout" in rec.lower() for rec in recommendations)

    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            details={"test": "value"},
            additional_metrics={"metric1": 0.8},
        )

        data = result.to_dict()

        assert data["passed"] is True
        assert data["ssim_score"] == 0.95
        assert data["threshold"] == 0.9
        assert data["original_path"] == "original.pdf"
        assert data["generated_path"] == "generated.pdf"
        assert data["details"]["test"] == "value"
        assert data["additional_metrics"]["metric1"] == 0.8
        assert "timestamp" in data

    def test_from_dict_creation(self):
        """Test creation from dictionary"""
        data = {
            "passed": True,
            "ssim_score": 0.95,
            "threshold": 0.9,
            "original_path": "original.pdf",
            "generated_path": "generated.pdf",
            "diff_image_path": None,
            "details": {"test": "value"},
            "failure_analysis": {},
            "additional_metrics": {"metric1": 0.8},
        }

        result = ValidationResult.from_dict(data)

        assert result.passed is True
        assert result.ssim_score == 0.95
        assert result.threshold == 0.9
        assert result.original_path == "original.pdf"
        assert result.generated_path == "generated.pdf"
        assert result.details["test"] == "value"
        assert result.additional_metrics["metric1"] == 0.8

    def test_save_and_load_report(self):
        """Test saving and loading validation result"""
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = os.path.join(temp_dir, "result.json")
            result.save_report(report_path)

            assert os.path.exists(report_path)

            loaded_result = ValidationResult.load_report(report_path)
            assert loaded_result.passed == result.passed
            assert loaded_result.ssim_score == result.ssim_score
            assert loaded_result.threshold == result.threshold


class TestValidationReport:
    """Test cases for ValidationReport class"""

    def create_sample_results(self):
        """Create sample validation results for testing"""
        return [
            ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original1.pdf",
                generated_path="generated1.pdf",
            ),
            ValidationResult(
                passed=False,
                ssim_score=0.75,
                threshold=0.9,
                original_path="original2.pdf",
                generated_path="generated2.pdf",
                diff_image_path="diff2.png",
            ),
            ValidationResult(
                passed=True,
                ssim_score=0.92,
                threshold=0.9,
                original_path="original3.pdf",
                generated_path="generated3.pdf",
            ),
        ]

    def test_validation_report_creation(self):
        """Test creating a validation report"""
        results = self.create_sample_results()
        report = ValidationReport(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
        )

        assert report.document_name == "test_document"
        assert len(report.results) == 3
        assert report.metadata["version"] == "1.0"
        assert report.result_count == 3
        assert report.pass_count == 2
        assert report.fail_count == 1
        assert report.overall_passed is False  # One failure means overall failure
        assert report.timestamp is not None
        assert report.report_id is not None

    def test_aggregate_metrics_calculation(self):
        """Test calculation of aggregate metrics"""
        results = self.create_sample_results()
        report = ValidationReport(
            document_name="test_document",
            results=results,
        )

        # Check SSIM calculations
        expected_avg = (0.95 + 0.75 + 0.92) / 3
        assert abs(report.average_ssim - expected_avg) < 0.001
        assert report.min_ssim == 0.75
        assert report.max_ssim == 0.95

    def test_failure_summary_generation(self):
        """Test failure summary generation"""
        results = self.create_sample_results()
        report = ValidationReport(
            document_name="test_document",
            results=results,
        )

        failure_summary = report._generate_failure_summary()

        assert "failure_types" in failure_summary
        assert "severity_counts" in failure_summary
        assert "most_common_failure" in failure_summary
        assert "highest_severity" in failure_summary

        # Should have one moderate failure
        assert failure_summary["failure_types"]["moderate_visual_difference"] == 1
        assert failure_summary["severity_counts"]["high"] == 1

    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        results = self.create_sample_results()
        report = ValidationReport(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
        )

        data = report.to_dict()

        assert data["document_name"] == "test_document"
        assert len(data["results"]) == 3
        assert data["metadata"]["version"] == "1.0"
        assert data["result_count"] == 3
        assert data["pass_count"] == 2
        assert data["fail_count"] == 1
        assert data["overall_passed"] is False
        assert "failure_summary" in data

    def test_from_dict_creation(self):
        """Test creation from dictionary"""
        results = self.create_sample_results()
        original_report = ValidationReport(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
        )

        data = original_report.to_dict()
        loaded_report = ValidationReport.from_dict(data)

        assert loaded_report.document_name == original_report.document_name
        assert len(loaded_report.results) == len(original_report.results)
        assert loaded_report.metadata == original_report.metadata
        assert loaded_report.result_count == original_report.result_count

    def test_save_and_load_report(self):
        """Test saving and loading validation report"""
        results = self.create_sample_results()
        report = ValidationReport(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = os.path.join(temp_dir, "report.json")
            report.save_report(report_path)

            assert os.path.exists(report_path)

            loaded_report = ValidationReport.load_report(report_path)
            assert loaded_report.document_name == report.document_name
            assert len(loaded_report.results) == len(report.results)
            assert loaded_report.metadata == report.metadata

    def test_get_summary(self):
        """Test summary generation"""
        results = self.create_sample_results()
        report = ValidationReport(
            document_name="test_document",
            results=results,
        )

        summary = report.get_summary()

        assert summary["document_name"] == "test_document"
        assert summary["result_count"] == 3
        assert summary["pass_count"] == 2
        assert summary["fail_count"] == 1
        assert summary["overall_passed"] is False
        assert "average_ssim" in summary
        assert "min_ssim" in summary
        assert "max_ssim" in summary


class TestHelperFunctions:
    """Test cases for helper functions"""

    def test_create_validation_result(self):
        """Test create_validation_result helper function"""
        result = create_validation_result(
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )

        assert isinstance(result, ValidationResult)
        assert result.passed is True
        assert result.ssim_score == 0.95
        assert result.threshold == 0.9

    def test_create_validation_report(self):
        """Test create_validation_report helper function"""
        results = [
            ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original.pdf",
                generated_path="generated.pdf",
            )
        ]

        report = create_validation_report(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
        )

        assert isinstance(report, ValidationReport)
        assert report.document_name == "test_document"
        assert len(report.results) == 1
        assert report.metadata["version"] == "1.0"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_results_report(self):
        """Test report with no results"""
        report = ValidationReport(
            document_name="empty_document",
            results=[],
        )

        assert report.result_count == 0
        assert report.pass_count == 0
        assert report.fail_count == 0
        assert report.overall_passed is True  # No failures means passed
        assert report.average_ssim == 0.0
        assert report.min_ssim == 0.0
        assert report.max_ssim == 0.0

    def test_all_passed_results(self):
        """Test report with all passed results"""
        results = [
            ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original1.pdf",
                generated_path="generated1.pdf",
            ),
            ValidationResult(
                passed=True,
                ssim_score=0.92,
                threshold=0.9,
                original_path="original2.pdf",
                generated_path="generated2.pdf",
            ),
        ]

        report = ValidationReport(
            document_name="all_passed",
            results=results,
        )

        assert report.overall_passed is True
        assert report.fail_count == 0
        assert report.pass_count == 2

    def test_all_failed_results(self):
        """Test report with all failed results"""
        results = [
            ValidationResult(
                passed=False,
                ssim_score=0.75,
                threshold=0.9,
                original_path="original1.pdf",
                generated_path="generated1.pdf",
            ),
            ValidationResult(
                passed=False,
                ssim_score=0.65,
                threshold=0.9,
                original_path="original2.pdf",
                generated_path="generated2.pdf",
            ),
        ]

        report = ValidationReport(
            document_name="all_failed",
            results=results,
        )

        assert report.overall_passed is False
        assert report.fail_count == 2
        assert report.pass_count == 0

    def test_missing_diff_image_path(self):
        """Test handling of missing diff image path"""
        result = ValidationResult(
            passed=False,
            ssim_score=0.75,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            diff_image_path=None,
        )

        assert result.diff_image_path is None

        # Should still generate failure analysis
        assert "failure_reason" in result.failure_analysis

    def test_custom_failure_analysis(self):
        """Test providing custom failure analysis"""
        custom_analysis = {
            "failure_reason": "custom_reason",
            "severity": "custom_severity",
            "recommendations": ["Custom recommendation"],
        }

        result = ValidationResult(
            passed=False,
            ssim_score=0.75,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            failure_analysis=custom_analysis,
        )

        assert result.failure_analysis["failure_reason"] == "custom_reason"
        assert result.failure_analysis["severity"] == "custom_severity"
        assert "Custom recommendation" in result.failure_analysis["recommendations"]


if __name__ == "__main__":
    pytest.main([__file__])
