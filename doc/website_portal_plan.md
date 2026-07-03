# Strategic Plan: Elite Website Rental Portal v2.0

This plan describes the architectural and user-experience (UX) transformation required to launch the **Elite Sport Technology** digital rental storefront.

---

## **1. The Digital Showcase (Frontend)**
*   **Asset Gallery**: Display high-resolution images, video walk-arounds (showing the unit starting up), and technical PDF documentation.
*   **Elite Branding**: Modern, clean design using the website's primary colors with "Trust Badges" (ISO certified, 24/7 service).
*   **Search & Filtering**: Categorize by "Machine Type" (Generators, Tents, Staff) and "Current Availability".

## **2. The Elite Booking Experience (Interactive)**
*   **Dual Calendar Widget**: A modern, mobile-friendly interface for selecting Pickup & Return dates.
*   **Frictionless Workflow**:
    1.  **Date Selection**: Users select dates; the system calculates "Duration" and "Estimated Cost" instantly.
    2.  **Live Availability**: Backend check for date overlaps (Conflict Detection Logic).
    3.  **One-Click Login**: Simple OTP or Google Login to link the request to the client's account.
    4.  **Instant Hub**: Redirect the user to their "My Order Tracker" immediately after submission.

## **3. Backend Automation (Technical)**
*   **Lead-to-Order Conversion**: Every "Request" automatically generates an `equipment.rental` record in the **Draft** state.
*   **Conflict Detection Logic**:
    *   **The Algorithm**: Scan all non-canceled rental lines for overlapping date ranges.
    *   **The Result**: If `requested_start` < `existing_end` AND `requested_end` > `existing_start`, block the web-booking.
*   **Admin Notification**: Instant email/Odoo notification to the manager: *"New Web Portal Request #RNT-W104 RECEIVED."*

## **4. Customer Self-Service (Portal)**
*   **Status Bar Tracker**: Visual progress bar matched to the Odoo state machine (Draft -> Approved -> On Rent -> Inspection -> Closed).
*   **Document Center**: Clients can view and download:
    - PDF Quotations (with the new Terms & Conditions).
    - Digital Invoices.
    - QC Inspection Photos (Proof of condition).
*   **Payment Gateway**: Direct link to pay the Security Deposit or Invoice via Credit Card.

---

## **Technical Prerequisites**
1.  **Core Dependencies**: `portal`, `website`, `website_sale`.
2.  **API Endpoints**: Specialized controllers to handle the "Availability Pulse Check".
3.  **Responsiveness**: Mobile-first design for project managers using phones on-site.

---
**Elite Sport Technology - Expansion Roadmap v2.1**
