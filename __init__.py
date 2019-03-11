import ssl
import urllib.request
import json

import geopy
from geopy.geocoders import Nominatim
from geopy import distance

TRANSPORT="car"
DOMAIN = "i-nominatim-01.informatik.hs-ulm.de/nominatim/"
GRAPHHOPPER_API = "http://i-nominatim-01.informatik.hs-ulm.de:11111"
GRAPHHOPPER_ROUTE_QUERY = "route?vehicle=" + TRANSPORT + "&instructions=false&points_encoded=false"

# Timeout for the nominatim server requests
## Some search requests can take some time when executed for the first time
TIMEOUT = 100000

class NotFoundException(Exception):
    pass

def format_points_graphhopper(point):
    return "&point=" + str(point[0]) + "," + str(point[1])

class Locator:
    def __init__(self, domain = DOMAIN):
        geopy.geocoders.options.default_scheme = "http"

        self.geolocator = Nominatim(user_agent="Test", timeout=TIMEOUT, domain=domain)

    def locate(self, address):
        """Gets the coordinates to a given address

            Args:
                address (str) : String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code

            Returns:
                Object containing informations such as address and coordinates
    """
        return self.geolocator.geocode(address)

    def get_coordinates(self, address):
        """Gets the coordinates to a given address

            Args:
                address (str): String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code

            Returns:
                (latitude (float), longitude (float) )
        """
        loc = self.locate(address)
        if loc == None:
            raise NotFoundException(address)
        return (loc.latitude, loc.longitude)

    def reverse_locate(self, coordinates):
        """Gets the address to given coordinates

            Args:
                coordinates ( (latitude (float), longitude (float)) ): tuple of the coordinates

            Returns:
                Object containing informations such as address and coordinates
        """
        return self.geolocator.reverse(coordinates)

    def distance_crow_addrs(self, address0, address1):
        """Gets the distance as the crow flies between two addresses

            Args:
                address0 and address1 (str) : String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code

            Returns:
                float : distance in km
        """
        coord0 = self.get_coordinates(address0)
        coord1 = self.get_coordinates(address1)
        return self.distance_crow_coords(coord0, coord1)

    def distance_crow_coords(self, coord0, coord1):
        """Gets the distance as the crow flies between two coordinates

            Args:
                coord0 and coord1 ( (latitude (float), longitude (float)) ) : coordinates

            Returns:
                float : distance in km
        """
        return distance.distance(coord0, coord1).km
        # return distance.geodesic(coord0,coord1, ellipsoid='GRS-80').km

    def path_route_addrs(self, address0, address1, calc_points=True):
        """
        Gets the distance on the route between two addresses

        Args:
            address0 and address1 (str) : String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code

        Returns:
            Dictionnary containing the shortest path information :
            path = {
                    "distance": distance in meters
                    "time": time in milisecond
                    "bbox": coordinates of the rectangle containing the path : [minLon, minLat, maxLon, maxLat]
                    "points": array of coordinates arrays : [[lon,lat]] only if `calc_points` is True
            }
        """

        coord0 = self.get_coordinates(address0)
        coord1 = self.get_coordinates(address1)
        return self.path_route_coords(coord0, coord1, calc_points)

    def path_route_coords(self, coord0, coord1, calc_points=True):
        """
        Gets the coordinates to a given address

        # See https://graphhopper.com/api/1/docs/routing/

        Returns:
            Dictionnary containing the shortest path information :
            path = {
                    "distance": distance in meters
                    "time": time in milisecond
                    "bbox": coordinates of the rectangle containing the path : [minLon, minLat, maxLon, maxLat]
                    "points": array of coordinates arrays : [[lon,lat]] only if `calc_points` is True
            }
        """

        calc_points_str = "&calc_points=" + str(calc_points)
        points_str = format_points_graphhopper(coord0) + format_points_graphhopper(coord1)
        query = GRAPHHOPPER_API + "/" + GRAPHHOPPER_ROUTE_QUERY + calc_points_str + points_str

        answer = urllib.request.urlopen(query).read()
        parsed_json = json.loads(answer)
        first_path = parsed_json["paths"][0]

        path = {
                "distance": first_path["distance"],
                "time": first_path["time"],
        }

        if calc_points:
            path["bbox"] = first_path["bbox"]
            path["points"] = first_path["points"]["coordinates"]

        return path

    def distance_route_addrs(self, address0, address1):
        """Gets the distance on the route between two addresses

            Args:
                address0 and address1 (str) : String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code

            Returns:
                float : distance in km
        """
        return self.path_route_addrs(address0, address1, False)["distance"] / 1000

    def distance_route_coords(self, coord0, coord1):
        """Gets the distance on the route between two addresses

            Args:
                coord0 and coord1 ( (latitude (float), longitude (float)) ) : coordinates

            Returns:
                float : distance in km
        """

        return self.path_route_coords(coord0, coord1, False)["distance"] / 1000

if __name__ == "__main__":
    ltr = Locator()

    hsulm = "10 Prittwitzstraße Ulm"
    hsulm2 = "Albert Einstein Allee, Ulm"

    loc = ltr.locate(hsulm)
    print(loc.address)
    print(loc.latitude, loc.longitude)

    loc = ltr.locate(hsulm2)
    print(loc.address)
    print(loc.latitude, loc.longitude)

    coords = ltr.get_coordinates(hsulm)
    print(coords)

    place = ltr.reverse_locate(coords)
    print(place.address)

    dist = ltr.distance_crow_addrs(hsulm, hsulm2)
    print(dist)

    distance_route = ltr.distance_route_addrs(hsulm, hsulm2)
    print(distance_route)
