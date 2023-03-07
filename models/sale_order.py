# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(string='Payment Count', compute='_get_payments', readonly=True)
    add_payment =fields.Boolean(string="Agregar Pagos", compute='_compute_add_payment')

    @api.one
    def _compute_add_payment(self):
        for rec in self:
            add_payment = True
            if rec.state in ['cancel']:
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
                        if invoice.state == 'open':
                            total_residual_invoice += invoice.residual
                            total_invoiced += invoice.amount_total
                        if invoice.state == 'paid':
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

    def _get_payments(self):
        for rec in self:
            count_payment = self.env['account.payment'].search([('sale_id','=',rec.id)])
            rec.payment_count = len(count_payment)
        return
    
    @api.multi
    def action_view_payments(self):
        action = self.env.ref('account.view_account_payment_tree').read()[0]
        payments = self.env['account.payment'].search([('sale_id','=',self.id)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', payments.ids]],
            "name": "Ventas",
        }
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def invoice_line_create_vals(self, invoice_id, qty):
        res = super(SaleOrderLine, self).invoice_line_create_vals(invoice_id, qty)
        invoice = self.env['account.invoice'].search([('id','=',res[0]['invoice_id'])])
        added_sale = True
        for sale in invoice.sale_ids:
            if sale == self.order_id:
                added_sale = False
        if added_sale == True:
            invoice.write({'sale_ids': [(4, self.order_id.id)]})
        return res
        
    