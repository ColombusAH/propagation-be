/*
  Warnings:

  - The values [OWNER,ADMIN] on the enum `Role` will be removed. If these variants are still used in the database, this will fail.

*/
-- CreateEnum
CREATE TYPE "PaymentStatus" AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REFUNDED');

-- CreateEnum
CREATE TYPE "PaymentProvider" AS ENUM ('STRIPE', 'TRANZILA', 'NEXI', 'CASH');

-- AlterEnum
BEGIN;
CREATE TYPE "Role_new" AS ENUM ('SUPER_ADMIN', 'NETWORK_MANAGER', 'STORE_MANAGER', 'EMPLOYEE', 'CUSTOMER');
ALTER TABLE "User" ALTER COLUMN "role" TYPE "Role_new" USING ("role"::text::"Role_new");
ALTER TYPE "Role" RENAME TO "Role_old";
ALTER TYPE "Role_new" RENAME TO "Role";
DROP TYPE "Role_old";
COMMIT;

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "receiveTheftAlerts" BOOLEAN NOT NULL DEFAULT false;

-- CreateTable
CREATE TABLE "Payment" (
    "id" TEXT NOT NULL,
    "orderId" TEXT NOT NULL,
    "amount" INTEGER NOT NULL,
    "currency" TEXT NOT NULL DEFAULT 'ILS',
    "status" "PaymentStatus" NOT NULL DEFAULT 'PENDING',
    "provider" "PaymentProvider" NOT NULL,
    "externalId" TEXT,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "paidAt" TIMESTAMP(3),

    CONSTRAINT "Payment_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TagMapping" (
    "id" TEXT NOT NULL,
    "epc" TEXT NOT NULL,
    "encryptedQr" TEXT NOT NULL,
    "epcHash" TEXT,
    "productId" TEXT,
    "productDescription" TEXT,
    "containerId" TEXT,
    "isPaid" BOOLEAN NOT NULL DEFAULT false,
    "paidAt" TIMESTAMP(3),
    "paymentId" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TagMapping_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TheftAlert" (
    "id" TEXT NOT NULL,
    "tagId" TEXT NOT NULL,
    "epc" TEXT NOT NULL,
    "productDescription" TEXT,
    "detectedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "location" TEXT,
    "resolved" BOOLEAN NOT NULL DEFAULT false,
    "resolvedAt" TIMESTAMP(3),
    "resolvedBy" TEXT,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "TheftAlert_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AlertRecipient" (
    "id" TEXT NOT NULL,
    "theftAlertId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "sentAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "delivered" BOOLEAN NOT NULL DEFAULT false,
    "deliveredAt" TIMESTAMP(3),
    "read" BOOLEAN NOT NULL DEFAULT false,
    "readAt" TIMESTAMP(3),

    CONSTRAINT "AlertRecipient_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Payment_orderId_idx" ON "Payment"("orderId");

-- CreateIndex
CREATE INDEX "Payment_status_idx" ON "Payment"("status");

-- CreateIndex
CREATE INDEX "Payment_provider_idx" ON "Payment"("provider");

-- CreateIndex
CREATE UNIQUE INDEX "TagMapping_epc_key" ON "TagMapping"("epc");

-- CreateIndex
CREATE UNIQUE INDEX "TagMapping_encryptedQr_key" ON "TagMapping"("encryptedQr");

-- CreateIndex
CREATE INDEX "TagMapping_epc_idx" ON "TagMapping"("epc");

-- CreateIndex
CREATE INDEX "TagMapping_encryptedQr_idx" ON "TagMapping"("encryptedQr");

-- CreateIndex
CREATE INDEX "TagMapping_epcHash_idx" ON "TagMapping"("epcHash");

-- CreateIndex
CREATE INDEX "TagMapping_productId_idx" ON "TagMapping"("productId");

-- CreateIndex
CREATE INDEX "TagMapping_isPaid_idx" ON "TagMapping"("isPaid");

-- CreateIndex
CREATE INDEX "TheftAlert_tagId_idx" ON "TheftAlert"("tagId");

-- CreateIndex
CREATE INDEX "TheftAlert_resolved_idx" ON "TheftAlert"("resolved");

-- CreateIndex
CREATE INDEX "TheftAlert_detectedAt_idx" ON "TheftAlert"("detectedAt");

-- CreateIndex
CREATE INDEX "AlertRecipient_theftAlertId_idx" ON "AlertRecipient"("theftAlertId");

-- CreateIndex
CREATE INDEX "AlertRecipient_userId_idx" ON "AlertRecipient"("userId");

-- CreateIndex
CREATE INDEX "AlertRecipient_delivered_idx" ON "AlertRecipient"("delivered");

-- CreateIndex
CREATE INDEX "AlertRecipient_read_idx" ON "AlertRecipient"("read");

-- AddForeignKey
ALTER TABLE "TagMapping" ADD CONSTRAINT "TagMapping_paymentId_fkey" FOREIGN KEY ("paymentId") REFERENCES "Payment"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TheftAlert" ADD CONSTRAINT "TheftAlert_tagId_fkey" FOREIGN KEY ("tagId") REFERENCES "TagMapping"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AlertRecipient" ADD CONSTRAINT "AlertRecipient_theftAlertId_fkey" FOREIGN KEY ("theftAlertId") REFERENCES "TheftAlert"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AlertRecipient" ADD CONSTRAINT "AlertRecipient_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
