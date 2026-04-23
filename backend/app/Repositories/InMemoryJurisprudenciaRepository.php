<?php

namespace App\Repositories;

/**
 * In-memory implementation of JurisprudenciaRepository.
 *
 * Placeholder for MVP — no actual persistence.
 * Replace with EloquentJurisprudenciaRepository when adding database.
 */
class InMemoryJurisprudenciaRepository implements JurisprudenciaRepositoryInterface
{
    /**
     * No cache in MVP — always returns null (cache miss).
     */
    public function findByQuery(string $query): ?array
    {
        return null;
    }

    /**
     * No-op in MVP — data is not persisted.
     */
    public function store(string $query, array $results): void
    {
        // Future: save to database
    }
}
