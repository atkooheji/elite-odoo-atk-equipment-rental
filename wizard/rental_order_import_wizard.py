# -*- coding: utf-8 -*-
import base64
import json
import logging
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class RentalOrderImportWizard(models.TransientModel):
    _name = 'rental.order.import.wizard'
    _description = 'AI Rental Order Import Wizard'

    import_file = fields.Binary(string='Order Image (Handwritten)', required=True)
    file_name = fields.Char(string='Filename')
    
    ai_raw_response = fields.Text(string='AI Raw Response', readonly=True)
    
    def action_import_ai(self):
        self.ensure_one()
        if not self.import_file:
            raise UserError(_("Please upload an image of the handwritten order."))

        # 1. Retrieve Gemini API Key
        params = self.env['ir.config_parameter'].sudo()
        api_key = params.get_param('hotel.ai.gemini_key')
        if not api_key:
            raise UserError(_("Gemini API Key not found. Please configure it in Settings > Hotel AI."))

        # 2. Call Gemini Vision
        if not genai:
             raise UserError(_("The 'google-genai' library is not installed on the server."))

        try:
            client = genai.Client(api_key=api_key)
            
            prompt = """
            Analyze this handwritten rental order. 
            Extract the data into a strictly valid JSON format with these keys:
            - customer_name: String
            - customer_phone: String (numeric only if possible)
            - customer_email: String
            - pickup_date: String (format YYYY-MM-DD HH:MM:SS, if only date is given use 19:00:00 as default)
            - return_date: String (format YYYY-MM-DD HH:MM:SS, if only date is given use 00:00:00 next day as default)
            - location: String
            - items: list of objects {name: String, qty: Float, price: Float}
            - operators_count: Integer (look for 'operators' or 'ops')
            - insurance_amount: Float (look for 'Ins')
            - deposit_amount: Float (look for 'Dp')
            - total_amount: Float
            
            Rules:
            1. If a year is not mentioned, use 2026.
            2. For time like '7pm - 12am', 7pm is 19:00:00 and 12am is 00:00:00 of the NEXT day.
            3. Return ONLY the JSON object, no markdown, no conversational text.
            """

            # Prepare image for Gemini
            image_data = base64.b64decode(self.import_file)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
                ]
            )

            if not response or not response.text:
                raise UserError(_("AI failed to return a response. Please try a clearer photo."))

            # 3. Parse JSON
            clean_json = response.text.strip().replace('```json', '').replace('```', '')
            data = json.loads(clean_json)
            self.ai_raw_response = json.dumps(data, indent=4)

            # 4. Process Data & Create Order
            return self._create_rental_order(data)

        except Exception as e:
            _logger.error("Rental AI Import Error: %s", str(e))
            raise UserError(_("AI Processing Failed: %s") % str(e))

    def _create_rental_order(self, data):
        """ Institutional Logic: Map AI JSON to Odoo Equipment Rental records. """
        Partner = self.env['res.partner']
        Product = self.env['product.product']
        Rental = self.env['equipment.rental']

        # 4.1. Resolve Partner
        partner = Partner.search([
            '|', '|',
            ('email', '=ilike', data.get('customer_email')),
            ('phone', '=', data.get('customer_phone')),
            ('mobile', '=', data.get('customer_phone')),
        ], limit=1)

        if not partner and data.get('customer_name'):
            partner = Partner.create({
                'name': data.get('customer_name'),
                'email': data.get('customer_email'),
                'phone': data.get('customer_phone'),
                'customer_rank': 1,
            })

        if not partner:
            raise UserError(_("Could not determine or create a customer from the AI response."))

        # 4.2. Prepare Rental Header
        rental_vals = {
            'partner_id': partner.id,
            'start_date': data.get('pickup_date'),
            'end_date': data.get('return_date'),
            'deposit_amount': data.get('deposit_amount', 0.0),
            'is_operators': bool(data.get('operators_count', 0) > 0),
            'operator_count': data.get('operators_count', 0),
        }

        # 4.3. Process Items
        line_ids = []
        for item in data.get('items', []):
            # Try to match product by name
            product = Product.search([
                ('name', 'ilike', item.get('name')),
                ('sale_ok', '=', True)
            ], limit=1)
            
            if product:
                line_ids.append((0, 0, {
                    'product_id': product.id,
                    'quantity': item.get('qty', 1.0),
                    'price_unit': item.get('price', product.list_price),
                    'name': item.get('name'),
                }))
            else:
                # Optional: Add as a generic service if not found? 
                # For now, we'll skip or use a placeholder
                _logger.warning("Product not found: %s", item.get('name'))

        # Add Insurance if present
        if data.get('insurance_amount', 0) > 0:
            ins_product = Product.search([('name', 'ilike', 'Insurance')], limit=1)
            if ins_product:
                line_ids.append((0, 0, {
                    'product_id': ins_product.id,
                    'quantity': 1.0,
                    'price_unit': data.get('insurance_amount'),
                    'name': _('Insurance (Parsed from Image)'),
                }))

        if line_ids:
            rental_vals['line_ids'] = line_ids

        # 5. Create and Return
        rental_order = Rental.create(rental_vals)
        
        # Attach the original image for reference
        self.env['ir.attachment'].create({
            'name': _('Original Source — %s') % self.file_name,
            'datas': self.import_file,
            'res_model': 'equipment.rental',
            'res_id': rental_order.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Rental Order'),
            'res_model': 'equipment.rental',
            'view_mode': 'form',
            'res_id': rental_order.id,
            'target': 'current',
        }
