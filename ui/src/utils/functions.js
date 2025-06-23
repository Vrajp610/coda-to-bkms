import * as axios from "axios";
import { CONSTANTS } from "./CONSTANTS";

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

export function handleRunBotHelper(signedIn, setSignInOpen, runBot) {
  if (!signedIn) {
    setSignInOpen(true);
  } else {
    runBot();
  }
}

export function handleSignInSuccessHelper(setSignedIn, setSignInOpen, runBot) {
  setSignedIn(true);
  setSignInOpen(false);
  runBot();
}
