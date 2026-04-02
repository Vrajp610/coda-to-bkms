import { useState } from "react";
import { runGoshthiBot } from "../../utils/functions";
import { CONSTANTS } from "../../utils/CONSTANTS";
import GoshthiForm from "../GoshthiForm/GoshthiForm";
import styles from "./GoshthiBot.module.css";

const GoshthiBot = () => {
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [goshthiHeld, setGoshthiHeld] = useState("");
  const [hangout, setHangout] = useState("");
  const [workshop, setWorkshop] = useState("");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [countdown, setCountdown] = useState(null);

  const runBot = () =>
    runGoshthiBot({
      selectedMonth,
      goshthiHeld,
      hangout,
      workshop,
      setLogs,
      setCountdown,
      setLoading,
    });

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{CONSTANTS.GOSHTHI_BOT}</h1>
      <GoshthiForm
        selectedMonth={selectedMonth}
        setSelectedMonth={setSelectedMonth}
        goshthiHeld={goshthiHeld}
        setGoshthiHeld={setGoshthiHeld}
        hangout={hangout}
        setHangout={setHangout}
        workshop={workshop}
        setWorkshop={setWorkshop}
        loading={loading}
        runBot={runBot}
        logs={logs}
        countdown={countdown}
      />
    </div>
  );
};

export default GoshthiBot;
