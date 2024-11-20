import { useState } from 'react'
import {BrowserRouter} from "react-router-dom";
import './assets/css/App.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import Router from "./Router.jsx";
import Header from "./Header.jsx";
import Footer from "./Footer.jsx";

function App() {
  return (
    <>
        <BrowserRouter>
            <Header/>
            <Router/>
            <Footer/>
        </BrowserRouter>
    </>
  )
}

export default App
