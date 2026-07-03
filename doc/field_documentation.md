# Equipment Rental: Field Documentation & Guide

This document describes all the interactive fields within the **Equipment Rental System** (`atk_equipment_rental`). Use this as a reference for training and system maintenance.

---

## 1. Primary Order Information
| # | Field Label | Technical Name | Description | Data Type | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | **Order Number** | `name` | Unique system ID (e.g., RNT/0001). | `Char` | Read-only; auto-generated. |
| 1.2 | **Customer** | `partner_id` | The partner renting the equipment. | `Many2one` | Required for quoting. |
| 1.3 | **Pickup Date** | `start_date` | Date & Time the rental starts. | `Datetime` | Affects availability checks. |
| 1.4 | **Return Date** | `end_date` | Expected Date & Time for return. | `Datetime` | Used to calculate duration. |
| 1.5 | **Duration (Days)** | `N/A` | Computed length of the rental. | `Integer` | Based on 24-hour periods (System Policy). |

---

## 2. Order Grid (The Items)
| # | Field Label | Technical Name | Description | Data Type | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 | **Equipment/Service** | `product_id` | The rental item (Unit or Support). | `Many2one` | Links to **Product**. |
| 2.2 | **Quantity** | `quantity` | Number of units booked. | `Float` | Updated on delivery/return. |
| 2.3 | **Price/Day** | `price_unit` | daily cost for one unit. | `Monetary` | Fetched from Pricelist. |
| 2.4 | **Taxes** | `N/A` | VAT or other surcharges. | `Many2many` | To be implemented (Standard Odoo). |

---

## 3. Financial & Risk Control
| # | Field Label | Technical Name | Description | Data Type | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 | **Security Deposit** | `deposit_amount` | Refundable guarantee amount. | `Monetary` | **Mandatory** field. |
| 3.2 | **Total Rental** | `total_amount` | Cumulative total of all lines. | `Monetary` | Shown in status banner. |
| 3.3 | **Internal Expenses** | `expense_line_ids` | MIS grid for costing resources. | `One2many` | Hidden unless MIS toggle on. |
| 3.4 | **Total Internal Cost**| `total_internal_cost` | Sum of direct wages/fuel/parts. | `Monetary` | Used for Margin calculation. |
| 3.5 | **Net Profit** | `net_profit` | Order Revenue - Direct Expenses. | `Monetary` | Key performance indicator. |

---

## 4. Operational Controls (Advanced Tab)
| # | Field Label | Technical Name | Description | Data Type | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 | **Late Fee/HR** | `overtime_fee_per_hr` | Hourly fine for late equipment. | `Float` | Overridden from global config. |
| 4.2 | **Operator Fee/HR** | `operator_overtime_fee_per_hr`| Hourly fine for driver overtime. | `Float` | Only visible if staff present. |
| 4.3 | **QC Checklist** | `dispatch_qc_line_ids` / `return_qc_line_ids` | Mandatory checklist for handover. | `One2many` | Required to Dispatch/Close Order. |
| 4.4 | **Damage Logs** | `dispatch_notes` / `return_notes` | Detailed record of damages found. | `Text` | Appears as a warning to admin. |

---

## 5. Contractual Agreement
| # | Field Label | Technical Name | Description | Data Type | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 | **Terms ID** | `terms_id` | Selection of a contract template. | `Many2one` | Configurable in "Settings". |
| 5.2 | **Rental Terms** | `rental_terms` | The actual contract text (HTML). | `Html` | **Editable** per quotation. |

---

## 6. Logic System (States)
| # | Status Name | Description |
| :--- | :--- | :--- |
| 6.1 | **Application & KYC (Draft)** | Gathering info & credit check. |
| 6.2 | **Approved** | Legal contract signed; ready for loading. |
| 6.3 | **On Rent** | Equipment is at client site; revenue starts. |
| 6.4 | **Return Inspection** | Equipment is back; checking for issues. |
| 6.5 | **Settled & Closed** | Final invoice sent; deposit returned. |

---
**Elite Sports Technology - Field Manual v1.3**
