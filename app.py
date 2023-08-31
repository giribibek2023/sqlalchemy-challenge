import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Passenger = Base.classes.passenger

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
      return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation date for the last year"""
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    prcp_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    prcp_dict = {date: prcp for date, prcp in prcp_results}
    
    return jsonify(prcp_dict)


# Stations route
@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.station).all()
    stations_list = list(np.ravel(station_results))
    
    return jsonify(stations_list)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent data point
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query temperature observations for the most active station in the last year
    temperature_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 2772).\
        filter(Measurement.date >= one_year_ago).all()
    
    return jsonify(temperature_results)
# Temperature statistics route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    if not end:
        end = 2017,8,23
    
    # Query to calculate temperature statistics for the specified date range
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)

    