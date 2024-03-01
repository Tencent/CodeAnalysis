# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""Analyse Server Ticket
"""

from time import time
from hashlib import sha256

from django.conf import settings

from util.cdcrypto import encrypt


class MainServerTicket(object):
    """MainServer票据
    """
    @classmethod
    def generate_ticket(cls):
        """ticket生成算法
        :return: str
        """
        api_ticket_token = settings.API_TICKET_TOKEN
        ticket_timestamp = int(time())
        ticket_string = "%s,%s,%s" % (ticket_timestamp, api_ticket_token, ticket_timestamp)
        ticket_signature = sha256(ticket_string.encode("utf-8")).hexdigest().upper()
        # 使用 $#$ 分隔符
        ticket_data = "%s$#$%s" % (ticket_timestamp, ticket_signature)
        ticket = encrypt(ticket_data, settings.API_TICKET_SALT)
        return ticket
