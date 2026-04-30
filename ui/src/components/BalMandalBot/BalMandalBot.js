import { useState } from "react";
import { runBalMandalBot } from "../../utils/functions";
import { CONSTANTS } from "../../utils/CONSTANTS";
import BalMandalForm from "../BalMandalForm/BalMandalForm";
import styles from "./BalMandalBot.module.css";

const BalMandalBot = () => {
  const [date, setDate] = useState(null);
  const [day, setDay] = useState("");
  const [sabhaHeld, setSabhaHeld] = useState("");
  const [combinedGroups, setCombinedGroups] = useState("");
  const [smrutiTime, setSmrutiTime] = useState("No");
  const [mukhpath, setMukhpath] = useState("No");
  const [prepCycleDone, setPrepCycleDone] = useState("No");
  const [individualGroups, setIndividualGroups] = useState({});
  const [captchaSeconds, setCaptchaSeconds] = useState("20");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [countdown, setCountdown] = useState(null);

  const runBot = () =>
    runBalMandalBot({
      date,
      day,
      sabhaHeld,
      combinedGroups,
      smrutiTime,
      mukhpath,
      prepCycleDone,
      individualGroups,
      captchaSeconds,
      setLogs,
      setCountdown,
      setLoading,
    });

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{CONSTANTS.BAL_MANDAL_BOT}</h1>
      <BalMandalForm
        date={date}
        setDate={setDate}
        day={day}
        setDay={setDay}
        sabhaHeld={sabhaHeld}
        setSabhaHeld={setSabhaHeld}
        combinedGroups={combinedGroups}
        setCombinedGroups={setCombinedGroups}
        smrutiTime={smrutiTime}
        setSmrutiTime={setSmrutiTime}
        mukhpath={mukhpath}
        setMukhpath={setMukhpath}
        prepCycleDone={prepCycleDone}
        setPrepCycleDone={setPrepCycleDone}
        individualGroups={individualGroups}
        setIndividualGroups={setIndividualGroups}
        captchaSeconds={captchaSeconds}
        setCaptchaSeconds={setCaptchaSeconds}
        loading={loading}
        runBot={runBot}
        logs={logs}
        countdown={countdown}
      />
    </div>
  );
};

export default BalMandalBot;
