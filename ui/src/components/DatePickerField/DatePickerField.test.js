import { render, screen, fireEvent } from "@testing-library/react";
import DatePickerField from "./DatePickerField";

jest.mock("@mui/x-date-pickers/DatePicker", () => ({
    DatePicker: ({ label, value, onChange, shouldDisableDate, slotProps }) => (
        <div data-testid="date-picker">
            <span>{label}</span>
            <input
                data-testid="date-input"
                value={value || ""}
                onChange={e => onChange && onChange(e.target.value)}
            />
            {shouldDisableDate && (
                <span data-testid="should-disable-date">shouldDisableDate provided</span>
            )}
            {slotProps && <span data-testid="slot-props">slotProps provided</span>}
        </div>
    ),
}));
jest.mock("@mui/x-date-pickers/LocalizationProvider", () => ({
    LocalizationProvider: ({ children }) => <div data-testid="localization-provider">{children}</div>,
}));
jest.mock("@mui/x-date-pickers/AdapterDateFns", () => ({
    AdapterDateFns: {},
}));

describe("DatePickerField", () => {
    it("renders with label", () => {
        render(<DatePickerField label="Test Label" />);
        expect(screen.getByText("Test Label")).toBeInTheDocument();
        expect(screen.getByTestId("date-picker")).toBeInTheDocument();
        expect(screen.getByTestId("localization-provider")).toBeInTheDocument();
    });

    it("passes value to DatePicker", () => {
        render(<DatePickerField label="Date" value="2024-06-01" />);
        expect(screen.getByTestId("date-input")).toHaveValue("2024-06-01");
    });

    it("calls onChange when input changes", () => {
        const handleChange = jest.fn();
        render(<DatePickerField label="Date" value="" onChange={handleChange} />);
        fireEvent.change(screen.getByTestId("date-input"), { target: { value: "2024-06-02" } });
        expect(handleChange).toHaveBeenCalledWith("2024-06-02");
    });

    it("renders shouldDisableDate indicator when provided", () => {
        const shouldDisableDate = () => false;
        render(<DatePickerField label="Date" shouldDisableDate={shouldDisableDate} />);
        expect(screen.getByTestId("should-disable-date")).toBeInTheDocument();
    });

    it("renders slotProps indicator when provided", () => {
        render(<DatePickerField label="Date" slotProps={{ someProp: true }} />);
        expect(screen.getByTestId("slot-props")).toBeInTheDocument();
    });
});