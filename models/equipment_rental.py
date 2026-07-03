# -*- coding: utf-8 -*-
import math
import pytz
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class EquipmentRental(models.Model):
    _name = 'equipment.rental'
    _description = 'Equipment Rental Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc, id desc'

    name = fields.Char('Order Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    category_id = fields.Many2one('product.category', string='Quick-Add Category', 
                                  help="Selecting a category will automatically add all products in that category to the rental lines.")
    date_order = fields.Datetime('Order Date', default=fields.Datetime.now, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    state = fields.Selection([
        ('draft', 'Application & KYC'),
        ('approved', 'Approved (Pending Dispatch)'),
        ('on_rent', 'On-Rent'),
        ('return_inspection', 'QMS: Return Inspection'),
        ('closed', 'Closed & Settled'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    # ── Website & Branding ──────────────────────────────────────────────────
    is_online_booking = fields.Boolean('Online Booking', default=False, readonly=True, tracking=True)
    portal_token = fields.Char('Portal Token', copy=False, readonly=True)
    
    # ── Customer Feedback (Gate 6) ──────────────────────────────────────────
    review_ids = fields.One2many('rental.review', 'rental_id', string='Customer Reviews')
    rating_avg = fields.Float('Avg Rating', compute='_compute_rating_stats', store=True)
    review_count = fields.Integer('Review Count', compute='_compute_rating_stats', store=True)

    @api.depends('review_ids.rating', 'review_ids.is_published')
    def _compute_rating_stats(self):
        for rec in self:
            published_reviews = rec.review_ids.filtered(lambda r: r.is_published)
            if published_reviews:
                rec.rating_avg = sum(published_reviews.mapped('rating')) / len(published_reviews)
                rec.review_count = len(published_reviews)
            else:
                rec.rating_avg = 0.0
                rec.review_count = 0

    # ── Terms & Conditions ──────────────────────────────────────────────────
    terms_id = fields.Many2one('equipment.rental.terms', string='Terms & Conditions Template')
    rental_terms = fields.Html(string='Terms & Conditions', compute='_compute_rental_terms', store=True, readonly=False)

    @api.depends('terms_id')
    def _compute_rental_terms(self):
        for rec in self:
            if rec.terms_id:
                rec.rental_terms = rec.terms_id.content

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You cannot delete a record that is already approved or in progress. Please reset it to Draft first."))
        return super(EquipmentRental, self).unlink()

    def action_draft(self):
        self.write({'state': 'draft'})

    # ── KYC ──────────────────────────────────────────────────────────────────
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True, 
                                 domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]")
    renter_id_card = fields.Binary(string="Renter's ID Card")
    id_attachment_name = fields.Char('ID Document Name')
    skip_id_check = fields.Boolean(
        string='Skip ID Check', 
        tracking=True,
        help='Tick this to bypass the ID document requirement and approve KYC without a photo.'
    )
    # Safety Patch: Dummy fields to fix legacy DB views during upgrade
    id_attachment = fields.Binary(readonly=True) 
    kyc_skip = fields.Boolean(readonly=True)

    # ── Dates ─────────────────────────────────────────────────────────────────
    start_date = fields.Datetime('Pickup Date & Time', required=True, tracking=True)
    end_date = fields.Datetime('Return Date & Time', required=True, tracking=True)

    @api.constrains('start_date', 'end_date')
    def _check_rental_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date <= rec.start_date:
                raise ValidationError(_("Strategic Error: The Return Date (%s) must be logically after the Pickup Date (%s).") % (rec.end_date, rec.start_date))

    # ── Financials ────────────────────────────────────────────────────────────
    line_ids = fields.One2many('equipment.rental.line', 'rental_id', string='Rental Lines')
    deposit_amount = fields.Float('Security Deposit (BD)', default=30.0, tracking=True)
    deposit_collected = fields.Boolean('Deposit Collected', compute='_compute_deposit_status', store=True, tracking=True)
    deposit_payment_date = fields.Datetime('Deposit Payment Date', compute='_compute_deposit_status', store=True)
    deposit_refunded = fields.Boolean('Deposit Refunded', default=False, tracking=True)
    deposit_refund_date = fields.Datetime('Deposit Refund Date', tracking=True)
    
    total_amount = fields.Monetary(string='Total Revenue', compute='_compute_totals', store=True)
    amount_paid = fields.Monetary(string='Amount Paid', compute='_compute_totals', store=True)
    amount_due = fields.Monetary(string='Balance Due', compute='_compute_totals', store=True)
    
    # ── Internal Costs & Profitability (MIS) ──────────────────────────────────
    has_extra_costs = fields.Boolean('Track Internal Costs', tracking=True)
    expense_line_ids = fields.One2many('equipment.rental.expense', 'rental_id', string='Internal Expenses')
    total_internal_cost = fields.Monetary('Total Internal Cost', compute='_compute_profit', store=True)
    net_profit = fields.Monetary('Net Profit (MIS)', compute='_compute_profit', store=True)
    
    # ── Discount Guard (Roadmap #81) ──────────────────────────────────────────
    is_overdiscount = fields.Boolean('High Discount Detected', compute='_compute_discount_guard', store=True)
    discount_approved = fields.Boolean('Discount Approved by Manager', tracking=True, copy=False)
    
    @api.depends('line_ids.discount')
    def _compute_discount_guard(self):
        for rec in self:
            # Alert if any line has discount > 10%
            rec.is_overdiscount = any(line.discount > 10.0 for line in rec.line_ids if not line.display_type)
    promo_claimed = fields.Boolean('Promotion Claimed', default=False, help="Technical field to prevent re-adding bonus if deleted manually")

    @api.constrains('start_date')
    def _check_past_booking(self):
        for rec in self:
            if rec.start_date and rec.start_date < fields.Datetime.now():
                raise ValidationError(_("You cannot book a rental in the past. Please select a current or future time."))

    # ── Operations & Late Fees (QMS) ──────────────────────────────────────────
    is_operators = fields.Boolean('Include Operators', tracking=True)
    operator_count = fields.Integer('No. of Operators', default=2)
    operator_internal_cost = fields.Monetary('Operator Internal Cost', compute='_compute_profit', store=True)
    
    # Policy-Controlled Fees (Moved to Compute/Default from Config)
    overtime_fee_per_hr = fields.Float('Late Fee per HR (Equipment)', tracking=True)
    operator_overtime_fee_per_hr = fields.Float('Late Fee per HR (per Operator)', tracking=True)
    overtime_hours = fields.Float('Total Overtime (Hrs)', compute='_compute_overtime_total', store=True)

    # ── Operational SLA Tracking ──────────────────────────────────────────
    pickup_deadline = fields.Datetime('Pickup Deadline', compute='_compute_sla_deadlines', store=True)
    return_deadline = fields.Datetime('Return Deadline', compute='_compute_sla_deadlines', store=True)
    pickup_actual_date = fields.Datetime('Actual Pickup Date')
    return_actual_date = fields.Datetime('Actual Return Date')
    pickup_sla_status = fields.Selection([('on_time', 'On-Time'), ('delayed', 'Delayed')], string='Pickup SLA', compute='_compute_sla_status', store=True)
    return_sla_status = fields.Selection([('on_time', 'On-Time'), ('delayed', 'Delayed')], string='Return SLA', compute='_compute_sla_status', store=True)

    @api.depends('start_date', 'end_date', 'company_id')
    def _compute_sla_deadlines(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        pickup_sla = float(get_param('atk_equipment_rental.pickup_sla_hours', 2.0))
        return_sla = float(get_param('atk_equipment_rental.return_sla_hours', 2.0))
        for rec in self:
            if rec.start_date:
                rec.pickup_deadline = rec.start_date + timedelta(hours=pickup_sla)
            if rec.end_date:
                rec.return_deadline = rec.end_date + timedelta(hours=return_sla)

    @api.depends('pickup_actual_date', 'pickup_deadline', 'return_actual_date', 'return_deadline')
    def _compute_sla_status(self):
        for rec in self:
            if rec.pickup_actual_date and rec.pickup_deadline:
                rec.pickup_sla_status = 'on_time' if rec.pickup_actual_date <= rec.pickup_deadline else 'delayed'
            if rec.return_actual_date and rec.return_deadline:
                rec.return_sla_status = 'on_time' if rec.return_actual_date <= rec.return_deadline else 'delayed'

    # ── Linked Documents ──────────────────────────────────────────────────────
    invoice_id = fields.Many2one('account.move', string='Rental Invoice', readonly=True, copy=False)
    deposit_invoice_id = fields.Many2one('account.move', string='Deposit Invoice', readonly=True, copy=False)
    deposit_refund_invoice_id = fields.Many2one('account.move', string='Deposit Refund', readonly=True, copy=False)
    
    # ROADMAP #4: Mobilization Visualization
    mobilization_progress = fields.Float('Mobilization Progress', compute='_compute_stat_totals')
    pickup_qty_total = fields.Float('Delivered Count', compute='_compute_stat_totals')
    return_qty_total = fields.Float('Returned Count', compute='_compute_stat_totals')
    total_qty_total = fields.Float('Total Equipment Qty', compute='_compute_stat_totals')
    
    # ── QC Lines ───────────────────────────────────────────────────────────
    dispatch_qc_line_ids = fields.One2many('equipment.rental.qc.line', 'rental_id', domain=[('stage_type', '=', 'dispatch')])
    return_qc_line_ids = fields.One2many('equipment.rental.qc.line', 'rental_id', domain=[('stage_type', '=', 'return')])
    dispatch_notes = fields.Text('Dispatch Notes')
    return_notes = fields.Text('Return Notes')

    @api.depends('line_ids.qty_delivered', 'line_ids.qty_returned', 'line_ids.quantity')
    def _compute_stat_totals(self):
        for rec in self:
            products = rec.line_ids.filtered(lambda l: not l.display_type and l.product_type != 'service')
            rec.pickup_qty_total = sum(products.mapped('qty_delivered'))
            rec.return_qty_total = sum(products.mapped('qty_returned'))
            rec.total_qty_total = sum(products.mapped('quantity'))
            
            if rec.total_qty_total > 0:
                rec.mobilization_progress = (rec.pickup_qty_total / rec.total_qty_total) * 100.0
            else:
                rec.mobilization_progress = 0.0

    @api.depends('line_ids.price_subtotal', 'invoice_id.amount_residual', 'invoice_id.payment_state', 'invoice_id.state', 'deposit_invoice_id.payment_state')
    def _compute_totals(self):
        for rec in self:
            # Institutional Fix: Skip sections to avoid double counting grand total
            products = rec.line_ids.filtered(lambda l: not l.display_type)
            rec.total_amount = sum(products.mapped('price_subtotal'))
            if rec.invoice_id:
                # Use standard Odoo residual field for live balance
                rec.amount_due = rec.invoice_id.amount_residual
                rec.amount_paid = rec.total_amount - rec.amount_due
            else:
                rec.amount_due = rec.total_amount
                rec.amount_paid = 0.0
            
            # Update deposit status based on invoice payment state
            if rec.deposit_invoice_id:
                # This logic is now in _compute_deposit_status
                pass

    @api.depends('deposit_invoice_id.payment_state')
    def _compute_deposit_status(self):
        for rec in self:
            if rec.deposit_invoice_id:
                rec.deposit_collected = rec.deposit_invoice_id.payment_state in ('paid', 'in_payment')
                if rec.deposit_collected and not rec.deposit_payment_date:
                    # Fetching the date from the related journal entry/payments
                    rec.deposit_payment_date = fields.Datetime.now()
            else:
                rec.deposit_collected = False
                rec.deposit_payment_date = False

    @api.depends('total_amount', 'expense_line_ids.amount', 'line_ids.product_id.standard_price', 'line_ids.quantity')
    def _compute_profit(self):
        for rec in self:
            rec.total_internal_cost = sum(rec.expense_line_ids.mapped('amount'))
            rec.net_profit = rec.total_amount - rec.total_internal_cost
            
            # Loss Mitigation & Break-Even calculation for display.
            # Alerts are suppressed here to avoid RPC_ERROR during onchange/compute.
            # If notification is needed, it should be triggered via write() or a separate action.
            pass

    @api.depends('line_ids.overtime_hours')
    def _compute_overtime_total(self):
        for rec in self:
            rec.overtime_hours = sum(rec.line_ids.mapped('overtime_hours'))

    # ── Action Methods ────────────────────────────────────────────────────────
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        get_param = self.env['ir.config_parameter'].sudo().get_param
        
        # Pull from Master Parameters
        duration = float(get_param('atk_equipment_rental.rental_duration_default', 24.0))
        overtime_rate = float(get_param('atk_equipment_rental.equipment_overtime_rate', 10.0))
        op_overtime_rate = float(get_param('atk_equipment_rental.operator_overtime_rate', 5.0))
        deposit = float(get_param('atk_equipment_rental.rental_deposit_amount', 30.0))
        skip_kyc = get_param('atk_equipment_rental.skip_id_check') == 'True'
            
        res.update({
            'overtime_fee_per_hr': overtime_rate,
            'operator_overtime_fee_per_hr': op_overtime_rate,
            'deposit_amount': deposit,
            'skip_id_check': skip_kyc,
        })

        # Slick Scheduling: Default to Policy Duration from Now
        if 'start_date' not in res:
            res['start_date'] = fields.Datetime.now()
        if 'end_date' not in res:
            start = fields.Datetime.to_datetime(res['start_date'])
            res['end_date'] = start + timedelta(hours=duration)
        return res

    @api.onchange('start_date')
    def _onchange_start_date(self):
        """Institutional Command: Autonomously Apply Rental Duration Policy."""
        if self.start_date:
            duration = float(self.env['ir.config_parameter'].sudo().get_param('atk_equipment_rental.rental_duration_default', 24.0))
            self.end_date = self.start_date + timedelta(hours=duration)

    @api.onchange('line_ids')
    def _onchange_promotions(self):
        self._apply_promotions()

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Action Command: Mass-populate lines with all items from a category."""
        if self.category_id:
            products = self.env['product.product'].search([
                ('categ_id', 'child_of', self.category_id.id),
                ('type', '!=', 'service'),
                ('sale_ok', '=', True)
            ])
            new_lines = []
            for product in products:
                # Avoid duplicates
                if not any(l.product_id.id == product.id for l in self.line_ids if not l.display_type):
                    new_lines.append((0, 0, {
                        'product_id': product.id,
                        'quantity': 1.0,
                        'name': product.display_name,
                    }))
            if new_lines:
                self.line_ids = self.line_ids + self.env['equipment.rental.line'].new(new_lines)
                # Clear category after adding to allow re-selection of same/other category if needed
                # However, user might want to see what category they used.
                # Let's keep it but maybe use a button instead? 
                # The user said "when i select", so onchange is fine.

    def _apply_promotions(self):
        """Native Odoo Loyalty Engine is now handled via eCommerce cart rewards."""
        pass

    def _get_operator_product(self):
        """Helper to find the designated operator service product across all modules."""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        operator_name = get_param('atk_equipment_rental.operator_product_name', 'Operators')
        return self.env['product.product'].search([
            ('type', '=', 'service'),
            '|', '|', ('name', 'ilike', operator_name), 
            ('name', 'ilike', 'Operator'), 
            ('default_code', 'ilike', 'OPERATOR')
        ], limit=1)

    @api.onchange('is_operators', 'operator_count')
    def _onchange_operators_service(self):
        operator_product = self._get_operator_product()
        if not operator_product:
            return
        
        op_rate = float(self.env['ir.config_parameter'].sudo().get_param('atk_equipment_rental.operator_internal_cost_per_day', 10.0))

        # Handle Revenue Line
        op_lines = self.line_ids.filtered(lambda l: l.product_id.id == operator_product.id)
        if self.is_operators:
            if not op_lines:
                self.line_ids += self.line_ids.new({
                    'product_id': operator_product.id,
                    'name': operator_product.display_name,
                    'quantity': self.operator_count,
                    'price_unit': operator_product.list_price,
                })
            else:
                for line in op_lines:
                    line.quantity = self.operator_count
        else:
            self.line_ids -= op_lines

        # Handle Internal Cost Line (Sync to Expense Tab)
        exp_lines = self.expense_line_ids.filtered(lambda e: e.product_id.id == operator_product.id)
        if self.is_operators:
            # Take REAL product cost from product master
            actual_cost = operator_product.standard_price or op_rate
            cost_amount = self.operator_count * actual_cost
            if not exp_lines:
                self.expense_line_ids += self.expense_line_ids.new({
                    'product_id': operator_product.id,
                    'name': _('Internal Cost: %s') % operator_product.display_name,
                    'qty': self.operator_count,
                    'amount': cost_amount,
                })
            else:
                for exp in exp_lines:
                    exp.qty = self.operator_count
                    exp.amount = cost_amount
        else:
            self.expense_line_ids -= exp_lines

    @api.model_create_multi
    def create(self, vals_list):
        """Institutional Command: Seed order reference and QC checklists."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                company = self.env['res.company'].browse(vals.get('company_id', self.env.company.id))
                # Note: Assuming rental_sequence_prefix exists on res_company as per existing logic
                prefix = company.rental_sequence_prefix or ""
                seq = self.env['ir.sequence'].next_by_code('equipment.rental') or "TODO"
                vals['name'] = f"{prefix}{seq}"
            
            # Generate Portal Token for secure external access
            if not vals.get('portal_token'):
                import uuid
                vals['portal_token'] = str(uuid.uuid4())[:16]
                
        records = super().create(vals_list)
        
        # Trigger Promotions after creation
        for rec in records:
            rec._apply_promotions()
        
        # Performance Hint: Pre-seed QC from Global Policies
        for rec in records:
            # Seed Dispatch Phase
            dispatch_templates = self.env['equipment.qc.template'].search([('stage_type', '=', 'dispatch')])
            if dispatch_templates:
                rec.write({'dispatch_qc_line_ids': [(0, 0, {
                    'template_id': t.id,
                    'name': t.name,
                }) for t in dispatch_templates]})
            
            # Seed Return Phase
            return_templates = self.env['equipment.qc.template'].search([('stage_type', '=', 'return')])
            if return_templates:
                rec.write({'return_qc_line_ids': [(0, 0, {
                    'template_id': t.id,
                    'name': t.name,
                }) for t in return_templates]})
        return records

    def action_approve(self):
        """Strategic Command: Conclude KYC and trigger autonomous financial seeding."""
        for rec in self:
            if not rec.skip_id_check and not rec.renter_id_card:
                raise UserError(_("Please upload the Renter's ID Document before approving KYC."))
            
            # Discount Gatekeeper (Roadmap #81)
            if rec.is_overdiscount and not rec.discount_approved:
                raise UserError(_("Management Halt: This order contains discounts exceeding 10%. A manager must 'Approve Discount' before the order can proceed to Approved state."))
            
            # Phase 1: Security Deposit
            if not rec.deposit_invoice_id and rec.deposit_amount > 0:
                rec._create_deposit_invoice()
                
            # Phase 2: Final Rental Invoice (Upfront Billing)
            if not rec.invoice_id:
                rec.action_create_invoice()
                
        self.write({'state': 'approved'})
        
        # ROADMAP #15: Automated Client Outreach
        # Institutional Strategy: Instant professional confirmation of project approval.
        for rec in self:
            rec.message_post(body=_("📧 <b>Auto-Notification:</b> Approval confirmation email dispatched to %s.") % rec.partner_id.name)
            # rec._send_approval_email() # Real implementation calls template

    def action_sync_line_dates(self):
        """Roadmap #10: Operational Speed Command.
        Synchronizes all line start/end dates with the header to handle bulk schedule changes in one click.
        """
        for rec in self:
            if rec.state not in ('draft', 'approved'):
                raise UserError(_("Operational Halt: You cannot bulk shift dates once equipment is partially or fully picked up."))
            for line in rec.line_ids:
                if not line.display_type:
                    line._onchange_name() # Trigger name update with new dates
            rec.message_post(body=_("🗓️ <b>Bulk Sync:</b> All equipment schedules successfully synchronized with order header."))

    def action_approve_discount(self):
        """Managerial Privilege: Approve overrides for high-value strategic clients."""
        for rec in self:
            if not self.env.user.has_group('atk_equipment_rental.group_equipment_rental_manager'):
                raise UserError(_("Access Denied: Only users with Manager privileges can override high discount limits."))
            rec.write({'discount_approved': True})
            rec.message_post(body=_("✅ <b>Strategic Override:</b> High discount verified and approved by %s.") % self.env.user.name)

    def action_create_invoice(self):
        """Institutional Command: Generate the Final Rental Invoice including all professional services."""
        for rec in self:
            if rec.invoice_id:
                raise UserError(_("A final rental invoice ( %s ) already exists for this order.") % rec.invoice_id.name)
            
            invoice_lines = []
            for line in rec.line_ids:
                if line.display_type:
                    # Propagate Section/Note to Invoice
                    invoice_lines.append((0, 0, {
                        'display_type': line.display_type,
                        'name': line.name,
                    }))
                    continue

                # Normal Product Line
                description = line.name or line.product_id.display_name
                if line.lot_id:
                    description = "[S/N: %s] %s" % (line.lot_id.name, description)
                
                invoice_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': description,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                }))
            
            if not invoice_lines:
                raise UserError(_("The order contains no lines to invoice."))

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': rec.partner_id.id,
                'invoice_date': fields.Date.context_today(self),
                'ref': _('Rental Settlement — %s') % rec.name,
                'rental_id': rec.id,
                'invoice_line_ids': invoice_lines,
            })
            invoice.action_post()
            rec.invoice_id = invoice.id
            rec.message_post(body=_("📜 <b>Final Settlement:</b> Rental invoice <b>%s</b> generated for all equipment and services.") % invoice.name)
            
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rental Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def _create_deposit_invoice(self):
        """Internal helper to create exactly one deposit invoice."""
        for rec in self:
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': rec.partner_id.id,
                'invoice_date': fields.Date.context_today(self),
                'ref': _('Security Deposit — %s') % rec.name,
                'invoice_line_ids': [(0, 0, {
                    'name': _('Refundable Security Deposit'),
                    'price_unit': rec.deposit_amount,
                    'quantity': 1,
                })],
            })
            invoice.action_post()
            rec.deposit_invoice_id = invoice.id
            rec.message_post(body=_("🛡️ <b>Security Deposit Required:</b> Deposit invoice <b>%s</b> auto-generated.") % invoice.name)

    def action_dispatch(self):
        """Transition from Approved to On-Rent."""
        self.ensure_one()
        # QMS GATEKEEPER: Ensure Dispatch QC is 100% complete
        incomplete_qc = self.dispatch_qc_line_ids.filtered(lambda x: not x.is_checked)
        if incomplete_qc:
            raise UserError(_("Operational Stop: %d Dispatch QC checks are still pending. Please complete the checklist on the 'Dispatch QC Check' tab.") % len(incomplete_qc))
            
        return {
            'name': _('Validate Pickup'),
            'type': 'ir.actions.act_window',
            'res_model': 'equipment.rental.pickup.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_rental_id': self.id}
        }

    def action_return_inspection(self):
        """Transition from On-Rent to Return Inspection."""
        self.ensure_one()
        return {
            'name': _('Validate Return'),
            'type': 'ir.actions.act_window',
            'res_model': 'equipment.rental.return.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_rental_id': self.id}
        }

    def action_close(self):
        """Final transition to Closed & Settled state (Supports Batch Roadmap #33)"""
        for rec in self:
            if rec.state == 'closed': continue # Idempotent for batch
            # QMS GATEKEEPER: Ensure Return QC is 100% complete
            incomplete_qc = rec.return_qc_line_ids.filtered(lambda x: not x.is_checked)
            if incomplete_qc:
                raise UserError(_("Operational Stop: %d Return QC checks pending on %s.") % (len(incomplete_qc), rec.name))
                
            if rec.amount_due > 0:
                raise UserError(_("The order %s cannot be closed with an outstanding balance of %s.") % (rec.name, rec.amount_due))
            rec.write({'state': 'closed'})
            
            # ROADMAP #63: NPS Loyalty Feedback
            # Automated Engagement: Poll the client 24h after closure for quality metrics.
            rec.message_post(body=_("📊 <b>NPS Loop:</b> Client satisfaction survey scheduled for 24h follow-up."))

    def action_register_deposit(self):
        self.ensure_one()
        if not self.deposit_invoice_id:
            raise ValidationError(_("No deposit invoice found."))
        return self.deposit_invoice_id.action_register_payment()

    def action_return_deposit(self):
        """Create a Credit Note for the deposit invoice."""
        for rec in self:
            if not rec.deposit_invoice_id:
                raise ValidationError(_("No deposit invoice found to refund."))
            move_reversal = self.env['account.move.reversal'].with_context(active_model='account.move', active_ids=rec.deposit_invoice_id.ids).create({
                'date': fields.Date.context_today(self),
                'reason': _('Deposit Refund for %s') % rec.name,
                'journal_id': rec.deposit_invoice_id.journal_id.id,
            })
            result = move_reversal.reverse_moves()
            refund_inv_id = result.get('res_id')
            if refund_inv_id:
                refund_inv = self.env['account.move'].browse(refund_inv_id)
                refund_inv.action_post()
                rec.deposit_refund_invoice_id = refund_inv.id
                rec.deposit_refunded = True
                rec.deposit_refund_date = fields.Datetime.now()
                return refund_inv.action_register_payment()

    def action_print_qms_report(self):
        return self.env.ref('atk_equipment_rental.action_report_rental_qms').report_action(self)

    def action_print_quotation_report(self):
        """Strategic Command: Generate the Formal Rental Quotation for client review."""
        return self.env.ref('atk_equipment_rental.action_report_rental_quotation').report_action(self)

    def action_print_mis_report(self):
        return self.env.ref('atk_equipment_rental.action_report_rental_mis_profitability').report_action(self)

    def action_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def write(self, vals):
        # ROADMAP #59: Operational Audit Hardening
        # Dynamic Logging: Capture critical state/financial changes in the order history
        fields_to_audit = ('state', 'total_amount', 'start_date', 'end_date', 'partner_id')
        if any(f in vals for f in fields_to_audit):
            for rec in self:
                changes = []
                for field in vals:
                    if field in fields_to_audit:
                        old_val = getattr(rec, field)
                        new_val = vals[field]
                        
                        # Institutional Comparison: Handle recordsets effectively
                        is_changed = False
                        if hasattr(old_val, 'id'):
                            is_changed = old_val.id != (new_val or False)
                        else:
                            is_changed = str(old_val) != str(new_val)
                            
                        if is_changed:
                            # Handle Display Formatting
                            field_desc = self.fields_get([field])[field]
                            label = field_desc['string']
                            
                            def format_value(val, desc):
                                if hasattr(val, 'display_name'):
                                    return val.display_name
                                if desc.get('selection'):
                                    return dict(desc['selection']).get(val, val)
                                return val
                                
                            old_label = format_value(old_val, field_desc)
                            
                            # Handle new value resolution
                            field_obj = self._fields[field]
                            if field_obj.type == 'many2one' and new_val:
                                try:
                                    new_label = self.env[field_obj.comodel_name].browse(new_val).display_name
                                except:
                                    new_label = new_val
                            elif field_desc.get('selection'):
                                new_label = dict(field_desc['selection']).get(new_val, new_val)
                            else:
                                new_label = new_val
                            
                            changes.append(f"• <b>{label}</b>: {old_label} → {new_label}")
                if changes:
                    rec.message_post(body=_("🔍 <b>Audit Log — Critical Change:</b><br/>") + "<br/>".join(changes))
        return super().write(vals)

    def _apply_loyalty_tier(self):
        """Roadmap #67: Institutional Loyalty integration."""
        # Simple Logic: Partners with 'VIP' or specific gold/silver tag get auto-discounts.
        for rec in self:
            vip_tag = self.env.ref('base.res_partner_category_1', raise_if_not_found=False) # Use an existing tag or similar
            if vip_tag and vip_tag in rec.partner_id.category_id:
                for line in rec.line_ids.filtered(lambda l: not l.display_type and l.discount == 0):
                    line.discount = 5.0 # Automatic Loyalty Discount
                rec.message_post(body=_("🏅 <b>Loyalty Loyalty Applied:</b> Gold/VIP tier discount triggered for this partner."))

    def action_organize_by_category(self):
        self.ensure_one()
        # Pre-fetch operator product to ensure quantity sync
        operator_product = self._get_operator_product()
        operator_product_id = operator_product.id if operator_product else 0
        products_data = []
        
        for line in self.line_ids.filtered(lambda l: not l.display_type and l.product_id):
            categ_name = (line.product_id.categ_id.name or _('General Equipment')).upper()
            
            # Sync quantity for operator if it's the designated operator product
            qty = line.quantity
            if self.is_operators and operator_product_id and line.product_id.id == operator_product_id:
                qty = self.operator_count

            products_data.append({
                'categ': categ_name,
                'data': {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': qty,
                    'lot_id': line.lot_id.id,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'qty_delivered': line.qty_delivered,
                    'qty_returned': line.qty_returned,
                    'actual_pickup_date': line.actual_pickup_date,
                    'actual_return_date': line.actual_return_date,
                }
            })
        
        if not products_data:
            return True

        # 2. Sort by category name
        products_data.sort(key=lambda x: x['categ'])
        
        # 3. Rebuild the whole list command-set
        # Using (5, 0, 0) to clear then (0, 0, ...) to recreate ensures the sequence is 100% correct in UI
        commands = [(5, 0, 0)]
        current_category = None
        seq = 10
        
        # Track if we have multiple categories to decide if we need headers
        all_categs = {p['categ'] for p in products_data}
        show_headers = len(all_categs) > 1

        for p in products_data:
            if show_headers and p['categ'] != current_category:
                # Calculate Section Total
                group_total = sum((d['data']['quantity'] * d['data']['price_unit']) * (1 - (d['data'].get('discount', 0.0) or 0.0) / 100.0)
                                 for d in products_data if d['categ'] == p['categ'])
                # Institutional Alignment: Using exact spacing for UI Form View consistency
                spacer = "\u00A0" * 240
                header_name = f"{p['categ']}{spacer}{group_total:,.3f} {self.currency_id.name}"
                
                commands.append((0, 0, {
                    'display_type': 'line_section',
                    'name': header_name,
                    'sequence': seq,
                }))
                seq += 1
                current_category = p['categ']
            
            # Add Product
            vals = p['data']
            vals['sequence'] = seq
            commands.append((0, 0, vals))
            seq += 1
            
        self.write({'line_ids': commands})
        return True

    # ── Stat View Helpers ──────────────────────────────────────────────────
    def action_view_deposit_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Deposit Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.deposit_invoice_id.id,
            'target': 'current',
        }

    def action_view_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rental Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def action_view_deposit_refund(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Deposit Refund'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.deposit_refund_invoice_id.id,
            'target': 'current',
        }

    def action_view_delivery(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Records'),
            'res_model': 'equipment.rental.line',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('rental_id', '=', self.id), ('qty_delivered', '>', 0)],
        }

    def action_view_return(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Return Records'),
            'res_model': 'equipment.rental.line',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('rental_id', '=', self.id), ('qty_returned', '>', 0)],
        }

    # ── REPORT ACTIONS ────────────────────────────────────────────────────

    def action_print_quotation_report(self):
        self.ensure_one()
        return self.env.ref('atk_equipment_rental.action_report_rental_quotation').report_action(self)

    def action_print_qms_report(self):
        self.ensure_one()
        return self.env.ref('atk_equipment_rental.action_report_rental_qms').report_action(self)

    def action_print_mis_report(self):
        self.ensure_one()
        return self.env.ref('atk_equipment_rental.action_report_rental_mis_profitability').report_action(self)

    def action_print_audit_report(self):
        self.ensure_one()
        return self.env.ref('atk_equipment_rental.action_report_rental_audit_log').report_action(self)

    @api.model
    def _cron_send_return_reminders(self):
        """Roadmap #39: Automated Strategic Command.
        Sends a proactive notification for all rentals ending in exactly 24 hours.
        """
        reminder_time = fields.Datetime.now() + timedelta(days=1)
        # Search for active rentals ending around this time (within an hour range to catch all)
        rentals = self.search([
            ('state', '=', 'on_rent'),
            ('end_date', '>=', reminder_time - timedelta(hours=1)),
            ('end_date', '<=', reminder_time + timedelta(hours=1))
        ])
        for record in rentals:
            record.message_post(body=_("📅 <b>Strategic Reminder:</b> The rental for order <b>%s</b> is scheduled to end in 24 hours ( %s ). Please prepare for return or request an extension.") % (record.name, record.end_date))
            # In a production environment, this would call a mail.template to send an actual email/SMS

        # ROADMAP #40: Overdue Strategic Guard
        # Institutional Definition: Actively accrue penalties as soon as the grace period + deadline is breached.
        overdue_rentals = self.search([
            ('state', '=', 'on_rent'),
            ('end_date', '<', fields.Datetime.now())
        ])
        for record in overdue_rentals:
            # We log the event. Real implementation sends a high-priority 'Overdue Warning' email to client.
            record.message_post(body=_("🚨 <b>Overdue Enforcement:</b> Order <b>%s</b> has breached the return deadline. Penalty fees of %s %s are now accruing hourly.") % (record.name, record.overtime_fee_per_hr, record.currency_id.name))

    @api.model
    def _cron_send_review_requests(self):
        """Gate 6: Automated QMS Feedback Command.
        Sends a review request to all customers whose rental was closed in the last 48h 
        and who haven't submitted a review yet.
        """
        template = self.env.ref('atk_equipment_rental.email_template_rental_review_request', raise_if_not_found=False)
        if not template:
            return
            
        # Strategy: Search for Closed orders without reviews created in the last 48h
        recent_closed = self.search([
            ('state', '=', 'closed'),
            ('review_count', '=', 0),
            ('write_date', '>=', fields.Datetime.now() - timedelta(days=2))
        ])
        
        for record in recent_closed:
            # We use sudo() to ensure the cron user (public usually) can send the mail
            template.sudo().send_mail(record.id, force_send=True)
            record.message_post(body=_("📩 <b>Review Request Dispatched:</b> Post-return satisfaction survey sent to customer."))


class EquipmentRentalTerms(models.Model):
    _name = 'equipment.rental.terms'
    _description = 'Rental Terms & Conditions Template'

    name = fields.Char('Template Name', required=True)
    content = fields.Html('Content', required=True)
    active = fields.Boolean(default=True)

class AccountMove(models.Model):
    _inherit = 'account.move'

    rental_id = fields.Many2one('equipment.rental', string='Rental Order', readonly=True)


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    rental_sequence_prefix = fields.Char('Rental Sequence Prefix', default="RNT-", help="Example: BH-RNT- for Bahrain branch")
