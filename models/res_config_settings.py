# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rental_duration_default = fields.Float(
        string="Default Rental Duration (Hrs)", 
        config_parameter='atk_equipment_rental.rental_duration_default', 
        default=24.0
    )
    equipment_overtime_rate = fields.Float(
        string="Equipment Overtime Rate/HR", 
        config_parameter='atk_equipment_rental.equipment_overtime_rate', 
        default=10.0
    )
    operator_overtime_rate = fields.Float(
        string="Operator Overtime Rate/HR", 
        config_parameter='atk_equipment_rental.operator_overtime_rate', 
        default=5.0
    )
    rental_deposit_amount = fields.Float(
        string="Default Deposit (BD)", 
        config_parameter='atk_equipment_rental.rental_deposit_amount', 
        default=30.0
    )
    promo_product_id = fields.Many2one(
        'product.product',
        string="Free Bonus Product",
        config_parameter='atk_equipment_rental.promo_product_id'
    )
    promo_threshold_qty = fields.Integer(
        string="Free Bonus Threshold",
        config_parameter='atk_equipment_rental.promo_threshold_qty',
        default=5
    )
    pickup_sla_hours = fields.Float(
        string="Pickup SLA Window (Hrs)",
        config_parameter='atk_equipment_rental.pickup_sla_hours',
        default=2.0
    )
    return_sla_hours = fields.Float(
        string="Return SLA Window (Hrs)",
        config_parameter='atk_equipment_rental.return_sla_hours',
        default=2.0
    )
    skip_id_check = fields.Boolean(
        string="Default Skip KYC?",
        config_parameter='atk_equipment_rental.skip_id_check',
        default=False
    )
    operator_product_name = fields.Char(
        string="Operator Product Name",
        config_parameter='atk_equipment_rental.operator_product_name',
        default="Operators"
    )
    rental_sequence_prefix = fields.Char(
        related='company_id.rental_sequence_prefix', 
        string="Rental Order Prefix", 
        readonly=False
    )
