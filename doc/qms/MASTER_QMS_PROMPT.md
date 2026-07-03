# Master QMS Prompt: ATK Equipment Rental Management

## 1. System Mission
Build and manage a production-grade Equipment Rental ecosystem in Odoo 19 Enterprise. The system must be governed by **ISO 9001-style QMS controls** and **Strategic MIS reporting** to ensure zero financial leakage and 100% operational safety.

## 2. Core Governance: The State Machine
Every rental must strictly follow this lifecycle:
1. **Application & KYC (Draft)**: Mandatory ID document upload. 
2. **Approved (Pending Dispatch)**: Deposit invoice must be PAID (Deposit Management).
3. **On-Rent**: Dispatch QC checklist must be cleared; Actual Pickup date recorded.
4. **Return Inspection**: Return QC checklist must be cleared; Damages & Overtime recorded.
5. **Closed & Settled**: Final Invoice paid; Security Deposit refunded.

## 3. Financial & Strategic Controls (MIS)
- **Automatic Deposit Management**: System auto-generates a Security Deposit invoice on approval and manages the refund/credit note on closure.
- **Strategic Pricing**: Late fees (Overtime) are calculated per hour for both Equipment and Operators based on Master Global Policies.
- **Profitability Tracking**: Every rental order calculates **Net Profit** by subtracting internal operational expenses (Fuel, Labor, Transport) from total revenue.

## 4. Quality Control (QMS)
- **Checklist Seeding**: On record creation, Dispatch and Return QC lines are automatically pulled from global templates.
- **SLA Monitoring**: System calculates "Promised vs Actual" times for Pickup and Return, flagging **"Delayed"** records instantly on the dashboard.

## 5. Management Dashboard (Command Center)
Management must have 360° visibility via four tabs:
- **Logistics**: Today's workload (Dispatches vs Returns).
- **Fleet**: Real-time Utilization Rate and Quarantine status.
- **Financials**: Revenue MTD and Outstanding Balances.
- **QMS**: Compliance/QC failure rates.

## 6. Functional Architecture
- **Root Model**: `equipment.rental`
- **Line Items**: `equipment.rental.line` (supports Equipment + Service/Operators)
- **Quality Logic**: `equipment.qc.line` (linked to templates)
- **MIS Costs**: `equipment.rental.expense`

---

## 💡 How to use this documentation:
This Master Prompt, combined with files `01` through `11` in the `/doc/qms/` directory, represents the **Complete Architecture Statement**. Any developer or auditor can follow these files to rebuild or verify the system's integrity.
