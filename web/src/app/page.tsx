"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import LanguageSelector from "@/components/LanguageSelector";
import { translations, LanguageCode } from "@/lib/i18n/translations";
import styles from "./page.module.css";

type ClubData = {
  id: number;
  name: string;
  colors: number[] | null;
  logo: string | null;
};

type MatchTeam = ClubData;

type Match = {
  fixtureId: number;
  homeClubId: number;
  awayClubId: number;
  home: MatchTeam;
  away: MatchTeam;
  homeGoals: number;
  awayGoals: number;
  played: boolean;
  datetime: string;
  competition: string;
};

export default function Home() {
  const [clubId, setClubId] = useState("");
  const [language, setLanguage] = useState<LanguageCode>("it");
  const [club, setClub] = useState<ClubData | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [favorites, setFavorites] = useState<number[]>([]);
  const [favoriteClubs, setFavoriteClubs] = useState<Record<number, ClubData>>({});
  const [favoritesReady, setFavoritesReady] = useState(false);
  const t = translations[language];

  useEffect(() => {
    const saved = localStorage.getItem("sv-live-score-language") as LanguageCode | null;
    if (saved && translations[saved]) setLanguage(saved);

    const handleLanguageChange = () => {
      const current = localStorage.getItem("sv-live-score-language") as LanguageCode | null;
      if (current && translations[current]) setLanguage(current);
    };

    window.addEventListener("sv-language-change", handleLanguageChange);
    return () => window.removeEventListener("sv-language-change", handleLanguageChange);
  }, []);



  useEffect(() => {
    try {
      const raw = window.localStorage.getItem("sv-live-score-favorites");
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          const cleaned = parsed
            .map((value) => Number(value))
            .filter((value) => Number.isInteger(value) && value > 0)
            .slice(0, 10);
          setFavorites(cleaned);
        }
      }
    } catch {
      // Ignore malformed local storage.
    } finally {
      setFavoritesReady(true);
    }
  }, []);

  useEffect(() => {
    if (!favoritesReady || favorites.length === 0) return;

    void Promise.all(
      favorites.map(async (id) => {
        if (favoriteClubs[id]) return;

        try {
          const response = await fetch("/api/club/" + id, {
            cache: "no-store",
          });

          if (!response.ok) return;

          const data: ClubData = await response.json();

          setFavoriteClubs((current) => ({
            ...current,
            [id]: data,
          }));
        } catch {
          // Ignore unavailable favorite clubs.
        }
      }),
    );
  }, [favorites, favoritesReady, favoriteClubs]);

  useEffect(() => {
    if (!favoritesReady) return;
    window.localStorage.setItem(
      "sv-live-score-favorites",
      JSON.stringify(favorites.slice(0, 10)),
    );
  }, [favorites, favoritesReady]);

  function toggleFavorite(id: number) {
    setFavorites((current) =>
      current.includes(id)
        ? current.filter((value) => value !== id)
        : current.length >= 10
          ? current
          : [...current, id],
    );
  }

  const isFavorite = club ? favorites.includes(club.id) : false;

  async function loadClub(id: string) {
    const normalizedId = id.trim();

    if (!normalizedId) {
      setError("Inserisci un Club ID.");
      setClub(null);
      setMatches([]);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const clubResponse = await fetch("/api/club/" + normalizedId, {
        cache: "no-store",
      });

      if (!clubResponse.ok) {
        const data = await clubResponse.json().catch(() => null);
        throw new Error(data?.error || "Club non trovato.");
      }

      const clubData: ClubData = await clubResponse.json();

      const matchesResponse = await fetch(
        "/api/club/" + normalizedId + "/matches",
        { cache: "no-store" }
      );

      if (!matchesResponse.ok) {
        const data = await matchesResponse.json().catch(() => null);
        throw new Error(data?.error || "Impossibile caricare le partite.");
      }

      const matchesData = await matchesResponse.json();

      setClub(clubData);
      setMatches(matchesData.matches || []);
    } catch (err) {
      setClub(null);
      setMatches([]);
      setError(
        err instanceof Error
          ? err.message
          : "Errore durante la ricerca."
      );
    } finally {
      setLoading(false);
    }
  }

  async function searchClub() {
    await loadClub(clubId);
  }
  function handleKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "Enter") {
      searchClub();
    }
  }

  function formatDate(value: string) {
    const date = new Date(value.replace(" ", "T"));
    if (Number.isNaN(date.getTime())) return value;

    return new Intl.DateTimeFormat("it-IT", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(date);
  }

  function formatTime(value: string) {
    const date = new Date(value.replace(" ", "T"));
    if (Number.isNaN(date.getTime())) return "";

    return new Intl.DateTimeFormat("it-IT", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  }

  function teamColor(team: MatchTeam) {
    if (team.colors?.length === 3) {
      return "rgb(" + team.colors.join(", ") + ")";
    }
    return "#55c2ff";
  }

  const playedMatches = matches.filter((match) => match.played);
  const upcomingMatches = matches.filter((match) => !match.played);

  const lastMatch =
    playedMatches.length > 0
      ? playedMatches[playedMatches.length - 1]
      : null;

  const nextMatch =
    upcomingMatches.length > 0
      ? upcomingMatches[0]
      : null;

  const calendarMatches = matches.filter(
    (match) => match !== lastMatch && match !== nextMatch
  );

  const clubColor =
    club?.colors?.length === 3
      ? "rgb(" + club.colors.join(", ") + ")"
      : "#55c2ff";

  return (
    <main className={styles.page}>
      <div className={styles.backgroundGlow} />

      <section className={styles.container}>
        <header className={styles.header}>\n            <LanguageSelector />
          <div className={styles.brand}>
            <div className={styles.logo}>⚽</div>
            <div>
              <h1>SV LIVE SCORE</h1>
              <p>{t.matchCenter}</p>
            </div>
          </div>

          <div className={styles.status}>
            <span className={styles.statusDot} />
            ONLINE
          </div>
        </header>

        <section className={styles.hero}>
          <span className={styles.eyebrow}>
            SOCCERVERSE MATCH CENTER
          </span>

          <h2>{t.followMatches}</h2>

          <p className={styles.heroText}>
            {t.heroText}
          </p>

          <div className={styles.searchBox}>
            <label htmlFor="clubId">{t.clubId}</label>

            <div className={styles.searchRow}>
              <input
                id="clubId"
                type="number"
                min="1"
                placeholder="Es. 3340"
                value={clubId}
                onChange={(event) => setClubId(event.target.value)}
                onKeyDown={handleKeyDown}
              />

              <button
                type="button"
                onClick={searchClub}
                disabled={loading}
              >
                {loading ? t.loading : t.search}
              </button>
            </div>

            {error && (
              <p className={styles.error}>{error}</p>
            )}
          </div>

          {favorites.length > 0 && (
            <div className={styles.favoriteBar}>
              <div className={styles.favoriteBarHeader}>
                <span className={styles.eyebrow}>{t.yourClubs}</span>
                <span>{favorites.length}/10</span>
              </div>

              <div className={styles.favoriteList}>
                {favorites.map((id) => (
                  <button
                    key={id}
                    type="button"
                    className={
                      id === club?.id
                        ? styles.favoriteChipActive
                        : styles.favoriteChip
                    }
                    onClick={() => {
                      setClubId(String(id));
                      void loadClub(String(id));
                    }}
                  >
                    {favoriteClubs[id] ? (
                      <>
                        {favoriteClubs[id].logo ? (
                          <img
                            src={favoriteClubs[id].logo}
                            alt=""
                            className={styles.favoriteChipLogo}
                          />
                        ) : (
                          <span>⚽</span>
                        )}
                        <span>{favoriteClubs[id].name}</span>
                      </>
                    ) : (
                      "#" + id
                    )}
                  </button>
                ))}
              </div>

            </div>
          )}
        </section>

        {club && (
          <>
            <section
              className={styles.clubCard}
              style={{
                borderColor: "rgba(" +
                  club.colors?.join(", ") +
                  ", 0.35)",
                boxShadow:
                  "0 25px 70px rgba(" +
                  club.colors?.join(", ") +
                  ", 0.12)",
              }}
            >
              <div
                className={styles.clubAccent}
                style={{ background: clubColor }}
              />

              <div className={styles.clubLogoWrap}>
                {club.logo ? (
                  <img
                    src={club.logo}
                    alt={club.name}
                    className={styles.clubLogo}
                  />
                ) : (
                  <span className={styles.clubLogoFallback}>
                    ⚽
                  </span>
                )}
              </div>

              <div className={styles.clubInfo}>
                <span className={styles.eyebrow}>
                  {t.clubFound}
                </span>
                <h3>{club.name}</h3>
                <p>Club ID {club.id}</p>
              </div>

              <button
                type="button"
                className={
                  isFavorite
                    ? styles.favoriteToggleActive
                    : styles.favoriteToggle
                }
                onClick={() => toggleFavorite(club.id)}
                disabled={!isFavorite && favorites.length >= 10}
                title={
                  isFavorite
                    ? t.removeFavorite
                    : favorites.length >= 10
                      ? t.favoriteLimit
                      : t.saveFavorite
                }
              >
                {isFavorite ? "★" : "☆"}
                <span>{isFavorite ? "PREFERITO" : "SALVA"}</span>
              </button>
            </section>

            <section className={styles.matches}>
              <div className={styles.sectionHeader}>
                <div>
                  <span className={styles.eyebrow}>
                    MATCH CENTER
                  </span>
                  <h3>{club.name}</h3>
                </div>

                <span className={styles.liveBadge}>
                  {matches.length} MATCH
                </span>
              </div>

              <div className={styles.featuredGrid}>
                {lastMatch && (
                  <MatchCard
                    match={lastMatch}
                    label={t.lastMatch}
                    variant="last"
                    hideScore
                    formatDate={formatDate}
                    formatTime={formatTime}
                    teamColor={teamColor}
                  />
                )}

                {nextMatch && (
                  <MatchCard
                    match={nextMatch}
                    label={t.nextMatch}
                    variant="next"
                    formatDate={formatDate}
                    formatTime={formatTime}
                    teamColor={teamColor}
                  />
                )}
              </div>

              <div className={styles.calendarHeader}>
                <div>
                  <span className={styles.eyebrow}>
                    {t.calendar}
                  </span>
                  <h4>{t.allMatches}</h4>
                </div>
              </div>

              <div className={styles.calendar}>
                {calendarMatches.map((match) => (
                  <MatchRow
                    key={match.fixtureId}
                    match={match}
                    formatDate={formatDate}
                    formatTime={formatTime}
                    teamColor={teamColor}
                  />
                ))}
              </div>
            </section>
          </>
        )}

        {!club && (
          <section className={styles.matches}>
            <div className={styles.sectionHeader}>
              <div>
                <span className={styles.eyebrow}>
                  MATCH CENTER
                </span>
                <h3>{t.yourMatches}</h3>
              </div>
              <span className={styles.liveBadge}>
                {t.liveReady}
              </span>
            </div>

            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>⚽</div>
              <h4>{t.noMatchSelected}</h4>
              <p>
                {t.startMessage}
              </p>
            </div>
          </section>
        )}

        <section className={styles.supportCard}>
          <div className={styles.supportGlow} />
          <div className={styles.supportContent}>
            <div className={styles.supportIcon}>☕</div>
            <div className={styles.supportText}>
              <span className={styles.supportEyebrow}>{t.supportEyebrow}</span>
              <h3>{t.supportTitle}</h3>
              <p>
                {t.supportCopy}
              </p>
              <span className={styles.supportNote}>{t.supportCreated}</span>
            </div>
            <a
              className={styles.supportButton}
              href="https://play.soccerverse.com/profile?user=SirAlex79"
              target="_blank"
              rel="noreferrer"
            >
              ☕ TIP ME WITH SVC
            </a>
          </div>
        </section>

        <footer className={styles.footer}>
          <span>SV LIVE SCORE</span>

          <a
            href="https://play.soccerverse.com/profile?user=SirAlex79"
            target="_blank"
            rel="noreferrer"
          >
            {t.support}
          </a>
        </footer>
      </section>
    </main>
  );
}

function MatchCard({
  match,
  label,
  variant,
  hideScore = false,
  formatDate,
  formatTime,
  teamColor,
}: {
  match: Match;
  label: string;
  variant: "last" | "next";
  hideScore?: boolean;
  formatDate: (value: string) => string;
  formatTime: (value: string) => string;
  teamColor: (team: MatchTeam) => string;
}) {
  const router = useRouter();
  return (
    <article
      className={`${styles.matchCard} ${
        variant === "next" ? styles.matchCardNext : ""
      }`}
      role="button"
      tabIndex={0}
      onClick={() => router.push("/match/" + match.fixtureId)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          router.push("/match/" + match.fixtureId);
        }
      }}
      style={{
        borderColor:
          variant === "next"
            ? "rgba(74,222,128,0.25)"
            : "rgba(255,255,255,0.08)",
        ["--home-color" as string]: teamColor(match.home),
      }}
    >
      <div className={styles.matchCardTop}>
        <span className={styles.eyebrow}>{label}</span>

        <span
          className={
            variant === "next"
              ? styles.nextBadge
              : styles.finalBadge
          }
        >
          {variant === "next" ? "🕐" : "🏁"} {label}
        </span>
      </div>

      <div className={styles.matchDate}>
        {formatDate(match.datetime)} · {formatTime(match.datetime)}
      </div>

      <div className={styles.teams}>
        <TeamDisplay
          team={match.home}
          color={teamColor(match.home)}
          compact
        />

        <div className={styles.scoreBlock}>
          <strong>
            {hideScore
              ? "VS"
              : match.played
                ? match.homeGoals + " - " + match.awayGoals
                : "VS"}
          </strong>
        </div>

        <TeamDisplay
          team={match.away}
          color={teamColor(match.away)}
          compact
        />
      </div>

      <div className={styles.matchMeta}>
        <span>{match.played ? match.competition || "Soccerverse" : "🕐 PROGRAMMATA"}</span>
        <span>#{match.fixtureId}</span>
      </div>
    </article>
  );
}

function MatchRow({
  match,
  formatDate,
  formatTime,
  teamColor,
}: {
  match: Match;
  formatDate: (value: string) => string;
  formatTime: (value: string) => string;
  teamColor: (team: MatchTeam) => string;
}) {
  const router = useRouter();
  return (
    <article
      className={`${styles.matchRow} ${
        match.played ? styles.matchRowPlayed : styles.matchRowUpcoming
      }`}
      style={{
        ["--home-color" as string]: teamColor(match.home),
      }}
      role="button"
      tabIndex={0}
      onClick={() => router.push("/match/" + match.fixtureId)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          router.push("/match/" + match.fixtureId);
        }
      }}
    >
      <div className={styles.rowDate}>
        <strong>{formatDate(match.datetime)}</strong>
        <span>{formatTime(match.datetime)}</span>
      </div>

      <TeamDisplay
        team={match.home}
        compact
        color={teamColor(match.home)}
      />

      <div className={styles.rowScore}>
        {match.played
          ? match.homeGoals + " - " + match.awayGoals
          : "VS"}
      </div>

      <TeamDisplay
        team={match.away}
        compact
        color={teamColor(match.away)}
      />

      <div className={styles.rowCompetition}>
        {match.competition || "Soccerverse"}
      </div>
    </article>
  );
}

function TeamDisplay({
  team,
  color,
  compact = false,
}: {
  team: MatchTeam;
  color: string;
  compact?: boolean;
}) {
  return (
    <div
      className={
        compact
          ? styles.teamCompact
          : styles.team
      }
    >
      <div
        className={
          compact
            ? styles.rowLogo
            : styles.teamLogo
        }
        style={{
          borderColor: color,
          boxShadow:
            "0 0 20px " + color + "22",
        }}
      >
        {team.logo ? (
          <img
            src={team.logo}
            alt={team.name}
          />
        ) : (
          <span>⚽</span>
        )}
      </div>

      <span
        className={
          compact
            ? styles.rowTeamName
            : styles.teamName
        }
      >
        {team.name || "TBD"}
      </span>
    </div>
  );
}
