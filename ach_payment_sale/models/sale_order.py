# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(string='Payment Count', compute='_get_payments', readonly=True)
    add_payment =fields.Boolean(string="Add Payment", compute='_compute_add_payment')

    def _compute_add_payment(self):
        for rec in self:
            if rec.company_id.status_for_payment:
                add_payment = True
                if rec.state != rec.company_id.status_for_payment:
                    add_payment = False
                else:
                    if rec.invoice_ids:
                        total_sale = rec.amount_total
                        total_payment = 0
                        total_residual_invoice = 0
                        total_invoiced = 0
                        payments = self.env['account.payment'].search([('sale_id','=',rec.id),('state_sale_invoice','=','no_add')])
                        for payment in payments:
                            total_payment += payment.amount
                        for invoice in rec.invoice_ids:
                            if invoice.state == 'posted':
                                total_residual_invoice += invoice.amount_residual
                                total_invoiced += invoice.amount_total
                        diff_totals = (total_sale-total_invoiced+total_residual_invoice-total_payment)
                        if diff_totals <= 0:
                            add_payment = False
                    else:
                        total_sale = rec.amount_total
                        total_payment = 0
                        payments = self.env['account.payment'].search([('sale_id','=',rec.id),('state_sale_invoice','=','no_add')])
                        for payment in payments:
                            total_payment += payment.amount
                        if (total_sale-total_payment) <= 0:
                            add_payment == False
                if add_payment == True:
                    self.add_payment = True
                if add_payment == False:
                    self.add_payment = False
            else:
                raise ValidationError(_("Set in configuration of your company the state in sale for add payment"))

    def _get_payments(self):
        for rec in self:
            count_payment = self.env['account.payment'].search([('sale_id','=',rec.id)])
            rec.payment_count = len(count_payment)
        return

    def action_view_payments(self):
        action = self.env.ref('account.view_account_payment_tree').read()[0]
        payments = self.env['account.payment'].search([('sale_id','=',self.id)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', payments.ids]],
            "name": "Sales",
        }

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices(grouped,final,date)
        for move in res:
            for rec in self:
                added_sale = True
                for sale in move.sale_ids:
                    if sale == rec.order_id:
                        added_sale = False
                if added_sale == True:
                    move.write({'sale_ids': [(4, rec.id)]})
        return res

    def action_register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'sale.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }