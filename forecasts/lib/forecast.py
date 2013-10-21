# -*- coding: utf-8 -*-

import sys
import argparse
import requests
import dateutil.parser
import StringIO 
import urlparse
import os

from xml.etree import ElementTree as ET
from weather_symbols import WEATHER_SYMBOLS

class Forecast():

    ### These come from the python-noaa project ###

    @classmethod
    def _parse_time_layouts(self, tree):
        """Return a dictionary containing the time-layouts

        A time-layout looks like:

            { 'time-layout-key': [(start-time, end-time), ...] }
        """
        time_layouts = {}
        for tl_elem in tree.getroot().getiterator(tag="time-layout"):
            start_times = []
            end_times = []
            for tl_child in list(tl_elem):
                if tl_child.tag == "layout-key":
                    key = tl_child.text
                elif tl_child.tag == "start-valid-time":
                    dt = dateutil.parser.parse(tl_child.text)
                    start_times.append(dt)
                elif tl_child.tag == "end-valid-time":
                    dt = dateutil.parser.parse(tl_child.text)
                    end_times.append(dt)

            time_layouts[key] = zip(start_times, end_times)

        return time_layouts

    @classmethod
    def _parse_temperatures_for_type(self, tree, temp_type):
        for tmp_e in tree.getroot().getiterator(tag='temperature'):
            if tmp_e.attrib['type'] != temp_type:
                continue
            values = []
            for val_e in tmp_e.getiterator(tag='value'):
                try:
                    val = int(val_e.text)
                except TypeError:
                    # Temp can be none if we don't have a forecast for that
                    # date
                    val = None
                values.append(val)

            time_layout_key = tmp_e.attrib['time-layout']
            return time_layout_key, values

        raise Exception("temp type '%s' not found in data")

    @classmethod
    def _parse_conditions(self, tree):
        for weather_e in tree.getroot().getiterator(tag='weather'):
            values = []
            for condition_e in weather_e.getiterator(tag='weather-conditions'):
                value = condition_e.attrib.get('weather-summary')
                values.append(value)

            time_layout_key = weather_e.attrib['time-layout']
            return time_layout_key, values

    ### These are my functions ###

    @classmethod
    def _parse_probability_of_precip(self, tree, time_layout_key):
        for prob_e in tree.getroot().getiterator(tag='probability-of-precipitation'):
            all_values = []
            for value_e in prob_e.getiterator(tag='value'):
                percentage = value_e.text
                all_values.append(percentage)
        
        # POP values are given in 12-hour increments where everything else 
        # we parse is done in 24. We have to stick both values into a 
        # tuple
        values = zip(all_values,all_values[1:])[::2]
        return time_layout_key, values

    @classmethod
    def _parse_weather_type_codes(self, tree):
        for condition_e in tree.getroot().getiterator(tag='conditions-icon'):
            values = []
            for icon_e in condition_e.getiterator(tag='icon-link'):
                link_val = icon_e.text
                disassembled = urlparse.urlparse(link_val)
                name, ext = os.path.splitext(os.path.basename(disassembled.path))
                values.append(name)
            
            time_layout_key = condition_e.attrib['time-layout']
            return time_layout_key, values
    
    @classmethod
    def get_forecast(self, latitude, longitude, metric=False):
    
        url  = "http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php"
        url += "?whichClient=NDFDgenByDay&lat=%.3f&lon=%.3f&Unit=e&format=24+hourly&numDays=4" % (latitude, longitude)

        request = requests.get(url)
        tree = ET.parse(StringIO.StringIO(request.text))
    
        time_layouts = self._parse_time_layouts(tree)
        min_temp_tlk, min_temps = self._parse_temperatures_for_type(tree, 'minimum')
        max_temp_tlk, max_temps = self._parse_temperatures_for_type(tree, 'maximum')
        conditions_tlk, conditions = self._parse_conditions(tree)
        condition_codes_tlk, condition_codes = self._parse_weather_type_codes(tree)
        pop_tlk, prob_of_precips = self._parse_probability_of_precip(tree, condition_codes_tlk)

        # Time layout keys have to match for us to sequence and group by them
        assert (min_temp_tlk == max_temp_tlk == conditions_tlk == condition_codes_tlk)

        time_layout_key = min_temp_tlk
        time_layout = time_layouts[time_layout_key]
        dates = [dt.date() for dt, _ in time_layout]

        forecast = []
        for date, min_temp_value, max_temp_value, condition, condition_code, pop_tuple in \
            zip(dates, min_temps, max_temps, conditions, condition_codes, prob_of_precips):

            # If we're missing any data, don't create the data point
            if None in [min_temp_value, max_temp_value, condition]:
                continue
            
            try:
                code = WEATHER_SYMBOLS[condition_code]
            except KeyError:
                print "Error getting weather symbol for key: %s" % condition_code
                code = " "

            datapoint = {
                "date": date,
                "min_temp": min_temp_value,
                "max_temp": max_temp_value,
                "condition": condition,
                "code": code,
                "pop_day": pop_tuple[0],
                "pop_night": pop_tuple[1],
            }
            forecast.append(datapoint)

        return forecast

    @classmethod
    def get_multiple_forecasts(self, lat_long_list, metric=False):

        url  = "http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php"
        url += "?whichClient=NDFDgenByDay&listLatLon=%s" % "%20".join(lat_long_list)
        url += "&Unit=e&format=24+hourly&numDays=4"
        print url

if __name__ == "__main__":

    if not len(sys.argv) == 3:
        sys.exit("Usage: $ handler.py [latitude] [longitude]")
    else:    
        str_lat = sys.argv[1]
        str_lng = sys.argv[2]

    # Convert args to float
    try:
        lat = float(str_lat)
        lng = float(str_lng)
    except ValueError:
        sys.exit("Latitude and longitude must be numeric.")

    forecasts_list = Forecast.get_forecast(lat,lng)

    for forecast in forecasts_list:
        print "%s\t%s  %.0f%s-%.0f%s\t%s\t%s%% chance of precipitation" % (
            forecast['date'].strftime("%a"),
            forecast['code'], 
            forecast['min_temp'], 
            u'°', 
            forecast['max_temp'], 
            u'°', 
            forecast['condition'],
            forecast['pop_day'],
        )