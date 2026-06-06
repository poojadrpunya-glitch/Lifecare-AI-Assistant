function sendMessage(){

    let input = document.getElementById("userInput").value;

    let area = document.getElementById("chat-area");

    area.innerHTML += "<p><b>You:</b> " + input + "</p>";

    let reply = "";

    if(input.includes("fever")){

        reply = "Drink water and take rest";

    }

    else if(input.includes("headache")){

        reply = "Take proper sleep and hydration";

    }

    else{

        reply = "Please consult doctor for better guidance";
    }

    area.innerHTML += "<p><b>Bot:</b> " + reply + "</p>";
}