import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";

jest.mock("./components/AttendanceBot/AttendanceBot", () => () => (
  <div data-testid="attendance-bot" />
));
jest.mock("./components/GoshthiBot/GoshthiBot", () => () => (
  <div data-testid="goshthi-bot" />
));
jest.mock("./components/UserUpdateBot/UserUpdateBot", () => () => (
  <div data-testid="user-update-bot" />
));

describe("App", () => {
  it("renders the Attendance Bot tab and content by default", () => {
    render(<App />);
    expect(screen.getByText("Attendance Bot")).toBeInTheDocument();
    expect(screen.getByTestId("attendance-bot")).toBeInTheDocument();
  });

  it("shows the User Update Bot tab and it is enabled", () => {
    render(<App />);
    const tab = screen.getByRole("tab", { name: "User Update Bot" });
    expect(tab).toBeInTheDocument();
    expect(tab).not.toBeDisabled();
  });

  it("switches to GoshthiBot when the Goshthi Bot tab is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Goshthi Bot" }));
    expect(screen.queryByTestId("attendance-bot")).not.toBeInTheDocument();
    expect(screen.getByTestId("goshthi-bot")).toBeInTheDocument();
  });

  it("switches to UserUpdateBot when the tab is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "User Update Bot" }));
    expect(screen.queryByTestId("attendance-bot")).not.toBeInTheDocument();
    expect(screen.getByTestId("user-update-bot")).toBeInTheDocument();
  });

  it("switches back to AttendanceBot when Attendance Bot tab is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "User Update Bot" }));
    fireEvent.click(screen.getByRole("tab", { name: "Attendance Bot" }));
    expect(screen.getByTestId("attendance-bot")).toBeInTheDocument();
    expect(screen.queryByTestId("user-update-bot")).not.toBeInTheDocument();
  });
});
