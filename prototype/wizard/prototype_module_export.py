# -*- encoding: utf-8 -*-
# #############################################################################
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2010 - 2014 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import StringIO
import base64
import zipfile
from collections import namedtuple
from openerp import fields, models, api


class prototype_module_export(models.TransientModel):
    _name = "prototype.module.export"

    name = fields.Char('File Name', readonly=True)
    api_version = fields.Selection(
        [
            ('8.0', '8.0'),
            # ('7.0', '7.0')
        ],
        'API version',
        required=True,
        default='8.0'
    )
    data = fields.Binary('File', readonly=True)
    state = fields.Selection(
        [
            ('choose', 'choose'),  #  choose version
            ('get', 'get')  #  get module
        ],
        default='choose'
    )

    @api.model
    def action_export(self, ids):
        """
        Export a zip file containing the module based on the information
        provided in the prototype, using the templates chosen in the wizard.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        wizard = self.browse(ids)

        active_model = self._context.get('active_model')

        # checking if the wizard was called by a prototype.
        assert active_model == 'prototype', \
            '{} has to be called from a "prototype" , not a "{}"'.format(
                self, active_model
            )

        prototype_model = self.env[active_model]
        prototype = prototype_model.browse(
            self._context.get('active_id')
        )
        # files = prototype.generate_files()
        file_details = (
            ('test.txt', 'generated'),
        )
        zip_details = self.zip_files(file_details)

        wizard.write(
            {
                'name': '{}.zip'.format(prototype.name),
                'state': 'get',
                'data': base64.encodestring(zip_details.stringIO.getvalue())
            }
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'prototype.module.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wizard.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @staticmethod
    def zip_files(file_details):
        Zip_details = namedtuple('Zip_details', ['zip_file', 'stringIO'])
        out = StringIO.StringIO()

        with zipfile.ZipFile(out, 'w') as target:
            for filename, filecontent in file_details:
                info = zipfile.ZipInfo(filename)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 2175008768  # specifies mode 0644
                target.writestr(info, filecontent)

            return Zip_details(zip_file=target, stringIO=out)
