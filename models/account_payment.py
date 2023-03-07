# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_id = fields.Many2one('sale.order', string="Orden de Venta")
    state_sale_invoice = fields.Selection([('no_add','Sin añadir'),('add','Añadido'),('cancel','Cancelado')], string="Estado de Anticipo", default='no_add')

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        for rec in self:
            rec.communication = rec.sale_id.name
            rec.partner_id = rec.sale_id.partner_id.id
        return
    
    @api.model
    def create(self, vals):
        if vals['sale_id']:
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
                raise UserError(_("Solo puedes agregar un anticipo de %s a la venta") % (dif_amount))
        res = super(AccountPayment, self).create(vals)
        return res
    
    @api.multi
    def cancel(self):
        for rec in self:
            rec.write({'state_sale_invoice':'cancel'})
        return super(AccountPayment, self).cancel()
    
    @api.multi
    def post(self):
        for rec in self:
            if rec.sale_id:
                if rec.state != 'draft':
                    raise UserError(_("Solo se pueden validar pagos en estado Borrador"))
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
                res = super(AccountPayment, self).post()
            return True

class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if not self.sale_id:
            rec = super(AccountAbstractPayment, self)._compute_payment_difference()
            return rec        
    