from django.test import TestCase

from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common import languages

from ..train import train_update
from ..parse import parse_text
from ..parse import format_parse_output
from ...tests.utils import fill_examples
from ...tests.utils import EXAMPLES_MOCKUP
from ...tests.utils import EXAMPLES_WITH_LABEL_MOCKUP


class ParseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')
        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        self.update = self.repository.current_update()
        train_update(self.update, self.user)

    def test_parse(self):
        example = EXAMPLES_MOCKUP[0]
        response = parse_text(
            self.update,
            example.get('text'),
            use_cache=False)
        self.assertEqual(
            response.get('intent', {}).get('name'),
            example.get('intent'))


class ParseWithLabelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')
        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)
        fill_examples(EXAMPLES_WITH_LABEL_MOCKUP, self.repository)
        self.update = self.repository.current_update()
        train_update(self.update, self.user)

    def test_parse(self):
        response = parse_text(
            self.update,
            'I love cat',
            use_cache=False)
        self.assertListEqual(
            response.get('entities_list'),
            ['cat'])
        self.assertIsNone(
            response.get('entities').get('animal')[0].get('self'))

    def test_parse_label_self(self):
        response = parse_text(
            self.update,
            'My aunt love elephant',
            use_cache=False)
        self.assertListEqual(
            response.get('entities_list'),
            ['aunt'])
        animal_label = response.get('entities').get('animal')
        self.assertEqual(len(animal_label), 1)
        self.assertEqual(animal_label[0].get('entity'), 'animal')


class TestFormatParseOutput(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')
        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)
        fill_examples(EXAMPLES_WITH_LABEL_MOCKUP, self.repository)
        self.update = self.repository.current_update()

    def test_label_out(self):
        out = format_parse_output(self.update, {
            'intent': None,
            'intent_ranking': [],
            'entities': [
                {
                    'start': 0,
                    'end': 3,
                    'entity': 'cat',
                    'value': 'cat',
                    'confidence': .9,
                },
            ],
            'labels_as_entity': [],
        })
        self.assertIn('animal', out.get('labels_list'))
        self.assertIn('cat', out.get('entities_list'))
        self.assertEqual(
            len(out.get('entities').get('animal')),
            1)

    def test_entity_priority(self):
        out = format_parse_output(self.update, {
            'intent': None,
            'intent_ranking': [],
            'entities': [
                {
                    'start': 0,
                    'end': 3,
                    'entity': 'cat',
                    'value': 'cat',
                    'confidence': .9,
                },
            ],
            'labels_as_entity': [
                {
                    'start': 0,
                    'end': 3,
                    'entity': 'animal',
                    'value': 'cat',
                    'confidence': .9,
                    'label_as_entity': True,
                },
            ],
        })
        self.assertEqual(
            len(out.get('entities')),
            1)
