import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  parseRuntimeIdentityMode,
  verifyRuntimePackageIdentity,
} from '../e2e/support/runtime-identity.ts';

const contractSha256 = 'c'.repeat(64);

function digest(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function withPackage(
  callback: (paths: {
    root: string;
    runtime: string;
    worker: string;
  }) => Promise<void>,
): Promise<void> {
  const root = await mkdtemp(join(tmpdir(), 'capture-runtime-identity-'));
  const runtime = join(root, 'capture-runtime.exe');
  const worker = join(root, 'capture-engine-ocr.zip');
  await writeFile(runtime, 'runtime bytes');
  await writeFile(worker, 'worker bytes');
  try {
    await callback({ root, runtime, worker });
  } finally {
    await rm(root, { recursive: true, force: true });
  }
}

function localInput(paths: { root: string; runtime: string; worker: string }) {
  return {
    mode: 'local-probe' as const,
    packageRoot: paths.root,
    runtimeExecutablePath: paths.runtime,
    ocrWorkerArchivePath: paths.worker,
    expectedContractSha256: contractSha256,
    probe: {
      runtimeExecutableSha256: digest('runtime bytes'),
      ocrWorkerSha256: digest('worker bytes'),
    },
    observed: {
      apiVersion: '2.0',
      ocrSchemaVersion: '3',
      contractSha256,
      loadedRuntimeSha256: digest('runtime bytes'),
      loadedOcrWorkerSha256: digest('worker bytes'),
    },
  };
}

test('local-probe accepts semver, app hash, inventory, and local direct_url drift as record-only metadata', async () => {
  await withPackage(async (paths) => {
    const result = await verifyRuntimePackageIdentity({
      ...localInput(paths),
      soft: {
        runtimeVersion: '0.4.1',
        expectedRuntimeVersion: '0.4.2',
        desktopHash: 'rebuilt-app',
        expectedDesktopHash: 'previous-app',
        allAssetInventoryMatches: false,
        directUrl: 'file:../capture-runtime',
        registryPure: false,
        frozenLockPure: false,
      },
    });

    assert.equal(result.mode, 'local-probe');
    assert.equal(result.soft.runtimeVersion, 'drift');
    assert.equal(result.soft.desktopHash, 'drift');
    assert.equal(result.soft.allAssetInventory, 'drift');
    assert.equal(result.soft.directUrl, 'present');
    assert.equal(result.soft.registryPurity, 'drift');
    assert.equal(result.soft.frozenLockPurity, 'drift');
  });
});

test('local-probe rejects a mixed runtime and OCR-worker core hash', async () => {
  await withPackage(async (paths) => {
    await assert.rejects(
      verifyRuntimePackageIdentity({
        ...localInput(paths),
        observed: {
          ...localInput(paths).observed,
          loadedRuntimeSha256: digest('different runtime'),
        },
      }),
      /runtime executable SHA.*probe/u,
    );
  });
});

test('local-probe rejects a source-tree import even when the bytes match', async () => {
  await withPackage(async (paths) => {
    const sourceRoot = join(paths.root, 'source-tree');
    await mkdir(sourceRoot);
    const sourceRuntime = join(sourceRoot, 'capture-runtime.exe');
    await writeFile(sourceRuntime, 'runtime bytes');
    await assert.rejects(
      verifyRuntimePackageIdentity({
        ...localInput({ ...paths, runtime: sourceRuntime }),
        sourceTreeRoots: [sourceRoot],
      }),
      /source-tree import/u,
    );
  });
});

test('identity mode is explicit and unknown values fail closed', () => {
  assert.equal(parseRuntimeIdentityMode('local-probe'), 'local-probe');
  assert.equal(parseRuntimeIdentityMode('release'), 'release');
  assert.throws(
    () => parseRuntimeIdentityMode('auto'),
    /must be local-probe or release/u,
  );
});

test('release identity keeps strict version, manifest, lock, download-back, and direct_url gates', async () => {
  await withPackage(async (paths) => {
    const base = {
      ...localInput(paths),
      mode: 'release' as const,
      expectedRuntimeVersion: '0.4.2',
      expectedRuntimeSha256: digest('runtime bytes'),
      observed: {
        ...localInput(paths).observed,
        runtimeVersion: '0.4.2',
      },
      release: {
        allArtifactManifestMatches: true,
        frozenLocksMatch: true,
        downloadBackBytesMatch: true,
      },
    };
    await assert.doesNotReject(verifyRuntimePackageIdentity(base));

    await assert.rejects(
      verifyRuntimePackageIdentity({
        ...base,
        observed: { ...base.observed, runtimeVersion: '0.4.1' },
      }),
      /exact runtime version/u,
    );
    await assert.rejects(
      verifyRuntimePackageIdentity({
        ...base,
        release: { ...base.release, frozenLocksMatch: false },
      }),
      /exact release gates/u,
    );
    await assert.rejects(
      verifyRuntimePackageIdentity({
        ...base,
        soft: { directUrl: 'file:../capture-runtime' },
      }),
      /local direct_url/u,
    );
  });
});
