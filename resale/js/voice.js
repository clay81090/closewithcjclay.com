// Tap-to-talk notes. Speech never starts until the user taps the button.

export function createNoteDictation({ textarea, button, status, onSave }) {
  let recognition = null;
  let startingText = "";

  const resetButton = () => {
    button.classList.remove("listening");
    button.textContent = "🎤 Talk note";
  };

  const stop = () => {
    if (recognition) recognition.stop();
  };

  const toggle = () => {
    if (recognition) {
      stop();
      return;
    }

    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      textarea.focus();
      status.textContent =
        "Safari speech is unavailable here. Tap the microphone on the iPhone keyboard and dictate into the note box.";
      return;
    }

    recognition = new Recognition();
    startingText = textarea.value.trim();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;
    button.classList.add("listening");
    button.textContent = "■ Stop";
    status.textContent = "Listening… say the year, condition, box, model, and whether it works.";

    recognition.onresult = (event) => {
      let transcript = "";
      for (let index = 0; index < event.results.length; index += 1) {
        transcript += event.results[index][0].transcript;
      }
      textarea.value = [startingText, transcript.trim()].filter(Boolean).join(". ");
    };
    recognition.onerror = (event) => {
      status.textContent =
        event.error === "not-allowed"
          ? "Microphone permission is off. Allow it in Safari settings, or use the keyboard microphone."
          : "Speech stopped. You can type or tap Talk note again.";
    };
    recognition.onend = async () => {
      recognition = null;
      resetButton();
      if (textarea.value.trim() !== startingText) {
        await onSave();
      } else if (!status.textContent.includes("permission")) {
        status.textContent = "Nothing was heard. Tap Talk note or use the keyboard microphone.";
      }
    };
    recognition.start();
  };

  return { stop, toggle };
}
