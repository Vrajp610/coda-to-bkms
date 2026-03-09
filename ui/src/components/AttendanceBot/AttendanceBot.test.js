import { render, screen } from "@testing-library/react";
import { act } from "react";
import AttendanceBot from "./AttendanceBot";
import * as functions from "../../utils/functions";

jest.mock("./AttendanceBot.module.css", () => ({
  container: "container",
  title: "title",
}));

let lastAttendanceFormProps = {};
jest.mock("../AttendanceForm/AttendanceForm", () => (props) => {
  lastAttendanceFormProps = props;
  return <div data-testid="attendance-form" />;
});

jest.mock("../../utils/CONSTANTS", () => ({
  CONSTANTS: {
    ATTENDANCE_BOT: "BKMS Attendance Bot",
    YES: "Yes",
    REQUIRED_FIELDS: "Please fill out all required fields before running the bot.",
    SOMETHING_WENT_WRONG: "Something went wrong!",
    LONG: "long",
    NUMERIC: "numeric",
  },
}));

beforeAll(() => {
  jest.spyOn(window, "alert").mockImplementation(() => {});
});

describe("AttendanceBot", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    lastAttendanceFormProps = {};
  });

  it("renders the title and AttendanceForm", () => {
    render(<AttendanceBot />);
    expect(screen.getByText("BKMS Attendance Bot")).toBeInTheDocument();
    expect(screen.getByTestId("attendance-form")).toBeInTheDocument();
  });

  it("passes required props to AttendanceForm", () => {
    render(<AttendanceBot />);
    [
      "date", "setDate",
      "group", "setGroup",
      "sabhaHeld", "setSabhaHeld",
      "p2Guju", "setP2Guju",
      "prepCycleDone", "setPrepCycleDone",
      "loading", "runBot",
      "logs", "countdown",
    ].forEach((prop) => {
      expect(lastAttendanceFormProps).toHaveProperty(prop);
    });
  });

  it("handles state changes for all fields", async () => {
    render(<AttendanceBot />);
    await act(async () => {
      lastAttendanceFormProps.setDate("2024-06-09");
      lastAttendanceFormProps.setGroup("Saturday K1");
      lastAttendanceFormProps.setSabhaHeld("Yes");
      lastAttendanceFormProps.setP2Guju("Yes");
      lastAttendanceFormProps.setPrepCycleDone("Yes");
    });
    expect(lastAttendanceFormProps.date).toBe("2024-06-09");
    expect(lastAttendanceFormProps.group).toBe("Saturday K1");
    expect(lastAttendanceFormProps.sabhaHeld).toBe("Yes");
    expect(lastAttendanceFormProps.p2Guju).toBe("Yes");
    expect(lastAttendanceFormProps.prepCycleDone).toBe("Yes");
  });

  it("calls runAttendanceBot when runBot prop is invoked", async () => {
    const spy = jest.spyOn(functions, "runAttendanceBot").mockResolvedValue();
    render(<AttendanceBot />);
    await act(async () => {
      lastAttendanceFormProps.runBot();
    });
    expect(spy).toHaveBeenCalled();
  });
});
