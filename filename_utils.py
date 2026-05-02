import os
import re


DEFAULT_VIDEO_EXTENSION = '.mp4'
SAFE_FILENAME_CHARS = re.compile(r'[^A-Za-z0-9._-]+')


def safe_client_filename(filename: str | None, default: str = "video") -> str:
    """Return a display-safe basename for user-provided upload filenames."""
    if not filename:
        return default

    basename = filename.replace("\\", "/").split("/")[-1].strip()
    sanitized = SAFE_FILENAME_CHARS.sub("_", basename).strip("._-")
    return sanitized or default


def normalize_video_output_filename(output_filename: str | None) -> str:
    """
    Normalize a user-provided video output basename for FFmpeg.

    FFmpeg often fails with "Unable to find a suitable output format" when an
    output filename has no extension. Keep output names as basenames only so
    callers cannot traverse directories, and append .mp4 when no extension is
    present.
    """
    if not output_filename or not output_filename.strip():
        return f"output{DEFAULT_VIDEO_EXTENSION}"

    raw_filename = output_filename.strip()
    path_parts = raw_filename.replace("\\", "/").split("/")
    if len(path_parts) > 1 or raw_filename.startswith(("/", "\\")) or ".." in path_parts:
        raise ValueError("Output filename must be a filename, not a path")

    safe_filename = safe_client_filename(raw_filename, default="output")
    _, extension = os.path.splitext(safe_filename)
    if not extension:
        safe_filename = f"{safe_filename}{DEFAULT_VIDEO_EXTENSION}"

    return safe_filename
