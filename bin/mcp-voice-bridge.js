#!/usr/bin/env node
/**
 * Jarrvis – MCP Voice Bridge CLI entry point
 *
 * Run standalone:  node bin/mcp-voice-bridge.js
 * Run via npx:     npx jarrvis
 *
 * Configure in Claude Desktop (claude_desktop_config.json):
 *   "mcpServers": {
 *     "jarrvis": {
 *       "command": "node",
 *       "args": ["/path/to/XLab_Jarrvis/bin/mcp-voice-bridge.js"],
 *       "env": { "VOICE_LANGUAGE": "vi-VN" }
 *     }
 *   }
 */
import { startServer } from '../src/server.js';

// Ensure stdout/stderr use UTF-8 on all platforms (important on Windows)
if (process.stdout.setEncoding) process.stdout.setEncoding('utf8');
if (process.stderr.setEncoding) process.stderr.setEncoding('utf8');

// Set Python env for consistent UTF-8 I/O
process.env.PYTHONIOENCODING = process.env.PYTHONIOENCODING || 'utf-8';
process.env.PYTHONUTF8 = '1';

startServer().catch((err) => {
  process.stderr.write(`[jarrvis] Fatal: ${err.message}\n`);
  process.exit(1);
});
