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

import datetime
import os
from collections import namedtuple, OrderedDict

from jinja import Environment, PackageLoader
from pkg_resources import resource_filename
from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.action_steps import PrintHtml #, WordJinjaTemplate
from camelot.view.art import Icon
from PyQt4 import QtGui

import model
import settings

def spacer(field, width=10):
    if not field:
        return "_" * width
    return field

def fix_decimal_sep(str_num):
    # warning: forzando separador decimal a ","
    tmp = str_num.replace(".", ";")
    tmp = tmp.replace(",", ".")
    tmp = tmp.replace(";", ",")
    return tmp

def money_fmt(value, dec=1):
    # incluir separador de miles y signo de pesos
    fmtstring = "{:,.%df}" % dec
    ret = "$ %s" % fmtstring.format(value)
    return fix_decimal_sep(ret)

class ReportePrecios(Action):
    verbose_name = ""
    icon = Icon("tango/16x16/actions/document-print.png")

    def _build_context(self, model_context):
        obj = model_context.get_collection()
        context = {
            "precios": obj,
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader("canasta", "templates")
        env = Environment(loader=fileloader)
        t = env.get_template("precios.html")
        yield PrintHtml(t.render(context))

