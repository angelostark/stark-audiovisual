/**
 * =====================================================================
 * AUTOMAÇÃO DE METAS — TIME AUDIOVISUAL STARK
 * =====================================================================
 *
 * Executa no dia 19 de cada mês automaticamente.
 *
 * FONTES:
 *   1. Planilha de Layouts    → "Novos Modelos de Layout" (20/20 = 100%, senão 0%)
 *   2. Planilha de Entregas   → "Prazo de Entrega de Demandas" (média % semanal)
 *
 * DESTINO:
 *   Planilha de Metas (aba com gid=386782566)
 *
 * SETUP:
 *   1. Abra a Planilha de Metas no Google Sheets
 *   2. Vá em Extensões > Apps Script
 *   3. Cole este código inteiro
 *   4. Execute a função configurarTriggerMensal() uma vez
 *   5. Autorize as permissões quando solicitado
 *   6. Pronto! Todo dia 19 roda automaticamente
 *
 * TESTE:
 *   Execute executarAutomacaoMetas() manualmente para testar
 * =====================================================================
 */

// =====================================================================
// CONFIGURAÇÃO — Altere aqui se os IDs mudarem
// =====================================================================

const CONFIG = {
  // Planilha de DESTINO (Metas)
  METAS_SPREADSHEET_ID: '1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc',
  METAS_GID: 386782566,

  // Planilha de LAYOUTS (Novos Modelos)
  LAYOUTS_SPREADSHEET_ID: '18IYDy4Pktx9f_86Jp-k6ErAXsFh7yKrPafcdhEvoa_o',

  // Planilha de ENTREGAS (Prazo de Entrega)
  ENTREGAS_SPREADSHEET_ID: '1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA',

  // Mapeamento de nomes (planilhas-fonte usam nomes completos, destino usa primeiro nome)
  // Chave: primeiro nome (como aparece na planilha de Metas)
  // Valor: nome completo (como aparece nas planilhas-fonte)
  NOMES: {
    'Eloy':     'Eloy Lopes',
    'Wygor':    'Wygor Matheus',
    'Humberto': 'Humberto Salles',
    'Fábio':    'Fábio Silva',
    'Karyne':   'Karyne Torres',
    'Milena':   'Milena Carneiro',
    'João':     'João',
    'Max':      'Max',
    'André':    'Andre Mello',
    'Ebertty':  'Ebertty Matnai',
    'Mateus':   'Mateus Redmann',
  },

  // Designers que participam da meta de Layouts (João e Max NÃO participam)
  DESIGNERS_LAYOUT: ['Eloy', 'Wygor', 'Humberto', 'Fábio', 'Karyne', 'Milena'],

  // E-mail para notificação (opcional)
  EMAIL_NOTIFICACAO: 'angelo@starkmkt.com',
};

// Meses em português para buscar abas
const MESES_PT = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

// =====================================================================
// FUNÇÃO PRINCIPAL
// =====================================================================

/**
 * Função principal — executa toda a automação.
 * Pode ser chamada manualmente para teste ou pelo trigger no dia 19.
 */
function executarAutomacaoMetas() {
  const log = [];
  log.push(`[${new Date().toLocaleString('pt-BR')}] Iniciando automação de metas...`);

  try {
    const hoje = new Date();
    const mesAtual = MESES_PT[hoje.getMonth()];
    const anoAtual = hoje.getFullYear();

    log.push(`Mês de referência: ${mesAtual} ${anoAtual}`);

    // 1. Buscar dados de LAYOUTS
    log.push('\n--- NOVOS MODELOS DE LAYOUT ---');
    const dadosLayouts = processarLayouts(mesAtual, anoAtual, log);

    // 2. Buscar dados de ENTREGAS
    log.push('\n--- PRAZO DE ENTREGA DE DEMANDAS ---');
    const dadosEntregas = processarEntregas(mesAtual, anoAtual, log);

    // 3. Escrever na planilha de Metas
    log.push('\n--- ESCREVENDO NA PLANILHA DE METAS ---');
    escreverNaMetas(dadosLayouts, dadosEntregas, log);

    log.push('\n✅ Automação concluída com sucesso!');

    // 4. Enviar notificação por e-mail
    enviarNotificacao(mesAtual, anoAtual, dadosLayouts, dadosEntregas, log);

  } catch (erro) {
    log.push(`\n❌ ERRO: ${erro.message}`);
    log.push(`Stack: ${erro.stack}`);

    // Notificar erro por e-mail
    try {
      MailApp.sendEmail(
        CONFIG.EMAIL_NOTIFICACAO,
        '❌ Erro na Automação de Metas AV',
        `A automação do dia 19 falhou.\n\nErro: ${erro.message}\n\nLog:\n${log.join('\n')}`
      );
    } catch (e) {
      // Silencioso se e-mail falhar
    }
  }

  // Salvar log
  console.log(log.join('\n'));
  return log.join('\n');
}

// =====================================================================
// PROCESSAMENTO DE LAYOUTS
// =====================================================================

/**
 * Lê a planilha de Layouts e verifica se cada designer tem 20/20 preenchidos.
 * Retorna: { 'Eloy': 1.0, 'Fábio': 0.0, ... } (1.0 = 100%, 0.0 = 0%)
 */
function processarLayouts(mes, ano, log) {
  const ss = SpreadsheetApp.openById(CONFIG.LAYOUTS_SPREADSHEET_ID);
  const aba = encontrarAbaPorMes(ss, mes, ano);

  if (!aba) {
    log.push(`⚠️ Aba de ${mes} ${ano} não encontrada na planilha de Layouts. Usando 0% para todos.`);
    const resultado = {};
    CONFIG.DESIGNERS_LAYOUT.forEach(nome => resultado[nome] = 0);
    return resultado;
  }

  log.push(`Aba encontrada: "${aba.getName()}"`);

  const dados = aba.getDataRange().getValues();
  const resultado = {};

  // A primeira linha tem o título, a segunda tem os nomes dos designers
  // Encontrar a linha de headers com nomes dos designers
  let headerRow = -1;
  for (let i = 0; i < Math.min(dados.length, 5); i++) {
    const row = dados[i].map(c => String(c).trim().toUpperCase());
    // Procurar linha que contém nomes de designers
    if (CONFIG.DESIGNERS_LAYOUT.some(nome => row.includes(nome.toUpperCase()))) {
      headerRow = i;
      break;
    }
  }

  if (headerRow === -1) {
    // Tentar formato alternativo: primeira coluna tem número/título, colunas seguintes são designers
    // Assumir que linha 0 ou 1 tem os nomes
    for (let i = 0; i < Math.min(dados.length, 3); i++) {
      for (let j = 0; j < dados[i].length; j++) {
        const celula = String(dados[i][j]).trim();
        if (CONFIG.DESIGNERS_LAYOUT.some(nome =>
          celula.toUpperCase().includes(nome.toUpperCase())
        )) {
          headerRow = i;
          break;
        }
      }
      if (headerRow !== -1) break;
    }
  }

  if (headerRow === -1) {
    log.push('⚠️ Não encontrei os nomes dos designers na planilha de Layouts.');
    CONFIG.DESIGNERS_LAYOUT.forEach(nome => resultado[nome] = 0);
    return resultado;
  }

  // Mapear coluna para cada designer
  const headers = dados[headerRow].map(c => String(c).trim());
  const colunasPorDesigner = {};

  CONFIG.DESIGNERS_LAYOUT.forEach(nome => {
    const idx = headers.findIndex(h =>
      h.toUpperCase().includes(nome.toUpperCase())
    );
    if (idx !== -1) {
      colunasPorDesigner[nome] = idx;
    }
  });

  log.push(`Designers mapeados: ${Object.keys(colunasPorDesigner).join(', ')}`);

  // Verificar linhas 1-20 após o header
  CONFIG.DESIGNERS_LAYOUT.forEach(nome => {
    const colIdx = colunasPorDesigner[nome];

    if (colIdx === undefined) {
      log.push(`  ${nome}: coluna não encontrada → 0%`);
      resultado[nome] = 0;
      return;
    }

    let preenchidos = 0;
    for (let i = headerRow + 1; i <= headerRow + 20 && i < dados.length; i++) {
      const valor = String(dados[i][colIdx] || '').trim();
      // Considerar preenchido se não for vazio, "-", "0" ou similar
      if (valor !== '' && valor !== '-' && valor !== '0' && valor !== 'undefined') {
        preenchidos++;
      }
    }

    resultado[nome] = preenchidos >= 20 ? 1.0 : 0.0;
    log.push(`  ${nome}: ${preenchidos}/20 preenchidos → ${resultado[nome] === 1 ? '100%' : '0%'}`);
  });

  return resultado;
}

// =====================================================================
// PROCESSAMENTO DE ENTREGAS
// =====================================================================

/**
 * Lê a planilha de Entregas e calcula a média da % de entrega por pessoa.
 * Retorna: { 'Eloy': 0.88, 'André': 0.95, ... } (valor decimal)
 */
function processarEntregas(mes, ano, log) {
  const ss = SpreadsheetApp.openById(CONFIG.ENTREGAS_SPREADSHEET_ID);
  const aba = encontrarAbaPorMes(ss, mes, ano);

  if (!aba) {
    log.push(`⚠️ Aba de ${mes} ${ano} não encontrada na planilha de Entregas. Usando 0% para todos.`);
    const resultado = {};
    Object.keys(CONFIG.NOMES).forEach(nome => resultado[nome] = 0);
    return resultado;
  }

  log.push(`Aba encontrada: "${aba.getName()}"`);

  const dados = aba.getDataRange().getValues();
  const resultado = {};

  // Estrutura: Semana | Nome | Posts a Entregar | Posts Entregues | %
  // Pode ter 2 tabelas lado a lado (Designers à esquerda, Editores à direita)
  // Precisamos agrupar por nome e calcular média da %

  const porcentagensPorPessoa = {};

  for (let i = 0; i < dados.length; i++) {
    const row = dados[i];

    // Percorrer a linha buscando padrões: nome seguido de números e percentual
    for (let j = 0; j < row.length; j++) {
      const celula = String(row[j] || '').trim();

      // Verificar se é um nome conhecido
      let nomeEncontrado = null;
      for (const [primeiroNome, nomeCompleto] of Object.entries(CONFIG.NOMES)) {
        if (celula === nomeCompleto || celula === primeiroNome ||
            celula.toUpperCase() === nomeCompleto.toUpperCase() ||
            celula.toUpperCase() === primeiroNome.toUpperCase()) {
          nomeEncontrado = primeiroNome;
          break;
        }
      }

      if (nomeEncontrado) {
        // Procurar a porcentagem nas colunas seguintes (geralmente 3 colunas depois)
        for (let k = j + 1; k < Math.min(j + 5, row.length); k++) {
          const valor = row[k];
          let percentual = null;

          if (typeof valor === 'number' && valor >= 0 && valor <= 1.5) {
            // Formato decimal (0.88 = 88%)
            percentual = valor;
          } else if (typeof valor === 'string') {
            const match = String(valor).replace(',', '.').match(/([\d.]+)%?/);
            if (match) {
              const num = parseFloat(match[1]);
              if (num >= 0 && num <= 150) {
                percentual = num > 1.5 ? num / 100 : num;
              }
            }
          }

          if (percentual !== null && percentual > 0) {
            if (!porcentagensPorPessoa[nomeEncontrado]) {
              porcentagensPorPessoa[nomeEncontrado] = [];
            }
            porcentagensPorPessoa[nomeEncontrado].push(percentual);
            break;
          }
        }
      }
    }
  }

  // Calcular média para cada pessoa
  for (const [nome, percentuais] of Object.entries(porcentagensPorPessoa)) {
    if (percentuais.length > 0) {
      const soma = percentuais.reduce((a, b) => a + b, 0);
      resultado[nome] = soma / percentuais.length;
      log.push(`  ${nome}: ${percentuais.length} semanas, média = ${(resultado[nome] * 100).toFixed(2)}%`);
    }
  }

  // Preencher com 0 quem não foi encontrado
  Object.keys(CONFIG.NOMES).forEach(nome => {
    if (!(nome in resultado)) {
      resultado[nome] = 0;
      log.push(`  ${nome}: não encontrado → 0%`);
    }
  });

  return resultado;
}

// =====================================================================
// ESCREVER NA PLANILHA DE METAS
// =====================================================================

/**
 * Escreve os dados calculados na planilha de Metas.
 */
function escreverNaMetas(dadosLayouts, dadosEntregas, log) {
  const ss = SpreadsheetApp.openById(CONFIG.METAS_SPREADSHEET_ID);
  const abas = ss.getSheets();

  // Encontrar aba pelo GID
  let abaMetas = null;
  for (const aba of abas) {
    if (aba.getSheetId() === CONFIG.METAS_GID) {
      abaMetas = aba;
      break;
    }
  }

  if (!abaMetas) {
    throw new Error(`Aba com GID ${CONFIG.METAS_GID} não encontrada na planilha de Metas.`);
  }

  log.push(`Aba de metas: "${abaMetas.getName()}"`);

  const dados = abaMetas.getDataRange().getValues();

  // Encontrar colunas relevantes pelo header
  let headerRow = -1;
  let colNome = -1;
  let colLayout = -1;
  let colPrazo = -1;

  for (let i = 0; i < Math.min(dados.length, 5); i++) {
    for (let j = 0; j < dados[i].length; j++) {
      const celula = String(dados[i][j] || '').trim().toLowerCase();

      if (celula.includes('nome') && celula.includes('prestador')) {
        headerRow = i;
        colNome = j;
      }
      if (celula.includes('novos modelos') || celula.includes('layout')) {
        colLayout = j;
      }
      if (celula.includes('prazo') && celula.includes('entrega')) {
        colPrazo = j;
      }
    }
    if (headerRow !== -1) break;
  }

  if (headerRow === -1 || colNome === -1) {
    throw new Error('Não encontrei os headers na planilha de Metas. Verifique a estrutura.');
  }

  log.push(`Headers na linha ${headerRow + 1}: Nome(col ${colNome + 1}), Layout(col ${colLayout + 1}), Prazo(col ${colPrazo + 1})`);

  // Percorrer as linhas de dados e preencher
  let preenchidos = 0;

  for (let i = headerRow + 1; i < dados.length; i++) {
    const nomeCelula = String(dados[i][colNome] || '').trim();
    if (!nomeCelula) continue;

    // Encontrar o primeiro nome correspondente
    let primeiroNome = null;
    for (const nome of Object.keys(CONFIG.NOMES)) {
      if (nomeCelula.toUpperCase().includes(nome.toUpperCase()) ||
          nome.toUpperCase().includes(nomeCelula.toUpperCase())) {
        primeiroNome = nome;
        break;
      }
    }

    if (!primeiroNome) {
      log.push(`  Linha ${i + 1}: "${nomeCelula}" não mapeado, pulando.`);
      continue;
    }

    // Preencher LAYOUT (se a coluna foi encontrada e o designer participa)
    if (colLayout !== -1) {
      if (primeiroNome in dadosLayouts) {
        const valorLayout = dadosLayouts[primeiroNome];
        abaMetas.getRange(i + 1, colLayout + 1).setValue(valorLayout);
        log.push(`  ${primeiroNome}: Layout = ${(valorLayout * 100).toFixed(0)}%`);
      } else {
        // João e Max não participam → 0%
        abaMetas.getRange(i + 1, colLayout + 1).setValue(0);
        log.push(`  ${primeiroNome}: Layout = 0% (não participa)`);
      }
    }

    // Preencher PRAZO DE ENTREGA (se a coluna foi encontrada)
    if (colPrazo !== -1) {
      const valorPrazo = dadosEntregas[primeiroNome] || 0;
      abaMetas.getRange(i + 1, colPrazo + 1).setValue(valorPrazo);
      log.push(`  ${primeiroNome}: Prazo = ${(valorPrazo * 100).toFixed(2)}%`);
    }

    preenchidos++;
  }

  log.push(`\nTotal: ${preenchidos} colaboradores atualizados.`);
}

// =====================================================================
// UTILITÁRIOS
// =====================================================================

/**
 * Encontra uma aba pelo nome do mês/ano.
 * Tenta variações: "Fevereiro 2026", "FEVEREIRO 2026", "Fev 2026", "02/2026", etc.
 */
function encontrarAbaPorMes(spreadsheet, mes, ano) {
  const abas = spreadsheet.getSheets();
  const mesUpper = mes.toUpperCase();
  const mesAbreviado = mes.substring(0, 3).toUpperCase();
  const mesNumero = String(MESES_PT.indexOf(mes) + 1).padStart(2, '0');

  // Padrões a tentar (em ordem de prioridade)
  const padroes = [
    mes,                          // "Fevereiro"
    `${mes} ${ano}`,              // "Fevereiro 2026"
    mesUpper,                     // "FEVEREIRO"
    `${mesUpper} ${ano}`,         // "FEVEREIRO 2026"
    mesAbreviado,                 // "FEV"
    `${mesAbreviado} ${ano}`,     // "FEV 2026"
    `${mesNumero}/${ano}`,        // "02/2026"
    `${mesNumero}-${ano}`,        // "02-2026"
    mes.toLowerCase(),            // "fevereiro"
    `${mes.toLowerCase()} ${ano}` // "fevereiro 2026"
  ];

  for (const padrao of padroes) {
    for (const aba of abas) {
      const nomeAba = aba.getName().trim();
      if (nomeAba === padrao || nomeAba.toUpperCase() === padrao.toUpperCase()) {
        return aba;
      }
    }
  }

  // Tentativa final: buscar aba que CONTÉM o nome do mês
  for (const aba of abas) {
    const nomeAba = aba.getName().toUpperCase();
    if (nomeAba.includes(mesUpper) || nomeAba.includes(mesAbreviado)) {
      return aba;
    }
  }

  return null;
}

// =====================================================================
// NOTIFICAÇÃO
// =====================================================================

/**
 * Envia e-mail com resumo da execução.
 */
function enviarNotificacao(mes, ano, dadosLayouts, dadosEntregas, log) {
  try {
    let corpo = `✅ Automação de Metas executada com sucesso!\n`;
    corpo += `📅 Referência: ${mes} ${ano}\n\n`;

    corpo += `📊 NOVOS MODELOS DE LAYOUT:\n`;
    for (const [nome, valor] of Object.entries(dadosLayouts)) {
      corpo += `  ${nome}: ${valor === 1 ? '100%' : '0%'}\n`;
    }

    corpo += `\n📊 PRAZO DE ENTREGA:\n`;
    for (const [nome, valor] of Object.entries(dadosEntregas)) {
      if (valor > 0) {
        corpo += `  ${nome}: ${(valor * 100).toFixed(2)}%\n`;
      }
    }

    corpo += `\n---\nLog completo:\n${log.join('\n')}`;

    MailApp.sendEmail(
      CONFIG.EMAIL_NOTIFICACAO,
      `✅ Metas AV ${mes} ${ano} — Automação concluída`,
      corpo
    );
  } catch (e) {
    console.log('Erro ao enviar e-mail: ' + e.message);
  }
}

// =====================================================================
// TRIGGER — CONFIGURAR UMA VEZ
// =====================================================================

/**
 * Configura o trigger para rodar todo dia 19 às 8h da manhã.
 * EXECUTE ESTA FUNÇÃO UMA VEZ para ativar a automação mensal.
 */
function configurarTriggerMensal() {
  // Remover triggers antigos desta função
  const triggers = ScriptApp.getProjectTriggers();
  for (const trigger of triggers) {
    if (trigger.getHandlerFunction() === 'executarNoDia19') {
      ScriptApp.deleteTrigger(trigger);
    }
  }

  // Criar trigger diário que verifica se é dia 19
  ScriptApp.newTrigger('executarNoDia19')
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();

  console.log('✅ Trigger configurado! A automação vai rodar todo dia 19 às 8h.');
}

/**
 * Função chamada pelo trigger diário.
 * Só executa se for dia 19.
 */
function executarNoDia19() {
  const hoje = new Date();
  if (hoje.getDate() === 19) {
    executarAutomacaoMetas();
  }
}

/**
 * Remove todos os triggers desta automação.
 */
function removerTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  let removidos = 0;
  for (const trigger of triggers) {
    if (trigger.getHandlerFunction() === 'executarNoDia19') {
      ScriptApp.deleteTrigger(trigger);
      removidos++;
    }
  }
  console.log(`${removidos} trigger(s) removido(s).`);
}
