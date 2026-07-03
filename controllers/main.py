# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request

class RentalWebsiteController(http.Controller):

    @http.route(['/rental/book'], type='http', auth="public", website=True)
    def rental_booking_page(self, **post):
        """Strategic Step 1: Collection of timeline parameters and redirection to the high-performance catalog."""
        Config = request.env['ir.config_parameter'].sudo()
        default_duration = float(Config.get_param('atk_equipment_rental.rental_duration_default', 12.0))
        return request.render('atk_equipment_rental.rental_booking_template', {
            'branding': 'WANNA PLAY ENTERTAINMENT',
            'default_duration': default_duration
        })

    @http.route(['/rental/catalog'], type='http', auth="public", website=True)
    def rental_catalog_page(self, **post):
        """Strategic Step 2: The high-end product selection arena with filtering for Packages vs Single Equipment."""
        # Fix for ISO datetime-local strings (T to space)
        start_date = post.get('start_date', '').replace('T', ' ') or request.session.get('rental_start_date')
        end_date = post.get('end_date', '').replace('T', ' ') or request.session.get('rental_end_date')
        
        # Lock dates in session for Step 2+3 stability
        if post.get('start_date'):
            request.session['rental_start_date'] = start_date
        if post.get('end_date'):
            request.session['rental_end_date'] = end_date

        # Fetch all website-published products that are marked as Rentable
        valid_products = request.env['product.template'].sudo().search([
            ('is_rentable', '=', True),
            ('website_published', '=', True)
        ])
        
        # Categorize by whether they are in a Package category or others
        packages = valid_products.filtered(lambda p: 'Package' in (p.categ_id.name or ''))
        all_singles = valid_products - packages
        
        # Group Single Games by Category
        categories = {}
        for product in all_singles:
            categ_name = product.categ_id.name or 'Games'
            if categ_name not in categories:
                categories[categ_name] = []
            categories[categ_name].append(product)
            
        # Get real cart count from website_sale order (Robust Search fallback)
        order = request.env['sale.order'].sudo().search([
            ('id', '=', request.session.get('sale_order_id')),
            ('state', '=', 'draft')
        ], limit=1)
        cart_count = order.cart_quantity if order else 0
        
        return request.render('atk_equipment_rental.rental_catalog_template', {
            'packages': packages,
            'categories': categories,
            'start_date': start_date,
            'end_date': end_date,
            'cart_count': cart_count
        })

    @http.route(['/rental/submit'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=True)
    def submit_rental_request(self, **post):
        """Institutional Command: Conclude the digital booking lifecycle and seed the formal rental draft."""
        partner = request.env.user.partner_id
        if request.env.user._is_public():
            return request.redirect('/web/signup?redirect=/rental/catalog')
            
        start_date = request.session.get('rental_start_date')
        end_date = request.session.get('rental_end_date')
        cart = request.session.get('rental_cart', [])
        
        if not cart:
            return request.redirect('/rental/catalog')

        line_ids = []
        for item in cart:
            product = request.env['product.product'].sudo().browse(int(item['product_id']))
            line_ids.append((0, 0, {
                'product_id': product.id,
                'name': product.display_name,
                'quantity': float(item['quantity']),
                'price_unit': product.lst_price,
            }))
            
        vals = {
            'partner_id': partner.id,
            'start_date': start_date,
            'end_date': end_date,
            'is_online_booking': True,
            'line_ids': line_ids
        }
        rental = request.env['equipment.rental'].sudo().create(vals)
        
        # Clear session after successful strategic seeding
        request.session['rental_cart'] = []
        
        # Redirect to Odoo Shop Checkout
        return request.redirect('/shop/checkout?express=1')

    @http.route(['/rental/review/<int:rental_id>/<string:token>'], type='http', auth="public", website=True)
    def rental_review_page(self, rental_id, token, **post):
        """Gate 6: Render the mobile-friendly quality satisfaction review form."""
        rental = request.env['equipment.rental'].sudo().browse(rental_id)
        if not rental.exists() or rental.portal_token != token:
            return request.render('website.404')
            
        return request.render('atk_equipment_rental.rental_review_template', {
            'rental': rental
        })

    @http.route(['/rental/review/submit'], type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def submit_review(self, **post):
        """Gate 6: Persist the customer review and update QMS metrics."""
        rental_id = int(post.get('rental_id'))
        token = post.get('token')
        rental = request.env['equipment.rental'].sudo().browse(rental_id)
        
        if not rental.exists() or rental.portal_token != token:
            return request.render('website.403')

        request.env['rental.review'].sudo().create({
            'rental_id': rental.id,
            'rating': int(post.get('rating')),
            'comment': post.get('comment'),
        })
        return request.render('atk_equipment_rental.review_thanks_template')
