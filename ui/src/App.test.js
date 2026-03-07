import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";

jest.mock("./components/AttendanceBot/AttendanceBot", () => () => (
  <div data-testid="attendance-bot" />
));
jest.mock("./components/UserUpdateBot/UserUpdateBot", () => () => (
  <div data-testid="user-update-bot" />
));

describe("App", () => {
  it("renders the AttendanceBot tab by default", () => {
    render(<App />);
    expect(screen.getByTestId("attendance-bot")).toBeInTheDocument();
    expect(screen.queryByTestId("user-update-bot")).not.toBeInTheDocument();
  });

  it("renders both tab labels", () => {
    render(<App />);
    expect(screen.getByText("Attendance Bot")).toBeInTheDocument();
    expect(screen.getByText("User Update Bot")).toBeInTheDocument();
  });

  it("switches to UserUpdateBot when the User Update Bot tab is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByText("User Update Bot"));
    expect(screen.queryByTestId("attendance-bot")).not.toBeInTheDocument();
    expect(screen.getByTestId("user-update-bot")).toBeInTheDocument();
  });
});
