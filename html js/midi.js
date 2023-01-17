if (navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess({sysex: false}).then(function (midiAccess) {
        midi = midiAccess;
        var inputs = midi.inputs.values();
        // loop through all inputs
        for (var input = inputs.next(); input && !input.done; input = inputs.next()) {
            // listen for midi messages
            input.value.onmidimessage = onMIDIMessage;
        }
    });
} else {
    alert("No MIDI support in your browser.");
}

function convertMidi() {
    const midiNote = [];
    for (let i = 0; i < 9; i++) {
        midiNote[i] = [];
    }

    midiNote[60] = ["C", 0, 3];
    midiNote[61] = ["C#", 1, 3];
    midiNote[62] = ["D", 2, 3];
    midiNote[63] = ["D#", 3, 3];
    midiNote[64] = ["E", 4, 3];
    midiNote[65] = ["F", 5, 3];
    midiNote[66] = ["F#", 6, 3];
    midiNote[67] = ["G", 7, 3];
    midiNote[68] = ["G#", 8, 3];
    midiNote[69] = ["A", 9, 3];
    midiNote[70] = ["A#", 10, 3];
    midiNote[71] = ["B", 11, 3];

    midiNote[72] = ["C", 12, 4];
    midiNote[73] = ["C#", 13, 4];
    midiNote[74] = ["D", 14, 4];
    midiNote[75] = ["D#", 15, 4];
    midiNote[76] = ["E", 16, 4];
    midiNote[77] = ["F", 17, 4];
    midiNote[78] = ["F#", 18, 4];
    midiNote[79] = ["G", 19, 4];
    midiNote[80] = ["G#", 20, 4];
    midiNote[81] = ["A", 21, 4];
    midiNote[82] = ["A#", 22, 4];
    midiNote[83] = ["B", 23, 4];

    return midiNote;
}

midiNote = convertMidi();

function onMIDIMessage(event) {
    // event.data is an array
    // event.data[0] = on (144) / off (128) / controlChange (176)  / pitchBend (224) / ...
    // event.data[1] = midi note
    // event.data[2] = velocity

    switch (event.data[0]) {
    case 144:
        // your function startNote(note, velocity)
        noteName = midiNote[event.data[1]][0];
        octaveName = midiNote[event.data[1]][2];
        keyNumber = midiNote[event.data[1]][1];
        startNote(octaveName, keyNumber, noteName);
        break;
    case 128:
        // your function stopNote(note, velocity)
        noteName = midiNote[event.data[1]][0];
        octaveName = midiNote[event.data[1]][2];
        keyNumber = midiNote[event.data[1]][1];
        stopNote(octaveName, keyNumber, noteName);
        break;
    case 176:
        // your function controlChange(controllerNr, value)
        //console.log('midi CC: ', event.data[1], event.data[2])
        controlChange(event.data[1], event.data[2]);
        break;
    case 224:
        // your function pitchBend(LSB, HSB)
        pitchBend(event.data[1], event.data[2]);
        break;
    }
}