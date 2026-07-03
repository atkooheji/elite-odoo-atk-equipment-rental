# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class RentalReturnWizard(models.TransientModel):
    _name = 'equipment.rental.return.wizard'
    _description = 'Validate Rental Return'

    rental_id = fields.Many2one('equipment.rental', string='Rental', required=True)
    line_ids = fields.One2many('equipment.rental.return.wizard.line', 'wizard_id', string='Products')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Fix: Try to get rental_id from res (if set by default_rental_id in context) or active_id
        rental_id = res.get('rental_id') or self._context.get('active_id')
        if rental_id:
            rental = self.env['equipment.rental'].browse(rental_id)
            if not res.get('rental_id'):
                res['rental_id'] = rental.id
            line_ids = []
            for line in rental.line_ids:
                if line.display_type or (line.product_id and line.product_id.type == 'service'):
                    continue
                if line.qty_delivered > line.qty_returned:
                    line_ids.append((0, 0, {
                        'rental_line_id': line.id,
                        'product_id': line.product_id.id,
                        'qty_delivered': line.qty_delivered - line.qty_returned,
                        'qty_returned': line.qty_delivered - line.qty_returned,
                    }))
            res['line_ids'] = line_ids
        return res

    def action_validate(self):
        for line in self.line_ids:
            if line.qty_returned > 0:
                line.rental_line_id.qty_returned += line.qty_returned
                line.rental_line_id.actual_return_date = fields.Datetime.now()
                
        # Move to return_inspection state (QMS center) if all items returned (skip services/sections)
        rental = self.rental_id
        all_returned = True
        for line in rental.line_ids:
            if not line.display_type and line.product_id.type != 'service':
                if line.qty_returned < line.quantity:
                    all_returned = False
                    break
        
        if all_returned:
            rental.state = 'return_inspection'
            rental.return_actual_date = fields.Datetime.now()
            rental.message_post(body=_("📦 <b>Mission Completed:</b> All equipment returned on %s. Order moved to <b>Return Inspection (QMS)</b> for final verification.") % fields.Datetime.now())
        else:
            rental.message_post(body=_("🚛 <b>Partial Return:</b> Some equipment returned. Order remains in <b>On-Rent</b> status."))


class RentalReturnWizardLine(models.TransientModel):
    _name = 'equipment.rental.return.wizard.line'
    _description = 'Rental Return Line Wizard'

    wizard_id = fields.Many2one('equipment.rental.return.wizard', ondelete='cascade')
    rental_line_id = fields.Many2one('equipment.rental.line', required=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    qty_delivered = fields.Float('Picked-up', readonly=True)
    qty_returned = fields.Float('Returned', required=True)
