import { render, screen, fireEvent } from "@testing-library/react";
import BalMandalBot from "./BalMandalBot";

jest.mock("../../utils/functions", () => ({
  runBalMandalBot: jest.fn(),
}));

jest.mock("../../utils/CONSTANTS", () => ({
  CONSTANTS: {
    BAL_MANDAL_BOT: "BKMS BM Attendance Bot",
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
    LONG: "long",
    NUMERIC: "numeric",
    REQUIRED_FIELDS: "Please fill out all required fields before running the bot.",
  },
}));

jest.mock("../BalMandalForm/BalMandalForm", () => (props) => (
  <div data-testid="bal-mandal-form">
    <button data-testid="run-trigger" onClick={props.runBot}>
      trigger run
    </button>
    <span data-testid="loading-value">{String(props.loading)}</span>
    <span data-testid="countdown-value">{String(props.countdown)}</span>
    <span data-testid="logs-count">{props.logs.length}</span>
    <button
      data-testid="set-day"
      onClick={() => props.setDay("Saturday")}
    >
      set day
    </button>
    <button
      data-testid="set-date"
      onClick={() => props.setDate(new Date("2024-06-15"))}
    >
      set date
    </button>
    <button
      data-testid="set-sabha-held"
      onClick={() => props.setSabhaHeld("Yes")}
    >
      set sabhaHeld
    </button>
    <button
      data-testid="set-combined-groups"
      onClick={() => props.setCombinedGroups("No")}
    >
      set combinedGroups
    </button>
    <button
      data-testid="set-smruti-time"
      onClick={() => props.setSmrutiTime("Yes")}
    >
      set smrutiTime
    </button>
    <button
      data-testid="set-mukhpath"
      onClick={() => props.setMukhpath("Yes")}
    >
      set mukhpath
    </button>
    <button
      data-testid="set-prep-cycle-done"
      onClick={() => props.setPrepCycleDone("Yes")}
    >
      set prepCycleDone
    </button>
    <button
      data-testid="set-individual-groups"
      onClick={() => props.setIndividualGroups({ "group 0": { held: "Yes" } })}
    >
      set individualGroups
    </button>
    <button
      data-testid="set-captcha-seconds"
      onClick={() => props.setCaptchaSeconds("30")}
    >
      set captchaSeconds
    </button>
  </div>
));

jest.mock("./BalMandalBot.module.css", () => ({
  container: "container",
  title: "title",
}));

import { runBalMandalBot } from "../../utils/functions";

describe("BalMandalBot", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the title", () => {
    render(<BalMandalBot />);
    expect(screen.getByText("BKMS BM Attendance Bot")).toBeInTheDocument();
  });

  it("renders the BalMandalForm", () => {
    render(<BalMandalBot />);
    expect(screen.getByTestId("bal-mandal-form")).toBeInTheDocument();
  });

  it("initial loading state is false", () => {
    render(<BalMandalBot />);
    expect(screen.getByTestId("loading-value").textContent).toBe("false");
  });

  it("initial countdown is null", () => {
    render(<BalMandalBot />);
    expect(screen.getByTestId("countdown-value").textContent).toBe("null");
  });

  it("initial logs count is 0", () => {
    render(<BalMandalBot />);
    expect(screen.getByTestId("logs-count").textContent).toBe("0");
  });

  it("calls runBalMandalBot when runBot is triggered", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot).toHaveBeenCalledTimes(1);
  });

  it("passes correct initial state props to BalMandalForm", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("run-trigger"));
    const call = runBalMandalBot.mock.calls[0][0];
    expect(call).toMatchObject({
      day: "",
      sabhaHeld: "",
      combinedGroups: "",
      smrutiTime: "No",
      mukhpath: "No",
      prepCycleDone: "No",
      captchaSeconds: "20",
    });
  });

  it("setDay updates day state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-day"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].day).toBe("Saturday");
  });

  it("setDate updates date state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-date"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].date).not.toBeNull();
  });

  it("setSabhaHeld updates sabhaHeld state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-sabha-held"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].sabhaHeld).toBe("Yes");
  });

  it("setCombinedGroups updates combinedGroups state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-combined-groups"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].combinedGroups).toBe("No");
  });

  it("setSmrutiTime updates smrutiTime state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-smruti-time"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].smrutiTime).toBe("Yes");
  });

  it("setMukhpath updates mukhpath state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-mukhpath"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].mukhpath).toBe("Yes");
  });

  it("setPrepCycleDone updates prepCycleDone state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-prep-cycle-done"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].prepCycleDone).toBe("Yes");
  });

  it("setIndividualGroups updates individualGroups state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-individual-groups"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].individualGroups).toEqual({
      "group 0": { held: "Yes" },
    });
  });

  it("setCaptchaSeconds updates captchaSeconds state passed to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("set-captcha-seconds"));
    fireEvent.click(screen.getByTestId("run-trigger"));
    expect(runBalMandalBot.mock.calls[0][0].captchaSeconds).toBe("30");
  });

  it("passes setLogs, setCountdown, setLoading to runBot", () => {
    render(<BalMandalBot />);
    fireEvent.click(screen.getByTestId("run-trigger"));
    const call = runBalMandalBot.mock.calls[0][0];
    expect(typeof call.setLogs).toBe("function");
    expect(typeof call.setCountdown).toBe("function");
    expect(typeof call.setLoading).toBe("function");
  });
});
