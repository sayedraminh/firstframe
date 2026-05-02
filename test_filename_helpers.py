import unittest

from filename_utils import normalize_video_output_filename, safe_client_filename


class FilenameHelperTests(unittest.TestCase):
    def test_extensionless_video_output_gets_mp4_extension(self):
        self.assertEqual(normalize_video_output_filename("string"), "string.mp4")

    def test_existing_video_output_extension_is_preserved(self):
        self.assertEqual(normalize_video_output_filename("clip.mov"), "clip.mov")

    def test_output_paths_are_rejected(self):
        with self.assertRaises(ValueError):
            normalize_video_output_filename("../clip")

    def test_upload_filename_is_sanitized_for_headers(self):
        self.assertEqual(safe_client_filename("../my video.mp4"), "my_video.mp4")


if __name__ == "__main__":
    unittest.main()
