# Phase 4 — Role & Security Design: Separation of Duties

## 1. User Role Definitions
To ensure internal control, we define three distinct access tiers:

| Role | Responsibility | Data Access |
|---|---|---|
| **Rental Operator** | Day-to-day operations (Drafting, QC, Pickup, Returns) | Read/Write (Draft/Rent states only) |
| **Rental Manager** | Approvals, Financial overrides, Config, Dashboard | Full Access (All states) |
| **Rental Auditor** | Compliance verification, Audit logs, MIS reports | Read-Only (All models) |

## 2. RACI Matrix (Rental Lifecycle)
- **R**: Responsible (Does the work)
- **A**: Accountable (Correctness/Approval)
- **C**: Consulted (Input)
- **I**: Informed (Notified)

| Stage | Operator | Manager | Customer | Auditor |
|---|---|---|---|---|
| **Create Order** | R | A | C | I |
| **Approve KYC** | C | R/A | I | I |
| **Collect Deposit** | I | R/A | C | I |
| **Validate Pickup** | R | A | C | I |
| **Return QC** | R | A | C | I |
| **Final Invoice** | I | R/A | C | I |
| **Audit Logs** | I | I | I | R |

## 3. Record Rule Logic (Target)
- **Multi-Company Separation**: Users only see rentals belonging to their allowed companies. 
- **Personal Scope**: (Optional) Operators only see rentals they created. 
- **Manager Scope**: Full visibility for department oversight.

## 4. Field-Level Constraints
- **Profitability (Net Profit)**: Only visible to the **Rental Manager** and **Auditor**. Hidden from Operators.
- **Master Policy (Config)**: Only editable by **Rental Manager**.
