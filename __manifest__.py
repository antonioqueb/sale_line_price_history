{
    'name': 'Sale Line Price History',
    'version': '19.0.1.0.0',
    'summary': 'Historial de precios de venta por cliente y producto en la línea de SO',
    'description': """
Agrega un ícono de historial en cada línea de la orden de venta.
Al pulsarlo abre un popup con las ventas anteriores del mismo producto
al mismo cliente, ordenadas por precio unitario.
Si no hay historial, muestra una notificación y no abre popup.
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
    'assets': {
        'web.assets_backend': [
            'sale_line_price_history/static/src/scss/sale_price_history.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}