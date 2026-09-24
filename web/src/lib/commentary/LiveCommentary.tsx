"use client";

import type { LiveCommentaryItem } from "./commentaryComposer";
import styles from "./LiveCommentary.module.css";

type Props = {
  item: LiveCommentaryItem | null;
};

export default function LiveCommentary({ item }: Props) {
  return (
    <section className={styles.liveCommentary}>
      <div className={styles.liveCommentaryHeader}>
        <div>
          <span>LIVE COMMENTARY</span>
          <h2>Match action</h2>
        </div>
        <div className={styles.liveDot}>LIVE</div>
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
              <strong>WAITING FOR KICK-OFF</strong>
              <span>La partita sta per iniziare</span>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
