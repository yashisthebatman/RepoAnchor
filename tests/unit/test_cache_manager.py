import unittest
import tempfile
import os
import json
from repoanchor.cache.manager import CacheManager

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_path = os.path.join(self.temp_dir.name, ".cache.json")
        self.manager = CacheManager(cache_filepath=self.cache_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_hash_comparison(self):
        test_file = os.path.join(self.temp_dir.name, "sample.py")
        with open(test_file, "w") as f:
            f.write("print('hello')")

        self.assertTrue(self.manager.is_changed(test_file))
        self.manager.update_cache(test_file, "print('hello')")
        self.assertFalse(self.manager.is_changed(test_file))

        # Change content
        with open(test_file, "w") as f:
            f.write("print('world')")
        self.assertTrue(self.manager.is_changed(test_file))

    def test_save_and_load_cache(self):
        test_file = os.path.join(self.temp_dir.name, "sample.py")
        with open(test_file, "w") as f:
            f.write("test")

        self.manager.update_cache(test_file, "skeleton_code")
        self.manager.save_cache()

        # Reload Cache
        new_manager = CacheManager(cache_filepath=self.cache_path)
        self.assertEqual(new_manager.get_cached_skeleton(test_file), "skeleton_code")