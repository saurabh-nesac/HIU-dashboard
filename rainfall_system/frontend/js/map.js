var map = L.map('map').setView([26.2, 92.9], 6);

// var map = L.map('map').setView([22, 80], 5);

L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  {
    attribution: '&copy; OpenStreetMap & CartoDB',
    subdomains: 'abcd',
    maxZoom: 19
  }
).addTo(map);