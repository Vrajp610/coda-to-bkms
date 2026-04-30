import { render, screen, fireEvent } from "@testing-library/react";
import BalMandalForm from "./BalMandalForm";

jest.mock("./BalMandalForm.module.css", () => ({
  form: "form",
  sectionLabel: "sectionLabel",
  dateGrid: "dateGrid",
  dateTile: "dateTile",
  dateTileActive: "dateTileActive",
  dateLabel: "dateLabel",
  dateValue: "dateValue",
  customDateWrapper: "customDateWrapper",
  numberInput: "numberInput",
  inputError: "inputError",
  inputErrorMsg: "inputErrorMsg",
  inputHint: "inputHint",
  toggle: "toggle",
  toggleBtn: "toggleBtn",
  toggleBtnActive: "toggleBtnActive",
  activitiesGrid: "activitiesGrid",
  activityItem: "activityItem",
  activityLabel: "activityLabel",
  compactGroupTable: "compactGroupTable",
  groupTableGrid: "groupTableGrid",
  groupTableHeader: "groupTableHeader",
  groupTableRow: "groupTableRow",
  groupTableLabel: "groupTableLabel",
  miniToggle: "miniToggle",
  miniToggleDisabled: "miniToggleDisabled",
  miniBtn: "miniBtn",
  miniBtnActive: "miniBtnActive",
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
    SATURDAY_BAL_GROUP_0: "Saturday Bal Group 0",
    SATURDAY_BAL_GROUP_1: "Saturday Bal Group 1",
    SATURDAY_BAL_GROUP_2A: "Saturday Bal Group 2A",
    SATURDAY_BAL_GROUP_2B: "Saturday Bal Group 2B",
    SATURDAY_BAL_GROUP_3: "Saturday Bal Group 3",
    SUNDAY_BAL_GROUP_0: "Sunday Bal Group 0",
    SUNDAY_BAL_GROUP_1: "Sunday Bal Group 1",
    SUNDAY_BAL_GROUP_2A: "Sunday Bal Group 2A",
    SUNDAY_BAL_GROUP_2B: "Sunday Bal Group 2B",
    SUNDAY_BAL_GROUP_3: "Sunday Bal Group 3",
  },
}));

jest.mock("../Button/Button", () => (props) => (
  <button onClick={props.onClick} disabled={props.disabled} data-testid="run-btn">
    {props.children}
  </button>
));

const defaultProps = {
  date: null,
  setDate: jest.fn(),
  day: "",
  setDay: jest.fn(),
  sabhaHeld: "",
  setSabhaHeld: jest.fn(),
  combinedGroups: "",
  setCombinedGroups: jest.fn(),
  smrutiTime: "No",
  setSmrutiTime: jest.fn(),
  mukhpath: "No",
  setMukhpath: jest.fn(),
  prepCycleDone: "No",
  setPrepCycleDone: jest.fn(),
  individualGroups: {},
  setIndividualGroups: jest.fn(),
  captchaSeconds: "20",
  setCaptchaSeconds: jest.fn(),
  loading: false,
  runBot: jest.fn(),
  logs: [],
  countdown: null,
};

describe("BalMandalForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  it("renders 4 date tiles", () => {
    render(<BalMandalForm {...defaultProps} />);
    expect(screen.getByText("2 Weeks Ago")).toBeInTheDocument();
    expect(screen.getByText("Last Week")).toBeInTheDocument();
    expect(screen.getByText("This Sunday")).toBeInTheDocument();
    expect(screen.getByText("Next Sunday")).toBeInTheDocument();
  });

  it("calls setDate and clears custom input when a date tile is clicked", () => {
    const setDate = jest.fn();
    render(<BalMandalForm {...defaultProps} setDate={setDate} />);
    fireEvent.click(screen.getByText("This Sunday").closest("button"));
    expect(setDate).toHaveBeenCalledWith(expect.any(Date));
  });

  it("applies dateTileActive to the selected date tile", () => {
    const today = new Date();
    const sunday = new Date(today);
    sunday.setDate(today.getDate() - today.getDay());
    render(<BalMandalForm {...defaultProps} date={sunday} />);
    const btn = screen.getByText("This Sunday").closest("button");
    expect(btn.className).toContain("dateTileActive");
  });

  it("does not apply dateTileActive when date is null", () => {
    render(<BalMandalForm {...defaultProps} date={null} />);
    const btn = screen.getByText("This Sunday").closest("button");
    expect(btn.className).not.toContain("dateTileActive");
  });

  it("renders Saturday and Sunday day toggle buttons", () => {
    render(<BalMandalForm {...defaultProps} />);
    expect(screen.getByText("Saturday")).toBeInTheDocument();
    expect(screen.getByText("Sunday")).toBeInTheDocument();
  });

  it("calls setDay when a day button is clicked", () => {
    const setDay = jest.fn();
    render(<BalMandalForm {...defaultProps} setDay={setDay} />);
    fireEvent.click(screen.getByText("Saturday"));
    expect(setDay).toHaveBeenCalledWith("Saturday");
  });

  it("applies toggleBtnActive to the selected day", () => {
    render(<BalMandalForm {...defaultProps} day="Sunday" />);
    expect(screen.getByText("Sunday").className).toContain("toggleBtnActive");
  });

  it("renders Was Sabha Held section", () => {
    render(<BalMandalForm {...defaultProps} />);
    expect(screen.getByText("Was Sabha Held?")).toBeInTheDocument();
  });

  it("calls setSabhaHeld when Yes is clicked", () => {
    const setSabhaHeld = jest.fn();
    render(<BalMandalForm {...defaultProps} setSabhaHeld={setSabhaHeld} />);
    fireEvent.click(screen.getAllByText("Yes")[0]);
    expect(setSabhaHeld).toHaveBeenCalledWith("Yes");
  });

  it("applies toggleBtnActive to active sabhaHeld option", () => {
    render(<BalMandalForm {...defaultProps} sabhaHeld="Yes" />);
    expect(screen.getAllByText("Yes")[0].className).toContain("toggleBtnActive");
  });

  it("does not show Combined Groups when sabhaHeld is not Yes", () => {
    render(<BalMandalForm {...defaultProps} sabhaHeld="" />);
    expect(screen.queryByText("Combined Groups Reporting?")).not.toBeInTheDocument();
  });

  it("shows Combined Groups when sabhaHeld is Yes", () => {
    render(<BalMandalForm {...defaultProps} sabhaHeld="Yes" />);
    expect(screen.getByText("Combined Groups Reporting?")).toBeInTheDocument();
  });

  it("calls setCombinedGroups when Yes is clicked under Combined Groups", () => {
    const setCombinedGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        setCombinedGroups={setCombinedGroups}
      />
    );
    fireEvent.click(screen.getAllByText("Yes")[1]);
    expect(setCombinedGroups).toHaveBeenCalledWith("Yes");
  });

  it("shows Activities section when sabhaHeld=Yes and combinedGroups=Yes", () => {
    render(
      <BalMandalForm {...defaultProps} sabhaHeld="Yes" combinedGroups="Yes" />
    );
    expect(screen.getByText("Activities")).toBeInTheDocument();
    expect(screen.getByText("Smruti Time")).toBeInTheDocument();
    expect(screen.getByText("Mukhpath")).toBeInTheDocument();
    expect(screen.getByText("Prep Cycle")).toBeInTheDocument();
  });

  it("calls setSmrutiTime when Smruti Time Yes is clicked", () => {
    const setSmrutiTime = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="Yes"
        setSmrutiTime={setSmrutiTime}
      />
    );
    fireEvent.click(screen.getAllByText("Yes")[2]);
    expect(setSmrutiTime).toHaveBeenCalledWith("Yes");
  });

  it("calls setMukhpath when Mukhpath Yes is clicked", () => {
    const setMukhpath = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="Yes"
        setMukhpath={setMukhpath}
      />
    );
    fireEvent.click(screen.getAllByText("No")[3]);
    expect(setMukhpath).toHaveBeenCalledWith("No");
  });

  it("calls setPrepCycleDone when Prep Cycle No is clicked", () => {
    const setPrepCycleDone = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="Yes"
        setPrepCycleDone={setPrepCycleDone}
      />
    );
    fireEvent.click(screen.getAllByText("No")[4]);
    expect(setPrepCycleDone).toHaveBeenCalledWith("No");
  });

  it("shows IndividualGroupsForm when sabhaHeld=Yes and combinedGroups=No", () => {
    render(
      <BalMandalForm {...defaultProps} sabhaHeld="Yes" combinedGroups="No" />
    );
    expect(screen.getByText("Individual Group Reporting")).toBeInTheDocument();
  });

  it("renders all 5 group rows in IndividualGroupsForm", () => {
    render(
      <BalMandalForm {...defaultProps} sabhaHeld="Yes" combinedGroups="No" />
    );
    expect(screen.getByText("0")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2A")).toBeInTheDocument();
    expect(screen.getByText("2B")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("clicking Y in individual group calls setIndividualGroups with held=Yes", () => {
    const setIndividualGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        setIndividualGroups={setIndividualGroups}
      />
    );
    const yButtons = screen.getAllByText("Y");
    fireEvent.click(yButtons[0]);
    expect(setIndividualGroups).toHaveBeenCalled();
    const updater = setIndividualGroups.mock.calls[0][0];
    const result = updater({});
    expect(result["group 0"].held).toBe("Yes");
  });

  it("clicking N in individual group calls setIndividualGroups with held=No", () => {
    const setIndividualGroups = jest.fn();
    const individualGroups = { "group 0": { held: "Yes" } };
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={individualGroups}
        setIndividualGroups={setIndividualGroups}
      />
    );
    const nButtons = screen.getAllByText("N");
    fireEvent.click(nButtons[0]);
    expect(setIndividualGroups).toHaveBeenCalled();
    const updater = setIndividualGroups.mock.calls[0][0];
    const result = updater(individualGroups);
    expect(result["group 0"].held).toBe("No");
  });

  it("smruti_time MiniYesNo is disabled when group not held", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "No" } }}
      />
    );
    const yButtons = screen.getAllByText("Y");
    expect(yButtons[1]).toBeDisabled();
  });

  it("smruti_time MiniYesNo is enabled when group is held", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes" } }}
      />
    );
    const yButtons = screen.getAllByText("Y");
    expect(yButtons[1]).not.toBeDisabled();
  });

  it("clicking disabled MiniYesNo does not call setIndividualGroups", () => {
    const setIndividualGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "No" } }}
        setIndividualGroups={setIndividualGroups}
      />
    );
    const yButtons = screen.getAllByText("Y");
    fireEvent.click(yButtons[1]);
    expect(setIndividualGroups).not.toHaveBeenCalled();
  });

  it("miniBtnActive applied to active MiniYesNo value", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes", smruti_time: "Yes" } }}
      />
    );
    const yButtons = screen.getAllByText("Y");
    expect(yButtons[1].className).toContain("miniBtnActive");
  });

  it("shows CAPTCHA input when sabhaHeld is Yes", () => {
    render(<BalMandalForm {...defaultProps} sabhaHeld="Yes" />);
    expect(screen.getByText("CAPTCHA Time (seconds)")).toBeInTheDocument();
  });

  it("calls setCaptchaSeconds on captcha input change", () => {
    const setCaptchaSeconds = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        setCaptchaSeconds={setCaptchaSeconds}
      />
    );
    fireEvent.change(screen.getByRole("spinbutton"), {
      target: { value: "60" },
    });
    expect(setCaptchaSeconds).toHaveBeenCalledWith("60");
  });

  it("captcha input is disabled when loading", () => {
    render(
      <BalMandalForm {...defaultProps} sabhaHeld="Yes" loading={true} />
    );
    expect(screen.getByRole("spinbutton")).toBeDisabled();
  });

  it("Run Bot is disabled when no date, day, or sabhaHeld", () => {
    render(<BalMandalForm {...defaultProps} />);
    expect(screen.getByTestId("run-btn")).toBeDisabled();
  });

  it("Run Bot is enabled when date, day, sabhaHeld are set", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
      />
    );
    expect(screen.getByTestId("run-btn")).not.toBeDisabled();
  });

  it("Run Bot shows Running... when loading", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
        loading={true}
      />
    );
    expect(screen.getByText("Running...")).toBeInTheDocument();
  });

  it("calls runBot when the button is clicked", () => {
    const runBot = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
        runBot={runBot}
      />
    );
    fireEvent.click(screen.getByTestId("run-btn"));
    expect(runBot).toHaveBeenCalled();
  });

  it("shows countdown when loading and countdown is set", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
        loading={true}
        countdown={15}
      />
    );
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByText(/15s remaining/)).toBeInTheDocument();
  });

  it("does not show countdown when not loading", () => {
    render(<BalMandalForm {...defaultProps} countdown={15} loading={false} />);
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows log box when logs are present", () => {
    render(<BalMandalForm {...defaultProps} logs={["hello"]} />);
    expect(screen.getByRole("log")).toBeInTheDocument();
    expect(screen.getByText("hello")).toBeInTheDocument();
  });

  it("shows log box when loading even with no logs", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
        loading={true}
        logs={[]}
      />
    );
    expect(screen.getByRole("log")).toBeInTheDocument();
  });

  it("shows '...' when loading and countdown is null", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
        loading={true}
        logs={[]}
        countdown={null}
      />
    );
    expect(screen.getByText("...")).toBeInTheDocument();
  });

  it("does not show '...' when countdown is set", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        date={new Date()}
        day="Saturday"
        sabhaHeld="Yes"
        loading={true}
        logs={[]}
        countdown={10}
      />
    );
    expect(screen.queryByText("...")).not.toBeInTheDocument();
  });

  it("applies logError class to lines containing ERROR", () => {
    render(<BalMandalForm {...defaultProps} logs={["ERROR: bad"]} />);
    expect(screen.getByText("ERROR: bad").className).toContain("logError");
  });

  it("applies logHeader class to lines starting with ---", () => {
    render(<BalMandalForm {...defaultProps} logs={["--- Section ---"]} />);
    expect(screen.getByText("--- Section ---").className).toContain("logHeader");
  });

  it("applies logLine class to regular log lines", () => {
    render(<BalMandalForm {...defaultProps} logs={["normal line"]} />);
    expect(screen.getByText("normal line").className).toContain("logLine");
  });

  it("does not show log box when logs empty and not loading", () => {
    render(<BalMandalForm {...defaultProps} logs={[]} loading={false} />);
    expect(screen.queryByRole("log")).not.toBeInTheDocument();
  });

  it("log box has correct aria attributes", () => {
    render(<BalMandalForm {...defaultProps} logs={["hello"]} />);
    const log = screen.getByRole("log");
    expect(log).toHaveAttribute("aria-live", "polite");
    expect(log).toHaveAttribute("aria-label", "Bot output log");
  });

  it("custom date input sets date on valid YYYY-MM-DD blur", () => {
    const setDate = jest.fn();
    render(<BalMandalForm {...defaultProps} setDate={setDate} />);
    const input = screen.getByPlaceholderText(/past date/i);
    fireEvent.change(input, { target: { value: "2026-03-09" } });
    fireEvent.blur(input);
    expect(setDate).toHaveBeenCalledWith(expect.any(Date));
  });

  it("custom date input shows error on invalid format", () => {
    render(<BalMandalForm {...defaultProps} />);
    const input = screen.getByPlaceholderText(/past date/i);
    fireEvent.change(input, { target: { value: "not-a-date" } });
    fireEvent.blur(input);
    expect(screen.getByText(/YYYY-MM-DD/)).toBeInTheDocument();
  });

  it("custom date input shows error on invalid date", () => {
    render(<BalMandalForm {...defaultProps} />);
    const input = screen.getByPlaceholderText(/past date/i);
    fireEvent.change(input, { target: { value: "2026-99-99" } });
    fireEvent.blur(input);
    expect(screen.getByText("Invalid date")).toBeInTheDocument();
  });

  it("custom date input blur with empty value does nothing", () => {
    const setDate = jest.fn();
    render(<BalMandalForm {...defaultProps} setDate={setDate} />);
    const input = screen.getByPlaceholderText(/past date/i);
    fireEvent.blur(input);
    expect(setDate).not.toHaveBeenCalled();
  });

  it("custom date input shows hint when date is set and no error", () => {
    render(
      <BalMandalForm {...defaultProps} date={new Date("2026-03-09T00:00:00")} />
    );
    const input = screen.getByPlaceholderText(/past date/i);
    fireEvent.change(input, { target: { value: "2026-03-09" } });
    expect(screen.getByText(/Selected:/)).toBeInTheDocument();
  });

  it("custom date input is disabled when loading", () => {
    render(<BalMandalForm {...defaultProps} loading={true} />);
    expect(screen.getByPlaceholderText(/past date/i)).toBeDisabled();
  });

  it("clears error when input changes after error", () => {
    render(<BalMandalForm {...defaultProps} />);
    const input = screen.getByPlaceholderText(/past date/i);
    fireEvent.change(input, { target: { value: "bad" } });
    fireEvent.blur(input);
    expect(screen.getByText(/YYYY-MM-DD/)).toBeInTheDocument();
    fireEvent.change(input, { target: { value: "2026-03-09" } });
    expect(screen.queryByText(/YYYY-MM-DD/)).not.toBeInTheDocument();
  });

  it("clicking Y for mukhpath calls setIndividualGroups with mukhpath=Yes", () => {
    const setIndividualGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes", mukhpath: "No" } }}
        setIndividualGroups={setIndividualGroups}
      />
    );
    const yButtons = screen.getAllByText("Y");
    fireEvent.click(yButtons[2]);
    expect(setIndividualGroups).toHaveBeenCalled();
    const updater = setIndividualGroups.mock.calls[0][0];
    const result = updater({ "group 0": { held: "Yes" } });
    expect(result["group 0"].mukhpath).toBe("Yes");
  });

  it("clicking N for prep_cycle calls setIndividualGroups with prep_cycle=No", () => {
    const setIndividualGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes", prep_cycle: "Yes" } }}
        setIndividualGroups={setIndividualGroups}
      />
    );
    const nButtons = screen.getAllByText("N");
    fireEvent.click(nButtons[3]);
    expect(setIndividualGroups).toHaveBeenCalled();
    const updater = setIndividualGroups.mock.calls[0][0];
    const result = updater({ "group 0": { held: "Yes" } });
    expect(result["group 0"].prep_cycle).toBe("No");
  });

  it("mukhpath MiniYesNo is disabled when group not held", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "No" } }}
      />
    );
    const yButtons = screen.getAllByText("Y");
    expect(yButtons[2]).toBeDisabled();
  });

  it("mukhpath MiniYesNo is enabled when group is held", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes" } }}
      />
    );
    const yButtons = screen.getAllByText("Y");
    expect(yButtons[2]).not.toBeDisabled();
  });

  it("prep_cycle MiniYesNo is disabled when group not held", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "No" } }}
      />
    );
    const nButtons = screen.getAllByText("N");
    expect(nButtons[3]).toBeDisabled();
  });

  it("prep_cycle MiniYesNo is enabled when group is held", () => {
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes" } }}
      />
    );
    const yButtons = screen.getAllByText("Y");
    expect(yButtons[3]).not.toBeDisabled();
  });

  it("clicking disabled mukhpath Y does not change value", () => {
    const setIndividualGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "No" } }}
        setIndividualGroups={setIndividualGroups}
      />
    );
    const yButtons = screen.getAllByText("Y");
    fireEvent.click(yButtons[2]);
    expect(setIndividualGroups).not.toHaveBeenCalled();
  });

  it("clicking Y for smruti_time calls setIndividualGroups with smruti_time=Yes", () => {
    const setIndividualGroups = jest.fn();
    render(
      <BalMandalForm
        {...defaultProps}
        sabhaHeld="Yes"
        combinedGroups="No"
        individualGroups={{ "group 0": { held: "Yes", smruti_time: "No" } }}
        setIndividualGroups={setIndividualGroups}
      />
    );
    const yButtons = screen.getAllByText("Y");
    fireEvent.click(yButtons[1]);
    expect(setIndividualGroups).toHaveBeenCalled();
    const updater = setIndividualGroups.mock.calls[0][0];
    const result = updater({ "group 0": { held: "Yes" } });
    expect(result["group 0"].smruti_time).toBe("Yes");
  });
});
