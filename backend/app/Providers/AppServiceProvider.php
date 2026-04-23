<?php

namespace App\Providers;

use App\Repositories\InMemoryJurisprudenciaRepository;
use App\Repositories\JurisprudenciaRepositoryInterface;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // Bind repository interface to in-memory implementation.
        // When adding a database, swap to EloquentJurisprudenciaRepository here.
        $this->app->bind(
            JurisprudenciaRepositoryInterface::class,
            InMemoryJurisprudenciaRepository::class
        );
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
    }
}
