import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const DatePickerField = ({ label, value, onChange, shouldDisableDate, slotProps }) => (
  <LocalizationProvider dateAdapter={AdapterDateFns}>
    <DatePicker
      label={label}
      value={value}
      onChange={onChange}
      shouldDisableDate={shouldDisableDate}
      slotProps={slotProps}
    />
  </LocalizationProvider>
);

export default DatePickerField;