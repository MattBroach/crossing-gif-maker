import pg8000
import subprocess
import requests
import json
import os
import boto3

from map import Map
from container import make_container


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
SECOND_TABLE = 'completed'

WRITE_DIR = '/tmp'

GIPHY_API_KEY = 'U0vOddn5W0Exy'
GIPHY_USER =  'crossing-us'


def makeIntersectionGif(event, context):
    data = event.get('queryStringParameters', {})
    id = data.get('id', 0)

    m = Map(float(data.get('lat', 39.82)), float(data.get('lon', -98.58)))
    m.create()

    output = subprocess.call([
        './gifcreate.sh', 
        data.get('nm1', ''), 
        data.get('nm2', ''),
        data.get('loc', ''),
        id
    ])

    filename = "{}/{}.mp4".format(WRITE_DIR, id)
    gifname = "{}/{}.gif".format(WRITE_DIR, id)
    files = {'file': open(filename, 'rb')}

    # Upload Video and container to S3
    s3 = boto3.resource('s3')
    s3.Object('container.crossing.us', '{}.html'.format(id)).put(Body=make_container(id), ContentType='text/html')
    s3.Object('video.crossing.us', '{}.mp4'.format(id)).put(Body=open(filename, 'rb'), ContentType='video/mp4')
    s3.Object('gif.crossing.us', '{}.gif'.format(id)).put(Body=open(gifname, 'rb'), ContentType='image/gif')

    conn = pg8000.connect(**DATABASE_SETTINGS)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO """ + SECOND_TABLE + """ 
        VALUES (%s);
        """, [id]
    )
    conn.commit()

    cur.close()
    conn.close()

    os.remove(filename)
    os.remove(gifname)

    return format_response(200, {})


def getIntersectionGif(event, context):
    data = event.get('queryStringParameters', {})

    # Check if the intersection ID already has a GIF associated with it
    if data.get('id', None) is not None:
        conn = pg8000.connect(**DATABASE_SETTINGS)
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM """ + SECOND_TABLE + """
            WHERE id = %s;
            """, [data.get('id', None)]
        )
        resp = cur.fetchone()
        cur.close()
        conn.close()

        # If the gif already exists, just return the URL
        if resp:
            return format_response(200, {})

        # Otherwise, return an error
        else:
            return format_response(400, {'error': 'No Gif Matches that ID'})
    else:
        return format_response(400, {'error': 'Gif Request missing ID'})
        

def make_giphy_url(giphy_id):
    return "https://giphy.com/gifs/%s" % giphy_id


class MockResponse():
    def __init__(self, giphy_id):
        self.content = '{"data":{"id":"%s"},"meta":{"status":200,"msg":"OK","response_id":"581823111c42f34bfe0790d4"}}' % giphy_id
        self.status_code = 200


def format_response(status, data):
    return {
        'statusCode': status,
        'body': json.dumps(data),
        'headers': {
            'X-Requested-With': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
        }
    }
