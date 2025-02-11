document.addEventListener("DOMContentLoaded", function () {
    var map = L.map('mapid').setView([0, 0], 2);

    var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    var CartoDB_Positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap © CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    });

    CartoDB_Positron.addTo(map);

    var baseMaps = {
        "White map": CartoDB_Positron,
        "Esri World Imagery": Esri_WorldImagery
    };

    L.control.layers(baseMaps).addTo(map);
});