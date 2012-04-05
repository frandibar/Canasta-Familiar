
from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section

import model

class MyApplicationAdmin(ApplicationAdmin):

    name = 'Canasta Familiar'
    # application_url = 'http://www.python-camelot.com'
    help_url = 'http://www.python-camelot.com/docs.html'
    author = 'Francisco Dibar'
    # domain = 'mydomain.com'

    def get_sections(self):
        from camelot.model.memento import Memento
        from camelot.model.i18n import Translation
        sections = [Section('Entidades',
                            self,
                            Icon('tango/22x22/apps/system-users.png'),
                            items = [model.Supermercado,
                                     model.Categoria,
                                     model.Marca,
                                     model.Articulo,
                                     model.Precio,
                                     model.Carrito,
                                     ]),
                    # Section('Consultas',
                    #         self,
                    #         Icon('tango/22x22/apps/system-users.png'),
                    #         items = [
                    #             ]),
                    ]
        return sections

