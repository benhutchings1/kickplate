import React, { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import BaseLayout from "./pages/Layout";
import { sidebarPageDirectory as pageDir } from "./pages/pageDirectory";
import ThemeContextProvider from "./contexts/theme/ThemeContextProvider";
// Bootstrap Bundles
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";

class App extends Component {
  render() {
    return (
      <ThemeContextProvider>
        <BrowserRouter>
          <Routes>
            {pageDir.map((page) => (
              <Route path={page.link} element={React.createElement(page.element)}>
              </Route>
            ))}
          </Routes>
        </BrowserRouter>
      </ThemeContextProvider>
    );
  }
}

export default App;
