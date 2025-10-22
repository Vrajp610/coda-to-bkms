import { render, screen } from "@testing-library/react";
import AttendanceAlerts from "./AttendanceAlerts";

const styles = {
    status: "status-class",
    markedPresent: "marked-present-class",
    notMarked: "not-marked-class",
    notFoundInBkms: "not-found-in-bkms-class",
};

const CONSTANTS = {
    KISHORES_CLICKED: "Marked Present:",
    KISHORES_NOT_CLICKED: "Not Marked:",
    KISHORES_NOT_FOUND: "Not Found:",
    CODA_ATTENDANCE_MISSING: "Coda attendance is currently missing. Please ensure it's filled out before proceeding further.",
    SABHA_NOT_HELD: "Sabha was not held. Attendance marked accordingly in BKMS.",
};

describe("AttendanceAlerts", () => {
    it("renders status alert when status is provided", () => {
        render(
            <AttendanceAlerts
                status="Test status"
                markedPresent={null}
                notMarked={null}
                notFoundInBkms={null}
                sabhaHeldResult={null}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Test status")).toBeInTheDocument();
        expect(screen.getByRole("alert")).toHaveClass(styles.status);
    });

    it("renders markedPresent alert when markedPresent is not null", () => {
        render(
            <AttendanceAlerts
                status={null}
                markedPresent={5}
                notMarked={null}
                notFoundInBkms={null}
                sabhaHeldResult={null}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText(/Marked Present:/)).toBeInTheDocument();
        expect(screen.getByText(/5/)).toBeInTheDocument();
        expect(screen.getByRole("alert")).toHaveClass(styles.markedPresent);
    });

    it("renders notMarked alert when notMarked is not null", () => {
        render(
            <AttendanceAlerts
                status={null}
                markedPresent={null}
                notMarked={3}
                notFoundInBkms={null}
                sabhaHeldResult={null}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText(/Not Marked:/)).toBeInTheDocument();
        expect(screen.getByText(/3/)).toBeInTheDocument();
        expect(screen.getByRole("alert")).toHaveClass(styles.notMarked);
    });

    it("renders notFoundInBkms alert when notFoundInBkms is not null", () => {
        render(
            <AttendanceAlerts
                status={null}
                markedPresent={null}
                notMarked={null}
                notFoundInBkms={["1001", "1002"]}
                sabhaHeldResult={null}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText(/Not Found:/)).toBeInTheDocument();
        expect(screen.getByText(/1001, 1002/)).toBeInTheDocument();
        expect(screen.getByRole("alert")).toHaveClass(styles.notFoundInBkms);
    });

    it("renders multiple alerts when multiple props are provided", () => {
        render(
            <AttendanceAlerts
                status="Status"
                markedPresent={1}
                notMarked={2}
                notFoundInBkms={["1003"]}
                sabhaHeldResult={true}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Status")).toBeInTheDocument();
        expect(screen.getByText(/Marked Present:/)).toBeInTheDocument();
        expect(screen.getByText("Marked Present: 1")).toBeInTheDocument();
        expect(screen.getByText(/Not Marked:/)).toBeInTheDocument();
        expect(screen.getByText("Not Marked: 2")).toBeInTheDocument();
        expect(screen.getByText(/Not Found:/)).toBeInTheDocument();
        expect(screen.getByText(/1003/)).toBeInTheDocument();
    });

    it("renders nothing if all props are null/undefined", () => {
        const { container } = render(
            <AttendanceAlerts
                status={null}
                markedPresent={null}
                notMarked={null}
                notFoundInBkms={null}
                sabhaHeldResult={null}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(container).toBeEmptyDOMElement();
    });

    it("renders only Coda attendance missing alert when markedPresent is 0", () => {
        const CONSTANTS = {
            CODA_ATTENDANCE_MISSING: "Coda attendance is not filled"
        };
        
        render(
            <AttendanceAlerts
                status="Status that should not show"
                markedPresent={0}
                notMarked={2}
                notFoundInBkms={["1001"]}
                sabhaHeldResult={null}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Coda attendance is not filled")).toBeInTheDocument();
        expect(screen.queryByText("Status that should not show")).not.toBeInTheDocument();
        expect(screen.queryByText(/Marked Present:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Marked:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Found:/)).not.toBeInTheDocument();
        expect(screen.getByRole("alert")).toHaveClass(styles.markedPresent);
    });

    it("renders Sabha not held message when markedPresent is 0 and sabhaHeldResult is false", () => {
        render(
            <AttendanceAlerts
                status="Status that should not show"
                markedPresent={0}
                notMarked={2}
                notFoundInBkms={["1001", "1002"]}
                sabhaHeldResult={false}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText(CONSTANTS.SABHA_NOT_HELD)).toBeInTheDocument();
        expect(screen.queryByText("Status that should not show")).not.toBeInTheDocument();
        expect(screen.queryByText(/Marked Present:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Marked:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Found:/)).not.toBeInTheDocument();
        const alert = screen.getByRole("alert");
        expect(alert).toHaveClass(styles.markedPresent);
    });

    it("renders Coda attendance missing message when markedPresent is 0 and sabhaHeldResult is true", () => {
        render(
            <AttendanceAlerts
                status="Status that should not show"
                markedPresent={0}
                notMarked={2}
                notFoundInBkms={["1001"]}
                sabhaHeldResult={true}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText(CONSTANTS.CODA_ATTENDANCE_MISSING)).toBeInTheDocument();
        expect(screen.queryByText(CONSTANTS.SABHA_NOT_HELD)).not.toBeInTheDocument();
        expect(screen.queryByText("Status that should not show")).not.toBeInTheDocument();
        expect(screen.queryByText(/Marked Present:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Marked:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Found:/)).not.toBeInTheDocument();
        const alert = screen.getByRole("alert");
        expect(alert).toHaveClass(styles.markedPresent);
    });

    it("renders attendance details when markedPresent is greater than 0", () => {
        render(
            <AttendanceAlerts
                status="Test status"
                markedPresent={5}
                notMarked={2}
                notFoundInBkms={["1001", "1002"]}
                sabhaHeldResult={true}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Test status")).toBeInTheDocument();
        expect(screen.getByText(/Marked Present:/)).toBeInTheDocument();
        expect(screen.getByText("Marked Present: 5")).toBeInTheDocument();
        expect(screen.getByText(/Not Marked:/)).toBeInTheDocument();
        expect(screen.getByText("Not Marked: 2")).toBeInTheDocument();
        expect(screen.getByText(/Not Found:/)).toBeInTheDocument();
        expect(screen.getByText(/1001, 1002/)).toBeInTheDocument();
    });

    it("does not render notMarked alert when notMarked is 0", () => {
        render(
            <AttendanceAlerts
                status="Test status"
                markedPresent={5}
                notMarked={0}
                notFoundInBkms={[]}
                sabhaHeldResult={true}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Test status")).toBeInTheDocument();
        expect(screen.getByText(/Marked Present:/)).toBeInTheDocument();
        expect(screen.queryByText(/Not Marked:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Not Found:/)).not.toBeInTheDocument();
    });

    it("does not render notFoundInBkms alert when array is empty", () => {
        render(
            <AttendanceAlerts
                status="Test status"
                markedPresent={5}
                notMarked={null}
                notFoundInBkms={[]}
                sabhaHeldResult={true}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Test status")).toBeInTheDocument();
        expect(screen.getByText(/Marked Present:/)).toBeInTheDocument();
        expect(screen.queryByText(/Not Found:/)).not.toBeInTheDocument();
    });
});