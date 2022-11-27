from json import load
from wger.config.models.language_config import LanguageConfig
from wger.core.models.language import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.language import load_language, load_item_languages, load_ingredient_languages
from unittest import mock

class LoadLanguageTestCase(WgerTestCase):
    def test_load_cached_language(self):
        expected_language = Language(short_name="sk", full_name="Slovak")
        with mock.patch("wger.utils.language.cache", {"language-sk": expected_language}):
            language = load_language("sk")
        self.assertEqual(expected_language, language)

    def test_load_translation_language_on_none(self):
        expected_language = Language(short_name="sk", full_name="Slovak")
        expected_language.save()

        with mock.patch("wger.utils.language.translation.get_language", lambda: "sk-SK"):
            language = load_language(None)

        self.assertEqual(expected_language, language)

    def test_load_default_language_if_not_found(self):
        expected_language = Language.objects.get(short_name="en")
        language = load_language("sk")
        self.assertEqual(expected_language, language)

    def test_item_languages_no_language_config(self):
        with mock.patch("wger.utils.language.LanguageConfig.objects.filter", return_value=[]):
            languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES, "fr")
        self.assertEqual(1, len(languages))
        self.assertEqual("en", languages[0].short_name)
        self.assertEqual("English", languages[0].full_name)

    def test_load_ingredient_languages(self):
        mocked_request = mock.Mock()
        mocked_request.user.userprofile.show_english_ingredients = True

        language = Language.objects.get(short_name="fr")
        expected_language = Language.objects.get(pk=2)

        @mock.patch("wger.utils.language.load_language", return_value=language)
        @mock.patch("wger.utils.language.load_item_languages", return_value=[language])
        def _test(*_):
            return load_ingredient_languages(mocked_request)

        languages = _test()
        self.assertIn(expected_language, languages)

