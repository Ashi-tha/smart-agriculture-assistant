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
    window.speechSynthesis.cancel();
    isReading = false;
    document.getElementById('tts-btn').innerHTML = '🔊 Read Aloud';
    document.getElementById('tts-btn').classList.remove('reading');
    return;
  }

  // Find the most meaningful text to read based on the page
  let textToRead = "";
  
  // Try to find prediction results
  const resultBoxes = document.querySelectorAll('.result-target, .result-card, .disease-card, .metric-card, .weather-card .temp');
  if (resultBoxes.length > 0) {
    resultBoxes.forEach(box => {
      textToRead += box.innerText + ". ";
    });
  } else {
    // Basic text query if specific cards are not found
    const resultBoxFallback = document.querySelectorAll('.result-box, .success-box, .alert-box');
    if(resultBoxFallback.length > 0) {
      resultBoxFallback.forEach(box => {
        textToRead += box.innerText + ". ";
      });
    } else {
      // Read the main content text as fallback
      const mainContent = document.querySelector('.main-content');
      if (mainContent) {
        // get clean text without hidden elements or script tags
        const clone = mainContent.cloneNode(true);
        const scripts = clone.querySelectorAll('script, style, button');
        scripts.forEach(s => s.remove());
        textToRead = clone.innerText;
      }
    }
  }

  if (!textToRead || !textToRead.trim()) {
    textToRead = "Hello! Welcome to AgroSense AI. Please navigate the dashboard to view insights.";
  }

  utterance = new SpeechSynthesisUtterance(textToRead);
  
  // Detect language naive approach (Hindi characters present?)
  if (/[\u0900-\u097F]/.test(textToRead)) utterance.lang = 'hi-IN';
  else if (/[\u0980-\u09FF]/.test(textToRead)) utterance.lang = 'bn-IN';
  else if (/[\u0C00-\u0C7F]/.test(textToRead)) utterance.lang = 'te-IN';
  else if (/[\u0B80-\u0BFF]/.test(textToRead)) utterance.lang = 'ta-IN';
  else utterance.lang = 'en-IN'; // Default to Indian English if available
  
  utterance.onend = function() {
    isReading = false;
    const btn = document.getElementById('tts-btn');
    if(btn) {
      btn.innerHTML = '🔊 Read Aloud';
      btn.classList.remove('reading');
    }
  };

  isReading = true;
  document.getElementById('tts-btn').innerHTML = '⏹ Stop Reading';
  document.getElementById('tts-btn').classList.add('reading');
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
