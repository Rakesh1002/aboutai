#!/usr/bin/env npx ts-node
/**
 * Script to manually trigger the content pipeline
 * 
 * Usage:
 *   npx ts-node scripts/run-pipeline.ts [--type news|tool] [--url <url>]
 */

const API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

async function triggerPipeline(contentType?: string, sourceUrl?: string) {
  console.log('🚀 Triggering content pipeline...\n');
  
  const endpoint = sourceUrl 
    ? `${API_URL}/api/v1/analyze`
    : `${API_URL}/api/v1/pipeline/run`;
  
  const body = sourceUrl
    ? { url: sourceUrl, priority: 'high' }
    : {};
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    
    const result = await response.json();
    console.log('✅ Pipeline triggered successfully!\n');
    console.log('Pipeline ID:', result.pipeline_id || result.task_id);
    console.log('Status:', result.status);
    
    if (result.pipeline_id) {
      console.log(`\nCheck status at: ${API_URL}/api/v1/pipeline/${result.pipeline_id}`);
    }
    
  } catch (error) {
    console.error('❌ Failed to trigger pipeline:', error);
    process.exit(1);
  }
}

async function checkPipelineStatus(pipelineId: string) {
  console.log(`📊 Checking pipeline status: ${pipelineId}\n`);
  
  try {
    const response = await fetch(`${API_URL}/api/v1/pipeline/${pipelineId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    
    const result = await response.json();
    console.log('Status:', result.status);
    console.log('Stage:', result.stage);
    console.log('Progress:', `${result.progress}%`);
    
    if (result.draft_id) {
      console.log('\n✅ Draft created:', result.draft_id);
    }
    
  } catch (error) {
    console.error('❌ Failed to check status:', error);
    process.exit(1);
  }
}

async function listDrafts() {
  console.log('📝 Listing content drafts...\n');
  
  try {
    const response = await fetch(`${API_URL}/api/v1/drafts`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    
    const drafts = await response.json();
    
    if (drafts.length === 0) {
      console.log('No drafts found.');
      return;
    }
    
    console.log(`Found ${drafts.length} draft(s):\n`);
    
    for (const draft of drafts) {
      console.log(`  [${draft.status}] ${draft.title || 'Untitled'}`);
      console.log(`    ID: ${draft.id}`);
      console.log(`    Type: ${draft.type}`);
      console.log(`    Quality: ${draft.quality_score || 'N/A'}`);
      console.log('');
    }
    
  } catch (error) {
    console.error('❌ Failed to list drafts:', error);
    process.exit(1);
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'run':
    const typeArg = args.indexOf('--type');
    const urlArg = args.indexOf('--url');
    const contentType = typeArg !== -1 ? args[typeArg + 1] : undefined;
    const sourceUrl = urlArg !== -1 ? args[urlArg + 1] : undefined;
    triggerPipeline(contentType, sourceUrl);
    break;
    
  case 'status':
    const pipelineId = args[1];
    if (!pipelineId) {
      console.error('Usage: run-pipeline.ts status <pipeline_id>');
      process.exit(1);
    }
    checkPipelineStatus(pipelineId);
    break;
    
  case 'drafts':
    listDrafts();
    break;
    
  default:
    console.log(`
aboutai Content Pipeline CLI

Usage:
  npx ts-node scripts/run-pipeline.ts <command> [options]

Commands:
  run [--url <url>]       Trigger the content pipeline
  status <pipeline_id>    Check pipeline status
  drafts                  List all content drafts

Examples:
  # Run full pipeline
  npx ts-node scripts/run-pipeline.ts run
  
  # Analyze specific tool URL
  npx ts-node scripts/run-pipeline.ts run --url https://example-ai-tool.com
  
  # Check status
  npx ts-node scripts/run-pipeline.ts status abc123
  
  # List drafts
  npx ts-node scripts/run-pipeline.ts drafts
`);
}

