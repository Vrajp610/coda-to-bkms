import CustomAlert from "../CustomAlert/CustomAlert";

/** * AttendanceAlerts component for displaying attendance-related alerts.
 * It shows different alerts based on the attendance status,
 * including success, error, and informational messages.
 * @param {Object} props - Component properties.
 * @param {string} props.status - Status message to display.
 * @param {number} props.markedPresent - Number of kishores marked present.
 * @param {number} props.notMarked - Number of kishores not marked.
 * @param {number} props.notFoundInBkms - Number of kishores not found in BKMS.
 * @param {Object} props.styles - Styles object for custom styling.
 * @param {Object} props.CONSTANTS - Constants object containing messages.
 */
const AttendanceAlerts = ({
  status,
  markedPresent,
  notMarked,
  notFoundInBkms,
  styles,
  CONSTANTS,
}) => (
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

    {notMarked !== null && (
      <CustomAlert severity="error" className={styles.notMarked}>
        {CONSTANTS.KISHORES_NOT_CLICKED} {notMarked}
      </CustomAlert>
    )}

    {notFoundInBkms !== null && (
      <CustomAlert severity="error" className={styles.notFoundInBkms}>
        {CONSTANTS.KISHORES_NOT_FOUND} {notFoundInBkms}
      </CustomAlert>
    )}
  </>
);

export default AttendanceAlerts;