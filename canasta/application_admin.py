#-------------------------------------------------------------------------------
# Copyright (C) 2012 Francisco Dibar

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------

from camelot.admin import action
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section
from camelot.view.art import Icon

import model
import view

class MyApplicationAdmin(ApplicationAdmin):

    name = 'Canasta Familiar'
    application_url = 'http://github.com/frandibar/canasta'
    help_url = 'http://www.python-camelot.com/docs.html'
    author = 'Francisco Dibar'
    # domain = 'mydomain.com'

    def get_sections(self):
        from camelot.model.memento import Memento
        from camelot.model.i18n import Translation
        sections = [
            # Section('Altas',
            #         self,
            #         Icon('tango/22x22/actions/list-add.png'),
            #         items = [model.Compra]),
            Section('Entidades',
                    self,
                    Icon('tango/22x22/apps/system-users.png'),
                    items = [model.Establecimiento,
                             model.Categoria,
                             model.Marca,
                             model.Articulo,
                             model.Precio,
                             model.Compra,
                             view.ListaDePrecios,
                             view.CompraMensual,
                             ]),
            # Section('Consultas',
            #         self,
            #         Icon('tango/22x22/apps/system-users.png'),
            #         items = [
            #             ]),
            ]
        return sections

    def get_actions(self):
        act = action.OpenNewView(self.get_related_admin(model.Compra))
        act.icon = Icon('tango/32x32/actions/list-add.png')
        return [act]
