import { render, screen, fireEvent } from "@testing-library/react";
import GoshthiForm from "./GoshthiForm";

jest.mock("./GoshthiForm.module.css", () => ({
  form: "form",
  sectionLabel: "sectionLabel",
  monthGrid: "monthGrid",
  monthTile: "monthTile",
  monthTileActive: "monthTileActive",
  monthLabel: "monthLabel",
  monthValue: "monthValue",
  toggle: "toggle",
  toggleBtn: "toggleBtn",
  toggleBtnActive: "toggleBtnActive",
  countdown: "countdown",
  logBox: "logBox",
  logLine: "logLine",
  logHeader: "logHeader",
  logError: "logError",
}));

jest.mock("../../utils/CONSTANTS", () => ({
  CONSTANTS: {
    YES: "Yes",
    NO: "No",
    RUN_BOT: "Run Bot",
    RUNNING: "Running...",
  },
}));

jest.mock("../Button/Button", () => (props) => (
  <button onClick={props.onClick} disabled={props.disabled}>
    {props.children}
  </button>
));

const defaultProps = {
  selectedMonth: null,
  setSelectedMonth: jest.fn(),
  goshthiHeld: "",
  setGoshthiHeld: jest.fn(),
  hangout: "",
  setHangout: jest.fn(),
  workshop: "",
  setWorkshop: jest.fn(),
  loading: false,
  runBot: jest.fn(),
  logs: [],
  countdown: null,
};

describe("GoshthiForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  it("renders 4 month tiles", () => {
    render(<GoshthiForm {...defaultProps} />);
    expect(screen.getByText("2 Months Ago")).toBeInTheDocument();
    expect(screen.getByText("Last Month")).toBeInTheDocument();
    expect(screen.getByText("This Month")).toBeInTheDocument();
    expect(screen.getByText("Next Month")).toBeInTheDocument();
  });

  it("calls setSelectedMonth when a month tile is clicked", () => {
    const setSelectedMonth = jest.fn();
    render(<GoshthiForm {...defaultProps} setSelectedMonth={setSelectedMonth} />);
    fireEvent.click(screen.getByText("This Month").closest("button"));
    expect(setSelectedMonth).toHaveBeenCalledWith(expect.any(Date));
  });

  it("applies monthTileActive class to the matching selected month", () => {
    const today = new Date();
    const thisMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    render(<GoshthiForm {...defaultProps} selectedMonth={thisMonth} />);
    const btn = screen.getByText("This Month").closest("button");
    expect(btn.className).toContain("monthTileActive");
  });

  it("does not apply monthTileActive when selectedMonth is null", () => {
    render(<GoshthiForm {...defaultProps} selectedMonth={null} />);
    const btn = screen.getByText("This Month").closest("button");
    expect(btn.className).not.toContain("monthTileActive");
  });

  it("renders Was Goshthi Held Yes/No toggle", () => {
    render(<GoshthiForm {...defaultProps} />);
    expect(screen.getAllByText("Yes").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("No").length).toBeGreaterThanOrEqual(1);
  });

  it("calls setGoshthiHeld when a toggle is clicked", () => {
    const setGoshthiHeld = jest.fn();
    render(<GoshthiForm {...defaultProps} setGoshthiHeld={setGoshthiHeld} />);
    fireEvent.click(screen.getAllByText("Yes")[0]);
    expect(setGoshthiHeld).toHaveBeenCalledWith("Yes");
  });

  it("applies toggleBtnActive to the selected toggle option", () => {
    render(<GoshthiForm {...defaultProps} goshthiHeld="Yes" />);
    expect(screen.getAllByText("Yes")[0].className).toContain("toggleBtnActive");
  });

  it("does not apply toggleBtnActive to the unselected option", () => {
    render(<GoshthiForm {...defaultProps} goshthiHeld="Yes" />);
    expect(screen.getAllByText("No")[0].className).not.toContain("toggleBtnActive");
  });

  it("shows hangout and workshop fields when goshthiHeld is Yes", () => {
    render(<GoshthiForm {...defaultProps} goshthiHeld="Yes" />);
    expect(screen.getByText("Was this a Hangout?")).toBeInTheDocument();
    expect(screen.getByText("Was a Karyakar Workshop Held?")).toBeInTheDocument();
  });

  it("hides hangout and workshop fields when goshthiHeld is not Yes", () => {
    render(<GoshthiForm {...defaultProps} goshthiHeld="" />);
    expect(screen.queryByText("Was this a Hangout?")).not.toBeInTheDocument();
    expect(screen.queryByText("Was a Karyakar Workshop Held?")).not.toBeInTheDocument();
  });

  it("calls setHangout when its toggle is clicked", () => {
    const setHangout = jest.fn();
    render(<GoshthiForm {...defaultProps} goshthiHeld="Yes" setHangout={setHangout} />);
    fireEvent.click(screen.getAllByText("No")[1]);
    expect(setHangout).toHaveBeenCalledWith("No");
  });

  it("calls setWorkshop when its toggle is clicked", () => {
    const setWorkshop = jest.fn();
    render(<GoshthiForm {...defaultProps} goshthiHeld="Yes" setWorkshop={setWorkshop} />);
    fireEvent.click(screen.getAllByText("Yes")[2]);
    expect(setWorkshop).toHaveBeenCalledWith("Yes");
  });

  it("disables Run Bot when no fields filled", () => {
    render(<GoshthiForm {...defaultProps} />);
    expect(screen.getByText("Run Bot")).toBeDisabled();
  });

  it("enables Run Bot when selectedMonth set and goshthiHeld=No", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="No"
      />
    );
    expect(screen.getByText("Run Bot")).not.toBeDisabled();
  });

  it("disables Run Bot when goshthiHeld=Yes but hangout/workshop missing", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="Yes"
        hangout=""
        workshop=""
      />
    );
    expect(screen.getByText("Run Bot")).toBeDisabled();
  });

  it("enables Run Bot when all fields including hangout and workshop are filled", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="Yes"
        hangout="No"
        workshop="Yes"
      />
    );
    expect(screen.getByText("Run Bot")).not.toBeDisabled();
  });

  it("shows Running... and disables button when loading", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="No"
        loading={true}
      />
    );
    expect(screen.getByText("Running...")).toBeDisabled();
  });

  it("calls runBot when the button is clicked", () => {
    const runBot = jest.fn();
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="No"
        runBot={runBot}
      />
    );
    fireEvent.click(screen.getByText("Run Bot"));
    expect(runBot).toHaveBeenCalled();
  });

  it("renders log lines when logs are provided", () => {
    render(<GoshthiForm {...defaultProps} logs={["Step 1", "Step 2"]} />);
    expect(screen.getByText("Step 1")).toBeInTheDocument();
    expect(screen.getByText("Step 2")).toBeInTheDocument();
  });

  it("applies logError class to log lines containing ERROR", () => {
    render(<GoshthiForm {...defaultProps} logs={["ERROR: something failed"]} />);
    const line = screen.getByText("ERROR: something failed");
    expect(line.className).toContain("logError");
  });

  it("applies logHeader class to log lines starting with ---", () => {
    render(<GoshthiForm {...defaultProps} logs={["--- Section ---"]} />);
    const line = screen.getByText("--- Section ---");
    expect(line.className).toContain("logHeader");
  });

  it("does not render log box when logs are empty and not loading", () => {
    render(<GoshthiForm {...defaultProps} logs={[]} loading={false} />);
    expect(screen.queryByRole("log")).not.toBeInTheDocument();
  });

  it("renders log box when loading even with no logs", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="No"
        loading={true}
        logs={[]}
      />
    );
    expect(screen.getByRole("log")).toBeInTheDocument();
  });

  it("shows '...' loading indicator when loading and countdown is null", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="No"
        loading={true}
        logs={[]}
        countdown={null}
      />
    );
    expect(screen.getByText("...")).toBeInTheDocument();
  });

  it("shows countdown when loading and countdown is set", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        selectedMonth={new Date()}
        goshthiHeld="No"
        loading={true}
        countdown={15}
      />
    );
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByText(/15s remaining/)).toBeInTheDocument();
  });

  it("does not show countdown when not loading", () => {
    render(<GoshthiForm {...defaultProps} countdown={15} loading={false} />);
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("log box has correct aria attributes", () => {
    render(<GoshthiForm {...defaultProps} logs={["hello"]} />);
    const logBox = screen.getByRole("log");
    expect(logBox).toHaveAttribute("aria-live", "polite");
    expect(logBox).toHaveAttribute("aria-label", "Bot output log");
  });

  it("countdown has correct aria attributes", () => {
    render(
      <GoshthiForm
        {...defaultProps}
        loading={true}
        countdown={10}
        selectedMonth={new Date()}
        goshthiHeld="No"
      />
    );
    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-live", "polite");
  });
});
