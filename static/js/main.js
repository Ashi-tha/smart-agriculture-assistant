// Google Translate Initialization
function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'en',
    includedLanguages: 'en,hi,mr,ta,te,gu,bn,kn,ml,pa,ur', // Indian languages + English
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE
  }, 'google_translate_element');
}

// Text to Speech
let isReading = false;
let utterance;

function toggleTTS() {
  if (isReading) {
    stopTTS();
    return;
  }

  // Find the most meaningful text to read based on the page
  let textToRead = "";
  
  // Try to find prediction results
  const resultBoxes = document.querySelectorAll('.result-target, .result-card, .disease-card, .metric-card, .weather-card .temp, .yield-hero, .disease-info, .result-section:not(.hidden)');
  if (resultBoxes.length > 0) {
    resultBoxes.forEach(box => {
      if (!box.classList.contains('hidden')) {
        textToRead += box.innerText + ". ";
      }
    });
  }
  
  if (!textToRead || !textToRead.trim()) {
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
      const clone = mainContent.cloneNode(true);
      const scripts = clone.querySelectorAll('script, style, button, .hidden');
      scripts.forEach(s => s.remove());
      textToRead = clone.innerText;
    }
  }

  if (!textToRead || !textToRead.trim()) {
    textToRead = "Hello! Welcome to AgriSense. Please navigate the dashboard to view insights.";
  }

  speakText(textToRead);
}

function stopTTS() {
  window.speechSynthesis.cancel();
  isReading = false;
  const btns = document.querySelectorAll('.tts-btn, #tts-btn');
  btns.forEach(btn => {
    if (btn.id === 'tts-btn') btn.innerHTML = '🔊 Read Aloud';
    else btn.innerHTML = '🔊 Read Section';
    btn.classList.remove('reading');
  });
}

function speakElement(elementId) {
  if (isReading) {
    stopTTS();
    return;
  }
  const el = document.getElementById(elementId);
  if (!el) return;
  
  // Clone to remove unwanted elements from speech
  const clone = el.cloneNode(true);
  const ignore = clone.querySelectorAll('button, .hidden, script, style');
  ignore.forEach(i => i.remove());
  
  speakText(clone.innerText);
}

function speakText(text) {
  if (!text || !text.trim()) return;
  
  window.speechSynthesis.cancel();
  utterance = new SpeechSynthesisUtterance(text);
  
  // Detect language
  if (/[\u0900-\u097F]/.test(text)) utterance.lang = 'hi-IN';
  else if (/[\u0980-\u09FF]/.test(text)) utterance.lang = 'bn-IN';
  else if (/[\u0C00-\u0C7F]/.test(text)) utterance.lang = 'te-IN';
  else if (/[\u0B80-\u0BFF]/.test(text)) utterance.lang = 'ta-IN';
  else utterance.lang = 'en-IN';
  
  utterance.onend = stopTTS;
  utterance.onerror = stopTTS;

  isReading = true;
  // Mark relevant button as reading
  const globalBtn = document.getElementById('tts-btn');
  if (globalBtn) {
    globalBtn.innerHTML = '⏹ Stop';
    globalBtn.classList.add('reading');
  }
  
  window.speechSynthesis.speak(utterance);
}


// Speech to Text (Voice Input for forms)
document.addEventListener('DOMContentLoaded', () => {
  // Add microphone buttons to all text and number inputs
  const inputs = document.querySelectorAll('input[type="text"], input[type="number"], textarea');
  
  // Check if browser supports speech recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  inputs.forEach(input => {
    // Don't add mic to hidden inputs or specific fields
    if (input.type === 'hidden' || input.readOnly || input.type === 'file') return;
    if (input.classList.contains('no-voice')) return;
    
    // Only wrap if it's not already wrapped
    if(input.parentNode.classList.contains('voice-input-wrapper')) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'voice-input-wrapper';

    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const micBtn = document.createElement('button');
    micBtn.type = 'button';
    micBtn.className = 'mic-btn';
    micBtn.innerHTML = '🎤';
    micBtn.title = 'Speak to type';

    wrapper.appendChild(micBtn);

    let recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-IN'; 

    micBtn.addEventListener('click', (e) => {
      e.preventDefault();
      
      if (micBtn.classList.contains('listening')) {
        recognition.stop();
        micBtn.classList.remove('listening');
        micBtn.innerHTML = '🎤';
        return;
      }

      try {
        recognition.start();
        micBtn.classList.add('listening');
        micBtn.innerHTML = '🔴'; // recording dot
      } catch (err) {
        console.error(err);
      }
    });

    recognition.onresult = (e) => {
      let transcript = e.results[0][0].transcript;
      
      // Remove trailing period sometimes added by recognition
      if(transcript.endsWith('.')) {
         transcript = transcript.slice(0, -1);
      }
      
      // If it's a number field, extract number
      if(input.type === 'number') {
         const match = transcript.match(/\d+(\.\d+)?/);
         if(match) {
             transcript = match[0];
         }
      }

      input.value = transcript;
      micBtn.classList.remove('listening');
      micBtn.innerHTML = '🎤';
      
      // Trigger input event to update any listeners
      const event = new Event('input', { bubbles: true });
      input.dispatchEvent(event);
    };

    recognition.onerror = (e) => {
      console.error("Speech Recognition Error:", e.error);
      micBtn.classList.remove('listening');
      micBtn.innerHTML = '🎤';
    };

    recognition.onend = () => {
      micBtn.classList.remove('listening');
      if (!micBtn.classList.contains('listening-error')) {
         micBtn.innerHTML = '🎤';
      }
    };
  });
});
