import {Container, Row} from "react-bootstrap";
import React, { useState, useEffect, useRef } from 'react';
import '../assets/css/LLMChat.css';

function LLMChat() {
    const [messages, setMessages] = useState([]);
    //const [requestData, setRequestData] = useState({});
    const [input, setInput] = useState('');
    const [instruction, setInstruction] = useState(false);
    const [example, setExample] = useState(1);
    const chatMessagesRef = useRef(null);

    useEffect(() => {
        chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }, [messages]);

    const addMessage = (message, role) => {
        setMessages(prevMessages => [...prevMessages, { role: role,content: message }]);
    };

    const handleInput = () => {
        if (input !== '') {
            addMessage(input, 'user');
            processUserInput(input);
            setInput('');
        }
    };

    const processUserInput = async (message) => {
        const messageList = [];

        if (!instruction) {
            messageList.unshift({role: 'user', content: message});
            messageList.unshift({role: 'system', content: 'Answer the questions as an expert on the PubMed corpus of research papers.'});
            setInstruction(true);
        }
        else {
            messageList.unshift({role: 'user', content: message});
        }

        const req = JSON.stringify({
            messages: messageList,
            model: "",
            max_tokens: 500,
            temperature: 0.7,
        });

        const result = await fetch('https://data.ai.uky.edu/llm-upload/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${import.meta.env.VITE_LLMF_API_KEY}`,
            },
            body: req
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage(data.error_message || 'Failed to submit query. Try reloading...', 'system');
                } else {
                    addMessage(data.choices[0].message.content, 'system');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };


    const resetChat = () => {
        setMessages([]);
        setInstruction(null);
        setExample(1);
    };

    return (
        <Container>
            {/*<h1 className="sub-headers">Chat With Our LLM</h1>*/}
            <div className="outer-container">
                <div className="chat-container">
                    <div className="chat-messages-container">
                        <div className="chat-messages" ref={chatMessagesRef}>
                            {messages.map((msg, index) => (
                                <div key={index} className={`message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
                                    {msg.content}
                                </div>
                            ))}
                        </div>
                        <div className="button-container">
                            <button className="reset-button" onClick={resetChat}>Reset</button>
                        </div>
                    </div>
                    <div className="chat-input-container">
                        <input
                            type="text"
                            className="chat-input"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message..."
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    handleInput();
                                }
                            }}
                            style={{zIndex: 999}}
                        />
                        <button className="submit-button" onClick={handleInput} style={{zIndex: 999}}>Submit</button>
                    </div>
                </div>
            </div>
        </Container>
    )
}

export default LLMChat;