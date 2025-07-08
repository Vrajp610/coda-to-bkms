import { Button as MUIButton } from "@mui/material";

/** * Button component for rendering a Material-UI button.
 * @param {Object} props - Component properties.
 * @param {Function} props.onClick - Function to call when the button is clicked.
 * @param {boolean} props.disabled - Whether the button is disabled.
 * @param {string} [props.className] - Additional CSS class for styling.
 * @param {ReactNode} props.children - Content to display inside the button.
 */
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