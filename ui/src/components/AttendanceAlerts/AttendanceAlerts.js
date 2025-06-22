import Alert from "@mui/material/Alert";

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
