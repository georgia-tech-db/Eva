# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from enum import Enum


class LoggingLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class Logger:
    class __Logger:
        def __init__(self):

            # LOGGING CONFIGURATION
            self.LOG = logging.getLogger(__name__)
            LOG_handler = logging.StreamHandler()
            LOG_formatter = logging.Formatter(
                fmt='%(asctime)s [%(funcName)s:%(lineno)03d] %(levelname)-5s: %(message)s',
                datefmt='%m-%d-%Y %H:%M:%S'
            )
            LOG_handler.setFormatter(LOG_formatter)
            self.LOG.addHandler(LOG_handler)
            self.LOG.setLevel(logging.INFO)

        def __str__(self):
            return repr(self)

    instance = None

    def __init__(self):
        if not Logger.instance:
            Logger.instance = Logger.__Logger()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def log(self, string, level: LoggingLevel = LoggingLevel.DEBUG):

        if level == LoggingLevel.DEBUG:
            Logger.instance.LOG.debug(string)
        elif level == LoggingLevel.INFO:
            Logger.instance.LOG.info(string)
        elif level == LoggingLevel.WARNING:
            Logger.instance.LOG.warn(string)
        elif level == LoggingLevel.ERROR:
            Logger.instance.LOG.error(string)
        elif level == LoggingLevel.CRITICAL:
            Logger.instance.LOG.critical(string)
