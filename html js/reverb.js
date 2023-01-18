function loadImpulseResponse(name) {
    fetch("/impulseResponses/" + name + ".wav")
        .then(response => response.arrayBuffer())
        .then(undecodedAudio => context.decodeAudioData(undecodedAudio))
        .then(audioBuffer => {
            if (convoler) {convoler.disconnect();}

            convoler = context.createConvolver();
            convoler.buffer = audioBuffer;
            convoler.normalize = true;

            source.connect(convoler);
            convoler.connect(masterGain);
        })
        .catch(console.error);
}