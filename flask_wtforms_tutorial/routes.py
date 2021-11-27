from flask import current_app as app
from flask import redirect, render_template, url_for, request, flash

from .forms import StockForm
from .charts import *
from datetime import timedelta


import requests
from datetime import datetime
from datetime import date
import pygal



@app.route("/", methods=['GET', 'POST'])
@app.route("/stocks", methods=['GET', 'POST'])
def stocks():
    
    form = StockForm()
    if request.method == 'POST':
        err = None
        if form.validate_on_submit():
            #Get the form data to query the api
            symbol = request.form['symbol']
            chart_type = request.form['chart_type']
            time_series = request.form['time_series']
            start_date = convert_date(request.form['start_date'])
            end_date = convert_date(request.form['end_date'])
            today = datetime.now().date()
            API_KEY = "NDN2S8ZUZVMFC79X"

            # start_date_str = datetime.strftime(start_date, '%Y-%m-%d').date()
            # end_date_str = datetime.strftime(end_date, '%Y-%m-%d').date()


            if end_date <= start_date:
                #Generate error message as pass to the page
                err = "ERROR: End date cannot be earlier than Start date."
                chart = None
            elif time_series == '1':
                earliest_date = today - timedelta(days=60)  # 60 days prior to today
                if start_date <= earliest_date:
                    err = "ERROR: Intraday Series cannot retrieve data more than 60 days ago"
                    chart = None
            elif start_date >= today or end_date >= today:
                #Generate error message as pass to the page
                err = "ERROR: Stock Data beyond today's date does not yet exist..."
                chart = None
            else:
                #query the api using the form data
                err = None

                GRAPH = {
                    '1': 'bar',
                    '2': 'line'
                }
                FUNCTION = {
                    '1': 'TIME_SERIES_INTRADAY',
                    '2': 'TIME_SERIES_DAILY',
                    '3': 'TIME_SERIES_WEEKLY',
                    '4': 'TIME_SERIES_MONTHLY'
                }
                return_dict = {}

                chart_type_str = GRAPH[str(chart_type)]  # converting ints to proper strings for queries
                time_series_str = FUNCTION[str(time_series)]  # converting ints to proper strings for queries

                # inputs = [symbol, chart_type_str, time_series_str, start_date, end_date]

                return_dict = {
                    "stock_symbol": symbol,  # string
                    "graph_type": chart_type_str,  # string
                    "time_series": time_series_str,  # string
                    "start_date": start_date,  # datetime object
                    "end_date": end_date  # datetime object
                }

                # create url string
                url = 'https://www.alphavantage.co/query?function=' + time_series_str + '&symbol=' + symbol

                # if time_series is 'TIME_SERIES_INTRADAY' then add the required 'interval' field to the url string
                if 'time_series' == 'TIME_SERIES_INTRADAY':
                    url = url + '&interval=60min'
                    url = url + '&outputsize=full'  # request more than the last 100 data points
                elif 'time_series' == 'TIME_SERIES_DAILY':
                    url = url + '&outputsize=full'  # request more than the last 100 data points

                # add API_KEY to url string
                url += '&apikey=' + API_KEY

                # make request using url string
                try:
                    r = requests.get(url)
                except Exception:
                    err = 'ERROR: API call error..no data sent'
                    chart = None

                if r.status_code == 200: #API call successful
                    # THIS IS WHERE YOU WILL CALL THE METHODS FROM THE CHARTS.PY FILE AND IMPLEMENT YOUR CODE

                    # This chart variable is what is passed to the stock.html page to render the chart returned from the api
                    data = r.json()

                    start = return_dict['start_date']
                    end = return_dict['end_date']

                    # FUNCTION:
                    # 1. intraday     } --> must also match time of day
                    # 2. daily          |
                    # 3. weekly         |--> same format
                    # 4. monthly        |
                    pattern = '%Y-%m-%d'
                    if return_dict['time_series'] == FUNCTION['1']:  # if it's intraday
                        pattern = pattern + ' %H:%M:%S'  # adjust pattern to match time of day

                    # variables for simplicity
                    try:
                        dates_key = list(data.keys())[
                            1]  # key corresponding to the value for the list of data entries
                        dates_dict = data[dates_key]  # make new dict to hold the dates
                    except Exception:
                        err = 'An error occurred retrieving data from the API. No data sent...'
                        chart = None

                    # remove dates from dates_dict as specified by start and end
                    for key in list(
                            dates_dict.keys()):  # list(<>.keys()) for iterating over keys. Note that dates_dict is still the entire dict of objects
                        try:
                            current_key = datetime.strptime(key, pattern)
                            if current_key.date() < start or current_key.date() > end:
                                dates_dict.pop(key)
                        except Exception:
                            err = 'exception occurred on data entry: ', key
                            continue


                    err = data
                    test_sdate = today
                    test_edate = today

                    #chart = render_graph(data, dates_dict)
                    chart = None


                else:
                    err = "ERROR: API call returned no data..."
                    chart = None

            return render_template("stock.html", form=form, template="form-template", err = err, chart = chart)
    
    return render_template("stock.html", form=form, template="form-template")
