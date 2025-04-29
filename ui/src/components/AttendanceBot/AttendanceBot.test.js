import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import AttendanceBot from "./AttendanceBot";
import axios from "axios";

jest.mock("axios");
window.alert = jest.fn();

describe("AttendanceBot", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders form title", () => {
    render(<AttendanceBot />);
    expect(screen.getByText(/BKMS Attendance Bot/i)).toBeInTheDocument();
  });

  it("alerts when required fields are not filled", () => {
    render(<AttendanceBot />);
    fireEvent.click(screen.getByText(/Run Bot/i));
    expect(window.alert).toHaveBeenCalledWith("Please fill out all required fields before running the bot.");
  });

  it("submits form when all required fields are filled", async () => {
    axios.post.mockResolvedValue({ data: { message: "Success!" } });

    render(<AttendanceBot />);
    
    // Simulate filling the form (you may need to adjust selectors if AttendanceForm is split)
    fireEvent.change(screen.getByLabelText(/Select Group/i), { target: { value: "Saturday K1" } });
    fireEvent.change(screen.getByLabelText(/Was Sabha Held\?/i), { target: { value: "No" } });

    // Manually set the date if there's a custom calendar (adjust based on your component)
    const dateInput = screen.getByPlaceholderText("Select a valid Sunday");
    fireEvent.change(dateInput, { target: { value: "04/21/2024" } });

    fireEvent.click(screen.getByText(/Run Bot/i));

    await waitFor(() => expect(axios.post).toHaveBeenCalled());
    expect(axios.post).toHaveBeenCalledWith("http://localhost:8000/run-bot", expect.any(Object));
  });
});