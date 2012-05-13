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

import logging
import os

logger = logging.getLogger('settings')

# media root needs to be an absolute path for the file open functions
# to function correctly
CAMELOT_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# backup root is the directory where the default backups are stored
CAMELOT_BACKUP_ROOT = os.path.join(os.path.dirname(__file__), 'backup')

# default extension for backup files
CAMELOT_BACKUP_EXTENSION = 'db'

# template used to create and find default backups
CAMELOT_BACKUP_FILENAME_TEMPLATE = 'default-backup-%(text)s.' + CAMELOT_BACKUP_EXTENSION


def ENGINE():
    """This function should return a connection to the database"""
    from sqlalchemy import create_engine
    return create_engine('mysql://root:root@localhost:3306/canasta',
                         encoding='latin1',
                         convert_unicode=True,
                         echo=False)

def setup_model():
    """This function will be called at application startup, it is used to setup
    the model"""
    import camelot.model
    from elixir import setup_all
    import canasta.model
    import canasta.view
    setup_all(create_tables=True)
    canasta.view.setup_views()

