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
    console.log(messageData);

    const chatBox = $('#chat-box');
    const messageDiv = $('<div>').addClass('message').addClass(type + '-message');

    if (type === 'bot') {
        // Convert markdown to HTML using marked
        const markedAnswer = marked.parse(messageData.answer);
        // Add the answer text with converted markdown
        const answerText = $('<div>').addClass('answer-text').html(markedAnswer);
        messageDiv.append(answerText);

        // Filter and sort sources
        const relevantSources = messageData.sources
            .filter(source => {
                // Keep sources with 'N/A' or similarity > 30%
                if (source.similarity === 'N/A') return true;
                const similarity = parseFloat(source.similarity.replace('%', ''));
                return !isNaN(similarity) && similarity > 30;
            })
            .sort((a, b) => {
                // Handle cases where either similarity is 'N/A'
                if (a.similarity === 'N/A' && b.similarity === 'N/A') return 0;
                if (a.similarity === 'N/A') return 1;  // Move a to end
                if (b.similarity === 'N/A') return -1; // Move b to end

                // Normal numeric comparison
                return parseFloat(b.similarity.replace('%', '')) - parseFloat(a.similarity.replace('%', ''));
            })
            .slice(0, 5);

        if (relevantSources.length > 0) {
            const sourcesContainer = $('<div>').addClass('sources-container');
            const sourcesTitle = $('<div>').addClass('sources-title').text('Related Sources:');
            sourcesContainer.append(sourcesTitle);

            relevantSources.forEach(source => {
                try {
                    const similarity = parseFloat(parseSimilarity(source.similarity)).toFixed(1);
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
                        .html(`${hostname}`);
                    // <span class="similarity">${similarity}%</span>
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

let currentConversationId = null;

function sendMessage() {
    const userInput = $('#user-input');
    const message = userInput.val().trim();

    const indexName = window.location.pathname.split('/').pop();

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
            url: `/api/v1/${indexName}/answer`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                "query": message,
                "conversation_id": currentConversationId
            }),
            success: function (response) {
                // Hide loader
                hideLoader();
                if (response.conversation_id) {
                    currentConversationId = response.conversation_id;
                }

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

async function clearHistory() {
    if (!currentConversationId) {
        console.warn('No active conversation to clear');
        return;
    }

    try {
        const response = await fetch(`/api/${indexName}/clear-history`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: currentConversationId
            })
        });

        const data = await response.json();
        if (data.message === "Chat history cleared successfully") {
            currentConversationId = null;
            // Update UI as needed
        }
    } catch (error) {
        console.error('Error clearing history:', error);
    }
}

function parseSimilarity(similarityStr) {
    // Return -1 for 'N/A' so it goes to the end when sorting
    if (similarityStr === 'N/A') return -1;
    // Otherwise parse the percentage
    return parseFloat(similarityStr.replace('%', ''));
}

// Handle Enter key
$(document).ready(function () {
    $('#user-input').keypress(function (e) {
        if (e.which == 13 && !$('#send-button').prop('disabled')) {
            sendMessage();
        }
    });

    window.marked.setOptions({
        breaks: true, // Adds <br> on single line breaks
        sanitize: false, // Allows HTML in markdown
        highlight: function (code, lang) {
            // Optional: Add syntax highlighting
            if (Prism && lang) { // If using Prism.js
                try {
                    return Prism.highlight(code, Prism.languages[lang], lang);
                } catch (e) {
                    return code;
                }
            }
            return code;
        }
    });
}); 