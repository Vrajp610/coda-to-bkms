import { FormControl, InputLabel, MenuItem, Select} from "@mui/material";

/** * SelectField component for rendering a dropdown select input.
 * @param {Object} props - Component properties.
 * @param {string} props.value - The current value of the select field.
 * @param {Function} props.onChange - Function to call when the value changes.
 * @param {Array} props.options - Array of options for the select field, each with a 'value' and 'label'.
 * @param {string} props.placeholder - Placeholder text for the select field.
 * @param {string} props.ariaLabel - Aria label for accessibility.
 */
const SelectField = ({ value, onChange, options, placeholder, ariaLabel }) => {
  return (
    <FormControl fullWidth>
      <InputLabel id={`${ariaLabel}-label`}>{placeholder}</InputLabel>
      <Select
        labelId={`${ariaLabel}-label`}
        value={value}
        label={placeholder}
        onChange={onChange}
      >
        <MenuItem value="">
          <em>{placeholder}</em>
        </MenuItem>
        {options.map((option, index) => (
          <MenuItem key={index} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default SelectField;