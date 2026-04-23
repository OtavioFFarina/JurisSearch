<?php

namespace App\Repositories;

/**
 * Interface for jurisprudencia data access.
 *
 * Currently a pass-through (no database), but defines the contract
 * for future persistence. When adding a database:
 * 1. Create EloquentJurisprudenciaRepository implementing this interface
 * 2. Bind in AppServiceProvider
 * 3. No changes needed in Controller or Service
 */
interface JurisprudenciaRepositoryInterface
{
    /**
     * Find cached results for a query (future: from database).
     *
     * @param string $query
     * @return array|null Null means cache miss / no stored data
     */
    public function findByQuery(string $query): ?array;

    /**
     * Store search results (future: persist to database).
     *
     * @param string $query
     * @param array $results
     * @return void
     */
    public function store(string $query, array $results): void;
}
