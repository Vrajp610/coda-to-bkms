import CustomAlert from "../CustomAlert/CustomAlert";

/** * AttendanceAlerts component for displaying attendance-related alerts.
 * It shows different alerts based on the attendance status,
 * including success, error, and informational messages.
 * @param {Object} props - Component properties.
 * @param {string} props.status - Status message to display.
 * @param {number} props.markedPresent - Number of kishores marked present.
 * @param {number} props.notMarked - Number of kishores not marked.
 * @param {number} props.notFoundInBkms - Number of kishores not found in BKMS.
 * @param {boolean} props.sabhaHeldResult - Whether sabha was actually held (from backend).
 * @param {Object} props.styles - Styles object for custom styling.
 * @param {Object} props.CONSTANTS - Constants object containing messages.
 */
const AttendanceAlerts = ({
  status,
  markedPresent,
  notMarked,
  notFoundInBkms,
  sabhaHeldResult,
  styles,
  CONSTANTS,
}) => (
  <>
    {markedPresent === 0 && sabhaHeldResult === false ? (
      <CustomAlert severity="success" className={styles.markedPresent}>
        {CONSTANTS.SABHA_NOT_HELD}
      </CustomAlert>
    ) : markedPresent === 0 ? (
      <CustomAlert severity="error" className={styles.markedPresent}>
        {CONSTANTS.CODA_ATTENDANCE_MISSING}
      </CustomAlert>
    ) : (
      <>
        {status && (
          <CustomAlert severity="info" className={styles.status}>
            {status}
          </CustomAlert>
        )}

        {markedPresent !== null && (
          <CustomAlert severity="success" className={styles.markedPresent}>
            {CONSTANTS.KISHORES_CLICKED} {markedPresent}
          </CustomAlert>
        )}

        {notMarked !== null && notMarked > 0 && (
          <CustomAlert severity="error" className={styles.notMarked}>
            {CONSTANTS.KISHORES_NOT_CLICKED} {notMarked}
          </CustomAlert>
        )}

        {notFoundInBkms !== null && notFoundInBkms.length > 0 && (
          <CustomAlert severity="error" className={styles.notFoundInBkms}>
            {CONSTANTS.KISHORES_NOT_FOUND} {notFoundInBkms.join(", ")}
          </CustomAlert>
        )}
      </>
    )}
  </>
);

export default AttendanceAlerts;