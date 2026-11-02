"""Exercise discovery's public contract on valid and malformed article collections."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('discovery', Path(__file__).with_name('discover-articles.py'))
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.previous = discovery.ARTICLES
        discovery.ARTICLES = Path(self.directory.name)
        self.addCleanup(setattr, discovery, 'ARTICLES', self.previous)

    def article(self, slug):
        root = discovery.ARTICLES / slug
        (root / 'tex').mkdir(parents=True)
        for name in ('README.md', 'Makefile', 'tex/main.tex'):
            (root / name).touch()
        return root

    def test_new_articles_are_discovered_in_stable_order(self):
        self.article('second')
        self.article('first')
        self.assertEqual(discovery.discover(), ['first', 'second'])

    def test_incomplete_article_is_an_error(self):
        root = self.article('incomplete')
        (root / 'tex/main.tex').unlink()
        with self.assertRaisesRegex(SystemExit, 'incomplete: missing tex/main.tex'):
            discovery.discover()

    def test_unsafe_slug_is_an_error(self):
        self.article('invalid slug')
        with self.assertRaisesRegex(SystemExit, 'Invalid article slug'):
            discovery.discover()

    def test_empty_collection_is_an_error(self):
        with self.assertRaisesRegex(SystemExit, 'No articles found'):
            discovery.discover()

    def test_symlink_is_an_error(self):
        root = self.article('original')
        (discovery.ARTICLES / 'alias').symlink_to(root, target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, 'must not be a symlink'):
            discovery.discover()


if __name__ == '__main__':
    unittest.main()
