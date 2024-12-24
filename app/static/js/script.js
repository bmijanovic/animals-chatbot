async function askQuestion() {
    const questionInput = document.getElementById("question");
    const question = questionInput.value;
    const chatHistory = document.getElementById("chat-history");
    const questionContainer = document.getElementById("question-container");

    if (!question) {
        return;
    }

    questionContainer.style.display = 'none';

    const chatItem = document.createElement("div");
    chatItem.classList.add("chat-item");

    // Question container with human emoji on the right
    const questionContainerElement = document.createElement("div");
    questionContainerElement.classList.add("question-container");

    const questionElement = document.createElement("div");
    questionElement.classList.add("question");
    questionElement.innerHTML = `${question}`;

    const emojiHuman = document.createElement("span");
    emojiHuman.classList.add("emoji-human");
    emojiHuman.innerText = "👨‍🦲";

    questionContainerElement.appendChild(questionElement);
    questionContainerElement.appendChild(emojiHuman);

    // Answer container with robot emoji outside the box
    const answerContainerElement = document.createElement("div");
    answerContainerElement.classList.add("answer-container");

    const thinkingElement = document.createElement("div");
    thinkingElement.classList.add("answer");
    thinkingElement.innerText = "Thinking...";

    const emojiRobot = document.createElement("span");
    emojiRobot.classList.add("emoji-robot");
    emojiRobot.innerText = "🤖";

    answerContainerElement.appendChild(emojiRobot);
    answerContainerElement.appendChild(thinkingElement);

    // Add new item (question + answer) to the chat history
    chatItem.appendChild(questionContainerElement);
    chatItem.appendChild(answerContainerElement);

    // Append chat item to chat history
    chatHistory.appendChild(chatItem);

    // Scroll to the bottom of the chat history
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Divider between each chat item
    const divider = document.createElement("hr");
    chatHistory.appendChild(divider);

    questionInput.value = "";
    try {
        const response = await fetch("/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });

        const data = await response.json();

        // Update the "Thinking..." message with the answer
        thinkingElement.innerHTML = `${data.answer || "No response."}`;
    } catch (error) {
        thinkingElement.innerText = "An error occurred. Please try again.";
        console.error(error);
    } finally {
        questionContainer.style.display = 'block';
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}
