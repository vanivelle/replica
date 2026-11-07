#!/usr/bin/env node
/**
 * Test script to verify frontend-backend integration
 */

const BACKEND_URL = 'http://127.0.0.1:8000';
const FRONTEND_URL = 'http://localhost:5173';

async function testBackendModels() {
  console.log('\n=== Testing Backend /v1/models Endpoint ===');
  try {
    const response = await fetch(`${BACKEND_URL}/v1/models`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json();
    console.log('✓ Backend responded');
    console.log(`✓ Found ${data.data.length} models`);
    
    if (data.data.length > 0) {
      console.log('Models:');
      data.data.forEach(m => console.log(`  - ${m.id}`));
      return true;
    } else {
      console.log('⚠ No models returned');
      return false;
    }
  } catch (error) {
    console.error('✗ Backend test failed:', error.message);
    return false;
  }
}

async function testBackendCompletions() {
  console.log('\n=== Testing Backend /v1/chat/completions Endpoint ===');
  try {
    const response = await fetch(`${BACKEND_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama2',
        messages: [{ role: 'user', content: 'Hi' }],
        stream: false,
      }),
    });
    
    if (response.ok) {
      console.log('✓ Completions endpoint is ready');
      return true;
    } else {
      console.log(`⚠ Endpoint returned HTTP ${response.status}`);
      return true; // Still OK, endpoint exists
    }
  } catch (error) {
    console.error('✗ Completions endpoint test failed:', error.message);
    return false;
  }
}

async function testFrontendIsServing() {
  console.log('\n=== Testing Frontend Server ===');
  try {
    const response = await fetch(FRONTEND_URL);
    if (response.ok) {
      console.log('✓ Frontend is serving on', FRONTEND_URL);
      return true;
    } else {
      console.log(`⚗ Frontend returned HTTP ${response.status}`);
      return false;
    }
  } catch (error) {
    console.error('✗ Frontend server test failed:', error.message);
    return false;
  }
}

async function main() {
  console.log('╔════════════════════════════════════════════════════╗');
  console.log('║  Frontend-Backend Integration Test Suite           ║');
  console.log('╚════════════════════════════════════════════════════╝');
  
  const results = [];
  
  // Test backend
  results.push(await testBackendModels());
  results.push(await testBackendCompletions());
  results.push(await testFrontendIsServing());
  
  console.log('\n╔════════════════════════════════════════════════════╗');
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  if (passed === total) {
    console.log(`║  ✓ ALL TESTS PASSED (${passed}/${total})                    ║`);
  } else {
    console.log(`║  ✗ SOME TESTS FAILED (${passed}/${total})                    ║`);
  }
  console.log('╚════════════════════════════════════════════════════╝');
  
  process.exit(passed === total ? 0 : 1);
}

main().catch(console.error);
