
from camelot.admin import action
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section
from camelot.view.art import Icon

import model

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
            Section('Altas',
                    self,
                    Icon('tango/22x22/actions/list-add.png'),
                    items = [model.Carrito]),
            Section('Entidades',
                    self,
                    Icon('tango/22x22/apps/system-users.png'),
                    items = [model.Supermercado,
                             model.Categoria,
                             model.Marca,
                             model.Articulo,
                             model.Precio,
                             ]),
            # Section('Consultas',
            #         self,
            #         Icon('tango/22x22/apps/system-users.png'),
            #         items = [
            #             ]),
            ]
        return sections

    def get_actions(self):
        act = action.OpenNewView(self.get_related_admin(model.Carrito))
        act.icon = Icon('tango/32x32/actions/list-add.png')
        return [act]
