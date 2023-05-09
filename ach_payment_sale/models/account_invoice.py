# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_ids = fields.Many2many('sale.order',string='Sales')
    add_payment_sale = fields.Boolean(string="Add Payment", compute="_compute_add_payment_sale")

    def mapping_sale_id(self):
        sql = """
select aml.move_id as invoice, sol.order_id as sale 
from account_move_line aml 
inner join sale_order_line_invoice_rel solir 
on solir.invoice_line_id = aml.id 
inner join sale_order_line sol 
on sol.id = solir.order_line_id """
        self.env.cr.execute(sql)
        aisor = self.env.cr.dictfetchall()
        for rel in aisor:
            sql = "INSERT INTO account_move_sale_order_rel (account_move_id, sale_order_id) "
            sql += "VALUES (%s, %s) ON CONFLICT DO NOTHING;"
            params = (int(rel['invoice']),int(rel['sale']))
            self.env.cr.execute(sql, params)

    def _compute_add_payment_sale(self):
        for rec in self:
            if rec.state == 'posted':
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

    def action_add_payment_sale(self):
        for rec in self:
            sale_ids = []
            for sale in rec.sale_ids:
                sale_ids.append(sale.id)
            payment_ids = self.env['account.payment'].search([('sale_id','in',sale_ids),('state_sale_invoice','=','no_add')])
            lines = []
            for payment in payment_ids:
                for payment_line in payment.move_id.line_ids:
                    if payment_line.account_id.reconcile:
                        if payment_line.reconciled == False:
                            lines.append(payment_line)
                            rec.js_assign_outstanding_line(payment_line.id)
                        else:
                            raise UserError(_('The Payment: %s is reconciled' % (payment_line.account_id.name)))
                payment.write({'state_sale_invoice':'add'})