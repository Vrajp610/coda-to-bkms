import styles from "./AttendanceForm.module.css";
import { filterValidSundays } from "../../utils/functions";
import SelectField from "../SelectField/SelectField";
import Button from "../Button/Button";
import { CONSTANTS } from "../../utils/CONSTANTS";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AttendanceAlerts from "../AttendanceAlerts/AttendanceAlerts";

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
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <DatePicker
          label={CONSTANTS.SELECT_A_VALID_SUNDAY}
          value={date}
          onChange={(selected) => setDate(selected)}
          shouldDisableDate={(date) => !filterValidSundays(date)}
          slotProps={{ textField: { className: styles.input } }}
        />
      </LocalizationProvider>

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

      <AttendanceAlerts
        status={status}
        markedPresent={markedPresent}
        notMarked={notMarked}
        notFoundInBkms={notFoundInBkms}
        styles={styles}
        CONSTANTS={CONSTANTS}
      />
    </div>
  );
};

export default AttendanceForm;