# Phase 9 — Test Strategy: Quality Assurance

## 1. Unit Test Matrix (Automated)
Primary focus on financial and logic integrity:
- **KYC Logic**: Test that `action_approve` fails if ID is missing.
- **Deposit Flow**: Test that the deposit invoice is created automatically and "collected" status updates on payment.
- **Promotion Logic**: Test that a bonus product is added when the quantity reaches the threshold.
- **SLA Calculation**: Verify that the "Delayed" status is applied if actual times exceed deadlines.

## 2. Access & Security Tests
- Verify that a **Rental Operator** cannot edit the "Net Profit" or "Internal Costs" fields.
- Verify that the **Rental Manager** can override the "Deposit Amount."
- Verify that the **Rental Auditor** can see all records but cannot "Approve" or "Close" them.

## 3. Workflow & State Tests
- **The "Happy Path"**: Draft → Approved → On-Rent → Inspection → Closed.
- **The "Exception Path"**: Draft → Cancel.
- **The "Blocking Path"**: Attempting to Close while `amount_due > 0` (Must Fail).

## 4. UI & Performance Tests
- Verify that the **Command Center** dashboard loads in < 2 seconds for a dataset of 1,000+ rentals.
- Verify that the **Form Banner** updates colors correctly for different states.
- Verify that the **Stat Buttons** correctly filter the target list views.
