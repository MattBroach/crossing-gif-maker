from __future__ import print_function

import pg8000
import subprocess
import requests
import json

from map import Map


DATABASE_SETTINGS = {
    'database': 'gif_db',
    'user': 'postgres',
    'password': 'password',
    'host': "localhost",
    'port': 5432

}
TABLE_NAME = 'intersections'


def gifFromIntersection(event, context):
    data = event.get('query', {})

    conn = pg8000.connect(**DATABASE_SETTINGS)
    cur = conn.cursor()

    # Check if the intersection ID already has a GIF associated with it
    if data.get('id', None) is not None:
        cur.execute("""
            SELECT url
            FROM """ + TABLE_NAME + """
            WHERE id = %s;
            """, [data.get('id', None)]
        )
        resp = cur.fetchone()

        # If the gif already exists, just return the URL
        if resp:
            cur.close()
            conn.close()

            return {
                'url': resp[1]
            }

        # Otherwise, run the gif creation process
        else:
            #print("Fetching Map Image")
            #m = Map(data.get('lat', 39.82), data.get('lon', -98.58))
            #m.create()

            #output = subprocess.call([
            #    './gifcreate.sh', 
            #    data.get('first_name', ''), 
            #    data.get('second_name', ''),
            #    data.get('location', ''),
            #    str(data.get('id', 0))
            #])

            #files = {'file': open("%s.gif" % data.get('id', 0), 'rb')}

            #r = requests.post('http://upload.giphy.com/v1/gifs', data={
            #        'api_key': 'dc6zaTOxFJmzC',
            #    }, files=files)
            #print(r.content)

            r = MockResponse("3oz8xVxJclwQixjhXW")            

            if r.status_code == 200:
                content = json.loads(r.content)
                url = make_giphy_url(content['data']['id'])

                cur.execute(
                    """
                    INSERT INTO """ + TABLE_NAME + """
                    VALUES (%s, %s);
                    """, [data.get('id'), url]
                )
                conn.commit()

                cur.close()
                conn.close()

                return {
                    'url': url
                }

            else:
                cur.close()
                conn.close()

                r.raise_for_status()


def make_giphy_url(giphy_id):
    return "https://giphy.com/gifs/%s" % giphy_id


class MockResponse():
    def __init__(self, giphy_id):
        self.content = '{"data":{"id":"%s"},"meta":{"status":200,"msg":"OK","response_id":"581823111c42f34bfe0790d4"}}' % giphy_id
        self.status_code = 200
