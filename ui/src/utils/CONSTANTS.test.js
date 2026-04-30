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
    expect(CONSTANTS.ATTENDANCE_BOT).toBe("BKMS KM Attendance Bot");
    expect(CONSTANTS.VALID_EMAIL).toBe(process.env.REACT_APP_VALID_EMAIL);
    expect(CONSTANTS.VALID_PASSWORD).toBe(process.env.REACT_APP_VALID_PASSWORD);
    expect(CONSTANTS.CANCEL).toBe("Cancel");
    expect(CONSTANTS.SIGN_IN).toBe("Sign In");
    expect(CONSTANTS.PASSWORD).toBe("Password");
    expect(CONSTANTS.EMAIL).toBe("Email");
    expect(CONSTANTS.CODA_ATTENDANCE_MISSING).toBe("Coda attendance is currently missing. Please ensure it’s filled out before proceeding further.");
    expect(CONSTANTS.SABHA_NOT_HELD).toBe("Sabha was not held. Attendance marked accordingly in BKMS.");
    expect(CONSTANTS.GOSHTHI_BOT).toBe("BKMS Goshthi Bot");
    expect(CONSTANTS.WAS_GOSHTHI_HELD).toBe("Was Goshthi Held?");
    expect(CONSTANTS.WAS_HANGOUT).toBe("Was this a Hangout?");
    expect(CONSTANTS.WAS_WORKSHOP).toBe("Was a Karyakar Workshop Held?");
    expect(CONSTANTS.BAL_MANDAL_BOT).toBe("BKMS BM Attendance Bot");
    expect(CONSTANTS.SATURDAY_BAL_GROUP_0).toBe("Saturday Bal Group 0");
    expect(CONSTANTS.SATURDAY_BAL_GROUP_1).toBe("Saturday Bal Group 1");
    expect(CONSTANTS.SATURDAY_BAL_GROUP_2A).toBe("Saturday Bal Group 2A");
    expect(CONSTANTS.SATURDAY_BAL_GROUP_2B).toBe("Saturday Bal Group 2B");
    expect(CONSTANTS.SATURDAY_BAL_GROUP_3).toBe("Saturday Bal Group 3");
    expect(CONSTANTS.SUNDAY_BAL_GROUP_0).toBe("Sunday Bal Group 0");
    expect(CONSTANTS.SUNDAY_BAL_GROUP_1).toBe("Sunday Bal Group 1");
    expect(CONSTANTS.SUNDAY_BAL_GROUP_2A).toBe("Sunday Bal Group 2A");
    expect(CONSTANTS.SUNDAY_BAL_GROUP_2B).toBe("Sunday Bal Group 2B");
    expect(CONSTANTS.SUNDAY_BAL_GROUP_3).toBe("Sunday Bal Group 3");
  });

  it('should not have unexpected keys', () => {
    const expectedKeys = [
      "KISHORES_CLICKED", "KISHORES_NOT_CLICKED", "KISHORES_NOT_FOUND", "SELECT_A_VALID_SUNDAY",
      "SATURDAY_K1", "SATURDAY_K2", "SUNDAY_K1", "SUNDAY_K2", "SELECT_GROUP",
      "YES", "NO", "WAS_SABHA_HELD", "WAS_P2_IN_GUJU", "PREP_CYCLE_DONE", "RUNNING", "RUN_BOT",
      "REQUIRED_FIELDS", "LONG", "NUMERIC", "SOMETHING_WENT_WRONG", "ATTENDANCE_BOT",
      "VALID_EMAIL", "VALID_PASSWORD", "CANCEL", "SIGN_IN", "PASSWORD", "EMAIL",
      "CODA_ATTENDANCE_MISSING", "SABHA_NOT_HELD",
      "GOSHTHI_BOT", "WAS_GOSHTHI_HELD", "WAS_HANGOUT", "WAS_WORKSHOP",
      "BAL_MANDAL_BOT",
      "SATURDAY_BAL_GROUP_0", "SATURDAY_BAL_GROUP_1", "SATURDAY_BAL_GROUP_2A",
      "SATURDAY_BAL_GROUP_2B", "SATURDAY_BAL_GROUP_3",
      "SUNDAY_BAL_GROUP_0", "SUNDAY_BAL_GROUP_1", "SUNDAY_BAL_GROUP_2A",
      "SUNDAY_BAL_GROUP_2B", "SUNDAY_BAL_GROUP_3",
    ];
    expect(Object.keys(CONSTANTS).sort()).toEqual(expectedKeys.sort());
  });
});
