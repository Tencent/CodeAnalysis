#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


class RuleParamer(object):
    @staticmethod
    def java_param_formart(rule_list):
        rules = []
        for rule_info in rule_list:
            rule_item = {"name": rule_info["name"]}
            params = rule_info.get("params", "").splitlines()
            for param in params:
                temp_str = param.lower().replace(" ", "")
                param_name = temp_str.split("=")[0]
                rule_item[param_name] = temp_str[len(param_name) + 1 :]

            rules.append(rule_item)
        return rules


if __name__ == "__main__":
    pass
