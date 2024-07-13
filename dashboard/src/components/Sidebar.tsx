import { Navbar, Nav } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  IconDefinition,
  faRocket,
  faSun,
} from "@fortawesome/free-solid-svg-icons";
import { useContext } from "react";
import ThemeContext from "../contexts/theme/ThemeContext";
import ThemeToggleSwitch from "./ThemeToggler";
export type pageMap = {
  name: string;
  link: string;
  icon: IconDefinition;
};
interface Props {
  pageDir: Array<pageMap>;
}

export const Sidebar = (props: Props) => {
  const { pageDir } = props;
  const { theme, setTheme } = useContext(ThemeContext);
  const oppTheme = theme === "dark" ? "light" : "dark";
  let navfooter = `mt-auto text-center text-${oppTheme}`;
  let navfooterText = `text-${oppTheme}`;
  

  return (
    <Navbar
      bg={theme}
      variant={theme}
      className="sidebar d-flex flex-column p-3"
      style={{ height: "100vh", width: "350px" }}
    >
      <Navbar.Brand href="#home" className="mb-4">
        <h5>
          <FontAwesomeIcon
            icon={faRocket}
            className="mr-2"
            style={{ paddingRight: "10px" }}
          />
          Execution Dashboard
        </h5>
      </Navbar.Brand>
      <Nav className="flex-column">
        {pageDir.map((page) => (
          <Nav.Link href={page.link}>
            <FontAwesomeIcon
              icon={page.icon}
              className="mr-2"
              style={{ paddingRight: "10px" }}
            />
            {page.name}
          </Nav.Link>
        ))}
      </Nav>

      <Nav variant={theme} className={navfooter}>
        <div>
          <p className={navfooterText} style={{ marginBottom: "5px" }}>
            <FontAwesomeIcon
              icon={faSun}
              className="mr-2"
              style={{ paddingRight: "10px" }}
            />
            Toggle Dark Mode
          </p>
          <ThemeToggleSwitch theme={theme} setTheme={setTheme}/>
        </div>
      </Nav>
    </Navbar>
  );
};
