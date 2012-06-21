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
from camelot.view.controls.delegates import CurrencyDelegate
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.filters import ComboBoxFilter
from elixir import Entity, Field, ManyToOne, OneToMany, using_options
from elixir.properties import ColumnProperty
from sqlalchemy import Unicode, Date, Float, Integer, Boolean
from sqlalchemy import sql, and_
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, FlushError
from PyQt4.QtGui import QMessageBox
import camelot
import datetime

class Cadena(Entity):
    using_options(tablename="cadena")
    denominacion = Field(Unicode(50), required=True)

    def __unicode__(self):
        return "%s" % (self.denominacion)

    class Admin(EntityAdmin):
        list_display = ["denominacion"]
        delete_mode = "on_confirm"
        field_attributes = dict(denominacion = dict(name = u"Denominaci�n"))

class Establecimiento(Entity):
    using_options(tablename="establecimiento", order_by=["denominacion"])
    cadena = ManyToOne("Cadena")# TODO, required=True)
    denominacion = Field(Unicode(50), required=True)
    domicilio = Field(Unicode(100), required=True)

    def __unicode__(self):
        return "%s - %s" % (self.denominacion, self.domicilio)

    class Admin(EntityAdmin):
        list_display = ["cadena", "denominacion", "domicilio"]
        delete_mode = "on_confirm"
        field_attributes = dict(denominacion = dict(name = u"Denominaci�n"))

class Categoria(Entity):
    using_options(tablename="categoria", order_by=["descripcion"])
    descripcion = Field(Unicode(50), required=True)

    def __unicode__(self):
        return self.descripcion

    class Admin(EntityAdmin):
        verbose_name = u"Categor�a"
        verbose_name_plural = u"Categor�as"
        list_display = ["descripcion"]
        delete_mode = "on_confirm"
        field_attributes = dict(descripcion = dict(name = u"Descripci�n"))

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
        if self.marca.denominacion != "sin_marca":
            return "%s %s %s %s %s" % (self.descripcion, self.marca, self.cantidad, self.unidad_medida, envase)
        else:
            return "%s %s %s %s" % (self.descripcion, self.cantidad, self.unidad_medida, envase)


    class Admin(EntityAdmin):
        verbose_name = u"Art�culo"
        verbose_name_plural = u"Art�culos"
        search_all_fields = False
        list_search = ["descripcion",
                       "codigo_barras",
                       ]
        search_all_fields = True
        # TODO en vez de este filtro hacer andar el expanded search
        list_filter = [ComboBoxFilter("marca.denominacion")]
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
        delete_mode = "on_confirm"
        field_attributes = dict(articulo = dict(name = u"Art�culo"),
                                categoria = dict(name = u"Categor�a"),
                                codigo_barras = dict(name = u"C�digo de barras"),
                                unidad_medida = dict(name = "Unidad de medida"),
                                descripcion = dict(name = u"Descripci�n"))

class Marca(Entity):
    using_options(tablename="marca", order_by=["denominacion"])
    denominacion = Field(Unicode(30), unique=True)

    def __unicode__(self):
        return self.denominacion

    class Admin(EntityAdmin):
        list_display = ["denominacion"]
        delete_mode = "on_confirm"
        field_attributes = dict(denominacion = dict(name = u"Denominaci�n"))

class Precio(Entity):
    using_options(tablename="precio")
    articulo = ManyToOne("Articulo", primary_key=True)
    fecha = Field(Date, primary_key=True, default=datetime.date.today)
    establecimiento = ManyToOne("Establecimiento", primary_key=True)
    precio = Field(Float)

    class Admin(EntityAdmin):
        list_display = ["articulo",
                        "precio",
                        "fecha",
                        "establecimiento",
                        ]
        search_all_fields = True
        # expanded_list_search = ["articulo",
        #                         "fecha",
        #                         "establecimiento.denominacion",
        #                         ]
        list_search = ["articulo.descripcion"]
        # TODO no anda
        expanded_list_search = ["articulo.descripcion",
                                "fecha",
                                "precio",
                                "establecimiento.denominacion",
                                ]
        list_filter = [ComboBoxFilter("establecimiento.denominacion"),
                       ComboBoxFilter("fecha"),
                       ]
        field_attributes = dict(precio = dict(prefix = "$"),
                                articulo = dict(name = u"Art�culo"))
        delete_mode = "on_confirm"

class ArticuloCompra(Entity):
    using_options(tablename="articulo_compra")
    compra = ManyToOne("Compra", primary_key=True, ondelete="cascade", onupdate="cascade")
    articulo = ManyToOne("Articulo", primary_key=True, ondelete="cascade", onupdate="cascade")
    precio = Field(Float)
    cantidad = Field(Float, default=1.0)

    # este lo uso para poder ordenar, porque el ordenamiento por articulo no funciona como espero
    @property
    def articulo_desc(self):
        if self.articulo:
            return self.articulo.descripcion
        return ""

    # @property
    # def etiqueta(self):
    #     return self.articulo.id

    # @ColumnProperty
    # def etiqueta(self):
    #     tbl_art_ticket = ArticuloTicket.mapper.mapped_table
    #     tbl_ticket = Ticket.mapper.mapped_table
    #     tbl_cadena = Cadena.mapper.mapped_table
    #     tbl_establec = Establecimiento.mapper.mapped_table
    #     return sql.select([tbl_art_ticket.c.etiqueta],
    #                       from_obj = [tbl_art_ticket, tbl_ticket, tbl_cadena, tbl_establec],
    #                       whereclause = and_(tbl_art_ticket.c.articulo_id == self.articulo.id,
    #                                          tbl_art_ticket.c.ticket_cadena_id == tbl_ticket.c.cadena_id,
    #                                          tbl_ticket.c.cadena_id == tbl_cadena.c.id,
    #                                          tbl_cadena.c.id == tbl_establec.c.cadena_id))

        # return sql.select([tbl_art_ticket.c.etiqueta],
        #                   from_obj = tbl_art_ticket.join(tbl_ticket).join(tbl_cadena).join(tbl_establec),
        #                   whereclause = tbl_art_ticket.c.articulo_id == self.articulo.id)

    def __unicode__(self):
        return self.articulo.descripcion

    class Admin(EntityAdmin):
        verbose_name = u"Art�culo"
        form_display = ["articulo", "precio", "cantidad"]
        # list_display = ["articulo", "precio", "cantidad", "etiqueta", "articulo_desc"]
        list_display = ["articulo", "precio", "cantidad", "articulo_desc"]
        field_attributes = dict(precio = dict(prefix = '$'),
                                articulo = dict(name = u"Art�culo"),
                                articulo_desc = dict(name = u"Art."))
        form_size = (750,250)

        # # esto es para que se refresque el campo total de compra
        # def get_depending_objects(self, obj):
        #     yield obj.compra

class ImputarCompra(Action):
    verbose_name = "Imputar"

    def model_run(self, model_context):
        # agregar estos campos a la tabla de pagos, solo si no existen.
        obj = model_context.get_object()
        if obj.imputado:
            yield MessageBox("La compra ya ha sido imputada.",
                             icon=QMessageBox.Warning,
                             title="Imputar compra",
                             standard_buttons=QMessageBox.Ok)
            return
        Precio.query.session.begin()
        try:
            for art in obj.articulos:
                row = Precio()
                row.articulo = art.articulo
                row.precio = art.precio
                row.fecha = obj.fecha
                row.establecimiento = obj.establecimiento
                yield FlushSession(Precio.query.session)
        except FlushError, e:
            Precio.query.session.rollback()
            yield MessageBox("Se ha producido un error de flush:\n\n%s" % e,
                             icon=QMessageBox.Critical,
                             title="Imputar compra",
                             standard_buttons=QMessageBox.Ok)
            yield UpdateObject(model_context.session)
            return
        except IntegrityError, e:
            Precio.query.session.rollback()
            yield MessageBox(u"Se ha producido un error, quiza el siguiente art�culo se encuentra repetido:\n\n%s" % e,
                             icon=QMessageBox.Critical,
                             title="Imputar compra",
                             standard_buttons=QMessageBox.Ok)
            yield UpdateObject(model_context.session)
            return
        except Exception, e:
            Precio.query.session.rollback()
            yield MessageBox("Se ha producido un error:\n\n%s" % e,
                             icon=QMessageBox.Critical,
                             title="Imputar compra",
                             standard_buttons=QMessageBox.Ok)
            yield UpdateObject(model_context.session)
            return
        Precio.query.session.commit()
        obj.imputado = True
        yield FlushSession(model_context.session)
        yield camelot.view.action_steps.CloseView()


class Compra(Entity):
    using_options(tablename="compra", order_by=["fecha"])
    establecimiento = ManyToOne("Establecimiento", primary_key=True)
    fecha = Field(Date, default=datetime.date.today, primary_key=True)
    articulos = OneToMany("ArticuloCompra")
    imputado = Field(Boolean, default=False)

    def __unicode__(self):
        return "%s %s" % (self.fecha, self.establecimiento.denominacion)

    # No uso ColumnProperty para que se refresque automaticamente cuando se modifican los totales
    @property
    def total(self):
        total = 0
        for i in self.articulos:
            total += i.cantidad * i.precio
        return total

    class Admin(EntityAdmin):
        form_display = ["establecimiento",
                        "fecha",
                        "articulos",
                        "total"
                        ]
        list_display = ["establecimiento", "fecha", "imputado"]
        form_actions = [ImputarCompra()]
        field_attributes = dict(imputado = dict(editable = True),  # TODO cambiar a false en produccion
                                total = dict(delegate = CurrencyDelegate,
                                             prefix = '$',
                                             editable = False),
                                articulos = dict(name = u"Art�culos",
                                                 create_inline = True))
        form_size = (1050,700)
        delete_mode = "on_confirm"

        def get_query(self):
            """Redefino para devolver ordenado por fecha desc"""
            return EntityAdmin.get_query(self).order_by(desc('fecha'))

class Ticket(Entity):
    using_options(tablename="ticket")
    cadena = ManyToOne("Cadena", primary_key=True)
    articulos = OneToMany("ArticuloTicket")

    def __unicode__(self):
        return "%s" % (self.cadena.denominacion)

    class Admin(EntityAdmin):
        form_display = ["cadena", "articulos"]
        list_display = ["cadena"]
        delete_mode = "on_confirm"
        form_size = (750,600)
        field_attributes = dict(articulos = dict(name = u"Art�culos"))

class ArticuloTicket(Entity):
    using_options(tablename="articulo_ticket")
    ticket = ManyToOne("Ticket", primary_key=True, ondelete="cascade", onupdate="cascade")
    articulo = ManyToOne("Articulo", primary_key=True, ondelete="cascade", onupdate="cascade")
    etiqueta = Field(Unicode(50), required=True)

    def __unicode__(self):
        return "%s" % (self.etiqueta)

    # este lo uso para poder ordenar, porque el ordenamiento por articulo no funciona como espero
    @property
    def articulo_desc(self):
        if self.articulo:
            return self.articulo.descripcion
        return ""

    class Admin(EntityAdmin):
        form_display = ["articulo", "etiqueta"]
        list_display = ["articulo", "etiqueta", "articulo_desc"]
        delete_mode = "on_confirm"
        form_size = (750,250)
        field_attributes = dict(articulo = dict(name = u"Art�culo"),
                                articulo_desc = dict(name = "Art."))
