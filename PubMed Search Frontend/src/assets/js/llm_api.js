
async function makeAPIcallPOST(server, apiPath, messagePayload, customHeaders, timeout = 60) {
    const url = server + apiPath;
    const headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'wp-openAI v1',
        ...customHeaders
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(messagePayload),
            timeout: timeout * 1000 // Convert to milliseconds
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            return { success: true, response: jsonResponse };
        } else {
            console.error(`HTTP error: ${response.status}`);
            return { success: false, error_message: `Failed to complete POST to ${server}` };
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error("Fetch error: Operation timed out");
            return { success: false, error_message: "Request timed out" };
        } else {
            console.error(`Fetch error: ${error.message}`);
            return { success: false, error_message: "Failed to complete POST to " + server };
        }
    }
}

// Function to query the model
async function queryModel(messages, model = "", maxNewTokens = 200, temperature = 0.7) {
    const header = { "Authorization": `Bearer ${import.meta.env.VITE_OPEN_AI_API_KEY}` };
    console.log(import.meta.env.VITE_OPEN_AI_API_KEY)
    const postMessage = {
        messages: messages,
        model: model,
        max_tokens: maxNewTokens,
        temperature: temperature
    };
    return await makeAPIcallPOST("https://data.ai.uky.edu/llm-upload", "/openai/v1/chat/completions", postMessage, header);
}

// Register the REST API endpoint for POST requests
const express = require('express');
const app = express();
app.use(express.json());

app.post('/openai/v1', async (req, res) => {
    const params = req.body;
    let success = false;
    let error_message = null;
    let response = null;

    const model = "";
    let maxNewTokens = 200;
    let temperature = 0.7;

    try {
        if (params.messages) {
            const messages = params.messages;
            if (params.max_tokens) {
                maxNewTokens = params.max_tokens;
            }
            if (params.temperature) {
                temperature = params.temperature;
            }
            const modelResponse = await queryModel(messages, model, maxNewTokens, temperature);
            if (modelResponse.success && modelResponse.response) {
                response = modelResponse.response;
                success = true;
            } else if (modelResponse.error_message) {
                error_message = modelResponse.error_message;
            } else {
                error_message = "Failed to communicate with API server";
            }
        } else {
            error_message = "Must include messages in request";
        }
    } catch (e) {
        error_message = e.message;
    }

    const ret = {
        success: success,
        error_message: error_message,
        response: response
    };
    res.json(ret);
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});

// Function to include HTML file content
const fs = require('fs');
const path = require('path');

function includeHTMLFile(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                reject('HTML file not found');
            } else {
                resolve(data);
            }
        });
    });
}

// Shortcode functions
async function includeLLMCompare() {
    const htmlFilePath = path.join(__dirname, 'compare.html');
    try {
        return await includeHTMLFile(htmlFilePath);
    } catch (error) {
        return error;
    }
}

async function includeLLMChat() {
    const htmlFilePath = path.join(__dirname, 'chat.html');
    try {
        return await includeHTMLFile(htmlFilePath);
    } catch (error) {
        return error;
    }
}