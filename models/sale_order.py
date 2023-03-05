# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(string='Payment Count', compute='_get_payments', readonly=True)

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
        
    