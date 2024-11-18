import React, { ReactElement, useState } from "react";
import ThemeContext from "./ThemeContext";
import Cookie from "js-cookie";

interface Props {
  children?: React.ReactNode;
}
const ThemeContextProvider = ({ children }: Props): ReactElement<any, any> => {
  const storedTheme = Cookie.get("theme");
  const [theme, setTheme] = useState(
    storedTheme == null ? "dark" : storedTheme,
  );
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
export default ThemeContextProvider;
