import { useState } from 'react';
import SearchBar from './components/SearchBar';
import ResultList from './components/ResultList';
import { searchJurisprudencia } from './services/api';

/**
 * Main application component.
 * Orchestrates search flow: input → API call → display results.
 */
export default function App() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchedQuery, setSearchedQuery] = useState('');

  const handleSearch = async (query) => {
    setIsLoading(true);
    setError(null);
    setSearchedQuery(query);

    const response = await searchJurisprudencia(query);

    if (response.error) {
      setError(response.error);
      setResults([]);
    } else {
      setResults(response.results || []);
    }

    setIsLoading(false);
  };

  const hasResults = results !== null;

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">⚖️</span>
            JurisSearch
          </div>
          <span className="logo-badge">MVP</span>
        </div>
      </header>

      <section className={`hero ${hasResults ? 'has-results' : ''}`}>
        <h1 className="hero-title">Busca de Jurisprudência Criminal</h1>
        <p className="hero-subtitle">
          Encontre decisões judiciais do TJSP de forma rápida e inteligente.
          Resultados classificados automaticamente.
        </p>
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      </section>

      <ResultList
        results={results}
        isLoading={isLoading}
        error={error}
        query={searchedQuery}
      />

      <footer className="footer">
        <p className="footer-text">
          JurisSearch MVP — Dados fornecidos pela API pública DATAJUD (CNJ/TJSP)
        </p>
      </footer>
    </div>
  );
}
