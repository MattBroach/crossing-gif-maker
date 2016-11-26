"""
Adapted from tyler
https://github.com/benbacardi/tyler
"""
import re
import io
import math
import requests
import random

from PIL import Image


def numTiles(z):
    return math.pow(2,z)

def sec(x):
    return 1 / math.cos(x)

def latlon2relativeXY(lat,lon):
    x = (lon + 180) / 360
    y = (1 - math.log(math.tan(math.radians(lat)) + sec(math.radians(lat))) / math.pi) / 2
    return x, y

def latlon2xy(lat,lon,z):
    n = numTiles(z)
    x,y = latlon2relativeXY(lat, lon)
    return n*x, n*y

def tileXY(lat, lon, z):
    x,y = latlon2xy(lat, lon, z)
    return int(x), int(y)

def get_tile(tile_url):
    return image_data

class Map(object):

    tile_width = 256
    tile_height = 256

    shard_re = re.compile(r'\[(.*)\]')

    def __init__(self, lat, lon, zoom=15, width=640, height=480, tile_url='http://[abc].tile.openstreetmap.org/{zoom}/{x}/{y}.png', format='png'):
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.width = width
        self.height = height
        self.format = format

        self.shards = self.shard_re.findall(tile_url)[0]
        self.tile_url = self.shard_re.sub('{sharding}', tile_url)

    def _number_of_tiles_for_zoom(self):
        return 2 ** self.zoom

    def _relative_x_y(self):
        x = (self.lon + 180) / 360
        y = (1 - math.log(math.tan(math.radians(self.lat)) + (1/math.cos(math.radians(self.lat)))) / math.pi) / 2
        return x, y

    def _absolute_x_y(self):
        tiles = self._number_of_tiles_for_zoom()
        x, y = self._relative_x_y()
        return tiles * x, tiles * y

    def tile_number(self):
        x, y = self._absolute_x_y()
        return int(x), int(y)

    def create(self, filename='/tmp/map.png'):
        tiles_x = int(math.ceil(self.width / self.tile_width)) + 3
        tiles_y = int(math.ceil(self.height / self.tile_height)) + 3

        x_row = range(-int(math.floor(tiles_x/2)),int(math.ceil(tiles_x/2)))
        y_row = range(-int(math.floor(tiles_y/2)),int(math.ceil(tiles_y/2)))

        x_offset, y_offset = tileXY(self.lat, self.lon, self.zoom)
        x_absolute, y_absolute = latlon2xy(self.lat, self.lon, self.zoom)

        x_offset, y_offset = self.tile_number()
        x_absolute, y_absolute = self._absolute_x_y()

        lat_center_diff = int((x_absolute - x_offset) * self.tile_width)
        lon_center_diff = int((y_absolute - y_offset) * self.tile_height)

        tiles = [[(x_offset + x, y_offset + y) for x in x_row] for y in y_row]

        x_left = x_row.index(0) * self.tile_width + lat_center_diff
        y_top = y_row.index(0) * self.tile_height + lon_center_diff

        image_width = tiles_x * self.tile_width
        image_height = tiles_y * self.tile_height


        image = Image.new('RGBA', (image_width, image_height), (0,0,0,0))
        blank_image = Image.new('RGBA', (image_width, image_height), (0,0,0,0))

        for row_offset, row in enumerate(tiles):
            for col_offset, (x, y) in enumerate(row):
                try:
                    new_image = Image.open(self.get_tile(self.zoom, x, y))
                except requests.HTTPError:
                    new_image = blank_image
                image.paste(new_image, ((col_offset * self.tile_width, row_offset * self.tile_height)))

        image = image.crop((
            int(x_left - (self.width / 2)),
            int(y_top - (self.height / 2)),
            int(x_left + (self.width / 2)),
            int(y_top + (self.height / 2)),
        ))

        return image.save(filename, format=self.format)

    def get_tile(self, zoom, x, y):
        tile_url = self.get_tile_url(zoom, x, y)
        response = requests.get(tile_url)
        response.raise_for_status()
        image_data = response.content
        return io.BytesIO(image_data)

    def get_tile_url(self, zoom, x, y):
        return self.tile_url.format(zoom=zoom, x=x, y=y, sharding=random.choice(self.shards))
