import json
from unittest import mock
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.api.views import ExerciseImageViewSet, ExerciseViewSet
from rest_framework.response import Response
from easy_thumbnails.alias import Aliases
from wger.exercises.models.image import ExerciseImage


class ExerciseViewSetTestCase(TestCase):

    def test_get_queryset_filters(self):
        request = HttpRequest()
        request.query_params = {
            "category": "123",
            "muscles": "11,12",
            "muscles_secondary": "12,13",
            "equipment": "22,44",
            "license": "33",
        }
        mocked_qs = mock.Mock()
        mocked_qs.filter.return_value = mocked_qs
        expected_filter_calls = [
            mock.call(exercise_base__category_id=123),
            mock.call(exercise_base__muscles__in=[11,12]),
            mock.call(exercise_base__muscles_secondary__in=[12,13]),
            mock.call(exercise_base__equipment__in=[22,44]),
            mock.call(exercise_base__license_id=33),
        ]

        view_set = ExerciseViewSet(request=request)

        with mock.patch("wger.exercises.api.views.Exercise.objects.all", return_value=mocked_qs):
            qs = view_set.get_queryset()

        mocked_qs.filter.assert_has_calls(expected_filter_calls, any_order=True)
        self.assertEqual(qs, mocked_qs)

    @mock.patch("wger.exercises.api.views.logger")
    def test_get_queryset_value_error(self, mocked_logger):
        request = HttpRequest()
        request.query_params = {
            "category": "1",
            "muscles": "1",
            "muscles_secondary": "1",
            "equipment": "1",
            "license": "1",
        }
        mocked_qs = mock.Mock()
        mocked_qs.filter.side_effect = ValueError()

        view_set = ExerciseViewSet(request=request)

        with mock.patch("wger.exercises.api.views.Exercise.objects.all", return_value=mocked_qs):
            qs = view_set.get_queryset()

        self.assertEqual(qs, mocked_qs)
        self.assertEqual(5, mocked_logger.info.call_count)


class ExerciseImageViewSetTestCase(TestCase):

    def test_thumbnails(self):
        mocked_image = mock.Mock()
        mocked_image.image.url = "original_img_url"

        mocked_thumbnail_alias1 = mock.Mock()
        mocked_thumbnail_alias1.url = "test_url_1"

        mocked_thumbnail_alias2 = mock.Mock()
        mocked_thumbnail_alias2.url = "test_url_2"

        def mocked_get_thumbnail(alias: str) -> mock.Mock:
            if alias == {"setting": "setting1"}:
                return mocked_thumbnail_alias1
            if alias == {"setting": "setting2"}:
                return mocked_thumbnail_alias2
            return None

        mocked_thumbnailer = mock.Mock()
        mocked_thumbnailer.get_thumbnail.side_effect = mocked_get_thumbnail

        aliases = {
            "alias1": {"setting": "setting1"},
            "alias2": {"setting": "setting2"},
        }

        expected_response = Response({
            "original": "original_img_url",
            "alias1": {
                "url": "test_url_1",
                "settings": {"setting": "setting1"}
            },
            "alias2": {
                "url": "test_url_2",
                "settings": {"setting": "setting2"}
            },
        })

        @mock.patch("wger.exercises.api.views.ExerciseImage.objects.get", return_value = mocked_image)
        @mock.patch("wger.exercises.api.views.aliases.all", return_value=aliases)
        @mock.patch("wger.exercises.api.views.aliases.get", side_effect=lambda alias: aliases.get(alias))
        @mock.patch("wger.exercises.api.views.get_thumbnailer", return_value=mocked_thumbnailer)
        def _test(*_):
            view_set = ExerciseImageViewSet()
            return view_set.thumbnails(None, pk=1)

        self.assertEqual(expected_response.data, _test().data)

    @mock.patch("wger.exercises.api.views.ExerciseImage.objects.get", side_effect=ExerciseImage.DoesNotExist())
    def test_thumbnails_no_image(self, _):
        view_set = ExerciseImageViewSet()
        response = view_set.thumbnails(None, pk=1)
        self.assertEquals(Response([]).data, response.data)


class ExerciseSearchTestCase(WgerTestCase):
    def test_search_with_img(self):
        mocked_thumbnail = mock.Mock()
        mocked_thumbnail.url = "test_thumbnail_url"
        mocked_thumbnailer = mock.Mock()
        mocked_thumbnailer.get_thumbnail.return_value = mocked_thumbnail
        with mock.patch("wger.exercises.api.views.get_thumbnailer", return_value=mocked_thumbnailer):
            response = self.client.get(reverse("exercise-search"), {"term": "123", "language": "fr"})

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result), 1)
        suggestion = result['suggestions'][0]
        self.assertEqual(suggestion["value"], "Test exercise 123")
        self.assertEqual(suggestion["data"]["image"], "/media/exercise-images/1/protestschwein.jpg")
        self.assertEqual(suggestion["data"]["image_thumbnail"], "test_thumbnail_url")
