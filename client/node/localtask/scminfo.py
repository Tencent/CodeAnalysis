# -*- encoding: utf-8 -*-
"""
scm
"""
import logging

logger = logging.getLogger(__name__)


class ScmInfo(object):
    def __init__(self):
        self.repo_url = None
        self.scm_url = None
        self.scm_type = None
        self.scm_revision = None
        self.scm_time = None
        self.branch = None


class ScmAuthInfo(object):
    def __init__(self):
        self.username = ""
        self.password = ""
        self.ssh_file = None
