import Button from "../Button/Button";
import AttendanceAlerts from "../AttendanceAlerts/AttendanceAlerts";
import styles from "./AttendanceForm.module.css";
import { CONSTANTS } from "../../utils/CONSTANTS";

const GROUPS = [
  { value: CONSTANTS.SATURDAY_K1, label: "Saturday", sub: "K1" },
  { value: CONSTANTS.SATURDAY_K2, label: "Saturday", sub: "K2" },
  { value: CONSTANTS.SUNDAY_K1,   label: "Sunday",   sub: "K1" },
  { value: CONSTANTS.SUNDAY_K2,   label: "Sunday",   sub: "K2" },
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

const AttendanceForm = ({
  date, setDate,
  group, setGroup,
  sabhaHeld, setSabhaHeld,
  p2Guju, setP2Guju,
  prepCycleDone, setPrepCycleDone,
  status, loading, runBot,
  markedPresent, notMarked, notFoundInBkms, sabhaHeldResult,
}) => {
  const sundays = getValidSundays();

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
              onClick={() => setDate(d)}
            >
              <span className={styles.dateLabel}>{label}</span>
              <span className={styles.dateValue}>
                {d.toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </button>
          );
        })}
      </div>

      <div className={styles.sectionLabel}>Sabha Group</div>
      <div className={styles.groupGrid}>
        {GROUPS.map((g) => (
          <button
            key={g.value}
            type="button"
            className={`${styles.groupTile} ${group === g.value ? styles.groupTileActive : ""}`}
            onClick={() => setGroup(g.value)}
          >
            <span className={styles.groupDay}>{g.label}</span>
            <span className={styles.groupSub}>{g.sub}</span>
          </button>
        ))}
      </div>

      <div className={styles.sectionLabel}>Was Sabha Held?</div>
      <YesNo value={sabhaHeld} onChange={setSabhaHeld} />

      {sabhaHeld === CONSTANTS.YES && (
        <>
          <div className={styles.sectionLabel}>Was P2 in Guju?</div>
          <YesNo value={p2Guju} onChange={setP2Guju} />

          <div className={styles.sectionLabel}>2 Week Prep Cycle Done?</div>
          <YesNo value={prepCycleDone} onChange={setPrepCycleDone} />
        </>
      )}

      <Button
        onClick={runBot}
        disabled={
          loading ||
          !date || !group || !sabhaHeld ||
          (sabhaHeld === CONSTANTS.YES && (!p2Guju || !prepCycleDone))
        }
        variant="contained"
      >
        {loading ? CONSTANTS.RUNNING : CONSTANTS.RUN_BOT}
      </Button>

      <AttendanceAlerts
        status={status}
        markedPresent={markedPresent}
        notMarked={notMarked}
        notFoundInBkms={notFoundInBkms}
        sabhaHeldResult={sabhaHeldResult}
        styles={styles}
        CONSTANTS={CONSTANTS}
      />
    </div>
  );
};

export default AttendanceForm;
