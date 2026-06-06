function startVoice(){

    const recognition = new webkitSpeechRecognition();

    recognition.onresult = function(event){

        document.getElementById("userInput").value =
        event.results[0][0].transcript;
    }

    recognition.start();
}