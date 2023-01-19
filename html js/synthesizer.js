const context = new AudioContext();
let Osc1Gain = context.createGain();
let Osc2Gain = context.createGain();
let reverbBypassGain = context.createGain();
let masterGain = context.createGain();
let lfo = context.createOscillator();
let lfoGain = context.createGain();
let lfo2 = context.createOscillator();
let lfoGain2 = context.createGain();

// Reverb
let reverb = context.createConvolver();
let stateReverb = false;
let reverbGain = context.createGain();
reverbGain.gain.value = 0;
reverbBypassGain.gain.value = 1;
loadImpulseResponse("room");

// Distortion
let distortion = context.createWaveShaper();
let stateDistortion = false;

//OSCI
const waveform = document.getElementsByClassName("waveform");
const waveform2 = document.getElementsByClassName("waveform2");
let currentWaveform1 = "sine";
let currentWaveform2 = "sine";
const oscillators1 = [];
const oscillators2 = []; 
const osciGains1 = [];
const osciGains2 = [];
let detuneOsci2Cent = 100;

// LFO
lfo.frequency.value = 6;
lfoGain.gain.value = 0.2;
lfo.start(context.currentTime);
lfo.connect(lfoGain);

lfo2.frequency.value = 6;
lfoGain2.gain.value = 0.2;
lfo2.start(context.currentTime);
lfo2.connect(lfoGain2);

masterGain.gain.value = 0.3; 

// Audiograph
lfoGain.connect(Osc1Gain.gain);
lfoGain2.connect(Osc2Gain.gain);
Osc1Gain.connect(distortion);
Osc2Gain.connect(distortion);
distortion.connect(reverb);
distortion.connect(reverbBypassGain);
reverbBypassGain.connect(masterGain);

reverb.connect(reverbGain);
reverbGain.connect(masterGain);

masterGain.connect(context.destination);

const keys = document.getElementsByClassName("key");
let noteFreq = null;




function createNoteTable() {
    const noteFreq = [];
    for (let i = 0; i < 9; i++) {
        noteFreq[i] = [];
    }

    noteFreq[1]["C"] = 32.703195662574829;
    noteFreq[1]["C#"] = 34.647828872109012;
    noteFreq[1]["D"] = 36.708095989675945;
    noteFreq[1]["D#"] = 38.890872965260113;
    noteFreq[1]["E"] = 41.203444614108741;
    noteFreq[1]["F"] = 43.653528929125485;
    noteFreq[1]["F#"] = 46.249302838954299;
    noteFreq[1]["G"] = 48.999429497718661;
    noteFreq[1]["G#"] = 51.913087197493142;
    noteFreq[1]["A"] = 55.000000000000000;
    noteFreq[1]["A#"] = 58.270470189761239;
    noteFreq[1]["B"] = 61.735412657015513;

    noteFreq[2]["C"] = 65.406391325149658;
    noteFreq[2]["C#"] = 69.295657744218024;
    noteFreq[2]["D"] = 73.416191979351890;
    noteFreq[2]["D#"] = 77.781745930520227;
    noteFreq[2]["E"] = 82.406889228217482;
    noteFreq[2]["F"] = 87.307057858250971;
    noteFreq[2]["F#"] = 92.498605677908599;
    noteFreq[2]["G"] = 97.998858995437323;
    noteFreq[2]["G#"] = 103.826174394986284;
    noteFreq[2]["A"] = 110.000000000000000;
    noteFreq[2]["A#"] = 116.540940379522479;
    noteFreq[2]["B"] = 123.470825314031027;

    noteFreq[3]["C"] = 130.812782650299317;
    noteFreq[3]["C#"] = 138.591315488436048;
    noteFreq[3]["D"] = 146.832383958703780;
    noteFreq[3]["D#"] = 155.563491861040455;
    noteFreq[3]["E"] = 164.813778456434964;
    noteFreq[3]["F"] = 174.614115716501942;
    noteFreq[3]["F#"] = 184.997211355817199;
    noteFreq[3]["G"] = 195.997717990874647;
    noteFreq[3]["G#"] = 207.652348789972569;
    noteFreq[3]["A"] = 220.000000000000000;
    noteFreq[3]["A#"] = 233.081880759044958;

    noteFreq[3]["B"] = 246.941650628062055;
    noteFreq[4]["C"] = 261.625565300598634;
    noteFreq[4]["C#"] = 277.182630976872096;
    noteFreq[4]["D"] = 293.664767917407560;
    noteFreq[4]["D#"] = 311.126983722080910;
    noteFreq[4]["E"] = 329.627556912869929;
    noteFreq[4]["F"] = 349.228231433003884;
    noteFreq[4]["F#"] = 369.994422711634398;
    noteFreq[4]["G"] = 391.995435981749294;
    noteFreq[4]["G#"] = 415.304697579945138;
    noteFreq[4]["A"] = 440.000000000000000;
    noteFreq[4]["A#"] = 466.163761518089916;
    noteFreq[4]["B"] = 493.883301256124111;

    noteFreq[5]["C"] = 523.251130601197269;
    noteFreq[5]["C#"] = 554.365261953744192;
    noteFreq[5]["D"] = 587.329535834815120;
    noteFreq[5]["D#"] = 622.253967444161821;
    noteFreq[5]["E"] = 659.255113825739859;
    noteFreq[5]["F"] = 698.456462866007768;
    noteFreq[5]["F#"] = 739.988845423268797;
    noteFreq[5]["G"] = 783.990871963498588;
    noteFreq[5]["G#"] = 830.609395159890277;
    noteFreq[5]["A"] = 880.000000000000000;
    noteFreq[5]["A#"] = 932.327523036179832;
    noteFreq[5]["B"] = 987.766602512248223;

    noteFreq[6]["C"] = 1046.502261202394538;
    noteFreq[6]["C#"] = 1108.730523907488384;
    noteFreq[6]["D"] = 1174.659071669630241;
    noteFreq[6]["D#"] = 1244.507934888323642;
    noteFreq[6]["E"] = 1318.510227651479718;
    noteFreq[6]["F"] = 1396.912925732015537;
    noteFreq[6]["F#"] = 1479.977690846537595;
    noteFreq[6]["G"] = 1567.981743926997176;
    noteFreq[6]["G#"] = 1661.218790319780554;
    noteFreq[6]["A"] = 1760.000000000000000;
    noteFreq[6]["A#"] = 1864.655046072359665;
    noteFreq[6]["B"] = 1975.533205024496447;

    noteFreq[7]["C"] = 2093.004522404789077;
    noteFreq[7]["C#"] = 2217.461047814976769;
    noteFreq[7]["D"] = 2349.318143339260482;
    noteFreq[7]["D#"] = 2489.015869776647285;
    noteFreq[7]["E"] = 2637.020455302959437;
    noteFreq[7]["F"] = 2793.825851464031075;
    noteFreq[7]["F#"] = 2959.955381693075191;
    noteFreq[7]["G"] = 3135.963487853994352;
    noteFreq[7]["G#"] = 3322.437580639561108;
    noteFreq[7]["A"] = 3520.000000000000000;
    noteFreq[7]["A#"] = 3729.310092144719331;
    noteFreq[7]["B"] = 3951.066410048992894;

    noteFreq[8]["C"] = 4186.009044809578154;

    return noteFreq;
}

noteFreq = createNoteTable();

// Distortion On oder Off
document.querySelector("#Distortion").addEventListener("click", function(e) {
  if(stateDistortion == false) {
    stateDistortion = true;
    distortionOn(this.id);
    //this.classList.add('active')
  } else {
    stateDistortion = false;
    distortionOff(this.id);
    //this.classList.remove('active')
  }
});

function distortionOn(elemntID){
  distortion.curve = makeDistortionCurve(250);
  document.getElementById(elemntID).classList.add('active');
}

function distortionOff(elemntID){
  distortion.curve = makeDistortionCurve(0);
  document.getElementById(elemntID).classList.remove('active');
}

// Reverb On oder Off
document.querySelector("#Reverb").addEventListener("click", function(e) {
  if(stateReverb == false) {
    stateReverb = true;
    reverbOn(this.id);
    //this.classList.add('active')
  } else {
    stateReverb = false;
    reverbOff(this.id);
    //this.classList.remove('active')
  }
});

function reverbOn(elemntID){
  reverbGain.gain.value = 1;
  reverbBypassGain.gain.value = 0;
  document.getElementById(elemntID).classList.add('active');
}

function reverbOff(elemntID){
  reverbGain.gain.value = 0;
  reverbBypassGain.gain.value = 1;
  document.getElementById(elemntID).classList.remove('active');
}


// Ton-Ausgabe bei Tastendruck
for (let i = 0; i < keys.length; i++) {
  console.log(keys[i].getAttribute("octave"), keys[i].id);
  keys[i].addEventListener("mousedown", function() {startNote(keys[i].getAttribute("octave"), i, keys[i].name, keys[i].id)});
  keys[i].addEventListener("mouseup", function() {stopNote(keys[i].getAttribute("octave"), i, keys[i].name ,keys[i].id)});
}

//Auswahl Waveform für Oszillator 1
for (let i = 0; i < waveform.length; i++) {
  console.log(waveform[i].id);
  waveform[i].addEventListener("click", function() {setWaveformOszi1(waveform[i])});
}

function setWaveformOszi1(selectedWaveformElement) {
  waveformName = selectedWaveformElement.name
  console.log('Oszi 1: ', waveformName);
  currentWaveform1 = waveformName;

  // visual Feedback
  for (let i = 0; i < waveform.length; i++) {
    waveform[i].classList.remove('active');
  }
  selectedWaveformElement.classList.add('active')
}

// Slider für Gain für Oszillator 1
document.querySelector("#gainSlider").addEventListener("input", function (e) {
  let gain1Value = (this.value);
  document.querySelector("#gainOutput").innerHTML = (gain1Value*100).toFixed(0) + " %";
  Osc1Gain.gain.value = gain1Value;
  lfoGain.gain.value = mapValue(gain1Value, 0, 1, 0, 0.4);
});

// Slider für LFO für Oszillator 1
document.querySelector("#lfoSlider").addEventListener("input", function(e){
  lfo.frequency.value = this.value;
  document.querySelector("#lfoOutput").innerHTML = this.value + " Hz";
});

//Auswahl Waveform für Oszillator 2
for (let i = 0; i < waveform2.length; i++) {
  console.log(waveform2[i].id);
  waveform2[i].addEventListener("click", function() {setWaveformOszi2(waveform2[i])});
}

function setWaveformOszi2(selectedWaveformElement) {
  waveformName = selectedWaveformElement.name
  console.log('Oszi 2: ', waveformName);
  currentWaveform2 = waveformName;

  // visual Feedback
  for (let i = 0; i < waveform2.length; i++) {
    waveform2[i].classList.remove('active');
  }
  selectedWaveformElement.classList.add('active')
}

// Slider für Gain für Oszillator 2
document.querySelector("#gainSlider2").addEventListener("input", function (e) {
  let gain2Value = (this.value);
  document.querySelector("#gainOutput2").innerHTML = (gain2Value*100).toFixed(0) + " %";
  Osc2Gain.gain.value = gain2Value;
  lfoGain2.gain.value = mapValue(gain2Value, 0, 1, 0, 0.4);
});

// Slider für LFO für Oszillator 2
document.querySelector("#lfoSlider2").addEventListener("input", function(e){
  lfo2.frequency.value = this.value;
  document.querySelector("#lfoOutput2").innerHTML = this.value + " Hz";
});

// MasterGain-Slider
document.querySelector("#mainGainSlider").addEventListener("input", function (e) {
  let masterGainValue = (this.value);
  document.querySelector("#mainGainOutput").innerHTML = (masterGainValue*100).toFixed(0) + " %";
  masterGain.gain.value = masterGainValue;
});

// Rerverb-Slider
document.querySelector("#reverbSlider").addEventListener("input", function (e) {
  let reverbGainValue = (this.value);
  document.querySelector("#reverbfaderOutput").innerHTML = (reverbGainValue*100).toFixed(0) + " %";
  reverbGain.gain.value = reverbGainValue;
  reverbBypassGain.gain.value = 1-reverbGainValue;
});

// Pitch-Slider
document.querySelector('#pitchSlider').addEventListener('input', function(e) {
  let pitchValue = this.value;
  document.querySelector('#pitchOutput').innerHTML = (pitchValue*100).toFixed(0) + ' %';
  pitch(pitchValue);
})

function pitch(value){
  value = mapValue(value, 0, 1, -1200, 1200);
  console.log(value);
  for (let i = 0; i < oscillators1.length; i++ ) {
    try {
      oscillators1[i].detune.setValueAtTime(value, context.currentTime + 0.1);
    } catch(error){
      //console.log(error);
    }
  }

  for (let i = 0; i < oscillators2.length; i++ ) {
    try {
      oscillators2[i].detune.setValueAtTime(value+detuneOsci2Cent, context.currentTime + 0.1);
    } catch(error){
      //console.log(error);
    }
  }
}

function startNote(octave, keyNumber, noteName, idName) {
  gain1Value = document.querySelector("#gainSlider").value;
  gain2Value = document.querySelector("#gainSlider2").value;

  // Osci 1
  osciGains1[keyNumber] = context.createGain();
  oscillators1[keyNumber] = context.createOscillator();
  oscillators1[keyNumber].frequency.value = noteFreq[octave][noteName];
  oscillators1[keyNumber].type = currentWaveform1;

  oscillators1[keyNumber].connect(osciGains1[keyNumber]);

  osciGains1[keyNumber].connect(Osc1Gain);

  // Osci 2
  osciGains2[keyNumber] = context.createGain();
  oscillators2[keyNumber] = context.createOscillator();
  oscillators2[keyNumber].frequency.value = noteFreq[octave][noteName];
  oscillators2[keyNumber].type = currentWaveform2;

  oscillators1[keyNumber].connect(osciGains1[keyNumber]);
  oscillators2[keyNumber].connect(Osc2Gain);

  // pitch and play
  pitch(document.querySelector('#pitchSlider').value);
  oscillators1[keyNumber].start(context.currentTime+0.1);
  oscillators2[keyNumber].start(context.currentTime+0.1);
  osciGains1[keyNumber].gain.linearRampToValueAtTime(gain1Value, context.currentTime + 0.2);
  osciGains2[keyNumber].gain.linearRampToValueAtTime(gain1Value, context.currentTime + 0.2);
  //lfoGain.gain.linearRampToValueAtTime(gain2Value, context.currentTime + 0.3);

  document.getElementById(idName).classList.add('active')
}

function stopNote(octave, keyNumber, noteName, idName) {
  osciGains1[keyNumber].gain.linearRampToValueAtTime(0, context.currentTime + 0.1);
  //lfoGain.gain.linearRampToValueAtTime(0, context.currentTime + 0.3);
  //masterGain.gain.linearRampToValueAtTime(0, context.currentTime + 0.003);
  oscillators1[keyNumber].stop(context.currentTime + 0.3);
  oscillators2[keyNumber].stop(context.currentTime + 0.3);

  document.getElementById(idName).classList.remove('active')
}

// MIDI FUNKTIONEN

function mapValue (number, inMin, inMax, outMin, outMax) {
  return (number - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}

function controlChange(channel, value) {
  //Pitch (MODULATION)
  if (channel == 1){
    value = mapValue(value, 0, 127, 1, 0)
    console.log('Pitch: ', value);
    document.querySelector("#pitchSlider").value = value;
    document.querySelector("#pitchOutput").innerHTML = (value*100).toFixed(0) + " %";
    pitch(value);
  }

  // Reverb (EFFECT_CONTROL_1)
  if (channel == 12){
    value = mapValue(value, 0, 127, 1, 0)
    console.log('Reverb: ', value);
    document.querySelector("#reverbSlider").value = value;

    document.querySelector("#reverbSlider").innerHTML = (value*100).toFixed(0) + " %";
    reverbGain.gain.value = value;
    reverbBypassGain.gain1Value = 1-value;
  }

  // Main Gain (VOLUME)
  if (channel == 7){   
    value = mapValue(value, 0, 127, 1, 0)
    console.log('Main Gain: ', value);
    document.querySelector("#mainGainSlider").value = value;

    document.querySelector("#mainGainOutput").innerHTML = (value*100).toFixed(0) + " %";
    masterGain.gain.value = value;
  }


  // Oszi 1 Gain (SOUND_CONTROLLER_1)
  if (channel == 70){
    value = mapValue(value, 0, 127, 0, 1)

    console.log('Oszi 1 Gain: ', value);
    document.querySelector("#gainSlider").value = value;

    document.querySelector("#gainOutput").innerHTML = (value*100).toFixed(0) + " %";
    Osc1Gain.gain.value = value;

  }

  // Oszi 1 LFO (SOUND_CONTROLLER_2)
  if (channel == 71){  
    value = mapValue(value, 0, 127, 0, 100)

    console.log('Oszi 1 LFO: ', value);
    document.querySelector("#lfoSlider").value = value;

    document.querySelector("#lfoOutput").innerHTML = value.toFixed(0) + " Hz";
  }
  
  // Oszi 1 Waveform (SOUND_CONTROLLER_3)
  if (channel == 72){   
    if (value <= 31) {   // sine (0..31)
      //getWaveformOszi1('sine');
      document.querySelector('#sine').click();
    }
    else if (value <= 63) {   // triangle (32..63)
      //getWaveformOszi1('triangle');
      document.querySelector('#triangle').click();
    }
    else if (value <= 95) {   // sawtooth (64..95)
      //getWaveformOszi1('sawtooth');
      document.querySelector('#sawtooth').click();
    }
    else if (value <= 127) {   // triangle (96..127)
      //getWaveformOszi1('square');
      document.querySelector('#square').click();
    }
  }

  // Oszi 2 Gain (SOUND_CONTROLLER_4)
  if (channel == 73){   
    value = mapValue(value, 0, 127, 0, 1)

    console.log('Pszi 2 Gain: ', value);
    document.querySelector("#gainSlider2").value = value;

    document.querySelector("#gainOutput2").innerHTML = (value*100).toFixed(0) + " %";
    Osc2Gain.gain.value = value;
  }

  // Oszi 2 LFO (SOUND_CONTROLLER_5)
  if (channel == 74){ 
    value = mapValue(value, 0, 127, 0, 100)

    console.log('Oszi 2 LFO: ', value);
    document.querySelector("#lfoSlider2").value = value/127*100;

    document.querySelector("#lfoOutput2").innerHTML = value.toFixed(0) + " Hz";
  }

  // Waveform Oszi 2 (SOUND_CONTROLLER_6)
  if (channel == 75){   
    if (value <= 31) {   // sine (0..31)
      //getWaveformOszi2('sine');
      document.querySelector('#sine2').click();
    }
    else if (value <= 63) {   // triangle (32..63)
      //getWaveformOszi2('triangle');
      document.querySelector('#triangle2').click();
    }
    else if (value <= 95) {   // sawtooth (64..95)
      //getWaveformOszi2('sawtooth');
      document.querySelector('#sawtooth2').click();
    }
    else if (value <= 127) {   // triangle (96..127)
      //getWaveformOszi2('square');
      document.querySelector('#square2').click();
    }
  }


  // Mode (BANK_SELECT)
  if (channel == 0){   
    if (value <= 41) {   // keys (0..41)
      console.log('Mode: Keys')
    }
    else if (value <= 83) {   // drums (42..83)
      console.log('Mode: Drums')
    }
    else if (value <= 127) {   // sounds (84..127)
      console.log('Mode: Sounds')
    }
  }


  // Record / Play (GENERAL_PURPOSE_CONTROLLER_1)
  if (channel == 16){   
    if (value <= 63) {   // play (0..63)
      console.log('Play')
    }
    else if (value <= 127) {   // record (64..127)
      console.log('Record')
    }
  }


  // Distortion (EFFECTS_1)
  if (channel == 91){   
    if (value <= 63) {   // off (0..63)
      console.log('Distortion off')
      distortionOff('Distortion');
    }
    else if (value <= 127) {   // on (64..127)
      console.log('Distortion on')
      distortionOn('Distortion');
    }
  }


  // Reverb (EFFECTS_2)
  if (channel == 92){   
    if (value <= 63) {   // off (0..63)
      console.log('Reverb off')
      reverbOff('Reverb');
    }
    else if (value <= 127) {   // on (64..127)
      console.log('Reverb on')
      reverbOn('Reverb');
    }
  }


  



}