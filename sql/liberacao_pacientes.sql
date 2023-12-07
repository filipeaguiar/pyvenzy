With prontuarios_alterados as (
  SELECT --Agendamento de Consulta Ambulatorial
    cons.pac_codigo
    ,'Consulta Libera'::text situacao
  FROM    agh.aac_consultas   cons
  WHERE   (cons.ind_sit_consulta = 'M') 
  AND cons.ret_seq = 9 -- Agendado
  AND cons.fag_caa_seq != 10 -- Teleatendimento
  AND cons.alterado_em > '{} -03:00:00'
  AND cons.dt_consulta::DATE = CURRENT_DATE
  UNION
  SELECT --Cancelamento de Consulta Ambulatorial 
    hist_cons.pac_codigo
    ,'Consulta Bloqueia'::text situacao
--    ,hist_cons.jn_date_time
  from AGH.AAC_CONSULTAS_JN hist_cons
  where   hist_cons.dt_consulta::DATE = CURRENT_DATE
  AND hist_cons.jn_date_time > '{} -03:00:00'
  and ((hist_cons.jn_operation = 'DEL' 
    and hist_cons.pac_codigo is not null)
  or (hist_cons.jn_operation = 'UPD' 
    and hist_cons.stc_situacao = 'M' ))
  UNION
  SELECT -- Marcação de Cirurgias
    cir.pac_codigo
    ,'Cirurgia Libera'::text situacao
--    ,cir.criado_em
  FROM    agh.mbc_cirurgias   cir
  INNER JOIN  agh.MBC_AGENDAS   agd ON cir.agd_seq = agd.seq
  WHERE cir.data::DATE = CURRENT_DATE
  AND cir.criado_em > '{} -03:00:00'
  AND   cir.situacao != 'CANC' -- Cirurgias canceladas
  AND agd.ind_exclusao != 'S'
  UNION
  SELECT -- Cancelamento de Cirurgias
    cir.pac_codigo
    ,'Cirurgia Bloqueia'::text situacao
--    ,jn_date_time
  FROM    agh.mbc_cirurgias_jn  cir_jn
  INNER JOIN  agh.mbc_cirurgias   cir ON (cir.seq = cir_jn.seq and cir.pac_codigo = cir_jn.pac_codigo and cir.situacao = 'CANC')
  WHERE cir.data::DATE = CURRENT_DATE
  AND	cir_jn.jn_date_time > '{} -03:00:00'
  UNION
  SELECT -- Marcação de Exames
    atd.pac_codigo
    ,'Exames Libera'::text situacao
--    ,hed.alterado_em
  FROM    agh.ael_solicitacao_exames  soe
  INNER JOIN  agh.agh_atendimentos    atd on atd.seq = soe.atd_seq
  INNER JOIN  agh.ael_item_solicitacao_exames ise on ise.soe_seq = soe.seq
  LEFT JOIN   agh.ael_item_horario_agendados  ihe on ihe.ise_soe_seq  = ise.soe_seq and ihe.ise_seqp = ise.seqp
  LEFT JOIN agh.ael_horario_exame_disps   hed on (hed_gae_unf_seq = hed.gae_unf_seq and hed_gae_seqp = hed.gae_seqp and hed_dthr_agenda = hed.dthr_agenda)
  WHERE   ihe.hed_dthr_agenda::DATE = CURRENT_DATE
  AND ise.sit_codigo != 'CA'
  AND hed.alterado_em > '{} -03:00:00'
),
prontuarios_marcacao as (
SELECT distinct -- Consultas
  cons.pac_codigo
  ,'Consulta'::text as situacao_marc
FROM    agh.aac_consultas   cons 
LEFT JOIN agh.mam_controles   controle  on cons.numero = controle.con_numero
WHERE   (cons.ind_sit_consulta = 'M') 
AND cons.fag_caa_seq != 10 -- Teleatendimento
AND cons.dt_consulta::DATE = CURRENT_DATE
UNION
SELECT distinct -- Exames
  atd.pac_codigo
  ,'Exame'::text as situacao
FROM    agh.ael_solicitacao_exames  soe
INNER JOIN  agh.ael_item_solicitacao_exames ise on ise.soe_seq = soe.seq
INNER JOIN  agh.agh_atendimentos    atd on atd.seq = soe.atd_seq
LEFT JOIN   agh.ael_item_horario_agendados  ihe on ihe.ise_soe_seq  = ise.soe_seq and ihe.ise_seqp = ise.seqp
WHERE   ihe.hed_dthr_agenda::DATE = CURRENT_DATE
UNION
select distinct -- Cirurgias
  cir.pac_codigo
  ,'Cirurgia'::text as situacao
FROM    agh.mbc_cirurgias   cir
INNER JOIN  agh.MBC_AGENDAS   agd on cir.agd_seq = agd.seq
where cir.data::date = CURRENT_DATE
and   cir.situacao != 'CANC' -- Cirurgias canceladas
and agd.ind_exclusao != 'S'
order by 1
)
select 
  p.prontuario as "IdNumber"
  --,pm.situacao_marc
  --,pa.* 
  --,pa.situacao
  ,case when (pm.pac_codigo is null) then 1 ELSE 0 END as "CHState"
from    prontuarios_alterados pa
left join   prontuarios_marcacao  pm on pa.pac_codigo = pm.pac_codigo
INNER JOIN  agh.aip_pacientes p  on p.codigo = pa.pac_codigo
order by 1