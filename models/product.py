# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_rentable = fields.Boolean('Is Rentable', default=False, tracking=True, help="Tick this for professional equipment that can be booked online via the nl3ab portal.")

