import { useState } from 'react';

/**
 * Single result card component.
 * Displays case information with classification and confidence badges.
 * Supports expanding to view all movements.
 */
export default function ResultCard({ item, index }) {
  const [expanded, setExpanded] = useState(false);

  const { titulo, processo, tribunal, resumo, resultado, confidence, justificativa, movimentos } = item;

  const badgeConfig = {
    'favorável': { class: 'badge-favoravel', label: 'Favorável' },
    'desfavorável': { class: 'badge-desfavoravel', label: 'Desfavorável' },
    'neutro': { class: 'badge-neutro', label: 'Neutro' },
  };

  const confidenceConfig = {
    'alta': { class: 'badge-alta', label: 'Alta Confiança' },
    'media': { class: 'badge-media', label: 'Média Confiança' },
    'baixa': { class: 'badge-baixa', label: 'Baixa Confiança' },
  };

  const badge = badgeConfig[resultado] || badgeConfig['neutro'];
  const confBadge = confidence ? (confidenceConfig[confidence] || confidenceConfig['baixa']) : null;

  return (
    <article
      className="result-card"
      style={{ animationDelay: `${index * 0.08}s` }}
      id={`result-card-${index}`}
    >
      <div className="card-header">
        {titulo && <h3 className="card-titulo">{titulo}</h3>}
        <div className="badge-group">
          <span className={`badge ${badge.class}`}>
            <span className="badge-dot"></span>
            {badge.label}
          </span>
          {confBadge && (
            <span className={`badge ${confBadge.class}`}>
              {confBadge.label}
            </span>
          )}
        </div>
      </div>

      <div className="card-meta">
        {processo && (
          <span className="card-meta-item">
            <span className="card-meta-icon">📋</span>
            {processo}
          </span>
        )}
        {tribunal && (
          <span className="card-meta-item">
            <span className="card-meta-icon">🏛️</span>
            {tribunal}
          </span>
        )}
      </div>

      {resumo && resumo !== 'Sem movimentações disponíveis.' && !expanded && (
        <p className="card-resumo">{resumo}</p>
      )}

      {justificativa && (
        <div className="card-justificativa">
          <strong>Motivo: </strong>
          <span>{justificativa}</span>
        </div>
      )}

      {movimentos && movimentos.length > 0 && (
        <div className="card-actions">
          <button 
            onClick={() => setExpanded(!expanded)} 
            className="btn-toggle-details"
          >
            {expanded ? "Ocultar Detalhes" : "Ver Processo Completo"}
          </button>
        </div>
      )}

      {expanded && movimentos && (
        <div className="card-details">
          <h4>Histórico de Movimentações (Recentes)</h4>
          <ul className="movimentos-list">
            {movimentos.map((mov, i) => (
              <li key={i} className="movimento-item">
                <span className="movimento-data">
                  {mov.data ? new Date(mov.data).toLocaleDateString('pt-BR') : 'Data não informada'}
                </span>
                <span className="movimento-texto">{mov.movimento_original}</span>
                {/* Optional Debug Note: <span className="movimento-debug">({mov.movimento_normalizado})</span> */}
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}
