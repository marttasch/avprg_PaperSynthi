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
    // [noteName, idName, keyNumber, ovtaveNumber]
    midiNote[60] = ["C", "C", 0, 4];
    midiNote[61] = ["C#", "C#", 1, 4];
    midiNote[62] = ["D", "D", 2, 4];
    midiNote[63] = ["D#", "D#", 3, 4];
    midiNote[64] = ["E", "E", 4, 4];
    midiNote[65] = ["F", "F", 5, 4];
    midiNote[66] = ["F#", "F#", 6, 4];
    midiNote[67] = ["G", "G", 7, 4];
    midiNote[68] = ["G#", "G#", 8, 4];
    midiNote[69] = ["A", "A", 9, 4];
    midiNote[70] = ["A#", "A#", 10, 4];
    midiNote[71] = ["B", "B", 11, 4];

    midiNote[72] = ["C", "C1", 12, 5];
    midiNote[73] = ["C#", "C1#", 13, 5];
    midiNote[74] = ["D", "D1", 14, 5];
    midiNote[75] = ["D#", "D1#", 15, 5];
    midiNote[76] = ["E", "E1", 16, 5];
    midiNote[77] = ["F", "F1", 17, 5];
    midiNote[78] = ["F#", "F1#", 18, 5];
    midiNote[79] = ["G", "G1", 19, 5];
    midiNote[80] = ["G#", "G1#", 20, 5];
    midiNote[81] = ["A", "A1", 21, 5];
    midiNote[82] = ["A#", "A1#", 22, 5];
    midiNote[83] = ["B", "B1", 23, 5];

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
        idName = midiNote[event.data[1]][1];
        keyNumber = midiNote[event.data[1]][2];
        octaveNumber = midiNote[event.data[1]][3];
        startNote(octaveNumber, keyNumber, noteName, idName);
        break;
    case 128:
        // your function stopNote(note, velocity)
        noteName = midiNote[event.data[1]][0];
        idName = midiNote[event.data[1]][1];
        keyNumber = midiNote[event.data[1]][2];
        octaveNumber = midiNote[event.data[1]][3];
        stopNote(octaveNumber, keyNumber, noteName, idName);
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