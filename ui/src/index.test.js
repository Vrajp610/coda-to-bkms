import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

jest.mock("./App", () => () => <div>Mocked App</div>);

describe("index.js", () => {
    it("renders without crashing", () => {
        const rootDiv = document.createElement("div");
        rootDiv.id = "root";
        document.body.appendChild(rootDiv);

        const root = ReactDOM.createRoot(rootDiv);
        expect(() => {
        root.render(
            <React.StrictMode>
            <App />
            </React.StrictMode>
        );
        }).not.toThrow();

        document.body.removeChild(rootDiv);
    });

    it("calls ReactDOM.createRoot with the root element", () => {
        const createRootSpy = jest.spyOn(ReactDOM, "createRoot");
        const rootDiv = document.createElement("div");
        rootDiv.id = "root";
        document.body.appendChild(rootDiv);

        ReactDOM.createRoot(rootDiv);

        expect(createRootSpy).toHaveBeenCalledWith(rootDiv);

        createRootSpy.mockRestore();
        document.body.removeChild(rootDiv);
    });

    it("calls root.render with <React.StrictMode><App /></React.StrictMode>", () => {
        const rootDiv = document.createElement("div");
        rootDiv.id = "root";
        document.body.appendChild(rootDiv);

        const mockRender = jest.fn();
        jest.spyOn(ReactDOM, "createRoot").mockReturnValue({ render: mockRender });

        require("./index.js");

        expect(mockRender).toHaveBeenCalledTimes(1);
        const renderedElement = mockRender.mock.calls[0][0];
        expect(renderedElement.type).toBe(React.StrictMode);
        expect(renderedElement.props.children.type).toBe(require("./App").default || require("./App"));

        document.body.removeChild(rootDiv);
        jest.resetModules();
    });
});