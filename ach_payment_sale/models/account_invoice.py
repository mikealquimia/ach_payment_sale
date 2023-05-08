# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many('sale.order',string='Sales')
    add_payment_sale = fields.Boolean(string="Add Payment", compute="_compute_add_payment_sale")

    def mapping_sale_id(self):
        sql = "select ail.invoice_id as invoice, sol.order_id as sale "
        sql += "from account_invoice_line ail "
        sql += "inner join sale_order_line_invoice_rel solir "
        sql += "on solir.invoice_line_id = ail.id "
        sql += "inner join sale_order_line sol "
        sql += "on sol.id = solir.order_line_id "
        self.env.cr.execute(sql)
        aisor = self.env.cr.dictfetchall()
        for rel in aisor:
            sql = "INSERT INTO account_invoice_sale_order_rel (account_invoice_id, sale_order_id) "
            sql += "VALUES (%s, %s) ON CONFLICT DO NOTHING;"
            params = (int(rel['invoice']),int(rel['sale']))
            self.env.cr.execute(sql, params)
    @api.one
    def _compute_add_payment_sale(self):
        for rec in self:
            if rec.state == 'open':
                sale_ids = []
                for sale in rec.sale_ids:
                    sale_ids.append(sale.id)
                payments = self.env['account.payment'].search([('sale_id','in',sale_ids),('state_sale_invoice','=','no_add')])
                if len(payments) > 0:
                    self.add_payment_sale = True
                else:
                    self.add_payment_sale = False
            else:
                self.add_payment_sale = False
    @api.multi
    def action_add_payment_sale(self):
        for rec in self:
            sale_ids = []
            for sale in rec.sale_ids:
                sale_ids.append(sale.id)
            payment_ids = self.env['account.payment'].search([('sale_id','in',sale_ids),('state_sale_invoice','=','no_add')])
            lines = []
            for payment in payment_ids:
                for payment_line in payment.move_line_ids:
                    if payment_line.account_id.reconcile:
                        if payment_line.reconciled == False:
                            lines.append(payment_line)
                            rec.assign_outstanding_credit(payment_line.id)
                        else:
                            raise UserError(_('The Payment: %s is reconciled' % (payment_line.account_id.name)))
                payment.write({'state_sale_invoice':'add'})