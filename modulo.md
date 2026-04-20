## ./__init__.py
```py
from . import models
from . import wizard
```

## ./__manifest__.py
```py
{
    'name': 'Sale Line Price History',
    'version': '19.0.1.0.0',
    'summary': 'Historial de precios de venta por cliente y producto en la línea de SO',
    'description': """
Agrega un ícono de historial en cada línea de la orden de venta.
Al pulsarlo abre un popup con las ventas anteriores del mismo producto
al mismo cliente, mostrando número de orden, precio unitario, cantidad,
descuento y subtotal, más un resumen con precio mínimo, máximo, promedio
y último precio.
Si no hay historial, muestra una notificación discreta y no abre popup.
    """,
    'author': 'Alphaqueb Consulting SAS',
    'website': 'https://alphaqueb.com',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_price_history_wizard_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## ./models/__init__.py
```py
from . import sale_order_line
```

## ./models/sale_order_line.py
```py
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
        }```

## ./views/sale_order_view.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_order_form_inherit_price_history" model="ir.ui.view">
        <field name="name">sale.order.form.inherit.price.history</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="arch" type="xml">

            <!-- Botón en la vista de lista editable de las líneas -->
            <xpath expr="//field[@name='order_line']/list//field[@name='price_unit']" position="before">
                <button name="action_view_price_history"
                        type="object"
                        icon="fa-history"
                        title="Ver historial de precios para este cliente"
                        class="btn btn-link p-0"
                        invisible="not product_id or not parent.partner_id"/>
            </xpath>

            <!-- Botón también en la vista form emergente de la línea -->
            <xpath expr="//field[@name='order_line']/form//field[@name='price_unit']" position="before">
                <button name="action_view_price_history"
                        type="object"
                        icon="fa-history"
                        string="Historial de precios"
                        class="btn btn-link oe_inline"
                        invisible="not product_id or not parent.partner_id"/>
            </xpath>

        </field>
    </record>

</odoo>
```

## ./wizard/__init__.py
```py
from . import sale_price_history_wizard
```

## ./wizard/sale_price_history_wizard.py
```py
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
    )```

## ./wizard/sale_price_history_wizard_view.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_sale_price_history_wizard_form" model="ir.ui.view">
        <field name="name">sale.price.history.wizard.form</field>
        <field name="model">sale.price.history.wizard</field>
        <field name="arch" type="xml">
            <form string="Historial de precios">
                <div class="p-3">
                    <h2 class="mb-0">
                        <i class="fa fa-history me-2 text-primary"/>
                        <field name="product_id" nolabel="1" readonly="1" class="oe_inline"
                               options="{'no_open': True, 'no_create': True}"/>
                    </h2>
                    <h4 class="text-muted mt-1 mb-3">
                        <i class="fa fa-user me-1"/>
                        <field name="partner_id" nolabel="1" readonly="1" class="oe_inline"
                               options="{'no_open': True, 'no_create': True}"/>
                    </h4>

                    <field name="line_ids" nolabel="1">
                        <list create="0" edit="0" delete="0" duplicate="0"
                              default_order="price_unit asc">
                            <field name="order_id" string="Orden"/>
                            <field name="create_date" string="Fecha"/>
                            <field name="product_uom_qty" string="Cantidad"/>
                            <field name="price_unit" string="Precio unitario" decoration-bf="1"/>
                            <field name="discount" string="Desc. %"/>
                            <field name="price_subtotal" string="Subtotal"/>
                            <field name="currency_id" column_invisible="1"/>
                            <field name="state" string="Estado"
                                   decoration-success="state == 'sale'"
                                   decoration-muted="state == 'done'"
                                   widget="badge"/>
                        </list>
                    </field>
                </div>
                <footer>
                    <button string="Cerrar" special="cancel" class="btn-primary"/>
                </footer>
            </form>
        </field>
    </record>

</odoo>```

