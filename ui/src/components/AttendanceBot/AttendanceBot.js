import React, { useState } from "react";
import axios from "axios";
import styles from "./AttendanceBot.module.css";
import AttendanceForm from "../AttendanceForm/AttendanceForm";
import { CONSTANTS } from "../../utils/CONSTANTS";

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

  const runBot = async () => {
    if (!date || !group || !sabhaHeld || (sabhaHeld === CONSTANTS.YES && (!p2Guju || !prepCycleDone))) {
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
      if (response.data.marked_present !== undefined) setMarkedPresent(response.data.marked_present);
      if (response.data.not_marked !== undefined) setNotMarked(response.data.not_marked);
      if (response.data.not_found_in_bkms !== undefined) setNotFoundInBkms(response.data.not_found_in_bkms);
    } catch (error) {
      setStatus(CONSTANTS.SOMETHING_WENT_WRONG);
    }
    setLoading(false);
  };

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
        runBot={runBot}
        markedPresent={markedPresent}
        notMarked={notMarked}
        notFoundInBkms={notFoundInBkms}
      />
    </div>
  );
};

export default AttendanceBot;
