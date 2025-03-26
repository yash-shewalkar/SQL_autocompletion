$(document).ready(function() {
    let typingTimer;
    let doneTypingInterval = 500; // Adjust for responsiveness

    $("#query").on("input", function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(fetchSuggestion, doneTypingInterval);
    });

    function fetchSuggestion() {
        let userQuery = $("#query").val();
        let schema = $("#schema").val();

        if (userQuery.length > 3) {
            $.ajax({
                url: "/suggest",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ query: userQuery, schema: schema }),
                success: function(response) {
                    $("#suggestions").text(response.suggestion);
                }
            });
        }
    }
});
