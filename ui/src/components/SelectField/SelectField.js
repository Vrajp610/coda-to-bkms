import { FormControl, InputLabel, MenuItem, Select} from "@mui/material";

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