import { useRef, useEffect, useState } from "react";
import Button from "../Button/Button";
import styles from "./BalMandalForm.module.css";
import { CONSTANTS } from "../../utils/CONSTANTS";

const SAT_GROUPS = [
  { value: CONSTANTS.SATURDAY_BAL_GROUP_0, label: "0" },
  { value: CONSTANTS.SATURDAY_BAL_GROUP_1, label: "1" },
  { value: CONSTANTS.SATURDAY_BAL_GROUP_2A, label: "2A" },
  { value: CONSTANTS.SATURDAY_BAL_GROUP_2B, label: "2B" },
  { value: CONSTANTS.SATURDAY_BAL_GROUP_3, label: "3" },
];

const SUN_GROUPS = [
  { value: CONSTANTS.SUNDAY_BAL_GROUP_0, label: "0" },
  { value: CONSTANTS.SUNDAY_BAL_GROUP_1, label: "1" },
  { value: CONSTANTS.SUNDAY_BAL_GROUP_2A, label: "2A" },
  { value: CONSTANTS.SUNDAY_BAL_GROUP_2B, label: "2B" },
  { value: CONSTANTS.SUNDAY_BAL_GROUP_3, label: "3" },
];

function getValidSundays() {
  const today = new Date();
  const currentSunday = new Date(today);
  currentSunday.setDate(today.getDate() - today.getDay());

  const make = (base, offsetWeeks, label) => {
    const d = new Date(base);
    d.setDate(base.getDate() + offsetWeeks * 7);
    return { date: d, label };
  };

  return [
    make(currentSunday, -2, "2 Weeks Ago"),
    make(currentSunday, -1, "Last Week"),
    make(currentSunday,  0, "This Sunday"),
    make(currentSunday,  1, "Next Sunday"),
  ];
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

const MiniYesNo = ({ value, onChange, disabled }) => (
  <div className={`${styles.miniToggle} ${disabled ? styles.miniToggleDisabled : ""}`}>
    {["Y", "N"].map((opt) => {
      const full = opt === "Y" ? "Yes" : "No";
      return (
        <button
          key={opt}
          type="button"
          disabled={disabled}
          className={`${styles.miniBtn} ${value === full ? styles.miniBtnActive : ""}`}
          onClick={() => !disabled && onChange(full)}
        >
          {opt}
        </button>
      );
    })}
  </div>
);

const IndividualGroupsForm = ({ individualGroups, setIndividualGroups }) => {
  const updateGroup = (groupName, field, value) => {
    setIndividualGroups(prev => ({
      ...prev,
      [groupName]: { ...prev[groupName], [field]: value }
    }));
  };

  const groups = ["group 0", "group 1", "group 2a", "group 2b", "group 3"];

  return (
    <div className={styles.compactGroupTable}>
      <div className={styles.sectionLabel}>Individual Group Reporting</div>
      <div className={styles.groupTableGrid}>
        <div className={styles.groupTableHeader}>
          <span>Group</span>
          <span>Held</span>
          <span>Smruti</span>
          <span>Mukhpath</span>
          <span>Prep</span>
        </div>
        {groups.map(groupName => {
          const held = individualGroups[groupName]?.held || "No";
          const inactive = held !== "Yes";
          return (
            <div key={groupName} className={styles.groupTableRow}>
              <span className={styles.groupTableLabel}>
                {groupName.split(' ')[1].toUpperCase()}
              </span>
              <MiniYesNo value={held} onChange={(v) => updateGroup(groupName, 'held', v)} />
              <MiniYesNo
                value={individualGroups[groupName]?.smruti_time || "No"}
                onChange={(v) => updateGroup(groupName, 'smruti_time', v)}
                disabled={inactive}
              />
              <MiniYesNo
                value={individualGroups[groupName]?.mukhpath || "No"}
                onChange={(v) => updateGroup(groupName, 'mukhpath', v)}
                disabled={inactive}
              />
              <MiniYesNo
                value={individualGroups[groupName]?.prep_cycle || "No"}
                onChange={(v) => updateGroup(groupName, 'prep_cycle', v)}
                disabled={inactive}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

const BalMandalForm = ({
  date, setDate,
  day, setDay,
  sabhaHeld, setSabhaHeld,
  combinedGroups, setCombinedGroups,
  smrutiTime, setSmrutiTime,
  mukhpath, setMukhpath,
  prepCycleDone, setPrepCycleDone,
  individualGroups, setIndividualGroups,
  captchaSeconds, setCaptchaSeconds,
  loading, runBot,
  logs, countdown,
}) => {
  const sundays = getValidSundays();
  const logEndRef = useRef(null);
  const [customDateInput, setCustomDateInput] = useState("");
  const [customDateError, setCustomDateError] = useState("");

  const handleCustomDateChange = (val) => {
    setCustomDateInput(val);
    setCustomDateError("");
  };

  const handleCustomDateBlur = () => {
    const val = customDateInput.trim();
    if (!val) return;
    const match = val.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!match) {
      setCustomDateError("Use YYYY-MM-DD format (e.g. 2026-03-09)");
      return;
    }
    const parsed = new Date(`${val}T00:00:00`);
    if (isNaN(parsed.getTime())) {
      setCustomDateError("Invalid date");
      return;
    }
    setDate(parsed);
  };

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className={styles.form}>

      <div className={styles.sectionLabel}>Date</div>
      <div className={styles.dateGrid}>
        {sundays.map(({ date: d, label }) => {
          const isSelected = date && date.toDateString() === d.toDateString();
          return (
            <button
              key={d.toDateString()}
              type="button"
              className={`${styles.dateTile} ${isSelected ? styles.dateTileActive : ""}`}
              onClick={() => { setDate(d); setCustomDateInput(""); setCustomDateError(""); }}
            >
              <span className={styles.dateLabel}>{label}</span>
              <span className={styles.dateValue}>
                {d.toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </button>
          );
        })}
      </div>

      <div className={styles.customDateWrapper}>
        <input
          type="text"
          placeholder="Or enter a past date: YYYY-MM-DD"
          className={`${styles.numberInput} ${customDateError ? styles.inputError : ""}`}
          value={customDateInput}
          onChange={(e) => handleCustomDateChange(e.target.value)}
          onBlur={handleCustomDateBlur}
          disabled={loading}
        />
        {customDateError && (
          <div className={styles.inputErrorMsg}>{customDateError}</div>
        )}
        {customDateInput.trim() && !customDateError && date && (
          <div className={styles.inputHint}>
            Selected: {date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" })}
          </div>
        )}
      </div>

      <div className={styles.sectionLabel}>Sabha Day</div>
      <div className={styles.toggle}>
        {["Saturday", "Sunday"].map((opt) => (
          <button
            key={opt}
            className={`${styles.toggleBtn} ${day === opt ? styles.toggleBtnActive : ""}`}
            onClick={() => setDay(opt)}
            type="button"
          >
            {opt}
          </button>
        ))}
      </div>

      <div className={styles.sectionLabel}>Was Sabha Held?</div>
      <YesNo value={sabhaHeld} onChange={setSabhaHeld} />

      {sabhaHeld === CONSTANTS.YES && (
        <>
          <div className={styles.sectionLabel}>Combined Groups Reporting?</div>
          <YesNo value={combinedGroups} onChange={setCombinedGroups} />

          {combinedGroups === CONSTANTS.YES && (
            <>
              <div className={styles.sectionLabel}>Activities</div>
              <div className={styles.activitiesGrid}>
                <div className={styles.activityItem}>
                  <span className={styles.activityLabel}>Smruti Time</span>
                  <YesNo value={smrutiTime} onChange={setSmrutiTime} />
                </div>
                <div className={styles.activityItem}>
                  <span className={styles.activityLabel}>Mukhpath</span>
                  <YesNo value={mukhpath} onChange={setMukhpath} />
                </div>
                <div className={styles.activityItem}>
                  <span className={styles.activityLabel}>Prep Cycle</span>
                  <YesNo value={prepCycleDone} onChange={setPrepCycleDone} />
                </div>
              </div>
            </>
          )}

          {combinedGroups === CONSTANTS.NO && (
            <IndividualGroupsForm 
              individualGroups={individualGroups} 
              setIndividualGroups={setIndividualGroups} 
            />
          )}

          <div className={styles.sectionLabel}>CAPTCHA Time (seconds)</div>
          <input
            type="number"
            min="1"
            max="300"
            step="1"
            className={styles.numberInput}
            value={captchaSeconds}
            onChange={(e) => setCaptchaSeconds(e.target.value)}
            disabled={loading}
          />
        </>
      )}

      <Button
        onClick={runBot}
        disabled={loading || !date || !day || !sabhaHeld}
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

export default BalMandalForm;
