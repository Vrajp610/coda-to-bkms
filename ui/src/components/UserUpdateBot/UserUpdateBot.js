import { useState, useRef, useEffect } from "react";
import Button from "../Button/Button";
import styles from "./UserUpdateBot.module.css";

const API_BASE_URL = process.env.REACT_APP_API_URL;

const UserUpdateBot = () => {
  const [rawInput, setRawInput] = useState("");
  const [logs, setLogs] = useState([]);
  const [running, setRunning] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const runBot = () => {
    const userIds = rawInput
      .split("\n")
      .map((id) => id.trim())
      .filter(Boolean);

    if (userIds.length === 0) {
      window.alert("Please enter at least one User ID.");
      return;
    }

    setLogs([]);
    setCountdown(null);
    setRunning(true);

    const eventSource = new EventSource(
      `${API_BASE_URL}/run-user-update-stream?dummy=1`
    );

    // SSE requires GET; use fetch with POST + ReadableStream instead
    eventSource.close();

    fetch(`${API_BASE_URL}/run-user-update-stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_ids: userIds }),
    }).then(async (response) => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const msg = line.slice(6);

          if (msg === "__DONE__") {
            setRunning(false);
            setCountdown(null);
            return;
          }

          if (msg.startsWith("__COUNTDOWN__")) {
            const secs = parseInt(msg.replace("__COUNTDOWN__", ""), 10);
            setCountdown(secs);
          } else {
            setCountdown(null);
            setLogs((prev) => [...prev, msg]);
          }
        }
      }

      setRunning(false);
      setCountdown(null);
    }).catch((err) => {
      setLogs((prev) => [...prev, `Connection error: ${err.message}`]);
      setRunning(false);
      setCountdown(null);
    });
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>User Update Bot</h1>
      <div className={styles.card}>
        <label className={styles.label}>User IDs (one per line)</label>
        <textarea
          className={styles.textarea}
          value={rawInput}
          onChange={(e) => setRawInput(e.target.value)}
          placeholder={"19477\n19478\n63040"}
          rows={6}
          disabled={running}
        />

        <Button onClick={runBot} disabled={running} variant="contained">
          {running ? "Running..." : "Run Bot"}
        </Button>

        {running && countdown !== null && (
          <div className={styles.countdown}>
            Waiting for login — {countdown}s remaining
          </div>
        )}

        {(logs.length > 0 || running) && (
          <div className={styles.logBox}>
            {logs.map((line, i) => (
              <div
                key={i}
                className={
                  line.includes("ERROR")
                    ? styles.logError
                    : line.startsWith("---")
                    ? styles.logHeader
                    : styles.logLine
                }
              >
                {line}
              </div>
            ))}
            {running && countdown === null && (
              <div className={styles.logLine}>...</div>
            )}
            <div ref={logEndRef} />
          </div>
        )}
      </div>
    </div>
  );
};

export default UserUpdateBot;
