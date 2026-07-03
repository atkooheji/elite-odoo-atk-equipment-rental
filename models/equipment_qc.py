# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class EquipmentQcTemplate(models.Model):
    _name = 'equipment.qc.template'
    _description = 'Equipment QC Checklist Template'
    _order = 'sequence, id'

    name = fields.Char('Checklist Item', required=True)
    sequence = fields.Integer('Sequence', default=10)
    stage_type = fields.Selection([
        ('dispatch', 'Dispatch QC'),
        ('return', 'Return QC')
    ], string='Stage Type', required=True, default='dispatch', help="Determines which phase of the rental order this rule applies to.")
    active = fields.Boolean('Active', default=True)


class EquipmentRentalQcLine(models.Model):
    _name = 'equipment.rental.qc.line'
    _description = 'Rental QC Checklist Line'
    _order = 'sequence, id'

    rental_id = fields.Many2one('equipment.rental', string='Rental', required=True, ondelete='cascade')
    template_id = fields.Many2one('equipment.qc.template', string='Template Item', required=True, ondelete='restrict')
    name = fields.Char(related='template_id.name', string='Checklist Item', store=True)
    stage_type = fields.Selection(related='template_id.stage_type', store=True)
    sequence = fields.Integer(related='template_id.sequence', store=True)
    
    is_checked = fields.Boolean('Checked?', default=False)
    check_date = fields.Datetime('Time Checked', readonly=True)
    check_user_id = fields.Many2one('res.users', 'Checked By', readonly=True)

    @api.onchange('is_checked')
    def _onchange_is_checked(self):
        if self.is_checked:
            if not self.check_date:
                self.check_date = fields.Datetime.now()
                self.check_user_id = self.env.user
        else:
            self.check_date = False
            self.check_user_id = False

    def write(self, vals):
        if 'is_checked' in vals:
            if vals['is_checked']:
                vals['check_date'] = fields.Datetime.now()
                vals['check_user_id'] = self.env.user.id
            else:
                vals['check_date'] = False
                vals['check_user_id'] = False
        return super().write(vals)
