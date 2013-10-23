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
    def _parse_locations(self, tree):
        locations = {}
        for loc_elem in tree.getroot().iter(tag='location'):
            key = loc_elem.find("location-key").text
            lat = loc_elem.find("point").attrib['latitude']
            lng = loc_elem.find("point").attrib['longitude']            
            locations[key] = (lat,lng)
        return locations

    @classmethod
    def _parse_time_layouts(self, tree):
        """
        Return a dictionary containing the time-layouts
        A time-layout looks like:
            { 'time-layout-key': [(start-time, end-time), ...] }
        """
        time_layouts = {}
        for tl_elem in tree.getroot().iter(tag="time-layout"):
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
    def _parse_temperatures_for_type(self, element, temp_type):                
        for tmp_el in element.iter(tag='temperature'):
            if tmp_el.attrib['type'] != temp_type:
                continue
            values = []
            for val_el in tmp_el.iter(tag='value'):
                try:
                    val = int(val_el.text)
                except TypeError:
                    # Temp can be none if we don't have a forecast for that date
                    val = None
                values.append(val)

            time_layout_key = tmp_el.attrib['time-layout']
            return time_layout_key, values

        raise Exception("temp type '%s' not found in data")

    @classmethod
    def _parse_conditions(self, element):
        for weather_el in element.iter(tag='weather'):
            values = []
            for condition_el in weather_el.iter(tag='weather-conditions'):
                value = condition_el.attrib.get('weather-summary')
                values.append(value)

            time_layout_key = weather_el.attrib['time-layout']
            return time_layout_key, values

    ### These are my functions ###

    @classmethod
    def _parse_probability_of_precip(self, element, time_layout_key):
        for prob_el in element.iter(tag='probability-of-precipitation'):
            all_values = []
            for value_el in prob_el.iter(tag='value'):
                percentage = value_el.text
                all_values.append(percentage)
        
        # POP values are given in 12-hour increments where everything else 
        # we parse is done in 24. We have to stick both values into a tuple
        values = zip(all_values,all_values[1:])[::2]
        return time_layout_key, values

    @classmethod
    def _parse_weather_type_codes(self, element):
        for condition_el in element.iter(tag='conditions-icon'):
            values = []
            for icon_el in condition_el.iter(tag='icon-link'):
                link_val = icon_el.text
                disassembled = urlparse.urlparse(link_val)
                name, ext = os.path.splitext(os.path.basename(disassembled.path))
                values.append(name)
            
            time_layout_key = condition_el.attrib['time-layout']
            return time_layout_key, values
    
    @classmethod
    def get_forecast(self, lat, lng):
        """ A convenience method to make it simpler to get forecast for one location """
        locations = [(lat,lng),]
        location_forecasts = self.get_multiple_forecasts(locations)
        return location_forecasts[0]['forecasts']
    
    @classmethod
    def get_multiple_forecasts(self, latlong_list, metric=False):
    
        # This nasty bit of logic takes each of the (lat,lng) tuples, combines 
        # them into a string with a comma, then joins them with a %20 (encoded space)
        latlong_params = "%20".join([",".join(map(str,l)) for l in latlong_list])
        
        url  = "http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php"
        url += "?whichClient=NDFDgenByDay&listLatLon=%s" % latlong_params
        url += "&Unit=e&format=24+hourly&numDays=4"

        request = requests.get(url, timeout=30.0)
        tree = ET.parse(StringIO.StringIO(request.text))

        # Make sure an error was not returned. If it was, return an empty list.
        if tree.getroot().tag == "error":
            print "Error getting forecasts."
            return []

        time_layouts = self._parse_time_layouts(tree)

        location_forecasts = []

        locations = self._parse_locations(tree)
        for point in locations.keys():

            param_el = tree.find("data/parameters[@applicable-location='%s']" % point)
            min_temp_tlk, min_temps = self._parse_temperatures_for_type(param_el, 'minimum')
            max_temp_tlk, max_temps = self._parse_temperatures_for_type(param_el, 'maximum')
            conditions_tlk, conditions = self._parse_conditions(param_el)
            condition_codes_tlk, condition_codes = self._parse_weather_type_codes(param_el)
            pop_tlk, prob_of_precips = self._parse_probability_of_precip(param_el, condition_codes_tlk)

            # Time layout keys have to match for us to sequence and group by them
            assert (min_temp_tlk == max_temp_tlk == conditions_tlk == condition_codes_tlk)

            time_layout_key = min_temp_tlk
            time_layout = time_layouts[time_layout_key]
            dates = [dt.date() for dt, _ in time_layout]

            forecasts = []
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
                forecasts.append(datapoint)
            
            location_forecasts.append({'location': locations[point], 'forecasts': forecasts})
            
        return location_forecasts


if __name__ == "__main__":

    if not len(sys.argv) == 3:
        sys.exit("Usage: $ python forecast.py [latitude] [longitude]")
    else:    
        str_lat = sys.argv[1]
        str_lng = sys.argv[2]

    # Convert args to float
    try:
        lat = float(str_lat)
        lng = float(str_lng)
    except ValueError:
        sys.exit("Latitude and longitude must be numeric.")

    forecasts = Forecast.get_forecast(lat,lng)
    for forecast in forecasts:
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
