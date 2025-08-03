import { render, screen } from "@testing-library/react";
import CustomAlert from "./CustomAlert";
import "@testing-library/jest-dom";

describe("CustomAlert", () => {
  it("renders with correct severity and children", () => {
    render(<CustomAlert severity="success">Success message</CustomAlert>);
    expect(screen.getByText("Success message")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveClass("MuiAlert-standardSuccess");
  });

  it("renders with error severity", () => {
    render(<CustomAlert severity="error">Error occurred</CustomAlert>);
    expect(screen.getByText("Error occurred")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveClass("MuiAlert-standardError");
  });

  it("renders with warning severity", () => {
    render(<CustomAlert severity="warning">Warning!</CustomAlert>);
    expect(screen.getByText("Warning!")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveClass("MuiAlert-standardWarning");
  });

  it("renders with info severity", () => {
    render(<CustomAlert severity="info">Info here</CustomAlert>);
    expect(screen.getByText("Info here")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveClass("MuiAlert-standardInfo");
  });

  it("applies custom className", () => {
    render(
      <CustomAlert severity="info" className="my-custom-class">
        Custom class
      </CustomAlert>
    );
    expect(screen.getByRole("alert")).toHaveClass("my-custom-class");
  });

  it("renders children as nodes", () => {
    render(
      <CustomAlert severity="success">
        <span data-testid="child-node">Node Child</span>
      </CustomAlert>
    );
    expect(screen.getByTestId("child-node")).toBeInTheDocument();
  });

  it("handles missing severity gracefully", () => {
    render(<CustomAlert>Missing severity</CustomAlert>);
    expect(screen.getByText("Missing severity")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("handles empty children", () => {
    render(<CustomAlert severity="info" />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("handles undefined className", () => {
    render(<CustomAlert severity="info">No className</CustomAlert>);
    expect(screen.getByText("No className")).toBeInTheDocument();
  });
});
