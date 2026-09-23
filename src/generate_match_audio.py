from pathlib import Path
import math
import random
import wave


OUT = Path("assets/audio")
RATE = 44100


def write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    peak = max(1e-9, max(abs(x) for x in samples))
    gain = min(0.94 / peak, 1.0)

    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)

        frames = bytearray()
        for sample in samples:
            value = int(max(-1.0, min(1.0, sample * gain)) * 32767)
            frames += value.to_bytes(2, "little", signed=True)

        wav.writeframes(frames)


def smooth_noise(
    duration: float,
    seed: int,
    strength: float = 1.0,
    lowpass: float = 0.995,
) -> list[float]:
    rng = random.Random(seed)
    count = int(RATE * duration)
    result = []
    state = 0.0

    for _ in range(count):
        state = state * lowpass + rng.uniform(-1.0, 1.0) * (1.0 - lowpass)
        result.append(state * strength)

    return result


def whistle(
    duration: float = 0.65,
    pitch: float = 3150.0,
) -> list[float]:
    """
    Fischio sportivo sintetizzato con:
    - fondamentale forte
    - armoniche
    - attacco rapido
    - piccola instabilità naturale
    """
    count = int(RATE * duration)
    result = []

    phase = 0.0
    rng = random.Random(int(pitch * 10))

    for i in range(count):
        t = i / RATE

        # Piccola variazione di pitch, quasi impercettibile.
        drift = (
            1.0
            + 0.004 * math.sin(2 * math.pi * 3.7 * t)
            + 0.0015 * rng.uniform(-1.0, 1.0)
        )

        freq = pitch * drift
        phase += 2.0 * math.pi * freq / RATE

        fundamental = math.sin(phase)
        harmonic_2 = math.sin(phase * 2.01) * 0.22
        harmonic_3 = math.sin(phase * 3.01) * 0.10

        attack = min(1.0, t / 0.012)
        release = min(1.0, max(0.0, (duration - t) / 0.075))
        envelope = attack * release

        # Leggerissima "aria" del fischietto.
        breath = math.sin(2 * math.pi * 7200 * t) * 0.025

        result.append(
            (fundamental + harmonic_2 + harmonic_3 + breath)
            * 0.62
            * envelope
        )

    return result


def crowd_burst(
    duration: float,
    seed: int,
    energy: float = 1.0,
) -> list[float]:
    """
    Massa di pubblico più credibile:
    più strati indipendenti, basse frequenze,
    medio-alte e rumore impulsivo.
    """
    rng = random.Random(seed)
    count = int(RATE * duration)

    low = 0.0
    mid = 0.0
    result = []

    for i in range(count):
        t = i / RATE

        n1 = rng.uniform(-1.0, 1.0)
        n2 = rng.uniform(-1.0, 1.0)

        low = low * 0.9992 + n1 * 0.0008
        mid = mid * 0.985 + n2 * 0.015

        rumble = low * 4.0
        voices = mid * 0.75
        air = n1 * 0.08

        # Ondulazione lenta della massa sonora.
        swell = (
            0.72
            + 0.28 * math.sin(2 * math.pi * 0.72 * t + 0.8)
        )

        # Piccoli impulsi irregolari = persone che urlano/clapping.
        pulse = 0.0
        if rng.random() < 0.00055:
            pulse = rng.uniform(0.15, 0.65)

        envelope = min(
            1.0,
            t / 0.035,
            max(0.0, (duration - t) / 0.45),
        )

        result.append(
            (
                rumble * 0.55
                + voices * 0.34
                + air
                + pulse
            )
            * swell
            * energy
            * envelope
        )

    return result


def goal_roar(duration: float = 4.5, seed: int = 1001) -> list[float]:
    """
    Gol:
    impatto iniziale + esplosione del pubblico +
    coda lunga che si assesta.
    """
    count = int(RATE * duration)
    crowd = crowd_burst(duration, seed, 1.0)

    result = []

    for i in range(count):
        t = i / RATE

        # Impatto iniziale molto breve.
        impact_env = math.exp(-t * 12.0)
        impact = (
            math.sin(2 * math.pi * 72 * t)
            + 0.35 * math.sin(2 * math.pi * 118 * t)
        ) * impact_env * 0.30

        # Primo picco della folla.
        surge = math.exp(-t * 1.7) * 0.95

        # Coda più lunga.
        tail = 0.45 + 0.55 * math.exp(-t * 0.22)

        result.append(
            crowd[i] * (0.70 + surge * 0.48) * tail
            + impact
        )

    return result


def red_card_reaction(duration: float = 2.8) -> list[float]:
    whistle_track = whistle(0.58, 3300.0)
    crowd = crowd_burst(duration, 2002, 0.72)

    count = int(RATE * duration)
    result = [0.0] * count

    for i in range(count):
        t = i / RATE

        whistle_value = (
            whistle_track[i]
            if i < len(whistle_track)
            else 0.0
        )

        # Brusio/disapprovazione dopo il fischio.
        boo_env = min(1.0, max(0.0, (t - 0.30) / 0.20))
        boo_env *= min(1.0, max(0.0, (duration - t) / 0.40))

        result[i] = (
            whistle_value * 0.82
            + crowd[i] * boo_env * 0.85
        )

    return result


def concatenate(*tracks: list[float]) -> list[float]:
    result: list[float] = []
    for track in tracks:
        result.extend(track)
    return result


# ------------------------------------------------------------
# MATCH START
# ------------------------------------------------------------

write_wav(
    OUT / "match_start.wav",
    whistle(0.68, 3150.0),
)


# ------------------------------------------------------------
# GOAL
# ------------------------------------------------------------

write_wav(
    OUT / "goal.wav",
    goal_roar(4.5, 1001),
)


# ------------------------------------------------------------
# RED CARD
# ------------------------------------------------------------

write_wav(
    OUT / "red_card.wav",
    red_card_reaction(2.8),
)


# ------------------------------------------------------------
# FINAL WHISTLE
# ------------------------------------------------------------

end_whistle = concatenate(
    whistle(0.48, 3100.0),
    [0.0] * int(RATE * 0.16),
    whistle(0.48, 3250.0),
    [0.0] * int(RATE * 0.18),
    whistle(0.72, 3400.0),
)

write_wav(
    OUT / "match_end.wav",
    end_whistle,
)


print("Generated:")
for path in sorted(OUT.glob("*.wav")):
    with wave.open(str(path), "rb") as wav:
        duration = wav.getnframes() / wav.getframerate()
    print(f"  {path}  {path.stat().st_size:,} bytes  {duration:.2f}s")
