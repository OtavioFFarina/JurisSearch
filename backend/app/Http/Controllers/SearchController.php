<?php

namespace App\Http\Controllers;

use App\Services\JurisprudenciaService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * Handles jurisprudencia search requests.
 *
 * Thin controller — all business logic is in JurisprudenciaService.
 */
class SearchController extends Controller
{
    private JurisprudenciaService $service;

    public function __construct(JurisprudenciaService $service)
    {
        $this->service = $service;
    }

    /**
     * Search for jurisprudencia.
     *
     * GET /api/search?q={term}
     */
    public function search(Request $request): JsonResponse
    {
        $query = $request->input('q', '');

        if (strlen(trim($query)) < 2) {
            return response()->json([
                'results' => [],
                'error' => 'query_too_short',
                'query' => $query,
            ], 422);
        }

        $result = $this->service->search(trim($query));

        $status = isset($result['error']) ? 503 : 200;

        return response()->json($result, $status);
    }
}
