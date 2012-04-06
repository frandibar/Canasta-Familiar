# -*- coding: latin-1 -*-

from camelot.model import metadata

__metadata__ = metadata

from camelot.admin.action import Action
from camelot.view.action_steps import FlushSession
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.filters import ComboBoxFilter
from elixir import Entity, Field, ManyToOne, OneToMany, using_options
from sqlalchemy import Unicode, Date, Float, Integer, String, Boolean
import camelot
import datetime

class Supermercado(Entity):
    using_options(tablename="supermercado")
    denominacion = Field(Unicode(50), required=True)
    domicilio = Field(Unicode(100), required=True)

    def __unicode__(self):
        return "%s - %s" % (self.denominacion, self.domicilio)

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
    codigo_barras = Field(Unicode(25))

    def __unicode__(self):
        envase = self.envase if self.envase else ""
        return "%s %s %s %s %s" % (self.descripcion, self.marca, self.cantidad, self.unidad_medida, envase)

    class Admin(EntityAdmin):
        search_all_fields = False
        list_search = ["descripcion",
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
    articulo = ManyToOne("Articulo", primary_key=True)
    fecha = Field(Date, primary_key=True)
    supermercado = ManyToOne("Supermercado", primary_key=True)
    precio = Field(Float)

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
        field_attributes = dict(precio = dict(prefix = "$"))

class ArticuloCarrito(Entity):
    using_options(tablename="articulo_carrito")
    carrito = ManyToOne("Carrito", primary_key=True, ondelete="cascade", onupdate="cascade")
    articulo = ManyToOne("Articulo", primary_key=True, ondelete="cascade", onupdate="cascade")
    precio = Field(Float)

    def __unicode__(self):
        return self.articulo.descripcion

    class Admin(EntityAdmin):
        verbose_name = u"Artículo"
        list_display = ["articulo", "precio"]
        field_attributes = dict(precio = dict(prefix = '$'))
        form_size = (600,150)


class ImputarCarrito(Action):
    verbose_name = "Imputar"

    def model_run(self, model_context):
        # agregar estos campos a la tabla de pagos, solo si no existen.
        obj = model_context.get_object()
        if obj.imputado:
            # TODO show messagebox
            print "Ya fue imputado!"
            return
        for art in obj.articulos:
            row = Precio()
            row.articulo = art.articulo
            row.precio = art.precio
            row.fecha = obj.fecha
            row.supermercado = obj.supermercado
            Precio.query.session.flush()
        obj.imputado = True
        yield FlushSession(model_context.session)

class Carrito(Entity):
    using_options(tablename="carrito")
    supermercado = ManyToOne("Supermercado", primary_key=True)
    fecha = Field(Date, default=datetime.date.today, primary_key=True)
    articulos = OneToMany("ArticuloCarrito")
    imputado = Field(Boolean, default=False)

    def __unicode__(self):
        return "%s %s" % (self.fecha, self.supermercado.denominacion)

    class Admin(EntityAdmin):
        form_display = ["supermercado",
                        "fecha",
                        "articulos"
                        ]
        list_display = ["supermercado", "fecha", "imputado"]
        form_actions = [ImputarCarrito()]
        field_attributes = dict(imputado = dict(editable = False))
        form_size = (800,600)
