import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import UserUpdateBot from "./UserUpdateBot";

jest.mock("./UserUpdateBot.module.css", () => ({
  container: "container",
  title: "title",
  card: "card",
  label: "label",
  textarea: "textarea",
  countdown: "countdown",
  logBox: "logBox",
  logLine: "logLine",
  logError: "logError",
  logHeader: "logHeader",
}));

jest.mock("../Button/Button", () => (props) => (
  <button onClick={props.onClick} disabled={props.disabled} data-testid="run-btn">
    {props.children}
  </button>
));

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

beforeAll(() => {
  window.HTMLElement.prototype.scrollIntoView = jest.fn();
});

beforeEach(() => {
  global.EventSource = jest.fn(() => ({ close: jest.fn() }));
  global.fetch = jest.fn();
  window.alert = jest.fn();
  process.env.REACT_APP_API_URL = "http://test";
});

afterEach(() => {
  jest.clearAllMocks();
});

describe("UserUpdateBot", () => {
  it("renders the title, textarea, and button", () => {
    render(<UserUpdateBot />);
    expect(screen.getByText("User Update Bot")).toBeInTheDocument();
    expect(screen.getByRole("textbox")).toBeInTheDocument();
    expect(screen.getByTestId("run-btn")).toBeInTheDocument();
    expect(screen.getByText("Run Bot")).toBeInTheDocument();
  });

  it("updates textarea value on change", () => {
    render(<UserUpdateBot />);
    const textarea = screen.getByRole("textbox");
    fireEvent.change(textarea, { target: { value: "12345\n67890" } });
    expect(textarea.value).toBe("12345\n67890");
  });

  it("alerts when textarea is empty", () => {
    render(<UserUpdateBot />);
    fireEvent.click(screen.getByTestId("run-btn"));
    expect(window.alert).toHaveBeenCalledWith("Please enter at least one User ID.");
  });

  it("alerts when textarea contains only whitespace", () => {
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "   \n  " } });
    fireEvent.click(screen.getByTestId("run-btn"));
    expect(window.alert).toHaveBeenCalledWith("Please enter at least one User ID.");
  });

  it("calls fetch with correct method, headers, and body", async () => {
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345\n67890" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/run-user-update-stream"),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_ids: ["12345", "67890"] }),
      }
    );
  });

  it("creates and immediately closes EventSource", async () => {
    const mockClose = jest.fn();
    global.EventSource = jest.fn(() => ({ close: mockClose }));
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    expect(global.EventSource).toHaveBeenCalled();
    expect(mockClose).toHaveBeenCalled();
  });

  it("sets running=false and re-enables button after __DONE__", async () => {
    fetch.mockResolvedValue(makeStream("data: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByTestId("run-btn")).not.toBeDisabled());
    expect(screen.getByText("Run Bot")).toBeInTheDocument();
  });

  it("adds regular messages to the log", async () => {
    fetch.mockResolvedValue(makeStream("data: Processing 12345\n", "data: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("Processing 12345")).toBeInTheDocument());
  });

  it("skips lines that do not start with 'data: '", async () => {
    fetch.mockResolvedValue(makeStream(": keep-alive\ndata: hello\ndata: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("hello")).toBeInTheDocument());
    expect(screen.queryByText("keep-alive")).not.toBeInTheDocument();
  });

  it("accumulates buffer across partial chunks", async () => {
    fetch.mockResolvedValue(makeStream("data: hel", "lo world\ndata: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("hello world")).toBeInTheDocument());
  });

  it("sets running=false when stream ends without __DONE__", async () => {
    fetch.mockResolvedValue(makeStream("data: hello\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByTestId("run-btn")).not.toBeDisabled());
  });

  it("shows a connection error log on fetch failure", async () => {
    fetch.mockRejectedValue(new Error("Network Error"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() =>
      expect(screen.getByText("Connection error: Network Error")).toBeInTheDocument()
    );
  });

  it("applies logError class to lines containing ERROR", async () => {
    fetch.mockResolvedValue(makeStream("data: ERROR: bad thing\ndata: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => {
      expect(screen.getByText("ERROR: bad thing").className).toContain("logError");
    });
  });

  it("applies logHeader class to lines starting with ---", async () => {
    fetch.mockResolvedValue(makeStream("data: --- Section ---\ndata: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => {
      expect(screen.getByText("--- Section ---").className).toContain("logHeader");
    });
  });

  it("applies logLine class to regular log lines", async () => {
    fetch.mockResolvedValue(makeStream("data: normal line\ndata: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => {
      expect(screen.getByText("normal line").className).toContain("logLine");
    });
  });

  it("shows countdown display when __COUNTDOWN__ message received", async () => {
    let resolveHold;
    const hold = new Promise((res) => { resolveHold = res; });
    fetch.mockResolvedValue({
      body: {
        getReader: () => ({
          read: jest.fn()
            .mockResolvedValueOnce({ done: false, value: encoder.encode("data: __COUNTDOWN__10\n") })
            .mockReturnValue(hold),
        }),
      },
    });
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    act(() => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() =>
      expect(screen.getByText("Waiting for login — 10s remaining")).toBeInTheDocument()
    );
    await act(async () => { resolveHold({ done: true }); });
  });

  it("shows running spinner (…) when running with no countdown", async () => {
    let resolveHold;
    const hold = new Promise((res) => { resolveHold = res; });
    fetch.mockResolvedValue({
      body: {
        getReader: () => ({
          read: jest.fn().mockReturnValue(hold),
        }),
      },
    });
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    act(() => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("...")).toBeInTheDocument());
    await act(async () => { resolveHold({ done: true }); });
  });

  it("disables textarea while running", async () => {
    let resolveHold;
    const hold = new Promise((res) => { resolveHold = res; });
    fetch.mockResolvedValue({
      body: {
        getReader: () => ({
          read: jest.fn().mockReturnValue(hold),
        }),
      },
    });
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    act(() => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByRole("textbox")).toBeDisabled());
    await act(async () => { resolveHold({ done: true }); });
  });

  it("shows Running… on the button while running", async () => {
    let resolveHold;
    const hold = new Promise((res) => { resolveHold = res; });
    fetch.mockResolvedValue({
      body: {
        getReader: () => ({
          read: jest.fn().mockReturnValue(hold),
        }),
      },
    });
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    act(() => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("Running...")).toBeInTheDocument());
    await act(async () => { resolveHold({ done: true }); });
  });

  it("clears countdown after a regular message follows a countdown", async () => {
    fetch.mockResolvedValue(
      makeStream("data: __COUNTDOWN__5\n", "data: regular\n", "data: __DONE__\n")
    );
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("regular")).toBeInTheDocument());
    expect(screen.queryByText(/Waiting for login/)).not.toBeInTheDocument();
  });

  it("scrolls log into view when logs update", async () => {
    fetch.mockResolvedValue(makeStream("data: msg\n", "data: __DONE__\n"));
    render(<UserUpdateBot />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "12345" } });
    await act(async () => { fireEvent.click(screen.getByTestId("run-btn")); });
    await waitFor(() => expect(screen.getByText("msg")).toBeInTheDocument());
    expect(window.HTMLElement.prototype.scrollIntoView).toHaveBeenCalled();
  });
});
