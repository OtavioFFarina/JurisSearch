<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Stores the lawyer's e-SAJ session credentials as an encrypted blob.
 *
 * Security invariants:
 * - `encrypted_cookie` is the WebCrypto AES-GCM ciphertext produced client-side
 *   using a key derived from the user's passphrase (PBKDF2). The server cannot
 *   decrypt it without that passphrase.
 * - Laravel adds a second encryption layer via Crypt::encrypt (defense in depth,
 *   so that a DB dump alone is useless even if the client-side key is exposed).
 * - No plaintext session cookie is ever persisted.
 * - Rows are deleted when `expires_at < now()` by the scheduled purge job.
 */
return new class extends Migration {
    public function up(): void
    {
        Schema::create('esaj_sessions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->text('encrypted_cookie');
            $table->string('salt', 64);
            $table->string('nonce', 64);
            $table->string('kdf_algo', 32)->default('PBKDF2-SHA256');
            $table->unsignedInteger('kdf_iterations')->default(600000);
            $table->timestamp('expires_at');
            $table->timestamp('last_used_at')->nullable();
            $table->string('created_ip', 45)->nullable();
            $table->string('user_agent_hash', 64)->nullable();
            $table->timestamps();

            $table->index(['user_id', 'expires_at']);
            $table->index('expires_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('esaj_sessions');
    }
};
