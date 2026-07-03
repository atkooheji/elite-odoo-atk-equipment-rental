# QMS PHASE 4 — Security Matrix: Elite Sport Rental

## 1. Technical Groups
| ID | Name | Hierarchy |
| :--- | :--- | :--- |
| `group_equipment_rental_user` | Logistics / Operational User | Base Access (Full Ops) |
| `group_equipment_rental_manager` | Operations Manager / QC Officer | Advanced Access (Approve / Overrides) |
| `group_equipment_rental_finance` | Finance / Accountant | Advanced Access (Invoicing / Deposits) |

## 2. Model Access Matrix (ir.model.access.csv)
| Model | User | Manager | Finance |
| :--- | :--- | :--- | :--- |
| `equipment.rental` | RW | RWA | R |
| `equipment.rental.line`| RW | RWA | R |
| `equipment.qc.template` | R | RW | R |
| `equipment.rental.config`| R | RW | R |

## 3. Record Rule Design
- **Multi-Company Constraint**: Users must only see orders for the company they are currently in.
- **Renter Visibility**: Managers can see orders from ALL customers; regular users can only see their assigned orders (if assigned field exists).
- **Global Settings**: Only 'Manager' role can see 'Global Settings' menu via group access on `menuitem`.

## 4. Operational Controls
- **Dispatch Lock**: Regular User CANNOT trigger dispatch if `deposit_collected` is False. Logic: Checked in Python `action_dispatch`.
- **Price Override**: Only Manager can modify `overtime_fee_per_hr` in the 'Policies' tab (Controlled via `groups="group_equipment_rental_manager"` on field).
- **Settlement Bridge**: Standard Finance role handles the payment reconciliation.
