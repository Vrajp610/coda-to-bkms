import { CONSTANTS } from './CONSTANTS';

describe('CONSTANTS', () => {
  it('should have all required keys with correct values', () => {
    expect(CONSTANTS.KISHORES_CLICKED).toBe("Kishores clicked in BKMS:");
    expect(CONSTANTS.KISHORES_NOT_CLICKED).toBe("Kishores not clicked in BKMS:");
    expect(CONSTANTS.KISHORES_NOT_FOUND).toBe("Kishores not found in BKMS:");
    expect(CONSTANTS.SELECT_A_VALID_SUNDAY).toBe("Select a valid Sunday");
    expect(CONSTANTS.SATURDAY_K1).toBe("Saturday K1");
    expect(CONSTANTS.SATURDAY_K2).toBe("Saturday K2");
    expect(CONSTANTS.SUNDAY_K1).toBe("Sunday K1");
    expect(CONSTANTS.SUNDAY_K2).toBe("Sunday K2");
    expect(CONSTANTS.SELECT_GROUP).toBe("Select Group");
    expect(CONSTANTS.YES).toBe("Yes");
    expect(CONSTANTS.NO).toBe("No");
    expect(CONSTANTS.WAS_SABHA_HELD).toBe("Was Sabha Held?");
    expect(CONSTANTS.WAS_P2_IN_GUJU).toBe("Was P2 in Guju?");
    expect(CONSTANTS.PREP_CYCLE_DONE).toBe("2 Week Prep Cycle Done?");
    expect(CONSTANTS.RUNNING).toBe("Running...");
    expect(CONSTANTS.RUN_BOT).toBe("Run Bot");
    expect(CONSTANTS.REQUIRED_FIELDS).toBe("Please fill out all required fields before running the bot.");
    expect(CONSTANTS.LONG).toBe("long");
    expect(CONSTANTS.NUMERIC).toBe("numeric");
    expect(CONSTANTS.SOMETHING_WENT_WRONG).toBe("Something went wrong!");
    expect(CONSTANTS.ATTENDANCE_BOT).toBe("BKMS Attendance Bot");
    expect(CONSTANTS.VALID_EMAIL).toBe(process.env.REACT_APP_VALID_EMAIL);
    expect(CONSTANTS.VALID_PASSWORD).toBe(process.env.REACT_APP_VALID_PASSWORD);
    expect(CONSTANTS.CANCEL).toBe("Cancel");
    expect(CONSTANTS.SIGN_IN).toBe("Sign In");
    expect(CONSTANTS.PASSWORD).toBe("Password");
    expect(CONSTANTS.EMAIL).toBe("Email");
    expect(CONSTANTS.CODA_ATTENDANCE_MISSING).toBe("Coda attendance is currently missing. Please ensure it’s filled out before proceeding further.");
  });

  it('should not have unexpected keys', () => {
    const expectedKeys = [
      "KISHORES_CLICKED", "KISHORES_NOT_CLICKED", "KISHORES_NOT_FOUND", "SELECT_A_VALID_SUNDAY",
      "SATURDAY_K1", "SATURDAY_K2", "SUNDAY_K1", "SUNDAY_K2", "SELECT_GROUP",
      "YES", "NO", "WAS_SABHA_HELD", "WAS_P2_IN_GUJU", "PREP_CYCLE_DONE", "RUNNING", "RUN_BOT",
      "REQUIRED_FIELDS", "LONG", "NUMERIC", "SOMETHING_WENT_WRONG", "ATTENDANCE_BOT",
      "VALID_EMAIL", "VALID_PASSWORD", "CANCEL", "SIGN_IN", "PASSWORD", "EMAIL", "CODA_ATTENDANCE_MISSING"
    ];
    expect(Object.keys(CONSTANTS).sort()).toEqual(expectedKeys.sort());
  });
});