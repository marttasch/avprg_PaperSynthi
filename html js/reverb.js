function loadImpulseResponse(name) {
    fetch("./impulseResponses/" + name + ".wav")
        .then(response => response.arrayBuffer())
        .then(undecodedAudio => context.decodeAudioData(undecodedAudio))
        .then(audioBuffer => {
            //if (reverb) {reverb.disconnect();}

            //reverb = context.createConvolver();
            reverb.buffer = audioBuffer;
            reverb.normalize = true;

            //source.connect(reverb);
            //reverb.connect(masterGain);
        })
        .catch(console.error);
}