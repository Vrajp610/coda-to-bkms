import { render, screen, fireEvent } from "@testing-library/react";
import Button from "./Button";

jest.mock("@mui/material", () => ({
  Button: ({ onClick, disabled, className, variant, children }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={className}
      data-variant={variant}
    >
      {children}
    </button>
  ),
}));

describe("Button component", () => {
  it("renders children correctly", () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText("Click Me")).toBeInTheDocument();
  });

  it("calls onClick when clicked and not disabled", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(handleClick).toHaveBeenCalled();
  });

  it("does not call onClick when disabled", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("applies the className prop", () => {
    render(<Button className="test-class">Class</Button>);
    expect(screen.getByText("Class")).toHaveClass("test-class");
  });

  it("uses variant='contained' by default", () => {
    render(<Button>Variant</Button>);
    expect(screen.getByText("Variant")).toHaveAttribute("data-variant", "contained");
  });
});
