import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { join } from 'path';
import { config } from './config.js';

// ── Tool definitions ──────────────────────────────────────────────────────────
const TOOLS = [
  {
    name: 'voice_speak',
    description:
      'Speak text aloud to the user via text-to-speech. ' +
      'Use this to communicate information, ask questions verbally, or give voice feedback. ' +
      'Supports Vietnamese (vi-VN), English (en-US/en-GB), Japanese (ja-JP), Chinese (zh-CN).',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'The text to speak to the user.',
        },
        language: {
          type: 'string',
          description:
            'BCP-47 language code, e.g. vi-VN (default), en-US, ja-JP.',
          default: 'vi-VN',
        },
      },
      required: ['text'],
    },
  },
  {
    name: 'voice_listen',
    description:
      'Listen via microphone and transcribe what the user says. ' +
      'Uses Voice Activity Detection – waits for speech then stops on silence. ' +
      'Returns the transcribed text, or empty string if nothing was heard.',
    inputSchema: {
      type: 'object',
      properties: {
        timeout_seconds: {
          type: 'number',
          description: 'Maximum seconds to wait for speech (default: 30).',
          default: 30,
        },
        language: {
          type: 'string',
          description:
            'BCP-47 language code for recognition, e.g. vi-VN (default), en-US.',
          default: 'vi-VN',
        },
      },
    },
  },
  {
    name: 'voice_ask',
    description:
      'Ask the user a question by speaking it aloud, then wait for and transcribe their spoken response. ' +
      'Combines voice_speak + voice_listen in one step. ' +
      'Returns the user\'s spoken answer as text.',
    inputSchema: {
      type: 'object',
      properties: {
        question: {
          type: 'string',
          description: 'The question to speak to the user.',
        },
        timeout_seconds: {
          type: 'number',
          description: 'Seconds to wait for the user\'s spoken reply (default: 30).',
          default: 30,
        },
        language: {
          type: 'string',
          description:
            'BCP-47 language code for both TTS and STT (default: vi-VN).',
          default: 'vi-VN',
        },
      },
      required: ['question'],
    },
  },
  {
    name: 'list_audio_devices',
    description:
      'List all available audio devices (microphones and speakers) on the system. ' +
      'Useful for diagnosing audio issues or picking a specific microphone.',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
];

// ── Python subprocess helper ──────────────────────────────────────────────────
function runPython(scriptName, args = [], timeoutMs = 120_000) {
  return new Promise((resolve, reject) => {
    const scriptPath = join(config.pythonDir, scriptName);
    const proc = spawn(config.python, [scriptPath, ...args.map(String)], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });

    const timer = setTimeout(() => {
      proc.kill();
      reject(new Error(`Timeout after ${timeoutMs}ms running ${scriptName}`));
    }, timeoutMs);

    proc.on('close', (code) => {
      clearTimeout(timer);
      if (code === 0 || code === null) {
        resolve(stdout.trimEnd());
      } else {
        reject(
          new Error(
            `${scriptName} exited with code ${code}.\nstderr: ${stderr.slice(0, 500)}`
          )
        );
      }
    });

    proc.on('error', (err) => {
      clearTimeout(timer);
      reject(new Error(`Failed to spawn ${config.python}: ${err.message}`));
    });
  });
}

// ── Text helpers ──────────────────────────────────────────────────────────────
function resolveLanguage(args) {
  return String(args.language || config.language || 'vi-VN');
}

function mkText(text) {
  return { content: [{ type: 'text', text: String(text) }] };
}

function mkError(msg) {
  return { content: [{ type: 'text', text: String(msg) }], isError: true };
}

// ── MCP Server ────────────────────────────────────────────────────────────────
export async function createServer() {
  const server = new Server(
    { name: 'mcp-voice-bridge', version: '1.0.0' },
    { capabilities: { tools: {} } }
  );

  // List tools
  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args = {} } = request.params;

    try {
      switch (name) {
        // ── voice_speak ──────────────────────────────────────────────────────
        case 'voice_speak': {
          const text = String(args.text || '').trim();
          if (!text) return mkError('voice_speak: text is required');
          const lang = resolveLanguage(args);
          await runPython('speak.py', [text, lang]);
          return mkText(`[voice] Spoken: "${text}"`);
        }

        // ── voice_listen ─────────────────────────────────────────────────────
        case 'voice_listen': {
          const timeout = Math.max(5, Number(args.timeout_seconds || 30));
          const lang = resolveLanguage(args);
          const result = await runPython(
            'listen.py',
            [lang, timeout, config.micIndex],
            (timeout + 15) * 1000
          );
          if (!result) return mkText('[voice] No speech detected (silence or timeout)');
          return mkText(result);
        }

        // ── voice_ask ────────────────────────────────────────────────────────
        case 'voice_ask': {
          const question = String(args.question || '').trim();
          if (!question) return mkError('voice_ask: question is required');
          const timeout = Math.max(5, Number(args.timeout_seconds || 30));
          const lang = resolveLanguage(args);

          // 1. Speak the question
          await runPython('speak.py', [question, lang]);

          // 2. Listen for answer
          const answer = await runPython(
            'listen.py',
            [lang, timeout, config.micIndex],
            (timeout + 20) * 1000
          );
          if (!answer) return mkText('[voice] No response received (silence or timeout)');
          return mkText(answer);
        }

        // ── list_audio_devices ───────────────────────────────────────────────
        case 'list_audio_devices': {
          const raw = await runPython('devices.py', [], 15_000);
          let devices;
          try {
            devices = JSON.parse(raw);
          } catch {
            return mkText(raw);
          }
          if (devices.error) return mkError(`Audio device error: ${devices.error}`);
          const lines = devices.map((d) => {
            const tags = [];
            if (d.is_default_input) tags.push('DEFAULT_MIC');
            if (d.is_default_output) tags.push('DEFAULT_SPK');
            const tag = tags.length ? ` [${tags.join(', ')}]` : '';
            return `[${d.id}] ${d.name}${tag} – in:${d.max_input_channels} out:${d.max_output_channels} @ ${d.default_samplerate}Hz`;
          });
          return mkText(lines.join('\n'));
        }

        default:
          return mkError(`Unknown tool: ${name}`);
      }
    } catch (err) {
      return mkError(`Error in ${name}: ${err.message}`);
    }
  });

  return server;
}

export async function startServer() {
  const server = await createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // Running – stdio transport handles the message loop
}
