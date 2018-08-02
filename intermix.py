# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2018 Intermix Software, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals

import base64
from datetime import datetime
import inspect
import json
import logging
import re
import traceback

logger = logging.getLogger(__name__)

__PLUGIN_ID__ = 'intermix-python-plugin'
__VERSION__ = '0.7'
INTERMIX_RE = re.compile(r"(\s*/\* INTERMIX_ID.*?\*/)")


def annotate(sql, app, app_ver, dag, task, user='', meta='', override=True):
    # type: (basestring, basestring, basestring, basestring, basestring, basestring, dict, bool) -> basestring
    """
        The main annotation function. Returns `sql` annotated with the Intermix annotation format.

        :param sql: the pre-annotation SQL query string
        :param app: the name of your app
        :param app_ver: the version running (can also be a deployment tag or git commit hash)
        :param dag: short for directed acyclic graph, or a category/grouping of associated tasks
        :param task: the individual task that this query is performing
        :param user: (optional) the user running this query
        :param meta: (optional) additional values, must be a dictionary
        :param override: Whether to override an existing Intermix annotation of this SQL
        :return: annotated sql
    """
    try:
        map(json.dumps, [app, app_ver, dag, task, user, meta])
    except TypeError:
        logger.warn("Cannot JSON serialize app, app_ver, dag, task, user, or meta. Not annotating.")
        return sql
    except:
        logger.warn("Non-serialization error. Not annotating.")
        return sql

    if meta and not isinstance(meta, dict):
        logger.warn("meta must be a dictionary. Not annotating.")
        return sql

    # We want to avoid mutable parameter types, so we set meta to be the real default (a dictionary) here.
    if not meta:
        meta = {}

    try:
        the_file, the_module, the_class, the_function, the_linenumber = inspector()
        blob = {'format': 'intermix', 'version': '1', 'plugin': __PLUGIN_ID__, 'plugin_ver': __VERSION__, 'app': app,
                'user': user, 'app_ver': app_ver, 'dag': dag, 'task': task, 'at': datetime.utcnow().isoformat() + 'Z',
                'file': the_file, 'module': the_module, 'classname': the_class, 'function': the_function,
                'linenumber': the_linenumber, 'meta': meta}

        # See if there is already an Intermix annotation for this query
        intermix_annotation_match = re.search(INTERMIX_RE, sql)
        if intermix_annotation_match:
            if not override:
                logger.info("Override is False so leaving existing Intermix annotation intact.")
                return sql
            sql = re.sub(INTERMIX_RE, '', sql)

        # Explicitly encode the JSON string for Python 2/3 compatibility
        annotation = "/* INTERMIX_ID: {} */ ".format(base64.b64encode(json.dumps(blob).encode()).decode())
        sql = "{}{}".format(annotation, sql)

    except:
        logger.warn(traceback.format_exc())

    return sql


def inspector():
    # type: () -> (basestring, basestring, basestring, basestring, basestring)
    """ Stack inspector to obtain runtime metadata for annotation """

    the_file = ''
    the_module = '__main__'
    the_class = ''
    the_function = ''
    the_linenumber = ''

    try:
        previous_frame = inspect.currentframe().f_back.f_back
        try:
            the_file, the_linenumber, the_function, lines, index = inspect.getframeinfo(previous_frame)
            the_linenumber = str(the_linenumber)
        finally:
            # Keeping references to frame objects can create reference cycles, so we make removal deterministic
            del previous_frame

        stack = inspect.stack()
        try:
            the_class = stack[2][0].f_locals["self"].__class__
        except KeyError:
            try:
                the_class = stack[2][0].f_locals["cls"]
            except KeyError:
                pass

        if the_class:
            the_module = the_class.__module__
            the_class = the_class.__name__

    except:
        the_module = '<error>'
        logger.warn(traceback.format_exc())

    return the_file, the_module, the_class, the_function, the_linenumber
