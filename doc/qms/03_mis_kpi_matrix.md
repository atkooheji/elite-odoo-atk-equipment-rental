# Phase 3 — MIS Design: KPI & Performance Matrix

## 1. Executive Dashboard Objectives
To provide real-time visibility into fleet utilization, financial health, and operational speed.

---

## 2. KPI Matrix: Operational Efficiency (QMS)
| KPI Name | Business Meaning | Formula | Alert Threshold | Source Field |
|---|---|---|---|---|
| **Pickup SLA %** | Speed of dispatch service. | Count(On-Time) / Total Dispatch | < 85% | `pickup_sla_status` |
| **Return SLA %** | Speed of equipment retrieval. | Count(On-Time) / Total Return | < 80% | `return_sla_status` |
| **Fleet Utilization** | % of fleet currently earning revenue. | On-Rent / Total Items | < 60% | `state` = 'on_rent' |
| **Late Return Index** | Severity of delays. | Total Overtime Hours | > 100 Hrs/Month | `overtime_hours` |

---

## 3. KPI Matrix: Financial Health (MIS)
| KPI Name | Business Meaning | Formula | Alert Threshold | Source Field |
|---|---|---|---|---|
| **Gross Revenue** | Total value of all closed rentals. | Sum(Total Amount) | N/A | `total_amount` |
| **Net Profit** | Revenue minus internal costs. | Sum(Revenue - Cost) | < 15% Margin | `net_profit` |
| **Internal Cost Ratio** | % of revenue lost to ops costs. | Cost / Revenue | > 30% | `total_internal_cost` |
| **Deposit Coverage** | Security deposit vs Equipment value risk. | Sum(Deposit) / Fleet Value | < 5% | `deposit_amount` |

---

## 4. Status Breakdown (Bottleneck Analysis)
Management will monitor the following buckets on the dashboard:
- **KYC Pending (Draft)**: Orders waiting for customer documents.
- **Ready for Dispatch (Approved)**: Orders stalled in the warehouse.
- **Active (On-Rent)**: Current revenue-generating assets.
- **In-Inspection**: Items returned but not yet finalized (potential bottleneck).

---

## 5. User & Department Performance
- **Inspector Productivity**: Number of QC checks completed per day.
- **Sales Conversion**: Ratio of Draft orders that reach "Closed" status.
- **SLA Breach Reasons**: Category of delays (Customer late, Warehouse busy, Transport delay).
