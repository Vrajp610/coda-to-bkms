import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

/** * DatePickerField component for rendering a date picker input.
 * @param {Object} props - Component properties.
 * @param {string} props.label - Label for the date picker.
 * @param {Date} props.value - Current value of the date picker.
 * @param {Function} props.onChange - Function to call when the date changes.
 * @param {Function} [props.shouldDisableDate] - Function to disable specific dates.
 * @param {Object} [props.slotProps] - Additional slot properties for customization.
 */
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