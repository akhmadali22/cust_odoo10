# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import re
import uuid
from urlparse import urljoin
from collections import Counter, OrderedDict
from itertools import product

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.website.models.website import slug
_logger = logging.getLogger(__name__)

class SurveyLabel(models.Model):
    """ A suggested answer for a question """

    _inherit = 'survey.label'

    sub_page_id = fields.Many2one('survey.page', string='Jadikan Pertanyaan Lanjutan')

class SurveyUserInput(models.Model):
    """ Metadata for a set of one user's answers to a particular survey """

    _inherit = "survey.user_input"

    sub_page_id = fields.Many2one('survey.page')

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    sub_page_id = fields.Many2one('survey.page')

    def _get_default_sub_page_id(self, value_suggested):
        if value_suggested:
            label = self.env['survey.label'].search([('id', '=', int(value_suggested))], limit=1)
            if label:
                return label.sub_page_id.id

    @api.model
    def create(self, vals):
        value_suggested = vals.get('value_suggested')
        sub_page_id = self._get_default_sub_page_id(value_suggested)
        if value_suggested:
            vals.update({
                'quizz_mark': self._get_mark(value_suggested),
                'sub_page_id': sub_page_id
            })
        return super(SurveyUserInputLine, self).create(vals)

    @api.multi
    def write(self, vals):
        value_suggested = vals.get('value_suggested')
        sub_page_id = self._get_default_sub_page_id(value_suggested)
        if value_suggested:
            vals.update({
                'quizz_mark': self._get_mark(value_suggested),
                'sub_page_id': sub_page_id
            })
        return super(SurveyUserInputLine, self).write(vals)

    def update_sub_page_user_input(self, user_input_id, sub_page):
        user_input = self.env['survey.user_input'].search([('id', '=', user_input_id)], limit=1)
        if sub_page:
            sub_page_id = self.env['survey.label'].search([('id', '=', sub_page)], limit=1).sub_page_id.id
            user_input.write({'sub_page_id': sub_page_id})
        
    @api.model
    def save_line_simple_choice(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        old_uil.sudo().unlink()

        if answer_tag in post and post[answer_tag].strip():
            vals.update({'answer_type': 'suggestion', 'value_suggested': post[answer_tag]})
            self.update_sub_page_user_input(user_input_id, post[answer_tag])

        else:
            vals.update({'answer_type': None, 'skipped': True})

        # '-1' indicates 'comment count as an answer' so do not need to record it
        if post.get(answer_tag) and post.get(answer_tag) != '-1':
            self.create(vals)

        comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
        if comment_answer:
            vals.update({'answer_type': 'text', 'value_text': comment_answer, 'skipped': False, 'value_suggested': False})
            self.create(vals)
            
        return True