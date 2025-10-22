import { useState } from "react";
import { runAttendanceBot, handleRunBotHelper, handleSignInSuccessHelper } from "../../utils/functions";
import { CONSTANTS } from "../../utils/CONSTANTS";
import AttendanceForm from "../AttendanceForm/AttendanceForm";
import styles from "./AttendanceBot.module.css";

/** * AttendanceBot component for managing attendance operations.
 * It includes a form for inputting attendance details and running the attendance bot.
 * @returns {JSX.Element} The rendered AttendanceBot component.
 */
const AttendanceBot = () => {
  const [date, setDate] = useState(null);
  const [group, setGroup] = useState("");
  const [sabhaHeld, setSabhaHeld] = useState("");
  const [p2Guju, setP2Guju] = useState("");
  const [prepCycleDone, setPrepCycleDone] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [markedPresent, setMarkedPresent] = useState(null);
  const [notMarked, setNotMarked] = useState(null);
  const [notFoundInBkms, setNotFoundInBkms] = useState(null);
  const [sabhaHeldResult, setSabhaHeldResult] = useState(null);
  const [signInOpen, setSignInOpen] = useState(false);
  const [signedIn, setSignedIn] = useState(false);

  const runBot = () =>
    runAttendanceBot({
      date,
      group,
      sabhaHeld,
      p2Guju,
      prepCycleDone,
      setStatus,
      setMarkedPresent,
      setNotMarked,
      setNotFoundInBkms,
      setSabhaHeldResult,
      setLoading,
    });

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{CONSTANTS.ATTENDANCE_BOT}</h1>
      <AttendanceForm
        date={date}
        setDate={setDate}
        group={group}
        setGroup={setGroup}
        sabhaHeld={sabhaHeld}
        setSabhaHeld={setSabhaHeld}
        p2Guju={p2Guju}
        setP2Guju={setP2Guju}
        prepCycleDone={prepCycleDone}
        setPrepCycleDone={setPrepCycleDone}
        status={status}
        loading={loading}
        runBot={() => handleRunBotHelper(signedIn, setSignInOpen, runBot)}
        markedPresent={markedPresent}
        notMarked={notMarked}
        notFoundInBkms={notFoundInBkms}
        sabhaHeldResult={sabhaHeldResult}
        signInOpen={signInOpen}
        setSignInOpen={setSignInOpen}
        handleSignInSuccess={() => handleSignInSuccessHelper(setSignedIn, setSignInOpen, runBot)}
      />
    </div>
  );
};

export default AttendanceBot;