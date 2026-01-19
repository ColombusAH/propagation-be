import { promisify } from "node:util";
import { execFile } from "node:child_process";
import { z } from "zod";

// Generic email schema supporting multiple recipients and optional fields
export const zEmailMessage = z.object({
  from: z.string().email().optional().describe("Sender email address"),
  to: z.array(z.string().email()).nonempty().describe("Primary recipients"),
  cc: z.array(z.string().email()).optional().describe("CC recipients"),
  bcc: z.array(z.string().email()).optional().describe("BCC recipients"),
  subject: z.string().describe("Email subject"),
  text: z.string().optional().describe("Plain text body"),
  html: z.string().optional().describe("HTML body"),
  attachments: z
    .array(
      z.object({
        filename: z.string().describe("File name"),
        content: z.string().describe("Base64 encoded content"),
        contentType: z.string().optional().describe("MIME type"),
        encoding: z
          .enum(["base64", "7bit", "quoted-printable", "binary"])
          .default("base64"),
      })
    )
    .optional()
    .describe("Email attachments"),
});

export type EmailMessage = z.infer<typeof zEmailMessage>;

// Helper to obtain Replit auth token and hostname
async function getAuthToken(): Promise<{ authToken: string; hostname: string }> {
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME || "";
  const { stdout } = await promisify(execFile)(
    "replit",
    ["identity", "create", "--audience", `https://${hostname}`],
    { encoding: "utf8" }
  );
  const replitToken = stdout.trim();
  if (!replitToken) {
    throw new Error("Replit Identity Token not found for repl/depl");
  }
  return { authToken: `Bearer ${replitToken}`, hostname };
}

/**
 * Send an email using Replit's mailer service.
 * The function is generic – you can specify multiple recipients, optional sender, and attachments.
 */
export async function sendEmail(message: EmailMessage): Promise<{
  accepted: string[];
  rejected: string[];
  pending?: string[];
  messageId: string;
  response: string;
}> {
  const { hostname, authToken } = await getAuthToken();
  if (!hostname) {
    throw new Error("REPLIT_CONNECTORS_HOSTNAME not found");
  }

  const payload = {
    from: message.from,
    to: message.to,
    cc: message.cc,
    bcc: message.bcc,
    subject: message.subject,
    text: message.text,
    html: message.html,
    attachments: message.attachments,
  };

  const response = await fetch(`https://${hostname}/api/v2/mailer/send`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Replit-Authentication": authToken,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to send email");
  }

  return await response.json();
}
