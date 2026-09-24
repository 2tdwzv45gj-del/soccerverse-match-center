# Soccerverse Match Center

A web-based live match center for Soccerverse.

Soccerverse Match Center lets users search for Soccerverse clubs and follow their matches with live match information, replay controls, commentary, lineups, goals, cards, substitutions, tactics and mentality changes.

The application is designed to work directly in the browser, on both desktop and mobile, without requiring users to install anything.

## 🌐 Live Demo

**Soccerverse Match Center**

https://soccerverse-match-center.vercel.app/

---

## ✨ Features

### ⚽ Match Center

- Search matches by Soccerverse Club ID
- View recent and upcoming matches
- Home and away team information
- Club logos and team colours
- Stadium information and imagery
- Match score and status

### 🔴 Live Commentary

Live match commentary includes:

- Goals
- Yellow cards
- Red cards
- Substitutions
- Match events
- Event times
- Player information

### ▶️ Match Replay

The replay system allows users to move through a match timeline and reconstruct the match state at different moments.

Replay information includes:

- Match minute
- Score
- Match events
- Starting lineups
- Tactical state
- Formation
- Playing style
- Tactical changes

### 🧠 Tactics & Mentality

The Match Center tracks tactical information during the match, including:

- Formation
- Playing style
- Tactical changes
- Situational tactical states
- Tactical timeline

Formation snapshots that do not represent an actual visible tactical change are kept as part of the match timeline without being incorrectly reported as a tactical change.

### 👥 Starting Lineups

Starting lineups are available for both teams, including player information and club affiliation.

### 🌍 Multilingual Interface

The interface currently supports:

- 🇮🇹 Italian
- 🇬🇧 English
- 🇪🇸 Spanish
- 🇫🇷 French
- 🇩🇪 German
- 🇵🇹 Portuguese

The selected language is remembered by the application.

### 💱 Market

The home page includes a live market section displaying:

- SVC / USDC
- ETH / USDC
- POL / USDC

Market data is periodically refreshed automatically.

### 📱 Responsive Design

The interface is optimized for:

- Desktop
- Tablet
- Mobile
- iPhone

The match interface adapts its layout for smaller screens while keeping the main match information and replay controls accessible.

---

## 🛠️ Technology

The project is built with:

- Next.js
- React
- TypeScript
- CSS Modules
- Next.js API Routes

The application is deployed on Vercel.

---

## 📡 Data

The application uses Soccerverse data to retrieve match information, commentary, players, tactics and other match-related information.

Some market data is retrieved through the Soccerverse MCP service and cryptocurrency market data through CoinGecko.

The application also uses Soccerverse/Rincon datapack data for player and club information, including names, logos and colours.

---

## 🚀 Running Locally

Clone the repository:

```bash
git clone https://github.com/2tdwzv45gj-del/soccerverse-match-center.git
cd soccerverse-match-center/web
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

http://localhost:3000

---

## 🏗️ Production Build

To create a production build:

```bash
npm run build
```

To run the production build locally:

```bash
npm run start
```

---

## 🎯 Project Goal

The goal of Soccerverse Match Center is to provide a simple and accessible way to follow Soccerverse matches directly from a web browser.

The project focuses on making match information easier to follow in real time while also providing a replay-oriented view of what happened during the match.

---

## 📰 Soccerverse Community & Friends

Looking for more Soccerverse content?

Check out **Soccerverse Tool**, a community site where you can read in-game news, follow what is happening around Soccerverse and have a few good laughs along the way. 😄

👉 https://soccerversetool.vercel.app/

A friendly place to keep an eye on the Soccerverse world beyond the matches.

---

## 👤 About the Project

Soccerverse Match Center was created by **Alessio Vernacotola (SirAlex79)**, a Soccerverse player and enthusiast.

👉 https://play.soccerverse.com/profile?user=SirAlex79

This project was born from an idea I believed in, despite having limited software development experience.

It has been built step by step through learning, experimentation, problem solving and a lot of trial and error, with the goal of creating something useful for the Soccerverse community.

What started as an idea gradually became a fully functional web application for following Soccerverse matches.

A lot of work has gone into making the Match Center available **completely free of charge**, with no subscription required.

---

## 💛 Support the Project

Soccerverse Match Center is completely free to use.

If you enjoy the project and would like to support its development, you can send a small SVC tip directly to **SirAlex79** through Soccerverse.

👉 **Send SVC to SirAlex79:** https://play.soccerverse.com/profile?user=SirAlex79

The support link is also available directly in the application's Home page.

There is absolutely no obligation — every tip is simply a nice way of saying thank you and helps support the continued development of the project. ❤️

Every contribution is a small but meaningful way of saying:

**Keep going.**

---

## ⚽ Made for the Soccerverse Community

This project is made with the Soccerverse community in mind.

If you find a bug, have an idea, or think something could be improved, feedback is always welcome.

Thank you for using Soccerverse Match Center. ❤️

---

## 📌 Status

The project is actively under development.

New features and improvements are being developed progressively.

---

## 📄 License

This project is currently provided as-is for the Soccerverse community.

---

**Built for the Soccerverse community ⚽**

**Created by Alessio Vernacotola — SirAlex79**
