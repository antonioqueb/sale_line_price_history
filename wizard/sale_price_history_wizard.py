# -*- coding: utf-8 -*-
from odoo import models, fields


class SalePriceHistoryWizard(models.TransientModel):
    _name = 'sale.price.history.wizard'
    _description = 'Historial de precios de venta por cliente y producto'

    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    line_ids = fields.One2many(
        'sale.price.history.wizard.line', 'wizard_id',
        string='Ventas anteriores',
    )


class SalePriceHistoryWizardLine(models.TransientModel):
    _name = 'sale.price.history.wizard.line'
    _description = 'Línea del historial de precios'
    _order = 'price_unit asc'

    wizard_id = fields.Many2one(
        'sale.price.history.wizard', required=True, ondelete='cascade',
    )
    sale_order_line_id = fields.Many2one('sale.order.line', string='Línea original')
    order_id = fields.Many2one('sale.order', string='Orden')
    date_order = fields.Datetime(string='Fecha')
    product_uom_qty = fields.Float(string='Cantidad')
    price_unit = fields.Monetary(string='Precio unitario', currency_field='currency_id')
    discount = fields.Float(string='Desc. %')
    price_subtotal = fields.Monetary(string='Subtotal', currency_field='currency_id')
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('sent', 'Enviada'),
            ('sale', 'Orden de venta'),
            ('done', 'Bloqueada'),
            ('cancel', 'Cancelada'),
        ],
        string='Estado',
    )
    currency_id = fields.Many2one('res.currency', string='Moneda')