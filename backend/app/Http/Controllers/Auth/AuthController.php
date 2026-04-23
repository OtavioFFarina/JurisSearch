<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Services\AuditLogger;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules\Password;

/**
 * Sanctum-backed cookie auth for the React SPA.
 *
 * The lawyer-facing auth surface. Uses session-cookie auth (not bearer tokens)
 * so XSS cannot exfiltrate the credential as easily — tokens in localStorage
 * are the classic XSS target.
 */
class AuthController extends Controller
{
    public function __construct(private AuditLogger $audit) {}

    public function register(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'email', 'max:255', 'unique:users,email'],
            'password' => ['required', 'confirmed', Password::defaults()->min(12)->letters()->numbers()->symbols()],
        ]);

        $user = User::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => Hash::make($data['password']),
        ]);

        Auth::login($user);
        $request->session()->regenerate();

        $this->audit->record($request, 'auth.register', user: $user, outcome: 'ok');

        return response()->json(['user' => $user->only('id', 'name', 'email')], 201);
    }

    public function login(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required', 'string'],
        ]);

        if (! Auth::attempt($data, remember: false)) {
            $this->audit->record($request, 'auth.login', outcome: 'failed', meta: ['email_attempt' => $data['email']]);
            return response()->json(['message' => 'Credenciais inválidas.'], 422);
        }

        $request->session()->regenerate();
        $user = $request->user();

        $this->audit->record($request, 'auth.login', user: $user, outcome: 'ok');

        return response()->json(['user' => $user->only('id', 'name', 'email')]);
    }

    public function logout(Request $request): JsonResponse
    {
        $user = $request->user();
        $this->audit->record($request, 'auth.logout', user: $user, outcome: 'ok');

        Auth::guard('web')->logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return response()->json(['message' => 'Sessão encerrada.']);
    }

    public function me(Request $request): JsonResponse
    {
        $user = $request->user();
        return response()->json(['user' => $user->only('id', 'name', 'email')]);
    }
}
