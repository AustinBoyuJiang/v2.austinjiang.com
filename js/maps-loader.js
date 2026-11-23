(function () {
  'use strict';

  function initialize() {
    var map = document.getElementById('map');
    if (!map) return;

    function showMapLink() {
      var link = document.createElement('a');
      link.href = 'https://www.google.com/maps/search/?api=1&query=redacted%2C%20BC';
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'View redacted on Google Maps';
      map.replaceChildren(link);
      map.style.display = 'grid';
      map.style.placeItems = 'center';
    }

    var key = window.AUSTIN_GOOGLE_MAPS_API_KEY || '';
    if (!key) {
      showMapLink();
      return;
    }
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(key);
    script.onerror = showMapLink;
    script.onload = function () {
      if (!window.google || !window.google.maps || !window.jQuery || !window.jQuery.fn.googleMap) {
        showMapLink();
        return;
      }
      window.jQuery(map).googleMap({ zoom: 15 });
      window.jQuery(map).addMarker({ address: 'redacted' });
    };
    document.head.appendChild(script);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
