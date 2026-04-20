# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_view_price_history(self):
        """Abre un popup grande con el historial de ventas del mismo producto
        al mismo cliente, ordenado por precio unitario ascendente.
        """
        self.ensure_one()

        partner = self.order_id.partner_id
        product = self.product_id

        if not partner:
            raise UserError(_("Selecciona primero el cliente en la orden."))
        if not product:
            raise UserError(_("Selecciona primero el producto en la línea."))

        partner_ids = [partner.id]
        if partner.parent_id:
            partner_ids.append(partner.parent_id.id)

        domain = [
            ('product_id', '=', product.id),
            ('order_partner_id', 'in', partner_ids),
            ('state', 'in', ['sale', 'done']),
            ('product_uom_qty', '>', 0),
        ]
        if isinstance(self.id, int):
            domain.append(('id', '!=', self.id))

        lines = self.env['sale.order.line'].search(domain)

        if not lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Sin historial"),
                    'message': _(
                        "No se ha vendido '%(product)s' a '%(partner)s' anteriormente.",
                        product=product.display_name,
                        partner=partner.name,
                    ),
                    'type': 'info',
                    'sticky': False,
                },
            }

        wizard = self.env['sale.price.history.wizard'].create({
            'partner_id': partner.id,
            'product_id': product.id,
            'line_ids': [(6, 0, lines.ids)],
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Historial de precios"),
            'res_model': 'sale.price.history.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'context': {'dialog_size': 'extra-large'},
        }