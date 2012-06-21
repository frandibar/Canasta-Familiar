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

from camelot.admin.entity_admin import EntityAdmin
from camelot.view.filters import ComboBoxFilter
from camelot.view.controls.delegates import CurrencyDelegate

from camelot.model import metadata
__metadata__ = metadata

from sqlalchemy.sql import select, func, and_
from sqlalchemy.orm import mapper
from sqlalchemy import distinct
import datetime

from model import Establecimiento, Articulo, Precio, Marca, Compra, ArticuloCompra
import reports

class ListaDePrecios(object):
    class Admin(EntityAdmin):
        verbose_name = u"Lista de Precios"
        verbose_name_plural = u"Lista de Precios"
        list_display = ["articulo",
                        "establecimiento",
                        "fecha",
                        "precio",
                        ]
        list_actions = [reports.ReportePrecios()]
        list_action = None
        list_filter = [ComboBoxFilter("articulo"),
                       ComboBoxFilter("establecimiento"),
                       ]
        field_attributes = dict(precio = dict(delegate = CurrencyDelegate,
                                              prefix = "$"),
                                articulo = dict(name = u"Artículo"),
                                )

class CompraMensual(object):
    class Admin(EntityAdmin):
        verbose_name = u"Compra Mensual"
        verbose_name_plural = u"Compra Mensual"
        list_display = ["periodo",
                        "articulo",
                        "cantidad",
                        ]
        # list_actions = [reports.ReporteCompraMensual()]
        list_action = None
        list_filter = [ComboBoxFilter("periodo"),
                       ]
        field_attributes = dict(periodo = dict(name = u"Período"),
                                articulo = dict(name = u"Artículo"))

def compra_mensual():
    tbl_compra = Compra.mapper.mapped_table
    tbl_artcompra = ArticuloCompra.mapper.mapped_table
    tbl_articulo = Articulo.mapper.mapped_table
    tbl_marca = Marca.mapper.mapped_table

    # stmt = select([func.concat(func.year(tbl_compra.c.fecha), "-", format(func.month(tbl_compra.c.fecha), "02")).label("periodo"),
    stmt = select([func.concat(func.year(tbl_compra.c.fecha), "-", func.month(tbl_compra.c.fecha)).label("periodo"),
                   func.concat(tbl_articulo.c.descripcion, " ", tbl_marca.c.denominacion, " ", tbl_articulo.c.cantidad, " ", tbl_articulo.c.unidad_medida).label("articulo"),
                   func.sum(tbl_artcompra.c.cantidad).label("cantidad"),
                   ],
                  from_obj=tbl_compra.join(tbl_artcompra).join(tbl_articulo).join(tbl_marca),
                  group_by=[func.year(tbl_compra.c.fecha), func.month(tbl_compra.c.fecha), tbl_artcompra.c.articulo_id],
                  )
    return stmt.alias("compra_mensual")

def precio_actualizado():
    tbl_precio = Precio.mapper.mapped_table
    # fecha mas actualizada por articulo y establecimiento
    pre = select([tbl_precio.c.articulo_id,
                  func.max(tbl_precio.c.fecha).label("fecha"),
                  tbl_precio.c.establecimiento_id],
                 group_by=[tbl_precio.c.articulo_id, tbl_precio.c.establecimiento_id]
                 ).alias("pre")
    stmt = tbl_precio.select(and_(tbl_precio.c.fecha == pre.c.fecha,
                                  tbl_precio.c.articulo_id == pre.c.articulo_id,
                                  tbl_precio.c.establecimiento_id == pre.c.establecimiento_id))
    return stmt.alias("precio_actualizado")

def lista_de_precios():
    tbl_articulo = Articulo.mapper.mapped_table
    tbl_estab = Establecimiento.mapper.mapped_table
    tbl_marca = Marca.mapper.mapped_table
    pa = precio_actualizado()

    stmt = select([func.concat(tbl_articulo.c.descripcion, " ", tbl_marca.c.denominacion, " ", tbl_articulo.c.cantidad, " ", tbl_articulo.c.unidad_medida).label("articulo"),
                   func.concat(tbl_estab.c.denominacion, " ", tbl_estab.c.domicilio).label("establecimiento"),
                   pa.c.fecha,
                   pa.c.precio,
                   ],
                  from_obj=pa.join(tbl_articulo).join(tbl_marca).join(tbl_estab),
                  order_by=[func.concat(tbl_articulo.c.descripcion, " ", tbl_marca.c.denominacion), pa.c.precio]
                  )
    return stmt.alias("lista_de_precios")

def setup_compra_mensual():
    stmt = compra_mensual()
    mapper(CompraMensual, stmt, always_refresh=True,
           primary_key=[stmt.c.periodo,
                        stmt.c.articulo,
                        ])

def setup_lista_de_precios():
    stmt = lista_de_precios()
    mapper(ListaDePrecios, stmt, always_refresh=True, order_by=[stmt.c.articulo, stmt.c.precio],
           primary_key=[stmt.c.articulo,
                        stmt.c.establecimiento,
                        ])

def setup_views():
    setup_lista_de_precios()
    setup_compra_mensual()
