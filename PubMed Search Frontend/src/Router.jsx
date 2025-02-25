import {Route, Routes} from "react-router-dom";

import React from "react";
import LLMChat from "./components/LLMChat.jsx";
import LandingPage from "./components/LandingPage.jsx";
import KnowledgeGraph from "./components/KnowledgeGraph.jsx";
import Neo4JGraph from "./components/Neo4JGraph.jsx";

function Router() {
    return(
        <Routes>
            <Route exact path="/" element={<LandingPage/>}/>
            <Route exact path="/chat-search" element={<LLMChat/>}/>
            <Route exact path="/knowledge-graph" element={<Neo4JGraph/>}/>
        </Routes>
    );
}
export default Router;