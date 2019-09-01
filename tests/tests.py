"""Basics tests for the backend."""
import json
from tornado.httputil import url_concat
from tornado.testing import AsyncHTTPTestCase

import route

# TODO must begin with getting test mode in settings.json


class TestBackend(AsyncHTTPTestCase):
    """Test the backend. To be improved."""

    def get_app(self):
        """Get the application to test."""
        settings = {}
        return route.Application(settings)

    def test_info(self):
        """Test that the info call works."""
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_unauth_pub(self):
        """Try publish/unpublish without being logged in."""
        key_arg = {"mode": "test"}
        subtype = 'unpub'
        url = url_concat('/publish/'+subtype, key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 401)
        url = url_concat('/subtypes', key_arg)
        response = self.fetch(url)
        published = json.loads(response.body).get('subtypes', [])
        self.assertNotIn(subtype, published)

    def test_unauth_unpub(self):
        """Try publish/unpublish without being logged in."""
        key_arg = {"mode": "test"}
        subtype = 'pub'
        # TODO add pub to subtypes file
        url = url_concat('/unpublish/'+subtype, key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 401)
        url = url_concat('/subtypes', key_arg)
        response = self.fetch(url)
        published = json.loads(response.body).get('subtypes', [])
        self.assertIn(subtype, published)

    def test_query(self):
        """Check search for muminfigurer in swedish and finnsh."""
        # get muminfigurer, order by swedish
        subtype = 'muminfigurer'
        key_arg = {"mode": "term-swefin", 'subtypes': subtype}
        url = url_concat('/search', key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
        hits = json.loads(response.body).get('result', [])

        # get muminfigurer, order by finnish
        key_arg['lang'] = 'fi'
        url = url_concat('/search', key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
        fi_hits = json.loads(response.body).get('result', [])

        # check that we got some hits
        self.assertNotEqual(hits, 0)
        # check that we got the same number of hits for both languages
        self.assertEqual(len(hits), len(fi_hits))
        # check that the order has changed
        self.assertNotEqual(hits, fi_hits)

    def test_word_query(self):
        """Check search for muminfigurer in swedish and finnsh."""
        # get muminfigurer, order by swedish
        subtype = 'muminfigurer'
        q = 'muminmamman'
        key_arg = {"mode": "term-swefin", 'subtypes': subtype, 'q': q}
        url = url_concat('/search', key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
        hits = json.loads(response.body).get('result', [])

        # check case insensitiveness
        key_arg['q'] = q.upper()
        url = url_concat('/search', key_arg)
        print(url)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
        upper_hits = json.loads(response.body).get('result', [])
        print(upper_hits)

        # get muminfigurer, order by finnish
        key_arg['lang'] = 'fi'
        url = url_concat('/search', key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
        fi_hits = json.loads(response.body).get('result', [])

        # check that we got some hits
        self.assertNotEqual(hits, 0)
        # check that we did not get the same hits for finnish
        self.assertNotEqual(len(hits), len(fi_hits))
        # check that we got the same number of hits for both cases
        self.assertEqual(len(hits), len(upper_hits))

    def test_subtypes(self):
        """Check search for muminfigurer in swedish and finnsh."""
        key_arg = {"mode": "test"}
        url = url_concat('/subtypes', key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
        self.assertIn('subtypes', json.loads(response.body))

    def test_html_conv(self):
        """Check search for muminfigurer in swedish and finnsh."""
        # get muminfigurer, order by swedish
        subtype = 'muminfigurer'
        q = 'muminmamman'
        key_arg = {"mode": "term-swefin", 'subtypes': subtype, 'q': q, 'format': 'html'}
        url = url_concat('/search', key_arg)
        response = self.fetch(url)
        self.assertEqual(response.code, 200)
