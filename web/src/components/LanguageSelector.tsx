"use client";

import { useEffect, useState } from "react";
import { languages, LanguageCode } from "@/lib/i18n/translations";

const STORAGE_KEY = "sv-live-score-language";

export default function LanguageSelector() {
  const [language, setLanguage] = useState<LanguageCode>("it");

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as LanguageCode | null;
    if (saved && languages.some((item) => item.code === saved)) {
      setLanguage(saved);
    }
  }, []);

  function changeLanguage(code: LanguageCode) {
    setLanguage(code);
    localStorage.setItem(STORAGE_KEY, code);
    window.dispatchEvent(new Event("sv-language-change"));
  }

  return (
    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
      {languages.map((item) => (
        <button
          key={item.code}
          type="button"
          onClick={() => changeLanguage(item.code)}
          title={item.label}
          aria-label={item.label}
          style={{
            border: language === item.code ? "1px solid rgba(255,255,255,.7)" : "1px solid transparent",
            background: language === item.code ? "rgba(255,255,255,.12)" : "transparent",
            borderRadius: 8,
            padding: "4px 6px",
            cursor: "pointer",
            fontSize: 18,
          }}
        >
          {item.flag}
        </button>
      ))}
    </div>
  );
}
