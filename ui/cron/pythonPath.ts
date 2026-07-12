import path from 'path';
import fs from 'fs';
import { TOOLKIT_ROOT } from './paths';

const isWindows = process.platform === 'win32';

// Shared resolver used by both the cron worker and Next.js API routes
// so the Python interpreter is configured in exactly one place.
export const resolvePythonPath = (): string => {
  // Allow overriding the Python path via environment variable.
  // Useful when the desired Python lives in a conda env or non-standard location.
  const envOverride = process.env.AITK_PYTHON_PATH;
  if (envOverride && envOverride.trim() !== '' && fs.existsSync(envOverride.trim())) {
    return envOverride.trim();
  }

  const candidates: string[] = [];

  if (isWindows) {
    candidates.push(path.join(TOOLKIT_ROOT, '.venv', 'Scripts', 'python.exe'));
    candidates.push(path.join(TOOLKIT_ROOT, 'venv', 'Scripts', 'python.exe'));
  } else {
    candidates.push(path.join(TOOLKIT_ROOT, '.venv', 'bin', 'python'));
    candidates.push(path.join(TOOLKIT_ROOT, 'venv', 'bin', 'python'));
  }

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return isWindows ? 'python.exe' : 'python3';
};
