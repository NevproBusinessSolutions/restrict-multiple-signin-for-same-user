# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

import logging
import openerp
from openerp import pooler, tools
from openerp.osv import fields, osv, orm
from datetime import date,datetime,time,timedelta
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.controllers import main as openerp_main

_logger = logging.getLogger(__name__)


class Session(openerp_main.Session):
	_cp_path = "/web/session"

	@http.jsonrequest
	def authenticate(self, req, db, login, password, sid=None, base_location=None):
		wsgienv = req.httprequest.environ
		env = dict(
			base_location=base_location,
			HTTP_HOST=wsgienv['HTTP_HOST'],
			REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
			sid=sid,
		)
		req.session.authenticate(db, login, password, env)
		
		return self.session_info(req)


class res_users(osv.osv):
	_inherit = 'res.users'
	
	_columns = { 
		'session_id' : fields.char('Session ID', size=100),
		'expiration_date' : fields.datetime('Expiration Date'),
		'logged_in': fields.boolean('Logged in'),
		}

	def authenticate(self, db, login, password, user_agent_env):
		"""Verifies and returns the user ID corresponding to the given 'login' and 'password' combination, or False if there was no matching user.
			:param str db: the database on which user is trying to authenticate
			:param str login: username
			:param str password: user password
			:param dict user_agent_env: environment dictionary describing any relevant environment attributes
		"""
		uid = self.login(db, login, password)
		if uid:
			sid = user_agent_env.get('sid')
			cr = pooler.get_db(db).cursor()
			result = self.check_session(cr, uid, sid)
			cr.close()
			if not result:
				return False
		if uid == openerp.SUPERUSER_ID:
			# Successfully logged in as admin!
			# Attempt to guess the web base url...
			if user_agent_env and user_agent_env.get('base_location'):
				cr = pooler.get_db(db).cursor()
				try:
					base = user_agent_env['base_location']
					ICP = self.pool.get('ir.config_parameter')
					if not ICP.get_param(cr, uid, 'web.base.url.freeze'):
						ICP.set_param(cr, uid, 'web.base.url', base)
					cr.commit()
				except Exception:
					_logger.exception("Failed to update web.base.url configuration parameter")
				finally:
					cr.close()
		return uid

	#checks is user in already logged in into the system
	def check_session(self, cr, user_id, session_id):
		res = True
		if isinstance(user_id, list): user_id = user_id[0]
		user_data = self.browse(cr, SUPERUSER_ID, user_id)
		if user_data.expiration_date:
			exp_date = datetime.strptime(user_data.expiration_date,"%Y-%m-%d %H:%M:%S")
			if exp_date < datetime.utcnow()  or user_data.session_id != session_id:
				res = False
		return res

	#clears session_id and session expiry from res.users
	def clear_session(self, cr, user_id):
		if isinstance(user_id, list): user_id = user_id[0]
		# cr.execute("UPDATE res_users SET session_id = '', expiration_date = NULL, logged_in = False WHERE id = %s",(user_id,))
		self.write(cr, SUPERUSER_ID, user_id, {'session_id':'','expiration_date':False,'logged_in':False})
		return True

	#insert session_id and session expiry into res.users
	def save_session(self, cr, user_id, sid):
		if isinstance(user_id, list): user_id = user_id[0]
		exp_date = datetime.utcnow() + timedelta(minutes=2)
		exp_date = exp_date.strftime("%Y-%m-%d %H:%M:%S")
		self.write(cr, SUPERUSER_ID, user_id, {'session_id':sid, 'expiration_date':exp_date, 'logged_in':True})
		return True

	#schedular function to validate users session
	def validate_sessions(self, cr, uid):
		ids = self.search(cr,SUPERUSER_ID,[('expiration_date','!=',False)])
		users = self.browse(cr, SUPERUSER_ID, ids)
		
		for user_id in users:
			exp_date = datetime.strptime(user_id.expiration_date,"%Y-%m-%d %H:%M:%S")
			if exp_date < datetime.utcnow():
				self.clear_session(cr, user_id.id)