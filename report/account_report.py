# -*- coding: utf-8 -*-
from odoo import models, api
import logging

class AccountReportLine(models.Model):
    _inherit = 'account.report.line'

    def _expand_groupby(self, line_dict_id, groupby, options, offset=0, limit=None, load_one_more=False, unfold_all_batch_data=None):
        res = super()._expand_groupby(line_dict_id, groupby, options, offset=0, limit=None, load_one_more=False, unfold_all_batch_data=None)
        for partner_lines in res:
            if partner_lines['caret_options'] == 'account.move.line':
                display_name = partner_lines['name']
                if "(" in display_name:
                    extracted_ref = display_name[display_name.find("(") + 1:display_name.find(")")]
                    partner_lines['name'] = extracted_ref
        return res