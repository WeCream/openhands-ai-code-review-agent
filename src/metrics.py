"""Evaluation metrics for case-level detection and finding-level quality."""


def calculate_metrics(results: list[dict]) -> dict:
    """Calculate case-level classification and finding-level review metrics.

    Strict recall is case-level: an issue case is recalled only if at least one
    valid finding has the expected issue type.
    Strict precision is finding-level: correctly typed valid findings from
    issue-positive cases divided by all valid findings (including findings
    emitted for clean cases and valid findings with the wrong issue type).
    """
    tp = sum(bool(r["expected_issue"] and r["detected"]) for r in results)
    fn = sum(bool(r["expected_issue"] and not r["detected"]) for r in results)
    fp = sum(bool(not r["expected_issue"] and r["detected"]) for r in results)
    tn = sum(bool(not r["expected_issue"] and not r["detected"]) for r in results)

    strict_tp = sum(bool(r["expected_issue"] and r["strict_detected"]) for r in results)
    strict_fn = sum(bool(r["expected_issue"] and not r["strict_detected"]) for r in results)
    strict_fp = sum(bool(not r["expected_issue"] and r["valid_finding_count"] > 0) for r in results)
    strict_tn = sum(bool(not r["expected_issue"] and r["valid_finding_count"] == 0) for r in results)

    total_findings = sum(r["finding_count"] for r in results)
    valid_findings = sum(r["valid_finding_count"] for r in results)
    type_matches = sum(r["issue_type_match_count"] for r in results)
    strict_type_match_findings = sum(
        r["issue_type_match_count"] for r in results if r["expected_issue"]
    )

    recall_denominator = tp + fn
    precision_denominator = tp + fp
    fpr_denominator = fp + tn
    accuracy_denominator = tp + tn + fp + fn
    strict_recall_denominator = strict_tp + strict_fn

    return {
        "case_count": len(results),
        "TP": tp,
        "FN": fn,
        "FP": fp,
        "TN": tn,
        "recall": tp / recall_denominator if recall_denominator else None,
        "precision": tp / precision_denominator if precision_denominator else None,
        "false_positive_rate": fp / fpr_denominator if fpr_denominator else None,
        "accuracy": (tp + tn) / accuracy_denominator if accuracy_denominator else None,
        "strict_TP": strict_tp,
        "strict_FN": strict_fn,
        "strict_FP": strict_fp,
        "strict_TN": strict_tn,
        "strict_recall": (
            strict_tp / strict_recall_denominator
            if strict_recall_denominator else None
        ),
        "strict_precision": (
            strict_type_match_findings / valid_findings if valid_findings else None
        ),
        "finding_count": total_findings,
        "valid_finding_count": valid_findings,
        "evidence_pass_rate": valid_findings / total_findings if total_findings else None,
        "issue_type_match_count": type_matches,
    }
