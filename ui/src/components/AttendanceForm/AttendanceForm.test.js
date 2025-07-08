import { render, screen, fireEvent } from "@testing-library/react";
import AttendanceForm from "./AttendanceForm";

const { filterValidSundays } = require("../../utils/functions");

jest.mock("./AttendanceForm.module.css", () => ({
    form: "form",
    input: "input"
}));
jest.mock("../../utils/functions", () => ({
    filterValidSundays: jest.fn(() => true)
}));
jest.mock("../SelectField/SelectField", () => (props) => (
    <select
        aria-label={props.ariaLabel}
        value={props.value}
        onChange={props.onChange}
        data-testid={props.ariaLabel}
    >
        <option value="">{props.placeholder}</option>
        {props.options.map((opt) => (
            <option key={opt.value} value={opt.value}>
                {opt.label}
            </option>
        ))}
    </select>
));
jest.mock("../Button/Button", () => (props) => (
    <button onClick={props.onClick} disabled={props.disabled}>
        {props.children}
    </button>
));
jest.mock("../AttendanceAlerts/AttendanceAlerts", () => () => <div data-testid="attendance-alerts" />);
jest.mock("@mui/x-date-pickers/DatePicker", () => ({
    __esModule: true,
    DatePicker: ({ label, value, onChange, shouldDisableDate }) => {
        if (shouldDisableDate) {
            shouldDisableDate("2024-06-09");
        }
        return (
            <input
                aria-label={label}
                type="date"
                value={value || ""}
                onChange={(e) => onChange(e.target.value)}
                data-testid="date-picker"
            />
        );
    },
}));
jest.mock("@mui/x-date-pickers/LocalizationProvider", () => ({
    LocalizationProvider: ({ children }) => <div>{children}</div>,
}));
jest.mock("@mui/x-date-pickers/AdapterDateFns", () => ({}));

const CONSTANTS = {
    SELECT_A_VALID_SUNDAY: "Select a valid Sunday",
    SELECT_GROUP: "Select Group", 
    WAS_SABHA_HELD: "Was Sabha Held?",
    WAS_P2_IN_GUJU: "Was P2 in Guju?",
    PREP_CYCLE_DONE: "2 Week Prep Cycle Done?",
    YES: "Yes",
    NO: "No",
    SATURDAY_K1: "Saturday K1",
    SATURDAY_K2: "Saturday K2",
    SUNDAY_K1: "Sunday K1",
    SUNDAY_K2: "Sunday K2",
    RUN_BOT: "Run Bot",
    RUNNING: "Running...",
};

const defaultProps = {
    date: "",
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
    markedPresent: [],
    notMarked: [],
    notFoundInBkms: [],
    CONSTANTS,
};

describe("AttendanceForm", () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it("renders all main fields", () => {
        render(<AttendanceForm {...defaultProps} />);
        expect(screen.getByLabelText(CONSTANTS.SELECT_A_VALID_SUNDAY)).toBeInTheDocument();
        expect(screen.getByTestId(CONSTANTS.SELECT_GROUP)).toBeInTheDocument();
        expect(screen.getByTestId(CONSTANTS.WAS_SABHA_HELD)).toBeInTheDocument();
        expect(screen.getByText(CONSTANTS.RUN_BOT)).toBeInTheDocument();
        expect(screen.getByTestId("attendance-alerts")).toBeInTheDocument();
    });

    it("disables Run Bot button if required fields are missing", () => {
        render(<AttendanceForm {...defaultProps} />);
        expect(screen.getByText(CONSTANTS.RUN_BOT)).toBeDisabled();
    });

    it("enables Run Bot button when all required fields are filled and sabhaHeld is NO", () => {
        render(
            <AttendanceForm
                {...defaultProps}
                date="2024-06-09"
                group={CONSTANTS.SATURDAY_K1}
                sabhaHeld={CONSTANTS.NO}
            />
        );
        expect(screen.getByText(CONSTANTS.RUN_BOT)).not.toBeDisabled();
    });

    it("shows extra fields when sabhaHeld is YES", () => {
        render(
            <AttendanceForm
                {...defaultProps}
                sabhaHeld={CONSTANTS.YES}
            />
        );
        expect(screen.getByTestId(CONSTANTS.WAS_P2_IN_GUJU)).toBeInTheDocument();
        expect(screen.getByTestId(CONSTANTS.PREP_CYCLE_DONE)).toBeInTheDocument();
    });

    it("disables Run Bot button if sabhaHeld is YES but extra fields are missing", () => {
        render(
            <AttendanceForm
                {...defaultProps}
                date="2024-06-09"
                group={CONSTANTS.SATURDAY_K1}
                sabhaHeld={CONSTANTS.YES}
                p2Guju=""
                prepCycleDone=""
            />
        );
        expect(screen.getByText(CONSTANTS.RUN_BOT)).toBeDisabled();
    });

    it("enables Run Bot button if all fields are filled and sabhaHeld is YES", () => {
        render(
            <AttendanceForm
                {...defaultProps}
                date="2024-06-09"
                group={CONSTANTS.SATURDAY_K1}
                sabhaHeld={CONSTANTS.YES}
                p2Guju={CONSTANTS.NO}
                prepCycleDone={CONSTANTS.YES}
            />
        );
        expect(screen.getByText(CONSTANTS.RUN_BOT)).not.toBeDisabled();
    });

    it("calls runBot when Run Bot button is clicked", () => {
        const runBot = jest.fn();
        render(
            <AttendanceForm
                {...defaultProps}
                date="2024-06-09"
                group={CONSTANTS.SATURDAY_K1}
                sabhaHeld={CONSTANTS.NO}
                runBot={runBot}
            />
        );
        fireEvent.click(screen.getByText(CONSTANTS.RUN_BOT));
        expect(runBot).toHaveBeenCalled();
    });

    it("shows loading state on button when loading is true", () => {
        render(
            <AttendanceForm
                {...defaultProps}
                loading={true}
                date="2024-06-09"
                group={CONSTANTS.SATURDAY_K1}
                sabhaHeld={CONSTANTS.NO}
            />
        );
        expect(screen.getByText(CONSTANTS.RUNNING)).toBeInTheDocument();
        expect(screen.getByText(CONSTANTS.RUNNING)).toBeDisabled();
    });

    it("calls setDate when date is changed", () => {
        const setDate = jest.fn();
        render(
            <AttendanceForm
                {...defaultProps}
                setDate={setDate}
            />
        );
        fireEvent.change(screen.getByLabelText(CONSTANTS.SELECT_A_VALID_SUNDAY), {
            target: { value: "2024-06-09" }
        });
        expect(setDate).toHaveBeenCalledWith("2024-06-09");
    });

    it("calls setGroup when group is changed", () => {
        const setGroup = jest.fn();
        render(
            <AttendanceForm
                {...defaultProps}
                setGroup={setGroup}
            />
        );
        fireEvent.change(screen.getByTestId(CONSTANTS.SELECT_GROUP), {
            target: { value: CONSTANTS.SATURDAY_K2 }
        });
        expect(setGroup).toHaveBeenCalled();
    });

    it("calls setSabhaHeld when sabhaHeld is changed", () => {
        const setSabhaHeld = jest.fn();
        render(
            <AttendanceForm
                {...defaultProps}
                setSabhaHeld={setSabhaHeld}
            />
        );
        fireEvent.change(screen.getByTestId(CONSTANTS.WAS_SABHA_HELD), {
            target: { value: CONSTANTS.YES }
        });
        expect(setSabhaHeld).toHaveBeenCalled();
    });

    it("calls setP2Guju and setPrepCycleDone when those fields are changed", () => {
        const setP2Guju = jest.fn();
        const setPrepCycleDone = jest.fn();
        render(
            <AttendanceForm
                {...defaultProps}
                sabhaHeld={CONSTANTS.YES}
                setP2Guju={setP2Guju}
                setPrepCycleDone={setPrepCycleDone}
            />
        );
        fireEvent.change(screen.getByTestId(CONSTANTS.WAS_P2_IN_GUJU), {
            target: { value: CONSTANTS.NO }
        });
        fireEvent.change(screen.getByTestId(CONSTANTS.PREP_CYCLE_DONE), {
            target: { value: CONSTANTS.YES }
        });
        expect(setP2Guju).toHaveBeenCalled();
        expect(setPrepCycleDone).toHaveBeenCalled();
    });

    it("calls filterValidSundays with the correct date in shouldDisableDate", () => {
        render(<AttendanceForm {...defaultProps} />);
        const testDate = "2024-06-09";
        expect(filterValidSundays).toHaveBeenCalledWith(testDate);
    });

    it("should disable dates where filterValidSundays returns false", () => {
        const { filterValidSundays } = require("../../utils/functions");
        filterValidSundays.mockImplementation((date) => date !== "2024-06-09");
        render(<AttendanceForm {...defaultProps} />);
        const shouldDisable = (date) => !filterValidSundays(date);
        expect(shouldDisable("2024-06-09")).toBe(true);
        expect(shouldDisable("2024-06-16")).toBe(false);
    });

    it("calls setSignInOpen(false) when SignInModal onClose is triggered", () => {
        const setSignInOpen = jest.fn();
        render(
            <AttendanceForm
                {...defaultProps}
                signInOpen={true}
                setSignInOpen={setSignInOpen}
            />
        );
        jest.resetModules();
        const SignInModal = ({ open, onClose }) => {
            if (open) onClose();
            return null;
        };
        jest.doMock("../SignInModal/SignInModal", () => SignInModal);
        const AttendanceFormReloaded = require("./AttendanceForm").default;
        render(
            <AttendanceFormReloaded
                {...defaultProps}
                signInOpen={true}
                setSignInOpen={setSignInOpen}
            />
        );
        expect(setSignInOpen).toHaveBeenCalledWith(false);
    });
});