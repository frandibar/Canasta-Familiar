# -*- coding: latin-1 -*-

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

from camelot.model import metadata

__metadata__ = metadata

from camelot.admin.action import Action
from camelot.view.action_steps import FlushSession, MessageBox
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.filters import ComboBoxFilter
from elixir import Entity, Field, ManyToOne, OneToMany, using_options
from sqlalchemy import Unicode, Date, Float, Integer, Boolean
from sqlalchemy.exc import IntegrityError, FlushError
from PyQt4.QtGui import QMessageBox
import camelot
import datetime

class Supermercado(Entity):
    using_options(tablename="supermercado", order_by=["denominacion"])
    denominacion = Field(Unicode(50), required=True)
    domicilio = Field(Unicode(100), required=True)

    def __unicode__(self):
        return "%s - %s" % (self.denominacion, self.domicilio)

    class Admin(EntityAdmin):
        list_display = ["denominacion", "domicilio"]

class Categoria(Entity):
    using_options(tablename="categoria", order_by=["descripcion"])
    descripcion = Field(Unicode(50), required=True)

    def __unicode__(self):
        return self.descripcion

    class Admin(EntityAdmin):
        list_display = ["descripcion"]

class Articulo(Entity):
    using_options(tablename="articulo", order_by=["descripcion"])
    categoria = ManyToOne("Categoria", required=True)
    descripcion = Field(Unicode(100), required=True)
    marca = ManyToOne("Marca", required=True)
    cantidad = Field(Float, default=1, required=True)
    unidad_medida = Field(Unicode(25))
    envase = Field(Unicode(25))
    foto = Field(camelot.types.Image(upload_to="fotos"))
    codigo_barras = Field(Unicode(25))  # unicode en vez de string porque sino no permite filtrado

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
                        "codigo_barras",
                        ]
        form_display = ["descripcion",
                        "marca",
                        "cantidad",
                        "unidad_medida",
                        "categoria",
                        "envase",
                        "codigo_barras",
                        "foto",
                        ]

class Marca(Entity):
    using_options(tablename="marca", order_by=["denominacion"])
    denominacion = Field(Unicode(30), unique=True)

    def __unicode__(self):
        return self.denominacion

    class Admin(EntityAdmin):
        list_display = ["denominacion"]

class Precio(Entity):
    using_options(tablename="precio")
    articulo = ManyToOne("Articulo", primary_key=True)
    fecha = Field(Date, primary_key=True, default=datetime.date.today)
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
    cantidad = Field(Float, default=1.0)

    def __unicode__(self):
        return self.articulo.descripcion

    class Admin(EntityAdmin):
        verbose_name = u"Artículo"
        list_display = ["articulo", "precio", "cantidad"]
        field_attributes = dict(precio = dict(prefix = '$'))
        form_size = (600,150)

        # esto es para que se refresque el campo total de carrito
        def get_depending_objects(self, obj):
            yield obj.carrito

class ImputarCarrito(Action):
    verbose_name = "Imputar"

    def model_run(self, model_context):
        # agregar estos campos a la tabla de pagos, solo si no existen.
        obj = model_context.get_object()
        error_occurred = False
        if obj.imputado:
            yield MessageBox("El carrito ya ha sido imputado.",
                             icon=QMessageBox.Warning,
                             title="Imputar carrito",
                             standard_buttons=QMessageBox.Ok)
            return
        for art in obj.articulos:
            try:
                row = Precio()
                row.articulo = art.articulo
                row.precio = art.precio
                row.fecha = obj.fecha
                row.supermercado = obj.supermercado
                Precio.query.session.flush()
            except FlushError, e:
                error_occurred = True
                yield MessageBox("Se ha producido un error de flush:\n\n%s" % e,
                                 icon=QMessageBox.Critical,
                                 title="Imputar carrito",
                                 standard_buttons=QMessageBox.Ok)
                return
            except IntegrityError, e:
                error_occurred = True
                yield MessageBox(u"Se ha producido un error, quiza el siguiente artículo se encuentra repetido:\n\n%s" % e,
                                 icon=QMessageBox.Critical,
                                 title="Imputar carrito",
                                 standard_buttons=QMessageBox.Ok)
                return
            except Exception, e:
                error_occurred = True
                yield MessageBox("Se ha producido un error:\n\n%s" % e,
                                 icon=QMessageBox.Critical,
                                 title="Imputar carrito",
                                 standard_buttons=QMessageBox.Ok)
                return
        obj.imputado = not error_occurred
        yield FlushSession(model_context.session)
        # try:
        #     yield FlushSession(model_context.session)
        # except Exeption, e:
        #         yield MessageBox("Se ha producido un error:\n\n%s" % e,
        #                          icon=QMessageBox.Critical,
        #                          title="Imputar carrito",
        #                          standard_buttons=QMessageBox.Ok)
        #         return


class Carrito(Entity):
    using_options(tablename="carrito")
    supermercado = ManyToOne("Supermercado", primary_key=True)
    fecha = Field(Date, default=datetime.date.today, primary_key=True)
    articulos = OneToMany("ArticuloCarrito")
    imputado = Field(Boolean, default=False)

    def __unicode__(self):
        return "%s %s" % (self.fecha, self.supermercado.denominacion)

    # No uso ColumnProperty para que se refresque automaticamente cuando se modifican los totales
    @property
    def total(self):
        total = 0
        for i in self.articulos:
            total += i.cantidad * i.precio
        return total

    class Admin(EntityAdmin):
        form_display = ["supermercado",
                        "fecha",
                        "articulos",
                        "total"
                        ]
        list_display = ["supermercado", "fecha", "imputado"]
        form_actions = [ImputarCarrito()]
        field_attributes = dict(imputado = dict(editable = True),  # TODO cambiar a false en produccion
                                total = dict(delegate = CurrencyDelegate,
                                             prefix = '$',
                                             editable = False),
                                )# articulos = dict(create_inline = True))
        form_size = (800,600)
