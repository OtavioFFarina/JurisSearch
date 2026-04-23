import ResultCard from './ResultCard';

/**
 * Renders the list of results with info bar,
 * loading skeletons, error state, and empty state.
 */
export default function ResultList({ results, isLoading, error, query }) {
  // Loading state — skeleton cards
  if (isLoading) {
    return (
      <div className="main-content">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <span className="loading-text">Buscando jurisprudência para "{query}"...</span>
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton-line skeleton-line-title"></div>
            <div className="skeleton-line skeleton-line-meta"></div>
            <div className="skeleton-line skeleton-line-text"></div>
            <div className="skeleton-line skeleton-line-text-short"></div>
          </div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    const errorMessages = {
      'service_unavailable': 'O serviço de busca está temporariamente indisponível.',
      'connection_error': 'Não foi possível conectar ao servidor.',
      'request_timeout': 'A busca demorou demais. Tente novamente.',
      'python_service_error': 'O serviço de dados está temporariamente indisponível.',
      'data_source_unavailable': 'A fonte de dados do tribunal está indisponível.',
      'query_too_short': 'Digite pelo menos 2 caracteres para buscar.',
    };

    return (
      <div className="main-content">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h2 className="error-title">Não foi possível buscar dados no momento</h2>
          <p className="error-message">
            {errorMessages[error] || 'Ocorreu um erro inesperado. Tente novamente em alguns instantes.'}
          </p>
        </div>
      </div>
    );
  }

  // No results after search
  if (results && results.length === 0 && query) {
    return (
      <div className="main-content">
        <div className="empty-container">
          <div className="empty-icon">📭</div>
          <h2 className="empty-title">Nenhum resultado encontrado para "{query}"</h2>
        </div>
      </div>
    );
  }

  // No search performed yet
  if (!results || results.length === 0) {
    return null;
  }

  // Results list
  return (
    <div className="main-content">
      <div className="results-info">
        <span className="results-count">
          <strong>{results.length}</strong> resultado{results.length !== 1 ? 's' : ''} encontrado{results.length !== 1 ? 's' : ''} para "{query}"
        </span>
      </div>

      {results.map((item, index) => (
        <ResultCard key={`${item.processo}-${index}`} item={item} index={index} />
      ))}
    </div>
  );
}
