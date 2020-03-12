# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    ice = fields.Char('ICE')

    @api.one
    @api.constrains('ice')
    def _check_ice(self):
        if self.ice and (len(self.ice) != 15 or not self.ice.isdigit()):
                raise ValidationError(u"L'ICE doit être constitué de 15 chiffres")