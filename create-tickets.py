#!/usr/bin/env python

import configparser
from pyexcel_ods3 import get_data
from pyexcel_ods3 import save_data
from redminelib import Redmine
from collections import namedtuple

CustomField = namedtuple('CustomField', ['field_id', 'column_idx'])
config_file = 'redmine.cfg'
config = None

def init():
	global config

	config = configparser.ConfigParser()
	files = config.read(config_file)

	if len(files) != 1:
		raise ValueError(f'{config_file}: invalid configuration file')
	
if __name__ == "__main__":
	init()

	url = config.get('redmine', 'url')
	apikey = config.get('redmine', 'apikey')
	tickets_file = config.get('tickets', 'file')
	sheet = config.get('tickets', 'sheet')

	ticket_mappings = config['ticket-mappings']

	issue_id = ticket_mappings.getint('issue_id')
	project_id = ticket_mappings.getint('project_id')
	subject = ticket_mappings.getint('subject')
	tracker_id = ticket_mappings.getint('tracker_id')
	description = ticket_mappings.getint('description')
	priority_id = ticket_mappings.getint('priority_id')

	custom_fields = [
		CustomField(int(c.split('custom_')[1]),int(ticket_mappings[c])) for c in 
			filter(lambda t: t.startswith('custom_'), ticket_mappings)
	]

	data = get_data(tickets_file)
	redmine = Redmine(url, key=apikey)

	tickets = data.get(sheet)

	for t in tickets[1:]:
		custom_values = [
			{
				'id': cv.field_id, 
				'value': t[cv.column_idx] if cv.column_idx < len(t) else ''
			} for cv in custom_fields
		]

		if t[issue_id] != '':
			print(f'Issue {t[issue_id]} already exists')
			# @TODO implement ticket update
			continue

		issue = redmine.issue.create (
			project_id = t[project_id],
			subject = t[subject],
			tracker_id = t[tracker_id],
			description = t[description],
			priority_id = t[priority_id],
			custom_fields = custom_values
		)
		id = issue['id']
		t[issue_id] = id
		print(f'Ticket {id} created!')

	save_data(tickets_file, data)