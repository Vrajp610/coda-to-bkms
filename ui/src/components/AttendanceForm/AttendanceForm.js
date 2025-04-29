import React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styles from "./AttendanceForm.module.css";
import { filterValidSundays, getStatusColor } from "../../utils/functions";
import SelectField from "../SelectField/SelectField";
import Button from "../Button/Button";

const AttendanceForm = ({
  date,
  setDate,
  group,
  setGroup,
  sabhaHeld,
  setSabhaHeld,
  p2Guju,
  setP2Guju,
  prepCycleDone,
  setPrepCycleDone,
  status,
  loading,
  runBot,
}) => {
  return (
    <div className={styles.form}>
      <DatePicker
        selected={date}
        onChange={(selected) => setDate(selected)}
        filterDate={filterValidSundays}
        placeholderText="Select a valid Sunday"
        dateFormat="MMMM d"
        className={styles.input}
      />

      <SelectField
        value={group}
        onChange={(e) => setGroup(e.target.value)}
        options={[
          { value: "Saturday K1", label: "Saturday K1" },
          { value: "Saturday K2", label: "Saturday K2" },
          { value: "Sunday K1", label: "Sunday K1" },
          { value: "Sunday K2", label: "Sunday K2" },
        ]}
        placeholder="Select Group"
        ariaLabel="Select Group"
      />

      <SelectField
        value={sabhaHeld}
        onChange={(e) => setSabhaHeld(e.target.value)}
        options={[
          { value: "Yes", label: "Yes" },
          { value: "No", label: "No" },
        ]}
        placeholder="Was Sabha Held?"
        ariaLabel="Was Sabha Held?"
      />

      {sabhaHeld === "Yes" && (
        <>
          <SelectField
            value={p2Guju}
            onChange={(e) => setP2Guju(e.target.value)}
            options={[
              { value: "Yes", label: "Yes" },
              { value: "No", label: "No" },
            ]}
            placeholder="Was P2 in Guju?"
          />

          <SelectField
            value={prepCycleDone}
            onChange={(e) => setPrepCycleDone(e.target.value)}
            options={[
              { value: "Yes", label: "Yes" },
              { value: "No", label: "No" },
            ]}
            placeholder="2 Week Prep Cycle Done?"
          />
        </>
      )}

      <Button
        onClick={runBot}
        disabled={
          loading ||
          !date ||
          !group ||
          !sabhaHeld ||
          (sabhaHeld === "Yes" && (!p2Guju || !prepCycleDone))
        }
      >
        {loading ? "Running..." : "Run Bot"}
      </Button>

      {status && (
        <p className={styles.status} style={{ color: getStatusColor(status) }}>
          {status}
        </p>
      )}
    </div>
  );
};

export default AttendanceForm;