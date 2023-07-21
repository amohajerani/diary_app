var recognition = new (window.SpeechRecognition ||
  window.webkitSpeechRecognition ||
  window.mozSpeechRecognition ||
  window.msSpeechRecognition)()
recognition.lang = "en-US"
recognition.interimResults = false
recognition.maxAlternatives = 1
recognition.continuous = true

var transcriptElement = document.querySelector("#transcript")
var startBtn = document.querySelector("#start-btn")
var pauseBtn = document.querySelector("#pause-btn")
var stopBtn = document.querySelector("#stop-btn")
var pointersBtn = document.querySelector("#pointers-btn")
var notesBtn = document.querySelector("#notes-btn")
var summaryElement = document.querySelector("#summaryNote")   
var isStopped = false
var resultIndex = 0

startBtn.addEventListener("click", function () {
  resultIndex = 0
  isStopped = false
  recognition.start()
  startBtn.disabled = true
  pauseBtn.disabled = false
  stopBtn.disabled = false
})

pauseBtn.addEventListener("click", function () {
  isStopped = true
  recognition.abort()
  startBtn.disabled = false
  pauseBtn.disabled = true
  stopBtn.disabled = true
})

stopBtn.addEventListener("click", function () {
  isStopped = true
  recognition.stop()
  startBtn.disabled = false
  pauseBtn.disabled = true
  stopBtn.disabled = true
})

notesBtn.addEventListener("click", function () {
    if (resultIndex<1){alert("Too short. Keep recording please.")}
    else {
        isStopped = true;
        recognition.stop();
        startBtn.disabled = true
        pauseBtn.disabled = false
        stopBtn.disabled = false
        const transcriptionData = {
            transcription: transcriptElement.innerHTML,
          }
          fetch("/summary-note", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(transcriptionData),
          })
            .then((response) => {
              if (response.ok) {
                response.json().then((data) => {
                    summaryElement.innerHTML = data.summary;
                  });
                console.log("transcription sent successfully")
              } else {
                console.log("Failed to send transcription")
                // Handle any errors or display appropriate error message
              }
            })
            .catch((error) => {
              console.log("Error:", error)
              // Handle any errors or display appropriate error message
            })
    }
  })

recognition.onresult = function (event) {
  var transcript = event.results[resultIndex][0].transcript
  transcriptElement.innerHTML += transcript + ". "
  resultIndex = event.resultIndex + 1
}

recognition.onerror = function (event) {
  console.error("Error occurred in recognition: " + event.error)
}

recognition.onend = function () {
  resultIndex = 0
  if (!isStopped) {
    recognition.start()
  } else {
    startBtn.disabled = false
    pauseBtn.disabled = true
    stopBtn.disabled = true
  }
}
