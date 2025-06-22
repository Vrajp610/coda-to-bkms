import { Button as MUIButton } from "@mui/material";

const Button = ({ onClick, disabled, className, children }) => {
  return (
    <MUIButton
      onClick={onClick}
      disabled={disabled}
      className={className}
      variant="contained"
    >
      {children}
    </MUIButton>
  );
};

export default Button;