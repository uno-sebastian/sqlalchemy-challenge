from flask import Flask, jsonify, request, render_template

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import dateutil.relativedelta as rd

# API version
api_version = "v1.0"
# global datetime format
datetime_format = "%Y-%m-%d"

def try_parse_datetime(value):
	"""
	Try to parse the datetime value
		If it is as a string with the format %Y-%m-%d or as a int formated as the POSIX timestamp

	value - string as date for example 1999-12-31 
			int as POSIX timestamp for example 946602000
	"""
	# create the date var we will send off
	date = dt.datetime.now()
	# try to convert from string if has dashes
	if type(value) is str and "-" in value:
		try:
			date = dt.datetime.strptime(value, datetime_format)
		except Exception as e:
			print(e)
			return f"Please format your dates as YYYY-MM-DD"
	# try to convert from POSIX timestamp
	else:
		try:
			date = dt.datetime.fromtimestamp(int(value)/1000)
		except Exception as e:
			print(e)
			return f"Please format your dates as corresponding to the POSIX timestamp"
	# return date
	return date

def api_path(endpoint=None):
	"""
	return a string that is the api endpoint for a url path,
		if nothing is sent in, then it returns the base path 
			for the api
		if something is sent in, it will point to the
			current version of the api that is live
	"""
	# if the endpoint value is not null,
	# return the full api path with the endpoint
	if (endpoint):
		# catch any typos in case there is
		# an extra forward slash sent in
		if (endpoint.startswith("/")):
			return f"/api/{api_version}{endpoint}"
		else:
			return f"/api/{api_version}/{endpoint}"
	# else if the endpoint is null,
	# send the basic api path
	return f"/api/{api_version}"


def api_endpoints(base_url):
	"""
	returns a dict of values for getting the info and link for each endpoint
	"""
	# remove any sub paths that the base url might return
	# for example 'http://###.#.#.#:####/home'
	if ("/" in base_url):
		base_url = base_url.split("/")[0]
	return {
		"home": {
			"info": "This lists all the avaliable endpoints",
			"link": base_url
		},
		"precipitation": {
			"info": "Return the JSON representation of the precipitation data",
			"link": base_url + api_path("precipitation")
		},
		"stations": {
			"info": "Return the JSON representation of the station's data",
			"link": base_url + api_path("stations")
		},
		"tobs": {
			"info": "Return a JSON list of temperature observations (TOBS) for the previous year",
			"link": base_url + api_path("tobs")
		},
		"temperature info start": {
			"info": "Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range",
			"link": base_url + api_path("2016-08-23")
		},
		"temperature info start and end": {
			"info": "Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end range",
			"link": base_url + api_path("2016-08-23/2017-08-23")
		}
	}

def sqlite_link():
	"""
	Create an sql lite link using sqlalchemy and return the session and classes as a tuple
		It sends back as the following
		(session, Measurement, Station)
	"""
	# create engine to hawaii.sqlite
	engine = create_engine("sqlite:///Resources/hawaii.sqlite")
	# reflect an existing database into a new model
	Base = automap_base()
	# reflect the tables
	Base.prepare(engine, reflect=True)
	# Save references to each table
	Measurement = Base.classes.measurement
	Station = Base.classes.station
	# Create our session (link) from Python to the DB
	session = Session(engine)
	# return as tuple
	return session, Measurement, Station

def query_to_json_dict_list(query):
	"""
	convert a query object to a list of dict using
	the class var names as the keys
	"""
	# create the json list
	json_list = []
	# for each instance of a class in the query
	for instance in query:
		# create the dict to send off
		class_dict = {}
		# for each item in the instance
		for key, value in instance.__dict__.items():
			# this ignores the base classes 
			# that being with underscore
			if not key.startswith("_"):
				# set the dict key and value
				class_dict[key] = value
		# append the new dict to the list
		json_list.append(class_dict)
	# send off the data
	return json_list
	
def most_occurrence(session, table_column):
	"""
	generate a sql alchemy query that grabs the item from a column with the most occurrence
		session - the sql alchemy session
		table_column - the table column to check for most occurrence
	"""
	return session.query(
		# create a responce with the station as the first column
		table_column
	# group by the station, so each unique instance in that column can be counted
	).group_by(table_column).\
	order_by(
		# order by the function call we had, and add the desc call at the end
		func.count(table_column).desc()
	).first()[0]

def most_recent(session, table_column):
	"""
	generate a sql alchemy query that grabs the item from a column which is the most recent
		session - the sql alchemy session
		table_column - the table column to check which is the most recent
	"""    
	# Query the database on the class Measurement
	return session.query(table_column).\
	order_by(
		# order the column, use the decending argument
		table_column.desc()
	).first()[0]

#################################################
# Launch this flask server by running
# python app.py

# used this tutorial for learning
# https://www.youtube.com/watch?v=zRwy8gtgJ1A

# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
	"""
	Home page.
					List all routes that are available.
	"""
	return render_template("home.html", endpoints=api_endpoints(request.base_url))

@app.route(api_path("precipitation"))
def precipitation():
	"""
	`/api/v1.0/precipitation`
					Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
					Return the JSON representation of your dictionary.
	"""
	# create the sqlite link
	# the underscore is to ignore the unused data
	session, Measurement, _ = sqlite_link()
	# create the container for the scores
	precipitation_scores = {}
	# create the query to use
	query_results = session.query(
		# we only need the dates and the prcp
		Measurement.date, 
		Measurement.prcp
	).order_by(Measurement.date)
	# iterate thru the results
	for result in query_results:
		# grab and set the key and 
		# value for each result
		key = str(result.date)
		value = result.prcp
		precipitation_scores[key] = value
	# Close Session
	session.close()
	# return data
	return jsonify(precipitation_scores)

@app.route(api_path("stations"))
def stations():
	"""
	`/api/v1.0/stations`
		Return a JSON list of stations from the dataset.
	"""
	# create the sqlite link
	# the underscore is to ignore the unused data
	session, _, Station = sqlite_link()
	# Return a JSON list of stations from the dataset.
	stations_list = query_to_json_dict_list(session.query(Station))
	# Close Session
	session.close()
	# return data
	return jsonify(stations_list)

@app.route(api_path("tobs"))
def tobs():
	"""
	`/api/v1.0/tobs`
		Query the dates and temperature observations of the most active station for the last year of data.
		Return a JSON list of temperature observations (TOBS) for the previous year.
	"""
	# create the sqlite link
	session, Measurement, _ = sqlite_link()
	# get the most active station
	most_active_station = most_occurrence(session, Measurement.station)
	# get the most recent date, 
	# we will use that as the ending date
	end_date = dt.datetime.strptime(
		most_recent(session, Measurement.date), 
		datetime_format
	)
	# use the ending date as a means to go back 
	# in time a year
	start_date = end_date - rd.relativedelta(years = 1)
	# get all the data with that station, 
	# within the range
	station_data_range = session.query(Measurement).filter(
		# filter most active station
		Measurement.station == most_active_station,
		# use the func.DATE to make sure your date is actually 
		# comparing datetime objects as opposed to a string objects
		func.DATE(Measurement.date) >= func.DATE(start_date.date())
	).order_by(Measurement.date)
	# create the sending data
	stations_list = query_to_json_dict_list(station_data_range)
	# Close Session
	session.close()
	# return data
	return jsonify(stations_list)

@app.route(api_path("<start>"))
def temperature_data_start(start):
	"""
	`/api/v1.0/<start>`
		Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
		When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
	"""
	# try to parse in the sent in start time
	start_date = try_parse_datetime(start)
	# if the returned start date is not datetime,
	# then it failed and has sent back an error string
	if type(start_date) is str:
		return start_date
	# create the sqlite link
	session, Measurement, _ = sqlite_link()
	# get the most active station
	most_active_station = most_occurrence(session, Measurement.station)
	# query the server
	station_tobs_min, station_tobs_max, station_tobs_avg = session.query(
		func.min(Measurement.tobs),
		func.max(Measurement.tobs),
		func.avg(Measurement.tobs)
	).filter(
		# filter most active station
		Measurement.station == most_active_station,
		# use the func.DATE to make sure your date is actually 
		# comparing datetime objects as opposed to a string objects
		func.DATE(Measurement.date) >= func.DATE(start_date.date())
	).first()
	# save the data
	station_info = {
		"TMIN" : station_tobs_min,
		"TMAX" : station_tobs_max,
		"TAVG" : station_tobs_avg
	}
	# Close Session
	session.close()
	# return data
	return jsonify(station_info)


@app.route(api_path("<start>/<end>"))
def temperature_data_start_end(start, end):
	"""
	`/api/v1.0/<start>/<end>`
		Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
		When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
	"""
	# try to parse in the sent in end time
	end_date = try_parse_datetime(end)
	# if the returned end date is not datetime,
	# then it failed and has sent back an error string
	if type(end_date) is str:
		return end_date
	# try to parse in the sent in start time
	start_date = try_parse_datetime(start)
	# if the returned start date is not datetime,
	# then it failed and has sent back an error string
	if type(start_date) is str:
		return start_date
	# create the sqlite link
	session, Measurement, _ = sqlite_link()
	# get the most active station
	most_active_station = most_occurrence(session, Measurement.station)
	# query the server
	station_tobs_min, station_tobs_max, station_tobs_avg = session.query(
		func.min(Measurement.tobs),
		func.max(Measurement.tobs),
		func.avg(Measurement.tobs)
	).filter(
		# filter most active station
		Measurement.station == most_active_station,
		# use the func.DATE to make sure your date is actually 
		# comparing datetime objects as opposed to a string objects
		func.DATE(Measurement.date) >= func.DATE(start_date.date()),
		func.DATE(Measurement.date) <= func.DATE(end_date.date())
	).first()
	# save the data
	station_info = {
		"TMIN" : station_tobs_min,
		"TMAX" : station_tobs_max,
		"TAVG" : station_tobs_avg
	}
	# Close Session
	session.close()
	# return data
	return jsonify(station_info)


if __name__ == "__main__":
	# Since the app is in debug mode as bellow,
	# we can save the python file with the server
	# running and flask will update itself without
	# having to close the server and re-launch it
	app.run(debug=True)
