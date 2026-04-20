# -*- coding: utf-8 -*-
from markupsafe import Markup, escape
from odoo import models, fields, api
from odoo.tools import format_amount, format_datetime


class SalePriceHistoryWizard(models.TransientModel):
    _name = 'sale.price.history.wizard'
    _description = 'Historial de precios de venta por cliente y producto'

    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    line_ids = fields.Many2many('sale.order.line', string='Ventas anteriores')
    history_html = fields.Html(
        string='Historial',
        compute='_compute_history_html',
        sanitize=False,
    )

    _STATE_MAP = {
        'draft': ('Borrador', 'text-bg-secondary'),
        'sent': ('Enviada', 'text-bg-info'),
        'sale': ('Orden de venta', 'text-bg-success'),
        'done': ('Bloqueada', 'text-bg-dark'),
        'cancel': ('Cancelada', 'text-bg-danger'),
    }

    @api.depends('line_ids')
    def _compute_history_html(self):
        for wiz in self:
            if not wiz.line_ids:
                wiz.history_html = False
                continue

            lines = wiz.line_ids.sorted(key=lambda l: l.price_unit)
            rows = []
            for line in lines:
                order_name = escape(line.order_id.name or '')
                order_url = f'/odoo/sales/{line.order_id.id}'
                date = (
                    format_datetime(self.env, line.order_id.date_order)
                    if line.order_id.date_order else ''
                )
                qty = f"{line.product_uom_qty:,.2f}"
                price = format_amount(self.env, line.price_unit, line.currency_id)
                discount = f"{line.discount:.2f}%"
                subtotal = format_amount(self.env, line.price_subtotal, line.currency_id)
                state_label, state_cls = self._STATE_MAP.get(
                    line.state, (line.state or '', 'text-bg-secondary')
                )
                rows.append(
                    '<tr>'
                    f'<td class="align-middle o_ph_order">'
                    f'<a href="{order_url}" target="_blank" rel="noopener" '
                    f'class="o_ph_link" title="Abrir orden en pestaña nueva">'
                    f'<strong>{order_name}</strong>'
                    f' <i class="fa fa-external-link fa-xs ms-1"/>'
                    f'</a></td>'
                    f'<td class="align-middle">{escape(date)}</td>'
                    f'<td class="align-middle text-end">{qty}</td>'
                    f'<td class="align-middle text-end o_ph_price">{escape(price)}</td>'
                    f'<td class="align-middle text-end">{discount}</td>'
                    f'<td class="align-middle text-end o_ph_subtotal">{escape(subtotal)}</td>'
                    f'<td class="align-middle">'
                    f'<span class="badge {state_cls}">{escape(state_label)}</span>'
                    f'</td>'
                    '</tr>'
                )
            table = (
                '<table class="table table-hover o_ph_table mb-0">'
                '<thead><tr>'
                '<th>Orden</th>'
                '<th>Fecha</th>'
                '<th class="text-end">Cantidad</th>'
                '<th class="text-end">Precio unitario</th>'
                '<th class="text-end">Desc. %</th>'
                '<th class="text-end">Subtotal</th>'
                '<th>Estado</th>'
                '</tr></thead>'
                '<tbody>' + ''.join(rows) + '</tbody>'
                '</table>'
            )
            wiz.history_html = Markup(table)