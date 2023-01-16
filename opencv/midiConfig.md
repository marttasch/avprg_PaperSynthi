# Keyboard
- midiChannel: 1
- Velocity: 112
- Channel:
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
- example note_on: [0x90, self.note, 112]
- example note_off: [0x80, self.note, 0]

## Notes:
Oktave 1 / 2
- C: 60 / 72
- C#: 61 / 73
- D: 62 / 74
- D#: 63 / 75
- E: 64 / 76
- F: 65 / 77
- F#: 66 / 78
- G: 67 / 79
- G#: 68 / 80
- A: 69 / 81
- A#: 70 / 82
- B: 72 / 83

---

# Layout - Button, Fader
- midiChannel: 1

[CONTROLL_CHANGE, CC, VALUE]
[0xB0, 0xxx, 0..127]

## Button
<name - CONTROLL_CHANGE - VALUE>

Mode - BANK_SELECT: 0x00 - VALUE: 0..41(Keys), 42..83(Drums), 84..127(Sounds)
Record/play - GENERAL_PURPOSE_CONTROLLER_1: 0x10 - VALUE: 0..63(Play), 64..127(Record)
Distortion - EFFECTS_1: 0x5B - VALUE: 0..63(Off), 64..127(On)
Reverb - EFFECTS_2: 0x5C - VALUE: 0..63(Off), 64..127(On)

## Fader
Pitch - MODULATION: 0x01 - Value: 0..127
Bend - EXPRESSION: 0x0B - Value: 0..127
Gain - VOLUME: 0x07 - Value: 0..127

## Oszi 1
Gain - SOUND_CONTROLLER_1: 0x46 - Value: 0..127
LFO - SOUND_CONTROLLER_2: 0x47 - Value: 0..127
Waveform - SOUND_CONTROLLER_3: 0x48 - Value: 0..31(Sine), 32..63(Triangle), 64..95(Sawtooth), 96..127(Rectangle)

## Oszi 2
Gain - SOUND_CONTROLLER_4: 0x49 - Value: 0..127
LFO - SOUND_CONTROLLER_5: 0x4A - Value: 0..127
Waveform - SOUND_CONTROLLER_6: 0x4B - Value: 0..31(Sine), 32..63(Triangle), 64..95(Sawtooth), 96..127(Rectangle)