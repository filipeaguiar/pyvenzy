SELECT
  acom.NOME as "FirstName"
  ,acom.rg as "IdNumber"
  ,pac.prontuario as "PacienteId"
  ,'Internação'::text as "tipo"
  ,acom.dthr_inicio::date as "CHStartValidityDateTime"
  ,acom.dthr_fim::date as "CHEndValidityDateTime"
  ,CASE
     WHEN cracha.tipo_credito_refeitorio IS NULL THEN false
     WHEN cracha.tipo_credito_refeitorio = 0 THEN false
     ELSE true
  END as "AcessoRefeitorio"
FROM agh.ain_internacoes inte 
INNER JOIN agh.aip_pacientes pac ON pac.codigo = inte.pac_codigo
INNER JOIN AGH.AIN_ACOMPANHANTES_INTERNACAO acom on acom.int_seq = inte.seq
left join agh.ain_cracha_acompanhantes cracha on (cracha.aci_int_seq = acom.int_seq and cracha.aci_seq = acom.seq)
where inte.dt_saida_paciente is null
AND acom.criado_em >= '{}'
order by 1