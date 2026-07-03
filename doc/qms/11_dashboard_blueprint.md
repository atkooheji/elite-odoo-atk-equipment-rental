# Phase 8 — Reporting & Dashboard: Management Blueprint

## 1. Dashboard Structure: The "Command Center"
The dashboard is organized into four strategic areas of focus, accessible via high-performance tabs:

### A. Logistics (The Morning Brief)
- **Primary KPI**: "Dispatches Today" and "Returns Today."
- **Goal**: Help the warehouse manager plan labor and transport resources for the next 24 hours.
- **Data Points**: Drafts, Pending Approvals, Today's Pickup deadlines.

### B. Fleet Utilization
- **Primary KPI**: "Fleet Utilization Rate (%)"
- **Goal**: Monitor asset ROI. High utilization = Profitable fleet. Low utilization = Overstocked or poor sales.
- **Status Buckets**: Available, On-Rent, and **Quarantine/Maintenance** (Critical for safety).

### C. Financials (MIS Profitability)
- **Primary KPI**: "Revenue MTD (Month-to-Date)."
- **Goal**: Instant financial pulse. 
- **Drill-down**: Balance due from customers and net profit margins per rental category.

### D. QMS & Compliance Integrity
- **Primary KPI**: "Failed QC Rate (%)"
- **Goal**: Identify equipment categories that are frequently failing dispatch checks, indicating a need for preventative maintenance or vendor replacement.

## 2. Dynamic Filtering
- **Period Filter**: Switches between "This Month" and "This Quarter."
- **Project/Company Filter**: (Multi-company support) to isolate performance for specific branches.

## 3. Interaction Design
- **Actionable Cards**: Clicking on a KPI card (e.g., "Pending Pipeline") automatically redirects the user to the list view of those specific records, filtered and ready for action.
