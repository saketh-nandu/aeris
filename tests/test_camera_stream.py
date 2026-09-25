import unittest

from app.services.camera_service import camera_service


class CameraStreamTests(unittest.TestCase):
    def test_store_live_frame_updates_latest_frame(self):
        camera_service.reset_live_stream("TEST-CAM")
        payload = b"real-camera-frame"

        camera_service.store_live_frame("TEST-CAM", payload)

        self.assertEqual(camera_service.get_latest_frame("TEST-CAM"), payload)

    def test_generate_mjpeg_stream_uses_latest_live_frame(self):
        camera_service.reset_live_stream("TEST-CAM")
        payload = b"real-camera-frame" 
        camera_service.store_live_frame("TEST-CAM", payload)

        chunks = list(camera_service.generate_mjpeg_stream("TEST-CAM", "Phone Camera", max_frames=1))

        self.assertTrue(chunks)
        output = b"".join(chunks)
        self.assertIn(b"Content-Type: image/jpeg", output)
        self.assertNotIn(b"SIMULATED FEED", output)


if __name__ == "__main__":
    unittest.main()
