from odoo import api, models, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super()._visible_menu_ids(debug)

        # Se podría chequea si el usaurio tiene el permiso de administración "Ajustes"
        # if not self.env.user.has_group('base.group_system'):
        menus_to_hide = (
            self.env.ref('sale.sale_menu_root'),                                    # Ventas
            self.env.ref('spreadsheet_dashboard.spreadsheet_dashboard_menu_root'),  # Tableros
        )
        for rec in menus_to_hide:
            menus.discard(rec.id)

        return menus
