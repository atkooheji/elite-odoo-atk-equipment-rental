# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class EquipmentRentalDashboard(models.Model):
    _name = 'equipment.rental.dashboard'
    _description = 'Equipment Rental Dashboard Controller'

    @api.model
    def get_dashboard_data(self, filters=None):
        if not filters:
            filters = {}
        
        # Security & Company Context
        company_ids = self.env.companies.ids
        today = fields.Date.context_today(self)

        # 1. Pipeline & Logistics (Today's Operations)
        # Count drafts/applications
        pipeline_count = self.env['equipment.rental'].search_count([
            ('state', '=', 'draft'),
            ('company_id', 'in', company_ids)
        ])
        
        # Today's Dispatches (Approved orders starting today)
        dispatch_today = self.env['equipment.rental'].search_count([
            ('state', '=', 'approved'),
            ('start_date', '>=', today),
            ('start_date', '<', today + __import__('datetime').timedelta(days=1)),
            ('company_id', 'in', company_ids)
        ])

        # Today's Returns (On-Rent orders expected back today)
        return_today = self.env['equipment.rental'].search_count([
            ('state', '=', 'on_rent'),
            ('end_date', '>=', today),
            ('end_date', '<', today + __import__('datetime').timedelta(days=1)),
            ('company_id', 'in', company_ids)
        ])
        
        # ROADMAP #50: Revenue Leakage Detection
        # Definition: Orders stuck in 'Return Inspection' for > 24 hours
        from datetime import timedelta
        leakage_threshold = fields.Datetime.now() - timedelta(days=1)
        stuck_in_inspection = self.env['equipment.rental'].search_count([
            ('state', '=', 'return_inspection'),
            ('write_date', '<', leakage_threshold),
            ('company_id', 'in', company_ids)
        ])

        # NEW: Critical Overdue Operations (MIS Exception)
        overdue_threshold = today - __import__('datetime').timedelta(days=1)
        critical_overdue = self.env['equipment.rental'].search_count([
            ('state', '=', 'on_rent'),
            ('end_date', '<', overdue_threshold),
            ('company_id', 'in', company_ids)
        ])

        # 2. Inventory & Fleet Status (Product based)
        storable_products = self.env['product.product'].search([('type', '!=', 'service')])
        total_assets = sum(storable_products.mapped('qty_available'))
        
        rented_lines = self.env['equipment.rental.line'].search([
            ('rental_id.state', 'in', ['on_rent', 'return_inspection'])
        ])
        rented_assets = sum(rented_lines.mapped('quantity'))
        
        available_assets = max(0, total_assets - rented_assets)
        utilization_rate = (rented_assets / total_assets * 100) if total_assets > 0 else 0

        # NEW: Quarantine Assets (Maintenance/Damaged)
        quarantine_assets = self.env['product.product'].search_count([
            ('type', '!=', 'service'),
            ('qty_available', '<=', 0),
            ('active', '=', True)
        ]) # Note: This is a placeholder logic depending on how maintenance is tracked

        # 3. Financials (MIS Profitability)
        revenue_query = """
            SELECT SUM(total_amount) as revenue, SUM(net_profit) as profit
            FROM equipment_rental 
            WHERE state IN ('on_rent', 'return_inspection', 'closed')
            AND company_id = ANY(%s)
        """
        self.env.cr.execute(revenue_query, [company_ids])
        fin_res = self.env.cr.dictfetchone()
        mtd_revenue = fin_res.get('revenue', 0.0) or 0.0
        mtd_profit = fin_res.get('profit', 0.0) or 0.0

        # 4. QMS SLA Performance
        # Pickup SLA
        pickup_total = self.env['equipment.rental'].search_count([
            ('pickup_actual_date', '!=', False),
            ('company_id', 'in', company_ids)
        ])
        pickup_ontime = self.env['equipment.rental'].search_count([
            ('pickup_sla_status', '=', 'on_time'),
            ('company_id', 'in', company_ids)
        ])
        pickup_sla_pc = (pickup_ontime / pickup_total * 100) if pickup_total > 0 else 100

        # Return SLA
        return_total = self.env['equipment.rental'].search_count([
            ('return_actual_date', '!=', False),
            ('company_id', 'in', company_ids)
        ])
        return_ontime = self.env['equipment.rental'].search_count([
            ('return_sla_status', '=', 'on_time'),
            ('company_id', 'in', company_ids)
        ])
        return_sla_pc = (return_ontime / return_total * 100) if return_total > 0 else 100

        # 5. NEW: Staff & Resource Performance (MIS)
        staff_costs = self.env['equipment.rental.expense'].search([
            ('rental_id.state', 'in', ['on_rent', 'return_inspection', 'closed'])
        ])
        total_staff_cost = sum(staff_costs.mapped('amount'))
        operator_count = len(staff_costs.mapped('product_id'))
        efficiency = (mtd_revenue / total_staff_cost) if total_staff_cost > 0 else 0

        # Stage counts for pipeline flow visualization
        stage_counts = {}
        for state in ['draft', 'approved', 'on_rent', 'return_inspection']:
            stage_counts[state] = self.env['equipment.rental'].search_count([
                ('state', '=', state),
                ('company_id', 'in', company_ids)
            ])
        stage_counts['closed_today'] = self.env['equipment.rental'].search_count([
            ('state', '=', 'closed'),
            ('write_date', '>=', fields.Datetime.now().replace(hour=0, minute=0, second=0)),
            ('company_id', 'in', company_ids)
        ])

        return {
            'labels': {
                'project': 'Equipment Fleet Intelligence',
                'date': today.strftime("%d %b %Y")
            },
            'pipeline': {
                'total_pending': pipeline_count,
                'dispatch_today': dispatch_today,
                'return_today': return_today,
                'critical_overdue': critical_overdue,
                'stage_counts': stage_counts,
            },
            'inventory': {
                'total': total_assets,
                'available': available_assets,
                'rented': rented_assets,
                'utilization_rate': utilization_rate,
                'quarantine': quarantine_assets
            },
            'financial': {
                'revenue_mtd': mtd_revenue,
                'profit_mtd': mtd_profit,
                'total_staff_cost': total_staff_cost,
                'currency_symbol': self.env.company.currency_id.symbol or 'BHD'
            },
            'staff': {
                'operator_count': operator_count,
                'efficiency_index': efficiency,
                'total_cost': total_staff_cost,
                'revenue_leakage_count': stuck_in_inspection
            },
            'qms': {
                'pickup_sla': pickup_sla_pc,
                'return_sla': return_sla_pc,
                'total_pickup_count': pickup_total,
                'total_return_count': return_total
            },
            'fleet_photos': self._get_fleet_photos()
        }

    def _get_fleet_photos(self):
        """Roadmap #8: Technical implementation of visual fleet monitoring."""
        # Institutional Alignment: Fetch products with images that are actively in the rental fleet
        products = self.env['product.product'].search([
            ('type', '!=', 'service'),
            ('image_128', '!=', False)
        ], limit=8)
        
        photos = []
        for p in products:
            photos.append({
                'id': p.id,
                'name': p.display_name,
                'image_url': f'/web/image/product.product/{p.id}/image_128',
                'category': p.categ_id.name or 'General'
            })
        return photos
