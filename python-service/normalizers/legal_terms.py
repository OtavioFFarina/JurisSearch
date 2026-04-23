"""Ordered list of legal terms mapping.

IMPORTANT: The order matters. 
Items with higher specificity should appear earlier in the list.
The matching process stops at the first match.

Tuple structure: ("termo específico minúsculo para busca", "termo_normalizado")
"""

LEGAL_MAPPING = [
    # Absolvição
    ("sentença absolutória", "sentenca_absolutoria"),
    ("absolvido", "absolvicao"),
    ("absolvição", "absolvicao"),
    ("improcedente", "absolvicao"),
    ("improcedência", "absolvicao"),
    ("inocentado", "absolvicao"),
    
    # Prisão / Trancamento / Extinção
    ("alvará de soltura expedido", "alvara_soltura_expedido"),
    ("alvará de soltura", "alvara_soltura"),
    ("trancamento", "trancamento_acao"),
    ("extinção da punibilidade", "extincao_punibilidade"),
    ("baixa definitiva", "baixa_definitiva"),
    ("arquivamento", "arquivamento"),

    # Condenação
    ("sentença condenatória", "sentenca_condenatoria"),
    ("condenado", "condenacao"),
    ("condenação", "condenacao"),
    ("procedente", "condenacao"),
    ("culpado", "condenacao"),
    ("trânsito em julgado", "transito_em_julgado"),

    # Sentença Genérica
    ("sentença", "sentenca_generica"),
    ("acórdão", "acordao_generico"),
    
    # Movimentações ordinárias
    ("documento juntado", "juntada_documento"),
    ("juntada", "juntada_documento"),
    ("mandado expedido", "mandado_expedido"),
    ("mandado devolvido", "mandado_devolvido"),
    ("conclusão", "conclusao"),
    ("vista", "vista_aberta"),
    ("publicado", "publicacao"),
    ("expedição", "expedicao_generica"),
    ("recebimento", "recebimento_generico"),
    ("remessa", "remessa_generica"),
    ("distribuição", "distribuicao"),
]
