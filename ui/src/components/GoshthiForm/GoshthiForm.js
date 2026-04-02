import { useRef, useEffect } from "react";
import Button from "../Button/Button";
import styles from "./GoshthiForm.module.css";
import { CONSTANTS } from "../../utils/CONSTANTS";

function getValidMonths() {
  const today = new Date();
  const offsets = [
    { offset: -2, label: "2 Months Ago" },
    { offset: -1, label: "Last Month" },
    { offset:  0, label: "This Month" },
    { offset:  1, label: "Next Month" },
  ];
  return offsets.map(({ offset, label }) => {
    const d = new Date(today.getFullYear(), today.getMonth() + offset, 1);
    return { date: d, label };
  });
}

const YesNo = ({ value, onChange }) => (
  <div className={styles.toggle}>
    {["Yes", "No"].map((opt) => (
      <button
        key={opt}
        className={`${styles.toggleBtn} ${value === opt ? styles.toggleBtnActive : ""}`}
        onClick={() => onChange(opt)}
        type="button"
      >
        {opt}
      </button>
    ))}
  </div>
);

const GoshthiForm = ({
  selectedMonth, setSelectedMonth,
  goshthiHeld, setGoshthiHeld,
  hangout, setHangout,
  workshop, setWorkshop,
  loading, runBot,
  logs, countdown,
}) => {
  const months = getValidMonths();
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className={styles.form}>

      <div className={styles.sectionLabel}>Month</div>
      <div className={styles.monthGrid}>
        {months.map(({ date: d, label }) => {
          const key = `${d.getFullYear()}-${d.getMonth()}`;
          const isSelected =
            selectedMonth &&
            selectedMonth.getFullYear() === d.getFullYear() &&
            selectedMonth.getMonth() === d.getMonth();
          return (
            <button
              key={key}
              type="button"
              className={`${styles.monthTile} ${isSelected ? styles.monthTileActive : ""}`}
              onClick={() => setSelectedMonth(d)}
            >
              <span className={styles.monthLabel}>{label}</span>
              <span className={styles.monthValue}>
                {d.toLocaleDateString("en-US", { month: "short", year: "numeric" })}
              </span>
            </button>
          );
        })}
      </div>

      <div className={styles.sectionLabel}>Was Goshthi Held?</div>
      <YesNo value={goshthiHeld} onChange={setGoshthiHeld} />

      {goshthiHeld === CONSTANTS.YES && (
        <>
          <div className={styles.sectionLabel}>Was this a Hangout?</div>
          <YesNo value={hangout} onChange={setHangout} />

          <div className={styles.sectionLabel}>Was a Karyakar Workshop Held?</div>
          <YesNo value={workshop} onChange={setWorkshop} />
        </>
      )}

      <Button
        onClick={runBot}
        disabled={
          loading ||
          !selectedMonth || !goshthiHeld ||
          (goshthiHeld === CONSTANTS.YES && (!hangout || !workshop))
        }
        variant="contained"
      >
        {loading ? CONSTANTS.RUNNING : CONSTANTS.RUN_BOT}
      </Button>

      {loading && countdown !== null && (
        <div role="status" aria-live="polite" className={styles.countdown}>
          Waiting for login — {countdown}s remaining
        </div>
      )}

      {(logs.length > 0 || loading) && (
        <div role="log" aria-live="polite" aria-label="Bot output log" className={styles.logBox}>
          {logs.map((line, i) => (
            <div
              key={i}
              className={
                line.includes("ERROR")
                  ? styles.logError
                  : line.startsWith("---")
                  ? styles.logHeader
                  : styles.logLine
              }
            >
              {line}
            </div>
          ))}
          {loading && countdown === null && (
            <div className={styles.logLine}>...</div>
          )}
          <div ref={logEndRef} />
        </div>
      )}
    </div>
  );
};

export default GoshthiForm;
