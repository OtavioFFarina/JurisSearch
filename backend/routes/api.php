<?php

use App\Http\Controllers\Auth\AuthController;
use App\Http\Controllers\SearchController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API routes
|--------------------------------------------------------------------------
| Public routes — no auth required (for now, jurisprudence search is open).
*/
Route::get('/search', [SearchController::class, 'search']);

/*
|--------------------------------------------------------------------------
| Auth routes (Sanctum SPA cookie-based)
|--------------------------------------------------------------------------
| Rate-limited to deter brute force against login and registration.
*/
Route::middleware('throttle:10,1')->group(function () {
    Route::post('/auth/register', [AuthController::class, 'register']);
    Route::post('/auth/login', [AuthController::class, 'login']);
});

Route::middleware('auth:sanctum')->group(function () {
    Route::get('/auth/me', [AuthController::class, 'me']);
    Route::post('/auth/logout', [AuthController::class, 'logout']);
});
