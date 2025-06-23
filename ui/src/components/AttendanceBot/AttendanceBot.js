import { useState } from "react";
import styles from "./AttendanceBot.module.css";
import AttendanceForm from "../AttendanceForm/AttendanceForm";
import { CONSTANTS } from "../../utils/CONSTANTS";
import { runAttendanceBot, handleRunBotHelper, handleSignInSuccessHelper } from "../../utils/functions";

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
        signInOpen={signInOpen}
        setSignInOpen={setSignInOpen}
        handleSignInSuccess={() => handleSignInSuccessHelper(setSignedIn, setSignInOpen, runBot)}
      />
    </div>
  );
};

export default AttendanceBot;
