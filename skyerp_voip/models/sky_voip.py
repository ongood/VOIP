# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

class PhoneCall(models.Model):
    _name = 'sky.phone.call'
    _description = 'Phone call event'
    _order = 'date desc'

    date        = fields.Datetime('Date', default=fields.Datetime.now(), readonly=True)
    name        = fields.Char('Phone number', required=True, readonly=True)
    partner_id  = fields.Many2one('res.partner', 'Partner', readonly=True)
    address     = fields.Char('Address')
    user_id     = fields.Many2one('res.users', 'Saleperson', readonly=True)
    order_id    = fields.Many2one('sale.order', 'Order', readonly=True)
    note        = fields.Text('Note')

class ResUsers(models.Model):
    _inherit = 'res.users'

    take_call  = fields.Boolean('To receive calls')
    phone      = fields.Char(related='partner_id.phone')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_internal_number_from_number(self, number=None):
        if not number:
            return 'Number is required'
        ids = self.search(['|', ('phone', '=', number), ('mobile', '=', number)])
        if not ids:
            return 'Not found'
        if not ids[0].sky_team_id:
            return 'Not found'
        for member in ids[0].sky_team_id.member_ids:
            if member.take_call:
                return member.phone

    @api.model
    def incoming_phone_call(self, number, phone):
        try:        
            user = self.env['res.users'].search([('partner_id.phone', '=', phone)])
            # user = self.env['res.users'].browse(1)
            wizard = self.env['web.action.request.setting'].create({
                'user': user.id,
                'action': 350,
            })
            wizard.button_check_action_request()
            partner = self.search(['|', ('phone', '=', number), ('mobile', '=', number)])
            partner = partner and partner[0] or False
            self.env['sky.phone.call'].sudo().create({
                'name': number,
                'user_id': user.id,
                'partner_id': partner.id,
                'address': partner and partner.with_context(show_address_only=1).name_get()[0][1] or False,
            })
            # user.notify_warning('You have a new call.')
        except Exception as e:
            return False
        return True

    @api.model
    def outgoing_phone_call(self, number, phone):
        try:
            print 'Out going phone', number, phone
            return True
        except Exception as e:
            return False

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        call = self.env['sky.phone.call'].search([('partner_id', '=', res.partner_id.id)], order='date desc', limit=1)
        if call:
            if not call.order_id:
                call.sudo().write({'order_id': res.id})
        return res