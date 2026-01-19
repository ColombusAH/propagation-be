/*
  Warnings:

  - You are about to drop the `TagMapping` table. If the table is not empty, all the data it contains will be lost.

*/
-- CreateEnum
CREATE TYPE "ReaderType" AS ENUM ('FIXED', 'HANDHELD', 'GATE');

-- CreateEnum
CREATE TYPE "ConnectionMethod" AS ENUM ('TCP', 'WIFI', 'CELLULAR');

-- CreateEnum
CREATE TYPE "ReaderStatus" AS ENUM ('ONLINE', 'OFFLINE', 'ERROR');

-- CreateEnum
CREATE TYPE "RfidTagType" AS ENUM ('PASSIVE', 'ACTIVE');

-- CreateEnum
CREATE TYPE "TagMaterial" AS ENUM ('METAL', 'GLASS', 'GENERAL');

-- CreateEnum
CREATE TYPE "TagStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'SOLD', 'STOLEN', 'DAMAGED');

-- DropForeignKey
ALTER TABLE "TagMapping" DROP CONSTRAINT "TagMapping_paymentId_fkey";

-- DropForeignKey
ALTER TABLE "TheftAlert" DROP CONSTRAINT "TheftAlert_tagId_fkey";

-- DropTable
DROP TABLE "TagMapping";

-- CreateTable
CREATE TABLE "RfidReader" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "ipAddress" TEXT NOT NULL,
    "location" TEXT,
    "type" "ReaderType" NOT NULL DEFAULT 'FIXED',
    "connection" "ConnectionMethod" NOT NULL DEFAULT 'TCP',
    "status" "ReaderStatus" NOT NULL DEFAULT 'OFFLINE',
    "lastSeen" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "RfidReader_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "RfidTag" (
    "id" TEXT NOT NULL,
    "epc" TEXT NOT NULL,
    "tagType" "RfidTagType" NOT NULL DEFAULT 'PASSIVE',
    "material" "TagMaterial" NOT NULL DEFAULT 'GENERAL',
    "status" "TagStatus" NOT NULL DEFAULT 'ACTIVE',
    "encryptedQr" TEXT,
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

    CONSTRAINT "RfidTag_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "InventorySnapshot" (
    "id" TEXT NOT NULL,
    "readerId" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "itemCount" INTEGER NOT NULL,

    CONSTRAINT "InventorySnapshot_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "InventorySnapshotItem" (
    "id" TEXT NOT NULL,
    "snapshotId" TEXT NOT NULL,
    "epc" TEXT NOT NULL,
    "tagId" TEXT,

    CONSTRAINT "InventorySnapshotItem_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "RfidReader_ipAddress_key" ON "RfidReader"("ipAddress");

-- CreateIndex
CREATE INDEX "RfidReader_ipAddress_idx" ON "RfidReader"("ipAddress");

-- CreateIndex
CREATE INDEX "RfidReader_status_idx" ON "RfidReader"("status");

-- CreateIndex
CREATE UNIQUE INDEX "RfidTag_epc_key" ON "RfidTag"("epc");

-- CreateIndex
CREATE UNIQUE INDEX "RfidTag_encryptedQr_key" ON "RfidTag"("encryptedQr");

-- CreateIndex
CREATE INDEX "RfidTag_epc_idx" ON "RfidTag"("epc");

-- CreateIndex
CREATE INDEX "RfidTag_encryptedQr_idx" ON "RfidTag"("encryptedQr");

-- CreateIndex
CREATE INDEX "RfidTag_status_idx" ON "RfidTag"("status");

-- CreateIndex
CREATE INDEX "RfidTag_isPaid_idx" ON "RfidTag"("isPaid");

-- CreateIndex
CREATE INDEX "InventorySnapshot_readerId_idx" ON "InventorySnapshot"("readerId");

-- CreateIndex
CREATE INDEX "InventorySnapshot_timestamp_idx" ON "InventorySnapshot"("timestamp");

-- CreateIndex
CREATE INDEX "InventorySnapshotItem_snapshotId_idx" ON "InventorySnapshotItem"("snapshotId");

-- CreateIndex
CREATE INDEX "InventorySnapshotItem_epc_idx" ON "InventorySnapshotItem"("epc");

-- AddForeignKey
ALTER TABLE "RfidTag" ADD CONSTRAINT "RfidTag_paymentId_fkey" FOREIGN KEY ("paymentId") REFERENCES "Payment"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "InventorySnapshot" ADD CONSTRAINT "InventorySnapshot_readerId_fkey" FOREIGN KEY ("readerId") REFERENCES "RfidReader"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "InventorySnapshotItem" ADD CONSTRAINT "InventorySnapshotItem_snapshotId_fkey" FOREIGN KEY ("snapshotId") REFERENCES "InventorySnapshot"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "InventorySnapshotItem" ADD CONSTRAINT "InventorySnapshotItem_tagId_fkey" FOREIGN KEY ("tagId") REFERENCES "RfidTag"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TheftAlert" ADD CONSTRAINT "TheftAlert_tagId_fkey" FOREIGN KEY ("tagId") REFERENCES "RfidTag"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
