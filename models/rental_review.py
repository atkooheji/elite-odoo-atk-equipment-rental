# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RentalReview(models.Model):
    _name = 'rental.review'
    _inherit = ['mail.thread']
    _description = 'Customer Rental Review'

    _order = 'date desc'

    rental_id = fields.Many2one('equipment.rental', string='Rental Order', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Customer', related='rental_id.partner_id', store=True)
    date = fields.Date('Review Date', default=fields.Date.context_today)
    
    rating = fields.Integer('Rating (1-5)', default=5, required=True)
    comment = fields.Text('Feedback')
    
    is_published = fields.Boolean('Is Published', default=False, tracking=True, 
                                  help="Set to true to show this review on the website.")
    
    @api.constrains('rating')
    def _check_rating(self):
        for rec in self:
            if rec.rating < 1 or rec.rating > 5:
                raise ValidationError(_("Review Validation: Rating must be an integer between 1 and 5."))

    @api.model_create_multi
    def create(self, vals_list):
        reviews = super().create(vals_list)
        for review in reviews:
            review.rental_id.message_post(body=_("⭐ <b>New Review Received:</b> Rating: %s/5<br/>Feedback: %s") % (review.rating, review.comment))
        return reviews
