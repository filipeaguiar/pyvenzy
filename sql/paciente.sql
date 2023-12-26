SELECT   
      P.NOME as "FirstName"
      ,P.NOME_SOCIAL as "AuxText02"
      ,P.CPF as "AuxText04"
      ,P.NOME_MAE as "AuxText06"
      ,P.DT_NASCIMENTO as "AuxDte02"
      ,P.PRONTUARIO as "IdNumber"
      ,'Livre Acesso' as "AuxLst05"
      ,CASE 
        WHEN (P.DT_RECADASTRO >= P.CRIADO_EM) THEN P.DT_RECADASTRO 
        ELSE P.CRIADO_EM 
      END AS modificado
    FROM   AGH.AIP_PACIENTES AS P   
    WHERE   (P.criado_em > '{}' OR P.dt_recadastro > '{}')
    AND dt_obito is null
    ORDER BY 1
