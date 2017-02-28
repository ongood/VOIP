# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

class PhoneCall(models.Model):
    _name = 'sky.phone.call'
    _description = 'Phone call event'
    _order = 'start_time desc'

    call_id     = fields.Char('Call ID', index=True)
    phone_src   = fields.Char('Số gọi đến', required=True)
    phone_dest  = fields.Char('Số nhận', required=True)
    status      = fields.Char('Trạng thái')
    link        = fields.Char('File ghi âm')
    duration    = fields.Integer('Duration')
    billsec     = fields.Integer('Billsec')
    type        = fields.Char('Kiểu cuộc gọi')
    start_time  = fields.Datetime('Thời gian bắt đầu')

    # date        = fields.Datetime('Date', default=fields.Datetime.now, readonly=True)
    # name        = fields.Char('Phone number', required=True, readonly=True)
    partner_id  = fields.Many2one('res.partner', 'Partner', readonly=True)
    address     = fields.Char('Address')
    user_id     = fields.Many2one('res.users', 'Người nhận', compute='_compute_user_id', store=True)
    order_id    = fields.Many2one('sale.order', 'Order', readonly=True)
    note        = fields.Text('Note')

    @api.one
    @api.depends('phone_dest')
    def _compute_user_id(self):
        self = self.sudo()
        user = self.env['res.users'].search([('partner_id.phone', '=', self.phone_dest)], limit=1)
        if user:
            self.user_id = user.id

    

    # call_id, phone_src, phone_dest, status, recording_link, duration, billsec, type, start_time

class ResUsers(models.Model):
    _inherit = 'res.users'

    take_call  = fields.Boolean('To receive calls')
    phone      = fields.Char(related='partner_id.phone')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_internal_number_from_number(self, number=None):
        self = self.sudo()
        print 'get_internal_number_from_number', number
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
    def incoming_phone_call(self, number, phone, call_id=None):
        print 'incoming_phone_call', number, phone, call_id
        self = self.sudo()
        try:        
            user = self.env['res.users'].search([('partner_id.phone', '=', phone)])
            
            partner_ids = self.search(['|', ('phone', '=', number), ('mobile', '=', number)])
            if partner_ids:
                action = self.env.ref('skyerp_voip.sky_action_poup')
                action['res_id']    = partner_ids[0].id
            else:
                action = self.env.ref('skyerp_voip.sky_phone_call_wizard_action')

            action['context'] = {'default_phone': number}
            wizard = self.env['web.action.request.setting'].create({
                'user': user.id,
                'action': action.id,
            })
            wizard.button_check_action_request()
            wizard.unlink()
            action['context'] = {}            
            partner = self.search(['|', ('phone', '=', number), ('mobile', '=', number)])
            partner = partner and partner[0] or False
            self.env['sky.phone.call'].create({
                'start_time': fields.Datetime.now(),
                'phone_src': number,
                'phone_dest': phone,                
                'partner_id': partner.id,
                'address': partner and partner.with_context(show_address_only=1).name_get()[0][1] or False,
            })

            # user.notify_warning('You have a new call.')
        except Exception as e:
            return False
        return True

    # @api.model
    # def outgoing_phone_call(self, number, phone, call_id=None):
    #     self = self.sudo()
    #     print 'outgoing_phone_call', number, phone, call_id
    #     try:
    #         print 'Out going phone', number, phone
    #         return True
    #     except Exception as e:
    #         return False

    @api.model
    def phone_call_result(self, call_id, phone_src, phone_dest, status, recording_link, duration, billsec, call_type, start_time):
        # print call_id, phone_src, phone_dest, status, recording_link, duration, billsec, type, start_time
        self = self.sudo()
        self.env['sky.phone.call'].create({
            'call_id': call_id,
            'phone_src': phone_src,
            'phone_dest': phone_dest,
            'status': status,
            'recording_link': recording_link,
            'duration': duration,
            'billsec': billsec,
            'type': call_type,
            'start_time': start_time,
        })

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