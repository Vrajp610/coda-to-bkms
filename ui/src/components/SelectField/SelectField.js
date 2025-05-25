import styles from "./SelectField.module.css";

const SelectField = ({ value, onChange, options, placeholder, ariaLabel }) => {
  return (
    <select
      value={value}
      onChange={onChange}
      className={styles.select}
      aria-label={ariaLabel}
    >
      <option value="">{placeholder}</option>
      {options.map((option, index) => (
        <option key={index} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
};

export default SelectField;