# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleRental(WebsiteSale):

    # we removed the checkout override to prevent AttributeError on super().checkout
    # the redirect from /rental/submit will call the standard Odoo /shop/checkout directly.


    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment(self, **post):
        # We use a direct method to get the order to ensure compatibility with Odoo 19 controller refactors
        order_id = request.session.get('sale_order_id')
        order = request.env['sale.order'].sudo().browse(order_id) if order_id else None
        if order and request.session.get('rental_start_date'):
            # Auto-link the order to the rental dates if they were lost/needed
            order.sudo().write({
                'note': "Rental Period: %s to %s" % (request.session.get('rental_start_date'), request.session.get('rental_end_date'))
            })
        return super(WebsiteSaleRental, self).shop_payment(**post)
