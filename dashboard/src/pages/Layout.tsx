import { useContext } from "react";
import { Sidebar } from "../components/Sidebar";
import ThemeContext from "../contexts/theme/ThemeContext";
import { sidebarPageDirectory } from "./PageDirectory";

interface Props {
  children?;
}

export const BaseLayout = (props: Props) => {
  const { theme } = useContext(ThemeContext);

  return (
    <div className={ theme }>
      <div className="canvas-container">
        <Sidebar pageDir={sidebarPageDirectory} >
          this is the main page
          {props.children}
        </Sidebar>
      </div>
    </div>
  );
};
export default BaseLayout;
