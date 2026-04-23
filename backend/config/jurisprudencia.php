<?php

return [
    /*
    |--------------------------------------------------------------------------
    | Python Service Configuration
    |--------------------------------------------------------------------------
    |
    | URL and timeout for the Python FastAPI service that handles
    | data collection, parsing and classification.
    |
    */
    'python_service_url' => env('PYTHON_SERVICE_URL', 'http://localhost:8001'),
    'python_service_timeout' => env('PYTHON_SERVICE_TIMEOUT', 5),
    'cache_ttl' => env('CACHE_TTL', 300), // Default 5 minutes
];
