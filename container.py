def make_container(oid):

    container = ("""
        <!DOCTYPE html>
        <html>
        <body>
          <style>
            video {{
               width:100%;
               max-width: 640px;
               height:auto;
            }}
          </style>

          <div id="media-player">
            <video id="media-video" width="100%" controls>
              <source src="https://video.crossing.us/{}.mp4" type="video/mp4">
              Your browser does not support video
            </video>
          </div>
        </body>
        </html>
    """).format(oid)

    return container
