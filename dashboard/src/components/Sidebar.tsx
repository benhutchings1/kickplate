import { Navbar, Nav } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRocket, faSun } from "@fortawesome/free-solid-svg-icons";
import { useContext } from "react";
import ThemeContext from "../contexts/theme/ThemeContext";
import ThemeToggleSwitch from "./ThemeToggler";
import { pageMap } from "../pages/pageDirectory";

interface Props {
  pageDir: Array<pageMap>;
}

export const Sidebar = (props: Props) => {
  const { pageDir } = props;
  const { theme, setTheme } = useContext(ThemeContext);

  return (
    <Navbar className="canvas-sidebar flex-column p-5">
      <Navbar.Brand className="navbrand mb-4" href="/">
        <FontAwesomeIcon icon={faRocket} className="icon mr-2" />
        <span className="brand">Execution Dashboard</span>
      </Navbar.Brand>
      <Nav className="flex-column">
        {pageDir.map((page) => (
          <Nav.Link href={page.link}>
            <FontAwesomeIcon icon={page.icon} className="icon mr-2" />
            <span className="item-text">{page.name}</span>
          </Nav.Link>
        ))}
      </Nav>

      <Nav variant={theme} className="mt-auto text-center">
        <div>
          <span className="item-text">
            <FontAwesomeIcon icon={faSun} className="icon mr-2" />
            Toggle Light Mode
          </span>
          <div className="mt-2">
            <ThemeToggleSwitch theme={theme} setTheme={setTheme} />
          </div>
        </div>
      </Nav>
    </Navbar>
  );
};
