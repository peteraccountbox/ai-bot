function showLoader() {
    const loaderHtml = `
        <div class="loader-message bot-message">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    $('#chat-box').append(loaderHtml);
    $('#chat-box').scrollTop($('#chat-box')[0].scrollHeight);

    // Disable input while loading
    $('.input-container').addClass('loading');
    $('#user-input, #send-button').prop('disabled', true);
}

function hideLoader() {
    $('.loader-message').remove();
    // Enable input after loading
    $('.input-container').removeClass('loading');
    $('#user-input, #send-button').prop('disabled', false);
}

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
            .slice(0, 5);

        if (relevantSources.length > 0) {
            const sourcesContainer = $('<div>').addClass('sources-container');
            const sourcesTitle = $('<div>').addClass('sources-title').text('Related Sources:');
            sourcesContainer.append(sourcesTitle);

            relevantSources.forEach(source => {
                try {
                    const similarity = parseFloat(source.similarity.replace('%', '')).toFixed(1);
                    let hostname = source.url;

                    // Safely parse URL
                    try {
                        hostname = new URL(source.url).hostname.replace('www.', '');
                    } catch (e) {
                        console.warn('Invalid URL:', source.url);
                    }

                    const sourceLink = $('<a>')
                        .addClass('source-capsule')
                        .attr('href', source.url)
                        .attr('target', '_blank')
                        .html(`${hostname} <span class="similarity">${similarity}%</span>`);
                    sourcesContainer.append(sourceLink);
                } catch (e) {
                    console.error('Error processing source:', source, e);
                }
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
        // Remove welcome message if it exists
        $('.welcome-message').remove();

        // Display user message
        appendMessage(message, 'user');
        userInput.val('');

        // Show loader
        showLoader();

        // Send to your API endpoint
        $.ajax({
            url: '/api/v1/answer',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                "query": message
            }),
            success: function (response) {
                // Hide loader
                hideLoader();

                if (response.answer) {
                    appendMessage(response, 'bot');
                } else {
                    appendMessage('No answer received', 'bot');
                }
            },
            error: function (error) {
                // Hide loader
                hideLoader();

                appendMessage('Sorry, there was an error processing your request.', 'bot');
                console.error('Error:', error);
            }
        });
    }
}

// Handle Enter key
$(document).ready(function () {
    $('#user-input').keypress(function (e) {
        if (e.which == 13 && !$('#send-button').prop('disabled')) {
            sendMessage();
        }
    });
}); 