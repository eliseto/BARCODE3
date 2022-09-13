from odoo import models, fields, api, _

class PaymentRegisterfrom(models.Model):

    _inherit= 'account.payment'
    payment_date = fields.Date(string="Fecha de cobro")
    list_register_ids = fields.Many2many('list.payment.register', string="Información de pago")
    

class ListPaymentRegister(models.Model):
    _name='list.payment.register'
    _description = 'Nuevo modelo'
    
    bank_id = fields.Many2one('res.bank', string="Banco", copy=True)
    transfer_register = fields.Char(string="No.Transferencia o Cheque")

class PaymentRegisterWizard(models.TransientModel):

    _inherit= 'account.payment.register'
    payment_date_wizard = fields.Date(string="Fecha de cobro")
    list_register_ids = fields.Many2many('list.payment.register', string="Información de pago")