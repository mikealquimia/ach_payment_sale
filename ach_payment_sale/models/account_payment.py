# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_id = fields.Many2one('sale.order', string="Sale")
    state_sale_invoice = fields.Selection([('no_add','No Add'),('add','Added'),('cancel','Cancel')], string="State Pay Advance", default='no_add')

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        for rec in self:
            if rec.sale_id:
                rec.ref = rec.sale_id.name
                rec.partner_id = rec.sale_id.partner_id.id
                rec.payment_type = 'inbound'
                rec.partner_type = 'customer'
        return

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val['sale_id']:
                val['partner_type'] = 'customer'
                sale_id = self.env['sale.order'].search([('id','=',val['sale_id'])])
                total_sale = sale_id.amount_total
                total_payment = 0
                total_invoice = 0
                total_residual = 0
                payments = self.env['account.payment'].search([('sale_id','=',sale_id.id),('state_sale_invoice','=','no_add')])
                for payment in payments:
                    total_payment += payment.amount
                if sale_id.invoice_ids:
                    for invoice in sale_id.invoice_ids:
                        if invoice.state == 'posted':
                            total_residual += invoice.amount_residual
                            total_invoice += invoice.amount_total
                dif_amount = (total_sale-total_invoice+total_residual-total_payment)
                if val['amount'] > dif_amount:
                    raise UserError(_("You can only add a down payment of %s to the sale") % (dif_amount))
                else:
                    return super(AccountPayment, self).create(vals)
        return super(AccountPayment, self).create(vals)

    def action_draft(self):
        for rec in self:
            rec.write({'state_sale_invoice':'cancel'})
        return super(AccountPayment, self).action_draft()

    def action_validate_invoice_payment(self):
        if any(len(record.invoice_ids) > 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        return self.post()

class SalePaymentRegister(models.TransientModel):
    _name = 'sale.payment.register'
    _description = 'Sale Payment Register'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner',
        string="Customer")
    payment_date = fields.Date(string="Payment Date", required=True,
        default=fields.Date.context_today)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False)
    communication = fields.Char(string="Memo", store=True, readonly=False, compute='_compute_communication')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        help="The payment's currency.")
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', store=True, copy=False,
        default='inbound')
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], store=True, copy=False,
        default='customer')
    sale_id = fields.Many2one('sale.order', string="Sale")
    state_sale_invoice = fields.Selection([('no_add','No Add'),('add','Added'),('cancel','Cancel')], string="State Pay Advance", default='no_add')
    company_id = fields.Many2one('res.company', store=True, copy=False)

    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ], limit=1)

    @api.depends('sale_id')
    def _compute_communication(self):
        for wizard in self:
            wizard.communication = wizard.sale_id.name

    def action_create_payments(self):
        vals = {
            'journal_id': self.journal_id.id,
            'partner_type': self.partner_type,
            'payment_type': self.payment_type,
            'state': 'draft',
            'partner_id': self.partner_id.id,
            'date': self.payment_date,
            'amount': self.amount,
            'ref': self.communication,
            'currency_id': self.currency_id.id,
            'sale_id': self.sale_id.id,
            'state_sale_invoice': self.state_sale_invoice,
            'company_id': self.company_id.id
        }
        payment = self.env['account.payment'].create(vals)
        payment.action_post()
        return
