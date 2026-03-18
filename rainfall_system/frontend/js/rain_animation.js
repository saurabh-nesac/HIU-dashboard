let frame = 1;

const rainLayer = L.tileLayer(
"/rain/"+frame+"/{z}/{x}/{y}.png",
{
opacity:0.65,
maxZoom:12
}).addTo(map);


setInterval(()=>{

frame++

if(frame>10)
frame=1

rainLayer.setUrl(
"/rain/"+frame+"/{z}/{x}/{y}.png"
)

},600)