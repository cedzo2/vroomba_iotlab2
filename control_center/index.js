document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "192.168.1.109";   // the IP address of your Raspberry PI

function client(){
    
    const net = require('net');
    var input = document.getElementById("input_speed").value;
    document.getElementById("speed").innerHTML = input;
    

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        var upArrow = document.getElementById("upArrow").style.color;
        var downArrow = document.getElementById("downArrow").style.color;
        var leftArrow = document.getElementById("leftArrow").style.color;
        var rightArrow = document.getElementById("rightArrow").style.color;
        // send the message
        if (upArrow == 'purple') {
            client.write("up");
            document.getElementById("direction").innerHTML = "Forward";
        }
        else if (downArrow == 'purple') {
            client.write("down");
            document.getElementById("direction").innerHTML = "Backward";
        }
        else if (leftArrow == 'purple') {
            client.write("left");
            document.getElementById("direction").innerHTML = "Left";
        }
        else if (rightArrow == 'purple') {
            client.write("right");
            document.getElementById("direction").innerHTML = "Right";
        }
        else {
            client.write(`${input}\r\n`);
            document.getElementById("direction").innerHTML = ""
        }
        
        
    });
    
    // get the data from the server
    client.on('data', (data) => {
        const data_array = data.toString().split(" ");
        document.getElementById("battery").innerHTML = data_array[1];
        document.getElementById("temperature").innerHTML = data_array[0];
        console.log(data_array[0]);
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });


}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "purple";
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "purple";
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "purple";
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "purple";
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "white";
    document.getElementById("downArrow").style.color = "white";
    document.getElementById("leftArrow").style.color = "white";
    document.getElementById("rightArrow").style.color = "white";
}


// update data for every 50ms
function update_data(){
    setInterval(function(){
        // get image from python server
        client();
    }, 50);
}
