import React from "react";
import styles from "./Button.module.css";

const Button = ({ onClick, disabled, className, children }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${styles.button} ${disabled ? styles.buttonDisabled : ""} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;