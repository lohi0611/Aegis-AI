"""
AEGIS — Binary Classification Metrics Utility
Pure-math functions for computing confusion matrix metrics.
Zero external dependencies — safe to import in CI without cv2/ultralytics.
"""

from typing import Dict


def compute_binary_metrics(tp: int, fp: int, tn: int, fn: int) -> Dict[str, float]:
    """Calculate full diagnostic metrics from a 2x2 confusion matrix."""
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    # Strict consistency verification
    assert 0.0 <= accuracy <= 1.0, f"Invalid accuracy: {accuracy}"
    assert 0.0 <= precision <= 1.0, f"Invalid precision: {precision}"
    assert 0.0 <= recall <= 1.0, f"Invalid recall: {recall}"
    assert 0.0 <= specificity <= 1.0, f"Invalid specificity: {specificity}"
    assert 0.0 <= f1 <= 1.0, f"Invalid F1: {f1}"
    assert 0.0 <= fpr <= 1.0, f"Invalid FPR: {fpr}"
    assert 0.0 <= fnr <= 1.0, f"Invalid FNR: {fnr}"

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall_sensitivity": round(recall, 4),
        "specificity": round(specificity, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate_fpr": round(fpr, 4),
        "false_negative_rate_miss_rate": round(fnr, 4),
    }
