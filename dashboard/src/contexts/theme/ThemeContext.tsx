import React from "react";

export default React.createContext({
  theme: "dark",
  setTheme: (theme: string) => {}
});
