import SelectField from "../SelectField/SelectField";
import Button from "../Button/Button";
import DatePickerField from "../DatePickerField/DatePickerField";
import AttendanceAlerts from "../AttendanceAlerts/AttendanceAlerts";
import SignInModal from "../SignInModal/SignInModal";
import styles from "./AttendanceForm.module.css";
import { filterValidSundays } from "../../utils/functions";
import { CONSTANTS } from "../../utils/CONSTANTS";

/** AttendanceForm component for managing attendance inputs and actions.
 * @param {Object} props - Component properties.
 * @param {Date} props.date - Selected date for attendance.
 * @param {Function} props.setDate - Function to update the selected date.
 * @param {string} props.group - Selected group for attendance.
 * @param {Function} props.setGroup - Function to update the selected group.
 * @param {string} props.sabhaHeld - Indicates if the sabha was held.
 * @param {Function} props.setSabhaHeld - Function to update the sabha held status.
 * @param {string} props.p2Guju - Indicates if P2 was in Guju.
 * @param {Function} props.setP2Guju - Function to update the P2 Guju status.
 * @param {string} props.prepCycleDone - Indicates if the prep cycle was done.
 * @param {Function} props.setPrepCycleDone - Function to update the prep cycle status.
 * @param {string} props.status - Current status of the attendance bot.
 * @param {boolean} props.loading - Indicates if the bot is currently running.
 * @param {Function} props.runBot - Function to run the attendance bot.
 * @param {Array} props.markedPresent - List of members marked present.
 * @param {Array} props.notMarked - List of members not marked.
 * @param {Array} props.notFoundInBkms - List of members not found in BKMS.
 * @param {boolean} props.sabhaHeldResult - Indicates if sabha was actually held (from backend).
 * @param {boolean} props.signInOpen - Indicates if the sign-in modal is open.
 * @param {Function} props.setSignInOpen - Function to update the sign-in modal state.
 * @param {Function} props.handleSignInSuccess - Function to handle successful sign-in.
 */
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
  sabhaHeldResult,
  signInOpen,
  setSignInOpen,
  handleSignInSuccess,
}) => {
  return (
    <div className={styles.form}>
      <DatePickerField
        label={CONSTANTS.SELECT_A_VALID_SUNDAY}
        value={date}
        onChange={(selected) => setDate(selected)}
        shouldDisableDate={(date) => !filterValidSundays(date)}
        slotProps={{ textField: { className: styles.input } }}
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
      <SignInModal
        open={signInOpen}
        onClose={() => setSignInOpen(false)}
        onSuccess={handleSignInSuccess}
      />
    </div>
  );
};

export default AttendanceForm;