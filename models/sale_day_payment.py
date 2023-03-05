# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SalePayments(models.TransientModel):
    _name = 'sale.day_payment'
    _description = 'Sale Payments'

    name = fields.Char(string='Nombre')
    date = fields.Date(string='Date')
    journal_ids = fields.Many2one('account.journal', string='Journal')

    def get_report(self):
        self.env.ref('sale.day_payment.report').report_action(self)
        return