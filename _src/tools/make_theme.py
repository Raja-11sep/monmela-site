# Makes a short instrumental theme for the website story: "Purano Sei Diner Kotha"
# (Tagore's song about old friends, on the Auld Lang Syne tune). Both are public domain, and
# this recording is synthesised here, so Mon Mela owns it outright.
#
# Arrangement (G major, 66 bpm, ~80 s):
#   intro  : tanpura drone + santoor-like plucks
#   verse  : bansuri-like flute carries the tune; soft chord plucks join on line 2
#   chorus : flowing pluck arpeggios, warm bass and a soft dholak-like pulse
#   outro  : C -> G, the drone fades out (so the loop restarts softly)
#
# Usage: python3 make_theme.py <out.mp3>      needs numpy, scipy, ffmpeg (libmp3lame)
import subprocess
import sys

import numpy as np
import scipy.signal as sg

SR = 44100
BPM = 66
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- the tune (MIDI note, beats)
# Each line is 16 beats: a one-beat pickup, then four bars. G4 = 67 is Sa (do).
L1 = [(62, 1), (67, 1.5), (67, .5), (67, 1), (71, 1), (69, 1.5), (67, .5), (69, 1), (71, 1),
      (67, 1.5), (67, .5), (71, 1), (74, 1), (76, 3)]
L2 = [(76, 1), (74, 1.5), (71, .5), (71, 1), (67, 1), (69, 1.5), (67, .5), (69, 1), (71, 1),
      (67, 1.5), (64, .5), (64, 1), (62, 1), (67, 3)]
L3 = [(76, 1), (74, 1.5), (71, .5), (71, 1), (67, 1), (69, 1.5), (67, .5), (69, 1), (76, 1),
      (74, 1.5), (71, .5), (71, 1), (74, 1), (76, 3)]
L4 = [(79, 1), (74, 1.5), (71, .5), (71, 1), (67, 1), (69, 1.5), (67, .5), (69, 1), (71, 1),
      (67, 1.5), (64, .5), (64, 1), (62, 1), (67, 7)]
MELODY = L1 + L2 + L3 + L4
MEL_START = 11            # beats: 3 intro bars, the pickup on the last beat of the third
BAR1 = 12                 # first full bar of the tune

# Chords per bar from bar 0 (root MIDI note of the chord, chord tones as semitones above it)
G, C, D, EM = (55, (0, 4, 7)), (48, (0, 4, 7)), (50, (0, 4, 7)), (52, (0, 3, 7))
TUNE_CHORDS = [G, D, G, C, G, D, EM, G, G, D, G, C, G, D, EM, G]
CHORDS = [G, C, G] + TUNE_CHORDS + [C, G]          # intro (3) + tune (16) + outro (2)
TOTAL_BEATS = 4 * len(CHORDS)
N = int((TOTAL_BEATS * BEAT + 4.0) * SR)           # + reverb tail


def place(buf, sig, t0, gain=1.0):
    a = int(t0 * SR)
    if a >= len(buf):
        return
    b = min(len(buf), a + len(sig))
    buf[a:b] += gain * sig[:b - a]


def bandpass(x, lo, hi, order=2):
    sos = sg.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sg.sosfilt(sos, x)


def lowpass(x, f, order=2):
    sos = sg.butter(order, f, btype="low", fs=SR, output="sos")
    return sg.sosfilt(sos, x)


# ---------------------------------------------------------------- instruments
def flute_line(notes, start_beat):
    """Bansuri-like flute: one continuous breath with glides (meend) between notes, delayed
    vibrato, breath noise and soft re-articulation. Returns (signal, pitch track)."""
    times, b = [], start_beat
    for m, d in notes:
        times.append((b * BEAT, d * BEAT, hz(m)))
        b += d
    n = int((times[-1][0] + times[-1][1] + 1.0) * SR)
    f = np.zeros(n)
    amp = np.zeros(n)
    puff = np.zeros(n)
    prev = times[0][2]
    for i, (s, d, h) in enumerate(times):
        a, e = int(s * SR), int((s + d) * SR)
        seg = np.arange(e - a) / SR
        g = np.clip(seg / .075, 0, 1)
        g = g * g * (3 - 2 * g)                                   # smooth glide from the last note
        logf = np.log(prev) + (np.log(h) - np.log(prev)) * g
        depth = np.clip((seg - .32) / .55, 0, 1) * .0065          # vibrato grows on held notes
        vib = depth * np.sin(2 * np.pi * 5.0 * seg + rng.uniform(0, 6.28))
        f[a:e] = np.exp(logf) * (1 + vib)
        first, last = i == 0, i == len(times) - 1
        start = 0.0 if first else .58                              # tongued, not silent, between notes
        env = start + (1 - start) * np.clip(seg / .055, 0, 1)
        if d > .8:                                                 # long notes: a gentle swell and settle
            env = env * (1 + .08 * np.sin(np.pi * np.clip(seg / d, 0, 1)))
        if last:
            env = env * np.clip((d - seg) / 2.2, 0, 1) ** 1.2        # the final note fades away
        else:
            env = env * (.62 + .38 * np.clip((d - seg) / .05, 0, 1))
        amp[a:e] = env
        puff[a:e] = np.exp(-seg / .035)
        prev = h
    amp[int(times[-1][0] * SR + times[-1][1] * SR):] = 0
    phase = 2 * np.pi * np.cumsum(f) / SR
    bright = .55 + .45 * amp
    tone = (np.sin(phase) + .42 * bright * np.sin(2 * phase + .3) + .17 * bright * np.sin(3 * phase + .9)
            + .07 * bright * np.sin(4 * phase + 1.7) + .03 * np.sin(5 * phase))
    breath = bandpass(rng.standard_normal(n), 1400, 5200) * (.035 * amp + .09 * puff * (amp > 0))
    out = lowpass(tone * amp + breath, 6500)
    return out, f, amp, start_beat * BEAT


def pluck(h, dur=2.4, bright=1.0):
    """Santoor/harp-like plucked string: harmonics that fade faster the higher they are."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, 14):
        fk = h * k * (1 + .00035 * k * k)
        if fk > 9500:
            break
        y += (bright if k > 1 else 1) / k ** 1.15 * np.exp(-t / (1.5 / (1 + .55 * (k - 1)))) * \
            np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    return y * np.clip(t / .003, 0, 1)


def tanpura(h, dur=4.6):
    """A tanpura string: rich harmonics, with the 'jawari' buzz blooming and shimmering."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, 26):
        fk = h * k
        if fk > 8500:
            break
        bloom = 1 + 1.5 * np.exp(-((k - 9) / 4.5) ** 2) * (1 - np.exp(-t / .5))
        shimmer = 1 + .45 * np.sin(2 * np.pi * (.3 + .06 * k) * t + rng.uniform(0, 6.28))
        y += (1 / k ** .95) * bloom * shimmer * np.exp(-t / (4.2 / (1 + .07 * (k - 1)))) * \
            np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    return y * np.clip(t / .012, 0, 1)


def bass(h, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.clip(t / .05, 0, 1) * np.exp(-t / 2.5) * np.clip((dur - t) / .2, 0, 1)
    return env * (np.sin(2 * np.pi * h * t) + .25 * np.sin(4 * np.pi * h * t))


def dhum(level=1.0):
    """Low dholak stroke: a pitch-dropping thump."""
    t = np.arange(int(.5 * SR)) / SR
    f = 62 + 75 * np.exp(-t / .05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .22)
    click = bandpass(rng.standard_normal(len(t)), 600, 2400) * np.exp(-t / .006) * .25
    return level * (body + click)


def na(level=1.0):
    """High dholak stroke: a short ringing tap."""
    t = np.arange(int(.3 * SR)) / SR
    ring = np.sin(2 * np.pi * 420 * t) * np.exp(-t / .07) * .6
    slap = bandpass(rng.standard_normal(len(t)), 1800, 5200) * np.exp(-t / .018)
    return level * (ring + slap)


def reverb_ir(seed, length=2.6, tau=.6):
    r = np.random.default_rng(seed)
    t = np.arange(int(length * SR)) / SR
    ir = r.standard_normal(len(t)) * np.exp(-t / tau)
    ir = lowpass(ir, 5200)
    ir[:int(.018 * SR)] = 0                                         # 18 ms before the first echo
    return ir / np.sqrt(np.sum(ir ** 2))


# ---------------------------------------------------------------- arrangement
def beat_t(b):
    return b * BEAT


flute = np.zeros(N)
plucks = np.zeros(N)
drone = np.zeros(N)
drums = np.zeros(N)
low = np.zeros(N)

# the tune
fl, pitch, famp, _ = flute_line(MELODY, MEL_START)   # already timed from the start of the track
place(flute, fl, 0)

# tanpura all the way: Pa, Sa, Sa, low Sa, one string per beat
strings = [hz(50), hz(55), hz(55), hz(43)]
for bt in range(0, TOTAL_BEATS - 2):
    place(drone, tanpura(strings[bt % 4]), beat_t(bt) + rng.uniform(-.01, .01), .9)

# intro: a santoor motif on the pentatonic scale over the drone
motif = [67, 71, 74, 76, 74, 71, 69, 67, 71, 74, 79, 76, 74, 71, 74, 76, 79, 74, 71, 69, 67]
for i, m in enumerate(motif):
    bt = i * .5
    if bt > 10.5:
        break
    place(plucks, pluck(hz(m), 2.2, .9), beat_t(bt) + rng.uniform(-.008, .008), .55 if i % 2 == 0 else .4)

for bar, (root, tones) in enumerate(CHORDS):
    b0 = bar * 4
    tune_bar = bar - 3                                              # 0..15 inside the tune
    notes = [root + tones[0], root + tones[1] + 12, root + tones[2]]
    if 4 <= tune_bar < 8:                                            # line 2: soft half-note chords
        for half in (0, 2):
            for j, m in enumerate(sorted(notes)):
                place(plucks, pluck(hz(m), 2.6, .7), beat_t(b0 + half) + j * .035 + rng.uniform(0, .01), .26)
    elif 8 <= tune_bar < 16 or tune_bar >= 16:                       # chorus and outro: flowing arpeggios
        pattern = [root + tones[0], root + tones[2], root + 12, root + tones[1] + 12,
                   root + 12 + tones[2], root + tones[1] + 12, root + 12, root + tones[2]]
        last = tune_bar >= 17
        for k, m in enumerate(pattern):
            if last and k > 0:
                break
            place(plucks, pluck(hz(m), 2.4, .85), beat_t(b0 + k * .5) + rng.uniform(-.006, .006),
                  .3 if k % 2 == 0 else .22)
        place(low, bass(hz(root - 12), 4 * BEAT + (2.5 if last else .05)), beat_t(b0), .5)
        if tune_bar < 16:                                            # dholak pulse in the chorus only
            place(drums, dhum(1.0), beat_t(b0), .55)
            place(drums, na(.6), beat_t(b0 + 1.5), .5)
            place(drums, dhum(.6), beat_t(b0 + 2), .45)
            place(drums, na(.7), beat_t(b0 + 3), .5)
            place(drums, na(.35), beat_t(b0 + 3.5), .45)

# ---------------------------------------------------------------- mix: pan, reverb, master
def stereo(x, pan):
    return np.stack([x * np.cos(pan * np.pi / 2), x * np.sin(pan * np.pi / 2)])


# Levels: the flute carries the tune; the drone sits underneath it, felt more than heard.
FL, PL, DR, DM, LO = .8, .34, .045, .32, .3
dry = (stereo(flute * FL, .5) + stereo(plucks * PL, .62) + stereo(drone * DR, .4)
       + stereo(drums * DM, .5) + stereo(low * LO, .5))
send = (stereo(flute * FL, .5) * .4 + stereo(plucks * PL, .62) * .45 + stereo(drone * DR, .4) * .3
        + stereo(drums * DM, .5) * .18)
irl, irr = reverb_ir(1), reverb_ir(2)
wet = np.stack([sg.fftconvolve(send[0], irl)[:N], sg.fftconvolve(send[1], irr)[:N]])
mix = dry + .9 * wet

t = np.arange(N) / SR
fade_in = np.clip(t / 2.0, 0, 1)
fade_out = np.clip((N / SR - t) / 4.0, 0, 1)
mix *= fade_in * fade_out
mix = lowpass(mix.T, 15000).T
mix /= np.max(np.abs(mix))
mix = np.tanh(1.3 * mix) / np.tanh(1.3)                              # gentle soft limit
mix *= 10 ** (-3.0 / 20)                                             # headroom; loudness is set at encoding

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "story-theme.mp3"
    pcm = (mix.T * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", "loudnorm=I=-18:TP=-2:LRA=11", "-ar", str(SR),          # calm background level
                    "-c:a", "libmp3lame", "-b:a", "160k", "-metadata", "title=Purano Sei Diner Kotha (Mon Mela theme)",
                    "-metadata", "artist=Mon Mela", out], input=pcm, check=True)
    np.save(out + ".pitch.npy", np.stack([pitch, famp]))
    print(out, f"{N / SR:.1f} s")
