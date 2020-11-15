# import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# flask setup
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    """List all available api routes."""
    return (
        f"<h1 style='margin : 30px 0 20px 100px; color : black;'>Available Routes:</h1>"
        f"<h3 style='margin : 0 0 10px 120px; color : red'>/api/v1.0/precipitation</h3>"
        f"<h3 style='margin : 0 0 10px 120px; color : red'>/api/v1.0/stations</h3>"
        f"<h3 style='margin : 0 0 10px 120px; color : red'>/api/v1.0/tobs</h3>"
        f"<h3 style='margin : 20px 0 10px 120px; color : blue'>For start_date and end_date, put dates in yyyy-mm-dd format:</h3>"
        f"<h3 style='margin : 0 0 10px 120px; color : red'>/api/v1.0/start_date</h3>"
        f"<h3 style='margin : 0 0 10px 120px; color : red'>/api/v1.0/start_date/end_date</h3>"
    )

# 4. Define what to do when a user hits the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for precipitation data...")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # query precipitation data
    results = session.query(*[measurement.date, measurement.prcp]).all()

    # Create dicionaries for each record and append to a list of results
    precipitation_data = []

    for date, prcp in results:
        date_dict = {date : prcp}
        precipitation_data.append(date_dict)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for stations list...")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    select = [station.station, station.name, station.latitude, station.longitude, station.elevation]
    # query precipitation data
    results = session.query(*select).all()

    # Create dicionaries for each record and append to a list of results
    station_data = []

    for station_id, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["station"] = station_id
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        station_data.append(station_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for temperature data...")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    start_date = dt.datetime(2016, 8, 23)
    # query precipitation data
    results = session.query(*[measurement.date, measurement.tobs]).filter(measurement.date > start_date).all()

    # Create dicionaries for each record and append to a list of results
    temp_data = []

    for date, tobs in results:
        date_dict = {date : tobs}
        temp_data.append(date_dict)

    return jsonify(temp_data)    
    

@app.route("/api/v1.0/<start_date>")
def startdate(start_date):
    print("Server received request for summary data after startdate...")

    # format start_date
    start_split = start_date.split("-")
    begin_date = dt.datetime(int(start_split[0]), int(start_split[1]), int(start_split[2]))

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # query precipitation data
    results = session.query(*[func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]).filter(measurement.date >= begin_date).all()

    # Create dicionaries for each record and append to list
    temp_data = []
    for mintobs, avgtobs, maxtobs in results:
        # exit for loop if no results
        if mintobs == None:
            break
        
        else:
            temp_dict = {}
            temp_dict["TMIN"] = mintobs
            temp_dict["TAVG"] = round(avgtobs, 1)
            temp_dict["TMAX"] = maxtobs
            temp_data.append(temp_dict)

    if len(temp_data) == 0:
        return jsonify({"error": f"No data returned for {start_date}. No data available for dates after 2017-08-23. Check date, {start_date}, is in correct format yyyy-mm-dd."})
    
    else:
        return jsonify(temp_data)
 

@app.route("/api/v1.0/<start_date>/<end_date>")
def daterange(start_date, end_date):
    print("Server received request for data between startdate and enddate...")
     # format start_date
    start_split = start_date.split("-")
    begin_date = dt.datetime(int(start_split[0]), int(start_split[1]), int(start_split[2]))

    # format end_date
    end_split = end_date.split("-")
    final_date = dt.datetime(int(end_split[0]), int(end_split[1]), int(end_split[2]))
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # query precipitation data
    results = session.query(*[func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]).filter(measurement.date >= begin_date).filter(measurement.date <= final_date).all()

    # Create dicionaries for each record and append to list
    temp_data = []
    for mintobs, avgtobs, maxtobs in results:
        # exit for loop if no results
        if mintobs == None:
            break
        
        else:
            temp_dict = {}
            temp_dict["TMIN"] = mintobs
            temp_dict["TAVG"] = round(avgtobs, 1)
            temp_dict["TMAX"] = maxtobs
            temp_data.append(temp_dict)
    
    # Throw error if no data returned
    if len(temp_data) == 0:
        return jsonify({"error": f"No data returned between {start_date} and {end_date}. No data available for dates after 2017-08-23. Check dates, {start_date} and {end_date}, are in correct format yyyy-mm-dd and order."})
    
    else:
        return jsonify(temp_data)


if __name__ == "__main__":
    app.run(debug=True)