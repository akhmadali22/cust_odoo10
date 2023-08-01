# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SurveyGenerator(models.TransientModel):
    _name = 'survey.generator'
    _description = 'Survey Generator'

    template = fields.One2many('survey.template', 'survey_generator_id', 'Template')

    @api.multi
    def generate_survey(self):
        context = self.env.context
        survey_id = context and context.get('active_ids', [])
        survey = self.env['survey.survey'].search([('id', 'in', survey_id)])
        new_survey = self.env['survey.survey']
        for data in self.template:
            new_survey = survey.copy()
            new_survey.write({'title': data.name+' '+survey.title})

class SurveyTemplate(models.TransientModel):
    _name = 'survey.template'
    _description = 'Survey Template'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name', required=True)
    survey_generator_id = fields.Many2one('survey.generator', 'Survey Generator')