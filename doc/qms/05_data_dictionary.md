# Phase 5 — Data Model Design: Technical Dictionary

## 1. Core Model: `equipment.rental`
- **Purpose**: Tracks the lifecycle, financials, and QMS status of a rental session.
- **Key Fields**:
| Field | Business Name | Type | Purpose |
|---|---|---|---|
| `name` | Order Reference | Char | Unique ID (Seq: `equipment.rental`). |
| `partner_id` | Customer | Many2one | The primary renter. |
| `state` | Status | Selection | Governance state machine. |
| `renter_id_card` | ID Document | Binary | Mandatory KYC attachment. |
| `deposit_amount` | Security Deposit | Float | Risk mitigation (Default: policy). |
| `total_amount` | Total Revenue | Monetary | Sum of all rental lines (Computed). |
| `net_profit` | Net Profit (MIS) | Monetary | Revenue - Internal Expenses (MIS). |
| `pickup_deadline` | Pickup Deadline | Datetime | Calculated based on QMS SLA policy. |
| `pickup_sla_status`| Pickup SLA | Selection | On-Time vs Delayed (Performance). |

---

## 2. Rental Lines: `equipment.rental.line`
- **Purpose**: Items and professional services included in the rental.
- **Key Fields**:
| Field | Business Name | Type | Purpose |
|---|---|---|---|
| `product_id` | Equipment | Many2one | The asset being rented. |
| `quantity` | Qty | Float | Number of items. |
| `price_unit` | Rate | Float | Rental rate per period. |
| `qty_delivered`| Pickup Count | Float | Actual items taken by customer. |
| `qty_returned` | Return Count | Float | Actual items returned to depot. |

---

## 3. QC Inspections: `equipment.rental.qc.line`
- **Purpose**: Tracks the condition of equipment at both dispatch and return.
- **Key Fields**:
| Field | Business Name | Type | Purpose |
|---|---|---|---|
| `template_id` | Checkpoint | Many2one | Pre-defined quality rule (e.g., Oil Level). |
| `status` | Inspection Result | Selection | PASS, FAIL, or N/A. |
| `stage_type` | Inspection Phase | Selection | Dispatch vs Return. |
