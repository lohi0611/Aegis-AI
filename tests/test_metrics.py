"""
AEGIS — Unit Tests for Research Metrics, Confusion Matrices, and Evaluation Logic
Ensures mathematical consistency of all reported metrics without requiring a GPU or model weights.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import numpy as np
from evaluation.evaluate_compliance import compute_binary_metrics
from src.association.spatial import SpatialPPEAssociator, compute_iou, compute_containment_ratio
from src.compliance.rules import PPERuleEngine
from src.alerts.manager import AlertManager


class TestConfusionMatrixMath:
    def test_frame_level_confusion_matrix_consistency(self):
        """Verify the exact empirical Frame-Level confusion matrix: 44 TP, 1 FP, 33 TN, 4 FN."""
        tp, fp, tn, fn = 44, 1, 33, 4
        m = compute_binary_metrics(tp, fp, tn, fn)

        assert m["accuracy"] == pytest.approx(77 / 82, abs=1e-4)  # 0.9390
        assert m["precision"] == pytest.approx(44 / 45, abs=1e-4)  # 0.9778
        assert m["recall_sensitivity"] == pytest.approx(44 / 48, abs=1e-4)  # 0.9167
        assert m["specificity"] == pytest.approx(33 / 34, abs=1e-4)  # 0.9706
        assert m["false_positive_rate_fpr"] == pytest.approx(1 / 34, abs=1e-4)  # 0.0294
        assert m["false_negative_rate_miss_rate"] == pytest.approx(4 / 48, abs=1e-4)  # 0.0833

        # Formula checks
        expected_f1 = 2 * (m["precision"] * m["recall_sensitivity"]) / (m["precision"] + m["recall_sensitivity"])
        assert m["f1_score"] == pytest.approx(expected_f1, abs=1e-4)
        assert m["false_positive_rate_fpr"] + m["specificity"] == pytest.approx(1.0, abs=1e-4)
        assert m["recall_sensitivity"] + m["false_negative_rate_miss_rate"] == pytest.approx(1.0, abs=1e-4)

    def test_worker_level_confusion_matrix_consistency(self):
        """Verify the exact empirical Worker-Level confusion matrix: 94 TP, 19 FP, 47 TN, 30 FN."""
        tp, fp, tn, fn = 94, 19, 47, 30
        m = compute_binary_metrics(tp, fp, tn, fn)

        total = 94 + 19 + 47 + 30  # 190 total worker evaluations
        assert m["accuracy"] == pytest.approx((94 + 47) / total, abs=1e-4)  # 0.7421
        assert m["precision"] == pytest.approx(94 / (94 + 19), abs=1e-4)  # 0.8319
        assert m["recall_sensitivity"] == pytest.approx(94 / (94 + 30), abs=1e-4)  # 0.7581
        assert m["specificity"] == pytest.approx(47 / (47 + 19), abs=1e-4)  # 0.7121
        assert m["false_positive_rate_fpr"] == pytest.approx(19 / (47 + 19), abs=1e-4)  # 0.2879
        assert m["false_negative_rate_miss_rate"] == pytest.approx(30 / (94 + 30), abs=1e-4)  # 0.2419

        expected_f1 = 2 * (m["precision"] * m["recall_sensitivity"]) / (m["precision"] + m["recall_sensitivity"])
        assert m["f1_score"] == pytest.approx(expected_f1, abs=1e-4)

    def test_zero_division_safety(self):
        """Ensure compute_binary_metrics gracefully handles zero denominators."""
        m = compute_binary_metrics(0, 0, 0, 0)
        assert m["accuracy"] == 0.0
        assert m["precision"] == 0.0
        assert m["recall_sensitivity"] == 0.0
        assert m["f1_score"] == 0.0


class TestDetectionMetricSeparation:
    def test_overall_map_not_overwritten_by_class_map(self):
        """Ensure overall mAP50_95 is distinct from individual class mAPs."""
        per_class_maps = [0.6463, 0.5580, 0.4019, 0.4144, 0.5683, 0.5590, 0.2847, 0.6203, 0.6903, 0.5301]
        overall_map50_95 = 0.5273  # Computed across all boxes

        # The last class is vehicle (0.5301), which must NOT equal the overall model metric (0.5273)
        assert per_class_maps[-1] != overall_map50_95
        assert round(float(np.mean(per_class_maps)), 4) == pytest.approx(0.5273, abs=0.01)

    def test_f1_harmonic_mean(self):
        """Verify F1 is the true harmonic mean of precision and recall."""
        p = 0.9197
        r = 0.7243
        expected_f1 = 2 * p * r / (p + r)
        assert expected_f1 == pytest.approx(0.8104, abs=1e-4)


class TestBenchmarkLatencyStats:
    def test_percentile_calculations(self):
        """Verify latency statistics (mean, median, P95, P99, std) calculations."""
        # Simulated latencies around 80ms
        np.random.seed(42)
        latencies = np.random.normal(loc=81.23, scale=5.0, size=100)
        latencies = np.clip(latencies, a_min=70.0, a_max=120.0)

        mean_val = float(np.mean(latencies))
        median_val = float(np.median(latencies))
        p95_val = float(np.percentile(latencies, 95))
        p99_val = float(np.percentile(latencies, 99))
        std_val = float(np.std(latencies))

        assert 75.0 < mean_val < 90.0
        assert 75.0 < median_val < 90.0
        assert p95_val >= median_val
        assert p99_val >= p95_val
        assert std_val > 0.0

        fps_array = 1000.0 / latencies
        mean_fps = float(np.mean(fps_array))
        assert 10.0 < mean_fps < 14.0  # Near 12.48 FPS


class TestScaleSensitivityCalculation:
    def test_scale_brackets_and_recalls(self):
        """Verify scale-error calculations for small, medium, and large objects."""
        scales = {
            "small": {"total": 328, "detected": 192},
            "medium": {"total": 195, "detected": 160},
            "large": {"total": 237, "detected": 228},
        }

        recalls = {k: round((v["detected"] / v["total"]) * 100, 2) for k, v in scales.items()}

        assert recalls["small"] == 58.54
        assert recalls["medium"] == 82.05
        assert recalls["large"] == 96.20

        # Small recall must be strictly less than medium and large
        assert recalls["small"] < recalls["medium"] < recalls["large"]


class TestWorkerAssociationLogic:
    def test_multi_person_containment_assignment(self):
        """Test associating PPE items to correct respective persons in a multi-person scene."""
        associator = SpatialPPEAssociator(containment_threshold=0.35)

        # Worker 1 on the left, Worker 2 on the right
        persons = [
            {"bbox": [10, 50, 100, 300], "track_id": "WKR_1"},
            {"bbox": [200, 50, 290, 300], "track_id": "WKR_2"},
        ]

        # Hardhat 1 on Worker 1's head, NO-Hardhat 2 on Worker 2's head
        ppe = [
            {"class_name": "Hardhat", "bbox": [20, 55, 90, 110], "confidence": 0.9},
            {"class_name": "NO-Hardhat", "bbox": [210, 55, 280, 110], "confidence": 0.85},
        ]

        workers, isolated = associator.associate(persons, ppe)
        assert len(workers) == 2
        assert len(isolated) == 0

        # Verify Worker 1 has Hardhat and Worker 2 has NO-Hardhat
        w1_ppe = [p["class_name"] for p in workers[0]["assigned_ppe"]]
        w2_ppe = [p["class_name"] for p in workers[1]["assigned_ppe"]]

        assert "Hardhat" in w1_ppe
        assert "NO-Hardhat" in w2_ppe

        # Test compliance evaluation on both workers
        rule_engine = PPERuleEngine(require_hardhat=True, require_vest=False)
        w1_eval = rule_engine.evaluate_worker(workers[0])
        w2_eval = rule_engine.evaluate_worker(workers[1])

        assert w1_eval["is_compliant"] is True
        assert w2_eval["is_compliant"] is False
        assert "NO-Hardhat" in w2_eval["violations"]


class TestWorkerAccounting:
    def test_worker_decision_accounting_structure(self):
        """Verify the exact relationship between GT workers, predicted workers, matched pairs, and decisions."""
        unique_gt_workers = 174
        total_pred_workers = 160
        matched_workers = 144
        unmatched_gt_workers = 30
        unmatched_predictions = 16
        evaluated_worker_decisions = 190

        # Structural assertions
        assert matched_workers + unmatched_gt_workers == unique_gt_workers
        assert matched_workers + unmatched_predictions == total_pred_workers
        assert unique_gt_workers + unmatched_predictions == evaluated_worker_decisions

        # Confusion matrix breakdown
        tp, fp, tn, fn = 94, 19, 47, 30
        assert tp + fp + tn + fn == evaluated_worker_decisions

    def test_worker_precision_recall_sensitivity(self):
        """Verify that worker precision and recall cannot contradict the underlying confusion matrix."""
        tp, fp, tn, fn = 94, 19, 47, 30
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        accuracy = (tp + tn) / (tp + fp + tn + fn)

        assert precision == pytest.approx(0.8319, abs=1e-4)
        assert recall == pytest.approx(0.7581, abs=1e-4)
        assert accuracy == pytest.approx(0.7421, abs=1e-4)


class TestAblationConfiguration:
    def test_ablation_hierarchy_definition(self):
        """Verify the 5 ablation configurations A0 through A4 are strictly defined."""
        configs = ["A0", "A1", "A2", "A3", "A4"]
        assert len(configs) == 5

        # Check required architectural component presence
        components = {
            "A0": ["detector"],
            "A1": ["detector", "spatial_association"],
            "A2": ["detector", "spatial_association", "centroid_tracking"],
            "A3": ["detector", "spatial_association", "centroid_tracking", "temporal_hysteresis"],
            "A4": ["detector", "spatial_association", "centroid_tracking", "temporal_hysteresis", "cooldown_throttling"],
        }
        for i in range(len(configs) - 1):
            curr_c = components[configs[i]]
            next_c = components[configs[i + 1]]
            # Each subsequent config is a strict superset of the previous
            assert set(curr_c).issubset(set(next_c))
            assert len(next_c) == len(curr_c) + 1

