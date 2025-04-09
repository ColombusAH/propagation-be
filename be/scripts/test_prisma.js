#!/usr/bin/env node

/**
 * This script tests the Prisma connection directly from Node.js
 * Run with: node scripts/test_prisma.js
 */

const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const path = require('path');

async function main() {
  console.log('=== Prisma Connection Test ===');
  
  // Check for schema.prisma file
  const possiblePaths = [
    path.join(process.cwd(), 'prisma/schema.prisma'),
    path.join(process.cwd(), '../prisma/schema.prisma'),
    '/app/prisma/schema.prisma',
    '/code/prisma/schema.prisma'
  ];
  
  let schemaPath = null;
  for (const p of possiblePaths) {
    try {
      if (fs.existsSync(p)) {
        schemaPath = p;
        break;
      }
    } catch (err) {
      // Ignore
    }
  }
  
  console.log('Environment:');
  console.log(`- Node.js version: ${process.version}`);
  console.log(`- Current directory: ${process.cwd()}`);
  console.log(`- DATABASE_URL found: ${!!process.env.DATABASE_URL}`);
  
  // Mask password for printing
  const dbUrl = process.env.DATABASE_URL || '';
  const maskedUrl = dbUrl.replace(/\/\/([^:]+):([^@]+)@/, '//\$1:***@');
  console.log(`- Masked DATABASE_URL: ${maskedUrl}`);
  
  console.log(`- Schema.prisma found: ${!!schemaPath} (${schemaPath || 'not found'})`);
  
  try {
    console.log('\nAttempting to connect to the database...');
    const prisma = new PrismaClient();
    await prisma.$connect();
    
    console.log('✅ Successfully connected to the database!');
    
    // Simple query to test actual database access
    console.log('\nTesting simple query...');
    const result = await prisma.$queryRaw`SELECT 1 as test`;
    console.log(`✅ Query result: ${JSON.stringify(result)}`);
    
    // Close the connection
    await prisma.$disconnect();
    console.log('Database connection closed gracefully.');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error connecting to the database:');
    console.error(error);
    
    // Provide helpful information based on error type
    if (error.message.includes('P1001')) {
      console.log('\nTroubleshooting Authentication Error:');
      console.log('- Check that username and password in DATABASE_URL are correct');
      console.log('- Verify that the specified user has access to the database');
    } else if (error.message.includes('P1002')) {
      console.log('\nTroubleshooting Database Connection Error:');
      console.log('- Verify the hostname is correct');
      console.log('- Check if the database server is running');
      console.log('- Ensure no firewall is blocking access');
    } else if (error.message.includes('P1003')) {
      console.log('\nTroubleshooting Database Not Found Error:');
      console.log('- Check if the database name in DATABASE_URL exists');
      console.log('- Try creating the database if it does not exist');
    }
    
    process.exit(1);
  }
}

main(); 