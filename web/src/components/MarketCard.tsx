"use client";

import { useEffect, useState } from "react";
import styles from "./MarketCard.module.css";

type MarketData = {
  svc: number | null;
  eth: number | null;
  pol: number | null;
  updatedAt: number;
};

function formatPrice(value: number | null, decimals: number) {
  if (value === null) return "—";

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export default function MarketCard() {
  const [market, setMarket] = useState<MarketData | null>(null);

  useEffect(() => {
    let active = true;

    const loadMarket = async () => {
      try {
        const response = await fetch("/api/market", {
          cache: "no-store",
        });

        if (!response.ok) return;

        const data = await response.json();

        if (active) {
          setMarket(data);
        }
      } catch {
        // Keep the last valid market values visible.
      }
    };

    loadMarket();

    const interval = window.setInterval(loadMarket, 30000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  return (
    <section className={styles.card} aria-label="Market">
      <div className={styles.header}>
        <span className={styles.title}>💱 MARKET</span>
        <span className={styles.live}>
          <span className={styles.dot} />
          LIVE
        </span>
      </div>

      <div className={styles.prices}>
        <div className={styles.item}>
          <span className={`${styles.asset} ${styles.svc}`}>SVC</span>
          <span className={styles.pair}>/ USDC</span>
          <span className={styles.value}>
            ${formatPrice(market?.svc ?? null, 6)}
          </span>
        </div>

        <div className={styles.item}>
          <span className={`${styles.asset} ${styles.eth}`}>ETH</span>
          <span className={styles.pair}>/ USDC</span>
          <span className={styles.value}>
            ${formatPrice(market?.eth ?? null, 2)}
          </span>
        </div>

        <div className={styles.item}>
          <span className={`${styles.asset} ${styles.pol}`}>POL</span>
          <span className={styles.pair}>/ USDC</span>
          <span className={styles.value}>
            ${formatPrice(market?.pol ?? null, 6)}
          </span>
        </div>
      </div>
    </section>
  );
}
