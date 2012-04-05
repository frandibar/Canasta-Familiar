
from camelot.model import metadata

__metadata__ = metadata

from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.filters import ComboBoxFilter
from elixir import Entity, Field, ManyToOne, OneToMany, using_options
from sqlalchemy import Unicode, Date, Float, Integer, String
import camelot

class Supermercado(Entity):
    using_options(tablename="supermercado")
    denominacion = Field(Unicode(50), required=True)
    domicilio = Field(Unicode(100), required=True)

    def __unicode__(self):
        return "%s (%s)" % (self.denominacion, self.domicilio)

    class Admin(EntityAdmin):
        list_display = ["denominacion", "domicilio"]

class Categoria(Entity):
    using_options(tablename="categoria")
    descripcion = Field(Unicode(50), required=True)

    def __unicode__(self):
        return self.descripcion

    class Admin(EntityAdmin):
        list_display = ["descripcion"]

class Articulo(Entity):
    using_options(tablename="articulo")
    categoria = ManyToOne("Categoria", required=True)
    descripcion = Field(Unicode(100), required=True)
    marca = ManyToOne("Marca", required=True)
    cantidad = Field(Float, default=1, required=True)
    unidad_medida = Field(String(25))
    envase = Field(String(25))
    foto = Field(camelot.types.Image(upload_to="fotos"))
    codigo_barras = Field(String(25))

    def __unicode__(self):
        envase = self.envase if self.envase else ""
        return "%s %s %s %s %s" % (self.descripcion, self.marca, self.cantidad, self.unidad_medida, envase)

    class Admin(EntityAdmin):
        search_all_fields = False
        list_search = [#"descripcion",
                       #"marca",
                       "codigo_barras",
                       ]
        list_display = ["descripcion",
                        "marca",
                        "cantidad",
                        "unidad_medida",
                        "categoria",
                        "envase",
                        "foto",
                        "codigo_barras",
                        ]

class Marca(Entity):
    using_options(tablename="marca")
    denominacion = Field(Unicode(30), unique=True)

    def __unicode__(self):
        return self.denominacion

    class Admin(EntityAdmin):
        list_display = ["denominacion"]

class Precio(Entity):
    using_options(tablename="precio")
    articulo = ManyToOne("Articulo", required=True)
    precio = Field(Float)
    fecha = Field(Date, required=True)
    supermercado = ManyToOne("Supermercado", required=True)

    class Admin(EntityAdmin):
        list_display = ["articulo",
                        "precio",
                        "fecha",
                        "supermercado",
                        ]
        search_all_fields = True
        # expanded_list_search = ["articulo",
        #                         "fecha",
        #                         "supermercado.denominacion",
        #                         ]
        expanded_list_search = ["articulo",
                                "fecha",
                                "precio",
                                "supermercado.denominacion",
                                ]
        list_filter = [ComboBoxFilter("supermercado.denominacion"),
                       ComboBoxFilter("fecha"),
                       ]

class ArticuloCarrito(Entity):
    using_options(tablename="articulo_carrito")
    carrito = ManyToOne("Carrito", primary_key=True)
    articulo = ManyToOne("Articulo", primary_key=True)
    precio = Field(Float)

    def __unicode__(self):
        return self.articulo.descripcion

    class Admin(EntityAdmin):
        list_display = ["articulo", "precio"]


class ImputarCarrito(Action):
    from camelot.view.action_steps import MessageBox
    def model_run(self, model_context):
        pass
        # obj = model_context.get_object()
        # for i in obj.articulos:
        #     MessageBox(i)

class Carrito(Entity):
    using_options(tablename="carrito")
    supermercado = ManyToOne("Supermercado", primary_key=True)
    fecha = Field(Date, primary_key=True)
    articulos = OneToMany("ArticuloCarrito")

    def __unicode__(self):
        return "%s %s" % (self.fecha, self.supermercado.denominacion)

    class Admin(EntityAdmin):
        form_display = ["supermercado",
                        "fecha",
                        "articulos"
                        ]
        list_display = ["supermercado", "fecha"]
        form_actions = [ImputarCarrito]

