import Alert from "@mui/material/Alert";

/** * CustomAlert component for rendering an alert message.
 * @param {Object} props - Component properties.
 * @param {string} props.severity - Severity level of the alert (e.g., "error", "warning", "info", "success").
 * @param {string} props.className - Additional CSS class names for styling.
 * @param {React.ReactNode} props.children - Content to display inside the alert.
 */

const CustomAlert = ({ severity, className, children }) => {
  return (
    <Alert severity={severity} className={className}>
      {children}
    </Alert>
  );
};

export default CustomAlert;
