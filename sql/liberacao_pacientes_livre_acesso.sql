select 
	pac.prontuario
--	,ate.especialidade
--	,ate.data

from (
	SELECT 
		con.pac_codigo
	--	,INITCAP(esp.nome_especialidade)	as especialidade
		,max(con.dt_consulta::date)		as data

		
	FROM		agh.aac_consultas			as con
	LEFT JOIN 	agh.rap_servidores			as ser	on (ser.matricula = con.ser_matricula_alterado
									AND ser.vin_codigo = con.ser_vin_codigo_alterado)
	LEFT JOIN 	agh.rap_pessoas_fisicas			as pes	on ser.pes_codigo = pes.codigo -- Pega o CNS do Profissional
	inner join 	agh.aac_grade_agendamen_consultas	as gac	on con.grd_seq = gac.seq
	inner join	agh.agh_especialidades			as esp	on gac.esp_seq = esp.seq

	WHERE	(con.pac_codigo <> 1000001)
	AND	con.ret_seq = 10 -- Paciente Atendido
	AND	con.dt_consulta::date > CURRENT_DATE  - interval '2 months'

	and	(
		esp.seq = 1430 -- Hematologia
	or	esp.seq = 1466 -- Oncologia
	or	esp.seq = 1457 -- Transplante Renal
	or	esp.esp_seq = 1430 -- Hematologia Genérica
	or	esp.esp_seq = 1466 -- Oncologia Genérica
	or	esp.esp_seq = 1457 -- Transplante Renal Genérica
		)
	group by 1

	union
	SELECT
		ate.pac_codigo
	--	,unf.descricao 		
		,max(ate.dthr_fim)
	FROM  		agh.agh_atendimentos		ate
	LEFT JOIN 	agh.agh_unidades_funcionais	unf ON ate.unf_seq = unf.seq
	LEFT JOIN 	agh.agh_especialidades		esp ON ate.esp_seq = esp.seq
	 
	WHERE 	ate.int_seq IS NOT NULL
	AND	unf.seq = 177
	AND	(ate.dthr_fim is null or ate.dthr_fim::date > CURRENT_DATE  - interval '6 months')

	group by 1
) as ate
inner join agh.aip_pacientes pac on ate.pac_codigo = pac.codigo