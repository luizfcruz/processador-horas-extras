# 🕒 Processador de Horas Extras  
Aplicação desktop desenvolvida em **Python + Tkinter** para automatizar o cálculo de horas extras, organizar registros de ponto e gerar relatórios detalhados.

Este projeto nasceu de uma necessidade real: processar grandes volumes de registros de ponto em TXT, identificar horários trabalhados em finais de semana/feriados e gerar relatórios claros para uso administrativo.

---

## 🖼️ Interface do Sistema

<p align="center">
  <img src="img/interface_principal.png" width="60%">
</p>

<p align="center">
  <img src="img/cadastro_funcionario.png" width="60%">
</p>

<p align="center">
  <img src="img/exclusao_funcionario.png" width="60%">
</p>

---

## 📌 Funcionalidades Principais

### ✔️ Processamento de Registros
- Importa arquivos `.txt` contendo registros de ponto.
- Identifica automaticamente:
  - Hora de entrada
  - Hora de saída
  - Dias úteis, sábados, domingos e feriados
  - Funcionários com regras especiais de horário
- Calcula:
  - Horas 50%
  - Horas 100%
  - Total de horas trabalhadas no período

---

## 👨‍💼 Gestão de Funcionários
- Cadastro de novos funcionários  
- Exclusão de funcionários  
- Armazenamento estruturado em `dados_funcionarios.json`  
- Suporte a:
  - Nome  
  - CPF  
  - Matrícula  
  - Função  
  - Setor  

---

## 📄 Geração de Relatórios

### 📘 Relatório Detalhado
Lista cada dia trabalhado por funcionário, contendo:
- Nome  
- Data  
- Hora de entrada  
- Hora de saída  
- Horas computadas  

### 🧾 Resumo Geral
Disponível em dois formatos:
- **TXT**
- **JSON**

Inclui:
- Horas 50%
- Horas 100%
- Total acumulado

---

## 🛠️ Tecnologias Utilizadas
- Python 3  
- Tkinter (Interface gráfica)  
- Pandas  
- JSON  
- Regex  
- Holidays (para feriados nacionais)  
- Pillow (para imagens PNG)

---

## 🚀 Evolução Planejada (Versão 2.0)
- Modularização completa  
- Documentação detalhada com docstrings  
- Interface atualizada  
- Exportação para Excel  
- Melhorias de performance  
- Geração de instalador (.exe)

---

## 👤 Autor
**Luiz Fernando Cruz**  
Desenvolvedor | Analista de Dados  

---

## 🤝 Agradecimento
Projeto desenvolvido com apoio do **ChatGPT**, auxiliando na organização, lógica e construção da interface.

---

## 📌 Licença
Este projeto é de uso pessoal e pode ser adaptado livremente.


📁 uploads/ — Esta pasta não faz parte do repositório porque contém arquivos carregados pelo usuário. O app cria automaticamente a pasta caso ela não exista.
