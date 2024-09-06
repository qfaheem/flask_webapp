document.addEventListener('DOMContentLoaded', function() {
    // Select the flash messages container
    var flashMessages = document.getElementById('flash-messages');

    if (flashMessages) {
        // Set a timeout to hide the flash messages after 1 second (1000 milliseconds)
        setTimeout(function() {
            flashMessages.style.opacity = '0';
            // Optional: Remove flash messages after fade-out
            setTimeout(function() {
                flashMessages.remove();
            }, 1000); // Matches the duration of the fade-out
        }, 1000); // 1 second before starting to fade out
    }
});
