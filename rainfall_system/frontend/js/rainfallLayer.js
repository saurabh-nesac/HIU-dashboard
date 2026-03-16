let timestamps = [];
let index = 0;

async function loadManifest(){

 const res = await fetch("/manifest");
 const data = await res.json();

 timestamps = data.timestamps;
}

function nextFrame(){

 index = (index + 1) % timestamps.length;

 rainLayer.getSource().setUrl(
  `/tiles/${timestamps[index]}/{z}/{x}/{y}.png`
 );
}