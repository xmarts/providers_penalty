# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import datetime

class LateOrder(models.Model):
	_inherit = 'stock.picking'

	to_accept_late_order = fields.Boolean(string='Acepto pedido', default=False)

	@api.multi
	def button_validate(self):
		self.ensure_one()
		fecha_pedido = self.scheduled_date
		fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		if fecha_actual > fecha_pedido:
			if self.to_accept_late_order is not True:
				raise ValidationError('La fecha de pedido ha expirado, si estas de acuerdo marca la casilla "ACEPTO PEDIDO"')
			if self.to_accept_late_order == True:
				domain = [('is_penalty_product', '!=',False)]
				penalty_product = self.env['product.template'].search(domain, limit=1)
				if penalty_product:
					#domain = [('id','=', self.purchase_id.invoice_ids.id)]
					#search_invoice = self.env['account.invoice'].search(domain, limit=1)
					invoice_true = False
					inv_id = ''
					id_refund = ''
					if self.purchase_id.invoice_ids:
						for i in self.purchase_id.invoice_ids:
							if i.state != 'cancel':
								invoice_true = True
								inv_id = i.id
					if invoice_true == True:
						#CREAMOS LA NOTA DE CREDITO CON RELACION A LA FACTURA DEL PROVEEDOR				
						refund_obj = self.env['account.invoice']
						refund_value = {
							'partner_id': self.purchase_id.partner_id.id,
							'reference': self.purchase_id.partner_ref,
							'origin': self.name,
							'date_invoice': fecha_actual,
							'type': 'in_refund',
						}	
						refund_id = refund_obj.create(refund_value)
						self.purchase_id.invoice_ids.write({'refund_invoice_id':refund_id.id})
						#LLENAMOS NUESTRA LINEAS CON UN PRODUCTO DE PENALIZACION
						line_refund_obj = self.env['account.invoice.line']
						line_refund_value = {
							'product_id': penalty_product.id,
							'name': penalty_product.name,
							'account_id': 1,
							'quantity': 1,
							'price_unit': penalty_product.list_price,
							'price_subtotal': penalty_product.list_price,
							'invoice_id': refund_id.id
						}
						line_refund_id = line_refund_obj.create(line_refund_value)

						return super(LateOrder, self).button_validate()
					else:
						#CREAMOS LA FACTURA, MANDADO LOS DATOS DE REFERENCIA DE LA COMPRA
						invoice_obj = self.env['account.invoice']
						invoice_value = {
							'partner_id': self.purchase_id.partner_id.id,
							'reference': self.purchase_id.partner_ref,
							'origin':self.name,
							'date_invoice':fecha_actual,
							'type': 'in_invoice',
						}
						invoice_id = invoice_obj.create(invoice_value)
						#LLENAMOS LA LINEAS DE LA FACTURA, LE MANDAMOS LOS DATOS DEL PRODUCTO
						line_obj = self.env['account.invoice.line']
						account_default = 27
						for line in self.purchase_id.order_line:
							line_value = {
								'product_id': line.product_id.id,
								'name':line.name,
								'account_id': account_default,
								'quantity': line.product_qty,
								'price_unit': line.price_unit,
								'invoice_line_tax_ids': [(6,0, line.taxes_id.ids)],
								'price_subtotal': line.price_subtotal,
								'invoice_id': invoice_id.id,
							}
							line_id = line_obj.create(line_value)	
							#LLENAMOS LA TABLA DE CUENTA DE LOS IMPUESTOS
							tax_obj = self.env['account.invoice.tax']
							cuenta = 1
							for x in line.taxes_id:
								tax_amount = x.amount * line.price_subtotal / 100
								tax_value = {
									'name': [(6,0, x.name)],
									'account_id': cuenta,
									'amount': tax_amount,
									'invoice_id': invoice_id.id,
								}
								tax_id = tax_obj.create(tax_value)
						#CREAMOS LA NOTA DE CREDITO CON RELACION A LA FACTURA DEL PROVEEDOR				
						refund_obj = self.env['account.invoice']
						refund_value = {
							'partner_id':self.purchase_id.partner_id.id,
							'reference': self.purchase_id.partner_ref,
							'origin': self.name,
							'date_invoice': fecha_actual,
							'type': 'in_refund',
						}	
						refund_id = refund_obj.create(refund_value)
						invoice_id.write({'refund_invoice_id':refund_id.id})
						#LLENAMOS NUESTRA LINEAS CON UN PRODUCTO DE PENALIZACION
						val_product = self.purchase_id.amount_total * 5 /100
						line_refund_obj = self.env['account.invoice.line']
						line_refund_value = {
							'product_id': penalty_product.id,
							'name': penalty_product.name,
							'account_id': 1,
							'quantity': 1,
							'price_unit': val_product,
							'price_subtotal': val_product,
							'invoice_id': refund_id.id
						}
						line_refund_id = line_refund_obj.create(line_refund_value)	
						return super(LateOrder, self).button_validate()
				else:
					raise ValidationError('No existe un producto de tipo penalización.')	
		else:
			return super(LateOrder, self).button_validate()				

class ProductTemplate(models.Model):
	_inherit = 'product.template'
	is_penalty_product = fields.Boolean(string='Producto de penalización', default=False)






























