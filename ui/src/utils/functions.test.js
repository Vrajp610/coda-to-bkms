import { filterValidSundays, runAttendanceBot, handleRunBotHelper, handleSignInSuccessHelper } from "./functions";
import { CONSTANTS } from "./CONSTANTS";

const encoder = new TextEncoder();

const makeStream = (...chunks) => {
  let idx = 0;
  return {
    body: {
      getReader: () => ({
        read: jest.fn().mockImplementation(() => {
          if (idx < chunks.length) {
            return Promise.resolve({ done: false, value: encoder.encode(chunks[idx++]) });
          }
          return Promise.resolve({ done: true });
        }),
      }),
    },
  };
};

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
    const mockSetLogs = jest.fn();
    const mockSetCountdown = jest.fn();
    const mockSetLoading = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        global.fetch = jest.fn();
        window.alert = jest.fn();
        process.env.REACT_APP_API_URL = "http://test";
    });

    const baseParams = {
        date: new Date("2024-06-16T12:00:00Z"),
        group: "GroupA",
        sabhaHeld: CONSTANTS.YES,
        p2Guju: "yes",
        prepCycleDone: "yes",
        setLogs: mockSetLogs,
        setCountdown: mockSetCountdown,
        setLoading: mockSetLoading,
    };

    it("alerts and returns if required fields are missing", async () => {
        await runAttendanceBot({ ...baseParams, date: null });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
        expect(mockSetLoading).not.toHaveBeenCalled();
    });

    it("alerts if sabhaHeld is YES but p2Guju is missing", async () => {
        await runAttendanceBot({ ...baseParams, p2Guju: null });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
    });

    it("calls fetch with correct URL, method, headers, and body", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runAttendanceBot(baseParams);
        expect(fetch).toHaveBeenCalledWith(
            "http://test/run-bot-stream",
            expect.objectContaining({
                method: "POST",
                headers: { "Content-Type": "application/json" },
            })
        );
    });

    it("sets loading=true then false on success", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runAttendanceBot(baseParams);
        expect(mockSetLoading).toHaveBeenCalledWith(true);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
    });

    it("streams log messages into setLogs", async () => {
        fetch.mockResolvedValue(makeStream("data: hello\n", "data: world\n", "data: __DONE__\n"));
        await runAttendanceBot(baseParams);
        expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
    });

    it("setLogs callback appends message to previous logs", async () => {
        const accumulated = [];
        const execSetLogs = jest.fn().mockImplementation((fn) => {
            if (typeof fn === "function") accumulated.push(...fn([]));
        });
        fetch.mockResolvedValue(makeStream("data: hello\n", "data: __DONE__\n"));
        await runAttendanceBot({ ...baseParams, setLogs: execSetLogs });
        expect(accumulated).toContain("hello");
    });

    it("connection error callback appends error message to logs", async () => {
        const accumulated = [];
        const execSetLogs = jest.fn().mockImplementation((fn) => {
            if (typeof fn === "function") accumulated.push(...fn([]));
        });
        fetch.mockRejectedValue(new Error("Network Error"));
        await runAttendanceBot({ ...baseParams, setLogs: execSetLogs });
        expect(accumulated.some((l) => l.includes("Connection error"))).toBe(true);
    });

    it("handles __COUNTDOWN__ messages via setCountdown", async () => {
        fetch.mockResolvedValue(makeStream("data: __COUNTDOWN__10\n", "data: __DONE__\n"));
        await runAttendanceBot(baseParams);
        expect(mockSetCountdown).toHaveBeenCalledWith(10);
    });

    it("sets loading=false and logs connection error on fetch failure", async () => {
        fetch.mockRejectedValue(new Error("Network Error"));
        await runAttendanceBot(baseParams);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
        expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
    });

    it("sets loading=false when stream ends without __DONE__", async () => {
        fetch.mockResolvedValue(makeStream("data: partial\n"));
        await runAttendanceBot(baseParams);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
    });

    it("skips lines that do not start with 'data: '", async () => {
        fetch.mockResolvedValue(makeStream("ignore this line\ndata: hello\ndata: __DONE__\n"));
        await runAttendanceBot(baseParams);
        expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
    });

    it("uses REACT_APP_API_URL when set", async () => {
        process.env.REACT_APP_API_URL = "http://custom.com";
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runAttendanceBot(baseParams);
        expect(fetch).toHaveBeenCalledWith(
            "http://custom.com/run-bot-stream",
            expect.any(Object)
        );
    });
});

describe("handleRunBotHelper", () => {
    it("calls setSignInOpen(true) when not signed in", () => {
        const setSignInOpen = jest.fn();
        const runBot = jest.fn();
        handleRunBotHelper(false, setSignInOpen, runBot);
        expect(setSignInOpen).toHaveBeenCalledWith(true);
        expect(runBot).not.toHaveBeenCalled();
    });

    it("calls runBot when already signed in", () => {
        const setSignInOpen = jest.fn();
        const runBot = jest.fn();
        handleRunBotHelper(true, setSignInOpen, runBot);
        expect(runBot).toHaveBeenCalled();
        expect(setSignInOpen).not.toHaveBeenCalled();
    });
});

describe("handleSignInSuccessHelper", () => {
    it("sets signedIn to true, closes modal, and calls runBot", () => {
        const setSignedIn = jest.fn();
        const setSignInOpen = jest.fn();
        const runBot = jest.fn();
        handleSignInSuccessHelper(setSignedIn, setSignInOpen, runBot);
        expect(setSignedIn).toHaveBeenCalledWith(true);
        expect(setSignInOpen).toHaveBeenCalledWith(false);
        expect(runBot).toHaveBeenCalled();
    });
});