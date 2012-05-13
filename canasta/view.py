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

from model import Establecimiento, Articulo, Precio, Marca
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
                                )

class PreciosComparados(object):
    class Admin(EntityAdmin):
        list_display = []

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

def precios_comparados():
    # -- para cada articulo, la diferencia porcentual entre el menor y mayor precio, entre todos los establecimientos
    # create view precio_comparado as
    # select distinct articulo_id, count(establecimiento_id), min(precio), max(precio), (max(precio)/min(precio)-1)*100 as dif_porcent
    # from precios_x_establecimiento
    # group by articulo_id;
    pxs = precios_x_establecimiento()
    stmt = select([pxs.c.articulo_id,
                   func.count(pxs.c.establecimiento_id),
                   func.min(pxs.c.precio).label("precio_min"),
                   func.max(pxs.c.precio).label("precio_max"),
                   # TODO diferencia porcentual
                   ],
                  from_obj=pxs,
                  group_by=[pxs.c.articulo_id],
                  ).distinct()
    return stmt.alias("precios_comparados")

def precios_x_establecimiento():
    # -- para cada articulo y establecimiento, el max precio de los ultimos 6 meses
    # alter view precios_x_establecimiento as
    # select articulo_id, establecimiento_id, max(precio) as precio
    # from precio
    # where fecha > date_add(now(), interval -6 month)
    # group by articulo_id, establecimiento_id;

    tbl_precio = Precio.mapper.mapped_table

    stmt = select([tbl_precio.c.articulo_id,
                   tbl_precio.c.establecimiento_id,
                   func.max(tbl_precio.c.precio).label("precio")
                   ],
                  from_obj=tbl_precio,
                  whereclause=tbl_precio.c.fecha > datetime.date.today() - datetime.timedelta(weeks=24),
                  group_by=[tbl_precio.c.articulo_id, tbl_precio.c.establecimiento_id],
                  )
    return stmt.alias("precios_x_establecimiento")


def setup_precios_comparados():
    stmt = precios_comparados()
    mapper(PreciosComparados, stmt, always_refresh=True)
           # primary_key=[stmt.c.beneficiaria_id,
           #              stmt.c.nro_credito,
                        # ])

def setup_lista_de_precios():
    stmt = lista_de_precios()
    mapper(ListaDePrecios, stmt, always_refresh=True, order_by=[stmt.c.articulo, stmt.c.precio],
           primary_key=[stmt.c.articulo,
                        stmt.c.establecimiento,
                        ])

def setup_views():
    # setup_precios_comparados()
    setup_lista_de_precios()
