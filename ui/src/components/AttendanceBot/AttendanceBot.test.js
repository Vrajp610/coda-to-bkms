import { render, screen, fireEvent } from "@testing-library/react";
import AttendanceBot from "./AttendanceBot";
import * as CONSTANTS_MODULE from "../../utils/CONSTANTS";
import * as functions from "../../utils/functions";

jest.mock("./AttendanceBot.module.css", () => ({
    container: "container",
    title: "title",
}));

jest.mock("../AttendanceForm/AttendanceForm", () => (props) => (
    <div data-testid="attendance-form">
        <button onClick={props.runBot} data-testid="run-bot-btn">Run Bot</button>
        <span data-testid="date">{String(props.date)}</span>
        <span data-testid="group">{props.group}</span>
        <span data-testid="sabhaHeld">{props.sabhaHeld}</span>
        <span data-testid="p2Guju">{props.p2Guju}</span>
        <span data-testid="prepCycleDone">{props.prepCycleDone}</span>
        <span data-testid="status">{props.status}</span>
        <span data-testid="loading">{String(props.loading)}</span>
        <span data-testid="markedPresent">{String(props.markedPresent)}</span>
        <span data-testid="notMarked">{String(props.notMarked)}</span>
        <span data-testid="notFoundInBkms">{String(props.notFoundInBkms)}</span>
    </div>
));

beforeAll(() => {
    CONSTANTS_MODULE.CONSTANTS = { ATTENDANCE_BOT: "Attendance Bot" };
});

describe("AttendanceBot", () => {
    it("renders AttendanceBot title", () => {
        render(<AttendanceBot />);
        expect(screen.getByText("Attendance Bot")).toBeInTheDocument();
    });

    it("renders AttendanceForm with initial props", () => {
        render(<AttendanceBot />);
        expect(screen.getByTestId("attendance-form")).toBeInTheDocument();
        expect(screen.getByTestId("date").textContent).toBe("null");
        expect(screen.getByTestId("group").textContent).toBe("");
        expect(screen.getByTestId("sabhaHeld").textContent).toBe("");
        expect(screen.getByTestId("p2Guju").textContent).toBe("");
        expect(screen.getByTestId("prepCycleDone").textContent).toBe("");
        expect(screen.getByTestId("status").textContent).toBe("");
        expect(screen.getByTestId("loading").textContent).toBe("false");
        expect(screen.getByTestId("markedPresent").textContent).toBe("null");
        expect(screen.getByTestId("notMarked").textContent).toBe("null");
        expect(screen.getByTestId("notFoundInBkms").textContent).toBe("null");
    });

    it("calls runAttendanceBot with correct arguments when runBot is triggered", () => {
        const runAttendanceBotMock = jest.spyOn(functions, "runAttendanceBot").mockImplementation(jest.fn());
        render(<AttendanceBot />);
        fireEvent.click(screen.getByTestId("run-bot-btn"));
        expect(runAttendanceBotMock).toHaveBeenCalledWith(
            expect.objectContaining({
                date: null,
                group: "",
                sabhaHeld: "",
                p2Guju: "",
                prepCycleDone: "",
                setStatus: expect.any(Function),
                setMarkedPresent: expect.any(Function),
                setNotMarked: expect.any(Function),
                setNotFoundInBkms: expect.any(Function),
                setLoading: expect.any(Function),
            })
        );
        runAttendanceBotMock.mockRestore();
    });
});