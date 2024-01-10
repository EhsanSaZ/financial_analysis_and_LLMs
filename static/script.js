function askQuestion() {
            var userQuestion = document.getElementById('user-question').value;
            displayMessage(userQuestion, 'user');
            displayMessage("Server is collecting the articles and synthesizing the response. Please wait while the server is processing your request. This might take several minutes.", 'bot');
            if (userQuestion.trim() !== '') {
                // Send the user's question to the server using AJAX
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/ask', true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                xhr.onload = function () {
                    if (xhr.status === 200) {
                        var botResponse = JSON.parse(xhr.responseText)['bot_response'];

                        displayMessage(botResponse, 'bot');
                        document.getElementById('user-question').value = '';
                    } else {
                        displayMessage(`Error: ${xhr.status} - ${xhr.statusText}`, 'bot');
                        document.getElementById('user-question').value = '';
                    }
                };
                xhr.send('user_question=' + encodeURIComponent(userQuestion));
            }
        }

        function displayMessage(message, sender) {



            var chatDisplay = document.getElementById('chat-display');
            // Check if the sender is the user before clearing the content
            if (sender === 'user') {
                // Clear existing content
                chatDisplay.innerHTML = '';
            }
            var messageElement = document.createElement('div');
            messageElement.className = sender;
            messageElement.textContent = message;
            chatDisplay.appendChild(messageElement);
        }