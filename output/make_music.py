#!/usr/bin/env python3
"""Generate an original kawaii-pop BGM (~23s) for the Reel."""
import numpy as np
import wave
import struct

SR = 44100
BPM = 132
BEAT = 60.0 / BPM  # ~0.4545s

def t_arr(seconds):
    return np.linspace(0, seconds, int(SR * seconds), endpoint=False)

def adsr(n, a=0.01, d=0.05, s=0.7, r=0.05):
    a_n = max(1, int(SR * a))
    d_n = max(1, int(SR * d))
    r_n = max(1, int(SR * r))
    s_n = max(1, n - a_n - d_n - r_n)
    env = np.concatenate([
        np.linspace(0, 1, a_n),
        np.linspace(1, s, d_n),
        np.full(s_n, s),
        np.linspace(s, 0, r_n),
    ])
    if env.shape[0] != n:
        env = np.resize(env, n)
    return env

def pluck_env(n, decay=0.6):
    t = np.linspace(0, n / SR, n)
    return np.exp(-t / decay)

def square(t, f, duty=0.5):
    phase = (t * f) % 1.0
    return np.where(phase < duty, 1.0, -1.0)

def saw(t, f):
    phase = (t * f) % 1.0
    return 2.0 * phase - 1.0

def tri(t, f):
    phase = (t * f) % 1.0
    return 4.0 * np.abs(phase - 0.5) - 1.0

def sine(t, f):
    return np.sin(2 * np.pi * f * t)

# --- Note names to frequencies ---
NOTE = {}
for i, name in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]):
    NOTE[name] = i
def freq(note):
    """e.g. 'A4' -> 440.0"""
    if note is None:
        return 0.0
    octave = int(note[-1])
    name = note[:-1]
    n = NOTE[name] + (octave - 4) * 12
    return 440.0 * (2 ** ((n - 9) / 12))  # A4=440, A4 is index 9

def play_note(note, dur, instrument="lead", vel=0.7):
    n = int(SR * dur)
    if note is None or note == "REST":
        return np.zeros(n)
    f = freq(note)
    t = np.linspace(0, dur, n, endpoint=False)
    if instrument == "lead":
        wave_ = 0.6 * tri(t, f) + 0.3 * square(t, f, 0.5) + 0.15 * tri(t, f * 2)
        env = adsr(n, a=0.005, d=0.05, s=0.7, r=0.04)
    elif instrument == "bass":
        wave_ = 0.7 * tri(t, f) + 0.5 * sine(t, f) + 0.2 * square(t, f, 0.3)
        env = adsr(n, a=0.005, d=0.04, s=0.85, r=0.03)
    elif instrument == "pad":
        wave_ = 0.5 * sine(t, f) + 0.3 * sine(t, f * 2) + 0.2 * tri(t, f)
        env = adsr(n, a=0.06, d=0.1, s=0.7, r=0.06)
    elif instrument == "pluck":
        wave_ = 0.6 * tri(t, f) + 0.4 * sine(t, f * 2)
        env = pluck_env(n, decay=dur * 0.45)
    elif instrument == "bell":
        wave_ = 0.5 * sine(t, f) + 0.35 * sine(t, f * 2) + 0.2 * sine(t, f * 3)
        env = pluck_env(n, decay=0.4)
    else:
        wave_ = sine(t, f)
        env = adsr(n)
    # gentle vibrato on lead
    if instrument == "lead":
        vib = 1 + 0.005 * np.sin(2 * np.pi * 5.5 * t)
        wave_ = wave_ * vib
    return wave_ * env * vel

def kick(dur=0.18, vel=0.95):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    pitch = 110 * np.exp(-t * 18) + 50
    sig = np.sin(2 * np.pi * np.cumsum(pitch) / SR)
    env = np.exp(-t * 12)
    click = np.exp(-t * 200) * 0.4 * np.random.uniform(-1, 1, n)
    return (sig * env + click) * vel

def hat(dur=0.05, vel=0.35, open_=False):
    n = int(SR * dur)
    noise = np.random.uniform(-1, 1, n)
    # high-pass-ish: emphasize highs by subtracting smoothed
    sm = np.convolve(noise, np.ones(8) / 8, mode="same")
    hp = noise - sm
    env = np.exp(-np.linspace(0, dur, n) * (15 if not open_ else 6))
    return hp * env * vel

def snare(dur=0.13, vel=0.7):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = np.random.uniform(-1, 1, n)
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 25)
    env = np.exp(-t * 18)
    return (noise * env * 0.7 + tone * 0.6) * vel

def shaker(dur=0.08, vel=0.18):
    n = int(SR * dur)
    noise = np.random.uniform(-1, 1, n)
    env = np.exp(-np.linspace(0, dur, n) * 25)
    return noise * env * vel


# --- Build tracks ---
TOTAL = 23.0  # seconds
TOTAL_N = int(SR * TOTAL)
mix = np.zeros(TOTAL_N)

def add(buf, sig, t_start):
    n0 = int(SR * t_start)
    n1 = min(n0 + len(sig), TOTAL_N)
    if n0 >= TOTAL_N:
        return
    mix_len = n1 - n0
    buf[n0:n1] += sig[:mix_len]

# Chord progression in beats (4/4, ~12 bars = 48 beats)
# Simplified: I - vi - IV - V (key C maj)  :: C - Am - F - G  (each 2 bars)
# Bars 1-2  C
# Bars 3-4  Am
# Bars 5-6  F
# Bars 7-8  G
# Bars 9    C
# Bars 10   Am
# Bars 11   F  G
# Bars 12   C (final hit)

def beats(n):
    return n * BEAT

# --- Bass line (root notes, walking octaves on 8ths) ---
# pattern per bar: root low, root high, fifth low, root high (oodles of bounce)
bass_pattern = {
    "C":  ["C2", "C3", "G2", "C3"],
    "Am": ["A2", "A3", "E2", "A3"],
    "F":  ["F2", "F3", "C3", "F3"],
    "G":  ["G2", "G3", "D3", "G3"],
}

bar_chords = ["C","C","Am","Am","F","F","G","G","C","Am","F","G"]

t = 0.0
for bar_i, ch in enumerate(bar_chords):
    pat = bass_pattern[ch]
    for j in range(8):  # 8 eighth notes per bar
        note = pat[j // 2]
        n = play_note(note, BEAT * 0.5 * 0.95, "bass", vel=0.45)
        add(mix, n, t + BEAT * 0.5 * j)
    t += BEAT * 4
end_bass_t = t

# --- Pad chords (long notes) ---
chord_voicings = {
    "C":  ["E4", "G4", "C5"],
    "Am": ["E4", "A4", "C5"],
    "F":  ["F4", "A4", "C5"],
    "G":  ["G4", "B4", "D5"],
}
t = 0.0
for bar_i, ch in enumerate(bar_chords):
    bar_dur = BEAT * 4 * 0.98
    for note in chord_voicings[ch]:
        n = play_note(note, bar_dur, "pad", vel=0.10)
        add(mix, n, t)
    t += BEAT * 4

# --- Lead melody (catchy hook in C major, kawaii bouncy) ---
# Bar 1-2 (C):    E5  G5  E5 D5  C5 D5 E5 -    (with 8th rests)
# Bar 3-4 (Am):   A5  E5  C5 -   A4 C5 E5 -
# Bar 5-6 (F):    F5  A5  G5 F5  E5 F5 G5 -
# Bar 7-8 (G):    D5  G5  B4 D5  G4 B4 D5 -
# Bar 9-10:       C5 E5 G5 - / A4 C5 E5 -
# Bar 11:         F5 G5 A5 G5 F5 E5 D5 -
# Bar 12:         C5 (held)

# Each list = 8 eighth notes for 2 bars (16 eighths) for first 4 chord groups,
# then 8 eighths each for bars 9 / 10 / 11 / 12.

def melody_bar(notes, t_start, instr="lead", vel=0.55, dur_factor=0.9):
    """notes: list of (note_or_None, beats_duration)"""
    cur = t_start
    for note, b in notes:
        d = b * BEAT
        if note is not None:
            sig = play_note(note, d * dur_factor, instr, vel=vel)
            add(mix, sig, cur)
        cur += d

# Bars 1-2 (C)  -- riff up
melody_bar([
    ("E5", 1), ("G5", 1), ("E5", 0.5), ("D5", 0.5), ("C5", 0.5), ("D5", 0.5), ("E5", 1),
    ("G5", 1), ("E5", 0.5), ("C5", 0.5), ("D5", 1), ("E5", 1),
], 0.0)

# Bars 3-4 (Am)
melody_bar([
    ("A5", 1), ("E5", 1), ("C5", 0.5), ("E5", 0.5), ("A4", 1),
    ("C5", 1), ("E5", 0.5), ("A4", 0.5), ("E5", 1), ("C5", 1),
], BEAT * 8)

# Bars 5-6 (F)
melody_bar([
    ("F5", 1), ("A5", 1), ("G5", 0.5), ("F5", 0.5), ("E5", 1),
    ("F5", 1), ("G5", 0.5), ("A5", 0.5), ("G5", 1), ("F5", 1),
], BEAT * 16)

# Bars 7-8 (G)
melody_bar([
    ("D5", 1), ("G5", 1), ("B4", 0.5), ("D5", 0.5), ("G4", 1),
    ("B4", 1), ("D5", 0.5), ("G5", 0.5), ("F5", 1), ("D5", 1),
], BEAT * 24)

# Bar 9 (C)
melody_bar([
    ("C5", 1), ("E5", 1), ("G5", 1), ("C6", 1),
], BEAT * 32)

# Bar 10 (Am)
melody_bar([
    ("A5", 1), ("G5", 0.5), ("E5", 0.5), ("C5", 1), ("E5", 1),
], BEAT * 36)

# Bar 11 (F G)
melody_bar([
    ("F5", 0.5), ("G5", 0.5), ("A5", 0.5), ("G5", 0.5),
    ("F5", 0.5), ("E5", 0.5), ("D5", 0.5), ("E5", 0.5),
], BEAT * 40)

# Bar 12 (C, final hit) - hold
melody_bar([("C5", 4)], BEAT * 44, vel=0.5, dur_factor=0.95)

# --- Bell sparkle counter-melody (octave above lead, sparser) ---
melody_bar([("E6", 1), ("G6", 1), (None, 2)], 0.0, instr="bell", vel=0.18)
melody_bar([("E6", 1), ("A5", 1), (None, 2)], BEAT * 8, instr="bell", vel=0.18)
melody_bar([("F6", 1), ("A6", 1), (None, 2)], BEAT * 16, instr="bell", vel=0.18)
melody_bar([("D6", 1), ("G6", 1), (None, 2)], BEAT * 24, instr="bell", vel=0.18)
melody_bar([("C6", 2), (None, 2)], BEAT * 32, instr="bell", vel=0.18)
melody_bar([("E6", 4)], BEAT * 44, instr="bell", vel=0.16)

# --- Drums ---
# Kick on 1, 3 of every bar; snare on 2, 4; hat on every 8th
for bar in range(12):
    bt = bar * BEAT * 4
    # kicks
    add(mix, kick(0.18, vel=0.95), bt + 0)
    add(mix, kick(0.18, vel=0.85), bt + 2 * BEAT)
    # extra ghost kick on bar 4, 8, 12 to add lift
    if bar in (3, 7, 11):
        add(mix, kick(0.12, vel=0.6), bt + 3.5 * BEAT)
    # snares (back beat)
    add(mix, snare(0.13, vel=0.55), bt + 1 * BEAT)
    add(mix, snare(0.13, vel=0.55), bt + 3 * BEAT)
    # hats every 8th
    for j in range(8):
        v = 0.20 if j % 2 == 0 else 0.14
        add(mix, hat(0.05, vel=v), bt + j * 0.5 * BEAT)
    # shaker on offbeats
    for j in range(1, 8, 2):
        add(mix, shaker(0.05, vel=0.10), bt + j * 0.5 * BEAT)

# --- Intro pluck pickup (very first 0.5 beat before bar 1) ---
# Actually start cleanly. Just add a soft cymbal swoosh.
def crash(dur=0.6, vel=0.6):
    n = int(SR * dur)
    noise = np.random.uniform(-1, 1, n)
    env = np.exp(-np.linspace(0, dur, n) * 4)
    return noise * env * vel
add(mix, crash(0.7, vel=0.25), 0.0)
add(mix, crash(0.5, vel=0.25), BEAT * 32)  # bar 9 lift

# --- Final hit emphasize ---
add(mix, kick(0.25, vel=1.0), BEAT * 44)
add(mix, crash(1.0, vel=0.45), BEAT * 44)

# --- Master: soft compression + normalize + mild stereo widening ---
# Soft saturation
mix = np.tanh(mix * 0.9)
# normalize
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.92

# Convert to 16-bit stereo (slight pan: bass center, lead a bit right, bell left)
# To keep simple and avoid bleed, just duplicate mono.
left = mix.copy()
right = mix.copy()

# Add subtle stereo on bell — but we already mixed mono. Skip.
stereo = np.stack([left, right], axis=1)
ints = np.clip(stereo * 32767, -32768, 32767).astype(np.int16)

with wave.open("/tmp/oden_work/bgm.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(ints.tobytes())
print("wrote /tmp/oden_work/bgm.wav  duration:", TOTAL, "s")
