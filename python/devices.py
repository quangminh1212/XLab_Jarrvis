#!/usr/bin/env python3
"""
List available audio devices for MCP Voice Bridge.

Usage: python devices.py
Output: JSON array of device objects on stdout.
"""
import json
import sys
import sounddevice as sd


def main():
    try:
        devices_raw = sd.query_devices()
        default_in = sd.default.device[0]
        default_out = sd.default.device[1]

        result = []
        for i, d in enumerate(devices_raw):
            result.append({
                'id': i,
                'name': d['name'],
                'max_input_channels': int(d['max_input_channels']),
                'max_output_channels': int(d['max_output_channels']),
                'default_samplerate': int(d['default_samplerate']),
                'is_input': d['max_input_channels'] > 0,
                'is_output': d['max_output_channels'] > 0,
                'is_default_input': i == default_in,
                'is_default_output': i == default_out,
            })

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
