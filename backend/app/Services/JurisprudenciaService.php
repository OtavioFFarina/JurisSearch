<?php

namespace App\Services;

use App\Repositories\JurisprudenciaRepositoryInterface;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

/**
 * Orchestrates jurisprudencia search through the Python service.
 *
 * Responsibilities:
 * - Call Python FastAPI service
 * - Handle failures gracefully (never throws to controller)
 * - Use repository for future caching/persistence
 */
class JurisprudenciaService
{
    private string $pythonUrl;
    private int $timeout;
    private JurisprudenciaRepositoryInterface $repository;

    public function __construct(JurisprudenciaRepositoryInterface $repository)
    {
        $this->pythonUrl = config('jurisprudencia.python_service_url');
        $this->timeout = config('jurisprudencia.python_service_timeout');
        $this->repository = $repository;
    }

    /**
     * Search for jurisprudencia by query term.
     *
     * @param string $query Search term
     * @return array Always returns a valid response structure
     */
    public function search(string $query): array
    {
        $normalizedQuery = trim(strtolower($query));
        $cacheKey = 'search_' . md5($normalizedQuery);
        $ttl = config('jurisprudencia.cache_ttl');

        // Check if we have it in cache first manually to log correctly
        if (\Illuminate\Support\Facades\Cache::has($cacheKey)) {
            Log::info('JurisprudenciaService: cache hit', ['query' => $normalizedQuery, 'cache_key' => $cacheKey]);
            return \Illuminate\Support\Facades\Cache::get($cacheKey);
        }

        // Call Python service on cache miss
        $result = $this->callPythonService($normalizedQuery);

        // Store successful results in Cache
        if (empty($result['error']) && !empty($result['results'])) {
            \Illuminate\Support\Facades\Cache::put($cacheKey, $result, $ttl);
            
            // Also keep repository storage if needed in the future
            $this->repository->store($normalizedQuery, $result);
        }

        return $result;
    }

    /**
     * Call the Python FastAPI service.
     *
     * @param string $query
     * @return array Always returns valid JSON structure
     */
    private function callPythonService(string $query): array
    {
        $url = $this->pythonUrl . '/search';

        Log::info('JurisprudenciaService: calling Python service', [
            'url' => $url,
            'query' => $query,
        ]);

        try {
            $response = Http::timeout($this->timeout)
                ->get($url, ['q' => $query]);

            if ($response->successful()) {
                $data = $response->json();
                Log::info('JurisprudenciaService: success', [
                    'query' => $query,
                    'results_count' => count($data['results'] ?? []),
                ]);
                return $data;
            }

            Log::warning('JurisprudenciaService: Python service returned error', [
                'status' => $response->status(),
                'body' => substr($response->body(), 0, 200),
            ]);

            return [
                'results' => [],
                'error' => 'python_service_error',
                'query' => $query,
            ];

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            Log::error('JurisprudenciaService: Python service unavailable', [
                'error' => $e->getMessage(),
            ]);

            return [
                'results' => [],
                'error' => 'service_unavailable',
                'query' => $query,
            ];

        } catch (\Exception $e) {
            Log::error('JurisprudenciaService: unexpected error', [
                'error' => $e->getMessage(),
            ]);

            return [
                'results' => [],
                'error' => 'internal_error',
                'query' => $query,
            ];
        }
    }
}
