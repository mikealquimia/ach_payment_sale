# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many('sale.order',string='Ventas')
    add_payment_sale = fields.Boolean(string="Agregar Anticipos", compute="_compute_add_payment_sale")

    def mapping_sale_id(self):
        invoices = self.env['account.invoice'].search([('type','in',['out_invoice','out_refund']),('sale_ids','=',False)])
        for invoice in invoices:
            sale_ids = []
            for line in invoice.invoice_line_ids:
                for sale_line in line.sale_line_ids:
                    if sale_line.order_id not in sale_ids:
                        sale_ids.append(sale_line.order_id)
            if len(sale_ids)>0:
                for sale in sale_ids:
                    invoice.write({'sale_ids': [(4, sale.id)]})
        return
    
    @api.one
    def _compute_add_payment_sale(self):
        for rec in self:
            sale_ids = []
            for sale in rec.sale_ids:
                sale_ids.append(sale.id)
            payments = self.env['account.payment'].search([('sale_id','in',sale_ids),('state_sale_invoice','=','no_add')])
            if len(payments) > 0:
                self.add_payment_sale = True
            else:
                self.add_payment_sale = False
    
    def action_add_payment_sale(self):
        print('agregar anticipos')
        return



    
    