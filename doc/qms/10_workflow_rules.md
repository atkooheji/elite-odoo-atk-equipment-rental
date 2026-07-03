# Phase 7 — Automation & Workflow: Logic & Command Rules

## 1. Institutional Defaults (Global Policy)
The system retrieves the following parameters from the **Master Configuration (`ir.config_parameter`)**:
- **Rental Duration Policy**: (Default: 24 hrs) automatically sets `end_date` based on the requested `start_date`.
- **Financial Rates**: Base Overtime, Operator HR rates, and Deposit Amount are all central-policy driven.

## 2. Strategic Automation
- **Autonomous Promotions**: The system monitors the quantity of items in the order. If a threshold (e.g., > 5 items) is met, a **PROMO Bonus** product is automatically added with a zero-unit price.
- **Operator Multi-Sync**: If "Include Operators" is enabled, the system hard-links a Service Product to the order lines and synchronizes the quantity with the `operator_count` field.

## 3. SLA Breach Monitoring
- **Pickup SLA**: Deadlines are calculated from `start_date`. If `pickup_actual_date` is later, the state is marked as **Delayed**.
- **Return SLA**: Deadlines are calculated from `end_date`. If `return_actual_date` is later, the state is marked as **Delayed**.

## 4. State Machine Transitions (Enforcement)
- **KYC Gate**: `action_approve` validates that ID document binary is present.
- **Settlement Gate**: `action_close` blocks if `amount_due > 0`, forcing the user to collect payment before closing the file.

## 5. QC Template Seeding
- On record creation, the system autonomously seeds the **Dispatch QC** and **Return QC** tabs from global templates, ensuring that no technician "forgets" a safety step.
