from flask import g, request, Blueprint

from mv_back.api.video_api import *

video = Blueprint("video", __name__, url_prefix="/api/video")

#--------------------------------------------------------------
# GETs

@video.route(f'', methods=['GET'])
def serve_video_with_range_route():
    video_path = request.args.get('path')
    range_header = request.headers.get('Range', None)
    return serve_video_with_range(video_path, range_header)