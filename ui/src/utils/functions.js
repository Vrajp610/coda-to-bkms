import * as axios from "axios";
import { CONSTANTS } from "./CONSTANTS";

/**
 * Filters valid Sundays for attendance based on the current date.
 * Valid Sundays are:
 * - The current Sunday
 * - The Sunday one week ago
 * - The Sunday two weeks ago
 * - The next Sunday
 *
 * @param {Date} date - The date to check.
 * @returns {boolean} - True if the date is a valid Sunday, false otherwise.
 */
export const filterValidSundays = (date) => {
  const today = new Date();
  const currentSunday = new Date(today);
  currentSunday.setDate(today.getDate() - today.getDay());

  const oneWeekAgoSunday = new Date(currentSunday);
  oneWeekAgoSunday.setDate(currentSunday.getDate() - 7);

  const twoWeeksAgoSunday = new Date(currentSunday);
  twoWeeksAgoSunday.setDate(currentSunday.getDate() - 14);

  const nextSunday = new Date(today);
  nextSunday.setDate(today.getDate() + (7 - today.getDay()));

  const allowedDates = [
    currentSunday.toDateString(),
    oneWeekAgoSunday.toDateString(),
    twoWeeksAgoSunday.toDateString(),
    nextSunday.toDateString(),
  ];

  return date.getDay() === 0 && allowedDates.includes(date.toDateString());
};

/**
 * Runs the attendance bot with the provided parameters.
 *
 * @param {Object} params - The parameters for running the bot.
 * @param {Date} params.date - The date of the attendance.
 * @param {string} params.group - The group for which attendance is being marked.
 * @param {string} params.sabhaHeld - Whether the sabha was held.
 * @param {string} params.p2Guju - Whether P2 was in Guju.
 * @param {string} params.prepCycleDone - Whether the prep cycle was done.
 * @param {Function} params.setStatus - Function to set the status message.
 * @param {Function} params.setMarkedPresent - Function to set marked present count.
 * @param {Function} params.setNotMarked - Function to set not marked count.
 * @param {Function} params.setNotFoundInBkms - Function to set not found in BKMS count.
 * @param {Function} params.setLoading - Function to set loading state.
 */
export async function runAttendanceBot({
  date,
  group,
  sabhaHeld,
  p2Guju,
  prepCycleDone,
  setStatus,
  setMarkedPresent,
  setNotMarked,
  setNotFoundInBkms,
  setLoading,
}) {
  if (
    !date ||
    !group ||
    !sabhaHeld ||
    (sabhaHeld === CONSTANTS.YES && (!p2Guju || !prepCycleDone))
  ) {
    window.alert(CONSTANTS.REQUIRED_FIELDS);
    return;
  }

  const options = { month: CONSTANTS.LONG, day: CONSTANTS.NUMERIC };
  const formattedDate = date.toLocaleDateString("en-US", options);

  setLoading(true);
  setStatus("");
  setMarkedPresent(null);
  setNotMarked(null);
  setNotFoundInBkms(null);
  try {
    const API_BASE_URL = process.env.REACT_APP_API_URL || CONSTANTS.LOCAL_URL;

    const response = await axios.post(`${API_BASE_URL}/run-bot`, {
      date: formattedDate,
      group,
      sabhaHeld,
      p2Guju,
      prepCycleDone,
    });
    setStatus(response.data.message || response.data.error);
    if (response.data.marked_present !== undefined)
      setMarkedPresent(response.data.marked_present);
    if (response.data.not_marked !== undefined)
      setNotMarked(response.data.not_marked);
    if (response.data.not_found_in_bkms !== undefined)
      setNotFoundInBkms(response.data.not_found_in_bkms);
  } catch (error) {
    setStatus(CONSTANTS.SOMETHING_WENT_WRONG);
  }
  setLoading(false);
}

/** * Handles the run bot action based on the signed-in state.
 *
 * @param {boolean} signedIn - Whether the user is signed in.
 * @param {Function} setSignInOpen - Function to open the sign-in modal.
 * @param {Function} runBot - Function to run the bot.
 */
export function handleRunBotHelper(signedIn, setSignInOpen, runBot) {
  if (!signedIn) {
    setSignInOpen(true);
  } else {
    runBot();
  }
}

/** * Handles the success of the sign-in action.
 *
 * @param {Function} setSignedIn - Function to set the signed-in state.
 * @param {Function} setSignInOpen - Function to close the sign-in modal.
 * @param {Function} runBot - Function to run the bot after signing in.
 */
export function handleSignInSuccessHelper(setSignedIn, setSignInOpen, runBot) {
  setSignedIn(true);
  setSignInOpen(false);
  runBot();
}