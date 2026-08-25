import { type ChildProcess, spawnSync } from 'node:child_process';
import net from 'node:net';
import { join } from 'node:path';

type OwnedRuntimeEvidence = {
  readonly pids: readonly number[];
  readonly listeners: readonly { readonly pid: number; readonly port: number }[];
};

function delay(milliseconds: number): Promise<void> {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));
}

export async function request<T>(
  port: number,
  token: string,
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${token}`,
      origin: 'http://tauri.localhost',
      ...init.headers,
    },
  });
  if (!response.ok) {
    const detail = (await response.text()).slice(0, 1_000);
    throw new Error(
      `Runtime request ${path} failed with HTTP ${response.status}${detail ? `: ${detail}` : '.'}`,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function reservePort(): Promise<number> {
  return new Promise((resolvePort, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      const port = typeof address === 'object' && address ? address.port : 0;
      server.close((error) => (error ? reject(error) : resolvePort(port)));
    });
  });
}

function windowsSystemExecutable(...segments: string[]): string {
  const systemRoot = Object.entries(process.env).find(
    ([name]) => name.toUpperCase() === 'SYSTEMROOT',
  )?.[1];
  if (!systemRoot) throw new Error('Windows SystemRoot is unavailable.');
  return join(systemRoot, ...segments);
}

function parseEvidence(value: unknown): OwnedRuntimeEvidence {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('Owned runtime process evidence was malformed.');
  }
  const payload = value as Record<string, unknown>;
  if (!Array.isArray(payload.pids) || !Array.isArray(payload.listeners)) {
    throw new Error('Owned runtime process evidence was malformed.');
  }
  const pids = payload.pids.map((value) => {
    if (!Number.isSafeInteger(value) || Number(value) < 1) {
      throw new Error('Owned runtime PID was invalid.');
    }
    return Number(value);
  });
  const listeners = payload.listeners.map((value) => {
    if (value === null || typeof value !== 'object' || Array.isArray(value)) {
      throw new Error('Owned runtime listener was invalid.');
    }
    const listener = value as Record<string, unknown>;
    if (
      !Number.isSafeInteger(listener.pid) ||
      Number(listener.pid) < 1 ||
      !Number.isSafeInteger(listener.port) ||
      Number(listener.port) < 1 ||
      Number(listener.port) > 65535
    ) {
      throw new Error('Owned runtime listener was invalid.');
    }
    return { pid: Number(listener.pid), port: Number(listener.port) };
  });
  return { pids, listeners };
}

function runObserver(script: string): OwnedRuntimeEvidence {
  const result = spawnSync(
    windowsSystemExecutable(
      'System32',
      'WindowsPowerShell',
      'v1.0',
      'powershell.exe',
    ),
    ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script],
    { encoding: 'utf8', windowsHide: true, timeout: 15_000 },
  );
  if (result.error || result.status !== 0 || !result.stdout.trim()) {
    throw new Error('Owned runtime process observer failed.');
  }
  return parseEvidence(JSON.parse(result.stdout) as unknown);
}

function observeOwnedRuntimeTree(rootPid: number): OwnedRuntimeEvidence {
  return runObserver(`
$rootPid = ${String(rootPid)}
$processes = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
$owned = [System.Collections.Generic.HashSet[int]]::new()
[void]$owned.Add($rootPid)
do {
  $changed = $false
  foreach ($item in $processes) {
    if ($owned.Contains([int]$item.ParentProcessId) -and $owned.Add([int]$item.ProcessId)) {
      $changed = $true
    }
  }
} while ($changed)
$listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $owned.Contains([int]$_.OwningProcess) } |
  ForEach-Object { [pscustomobject]@{ pid = [int]$_.OwningProcess; port = [int]$_.LocalPort } })
[pscustomobject]@{ pids = @($owned | Sort-Object); listeners = $listeners } | ConvertTo-Json -Compress
`);
}

function observeKnownRuntimeProcesses(pids: readonly number[]): OwnedRuntimeEvidence {
  if (pids.length === 0) return { pids: [], listeners: [] };
  return runObserver(`
$known = @(${pids.join(',')})
$live = @(Get-Process -Id $known -ErrorAction SilentlyContinue | ForEach-Object { [int]$_.Id })
$knownSet = [System.Collections.Generic.HashSet[int]]::new()
foreach ($processId in $known) { [void]$knownSet.Add([int]$processId) }
$listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $knownSet.Contains([int]$_.OwningProcess) } |
  ForEach-Object { [pscustomobject]@{ pid = [int]$_.OwningProcess; port = [int]$_.LocalPort } })
[pscustomobject]@{ pids = $live; listeners = $listeners } | ConvertTo-Json -Compress
`);
}

function isProcessAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

export async function terminateOwnedTree(child: ChildProcess): Promise<void> {
  const pid = child.pid;
  if (!pid) throw new Error('Owned Capture Runtime did not expose a PID.');
  const owned = observeOwnedRuntimeTree(pid);
  if (isProcessAlive(pid)) {
    const terminated = spawnSync(
      windowsSystemExecutable('System32', 'taskkill.exe'),
      ['/PID', String(pid), '/T', '/F'],
      { stdio: 'ignore', windowsHide: true },
    );
    if (terminated.error && isProcessAlive(pid)) throw terminated.error;
  }
  const deadline = Date.now() + 10_000;
  let remaining = observeKnownRuntimeProcesses(owned.pids);
  while (
    Date.now() < deadline &&
    (remaining.pids.length > 0 || remaining.listeners.length > 0)
  ) {
    await delay(100);
    remaining = observeKnownRuntimeProcesses(owned.pids);
  }
  if (remaining.pids.length > 0 || remaining.listeners.length > 0) {
    throw new Error(
      `Owned runtime cleanup left ${remaining.pids.length} process(es) and ${remaining.listeners.length} listener(s).`,
    );
  }
}
