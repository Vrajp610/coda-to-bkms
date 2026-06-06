import * as coda from "@codahq/packs-sdk";

export const pack = coda.newPack();

// Each user installs the Pack with:
//   1. Endpoint URL: their own public ngrok URL, e.g. https://agitative-continuatively-rea.ngrok-free.dev
//   2. Token: the BOT_TRIGGER_TOKEN from their local backend/.env
pack.setUserAuthentication({
  type: coda.AuthenticationType.CustomHeaderToken,
  headerName: "X-Bkms-Token",
  requiresEndpointUrl: true,
  instructionsUrl:
    "https://github.com/your-repo/coda-to-bkms#setup",
});

function normalizeDateInput(input: string): string {
  if (/^\d{4}-\d{2}-\d{2}$/.test(input)) {
    return input;
  }

  const trimmed = input.trim();
  const withYear = /\b\d{4}\b/.test(trimmed)
    ? trimmed
    : `${trimmed}, ${new Date().getFullYear()}`;
  const parsed = new Date(withYear);

  if (Number.isNaN(parsed.getTime())) {
    throw new coda.UserVisibleError(
      `Could not parse the date "${input}". Use a real date like 2026-04-12.`,
    );
  }

  const year = parsed.getFullYear();
  const month = `${parsed.getMonth() + 1}`.padStart(2, "0");
  const day = `${parsed.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatIdList(label: string, value: unknown): string {
  if (!Array.isArray(value) || value.length === 0) {
    return "";
  }
  return `${label}: ${(value as string[]).join(", ")}`;
}

const AttendanceJobSchema = coda.makeObjectSchema({
  properties: {
    jobId: { type: coda.ValueType.String, fromKey: "jobId" },
    status: { type: coda.ValueType.String, fromKey: "status" },
    message: { type: coda.ValueType.String, fromKey: "message" },
    date: { type: coda.ValueType.String, fromKey: "date" },
    group: { type: coda.ValueType.String, fromKey: "group" },
    captchaSeconds: { type: coda.ValueType.Number, fromKey: "captchaSeconds" },
    attendanceCount: { type: coda.ValueType.Number, fromKey: "attendanceCount" },
    markedPresent: { type: coda.ValueType.Number, fromKey: "markedPresent" },
    notMarked: { type: coda.ValueType.Number, fromKey: "notMarked" },
    clickedIds: {
      type: coda.ValueType.Array,
      items: { type: coda.ValueType.String },
      fromKey: "clickedIds",
    },
    notClickedIds: {
      type: coda.ValueType.Array,
      items: { type: coda.ValueType.String },
      fromKey: "notClickedIds",
    },
    notFoundInBkms: {
      type: coda.ValueType.Array,
      items: { type: coda.ValueType.String },
      fromKey: "notFoundInBkms",
    },
    sabhaHeld: { type: coda.ValueType.Boolean, fromKey: "sabhaHeld" },
    error: { type: coda.ValueType.String, fromKey: "error" },
    createdAt: { type: coda.ValueType.String, fromKey: "createdAt" },
    updatedAt: { type: coda.ValueType.String, fromKey: "updatedAt" },
    completedAt: { type: coda.ValueType.String, fromKey: "completedAt" },
  },
  displayProperty: "message",
  idProperty: "jobId",
  featuredProperties: [
    "status",
    "group",
    "date",
    "captchaSeconds",
    "markedPresent",
    "notMarked",
    "clickedIds",
    "notClickedIds",
    "notFoundInBkms",
  ],
});

function normalizeAttendanceJob(data: Record<string, unknown>): Record<string, unknown> {
  if (data.error && !data.job_id) {
    throw new coda.UserVisibleError(String(data.error));
  }

  return {
    jobId: String(data.job_id ?? ""),
    status: String(data.status ?? "unknown"),
    message: String(data.message ?? ""),
    date: String(data.date ?? ""),
    group: String(data.group ?? ""),
    captchaSeconds:
      typeof data.captchaSeconds === "number"
        ? data.captchaSeconds
        : typeof data.captcha_seconds === "number"
        ? data.captcha_seconds
        : 20,
    attendanceCount:
      typeof data.attendance_count === "number" ? data.attendance_count : 0,
    markedPresent:
      typeof data.marked_present === "number" ? data.marked_present : 0,
    notMarked:
      typeof data.not_marked === "number" ? data.not_marked : 0,
    clickedIds: Array.isArray(data.marked_present_ids) ? data.marked_present_ids : [],
    notClickedIds: Array.isArray(data.not_marked_ids) ? data.not_marked_ids : [],
    notFoundInBkms: Array.isArray(data.not_found_in_bkms) ? data.not_found_in_bkms : [],
    sabhaHeld: Boolean(data.sabha_held),
    error: data.error ? String(data.error) : "",
    createdAt: String(data.created_at ?? ""),
    updatedAt: String(data.updated_at ?? ""),
    completedAt: String(data.completed_at ?? ""),
  };
}

function formatAttendanceJobResult(data: Record<string, unknown>): string {
  if (data.error) {
    throw new coda.UserVisibleError(String(data.error));
  }

  const status = String(data.status ?? "unknown");
  
  // For queued or running status, show job ID for polling
  if (status === "queued" || status === "running") {
    return [
      `Status: ${status}`,
      `Job ID: ${data.job_id}`,
      String(data.message ?? "Check status using GetBalMandalJob(\"${data.job_id}\")"),
    ]
      .filter(Boolean)
      .join(" | ");
  }

  const prefix = `Status: ${status}`;

  if (status !== "completed") {
    return [prefix, String(data.message ?? "Attendance job is still running."), data.job_id ? `Job ID: ${data.job_id}` : ""]
      .filter(Boolean)
      .join(" | ");
  }

  const notFound = Array.isArray(data.not_found_in_bkms)
    ? (data.not_found_in_bkms as string[]).join(", ")
    : "";

  return [
    prefix,
    String(data.message ?? "Done"),
    `Marked present: ${data.marked_present ?? 0}`,
    `Not marked: ${data.not_marked ?? 0}`,
    formatIdList("Clicked IDs", data.marked_present_ids),
    formatIdList("Not clicked IDs", data.not_marked_ids),
    notFound ? `Not found in BKMS: ${notFound}` : "",
    data.job_id ? `Job ID: ${data.job_id}` : "",
  ]
    .filter(Boolean)
    .join(" | ");
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. RunAttendanceBot
// ─────────────────────────────────────────────────────────────────────────────
pack.addFormula({
  name: "RunAttendanceBot",
  description: "Trigger the BKMS Sabha attendance bot for a given date and group.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "date",
      description: "Sabha date in YYYY-MM-DD format",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "group",
      description: "Group name, e.g. 'Sunday K1'",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "sabhaHeld",
      description: "'yes' or 'no'",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "p2Guju",
      description: "'yes' or 'no' — was P2 in Gujarati?",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "prepCycleDone",
      description: "'yes' or 'no' — was prep cycle done?",
    }),
    coda.makeParameter({
      type: coda.ParameterType.Number,
      name: "captchaSeconds",
      description: "How many seconds the user wants to solve the CAPTCHA.",
      optional: true,
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([date, group, sabhaHeld, p2Guju, prepCycleDone, captchaSeconds], context) {
    const base = context.endpoint!.replace(/\/$/, "");

    // If date looks like a job ID (32 hex chars, no spaces), fetch that job instead of running the bot
    if (/^[0-9a-f]{32}$/i.test(date.trim())) {
      const response = await context.fetcher.fetch({
        method: "GET",
        url: `${base}/attendance-job/${encodeURIComponent(date.trim())}`,
        cacheTtlSecs: 0,
      });
      return formatAttendanceJobResult(response.body as Record<string, unknown>);
    }

    const normalizedDate = normalizeDateInput(date);
    const resolvedCaptchaSeconds =
      typeof captchaSeconds === "number" && Number.isFinite(captchaSeconds)
        ? Math.max(1, Math.min(300, Math.trunc(captchaSeconds)))
        : 20;
    const response = await context.fetcher.fetch({
      method: "POST",
      url: `${base}/run-bot`,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: normalizedDate,
        group,
        sabhaHeld,
        p2Guju,
        prepCycleDone,
        captchaSeconds: resolvedCaptchaSeconds,
      }),
    });
    const data = response.body as Record<string, unknown>;
    if (data.error) throw new coda.UserVisibleError(String(data.error));
    if (!data.job_id) throw new coda.UserVisibleError("No job ID returned from bot.");
    return String(data.job_id);
  },
});

pack.addFormula({
  name: "GetAttendanceJob",
  description: "Fetch the final status and result of a previously started BKMS attendance job.",
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunAttendanceBot.",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addFormula({
  name: "FetchAttendanceResult",
  description: "Button action: fetch the completed result for a job ID and return it as a string for storage in a column.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID stored in the Job ID column.",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    if (!jobId) throw new coda.UserVisibleError("No Job ID found. Run the bot first.");
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addColumnFormat({
  name: "AttendanceResult",
  formulaName: "FetchAttendanceResult",
});

pack.addFormula({
  name: "RunAttendanceBotStructured",
  description: "Fetch the completed result for a BKMS attendance job by job ID.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunAttendanceBot (stored in the Job ID column).",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    if (!jobId) throw new coda.UserVisibleError("No Job ID found. Run the bot first.");
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addFormula({
  name: "GetAttendanceJobStructured",
  description: "Fetch a structured BKMS attendance job result using the job ID.",
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunAttendanceBotStructured.",
    }),
  ],
  resultType: coda.ValueType.Object,
  schema: AttendanceJobSchema,
  execute: async function ([jobId], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return normalizeAttendanceJob(response.body as Record<string, unknown>);
  },
});

// ─────────────────────────────────────────────────────────────────────────────
// 2. RunBalMandalBot
// ─────────────────────────────────────────────────────────────────────────────
pack.addFormula({
  name: "RunBalMandalBot",
  description: "Trigger the BKMS Bal Mandal attendance bot for a given date and day (Saturday/Sunday).",
  isAction: true,
  parameters: [
    coda.makeParameter({ type: coda.ParameterType.String, name: "date", description: "Sabha date in YYYY-MM-DD format", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "day", description: "'Saturday' or 'Sunday'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "sabhaHeld", description: "'Yes' or 'No' — was at least one group sabha held?", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "combinedGroups", description: "'Yes' or 'No' — are all groups reporting the same activities?", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "smrutiTime", description: "'Yes' or 'No' (combined)", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "mukhpath", description: "'Yes' or 'No' (combined)", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "prepCycleDone", description: "'Yes' or 'No' (combined)", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.Number, name: "captchaSeconds", description: "Seconds to solve the CAPTCHA (default 20).", optional: true }),
    // Individual group params — Group 0
    coda.makeParameter({ type: coda.ParameterType.String, name: "g0Held", description: "Group 0: Sabha held? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g0Smruti", description: "Group 0: Smruti Time? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g0Mukhpath", description: "Group 0: Mukhpath? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g0Prep", description: "Group 0: Prep Cycle? 'Yes'/'No'", optional: true }),
    // Group 1
    coda.makeParameter({ type: coda.ParameterType.String, name: "g1Held", description: "Group 1: Sabha held? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g1Smruti", description: "Group 1: Smruti Time? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g1Mukhpath", description: "Group 1: Mukhpath? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g1Prep", description: "Group 1: Prep Cycle? 'Yes'/'No'", optional: true }),
    // Group 2A
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2aHeld", description: "Group 2A: Sabha held? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2aSmruti", description: "Group 2A: Smruti Time? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2aMukhpath", description: "Group 2A: Mukhpath? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2aPrep", description: "Group 2A: Prep Cycle? 'Yes'/'No'", optional: true }),
    // Group 2B
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2bHeld", description: "Group 2B: Sabha held? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2bSmruti", description: "Group 2B: Smruti Time? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2bMukhpath", description: "Group 2B: Mukhpath? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g2bPrep", description: "Group 2B: Prep Cycle? 'Yes'/'No'", optional: true }),
    // Group 3
    coda.makeParameter({ type: coda.ParameterType.String, name: "g3Held", description: "Group 3: Sabha held? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g3Smruti", description: "Group 3: Smruti Time? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g3Mukhpath", description: "Group 3: Mukhpath? 'Yes'/'No'", optional: true }),
    coda.makeParameter({ type: coda.ParameterType.String, name: "g3Prep", description: "Group 3: Prep Cycle? 'Yes'/'No'", optional: true }),
  ],
  resultType: coda.ValueType.String,
  execute: async function (
    [date, day, sabhaHeld, combinedGroups,
     smrutiTime, mukhpath, prepCycleDone, captchaSeconds,
     g0Held, g0Smruti, g0Mukhpath, g0Prep,
     g1Held, g1Smruti, g1Mukhpath, g1Prep,
     g2aHeld, g2aSmruti, g2aMukhpath, g2aPrep,
     g2bHeld, g2bSmruti, g2bMukhpath, g2bPrep,
     g3Held, g3Smruti, g3Mukhpath, g3Prep],
    context
  ) {
    const base = context.endpoint!.replace(/\/$/, "");
    const normalizedDate = date ? normalizeDateInput(date) : "";
    const resolvedCaptchaSeconds =
      typeof captchaSeconds === "number" && Number.isFinite(captchaSeconds)
        ? Math.max(1, Math.min(300, Math.trunc(captchaSeconds)))
        : 20;

    const individualGroups: Record<string, Record<string, string>> = {
      "group 0":  { held: g0Held  ?? "No", smruti_time: g0Smruti  ?? "No", mukhpath: g0Mukhpath  ?? "No", prep_cycle: g0Prep  ?? "No" },
      "group 1":  { held: g1Held  ?? "No", smruti_time: g1Smruti  ?? "No", mukhpath: g1Mukhpath  ?? "No", prep_cycle: g1Prep  ?? "No" },
      "group 2a": { held: g2aHeld ?? "No", smruti_time: g2aSmruti ?? "No", mukhpath: g2aMukhpath ?? "No", prep_cycle: g2aPrep ?? "No" },
      "group 2b": { held: g2bHeld ?? "No", smruti_time: g2bSmruti ?? "No", mukhpath: g2bMukhpath ?? "No", prep_cycle: g2bPrep ?? "No" },
      "group 3":  { held: g3Held  ?? "No", smruti_time: g3Smruti  ?? "No", mukhpath: g3Mukhpath  ?? "No", prep_cycle: g3Prep  ?? "No" },
    };

    const response = await context.fetcher.fetch({
      method: "POST",
      url: `${base}/run-bal-mandal`,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: normalizedDate,
        day: day ?? "Sunday",
        sabhaHeld: sabhaHeld ?? "No",
        combinedGroups: combinedGroups ?? "No",
        smrutiTime: smrutiTime ?? "No",
        mukhpath: mukhpath ?? "No",
        prepCycleDone: prepCycleDone ?? "No",
        individualGroups,
        captchaSeconds: resolvedCaptchaSeconds,
      }),
    });
    const data = response.body as Record<string, unknown>;
    if (data.error) throw new coda.UserVisibleError(String(data.error));
    if (!data.job_id) throw new coda.UserVisibleError("No job ID returned from bot.");
    return String(data.job_id);
  },
});

pack.addFormula({
  name: "GetBalMandalJob",
  description: "Fetch the status and result of a previously started Bal Mandal attendance job.",
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunBalMandalBot.",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addFormula({
  name: "FetchBalMandalResult",
  description: "Button action: fetch the completed Bal Mandal result for a job ID and store it in a column.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID stored in the Job ID column.",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    if (!jobId) throw new coda.UserVisibleError("No Job ID found. Run the bot first.");
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addColumnFormat({
  name: "BalMandalResult",
  formulaName: "FetchBalMandalResult",
});

pack.addFormula({
  name: "GetBalMandalJobStructured",
  description: "Fetch a structured Bal Mandal attendance job result using the job ID.",
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunBalMandalBot.",
    }),
  ],
  resultType: coda.ValueType.Object,
  schema: AttendanceJobSchema,
  execute: async function ([jobId], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return normalizeAttendanceJob(response.body as Record<string, unknown>);
  },
});

// ─────────────────────────────────────────────────────────────────────────────
// 3. RunGoshthiBot
// ─────────────────────────────────────────────────────────────────────────────
pack.addFormula({
  name: "RunGoshthiBot",
  description: "Trigger the BKMS Goshthi attendance bot for a given month and year.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "month",
      description: "Full month name, e.g. 'March'",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "year",
      description: "4-digit year, e.g. '2025'",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "goshthiHeld",
      description: "'yes' or 'no'",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "hangout",
      description: "'yes' or 'no' — was this a hangout?",
    }),
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "workshop",
      description: "'yes' or 'no' — was a Karyakar workshop held?",
    }),
    coda.makeParameter({
      type: coda.ParameterType.Number,
      name: "captchaSeconds",
      description: "How many seconds the user wants to solve the CAPTCHA.",
      optional: true,
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([month, year, goshthiHeld, hangout, workshop, captchaSeconds], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const resolvedCaptchaSeconds =
      typeof captchaSeconds === "number" && Number.isFinite(captchaSeconds)
        ? Math.max(1, Math.min(300, Math.trunc(captchaSeconds)))
        : 10;
    const response = await context.fetcher.fetch({
      method: "POST",
      url: `${base}/run-goshthi`,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ month, year, goshthiHeld, hangout, workshop, captchaSeconds: resolvedCaptchaSeconds }),
    });
    const data = response.body as Record<string, unknown>;
    if (data.error) throw new coda.UserVisibleError(String(data.error));
    if (!data.job_id) throw new coda.UserVisibleError("No job ID returned from bot.");
    return String(data.job_id);
  },
});

pack.addFormula({
  name: "GetGoshthiJob",
  description: "Fetch the status and result of a previously started Goshthi attendance job.",
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunGoshthiBot.",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addFormula({
  name: "FetchGoshthiResult",
  description: "Button action: fetch the completed Goshthi result for a job ID and store it in a column.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID stored in the Job ID column.",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([jobId], context) {
    if (!jobId) throw new coda.UserVisibleError("No Job ID found. Run the bot first.");
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return formatAttendanceJobResult(response.body as Record<string, unknown>);
  },
});

pack.addColumnFormat({
  name: "GoshthiResult",
  formulaName: "FetchGoshthiResult",
});

pack.addFormula({
  name: "GetGoshthiJobStructured",
  description: "Fetch a structured Goshthi attendance job result using the job ID.",
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.String,
      name: "jobId",
      description: "The job ID returned by RunGoshthiBot.",
    }),
  ],
  resultType: coda.ValueType.Object,
  schema: AttendanceJobSchema,
  execute: async function ([jobId], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "GET",
      url: `${base}/attendance-job/${encodeURIComponent(jobId)}`,
      cacheTtlSecs: 0,
    });
    return normalizeAttendanceJob(response.body as Record<string, unknown>);
  },
});

// ─────────────────────────────────────────────────────────────────────────────
// 3. RunUserUpdateBot
// ─────────────────────────────────────────────────────────────────────────────
pack.addFormula({
  name: "RunUserUpdateBot",
  description:
    "Trigger the BKMS user-update bot to mark the Saturday Sabha checkbox for a list of BKMS IDs.",
  isAction: true,
  parameters: [
    coda.makeParameter({
      type: coda.ParameterType.StringArray,
      name: "userIds",
      description: "List of BKMS member IDs to update",
    }),
  ],
  resultType: coda.ValueType.String,
  execute: async function ([userIds], context) {
    const base = context.endpoint!.replace(/\/$/, "");
    const response = await context.fetcher.fetch({
      method: "POST",
      url: `${base}/run-user-update`,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_ids: userIds }),
    });
    const data = response.body as Record<string, unknown>;
    if (data.error) throw new coda.UserVisibleError(String(data.error));
    return String(data.message ?? "Done");
  },
});
