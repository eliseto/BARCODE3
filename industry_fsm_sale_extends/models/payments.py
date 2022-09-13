from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    invoice_ids = fields.Many2many('account.move', 'account_invoice_payment_rel', 'payment_id', 'invoice_id', string="Invoices", copy=False)
    created_by_router = fields.Boolean(string="Creado por una ruta", default=False)
   
    def action_view_move(self):
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('move_id').ids)],
            'context': {
                'journal_id': self.journal_id.id,
            }
        }
    
    def action_post(self):
        """
        Herencia a la funcion action_post, si el pago es creado desde las rutas (project.task)
        Traera por defecto la factura, entonces se condiciona para hacer la conciliacion con el pago
        caso contrario solo publica el pago.
        """
        res = super(AccountPayment, self).action_post()
        if self.invoice_ids and self.created_by_router:
            partner_account = self.partner_id.property_account_receivable_id.id
            for payment_res in self:
                if payment_res.invoice_ids:
                    moves_to_reconcile = []
                    # Recorre las lineas de pago
                    for move in payment_res.move_id.line_ids:
                        if move.account_id.id == partner_account:
                            moves_to_reconcile = []
                            moves_to_reconcile.append(move.id)
                    # Recorre las lineas de la factura
                    for invoice in payment_res.invoice_ids:
                        for move in invoice.line_ids:

                            if move.account_id.id == partner_account:
                                moves_to_reconcile.append(move.id)
                    move_lines = self.env['account.move.line'].search([('id','in',moves_to_reconcile)])
                    move_lines.reconcile()
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    """ Herencia en el wizard para mandar nuevos campos a account_payment"""     
    def is_create_by_router(self):
        for record in self:
            created_by_router =  self._context.get('created_by_router', False)
        return created_by_router

    def _create_payment_vals_from_batch(self, batch_result):
        batch_values = self._get_wizard_values_from_batch(batch_result)
        if batch_values['payment_type'] == 'inbound':
            partner_bank_id = self.journal_id.bank_account_id.id
        else:
            partner_bank_id = batch_result['payment_values']['partner_bank_id']

        return {
            'date': self.payment_date,
            'amount': batch_values['source_amount_currency'],
            'payment_type': batch_values['payment_type'],
            'partner_type': batch_values['partner_type'],
            'ref': self._get_batch_communication(batch_result),
            'invoice_ids': self.line_ids.move_id,
            'created_by_router': self.is_create_by_router(),
            'list_register_ids': self.list_register_ids,
            'payment_date': self.payment_date_wizard,
            'journal_id': self.journal_id.id,
            'currency_id': batch_values['source_currency_id'],
            'partner_id': batch_values['partner_id'],
            'partner_bank_id': partner_bank_id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': batch_result['lines'][0].account_id.id
        }

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'invoice_ids': self.line_ids.move_id,
            'created_by_router': self.is_create_by_router(),
            'list_register_ids': self.list_register_ids,
            'payment_date': self.payment_date_wizard,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals

    def _reconcile_payments(self, to_process, edit_mode=False):
        if self.is_create_by_router:
            domain = [
                ('parent_state', '=', 'draft'),
                ('account_internal_type', 'in', ('receivable', 'payable')),
                ('reconciled', '=', False),
            ]
        else:
            domain = [
                ('parent_state', '=', 'posted'),
                ('account_internal_type', 'in', ('receivable', 'payable')),
                ('reconciled', '=', False),
            ]

            for vals in to_process:
                payment_lines = vals['payment'].line_ids.filtered_domain(domain)
                lines = vals['to_reconcile']

                for account in payment_lines.account_id:
                    (payment_lines + lines)\
                        .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                        .reconcile()

    def _post_payments(self, to_process, edit_mode=False):
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
        if self.is_create_by_router():
            payments.action_draft()
        else:
            payments.action_post()