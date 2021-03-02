from flask import Flask, jsonify, request

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

api_version = "v1.0"

def base_url():
	return "/api/" + api_version

#################################################
# Flask Routes
#################################################
@app.route("/")
@app.route("/index")
def home():
	'''
	Home page.
		List all routes that are available.
	'''
	base_p = f'{request.base_url}api/{api_version}/'
	api_p = f'/api/{api_version}/'
	return f'''
<!DOCTYPE html>
<html>
<body>

<h1>Welcome to the Flask API for the Hawaii Climate</h1>
<p>This app is version {api_version}. Please use the path {request.base_url}api/{api_version} to get to the endpoints.</p>

<h2>Headings</h2>
<ul>
  <li><a href="{request.base_url}">home</a></li>
  <li><a href="{base_p}precipitation">precipitation - {api_p}precipitation</a></li>
  <li><a href="{base_p}stations">stations - {api_p}stations</a></li>
  <li><a href="{base_p}tobs">tobs - {api_p}tobs</a></li>
  <li>start - {api_p}[start]</li>
  <li>start and end - {api_p}[start]/[end]</li>
</ul>
</body>
</html>'''

@app.route(base_url() + "/precipitation")
def precipitation():
	'''
	`/api/v1.0/precipitation`
		Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
		Return the JSON representation of your dictionary.
	'''
	return "precipitation"
	#return jsonify(justice_league_members)

@app.route(base_url() + "/stations")
def stations():
	'''
	`/api/v1.0/stations`
		Return a JSON list of stations from the dataset.
	'''
	return "stations"

@app.route(base_url() + "/tobs")
def tobs():
	'''
	`/api/v1.0/tobs`
		Query the dates and temperature observations of the most active station for the last year of data.
		Return a JSON list of temperature observations (TOBS) for the previous year.
	'''
	return "tobs"

@app.route(base_url() + "/<start>")
def start(start):
	'''
	`/api/v1.0/<start>`
		Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
		When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
	'''
	return f'start: {start}'

@app.route(base_url() + "/<start>/<end>")
def start_end(start, end):
	'''
	`/api/v1.0/<start>/<end>`
		Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
		When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
	'''
	return f'start: {start}, end: {end}'

if __name__ == "__main__":
	app.run(debug=True)
