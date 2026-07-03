# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class RentalPickupWizard(models.TransientModel):
    _name = 'equipment.rental.pickup.wizard'
    _description = 'Validate Rental Pickup'

    rental_id = fields.Many2one('equipment.rental', string='Rental', required=True)
    line_ids = fields.One2many('equipment.rental.pickup.wizard.line', 'wizard_id', string='Products')

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
                if line.quantity > line.qty_delivered:
                    line_ids.append((0, 0, {
                        'rental_line_id': line.id,
                        'product_id': line.product_id.id,
                        'qty_reserved': line.quantity - line.qty_delivered,
                        'qty_picked_up': line.quantity - line.qty_delivered,
                    }))
            res['line_ids'] = line_ids
        return res

    def action_validate(self):
        for line in self.line_ids:
            if line.qty_picked_up > 0:
                line.rental_line_id.qty_delivered += line.qty_picked_up
                line.rental_line_id.actual_pickup_date = fields.Datetime.now()
                
        # Move to on_rent state if all equipment picked up (ignore services/sections)
        rental = self.rental_id
        if not rental.pickup_actual_date:
            rental.pickup_actual_date = fields.Datetime.now()
            
        all_picked_up = True
        for l in rental.line_ids:
            if not l.display_type and l.product_id.type != 'service':
                if l.qty_delivered < l.quantity:
                    all_picked_up = False
                    break
        
        if all_picked_up:
            rental.state = 'on_rent'
            rental.message_post(body=_("🚚 <b>Picked-up:</b> All equipment has been delivered to the customer on %s.") % rental.pickup_actual_date)
        else:
            rental.message_post(body=_("🚛 <b>Partial Pickup:</b> Some equipment delivered. Order remains in <b>Approved</b> status."))


class RentalPickupWizardLine(models.TransientModel):
    _name = 'equipment.rental.pickup.wizard.line'
    _description = 'Rental Pickup Line Wizard'

    wizard_id = fields.Many2one('equipment.rental.pickup.wizard', ondelete='cascade')
    rental_line_id = fields.Many2one('equipment.rental.line', required=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    qty_reserved = fields.Float('Reserved', readonly=True)
    qty_picked_up = fields.Float('Picked-up', required=True)
