from __future__ import print_function

import pg8000
import subprocess
import requests
import json
import os

from map import Map


# DATABASE_SETTINGS = {
   # 'database': 'gif_db',
   # 'user': 'postgres',
   # 'password': 'password',
   # 'host': "localhost",
   # 'port': 5432
# }
DATABASE_SETTINGS = {
    'database': 'gif_db',
    'user': 'gifmaker',
    'password': 'P=jbiL.T2Vhv6x',
    'host': 'crossing-gif.civlb2aljpaw.us-east-1.rds.amazonaws.com'
}
    
TABLE_NAME = 'giphy'

WRITE_DIR='/tmp'

def makeIntersectionGif(event, context):
    data = event.get('queryStringParameters', {})

    m = Map(float(data.get('lat', 39.82)), float(data.get('lon', -98.58)))
    m.create()

    output = subprocess.call([
        './gifcreate.sh', 
        data.get('nm1', ''), 
        data.get('nm2', ''),
        data.get('loc', ''),
        str(data.get('id', 0))
    ])

    filename = "%s/%s.gif" % (WRITE_DIR, data.get('id', 0))
    files = {'file': open(filename, 'rb')}

    r = requests.post('http://upload.giphy.com/v1/gifs', data={
            'api_key': 'U0vOddn5W0Exy', 'username': 'crossing-us'
        }, files=files)

    # r = MockResponse("3oz8xVxJclwQixjhXW")            

    if r.status_code == 200:
        content = json.loads(r.content)
        url = make_giphy_url(content['data']['id'])
        giphy_id = os.path.basename(url)

        conn = pg8000.connect(**DATABASE_SETTINGS)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO """ + TABLE_NAME + """
            VALUES (%s, %s);
            """, [data.get('id'), giphy_id]
        )
        conn.commit()

        cur.close()
        conn.close()

        os.remove(filename)

        return {
            'statusCode': 200,
            'body': json.dumps({'giphy_id': giphy_id}),
            'headers':{}
        }

    else:
        cur.close()
        conn.close()

        r.raise_for_status()


def getIntersectionGif(event, context):
    data = event.get('queryStringParameters', {})

    conn = pg8000.connect(**DATABASE_SETTINGS)
    cur = conn.cursor()

    # Check if the intersection ID already has a GIF associated with it
    if data.get('id', None) is not None:
        cur.execute("""
            SELECT giphy_id
            FROM """ + TABLE_NAME + """
            WHERE id = %s;
            """, [data.get('id', None)]
        )
        resp = cur.fetchone()

        # If the gif already exists, just return the URL
        if resp:
            cur.close()
            conn.close()

            print(resp)

            return {
                'statusCode': 200,
                'body': json.dumps({'giphy_id': resp[0]}),
                'headers':{
                    'X-Requested-With': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
                }
            }

        # Otherwise, return an error
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No Gif Matches that ID'}),
                'headers':{}
            }
    else:
        cur.close()
        conn.close()

        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Gif Request missing ID'}),
            'headers':{}
        }
        

def make_giphy_url(giphy_id):
    return "https://giphy.com/gifs/%s" % giphy_id


class MockResponse():
    def __init__(self, giphy_id):
        self.content = '{"data":{"id":"%s"},"meta":{"status":200,"msg":"OK","response_id":"581823111c42f34bfe0790d4"}}' % giphy_id
        self.status_code = 200
        
