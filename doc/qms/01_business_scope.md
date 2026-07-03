# Phase 1 — Functional Definition: ATK Equipment Rental

## 1. Module Objective
To provide a production-grade, end-to-end framework for managing the rental of high-value equipment, machinery, and vehicles. The module ensures operational excellence through:
- Automated KYC (Know Your Customer) and ID verification.
- Rigorous financial controls (Security Deposits, Overtime Fees, Automatic Billing).
- QMS-driven Quality Control inspections at both Dispatch and Return.
- MIS-driven profitability and SLA performance tracking.

## 2. Business Scope
### In-Scope
- **Customer Identity Management**: Capturing and verifying ID documents for risk mitigation.
- **Rental Lifecycle Management**: Managing the transition from Application to Approved, On-Rent, and Closed.
- **Inventory Reservation**: Tracking delivered and returned quantities.
- **Financial Settlements**: Automatic generation of deposit invoices, rental invoices, and deposit refunds.
- **Operational SLA**: Monitoring deadlines for pickup and return to measure department performance.
- **Internal Costing**: Tracking internal expenses (fuel, labor, maintenance) against rental revenue to calculate Net Profit.
- **Website Rental Portal**: Enabling customers to browse, quote, and book equipment online.
- **Customer Feedback Lifecycle**: Capturing ratings and reviews post-return for QMS performance evaluation.

### Out-of-Scope
- **Direct Procurement**: Buying new equipment from vendors (handled by Odoo Purchase).
- **Physical Maintenance (R&M)**: Detailed workshop repair logs (handled by Odoo Maintenance).
- **Driver Management**: Tracking specific driver shifts or payroll (handled by Odoo Fleet/HR).

## 3. Process Owner
- **Operations Manager**: Responsible for the rental lifecycle and SLA compliance.
- **Quality Manager**: Responsible for the accuracy and completion of QC inspections.

## 4. Key Stakeholders
- **Sales Team**: To create applications and handle customer relations.
- **Accountants**: To verify deposit payments and finalize settlements.
- **Inspectors/Technicians**: To perform physical checks on equipment.
- **Webmaster / Marketing**: Responsible for the nl3ab 26 website presentation and review moderation.
- **Management (MIS Users)**: Interested in fleet utilization and profitability.

## 5. Integration Points
- **Odoo Base/Mail**: For chatter, activities, and internal communication.
- **Odoo Product**: To manage equipment as rentable items.
- **Odoo Accounting**: For invoicing, payments, and credit notes.
- **Odoo Sales**: For quoting and price list integration.
- **Odoo Website**: For the "nl3ab 26" frontend and customer portal.
