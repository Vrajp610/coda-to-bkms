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
};

describe("AttendanceAlerts", () => {
    it("renders status alert when status is provided", () => {
        render(
            <AttendanceAlerts
                status="Test status"
                markedPresent={null}
                notMarked={null}
                notFoundInBkms={null}
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
                notFoundInBkms={2}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText(/Not Found:/)).toBeInTheDocument();
        expect(screen.getByText(/2/)).toBeInTheDocument();
        expect(screen.getByRole("alert")).toHaveClass(styles.notFoundInBkms);
    });

    it("renders multiple alerts when multiple props are provided", () => {
        render(
            <AttendanceAlerts
                status="Status"
                markedPresent={1}
                notMarked={2}
                notFoundInBkms={3}
                styles={styles}
                CONSTANTS={CONSTANTS}
            />
        );
        expect(screen.getByText("Status")).toBeInTheDocument();
        expect(screen.getByText(/Marked Present:/)).toBeInTheDocument();
        expect(screen.getByText(/1/)).toBeInTheDocument();
        expect(screen.getByText(/Not Marked:/)).toBeInTheDocument();
        expect(screen.getByText(/2/)).toBeInTheDocument();
        expect(screen.getByText(/Not Found:/)).toBeInTheDocument();
        expect(screen.getByText(/3/)).toBeInTheDocument();
    });

    it("renders nothing if all props are null/undefined", () => {
        const { container } = render(
            <AttendanceAlerts
                status={null}
                markedPresent={null}
                notMarked={null}
                notFoundInBkms={null}
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
                notFoundInBkms={3}
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
});