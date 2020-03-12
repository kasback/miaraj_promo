# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    type = fields.Selection([
        ('parent', 'Bon de commande parent'),
        ('child', 'Sous bon de commande')],
        string="Type", default='parent', required=True)

    original_po = fields.Many2one('purchase.order', string='Document d\'origine')

    amount_total = fields.Monetary(string='Total', store=True, readonly=False, compute='_amount_all')

    ice_partenaire = fields.Char(related="partner_id.ice", string='ICE')

    @api.onchange('order_line')
    def on_change_order_line(self):
        for line in self.order_line:
            for origin_line in self.original_po.order_line:
                if line.product_id == origin_line.product_id and \
                        line.product_qty > (origin_line.product_qty - origin_line.qte_consomee):
                    raise ValidationError('Vous avez excédé la qte maximale')

    @api.model
    def create(self, vals):
        line_env = self.env['purchase.order.line']
        res = super(PurchaseOrder, self).create(vals)
        if vals.get('original_po'):
            original_po = self.search([('id', '=', vals.get('original_po'))])
            for line in original_po.order_line:
                new_line = line_env.create({
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'order_id': res.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_qty': 0,
                    'date_planned': line.date_planned,
                    'price_unit': line.price_unit
                })
                new_line.onchange_product_id()
                new_line.write({
                    'product_qty': 0
                })
        return res

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals.get('order_line', None) and self.type == 'child':
            changed_lines = vals['order_line']
            for line in changed_lines:
                if line[2] and "product_qty" in line[2]:
                    if line[0] == 0:
                        product_id = line[2]['product_id']
                    else:
                        product_id = self.env['purchase.order.line'].search([('id', '=', line[1])]).product_id.id
                    qte_changed = line[2]['product_qty']
                    for line_origin in self.original_po.order_line:
                        if line_origin.product_id.id == product_id:
                            # line_origin.product_qty -= qte_changed
                            # line_origin._onchange_quantity()
                            line_origin.qte_consomee += qte_changed
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qte_consomee = fields.Float(u'Qte consomée')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        purchase_id = self.env['purchase.order'].search([('id', '=', self.purchase_id.original_po.id)])
        for move in self.move_ids_without_package:
            print('move', move)
            for order_line in purchase_id.order_line:
                if order_line.product_id == move.product_id:
                    order_line.qty_received += move.quantity_done
        return res
