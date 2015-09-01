#############################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 OpenERP S.A. (<http://openerp.com>).
#
#    Copyright (C) 2011-2015 Nevpro Business Solutions Pvt Ltd. (<http://www.nevpro.co.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################################

{
	'name': 'Restrict Multiple Sign in for Same User',
	'version': '1.0',
	'category': 'Tools',
	'sequence': 999,
	'summary': 'Restrict Multiple Sign in for Same User in Odoo.',
	'description': """
Restrict Multiple Sign in for Same User
=======================================

Module to Restrict Multiple Sign in for Same User in OpenERP v7.""",
	'author': 'Nevpro Business Solutions Pvt Ltd.',
	'website': 'http://www.nevpro.co.in',
	'depends': ['web','base'],
	'data': [
		'scheduler.xml',
		],
	'demo_xml': [],
	'css': [],
	'js': [
		'static/src/js/custom.js',
	],
	'xml': [],
	'installable': True,
	'application': True,
	'auto_install': False,
}
