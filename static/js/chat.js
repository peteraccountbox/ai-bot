function appendMessage(messageData, type) {
    const chatBox = $('#chat-box');
    const messageDiv = $('<div>').addClass('message').addClass(type + '-message');

    if (type === 'bot') {
        // Add the answer text
        const answerText = $('<div>').addClass('answer-text').text(messageData.answer.answer);
        messageDiv.append(answerText);

        // Filter and sort sources
        const relevantSources = messageData.answer.sources
            .filter(source => parseFloat(source.similarity.replace('%', '')) > 30)
            .sort((a, b) => {
                return parseFloat(b.similarity.replace('%', '')) - parseFloat(a.similarity.replace('%', ''))
            })
            .slice(0, 5); // Take top 5 sources

        if (relevantSources.length > 0) {
            const sourcesContainer = $('<div>').addClass('sources-container');
            const sourcesTitle = $('<div>').addClass('sources-title').text('Related Sources:');
            sourcesContainer.append(sourcesTitle);

            relevantSources.forEach(source => {
                const similarity = parseFloat(source.similarity.replace('%', '')).toFixed(1);
                const sourceLink = $('<a>')
                    .addClass('source-capsule')
                    .attr('href', source.url)
                    .attr('target', '_blank')
                    .html(`${new URL(source.url).hostname.replace('www.', '')} <span class="similarity">${similarity}%</span>`);
                sourcesContainer.append(sourceLink);
            });

            messageDiv.append(sourcesContainer);
        }
    } else {
        // User message
        messageDiv.text(messageData);
    }

    chatBox.append(messageDiv);
    chatBox.scrollTop(chatBox[0].scrollHeight);
}

function sendMessage() {
    const userInput = $('#user-input');
    const message = userInput.val().trim();

    if (message) {
        // Display user message
        appendMessage(message, 'user');
        userInput.val('');

        // Send to your API endpoint
        $.ajax({
            url: '/api/v1/answer',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                "query": message
            }),
            success: function (response) {
                if (response.answer) {
                    appendMessage(response, 'bot');
                } else {
                    appendMessage('No answer received', 'bot');
                }
            },
            error: function (error) {
                appendMessage('Sorry, there was an error processing your request.', 'bot');
                console.error('Error:', error);
            }
        });
    }
}

// Initialize chat functionality when document is ready
$(document).ready(function () {
    // Handle Enter key
    $('#user-input').keypress(function (e) {
        if (e.which == 13) {
            sendMessage();
        }
    });
}); 