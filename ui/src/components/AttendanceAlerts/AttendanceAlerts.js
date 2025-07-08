import Alert from "@mui/material/Alert";

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
      <Alert severity="info" className={styles.status}>
        {status}
      </Alert>
    )}

    {markedPresent !== null && (
      <Alert severity="success" className={styles.markedPresent}>
        {CONSTANTS.KISHORES_CLICKED} {markedPresent}
      </Alert>
    )}

    {notMarked !== null && (
      <Alert severity="error" className={styles.notMarked}>
        {CONSTANTS.KISHORES_NOT_CLICKED} {notMarked}
      </Alert>
    )}

    {notFoundInBkms !== null && (
      <Alert severity="error" className={styles.notFoundInBkms}>
        {CONSTANTS.KISHORES_NOT_FOUND} {notFoundInBkms}
      </Alert>
    )}
  </>
);

export default AttendanceAlerts;