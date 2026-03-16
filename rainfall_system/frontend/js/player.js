let timer;

function play(){

 timer = setInterval(nextFrame,500);
}

function pause(){

 clearInterval(timer);
}