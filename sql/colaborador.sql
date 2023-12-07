SELECT 
        pessoa.nome AS "FirstName"
        ,''::text AS "AuxText02"
        ,pessoa.cpf AS "AuxText04"
        ,vinculo.descricao AS "AuxLst04"
        ,CASE
          WHEN vinculo.descricao = 'EBSERH - CLT' THEN 'EBSERH'
          WHEN vinculo.descricao = 'EBSERH - REQUISITADO' THEN 'EBSERH'
          WHEN vinculo.descricao = 'PROFESSOR' THEN 'DOCENTE'
          WHEN vinculo.descricao = 'VINCULO INTEGRACAO' THEN 'INTEGRAÇÃO'
          WHEN vinculo.descricao = 'RJU - UFPE' THEN 'RJU'
          WHEN vinculo.descricao = 'NASS - UFPE' THEN 'RJU'
          ELSE vinculo.descricao
        END AS "AuxLst01"
        ,CONCAT(servidor.matricula, servidor.vin_codigo) AS "IdNumber" -- !!!!!CONCATENAR COM O CÓDIGO DO VÍNCULO!!!!!!!!!
        ,servidor.matricula AS "AuxText03"
        ,curso.descricao AS "AuxLst02"
        ,oca.descricao AS "AuxLst03"
        ,servidor.dt_inicio_vinculo::text  AS "AuxDte02"
        ,servidor.dt_fim_vinculo::text AS "AuxDte03"
        ,CASE
          WHEN (servidor.ind_situacao = 'A') THEN 0
          WHEN (servidor.ind_situacao = 'I') THEN 1
          ELSE 0 END AS "CHState"
        ,CASE
          WHEN (servidor.ind_situacao = 'A') THEN 'ATIVO'
          WHEN (servidor.ind_situacao = 'I') THEN 'INATIVO'
          ELSE 'PROGRAMADO' END AS "Status Servidor"
        ,CASE
          WHEN (servidor.alterado_em >= pessoa.criado_em) THEN servidor.alterado_em
          ELSE pessoa.criado_em END AS ultima_alteracao
        ,CASE
          WHEN vinculo.descricao = 'ESTUDANTE' THEN 8
          WHEN vinculo.descricao = 'BOLSISTA - ESTAGIARIO' THEN 8
          WHEN vinculo.descricao = 'RESIDENTE' THEN 8
          WHEN vinculo.descricao = 'VINCULO INTEGRACAO' THEN 3
          WHEN vinculo.descricao = 'RJU - UFPE' THEN 3
          WHEN vinculo.descricao = 'NASS - UFPE' THEN 3
          WHEN vinculo.descricao = 'EBSERH - CLT' THEN 3
          WHEN vinculo.descricao = 'TERCEIRIZADO' THEN 3
          WHEN vinculo.descricao = 'EBSERH - REQUISITADO' THEN 3
          WHEN vinculo.descricao = 'PROFESSOR' THEN 3
          WHEN vinculo.descricao = 'VOLUNTÁRIO' THEN 3
          ELSE 3
        END as "CHType"
        ,servidor.ind_situacao as "StatusAtual"
        ,ultima_alteracao.ind_situacao as "StatusAnterior"
    FROM agh.rap_servidores servidor
    LEFT JOIN agh.rap_pessoas_fisicas pessoa ON pessoa.codigo = servidor.pes_codigo
    LEFT JOIN agh.rap_vinculos vinculo ON vinculo.codigo = servidor.vin_codigo
    --LEFT JOIN agh.rap_qualificacoes quali ON pessoa.codigo = quali.pes_codigo
    LEFT JOIN (    
        select distinct on (pes_codigo)
            pes_codigo
            ,tql_codigo
            ,dt_atualizacao
        from agh.rap_qualificacoes 
        order by pes_codigo, dt_atualizacao desc
        ) as quali ON pessoa.codigo = quali.pes_codigo
    LEFT JOIN agh.rap_tipos_qualificacao curso ON  quali.tql_codigo = curso.codigo
    LEFT JOIN agh.rap_ocupacoes_cargo oca ON servidor.oca_car_codigo = oca.car_codigo AND servidor.oca_codigo = oca.codigo
    left join (select  distinct on (vin_codigo, matricula)
        vin_codigo
        ,matricula
        ,ind_situacao
    from agh.rap_servidores_jn servidor
    order by vin_codigo, matricula, alterado_em desc) as ultima_alteracao on servidor.matricula = ultima_alteracao.matricula and servidor.vin_codigo = ultima_alteracao.vin_codigo
    WHERE 
    -- servidor.ind_situacao != 'I' -- Excluir servidores inativos
    -- AND 
    vinculo.descricao != 'TERCEIRIZADO' -- Excluir servidores terceirizados que serão cadastrados no Invenzi diretamente.
    AND CASE WHEN (servidor.alterado_em >= pessoa.criado_em) THEN servidor.alterado_em ELSE pessoa.criado_em END >= '{}'
    ORDER By pessoa.nome