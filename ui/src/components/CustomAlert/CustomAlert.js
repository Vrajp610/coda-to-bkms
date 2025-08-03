import Alert from "@mui/material/Alert";

const CustomAlert = ({ severity, className, children }) => {
  return (
    <Alert severity={severity} className={className}>
      {children}
    </Alert>
  );
};

export default CustomAlert;
