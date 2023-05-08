# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    status_for_payment = fields.Selection([('draft','Draft'),('sent','Sent'),('sale','Sale'),('done','Done'),('cancel','Cancel')],
                                          string="sale status for payment", default='sale')