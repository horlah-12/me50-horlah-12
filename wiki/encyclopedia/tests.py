from django.test import TestCase
from django.urls import reverse


class EntryViewTests(TestCase):
    def test_entry_page_renders_markdown_as_html(self):
        response = self.client.get(reverse("entry", kwargs={"title": "Python"}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Python</h1>")
        self.assertContains(response, "<strong>command-line scripts</strong>")
