/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class EquipmentRentalDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            data: {},
            loading: true,
            activeTab: 'logistics',
            filters: {
                period: 'this_month'
            }
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "equipment.rental.dashboard",
                "get_dashboard_data",
                [this.state.filters]
            );
            this.state.data = data;
        } catch (error) {
            console.error("Dashboard Loading Error:", error);
        } finally {
            this.state.loading = false;
        }
    }

    setTab(tab) {
        this.state.activeTab = tab;
    }

    formatCurrency(value) {
        if (value === undefined || value === null) return "0.00";
        const symbol = this.state.data?.financial?.currency_symbol || '$';
        return `${symbol}${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    
    formatPercentage(value) {
         if (value === undefined || value === null) return "0%";
         return `${value.toFixed(1)}%`;
    }

    onClickPipeline() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "equipment.rental",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['state', '=', 'draft']],
            name: "KYC Pending Pipeline"
        });
    }

    onClickDispatchToday() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "equipment.rental",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['state', '=', 'approved']],
            name: "Ready for Dispatch"
        });
    }

    onClickInventory() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "product.product",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['type', '!=', 'service']],
            name: "Fleet & Equipment Inventory"
        });
    }

    onClickOverdue() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "equipment.rental",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['state', '=', 'on_rent'], ['end_date', '<', new Date().toISOString().split('T')[0]]],
            name: "CRITICAL OVERDUE RETURNS"
        });
    }

    onClickFinancials() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "equipment.rental",
            view_mode: "pivot,graph,list",
            views: [[false, "pivot"], [false, "graph"], [false, "list"]],
            domain: [['state', 'in', ['on_rent', 'closed']]],
            name: "Strategic Profitability Analytics"
        });
    }

    onClickStaff() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "equipment.rental.expense",
            view_mode: "list,pivot",
            views: [[false, "list"], [false, "pivot"]],
            name: "Staff & Resource Burn Logs"
        });
    }
}

EquipmentRentalDashboard.template = "atk_equipment_rental.Dashboard";
registry.category("actions").add("atk_equipment_rental.Dashboard", EquipmentRentalDashboard);
