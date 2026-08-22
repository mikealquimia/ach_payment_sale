# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_id = fields.Many2one('sale.order', string="Sale")
    state_sale_invoice = fields.Selection([('no_add','No Add'),('add','Added'),('cancel','Cancel')], string="State Pay Advance", default='no_add')

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        for rec in self:
            if rec.sale_id:
                rec.communication = rec.sale_id.name
                rec.partner_id = rec.sale_id.partner_id.id
                rec.invoice_ids = False
                rec.payment_type = 'inbound'
                rec.partner_type = 'customer'
        return

    @api.model
    def create(self, vals):
        if vals['sale_id']:
            vals['invoice_ids'] = False
            vals['partner_type'] = 'customer'
            sale_id = self.env['sale.order'].search([('id','=',vals['sale_id'])])
            total_sale = sale_id.amount_total
            total_payment = 0
            total_invoice = 0
            total_residual = 0
            payments = self.env['account.payment'].search([('sale_id','=',sale_id.id),('state_sale_invoice','=','no_add')])
            print(payments)
            for payment in payments:
                total_payment += payment.amount
            if sale_id.invoice_ids:
                for invoice in sale_id.invoice_ids:
                    if invoice.state == 'open':
                        total_residual += invoice.residual
                        total_invoice += invoice.amount_total
                    if invoice.state == 'paid':
                        total_invoice += invoice.amount_total
            dif_amount = (total_sale-total_invoice+total_residual-total_payment)
            if vals['amount'] > dif_amount:
                raise UserError(_("You can only add a down payment of %s to the sale") % (dif_amount))
            else:
                return super(AccountPayment, self).create(vals)
        return super(AccountPayment, self).create(vals)

    @api.multi
    def cancel(self):
        for rec in self:
            rec.write({'state_sale_invoice':'cancel'})
        return super(AccountPayment, self).cancel()

    @api.multi
    def post(self):
        for rec in self:
            if rec.sale_id:
                rec.invoice_ids = False
                if rec.state != 'draft':
                    raise UserError(_("You can only validate payments in Draft status"))
                if not rec.name:
                    if rec.payment_type == 'transfer':
                        sequence_code = 'account.payment.transfer'
                    else:
                        if rec.partner_type == 'customer':
                            if rec.payment_type == 'inbound':
                                sequence_code = 'account.payment.customer.invoice'
                            if rec.payment_type == 'outbound':
                                sequence_code = 'account.payment.customer.refund'
                        if rec.partner_type == 'supplier':
                            if rec.payment_type == 'inbound':
                                sequence_code = 'account.payment.supplier.refund'
                            if rec.payment_type == 'outbound':
                                sequence_code = 'account.payment.supplier.invoice'
                    rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                    if not rec.name and rec.payment_type != 'transfer':
                        raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
                amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = rec._create_payment_entry(amount)
                persist_move_name = move.name
                rec.write({'state': 'posted', 'move_name': persist_move_name})
            else:
                return super(AccountPayment, self).post()

    def action_validate_invoice_payment(self):
        if any(len(record.invoice_ids) > 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        return self.post()

class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if not self.sale_id:
            rec = super(AccountAbstractPayment, self)._compute_payment_difference()
            return rec