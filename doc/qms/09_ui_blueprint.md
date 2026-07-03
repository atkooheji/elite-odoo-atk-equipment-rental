# Phase 6 — UI/UX Design: Blueprint

## 1. Interface Philosophy
The UI is designed for "High-Speed Operations." It uses a **Linear Header Workflow** to move users from Application to Closure without needing to search for buttons.

## 2. Global "Schedule Banner" (Custom Component)
A high-impact, color-coded banner at the top of the form provides instant status for:
- **📅 Schedule**: Current Pickup vs Return times.
- **💰 Balance**: Real-time "Amount Due" to prevent revenue leakage.
- **📊 Profitability**: Direct MIS Net Profit calculation.
- **🛡️ Deposit**: Visual badge for NOT PAID / COLLECTED / REFUNDED.
- **⚡ SLA**: On-Time vs Delayed badges for both Pickup and Return.

## 3. The "Governance Notebook"
The Notebook is organized into logical functional pods:
1. **Equipment Lines**: The core "Shopping Cart" of the rental.
2. **Dispatch QC**: Safety and condition checks before handover.
3. **Logistics & Overtime**: Detailed tracking of "Actuals" vs "Plan."
4. **Return QC**: Inspections for damages and meter readings.
5. **Internal Expenses**: Data entry for MIS cost tracking.
6. **Policies**: Overrides for custom rates and deadlines.

## 4. Stat Boxes (360° Visibility)
- **Delivery**: Count of items currently out with the customer.
- **Returns**: Count of items safely back in inventory.
- **Invoices**: Quick links to Deposit, Rental, and Refund invoices.

## 5. Mobile Readiness
- Uses **Standard Odoo Header Buttons** for full compatibility with the Odoo Mobile app.
- Lists use **Badges and Decorations** (Success/Danger) for quick scanning on small screens.
