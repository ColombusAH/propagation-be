/**
 * Email Service Utility
 * 
 * A generic email service that supports:
 * - Multiple email providers (Replit, SMTP, API-based)
 * - Custom recipients
 * - HTML and plain text content
 * - Attachments
 * - Email templates
 */

import { z } from "zod";

// ============ Schemas ============

export const EmailAttachmentSchema = z.object({
    filename: z.string().describe("File name"),
    content: z.string().describe("Base64 encoded content"),
    contentType: z.string().optional().describe("MIME type"),
    encoding: z
        .enum(["base64", "7bit", "quoted-printable", "binary"])
        .default("base64"),
});

export const EmailMessageSchema = z.object({
    to: z.array(z.string().email()).min(1).describe("Recipient email addresses"),
    cc: z.array(z.string().email()).optional().describe("CC recipients"),
    bcc: z.array(z.string().email()).optional().describe("BCC recipients"),
    subject: z.string().describe("Email subject"),
    text: z.string().optional().describe("Plain text body"),
    html: z.string().optional().describe("HTML body"),
    attachments: z.array(EmailAttachmentSchema).optional().describe("Email attachments"),
    replyTo: z.string().email().optional().describe("Reply-to address"),
});

export type EmailAttachment = z.infer<typeof EmailAttachmentSchema>;
export type EmailMessage = z.infer<typeof EmailMessageSchema>;

export interface EmailResult {
    success: boolean;
    messageId?: string;
    accepted?: string[];
    rejected?: string[];
    error?: string;
}

// ============ Email Templates ============

export interface EmailTemplate {
    subject: string;
    html: string;
    text?: string;
}

export const EmailTemplates = {
    /** Theft alert notification */
    theftAlert: (productName: string, location: string, time: string): EmailTemplate => ({
        subject: `🚨 התראת גניבה - ${productName}`,
        html: `
      <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #dc2626; color: white; padding: 20px; text-align: center;">
          <h1>🚨 התראת גניבה</h1>
        </div>
        <div style="padding: 20px; background: #f3f4f6;">
          <p><strong>מוצר:</strong> ${productName}</p>
          <p><strong>מיקום:</strong> ${location}</p>
          <p><strong>זמן:</strong> ${time}</p>
          <p style="color: #dc2626; font-weight: bold;">נדרשת פעולה מיידית!</p>
        </div>
      </div>
    `,
        text: `התראת גניבה!\n\nמוצר: ${productName}\nמיקום: ${location}\nזמן: ${time}\n\nנדרשת פעולה מיידית!`,
    }),

    /** Payment confirmation */
    paymentConfirmation: (orderId: string, total: string, items: string[]): EmailTemplate => ({
        subject: `✅ אישור תשלום - הזמנה #${orderId}`,
        html: `
      <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #16a34a; color: white; padding: 20px; text-align: center;">
          <h1>✅ התשלום התקבל</h1>
        </div>
        <div style="padding: 20px; background: #f3f4f6;">
          <p><strong>מספר הזמנה:</strong> ${orderId}</p>
          <p><strong>סה"כ:</strong> ${total}</p>
          <h3>פריטים:</h3>
          <ul>
            ${items.map(item => `<li>${item}</li>`).join('')}
          </ul>
          <p>תודה על הקנייה!</p>
        </div>
      </div>
    `,
        text: `אישור תשלום\n\nמספר הזמנה: ${orderId}\nסה"כ: ${total}\n\nפריטים:\n${items.map(item => `- ${item}`).join('\n')}\n\nתודה על הקנייה!`,
    }),

    /** Welcome email */
    welcome: (userName: string): EmailTemplate => ({
        subject: `ברוכים הבאים למערכת RFID!`,
        html: `
      <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #3b82f6; color: white; padding: 20px; text-align: center;">
          <h1>ברוכים הבאים!</h1>
        </div>
        <div style="padding: 20px; background: #f3f4f6;">
          <p>שלום ${userName},</p>
          <p>ברוכים הבאים למערכת ניהול המלאי והמכירות שלנו.</p>
          <p>אנחנו שמחים שהצטרפת אלינו!</p>
        </div>
      </div>
    `,
        text: `ברוכים הבאים!\n\nשלום ${userName},\n\nברוכים הבאים למערכת ניהול המלאי והמכירות שלנו.\n\nאנחנו שמחים שהצטרפת אלינו!`,
    }),
};

// ============ Email Service Class ============

export type EmailProvider = 'api' | 'console';

export interface EmailServiceConfig {
    provider: EmailProvider;
    apiEndpoint?: string;
    apiKey?: string;
    fromEmail?: string;
    fromName?: string;
}

class EmailService {
    private config: EmailServiceConfig;

    constructor(config?: Partial<EmailServiceConfig>) {
        this.config = {
            provider: config?.provider || 'console',
            apiEndpoint: config?.apiEndpoint || '/api/v1/notifications/email',
            fromEmail: config?.fromEmail || 'noreply@rfid-system.com',
            fromName: config?.fromName || 'מערכת RFID',
            ...config,
        };
    }

    /**
     * Send an email
     */
    async send(message: EmailMessage): Promise<EmailResult> {
        // Validate message
        const validationResult = EmailMessageSchema.safeParse(message);
        if (!validationResult.success) {
            return {
                success: false,
                error: `Validation failed: ${validationResult.error.message}`,
            };
        }

        switch (this.config.provider) {
            case 'api':
                return this.sendViaApi(message);
            case 'console':
            default:
                return this.sendToConsole(message);
        }
    }

    /**
     * Send email using backend API
     */
    private async sendViaApi(message: EmailMessage): Promise<EmailResult> {
        try {
            const response = await fetch(this.config.apiEndpoint!, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(this.config.apiKey ? { 'Authorization': `Bearer ${this.config.apiKey}` } : {}),
                },
                body: JSON.stringify({
                    to: message.to,
                    cc: message.cc,
                    bcc: message.bcc,
                    subject: message.subject,
                    text: message.text,
                    html: message.html,
                    attachments: message.attachments,
                    replyTo: message.replyTo,
                }),
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ message: 'Unknown error' }));
                return {
                    success: false,
                    error: error.message || `HTTP ${response.status}`,
                };
            }

            const result = await response.json();
            return {
                success: true,
                messageId: result.messageId,
                accepted: result.accepted || message.to,
                rejected: result.rejected || [],
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Failed to send email',
            };
        }
    }

    /**
     * Log email to console (for development)
     */
    private sendToConsole(message: EmailMessage): EmailResult {
        console.log('📧 Email would be sent:');
        console.log('  To:', message.to.join(', '));
        if (message.cc?.length) console.log('  CC:', message.cc.join(', '));
        console.log('  Subject:', message.subject);
        console.log('  Body:', message.text?.substring(0, 100) || message.html?.substring(0, 100));

        return {
            success: true,
            messageId: `console-${Date.now()}`,
            accepted: message.to,
            rejected: [],
        };
    }

    /**
     * Send email using a template
     */
    async sendTemplate(
        to: string[],
        template: EmailTemplate,
        options?: { cc?: string[]; attachments?: EmailAttachment[] }
    ): Promise<EmailResult> {
        return this.send({
            to,
            cc: options?.cc,
            subject: template.subject,
            html: template.html,
            text: template.text,
            attachments: options?.attachments,
        });
    }
}

// ============ Singleton Export ============

export const emailService = new EmailService({
    provider: typeof window !== 'undefined' ? 'api' : 'console',
});

// Convenience function
export async function sendEmail(message: EmailMessage): Promise<EmailResult> {
    return emailService.send(message);
}

// Template-based sending
export async function sendTheftAlert(
    recipients: string[],
    productName: string,
    location: string,
    time: string
): Promise<EmailResult> {
    return emailService.sendTemplate(
        recipients,
        EmailTemplates.theftAlert(productName, location, time)
    );
}

export async function sendPaymentConfirmation(
    recipient: string,
    orderId: string,
    total: string,
    items: string[]
): Promise<EmailResult> {
    return emailService.sendTemplate(
        [recipient],
        EmailTemplates.paymentConfirmation(orderId, total, items)
    );
}
