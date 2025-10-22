import { filterValidSundays, runAttendanceBot } from "./functions";
import { CONSTANTS } from "./CONSTANTS";
import axios from "axios";

jest.mock("axios");

describe("filterValidSundays", () => {
    const RealDate = Date;

    function mockDate(isoDate) {
        global.Date = class extends RealDate {
            constructor(...args) {
                if (args.length) {
                    return new RealDate(...args);
                }
                return new RealDate(isoDate);
            }
            static now() {
                return new RealDate(isoDate).getTime();
            }
        };
    }

    afterEach(() => {
        global.Date = RealDate;
    });

    it("returns true for current Sunday", () => {
        mockDate("2024-06-16T12:00:00Z");
        const today = new Date();
        expect(filterValidSundays(today)).toBe(true);
    });

    it("returns true for one week ago Sunday", () => {
        mockDate("2024-06-16T12:00:00Z");
        const oneWeekAgo = new Date("2024-06-09T12:00:00Z");
        expect(filterValidSundays(oneWeekAgo)).toBe(true);
    });

    it("returns true for two weeks ago Sunday", () => {
        mockDate("2024-06-16T12:00:00Z");
        const twoWeeksAgo = new Date("2024-06-02T12:00:00Z");
        expect(filterValidSundays(twoWeeksAgo)).toBe(true);
    });

    it("returns true for next Sunday", () => {
        mockDate("2024-06-16T12:00:00Z");
        const nextSunday = new Date("2024-06-23T12:00:00Z");
        expect(filterValidSundays(nextSunday)).toBe(true);
    });

    it("returns false for a non-Sunday", () => {
        mockDate("2024-06-16T12:00:00Z");
        const wednesday = new Date("2024-06-12T12:00:00Z");
        expect(filterValidSundays(wednesday)).toBe(false);
    });

    it("returns false for a Sunday not in allowed dates", () => {
        mockDate("2024-06-16T12:00:00Z");
        const oldSunday = new Date("2024-05-26T12:00:00Z");
        expect(filterValidSundays(oldSunday)).toBe(false);
    });
});

describe("runAttendanceBot", () => {
    const originalAlert = window.alert;
    const mockSetStatus = jest.fn();
    const mockSetMarkedPresent = jest.fn();
    const mockSetNotMarked = jest.fn();
    const mockSetNotFoundInBkms = jest.fn();
    const mockSetSabhaHeldResult = jest.fn();
    const mockSetLoading = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        window.alert = jest.fn();
        process.env.REACT_APP_API_URL = "";
    });

    afterAll(() => {
        window.alert = originalAlert;
    });

    const baseParams = {
        date: new Date("2024-06-16T12:00:00Z"),
        group: "GroupA",
        sabhaHeld: CONSTANTS.YES,
        p2Guju: "yes",
        prepCycleDone: "yes",
        setStatus: mockSetStatus,
        setMarkedPresent: mockSetMarkedPresent,
        setNotMarked: mockSetNotMarked,
        setNotFoundInBkms: mockSetNotFoundInBkms,
        setSabhaHeldResult: mockSetSabhaHeldResult,
        setLoading: mockSetLoading,
    };

    it("alerts and returns if required fields are missing", async () => {
        await runAttendanceBot({
            ...baseParams,
            date: null,
        });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
        expect(mockSetLoading).not.toHaveBeenCalledWith(true);
    });

    it("alerts and returns if sabhaHeld is YES but p2Guju or prepCycleDone is missing", async () => {
        await runAttendanceBot({
            ...baseParams,
            p2Guju: null,
        });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
    });

    it("calls API and sets state correctly on success", async () => {
        axios.post.mockResolvedValue({
            data: {
                message: "Success",
                marked_present: ["A"],
                not_marked: ["B"],
                not_found_in_bkms: ["C"],
                sabha_held: true,
            },
        });

        await runAttendanceBot(baseParams);

        expect(mockSetLoading).toHaveBeenCalledWith(true);
        expect(mockSetStatus).toHaveBeenCalledWith("Success");
        expect(mockSetMarkedPresent).toHaveBeenCalledWith(["A"]);
        expect(mockSetNotMarked).toHaveBeenCalledWith(["B"]);
        expect(mockSetNotFoundInBkms).toHaveBeenCalledWith(["C"]);
        expect(mockSetSabhaHeldResult).toHaveBeenCalledWith(true);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
    });

    it("sets error status on API failure", async () => {
        axios.post.mockRejectedValue(new Error("fail"));
        await runAttendanceBot(baseParams);
        expect(mockSetStatus).toHaveBeenCalledWith(CONSTANTS.SOMETHING_WENT_WRONG);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
    });

    it("uses REACT_APP_API_URL if set", async () => {
        process.env.REACT_APP_API_URL = "http://test.com";
        axios.post.mockResolvedValue({ data: {} });
        await runAttendanceBot(baseParams);
        expect(axios.post).toHaveBeenCalledWith(
            "http://test.com/run-bot",
            expect.any(Object)
        );
    });

    it("falls back to axios when axios.default is undefined", async () => {
        const originalDefault = axios.default;
        delete axios.default;
        axios.post.mockResolvedValue({ data: {} });
        await runAttendanceBot(baseParams);
        expect(axios.post).toHaveBeenCalled();
        axios.default = originalDefault;
    });
});