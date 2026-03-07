import { render, screen, fireEvent } from "@testing-library/react";
import AttendanceForm from "./AttendanceForm";

jest.mock("./AttendanceForm.module.css", () => ({
  form: "form",
  sectionLabel: "sectionLabel",
  dateGrid: "dateGrid",
  dateTile: "dateTile",
  dateTileActive: "dateTileActive",
  dateLabel: "dateLabel",
  dateValue: "dateValue",
  groupGrid: "groupGrid",
  groupTile: "groupTile",
  groupTileActive: "groupTileActive",
  groupDay: "groupDay",
  groupSub: "groupSub",
  toggle: "toggle",
  toggleBtn: "toggleBtn",
  toggleBtnActive: "toggleBtnActive",
}));

jest.mock("../../utils/CONSTANTS", () => ({
  CONSTANTS: {
    SATURDAY_K1: "Saturday K1",
    SATURDAY_K2: "Saturday K2",
    SUNDAY_K1: "Sunday K1",
    SUNDAY_K2: "Sunday K2",
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

jest.mock("../AttendanceAlerts/AttendanceAlerts", () => () => (
  <div data-testid="attendance-alerts" />
));

const defaultProps = {
  date: null,
  setDate: jest.fn(),
  group: "",
  setGroup: jest.fn(),
  sabhaHeld: "",
  setSabhaHeld: jest.fn(),
  p2Guju: "",
  setP2Guju: jest.fn(),
  prepCycleDone: "",
  setPrepCycleDone: jest.fn(),
  status: "",
  loading: false,
  runBot: jest.fn(),
  markedPresent: null,
  notMarked: null,
  notFoundInBkms: null,
  sabhaHeldResult: null,
};

describe("AttendanceForm", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders 4 date tiles", () => {
    render(<AttendanceForm {...defaultProps} />);
    expect(screen.getByText("2 Weeks Ago")).toBeInTheDocument();
    expect(screen.getByText("Last Week")).toBeInTheDocument();
    expect(screen.getByText("This Sunday")).toBeInTheDocument();
    expect(screen.getByText("Next Sunday")).toBeInTheDocument();
  });

  it("calls setDate when a date tile is clicked", () => {
    const setDate = jest.fn();
    render(<AttendanceForm {...defaultProps} setDate={setDate} />);
    fireEvent.click(screen.getByText("This Sunday").closest("button"));
    expect(setDate).toHaveBeenCalledWith(expect.any(Date));
  });

  it("applies dateTileActive class to the matching date tile", () => {
    const today = new Date();
    const currentSunday = new Date(today);
    currentSunday.setDate(today.getDate() - today.getDay());
    render(<AttendanceForm {...defaultProps} date={currentSunday} />);
    const btn = screen.getByText("This Sunday").closest("button");
    expect(btn.className).toContain("dateTileActive");
  });

  it("does not apply dateTileActive when date is null", () => {
    render(<AttendanceForm {...defaultProps} date={null} />);
    const btn = screen.getByText("This Sunday").closest("button");
    expect(btn.className).not.toContain("dateTileActive");
  });

  it("renders 4 group tiles", () => {
    render(<AttendanceForm {...defaultProps} />);
    expect(screen.getAllByText("Saturday")).toHaveLength(2);
    expect(screen.getAllByText("Sunday")).toHaveLength(2);
    expect(screen.getAllByText("K1")).toHaveLength(2);
    expect(screen.getAllByText("K2")).toHaveLength(2);
  });

  it("calls setGroup when a group tile is clicked", () => {
    const setGroup = jest.fn();
    render(<AttendanceForm {...defaultProps} setGroup={setGroup} />);
    fireEvent.click(screen.getAllByText("K1")[0].closest("button"));
    expect(setGroup).toHaveBeenCalledWith("Saturday K1");
  });

  it("applies groupTileActive class to the selected group tile", () => {
    render(<AttendanceForm {...defaultProps} group="Saturday K1" />);
    const btn = screen.getAllByText("K1")[0].closest("button");
    expect(btn.className).toContain("groupTileActive");
  });

  it("does not apply groupTileActive to unselected group tile", () => {
    render(<AttendanceForm {...defaultProps} group="" />);
    const btn = screen.getAllByText("K1")[0].closest("button");
    expect(btn.className).not.toContain("groupTileActive");
  });

  it("renders Yes/No toggle buttons", () => {
    render(<AttendanceForm {...defaultProps} />);
    expect(screen.getAllByText("Yes").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("No").length).toBeGreaterThanOrEqual(1);
  });

  it("calls setSabhaHeld when a toggle is clicked", () => {
    const setSabhaHeld = jest.fn();
    render(<AttendanceForm {...defaultProps} setSabhaHeld={setSabhaHeld} />);
    fireEvent.click(screen.getAllByText("Yes")[0]);
    expect(setSabhaHeld).toHaveBeenCalledWith("Yes");
  });

  it("applies toggleBtnActive to the selected toggle option", () => {
    render(<AttendanceForm {...defaultProps} sabhaHeld="Yes" />);
    expect(screen.getAllByText("Yes")[0].className).toContain("toggleBtnActive");
  });

  it("does not apply toggleBtnActive to the unselected toggle option", () => {
    render(<AttendanceForm {...defaultProps} sabhaHeld="Yes" />);
    expect(screen.getAllByText("No")[0].className).not.toContain("toggleBtnActive");
  });

  it("shows extra fields when sabhaHeld is Yes", () => {
    render(<AttendanceForm {...defaultProps} sabhaHeld="Yes" />);
    expect(screen.getByText("Was P2 in Guju?")).toBeInTheDocument();
    expect(screen.getByText("2 Week Prep Cycle Done?")).toBeInTheDocument();
  });

  it("hides extra fields when sabhaHeld is not Yes", () => {
    render(<AttendanceForm {...defaultProps} sabhaHeld="" />);
    expect(screen.queryByText("Was P2 in Guju?")).not.toBeInTheDocument();
  });

  it("calls setP2Guju when its toggle is clicked", () => {
    const setP2Guju = jest.fn();
    render(<AttendanceForm {...defaultProps} sabhaHeld="Yes" setP2Guju={setP2Guju} />);
    fireEvent.click(screen.getAllByText("No")[1]);
    expect(setP2Guju).toHaveBeenCalledWith("No");
  });

  it("calls setPrepCycleDone when its toggle is clicked", () => {
    const setPrepCycleDone = jest.fn();
    render(<AttendanceForm {...defaultProps} sabhaHeld="Yes" setPrepCycleDone={setPrepCycleDone} />);
    fireEvent.click(screen.getAllByText("Yes")[2]);
    expect(setPrepCycleDone).toHaveBeenCalledWith("Yes");
  });

  it("disables Run Bot when no fields filled", () => {
    render(<AttendanceForm {...defaultProps} />);
    expect(screen.getByText("Run Bot")).toBeDisabled();
  });

  it("enables Run Bot when date, group, sabhaHeld=No are filled", () => {
    render(
      <AttendanceForm
        {...defaultProps}
        date={new Date()}
        group="Saturday K1"
        sabhaHeld="No"
      />
    );
    expect(screen.getByText("Run Bot")).not.toBeDisabled();
  });

  it("disables Run Bot when sabhaHeld=Yes but extra fields missing", () => {
    render(
      <AttendanceForm
        {...defaultProps}
        date={new Date()}
        group="Saturday K1"
        sabhaHeld="Yes"
        p2Guju=""
        prepCycleDone=""
      />
    );
    expect(screen.getByText("Run Bot")).toBeDisabled();
  });

  it("enables Run Bot when all fields including sabhaHeld=Yes extras are filled", () => {
    render(
      <AttendanceForm
        {...defaultProps}
        date={new Date()}
        group="Saturday K1"
        sabhaHeld="Yes"
        p2Guju="Yes"
        prepCycleDone="Yes"
      />
    );
    expect(screen.getByText("Run Bot")).not.toBeDisabled();
  });

  it("shows Running... and disables button when loading", () => {
    render(
      <AttendanceForm
        {...defaultProps}
        date={new Date()}
        group="Saturday K1"
        sabhaHeld="No"
        loading={true}
      />
    );
    expect(screen.getByText("Running...")).toBeDisabled();
  });

  it("calls runBot when the button is clicked", () => {
    const runBot = jest.fn();
    render(
      <AttendanceForm
        {...defaultProps}
        date={new Date()}
        group="Saturday K1"
        sabhaHeld="No"
        runBot={runBot}
      />
    );
    fireEvent.click(screen.getByText("Run Bot"));
    expect(runBot).toHaveBeenCalled();
  });

  it("renders AttendanceAlerts", () => {
    render(<AttendanceForm {...defaultProps} />);
    expect(screen.getByTestId("attendance-alerts")).toBeInTheDocument();
  });
});
