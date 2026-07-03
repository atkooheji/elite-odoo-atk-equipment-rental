# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RentalDamageWizard(models.TransientModel):
    _name = 'equipment.rental.damage.wizard'
    _description = 'Damage Recovery Invoicing'

    rental_id = fields.Many2one('equipment.rental', string='Rental')
    line_ids = fields.One2many('equipment.rental.damage.wizard.line', 'wizard_id', string='Damaged Items')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        rental_id = self._context.get('active_id')
        if rental_id:
            rental = self.env['equipment.rental'].browse(rental_id)
            res['rental_id'] = rental.id
            line_ids = []
            for line in rental.line_ids.filtered(lambda l: not l.display_type and l.rental_state == 'returned'):
                line_ids.append((0, 0, {
                    'rental_line_id': line.id,
                    'product_id': line.product_id.id,
                    'qty_damaged': 0.0,
                    'repair_cost': 0.0,
                }))
            res['line_ids'] = line_ids
        return res

    def action_invoice_damages(self):
        """Roadmap #47: Strategic Recovery Integration."""
        self.ensure_one()
        invoice_lines = []
        for line in self.line_ids.filtered(lambda l: l.repair_cost > 0):
            invoice_lines.append((0, 0, {
                'name': _('Damage Repair: %s') % line.product_id.display_name,
                'quantity': line.qty_damaged,
                'price_unit': line.repair_cost,
            }))
        
        if not invoice_lines:
            raise UserError(_("Finance Stop: You must enter a repair cost to generate a recovery invoice."))

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.rental_id.partner_id.id,
            'invoice_date': fields.Date.context_today(self),
            'ref': _('Damage Recovery — %s') % self.rental_id.name,
            'invoice_line_ids': invoice_lines,
        })
        invoice.action_post()
        self.rental_id.message_post(body=_("💥 <b>Damage Recovery Triggered:</b> Invoice <b>%s</b> generated for repair costs.") % invoice.name)
        return {
            'name': _('Damage Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

class RentalDamageWizardLine(models.TransientModel):
    _name = 'equipment.rental.damage.wizard.line'
    _description = 'Damage Detail'

    wizard_id = fields.Many2one('equipment.rental.damage.wizard')
    rental_line_id = fields.Many2one('equipment.rental.line')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    qty_damaged = fields.Float('Qty Damaged')
    repair_cost = fields.Monetary('Repair Cost (per unit)')
    currency_id = fields.Many2one('res.currency', related='wizard_id.rental_id.currency_id')
    damage_notes = fields.Text('Structural Damage Details')
