import {Col, Container, Row} from "react-bootstrap";
import React, { useState, useEffect, useRef } from 'react';
import '../assets/css/LLMChat.css';
import ReactMarkdown from 'react-markdown';

function LLMChat() {
    const [messages, setMessages] = useState([]);
    const [results, setResults] = useState([]);
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
            messageList.unshift({role: 'system', content: 'You are the PubMed Connection Specialist. Your purpose is to find papers related to topics that the person communicating with you is asking about. If the query is related to medicine or medical research, use the neo4j database to find answers.'});
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

        //const result = await fetch('https://data.ai.uky.edu/llm-upload/openai/v1/chat/completions', {
        const result = await fetch('http://localhost:5000/check-database', {
            method: 'POST',
            headers: {
                'Access-Control-Allow-Origin':'*',
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${import.meta.env.VITE_LLMF_API_KEY}`,
            },
            body: req
        })
            .then(response => response.json())
            .then(data => {
                //setResults([]); // clean slate before getting new results
                console.log(data);
                if (data.error) {
                    addMessage(data.error_message || 'Failed to submit query. Try reloading...', 'system');
                } else {
                    //addMessage(data.choices[0].message.content, 'system');
                    addMessage(data.response.explanation, 'system');
                    setResults(data.response.papers);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };

    const resetChat = () => {
        setMessages([]);
        setInstruction(null);
        setResults([]);
    };

    const testMessage = () => {
        addMessage('find articles about cancer.', 'user');
        processUserInput('find articles about cancer');
    };

    return (
        <Container className={"flex"} style={{ display: "flex", justifyContent: "space-between", height: "90vh !important"}}>
            <Col className="outer-container">
                <div className="chat-container">
                    <div className="chat-messages-container">
                        <div className="chat-messages" ref={chatMessagesRef}>
                            {messages.map((msg, index) => (
                                <div key={index} className={`message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
                                    <ReactMarkdown>
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            ))}
                        </div>
                        <div className="button-container">
                            <button className="reset-button" onClick={resetChat}>Reset</button>
                            <button className="reset-button" onClick={testMessage}>Test</button>
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
            </Col>
            <Col className="papers-container" style={{ flex: 1, marginLeft: "10px", border: "none", flexDirection: "column" }}>
                {results.length > 0 ? (
                    results.map((result, index) => (
                        <div key={index} className="panel-group">
                            <div className="panel panel-default">
                                <div className="panel-heading">
                                    <h4 className="panel-title">
                                        <a
                                            className="submit-button"
                                            data-bs-toggle="collapse"
                                            data-bs-target={`#collapse-${index}`}
                                            aria-expanded="false"
                                            aria-controls={`collapse-${index}`}
                                        >
                                            {result.title}
                                        </a>
                                    </h4>
                                </div>
                                <div
                                    id={`collapse-${index}`}
                                    className="panel-collapse collapse"
                                    aria-labelledby={`heading-${index}`}
                                >
                                    <div className="panel-body">
                                        <p><strong>Authors:</strong> {result.authors}</p>
                                        <p><strong>Abstract:</strong> {result.abstract}</p>
                                        {/*<p><strong>Citation:</strong> {result.citation}</p>*/}
                                        {/* Add any other fields you want to display */}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <>
                        <p>
                            The chat window to the left utilizes the Center for Applied Artificial Intelligence's Large Language
                            Model platform <a href={"https://hub.ai.uky.edu/llm-factory/"} target={"_blank"}>LLM Factory</a> to assist you in identifying
                            PubMed papers which relate to your question.
                        </p>
                        <p>
                            This part of the page will be populated with results from your query once you have asked a question.
                        </p>
                    </>
                )}
            </Col>

        </Container>
    )
}

export default LLMChat;