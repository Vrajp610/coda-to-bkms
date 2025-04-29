import React, { useState } from "react";
import axios from "axios";
import styles from "./AttendanceBot.module.css";
import AttendanceForm from "../AttendanceForm/AttendanceForm";

const AttendanceBot = () => {
  const [date, setDate] = useState(null);
  const [group, setGroup] = useState("");
  const [sabhaHeld, setSabhaHeld] = useState("");
  const [p2Guju, setP2Guju] = useState("");
  const [prepCycleDone, setPrepCycleDone] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const runBot = async () => {
    if (!date || !group || !sabhaHeld || (sabhaHeld === "Yes" && (!p2Guju || !prepCycleDone))) {
      window.alert("Please fill out all required fields before running the bot.");
      return;
    }

    const options = { month: "long", day: "numeric" };
    const formattedDate = date.toLocaleDateString("en-US", options);

    setLoading(true);
    setStatus("");
    try {
      const response = await axios.post("http://localhost:8000/run-bot", {
        date: formattedDate,
        group,
        sabhaHeld,
        p2Guju,
        prepCycleDone,
      });
      setStatus(response.data.message || response.data.error);
    } catch (error) {
      console.error(error);
      setStatus("Something went wrong!");
    }
    setLoading(false);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>BKMS Attendance Bot</h1>
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
      />
    </div>
  );
};

export default AttendanceBot;