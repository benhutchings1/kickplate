import { Navbar, Nav } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRocket, faSun, faBars } from "@fortawesome/free-solid-svg-icons";
import { useContext } from "react";
import ThemeContext from "../contexts/theme/ThemeContext";
import ThemeToggleSwitch from "./ThemeToggler";
import { pageMap } from "../pages/PageDirectory";
import Offcanvas from 'react-bootstrap/Offcanvas';
import { useState } from 'react';
import Button from 'react-bootstrap/Button';


interface Props {
  pageDir: Array<pageMap>;
  children?;
}

export const Sidebar = (props: Props) => {
  const { pageDir } = props;
  const { theme, setTheme } = useContext(ThemeContext);

  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <div className="navbar">
        <div className="button-wrapper">
          <Button onClick={handleShow} className="open-bar-button">
            <FontAwesomeIcon icon={faBars} className="open-bar-icon"/>
          </Button>
        </div>
      </div>
      <div className="main-canvas">
        <div className="p-3">
          {props.children}
        </div>
      </div>
      <Offcanvas show={show} className={ theme + " sidebar"  } onHide={handleClose}>
          <Offcanvas.Header className="title text-centere" closeButton>
            <Offcanvas.Title>
              <FontAwesomeIcon icon={faRocket} className="icon mr-2" />
              <span className="brand">Execution Dashboard</span>
            </Offcanvas.Title>
          </Offcanvas.Header>
            <Offcanvas.Body>
              <Nav className="nav-item flex-column text-center">
                {pageDir.map((page) => (
                  <Nav.Link href={page.link}>
                    <FontAwesomeIcon icon={page.icon} className="icon" />
                    <span className="item-t ext">{page.name}</span>
                  </Nav.Link>
                ))}
              </Nav>
              <div className="theme-toggle text-center">
                  <div className="theme-toggle-text">
                    <div>
                      <FontAwesomeIcon icon={faSun} className="icon" />
                    </div>
                    <div>
                      Toggle Light Mode
                    </div>
                  </div>
                  <div className="theme-toggle-switch">
                    <ThemeToggleSwitch theme={theme} setTheme={setTheme} />
                  </div>
              </div>
            </Offcanvas.Body>
      </Offcanvas>
    </>
  );
};

