from __future__ import annotations

import json
from pathlib import Path

LANGUAGES = {
    "it": "Italiano",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "pt": "Português",
    "fr": "Français",
}


class I18NService:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent / "i18n"
        self.config_dir = (
            Path.home()
            / "Library"
            / "Application Support"
            / "SV Live Score"
        )
        self.config_file = self.config_dir / "language.json"
        self.language = self._load_language()
        self.translations = {}
        self._load()

    def _load_language(self):
        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
            lang = str(data.get("language", "it"))
            return lang if lang in LANGUAGES else "it"
        except Exception:
            return "it"

    def _load(self):
        path = self.base_dir / f"{self.language}.json"
        try:
            self.translations = json.loads(
                path.read_text(encoding="utf-8")
            )
        except Exception:
            self.translations = {}

    def languages(self):
        return list(LANGUAGES.items())

    def set_language(self, language):
        if language not in LANGUAGES:
            return
        self.language = language
        self._load()
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(
                json.dumps(
                    {"language": language},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            pass

    def get(self, key, default=None):
        value = self.translations.get(key)
        if value is None:
            return default if default is not None else key
        return str(value)

    def t(self, key, default=None):
        return self.get(key, default)

    def __call__(self, key, default=None):
        return self.get(key, default)


I18N = I18NService()
