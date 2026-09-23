"use client";

import type { LiveCommentaryItem } from "./commentaryComposer";

type Props = {
  item: LiveCommentaryItem | null;
};

export default function LiveCommentary({ item }: Props) {
  return (
    <section className="liveCommentary">
      <div className="liveCommentaryHeader">
        <div>
          <span>LIVE COMMENTARY</span>
          <h2>Match action</h2>
        </div>
        <div className="liveDot">LIVE</div>
      </div>
      <div className="liveCommentaryBody">
        {item ? (
          <>
            <div className="liveCommentaryTime">{item.time}&apos;</div>
            <div className="liveCommentaryIcon">{item.icon}</div>
            <div className="liveCommentaryText">
              <strong>{item.label}</strong>
              {item.player && <span>{item.player}</span>}
              {item.secondary && <small>{item.secondary}</small>}
              {item.club && <small>{item.club}</small>}
            </div>
          </>
        ) : (
          <>
            <div className="liveCommentaryTime">—</div>
            <div className="liveCommentaryIcon">⚽</div>
            <div className="liveCommentaryText">
              <strong>WAITING FOR KICK-OFF</strong>
              <span>La partita sta per iniziare</span>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
