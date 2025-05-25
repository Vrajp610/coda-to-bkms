import React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styles from "./AttendanceForm.module.css";
import { filterValidSundays, getStatusColor } from "../../utils/functions";
import SelectField from "../SelectField/SelectField";
import Button from "../Button/Button";
import { CONSTANTS } from "../../utils/CONSTANTS";

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
  markedPresent,
  notMarked,
  notFoundInBkms,
}) => {
  return (
    <div className={styles.form}>
      <DatePicker
        selected={date}
        onChange={(selected) => setDate(selected)}
        filterDate={filterValidSundays}
        placeholderText={CONSTANTS.SELECT_A_VALID_SUNDAY}
        dateFormat={CONSTANTS.DATE_FORMAT}
        className={styles.input}
      />

      <SelectField
        value={group}
        onChange={(e) => setGroup(e.target.value)}
        options={[
          { value: CONSTANTS.SATURDAY_K1, label: CONSTANTS.SATURDAY_K1 },
          { value: CONSTANTS.SATURDAY_K2, label: CONSTANTS.SATURDAY_K2 },
          { value: CONSTANTS.SUNDAY_K1, label: CONSTANTS.SUNDAY_K1 },
          { value: CONSTANTS.SUNDAY_K2, label: CONSTANTS.SUNDAY_K2 },
        ]}
        placeholder={CONSTANTS.SELECT_GROUP}
        ariaLabel={CONSTANTS.SELECT_GROUP}
      />

      <SelectField
        value={sabhaHeld}
        onChange={(e) => setSabhaHeld(e.target.value)}
        options={[
          { value: CONSTANTS.YES, label: CONSTANTS.YES },
          { value: CONSTANTS.NO, label: CONSTANTS.NO },
        ]}
        placeholder={CONSTANTS.WAS_SABHA_HELD}
        ariaLabel={CONSTANTS.WAS_SABHA_HELD}
      />

      {sabhaHeld === CONSTANTS.YES && (
        <>
          <SelectField
            value={p2Guju}
            onChange={(e) => setP2Guju(e.target.value)}
            options={[
              { value: CONSTANTS.YES, label: CONSTANTS.YES },
              { value: CONSTANTS.NO, label: CONSTANTS.NO },
            ]}
            placeholder={CONSTANTS.WAS_P2_IN_GUJU}
            ariaLabel={CONSTANTS.WAS_P2_IN_GUJU}
          />

          <SelectField
            value={prepCycleDone}
            onChange={(e) => setPrepCycleDone(e.target.value)}
            options={[
              { value: CONSTANTS.YES, label: CONSTANTS.YES },
              { value: CONSTANTS.NO, label: CONSTANTS.NO },
            ]}
            placeholder={CONSTANTS.PREP_CYCLE_DONE}
            ariaLabel={CONSTANTS.PREP_CYCLE_DONE}
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
          (sabhaHeld === CONSTANTS.YES && (!p2Guju || !prepCycleDone))
        }
      >
        {loading ? CONSTANTS.RUNNING : CONSTANTS.RUN_BOT}
      </Button>

      {status && (
        <p className={styles.status}>
          {status}
        </p>
      )}
  
      {markedPresent !== null && (
        <p className={styles.markedPresent}>
          {CONSTANTS.KISHORES_CLICKED} {markedPresent}
        </p>
      )}

      {notMarked !== null && (
        <p className={styles.notMarked}>
         {CONSTANTS.KISHORES_NOT_CLICKED} {notMarked}
        </p>
      )}

      {notFoundInBkms !== null && (
        <p className={styles.notFoundInBkms}>
          {CONSTANTS.KISHORES_NOT_FOUND} {notFoundInBkms}
        </p>
      )}
    </div>
  );
};

export default AttendanceForm;