from __future__ import print_function

import pg8000
import subprocess
import requests
import json
import os

from map import Map


#DATABASE_SETTINGS = {
#    'database': 'gif_db',
#    'user': 'postgres',
#    'password': 'password',
#    'host': "localhost",
#    'port': 5432
#}
DATABASE_SETTINGS = {
    'database': 'gif_db',
    'user': 'gifmaker',
    'password': 'P=jbiL.T2Vhv6x',
    'host': 'crossing-gif.civlb2aljpaw.us-east-1.rds.amazonaws.com'
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
            print("Fetching Map Image")
            m = Map(data.get('lat', 39.82), data.get('lon', -98.58))
            m.create()

            output = subprocess.call([
                './gifcreate.sh', 
                data.get('first_name', ''), 
                data.get('second_name', ''),
                data.get('location', ''),
                str(data.get('id', 0))
            ])

            filename = "%s.gif" % data.get('id'
            files = {'file': open(filename, 0), 'rb')}

            r = requests.post('http://upload.giphy.com/v1/gifs', data={
                    'api_key': 'U0vOddn5W0Exy', 'username': 'crossing-us'
                }, files=files)

            # r = MockResponse("3oz8xVxJclwQixjhXW")            

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

                os.remove(filename)

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
        
def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

