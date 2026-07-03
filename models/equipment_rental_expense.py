# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EquipmentRentalExpense(models.Model):
    _name = 'equipment.rental.expense'
    _description = 'Order Internal Expense'

    rental_id = fields.Many2one('equipment.rental', string='Rental', required=True, ondelete='cascade')
    name = fields.Char('Expense Description', required=True)
    product_id = fields.Many2one('product.product', string='Staff/Resource', domain="[('type', '=', 'service')]")
    qty = fields.Float('Quantity', default=1.0)
    date = fields.Date('Date', default=fields.Date.context_today)
    amount = fields.Monetary('Amount', compute='_compute_amount', store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', related='rental_id.currency_id')
    notes = fields.Text('Notes')

    @api.depends('product_id', 'qty')
    def _compute_amount(self):
        for rec in self:
            if rec.product_id:
                rec.amount = rec.product_id.standard_price * rec.qty
                if not rec.name:
                    rec.name = rec.product_id.display_name
            else:
                # No change if manually set previously
                pass
