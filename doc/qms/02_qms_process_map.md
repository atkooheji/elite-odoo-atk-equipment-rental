# Phase 2 — QMS Process Map: Rental Lifecycle

## 1. Process Overview
The equipment rental process is divided into 7 distinct "Governance Gates" to ensure financial security, operational quality, and digital customer satisfaction.

---

## 2. Gate 0: Online Selection & Request (Pre-Application)
- **Purpose**: Lead generation and digital engagement via nl3ab 26.
- **Inputs**: Website Product Selection, Desired Dates, Customer Email.
- **Process Steps**:
  1. User browses "Wanna Play" interactive catalog.
  2. System creates a `Draft` Rental Request with `is_online_booking=True`.
  3. Automated availability check triggers (Soft Block).
- **Quality Control**: Minimum booking duration and blacked-out date validation.
- **Output**: Online Lead / Draft Quotation.

---

## 2. Gate 1: Application & KYC (Draft → Approved)
- **Purpose**: Verify customer eligibility and secure financial commitment.
- **Inputs**: Customer Name, Requested Equipment, Start/End Dates, ID Card Photo.
- **Process Steps**:
  1. Salesperson enters rental request.
  2. ID/KYC document is uploaded (Binary field).
  3. Master Policy (Overtime Rates/Deposit) is automatically applied from Config.
- **Quality Control (QC)**: `action_approve` prevents progress if ID is missing (unless `skip_id_check` is ticked by a Manager).
- **Financial Control**: Deposit Invoice is automatically generated and must be "Paid" before dispatch.
- **Output**: Verified Application (State: Approved).

---

## 3. Gate 2: Dispatch Validation (Approved → On-Rent)
- **Purpose**: Ensure the equipment is functionally sound and the customer is satisfied.
- **Inputs**: QC Template (Dispatch checks), Actual Pickup DateTime.
- **Process Steps**:
  1. Operator performs visual and functional check using `rental_pickup_wizard`.
  2. Dispatch QMS lines are marked (Pass/Fail).
  3. System records `pickup_actual_date`.
- **Quality Control (QC)**: Mandatory QC checklist verification.
- **MIS Benchmark**: `pickup_sla_status` tracks if the customer took over the equipment within the promised window.
- **Output**: Dispatch Record (State: On-Rent).

---

## 4. Gate 3: Usage & Period Follow-up (On-Rent)
- **Purpose**: Active tracking of fleet location and utilization.
- **Process Steps**:
  1. System monitors `return_deadline`.
  2. Chatter tracks any issues reported during use.
- **Risk**: Late returns causing bottlenecks for other orders.
- **Control**: Real-time SLA counters visible on the Dashboard.

---

## 5. Gate 4: Return Inspection & Damage Control (On-Rent → Inspection)
- **Purpose**: Detect damages and calculate penalties.
- **Inputs**: QC Template (Return checks), Actual Return DateTime.
- **Process Steps**:
  1. Operator performs return check using `rental_return_wizard`.
  2. System automatically calculates `overtime_hours` if return date exceeds `end_date`.
- **Quality Control (QC)**: Return Inspection notes and PASS/FAIL records.
- **Output**: Inspection Report (State: Return Inspection).

---

## 6. Gate 5: Settlement & Closure (Inspection → Closed)
- **Purpose**: Final financial reconciliation.
- **Inputs**: Total Rental Fee, Overtime Fees, Deposit Status.
- **Process Steps**:
  1. Final Invoice generated for the session.
  2. Security Deposit Refund processed (if equipment is undamaged).
  3. Final balance check.
- **Nonconformity Handling**: If `amount_due > 0`, the system blocks `action_close` to prevent financial leakage.
- **Output**: Settled Record (State: Closed).

---

## 6. Gate 6: Quality Audit & Customer Review (Closed → Feedback)
- **Purpose**: Measure customer satisfaction and QMS effectiveness.
- **Inputs**: Rating (1-5), Text Feedback, Portal Response.
- **Process Steps**:
  1. Upon closure, an automated Review Request is triggered.
  2. Customer provides feedback via the Website Portal.
  3. Quality Manager moderates the review for public showing.
- **QMS Benchmark**: Continuous improvement based on customer satisfaction scores.
- **Output**: Verified Customer Review.

---

## 7. Escalation & Audit Trail
- **Documented Records**: Every change in status is tracked in the Odoo Chatter.
- **Retention**: Compliance requires keeping ID documents and QC logs for a minimum of 2 years (local policy).
- **Auditor Access**: Auditors have view-only access to the `equipment.qc` records for performance audits.
