from geopy.geocoders import Nominatim
from geopy import distance

from pyroutelib2.loadOsm import LoadOsm
from pyroutelib2.route import Router

class Locator:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="Test")

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
        return (loc.latitude, loc.longitude)

    def reverse_locate(self, coordinates):
        """Gets the address to given coordinates
            
            Args:
                coordinates ((latitude (float), longitude (float))): tuple of the coordinates
                
            Returns:
                Object containing informations such as address and coordinates
        """
        return self.geolocator.reverse(coordinates)
    
    def distance_crow_addrs(self, address0, address1):
        """Gets the address to given coordinates
            
            Args: 
                address0 and address1 (str) : String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code
                
            Returns:
                float : distance in km
        """
        coord0 = self.get_coordinates(address0)
        coord1 = self.get_coordinates(address1)
        return self.distance_crow_coords(coord0, coord1)
    
    def distance_crow_coords(self, coord0, coord1):
        return distance.distance(coord0, coord1).km
        # return distance.geodesic(coord0,coord1, ellipsoid='GRS-80').km

    def distance_route_addrs(self, address0, address1):
        """Gets the address to given coordinates
            
            Args: 
                address0 and address1 (str) : String List of following arguments: house_number,road, town, city, county, state_district, state, postcode, country, country_code
                
            Returns:
                float : distance in km
        """
        coord0 = self.get_coordinates(address0)
        coord1 = self.get_coordinates(address1)
        return self.distance_route_coords(coord0, coord1)
    
    def distance_route_coords(self, coord0, coord1):
        data = LoadOsm("cycle")
        router = Router(data)

        node0 = data.findNode(coord0[0], coord0[1])
        node1 = data.findNode(coord1[0], coord1[1])
        
        result, route = router.doRoute(node0, node1)

        if result == 'success':
            lats = []
            lons = []
            for i in route:
                node = data.rnodes[i]
                lats.append(node[0])
                lons.append(node[1])
                # print("%d: %f,%f" % (i, node[0], node[1]))
            
            distance_route = 0
            for i in range(len(lons)-1):
                p1=(lats[i],lons[i])
                p2=(lats[i+1],lons[i+1])
                distance_route += self.distance_crow_coords(p1, p2)

            return distance_route
        else:
            print("Error calculating the route.")


if __name__ == "__main__":
    ltr = Locator()

    hsulm = "10 Prittwitzstraße Ulm"
    hsulm2 = "Albert Einstein Allee, Ulm"

    loc = ltr.locate(hsulm)
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