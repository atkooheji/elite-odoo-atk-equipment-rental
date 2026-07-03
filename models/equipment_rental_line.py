# -*- coding: utf-8 -*-
import pytz
from odoo import models, fields, api, _

class EquipmentRentalLine(models.Model):
    _name = 'equipment.rental.line'
    _description = 'Equipment Rental Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')], default=False, help="Technical field for layout index")

    rental_id = fields.Many2one('equipment.rental', string='Rental', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', related='rental_id.company_id', store=True)
    product_id = fields.Many2one('product.product', string='Product')
    # ROADMAP #23: Multi-Lot Select (Institutional Command)
    lot_ids = fields.Many2many('stock.lot', string='Serial Numbers', domain="[('product_id', '=', product_id)]")
    # Legacy lot_id kept for single-item compatibility/reporting
    lot_id = fields.Many2one('stock.lot', string='Primary Serial Number', compute='_compute_lot_ids', store=True)
    product_type = fields.Selection(related='product_id.type', string='Product Type', store=True)
    name = fields.Text('Description', required=True)

    quantity = fields.Float('Quantity', default=1.0)
    qty_delivered = fields.Float('Delivered', default=0.0)
    qty_returned = fields.Float('Returned', default=0.0)
    
    actual_pickup_date = fields.Datetime('Actual Pickup')
    actual_return_date = fields.Datetime('Actual Return')
    
    # ROADMAP #43: Fuel & Telemetry Monitoring
    fuel_pickup = fields.Float('Fuel Level % (Pickup)', default=100.0)
    fuel_return = fields.Float('Fuel Level % (Return)')
    
    # ROADMAP #24: Multi-Yard Routing Control
    warehouse_id = fields.Many2one('stock.warehouse', string='Pickup Yard')
    return_warehouse_id = fields.Many2one('stock.warehouse', string='Return Yard')

    overtime_hours = fields.Float('Overtime (Hrs)', compute='_compute_overtime', store=True)
    
    rental_state = fields.Selection([
        ('booked', 'Booked'), ('picked_up', 'Picked-up'), ('returned', 'Returned')
    ], string='Status', compute='_compute_rental_state', store=True)

    available_qty = fields.Float('Available Qty', compute='_compute_availability')
    is_available = fields.Boolean('Is Available', compute='_compute_availability')
    start_date = fields.Datetime(related='rental_id.start_date', store=True)
    end_date = fields.Datetime(related='rental_id.end_date', store=True)
    price_unit = fields.Monetary(string='Unit Price', currency_field='currency_id')
    discount = fields.Float(string='Disc.%', default=0.0)
    currency_id = fields.Many2one('res.currency', related='rental_id.currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') and vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                vals['name'] = product.display_name
            if not vals.get('price_unit') and vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                vals['price_unit'] = product.lst_price
        return super().create(vals_list)

    @api.depends('lot_ids')
    def _compute_lot_ids(self):
        for line in self:
            line.lot_id = line.lot_ids[0] if line.lot_ids else False

    @api.depends('actual_return_date', 'end_date', 'display_type')
    def _compute_overtime(self):
        # ROADMAP #14: Overtime Grace Logic (Institutional Strategy)
        # Definition: Ignore any late return within the first 30 minutes of the deadline.
        grace_period = 0.5 # 30 minutes
        for line in self:
            if line.display_type:
                line.overtime_hours = 0.0
                continue
            if line.actual_return_date and line.end_date and line.actual_return_date > line.end_date:
                diff = (line.actual_return_date - line.end_date).total_seconds() / 3600.0
                line.overtime_hours = max(0.0, diff - grace_period)
            else:
                line.overtime_hours = 0.0

    @api.depends('quantity', 'price_unit', 'discount', 'display_type', 'rental_id.line_ids.quantity', 'rental_id.line_ids.price_unit', 'rental_id.line_ids.discount')
    def _compute_amount(self):
        # Build a cache of line sequences and subtotals to avoid n^2 if possible, 
        # but for typical rental orders (20-50 lines), a simple loop is highly reliable.
        for line in self:
            if not line.display_type:
                line.price_subtotal = (line.quantity * line.price_unit) * (1 - (line.discount or 0.0) / 100.0)
            else:
                # Group Total Logic: Sum products following this section
                total = 0.0
                all_lines = line.rental_id.line_ids.sorted('sequence')
                found_self = False
                for l in all_lines:
                    if l.id == line.id:
                        found_self = True
                        continue
                    if found_self:
                        if l.display_type: # Stop at next section or note
                            break
                        total += (l.quantity * l.price_unit) * (1 - (l.discount or 0.0) / 100.0)
                line.price_subtotal = total

    @api.onchange('product_id', 'rental_id.start_date', 'rental_id.end_date')
    def _onchange_name(self):
        for line in self:
            if line.display_type or not line.product_id:
                continue
            name = line.product_id.display_name
            if line.rental_id.start_date and line.rental_id.end_date:
                user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                sd_local = line.rental_id.start_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                ed_local = line.rental_id.end_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                name += f"\n{sd_local.strftime('%m/%d/%y, %I:%M %p')} to {ed_local.strftime('%m/%d/%y, %I:%M %p')}"
            line.name = name

    @api.depends('quantity', 'qty_delivered', 'qty_returned', 'display_type')
    def _compute_rental_state(self):
        for line in self:
            if line.display_type:
                line.rental_state = False
                continue
            if line.qty_returned >= line.quantity: line.rental_state = 'returned'
            elif line.qty_delivered >= line.quantity: line.rental_state = 'picked_up'
            else: line.rental_state = 'booked'

    @api.depends('product_id', 'rental_id.start_date', 'rental_id.end_date', 'quantity', 'display_type')
    def _compute_availability(self):
        for rec in self:
            if rec.display_type:
                rec.available_qty, rec.is_available = 0.0, True
                continue
            if rec.product_type == 'service':
                rec.available_qty, rec.is_available = 0.0, True
                continue
            qty_on_hand = rec.product_id.qty_available
            overlapping = self.env['equipment.rental.line'].search([
                ('product_id', '=', rec.product_id.id),
                ('rental_id.state', 'not in', ['draft', 'cancel', 'closed']),
                ('start_date', '<', rec.end_date),
                ('end_date', '>', rec.start_date)
            ])
            if rec.id: overlapping -= rec
            rec.available_qty = qty_on_hand - sum(overlapping.mapped('quantity'))
            rec.is_available = (rec.available_qty >= rec.quantity)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price

    @api.onchange('display_type')
    def _onchange_display_type(self):
        if self.display_type:
            self.product_id = False
            self.quantity = 0.0
            self.price_unit = 0.0
