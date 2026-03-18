let frame = 1
let maxFrames = 40

let rainA = L.tileLayer(
"/rain/1/{z}/{x}/{y}.png",
{
opacity:0.6,
maxZoom:12
}).addTo(map)

let rainB = L.tileLayer(
"/rain/2/{z}/{x}/{y}.png",
{
opacity:0.0,
maxZoom:12
}).addTo(map)


function animate(){

    frame++

    if(frame>maxFrames)
        frame=1

    let next = frame+1
    if(next>maxFrames) next=1

    rainA.setUrl("/rain/"+frame+"/{z}/{x}/{y}.png")
    rainB.setUrl("/rain/"+next+"/{z}/{x}/{y}.png")

    rainA.setOpacity(0.6)
    rainB.setOpacity(0.0)

    let step=0

    let fade = setInterval(()=>{

        step+=0.1

        rainA.setOpacity(0.6*(1-step))
        rainB.setOpacity(0.6*step)

        if(step>=1)
            clearInterval(fade)

    },40)

}

setInterval(animate,600)