"use client";

import type { LiveCommentaryItem } from "./commentaryComposer";
import styles from "./LiveCommentary.module.css";

type Props = {
  item: LiveCommentaryItem | null;
  translations: Record<string, string>;
};

export default function LiveCommentary({ item, translations: t }: Props) {
  return (
    <section className={styles.liveCommentary}>
      <div className={styles.liveCommentaryHeader}>
        <div>
          <span>{t.liveCommentary}</span>
          <h2>{t.matchAction}</h2>
        </div>
        <div className={styles.liveDot}>{t.live}</div>
      </div>
      <div className={styles.liveCommentaryBody}>
        {item ? (
          <>
            <div className={styles.liveCommentaryTime}>{item.time}&apos;</div>
            <div className={styles.liveCommentaryIcon}>{item.icon}</div>
            <div className={styles.liveCommentaryText}>
              <strong>{item.label}</strong>
              {item.player && <span>{item.player}</span>}
              {item.secondary && <small>{item.secondary}</small>}
              {item.club && <small>{item.club}</small>}
            </div>
          </>
        ) : (
          <>
            <div className={styles.liveCommentaryTime}>—</div>
            <div className={styles.liveCommentaryIcon}>⚽</div>
            <div className={styles.liveCommentaryText}>
              <strong>{t.waitingKickoff}</strong>
              <span>{t.kickoffMessage}</span>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
