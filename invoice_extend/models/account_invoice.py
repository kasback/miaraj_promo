# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    custom_total = fields.Float(string=u'Deuxième Total', store=True)

    order_ids = fields.One2many('purchase.order', 'invoice_id', string="Bon de commandes liés")

    @api.onchange('vendor_bill_purchase_id')
    def _onchange_bill_purchase_order(self):
        purchase_id = self.vendor_bill_purchase_id.purchase_order_id
        if purchase_id:
            self.order_ids = [(4, purchase_id.id)]
        res = super(AccountInvoice, self)._onchange_bill_purchase_order()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        pos_cat_id = self.env.ref('point_of_sale.product_category_pos')

        product_id = self.env['product.template'].search([('id', '=', vals['product_id'])])

        if not product_id.pos_comptabilise and product_id.categ_id == pos_cat_id:
            return self.browse()

        return super(AccountInvoiceLine, self).create(vals)


class SaleOrder(models.Model):
    _inherit = "purchase.order"

    invoice_id = fields.Many2one('account.invoice')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pos_comptabilise = fields.Boolean('POS comptabilisé')


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.multi
    def _create_returns(self):
        vals = super(StockReturnPicking, self)._create_returns()
        purchase_id = self.env['purchase.order'].search([('id', '=', self.picking_id.purchase_id.id)])
        for retour in self.product_return_moves:
            for order_line in purchase_id.order_line:
                if order_line.product_id == retour.product_id:
                    order_line.qty_received -= retour.quantity
        return vals

