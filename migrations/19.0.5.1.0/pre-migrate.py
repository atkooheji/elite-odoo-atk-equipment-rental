# -*- coding: utf-8 -*-
"""
Migration: 19.0.5.1.0
Remove stale res.config.settings field registrations that were renamed.
- default_deposit_amount  → rental_deposit_amount
- default_skip_id_check   → skip_id_check

Odoo raises "Field without attribute 'default_model'" if these old names
remain as ir.model.fields records pointing to res.config.settings.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    stale_fields = ['default_deposit_amount', 'default_skip_id_check']
    for field_name in stale_fields:
        cr.execute("""
            DELETE FROM ir_model_fields
            WHERE model_id IN (
                SELECT id FROM ir_model WHERE model = 'res.config.settings'
            )
            AND name = %s
        """, (field_name,))
        if cr.rowcount:
            _logger.info(
                "Migration 19.0.5.1.0: Removed stale field 'res.config.settings.%s' "
                "from ir_model_fields (%d row(s) deleted).",
                field_name, cr.rowcount
            )
