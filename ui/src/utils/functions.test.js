import { filterValidSundays, runAttendanceBot, runBalMandalBot, runGoshthiBot, handleRunBotHelper, handleSignInSuccessHelper, getApiUrl, getApiHeaders } from "./functions";
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
        delete process.env.REACT_APP_BKMS_TOKEN;
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

    it("clamps captchaSeconds to valid range", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runAttendanceBot({ ...baseParams, captchaSeconds: 9999 });
        const body = JSON.parse(fetch.mock.calls[0][1].body);
        expect(body.captchaSeconds).toBe(300);
    });

    it("uses default captchaSeconds=20 when non-numeric", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runAttendanceBot({ ...baseParams, captchaSeconds: "abc" });
        const body = JSON.parse(fetch.mock.calls[0][1].body);
        expect(body.captchaSeconds).toBe(20);
    });
});

describe("runGoshthiBot", () => {
  const mockSetLogs = jest.fn();
  const mockSetCountdown = jest.fn();
  const mockSetLoading = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
    window.alert = jest.fn();
    process.env.REACT_APP_API_URL = "http://test";
    delete process.env.REACT_APP_BKMS_TOKEN;
  });

  const baseParams = {
    selectedMonth: new Date("2026-01-01"),
    goshthiHeld: CONSTANTS.YES,
    hangout: "No",
    workshop: "Yes",
    setLogs: mockSetLogs,
    setCountdown: mockSetCountdown,
    setLoading: mockSetLoading,
  };

  it("alerts if selectedMonth is missing", async () => {
    await runGoshthiBot({ ...baseParams, selectedMonth: null });
    expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
    expect(mockSetLoading).not.toHaveBeenCalled();
  });

  it("alerts if goshthiHeld is missing", async () => {
    await runGoshthiBot({ ...baseParams, goshthiHeld: null });
    expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
  });

  it("alerts if goshthiHeld=Yes but hangout is missing", async () => {
    await runGoshthiBot({ ...baseParams, hangout: null });
    expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
  });

  it("alerts if goshthiHeld=Yes but workshop is missing", async () => {
    await runGoshthiBot({ ...baseParams, workshop: null });
    expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
  });

  it("does not alert when goshthiHeld=No (hangout and workshop not required)", async () => {
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    await runGoshthiBot({ ...baseParams, goshthiHeld: "No", hangout: null, workshop: null });
    expect(window.alert).not.toHaveBeenCalled();
  });

  it("calls fetch with correct URL, method, and headers", async () => {
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    await runGoshthiBot(baseParams);
    expect(fetch).toHaveBeenCalledWith(
      "http://test/run-goshthi-stream",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
    );
  });

  it("sets loading=true then false on success", async () => {
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    await runGoshthiBot(baseParams);
    expect(mockSetLoading).toHaveBeenCalledWith(true);
    expect(mockSetLoading).toHaveBeenLastCalledWith(false);
  });

  it("streams log messages into setLogs", async () => {
    fetch.mockResolvedValue(makeStream("data: hello\n", "data: __DONE__\n"));
    await runGoshthiBot(baseParams);
    expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
  });

  it("setLogs callback appends message to previous logs", async () => {
    const accumulated = [];
    const execSetLogs = jest.fn().mockImplementation((fn) => {
      if (typeof fn === "function") accumulated.push(...fn([]));
    });
    fetch.mockResolvedValue(makeStream("data: goshthi msg\n", "data: __DONE__\n"));
    await runGoshthiBot({ ...baseParams, setLogs: execSetLogs });
    expect(accumulated).toContain("goshthi msg");
  });

  it("handles __COUNTDOWN__ via setCountdown", async () => {
    fetch.mockResolvedValue(makeStream("data: __COUNTDOWN__20\n", "data: __DONE__\n"));
    await runGoshthiBot(baseParams);
    expect(mockSetCountdown).toHaveBeenCalledWith(20);
  });

  it("sets countdown=null after __COUNTDOWN__ clears", async () => {
    fetch.mockResolvedValue(makeStream(
      "data: __COUNTDOWN__10\n",
      "data: regular msg\n",
      "data: __DONE__\n"
    ));
    await runGoshthiBot(baseParams);
    const nullCalls = mockSetCountdown.mock.calls.filter(([v]) => v === null);
    expect(nullCalls.length).toBeGreaterThan(0);
  });

  it("handles connection errors and logs the error", async () => {
    const accumulated = [];
    const execSetLogs = jest.fn().mockImplementation((fn) => {
      if (typeof fn === "function") accumulated.push(...fn([]));
    });
    fetch.mockRejectedValue(new Error("Network Error"));
    await runGoshthiBot({ ...baseParams, setLogs: execSetLogs });
    expect(accumulated.some((l) => l.includes("Connection error"))).toBe(true);
    expect(mockSetLoading).toHaveBeenLastCalledWith(false);
  });

  it("sets loading=false when stream ends without __DONE__", async () => {
    fetch.mockResolvedValue(makeStream("data: partial\n"));
    await runGoshthiBot(baseParams);
    expect(mockSetLoading).toHaveBeenLastCalledWith(false);
  });

  it("skips lines that do not start with 'data: '", async () => {
    fetch.mockResolvedValue(makeStream("ignore this\ndata: hello\ndata: __DONE__\n"));
    await runGoshthiBot(baseParams);
    expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
  });

  it("uses REACT_APP_API_URL when set", async () => {
    process.env.REACT_APP_API_URL = "http://custom.goshthi";
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    await runGoshthiBot(baseParams);
    expect(fetch).toHaveBeenCalledWith(
      "http://custom.goshthi/run-goshthi-stream",
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

describe("getApiUrl", () => {
    const originalEnv = process.env.REACT_APP_API_URL;

    afterEach(() => {
        process.env.REACT_APP_API_URL = originalEnv;
        delete window.location;
        window.location = { hostname: "localhost", protocol: "http:" };
    });

    it("returns REACT_APP_API_URL when set", () => {
        process.env.REACT_APP_API_URL = "http://custom-api.com";
        expect(getApiUrl()).toBe("http://custom-api.com");
    });

    it("returns localhost URL when hostname is localhost and env not set", () => {
        delete process.env.REACT_APP_API_URL;
        Object.defineProperty(window, "location", {
            value: { hostname: "localhost", protocol: "http:" },
            writable: true,
        });
        expect(getApiUrl()).toBe("http://127.0.0.1:8000");
    });

    it("returns localhost URL when hostname is 127.0.0.1 and env not set", () => {
        delete process.env.REACT_APP_API_URL;
        Object.defineProperty(window, "location", {
            value: { hostname: "127.0.0.1", protocol: "http:" },
            writable: true,
        });
        expect(getApiUrl()).toBe("http://127.0.0.1:8000");
    });

    it("returns protocol+hostname for production when env not set", () => {
        delete process.env.REACT_APP_API_URL;
        Object.defineProperty(window, "location", {
            value: { hostname: "myapp.fly.dev", protocol: "https:" },
            writable: true,
        });
        expect(getApiUrl()).toBe("https://myapp.fly.dev");
    });
});

describe("getApiHeaders", () => {
    afterEach(() => {
        delete process.env.REACT_APP_BKMS_TOKEN;
    });

    it("returns only Content-Type when BKMS_TOKEN is not set", () => {
        delete process.env.REACT_APP_BKMS_TOKEN;
        expect(getApiHeaders()).toEqual({ "Content-Type": "application/json" });
    });

    it("includes X-Bkms-Token when BKMS_TOKEN is set", () => {
        process.env.REACT_APP_BKMS_TOKEN = "mock-token-123";
        expect(getApiHeaders()).toEqual({
            "Content-Type": "application/json",
            "X-Bkms-Token": "mock-token-123",
        });
    });
});

describe("runBalMandalBot", () => {
    const mockSetLogs = jest.fn();
    const mockSetCountdown = jest.fn();
    const mockSetLoading = jest.fn();

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

    beforeEach(() => {
        jest.clearAllMocks();
        global.fetch = jest.fn();
        window.alert = jest.fn();
        process.env.REACT_APP_API_URL = "http://test";
        delete process.env.REACT_APP_BKMS_TOKEN;
    });

    const baseParams = {
        date: new Date("2024-06-15T12:00:00Z"),
        day: "Saturday",
        sabhaHeld: "Yes",
        combinedGroups: "No",
        smrutiTime: "Yes",
        mukhpath: "No",
        prepCycleDone: "Yes",
        individualGroups: {},
        captchaSeconds: 20,
        setLogs: mockSetLogs,
        setCountdown: mockSetCountdown,
        setLoading: mockSetLoading,
    };

    it("alerts if date is missing", async () => {
        await runBalMandalBot({ ...baseParams, date: null });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
        expect(mockSetLoading).not.toHaveBeenCalled();
    });

    it("alerts if day is missing", async () => {
        await runBalMandalBot({ ...baseParams, day: null });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
    });

    it("alerts if sabhaHeld is missing", async () => {
        await runBalMandalBot({ ...baseParams, sabhaHeld: null });
        expect(window.alert).toHaveBeenCalledWith(CONSTANTS.REQUIRED_FIELDS);
    });

    it("calls fetch with correct URL, method, and headers", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runBalMandalBot(baseParams);
        expect(fetch).toHaveBeenCalledWith(
            "http://test/run-bal-mandal-stream",
            expect.objectContaining({
                method: "POST",
                headers: { "Content-Type": "application/json" },
            })
        );
    });

    it("sets loading=true then false on success", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runBalMandalBot(baseParams);
        expect(mockSetLoading).toHaveBeenCalledWith(true);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
    });

    it("streams log messages into setLogs", async () => {
        fetch.mockResolvedValue(makeStream("data: hello\n", "data: __DONE__\n"));
        await runBalMandalBot(baseParams);
        expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
    });

    it("handles __COUNTDOWN__ messages", async () => {
        fetch.mockResolvedValue(makeStream("data: __COUNTDOWN__10\n", "data: __DONE__\n"));
        await runBalMandalBot(baseParams);
        expect(mockSetCountdown).toHaveBeenCalledWith(10);
    });

    it("handles connection errors", async () => {
        const accumulated = [];
        const execSetLogs = jest.fn().mockImplementation((fn) => {
            if (typeof fn === "function") accumulated.push(...fn([]));
        });
        fetch.mockRejectedValue(new Error("Network Error"));
        await runBalMandalBot({ ...baseParams, setLogs: execSetLogs });
        expect(accumulated.some((l) => l.includes("Connection error"))).toBe(true);
    });

    it("sets loading=false when stream ends without __DONE__", async () => {
        fetch.mockResolvedValue(makeStream("data: partial\n"));
        await runBalMandalBot(baseParams);
        expect(mockSetLoading).toHaveBeenLastCalledWith(false);
    });

    it("clamps captchaSeconds to valid range", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runBalMandalBot({ ...baseParams, captchaSeconds: 9999 });
        const body = JSON.parse(fetch.mock.calls[0][1].body);
        expect(body.captchaSeconds).toBe(300);
    });

    it("uses default captchaSeconds=20 when non-numeric", async () => {
        fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
        await runBalMandalBot({ ...baseParams, captchaSeconds: "abc" });
        const body = JSON.parse(fetch.mock.calls[0][1].body);
        expect(body.captchaSeconds).toBe(20);
    });

    it("skips lines that do not start with 'data: '", async () => {
        fetch.mockResolvedValue(makeStream(": keep-alive\nignore this\ndata: hello\ndata: __DONE__\n"));
        await runBalMandalBot(baseParams);
        expect(mockSetLogs).toHaveBeenCalledWith(expect.any(Function));
    });

    it("setLogs callback appends message to previous logs", async () => {
        const accumulated = [];
        const execSetLogs = jest.fn().mockImplementation((fn) => {
            if (typeof fn === "function") accumulated.push(...fn([]));
        });
        fetch.mockResolvedValue(makeStream("data: bal msg\n", "data: __DONE__\n"));
        await runBalMandalBot({ ...baseParams, setLogs: execSetLogs });
        expect(accumulated).toContain("bal msg");
    });
});

describe("functions.js edge cases", () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.fetch = jest.fn();
        window.alert = jest.fn();
    });

    afterEach(() => {
        delete process.env.REACT_APP_API_URL;
        delete process.env.REACT_APP_BKMS_TOKEN;
    });

    it("runAttendanceBot with sabhaHeld=No does not require p2Guju or prepCycleDone", async () => {
        const mockSetLogs = jest.fn();
        const mockSetCountdown = jest.fn();
        const mockSetLoading = jest.fn();
        process.env.REACT_APP_API_URL = "http://test";
        fetch.mockResolvedValue({
            body: {
                getReader: () => ({
                    read: jest.fn()
                        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode("data: __DONE__\n") })
                        .mockResolvedValueOnce({ done: true }),
                }),
            },
        });

        await runAttendanceBot({
            date: new Date(),
            group: "GroupA",
            sabhaHeld: "No",
            p2Guju: null,
            prepCycleDone: null,
            captchaSeconds: 20,
            setLogs: mockSetLogs,
            setCountdown: mockSetCountdown,
            setLoading: mockSetLoading,
        });

        expect(window.alert).not.toHaveBeenCalled();
        expect(mockSetLoading).toHaveBeenCalledWith(true);
    });

    it("runBalMandalBot sends all parameters including individualGroups in body", async () => {
        const mockSetLogs = jest.fn();
        const mockSetCountdown = jest.fn();
        const mockSetLoading = jest.fn();
        process.env.REACT_APP_API_URL = "http://test";
        fetch.mockResolvedValue({
            body: {
                getReader: () => ({
                    read: jest.fn()
                        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode("data: __DONE__\n") })
                        .mockResolvedValueOnce({ done: true }),
                }),
            },
        });

        const individualGroups = { "group 0": { held: "Yes", smruti_time: "No" } };
        await runBalMandalBot({
            date: new Date("2026-03-15"),
            day: "Saturday",
            sabhaHeld: "Yes",
            combinedGroups: "No",
            smrutiTime: "No",
            mukhpath: "No",
            prepCycleDone: "Yes",
            individualGroups,
            captchaSeconds: 30,
            setLogs: mockSetLogs,
            setCountdown: mockSetCountdown,
            setLoading: mockSetLoading,
        });

        const callBody = JSON.parse(fetch.mock.calls[0][1].body);
        expect(callBody.day).toBe("Saturday");
        expect(callBody.combinedGroups).toBe("No");
        expect(callBody.individualGroups).toEqual(individualGroups);
        expect(callBody.captchaSeconds).toBe(30);
    });

    it("runGoshthiBot properly formats month and year in body", async () => {
        const mockSetLogs = jest.fn();
        const mockSetCountdown = jest.fn();
        const mockSetLoading = jest.fn();
        process.env.REACT_APP_API_URL = "http://test";
        fetch.mockResolvedValue({
            body: {
                getReader: () => ({
                    read: jest.fn()
                        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode("data: __DONE__\n") })
                        .mockResolvedValueOnce({ done: true }),
                }),
            },
        });

        await runGoshthiBot({
            selectedMonth: new Date("2026-03-15"),
            goshthiHeld: "Yes",
            hangout: "Yes",
            workshop: "No",
            setLogs: mockSetLogs,
            setCountdown: mockSetCountdown,
            setLoading: mockSetLoading,
        });

        const callBody = JSON.parse(fetch.mock.calls[0][1].body);
        expect(callBody.month).toBe("March");
        expect(callBody.year).toBe("2026");
    });
});