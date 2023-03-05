# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

class PayrollJournalReport(models.AbstractModel):
    _name = 'report.sale.day_payment.report' 
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Sale Payments Day"

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Movimiento de Caja')
        datetime_start = datetime(year=lines.date.year,month=lines.date.month,day=lines.date.day,hour=0,minute=0,second=1)
        datetime_stop = datetime(year=lines.date.year,month=lines.date.month,day=lines.date.day,hour=23,minute=59,second=59)
        #sales with confirmation date for the date report
        sale_order_ids = self.env['sale.order'].search([
            ('state','in',['sale','done']),
            ('confirmation_date','>=',datetime_start),('confirmation_date','>=',datetime_stop),],order='asc confirmation_date')
        for sale in sale_order_ids:
            without_payment = True
            if sale.invoice_ids:
                for invoice in sale.invoice_ids:
                    payment_day = 0
                    for payment in invoice.payment_ids:
                        if payment.date == lines.date:
                            payment_day += payment.amount
                    if payment_day != 0:
                        without_payment = False    
                        print('Se imprime info de venta con su factura y pagos')
            if sale.payment_ids:
                paymen_day = 0
                for paymen in sale.payment_ids:
                    if paymen.date == lines.date:
                        paymen_day += paymen.amount
                if paymen_day != 0:
                    without_payment = False
                    print('Se imprime datos de la venta sin facturas con adelantos')
            if without_payment == True:
                print('Imprimir información de la venta sin pagos')
                        
        #invoice with pament to date report
        payment_ids = self.env['account.payment'].search([
            ('date','=',lines.date),('partner_type','=','customer'),('invoice_ids','!=',False)])
        for payme in payment_ids:
            for invoic in payme.invoice_ids:
                for sale in invoic.sale_ids:
                    if sale.confirmation_date <= datetime_start and sale.confirmation_date >= datetime_stop:
                        print('imprime la')
        workbook.close()