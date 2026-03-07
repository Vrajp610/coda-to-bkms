import { useState } from "react";
import { Tabs, Tab, Box, CssBaseline } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import AttendanceBot from "./components/AttendanceBot/AttendanceBot";
import UserUpdateBot from "./components/UserUpdateBot/UserUpdateBot";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#c2622a" },
    background: {
      default: "#0a0e27",
      paper: "#1e2a3a",
    },
    text: {
      primary: "#f1f5f9",
      secondary: "#94a3b8",
    },
  },
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: "rgba(255,255,255,0.06)",
          borderRadius: "8px",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(255,255,255,0.12)",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(249,115,22,0.5)",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "#c2622a",
          },
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: "#94a3b8",
          "&.Mui-focused": { color: "#c2622a" },
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          color: "#f1f5f9",
          "&:hover": { backgroundColor: "rgba(249,115,22,0.15)" },
          "&.Mui-selected": { backgroundColor: "rgba(249,115,22,0.25)" },
          "&.Mui-selected:hover": { backgroundColor: "rgba(249,115,22,0.35)" },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        standardSuccess: {
          backgroundColor: "rgba(52,211,153,0.1)",
          border: "1px solid rgba(52,211,153,0.3)",
          color: "#34d399",
          "& .MuiAlert-icon": { color: "#34d399" },
        },
        standardError: {
          backgroundColor: "rgba(248,113,113,0.1)",
          border: "1px solid rgba(248,113,113,0.3)",
          color: "#f87171",
          "& .MuiAlert-icon": { color: "#f87171" },
        },
        standardInfo: {
          backgroundColor: "rgba(56,189,248,0.1)",
          border: "1px solid rgba(56,189,248,0.3)",
          color: "#38bdf8",
          "& .MuiAlert-icon": { color: "#38bdf8" },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        contained: {
          background: "linear-gradient(135deg, #c2622a, #a8521f)",
          color: "#fff",
          fontWeight: 600,
          borderRadius: "8px",
          textTransform: "none",
          fontSize: "15px",
          "&:hover": { background: "linear-gradient(135deg, #c2622a, #c2622a)", boxShadow: "0 4px 15px rgba(249,115,22,0.4)" },
          "&.Mui-disabled": { background: "rgba(255,255,255,0.08)", color: "#475569" },
        },
      },
    },
  },
});

function App() {
  const [tab, setTab] = useState(0);

  return (
    <ThemeProvider theme={darkTheme}>
    <CssBaseline />
    <Box sx={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0e27 0%, #111827 60%, #0d1117 100%)",
      paddingTop: "32px",
      paddingBottom: "40px",
    }}>
      <Box sx={{ display: "flex", justifyContent: "center", marginBottom: "24px" }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          sx={{
            background: "rgba(255,255,255,0.05)",
            borderRadius: "10px",
            padding: "4px",
            border: "1px solid rgba(255,255,255,0.08)",
            "& .MuiTab-root": {
              color: "#94a3b8",
              fontWeight: 600,
              fontSize: "0.95rem",
              textTransform: "none",
              minWidth: 160,
              transition: "color 0.2s",
            },
            "& .Mui-selected": { color: "#c2622a !important" },
            "& .MuiTabs-indicator": { backgroundColor: "#c2622a", height: "3px", borderRadius: "2px" },
          }}
        >
          <Tab label="Attendance Bot" />
          <Tab label="User Update Bot" />
        </Tabs>
      </Box>
      {tab === 0 && <AttendanceBot />}
      {tab === 1 && <UserUpdateBot />}
    </Box>
    </ThemeProvider>
  );
}

export default App;