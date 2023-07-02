function updateTime() {
  var timestamps = document.getElementsByClassName('timestamp');
  for (var i = 0; i < timestamps.length; i++) {
    var timestamp = timestamps[i];
    var time = new Date(parseInt(timestamp.getAttribute('data-timestamp')) * 1000);
    timestamp.innerHTML = getRelativeTime(time);
  }
}

function getRelativeTime(time) {
  var currentTime = new Date();
  var elapsed = currentTime - time;

  var seconds = Math.floor(elapsed / 1000);
  if (seconds < 60) {
    return seconds + ' seconds ago';
  }

  var minutes = Math.floor(elapsed / (1000 * 60));
  if (minutes < 60) {
    return minutes + ' minutes ago';
  }

  var hours = Math.floor(elapsed / (1000 * 60 * 60));
  if (hours < 24) {
    return hours + ' hours ago';
  }

  var days = Math.floor(elapsed / (1000 * 60 * 60 * 24));
  if (days < 30) {
    return days + ' days ago';
  }

  var months = Math.floor(elapsed / (1000 * 60 * 60 * 24 * 30));
  if (months < 12) {
    return months + ' months ago';
  }

  var years = Math.floor(elapsed / (1000 * 60 * 60 * 24 * 30 * 12));
  return years + ' years ago';
}

window.onload = function () {
  updateTime();
  setInterval(updateTime, 60000); // Update every minute
};