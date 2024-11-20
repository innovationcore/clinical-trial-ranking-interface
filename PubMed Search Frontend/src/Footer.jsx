import React from 'react';
import {Container} from "react-bootstrap";

function Footer() {
    return (
        <footer className="fixed-bottom bg-light" id="footer">
            <Container className="d-flex justify-content-center">
                <span>Available under the GNU v3.0.</span>
            </Container>
        </footer>
    );
}

export default Footer;