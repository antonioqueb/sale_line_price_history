# -*- coding: utf-8 -*-
from odoo import models, fields


class SalePriceHistoryWizard(models.TransientModel):
    _name = 'sale.price.history.wizard'
    _description = 'Historial de precios de venta por cliente y producto'

    partner_id = fields.Many2one(
        'res.partner', string='Cliente', readonly=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Producto', readonly=True,
    )
    line_ids = fields.Many2many(
        'sale.order.line', string='Ventas anteriores',
    )