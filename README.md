# NominatimLibrary

## Requirements

You must install `geopy` in order to run the library :

```shell
pip install geopy
```

## Usage

```python3
from NominatimLibrary import Locator, NotFoundException

# Initialize the connection with Nominatim:
locator = Locator()

# Use the methods described in the `__init__.py` file:
locator.distance_crow_coords((1.5,2.6),(0.4,2.6))
```
