<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Append-only audit log for LGPD compliance and professional-secrecy traceability.
 *
 * Rules:
 * - This table is append-only (no UPDATE, no DELETE outside the retention job).
 * - It must never contain: passphrases, cookies, cipher keys, client PII beyond CNJ.
 * - CNJ numbers are stored as identifiers — they are public-records by nature.
 * - Retention: 5 years (OAB-compliance baseline). Deleted by scheduled purge.
 */
return new class extends Migration {
    public function up(): void
    {
        Schema::create('audit_log', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->string('action', 64);
            $table->string('cnj', 32)->nullable();
            $table->string('outcome', 32)->nullable();
            $table->string('ip', 45)->nullable();
            $table->string('user_agent_hash', 64)->nullable();
            $table->json('meta')->nullable();
            $table->timestamp('created_at')->useCurrent();

            $table->index(['user_id', 'created_at']);
            $table->index('action');
            $table->index('cnj');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('audit_log');
    }
};
