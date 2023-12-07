SELECT 
  paciente.prontuario
FROM    agh.aac_consultas   cons 
INNER JOIN  agh.aip_pacientes   paciente  ON cons.pac_codigo = paciente.codigo
LEFT JOIN agh.mam_controles   controle  on cons.numero = controle.con_numero
WHERE   (cons.ind_sit_consulta = 'M') 
AND cons.fag_caa_seq != 10 -- Teleatendimento
AND cons.dt_consulta::DATE = CURRENT_DATE
union
SELECT 
  pac.prontuario
FROM    agh.ael_solicitacao_exames  soe
INNER JOIN  agh.ael_item_solicitacao_exames ise on ise.soe_seq = soe.seq
INNER JOIN  agh.agh_atendimentos    atd on atd.seq = soe.atd_seq
INNER JOIN  agh.aip_pacientes     pac   ON atd.pac_codigo = pac.codigo
LEFT JOIN   agh.ael_item_horario_agendados  ihe on ihe.ise_soe_seq  = ise.soe_seq and ihe.ise_seqp = ise.seqp
WHERE   ihe.hed_dthr_agenda::DATE = CURRENT_DATE
AND ise.sit_codigo != 'CA'
union
select 
  pac.prontuario
FROM    agh.mbc_cirurgias   cir
INNER JOIN  agh.aip_pacientes   pac   ON cir.pac_codigo = pac.codigo
INNER JOIN  agh.MBC_AGENDAS   agd on cir.agd_seq = agd.seq
where cir.data::date = current_date
and   cir.situacao != 'CANC' -- Cirurgias canceladas
and agd.ind_exclusao != 'S'