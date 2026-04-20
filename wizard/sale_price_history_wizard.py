# -*- coding: utf-8 -*-
from odoo import models, fields, api


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
    current_price_unit = fields.Monetary(
        string='Precio actual', readonly=True,
        currency_field='company_currency_id',
    )
    company_currency_id = fields.Many2one(
        'res.currency', compute='_compute_company_currency',
    )

    sale_count = fields.Integer(
        string='Ventas', compute='_compute_stats',
    )
    last_price = fields.Monetary(
        string='Último precio', compute='_compute_stats',
        currency_field='company_currency_id',
    )
    min_price = fields.Monetary(
        string='Precio mínimo', compute='_compute_stats',
        currency_field='company_currency_id',
    )
    max_price = fields.Monetary(
        string='Precio máximo', compute='_compute_stats',
        currency_field='company_currency_id',
    )
    avg_price = fields.Monetary(
        string='Precio promedio', compute='_compute_stats',
        currency_field='company_currency_id',
    )

    def _compute_company_currency(self):
        for wiz in self:
            wiz.company_currency_id = self.env.company.currency_id

    @api.depends('line_ids', 'line_ids.price_unit', 'line_ids.order_id.date_order')
    def _compute_stats(self):
        for wiz in self:
            lines = wiz.line_ids
            wiz.sale_count = len(lines)
            if not lines:
                wiz.last_price = 0.0
                wiz.min_price = 0.0
                wiz.max_price = 0.0
                wiz.avg_price = 0.0
                continue
            prices = [l.price_unit for l in lines]
            wiz.min_price = min(prices)
            wiz.max_price = max(prices)
            wiz.avg_price = sum(prices) / len(prices)
            ordered = lines.sorted(
                key=lambda l: l.order_id.date_order or fields.Datetime.now(),
                reverse=True,
            )
            wiz.last_price = ordered[:1].price_unit
