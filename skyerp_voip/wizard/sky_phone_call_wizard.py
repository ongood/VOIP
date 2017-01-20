# -*- coding: utf-8 -*-
from openerp import fields,models,api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

from odoo.http import content_disposition, request
from cStringIO import StringIO
try:
    import xlwt
except ImportError:
    xlwt = None

class PhoneCallWizard(models.TransientModel):
    _name = 'sky.phone.call.wizard'

    phone = fields.Char('Phone')