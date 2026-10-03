"""Deterministic validation guardrails — no LLM involved."""
import re
from dataclasses import dataclass, field
from .schemas import Invoice

GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

@dataclass
class ValidationReport:
    valid: bool
    issues: list[str] = field(default_factory=list)

def validate_invoice(inv: Invoice, tol: float = 0.51) -> ValidationReport:
    issues: list[str] = []

    # 1. GSTIN format (India)
    if inv.vendor_gstin and not GSTIN_RE.match(inv.vendor_gstin):
        issues.append(f"Invalid GSTIN format: {inv.vendor_gstin}")

    # 2. Per-line cross-field verification: qty × unit_price == total
    for i, li in enumerate(inv.line_items):
        expected = round(li.quantity * li.unit_price, 2)
        if abs(expected - li.total) > tol:
            issues.append(
                f"Line {i+1} ('{li.description}'): qty×price={expected} ≠ total={li.total}")

    # 3. Subtotal = Σ line totals
    line_sum = round(sum(li.total for li in inv.line_items), 2)
    if abs(line_sum - inv.subtotal) > tol:
        issues.append(f"Subtotal mismatch: Σ lines={line_sum} ≠ subtotal={inv.subtotal}")

    # 4. Grand total = subtotal + tax
    expected_total = round(inv.subtotal + inv.tax_amount, 2)
    if abs(expected_total - inv.grand_total) > tol:
        issues.append(f"Grand total mismatch: subtotal+tax={expected_total} ≠ {inv.grand_total}")

    return ValidationReport(valid=not issues, issues=issues)
