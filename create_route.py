#!/usr/bin/env python

#
# The MIT License (MIT)
#
# Copyright (c) 2016 Dan "Ducky" Little
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import psycopg2 
import click

import logging

## Parse a comma separated pair of lat, lon
#
# @param pointString A string comma delimited of lat, lon
#
# @returns a dict of {lat, lon}
#
def parse_point_string(pointString):
	# a lot of handy python tricks here, sorry.
	pt = [float(x) for x in pointString.split(',')]
	return {
		'lat' : pt[0], 'lon' : pt[1]
	}


## Find the nearest vertex to a point.
#
#  @param conn PostgreSQL connection
#  @param point {lat, lon} dict.
#
# @returns a list of vertex ids.
#
def get_nearest_vertex(conn, point, vertsTable='hh_2po_4pgr_vertices_pgr'):
	find_point_sql = """
	select id 
	from """+vertsTable+""" 
	order by the_geom <-> st_setsrid(st_makepoint(%(lat)s, %(lon)s), 4326)
	limit 5
	"""
	curs = conn.cursor()
	curs.execute(find_point_sql, point)
	return [x[0] for x in curs]


## Take in two geopgrahic points and attempt
#  to make a route between them.
#
#  @param conn a Postgresql connection
#  @param start A dict containing {lon, lat}
#  @param finish A dict containing {lon, lat}
#  @param targetTable A table name 
#  @param fun Fun or fast routing, True for fun, defaults to False
#
def route_points(conn, start, finish, targetTable, fun=False): 
	logging.info('Getting vertex for start point')
	start_points = get_nearest_vertex(conn, start)
	logging.info('Getting vertex for finish point')
	finish_points = get_nearest_vertex(conn, finish)

	drop_table_sql = "drop table if exists "+targetTable

	cost_field = 'speed_adjusted_cost'
	if(fun):
		cost_field = 'tortuosity_cost'

	create_table_sql = """
create table """+targetTable+""" as
select line.*
from (
 select seq, id1 as node, id2 as edge, cost
  from pgr_dijkstra('select id, source::integer, target::integer, """+cost_field+"""::float8 as cost, (2*"""+cost_field+""")::float8 as reverse_cost from hh_2po_4pgr',
    %(start)s, %(finish)s, false, false)
  ) as route, 
  hh_2po_4pgr as line
  where line.id = route.edge
	"""

	# check that a route was connected.
	check_route_sql = "select count(*) from "+targetTable

	curs = conn.cursor()
	route_found = False
	for start_point in start_points:	
		for finish_point in finish_points:
			if(not route_found):
				logging.info('Routing between '+str(start_point)+' to '+str(finish_point))
				# drop the old table
				# logging.info('Dropping Old Table '+targetTable)
				curs.execute(drop_table_sql)
				# populate the new one
				# logging.info('Creating new Table '+targetTable)
				n_steps = 0
				try:
					curs.execute(create_table_sql, {
						'start' : start_point,
						'finish' : finish_point
					})

					# check that there is a new route.
					curs.execute(check_route_sql)
					# flag off any more route calculations
					#  if a route has been found.
					n_steps = curs.fetchone()[0] 
				except:
					conn.rollback()
				route_found = n_steps > 0
				if(not route_found):
					logging.warning('Failed to route between '+str(start_point)+' to '+str(finish_point))
				else:
					logging.info('N STEPS: '+str(n_steps))
					conn.commit()

	if(not route_found):
		raise ValueError("No route was available.")

## Main program function
# 
#  Takes in the connection and points along with a table prefix
#  This will parse the coordinates then create both a "fast" and a "fun"
#  route based on pre-existings "costs"
#
@click.command()
@click.argument('connectionString')
@click.argument('startPoint')
@click.argument('finishPoint')
@click.argument('tablePrefix')
def main(**kwargs):
	conn = psycopg2.connect(kwargs['connectionstring'])
	start = parse_point_string(kwargs['startpoint'])
	finish = parse_point_string(kwargs['finishpoint'])

	table_prefix = kwargs['tableprefix']

	fun_table_out = table_prefix+'_fun'
	fast_table_out = table_prefix+'_fast'

	try:
		logging.info('Creating fastest route '+fast_table_out)
		route_points(conn, start, finish, fast_table_out) 
		logging.info('Finished fastest route')
		logging.info('Creating fun route '+fun_table_out)
		route_points(conn, start, finish, fun_table_out, fun=True) 
		logging.info('Finished fun route')
	except ValueError:
		logging.error('Could not find a route.')


if(__name__ == "__main__"):
	# get detailed debugging
	logging.basicConfig(level=logging.DEBUG)

	main()
