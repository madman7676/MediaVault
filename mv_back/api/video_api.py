import os
import mimetypes
import subprocess

def convert_to_mp4(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return False, result.stderr.decode('utf-8')
    return True, None

def prepare_video_payload(video_path, range_header=None):
    """
    Повертає dict у форматі:
      {"data": { video_path, mime_type, file_size, range: {start,end,length} | None }, 'status_code': 200/206}
    Або у випадку помилки:
      {"error": "message", 'status_code': 404/500}
    """
    if not video_path or not os.path.exists(video_path):
        return {"error": "File not found", "status_code": 404}

    try:
        ext = os.path.splitext(video_path)[1].lower()
        if ext == ".avi":
            converted_path = video_path[:-4] + ".mp4"
            if not os.path.exists(converted_path):
                ok, err = convert_to_mp4(video_path, converted_path)
                if not ok:
                    return {"error": f"Failed to convert file: {err}", "status_code": 500}
            video_path = converted_path

        mime_type = mimetypes.guess_type(video_path)[0] or "application/octet-stream"
        file_size = os.path.getsize(video_path)

        if range_header:
            # parse Range: bytes=start-end
            try:
                range_value = range_header.strip().split('=')[-1]
                start_str, end_str = range_value.split('-')
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                if end >= file_size:
                    end = file_size - 1
                if start > end:
                    return {"error": "Invalid Range header", "status_code": 416}
                length = end - start + 1

                return {
                    "data": {
                        "video_path": video_path,
                        "mime_type": mime_type,
                        "file_size": file_size,
                        "range": {"start": start, "end": end, "length": length}
                    },
                    "status_code": 206
                }
            except Exception:
                return {"error": "Invalid Range header format", "status_code": 416}

        # no range requested
        return {
            "data": {
                "video_path": video_path,
                "mime_type": mime_type,
                "file_size": file_size,
                "range": None
            },
            "status_code": 200
        }
    except Exception as e:
        return {"error": str(e), "status_code": 500}