import React, {useEffect, useRef, useState} from 'react';
import {Col, Container, Nav, Navbar, NavbarBrand, NavLink, NavDropdown, NavbarToggle, NavbarCollapse} from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.jsx';

function Header() {
    const [headerHeight, setHeaderHeight] = useState(0);
    const navbarRef = useRef(null);

    useEffect(() => {
        const handleResize = () => {
            if (navbarRef.current) {
                setHeaderHeight(navbarRef.current.clientHeight);
            }
        };

        // Calculate header height on mount and on resize
        handleResize();
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [headerHeight]);

    return (
        <>
            {/* Took out fixed top */}
            <Navbar ref={navbarRef} bg="light" expand="md" fixed="top" onLoad={setHeaderHeight}>
                <Container className="d-flex">
                    <Col style={{whiteSpace: 'nowrap'}}>
                        <Nav className={"align-items-end align-text-bottom justify-content-center"}>
                            <NavLink id="navbar-name" className="navbar-comp" href="/">
                                PubMed Search Assistant
                            </NavLink>
                        </Nav>
                    </Col>
                    <Col>
                        <NavbarToggle aria-controls="basic-navbar-nav" />
                        <NavbarCollapse id="basic-navbar-nav">
                            <Nav className="ms-auto" activeKey={location.pathname}>
                                <Nav.Item className="navbar-comp">
                                    <NavLink href="/">Home</NavLink>
                                </Nav.Item>
                                <Nav.Item className="navbar-comp">
                                    <NavLink href="/chat-search">Search</NavLink>
                                </Nav.Item>
                                <Nav.Item className="navbar-comp">
                                    <NavLink href="/knowledge-graph">Knowledge Graph</NavLink>
                                </Nav.Item>
                            </Nav>
                        </NavbarCollapse>
                    </Col>
                </Container>
            </Navbar>
            <div style={{ marginTop: headerHeight + 20 + "px" }}></div>
        </>
    );
}

export default Header;