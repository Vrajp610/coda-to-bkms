import { render, screen } from "@testing-library/react";
import { act } from "react";
import GoshthiBot from "./GoshthiBot";
import * as functions from "../../utils/functions";

jest.mock("./GoshthiBot.module.css", () => ({
  container: "container",
  title: "title",
}));

let lastGoshthiFormProps = {};
jest.mock("../GoshthiForm/GoshthiForm", () => (props) => {
  lastGoshthiFormProps = props;
  return <div data-testid="goshthi-form" />;
});

jest.mock("../../utils/CONSTANTS", () => ({
  CONSTANTS: {
    GOSHTHI_BOT: "BKMS Goshthi Bot",
    YES: "Yes",
  },
}));

describe("GoshthiBot", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    lastGoshthiFormProps = {};
  });

  it("renders the title and GoshthiForm", () => {
    render(<GoshthiBot />);
    expect(screen.getByText("BKMS Goshthi Bot")).toBeInTheDocument();
    expect(screen.getByTestId("goshthi-form")).toBeInTheDocument();
  });

  it("passes required props to GoshthiForm", () => {
    render(<GoshthiBot />);
    [
      "selectedMonth", "setSelectedMonth",
      "goshthiHeld", "setGoshthiHeld",
      "hangout", "setHangout",
      "workshop", "setWorkshop",
      "loading", "runBot",
      "logs", "countdown",
    ].forEach((prop) => {
      expect(lastGoshthiFormProps).toHaveProperty(prop);
    });
  });

  it("handles state changes for all fields", async () => {
    render(<GoshthiBot />);
    const month = new Date(2026, 0, 1);
    await act(async () => {
      lastGoshthiFormProps.setSelectedMonth(month);
      lastGoshthiFormProps.setGoshthiHeld("Yes");
      lastGoshthiFormProps.setHangout("No");
      lastGoshthiFormProps.setWorkshop("Yes");
    });
    expect(lastGoshthiFormProps.selectedMonth).toBe(month);
    expect(lastGoshthiFormProps.goshthiHeld).toBe("Yes");
    expect(lastGoshthiFormProps.hangout).toBe("No");
    expect(lastGoshthiFormProps.workshop).toBe("Yes");
  });

  it("calls runGoshthiBot when runBot prop is invoked", async () => {
    const spy = jest.spyOn(functions, "runGoshthiBot").mockResolvedValue();
    render(<GoshthiBot />);
    await act(async () => {
      lastGoshthiFormProps.runBot();
    });
    expect(spy).toHaveBeenCalled();
  });
});
