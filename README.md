# ATK - Equipment Rental Management

## Overview

A comprehensive Module for Managing the Rental of Equipment, Machinery, and Tools with rigorous QMS standards. Refactored for modularity and scalability.

This repository contains the standalone Odoo addon `atk_equipment_rental` extracted from the Elite Sport Odoo project. It is intended to be versioned, reviewed, and reused independently from the full Odoo deployment repository.

## Project Details

- **Technical module name:** `atk_equipment_rental`
- **GitHub repository:** `https://github.com/atkooheji/elite-odoo-atk-equipment-rental`
- **Odoo version target:** Odoo 19
- **Module version:** `19.0.5.1.6`
- **Author:** Elite Finance Master
- **License:** `LGPL-3`
- **Installable:** `True`
- **Application module:** `True`

## What This Module Does

Equipment & Vehicle Rental Management with QMS Workflow and Command Center Dashboard

Use this addon as part of the Elite Sport custom Odoo stack. It may depend on other ATK/Elite modules, so install dependencies first when deploying it outside the original monorepo.

## Dependencies

- `base`
- `mail`
- `product`
- `account`
- `stock`
- `sale_management`
- `web`
- `website_sale`
- `auth_signup`
- `loyalty`
- `atk_prop_mgmt`

## Included Data and Views

- `security/security.xml`
- `security/ir.model.access.csv`
- `data/equipment_rental_data.xml`
- `data/ir_cron_data.xml`
- `data/rental_email_templates.xml`
- `views/root_menu.xml`
- `views/action_views.xml`
- `data/website_menu_data.xml`
- `data/loyalty_program_data.xml`
- `wizard/rental_pickup_wizard_views.xml`
- `wizard/rental_return_wizard_views.xml`
- `wizard/rental_damage_wizard_views.xml`
- `wizard/rental_order_import_wizard_views.xml`
- `views/equipment_rental_views.xml`
- `views/equipment_qc_views.xml`
- `views/product_views.xml`
- `views/res_config_settings_views.xml`
- `views/rental_dashboard_views.xml`
- `views/account_move_views.xml`
- `views/rental_terms_views.xml`
- `views/website_rental_templates.xml`
- `views/menu_views.xml`
- `reports/report_rental_qms.xml`
- `reports/report_rental_mis_profit.xml`
- `reports/report_rental_quotation.xml`
- `reports/report_rental_audit_log.xml`

## Demo Data

- None declared

## Repository Structure

- `__manifest__.py` - Odoo module manifest
- `__init__.py` - module initialization
- `models/` - 9 file(s)
- `views/` - 11 file(s)
- `security/` - 2 file(s)
- `data/` - 6 file(s)
- `controllers/` - 3 file(s)
- `static/` - 4 file(s)
- `wizard/` - 9 file(s)
- `doc/` - 16 file(s)

## Installation

1. Copy this addon folder into an Odoo addons path, for example `/mnt/extra-addons/atk_equipment_rental`.
2. Make sure all dependencies listed above are installed or available in the same Odoo database.
3. Restart the Odoo service so the addon path is rescanned.
4. Activate developer mode in Odoo.
5. Go to **Apps**, update the apps list, search for `atk_equipment_rental`, and install it.

## Upgrade

After pulling changes into an existing Odoo environment, upgrade the module with:

```bash
odoo-bin -d <database_name> -u atk_equipment_rental --stop-after-init
```

For Odoo.sh, push the branch and upgrade the module from the Odoo Apps interface or through the deployment upgrade flow.

## Development Workflow

1. Create a feature branch from `main`.
2. Make changes inside this addon only.
3. Test installation and upgrade on a local/staging database.
4. Check server logs for registry, XML, access-rights, and dependency errors.
5. Commit with a clear message and open a pull request before production use.

## Testing Checklist

- Module installs without registry errors.
- Module upgrades cleanly from the previous version.
- Menus, views, security groups, and access rights load correctly.
- Any scheduled actions, controllers, or integrations run as expected.
- No secrets, database dumps, or environment files are committed.

## Security Notes

This is a public repository. Do not commit `.env` files, credentials, customer data, database backups, private tokens, or production logs. Keep deployment-specific configuration outside the addon source.

## Source Context

Extracted from the Elite Sport Odoo project under:

```text
D:\001-AntiGravity\003-Odoo\elite_sport_project-main\elite_sport_project-main\addons\atk_equipment_rental
```
