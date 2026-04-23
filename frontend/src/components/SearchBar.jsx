import { useState } from 'react';

/**
 * Search bar component with input and submit button.
 * Handles form submission and disables during loading.
 */
export default function SearchBar({ onSearch, isLoading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed.length >= 2 && !isLoading) {
      onSearch(trimmed);
    }
  };

  return (
    <div className="search-container">
      <form className="search-bar" onSubmit={handleSubmit}>
        <input
          id="search-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar jurisprudência criminal... ex: furto, homicídio, tráfico"
          autoFocus
          disabled={isLoading}
        />
        <span className="search-icon">🔍</span>
        <button
          id="search-button"
          type="submit"
          className="search-button"
          disabled={isLoading || query.trim().length < 2}
        >
          {isLoading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>
    </div>
  );
}
