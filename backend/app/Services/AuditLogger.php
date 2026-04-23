<?php

namespace App\Services;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * Append-only audit log writer.
 *
 * Rules (LGPD + professional secrecy):
 * - Never write cookies, passphrases, cipher keys, or client-identifying PII.
 * - CNJ is acceptable (public records).
 * - User-Agent is hashed (SHA-256) to prevent fingerprint leakage in dumps.
 * - IP is stored raw for incident response but must be purged after 12 months.
 * - No UPDATE/DELETE outside the scheduled retention job.
 */
class AuditLogger
{
    public function record(
        Request $request,
        string $action,
        ?User $user = null,
        ?string $cnj = null,
        string $outcome = 'ok',
        array $meta = [],
    ): void {
        DB::table('audit_log')->insert([
            'user_id' => $user?->id,
            'action' => substr($action, 0, 64),
            'cnj' => $cnj ? substr($cnj, 0, 32) : null,
            'outcome' => substr($outcome, 0, 32),
            'ip' => $request->ip(),
            'user_agent_hash' => hash('sha256', (string) $request->userAgent()),
            'meta' => $meta ? json_encode($this->redact($meta)) : null,
            'created_at' => now(),
        ]);
    }

    /**
     * Strip any field name that smells like a secret. Defense in depth —
     * callers should already have filtered these out.
     */
    private function redact(array $meta): array
    {
        $forbidden = [
            'password', 'passphrase', 'cookie', 'cookies', 'session',
            'token', 'secret', 'key', 'auth', 'credential', 'cert',
        ];

        foreach ($meta as $key => $value) {
            $lower = strtolower((string) $key);
            foreach ($forbidden as $needle) {
                if (str_contains($lower, $needle)) {
                    $meta[$key] = '[redacted]';
                    continue 2;
                }
            }
        }
        return $meta;
    }
}
