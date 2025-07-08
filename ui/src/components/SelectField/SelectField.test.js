import { render, screen, fireEvent } from "@testing-library/react";
import SelectField from "./SelectField";

jest.mock("@mui/material", () => ({
  FormControl: ({ children, ...props }) => <div data-testid="form-control">{children}</div>,
  InputLabel: ({ children, ...props }) => <label data-testid="input-label" {...props}>{children}</label>,
  Select: ({ children, value, onChange, labelId, label, ...props }) => (
    <select
      aria-labelledby={labelId}
      aria-label={label}
      value={value}
      onChange={onChange}
      data-testid="select"
      {...props}
    >
      {children}
    </select>
  ),

  MenuItem: ({ value, children }) =>
    value === ""
      ? <option value="">{children.props ? children.props.children : children}</option>
      : <option value={value}>{children}</option>,
}));

describe("SelectField component", () => {
  const options = [
    { value: "one", label: "One" },
    { value: "two", label: "Two" },
  ];

  it("renders with placeholder and options", () => {
    render(
      <SelectField
        value=""
        onChange={() => {}}
        options={options}
        placeholder="Pick one"
        ariaLabel="test-select"
      />
    );

    expect(screen.getByTestId("input-label")).toHaveTextContent("Pick one");
    const optionsList = screen.getAllByRole("option");
    expect(optionsList[0]).toHaveTextContent("Pick one");
    expect(optionsList[1]).toHaveTextContent("One");
    expect(optionsList[2]).toHaveTextContent("Two");
  });

  it("calls onChange when an option is selected", () => {
    const handleChange = jest.fn();
    render(
      <SelectField
        value=""
        onChange={handleChange}
        options={options}
        placeholder="Pick one"
        ariaLabel="test-select"
      />
    );
    fireEvent.change(screen.getByTestId("select"), { target: { value: "two" } });
    expect(handleChange).toHaveBeenCalled();
  });

  it("sets the correct value", () => {
    render(
      <SelectField
        value="two"
        onChange={() => {}}
        options={options}
        placeholder="Pick one"
        ariaLabel="test-select"
      />
    );
    expect(screen.getByTestId("select").value).toBe("two");
  });
});