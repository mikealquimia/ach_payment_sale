# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    status_for_payment = fields.Selection([('draft','Draft'),('sent','Sent'),('sale','Sale'),('done','Done'),('cancel','Cancel')],
                                          string="sale status for payment", related="company_id.status_for_payment", readonly=False)