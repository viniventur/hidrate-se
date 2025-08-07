# 💧 Hidrate-se

O **Hidrate-se** é um aplicativo web interativo, desenvolvido com [Streamlit](https://streamlit.io/), que incentiva o consumo diário adequado de água de forma divertida e visual. Ele permite que usuários registrem suas ingestões de água, acompanhem metas diárias com base no peso corporal e visualizem rankings de desempenho da equipe.

---

## 🚀 Funcionalidades

- **Cálculo de meta diária de água:** com base no peso corporal (35ml por kg).
- **Conversão de mililitros para litros:** ferramenta prática para ajudar na contagem.
- **Registro de consumo diário de água:** com escolha de data e horário personalizado.
- **Feedback de meta atingida:** indica se a meta diária foi atingida.
- **Ranking dos usuários:** mostra quem mais atingiu a meta de consumo.
- **Gráficos interativos:** consumo médio diário e desempenho por usuário.
- **Tabela com filtros:** registros completos por nome e período.

---

## 🧰 Backend e Armazenamento de Dados

Os dados do app **Hidrate-se** são armazenados em planilhas do **Google Sheets**, funcionando como um banco de dados leve e colaborativo. A integração é feita por meio da biblioteca `gspread` e credenciais de conta de serviço do Google.

### 🔌 Principais componentes do backend:

- **Autenticação via Google Service Account**
- **Planilhas utilizadas:**
  - `base_pessoal` → informações dos usuários (nome, peso, link da foto)
  - `base_acompanhamento` → registros de consumo de água
- **Funções principais:**
  - `read_data()` → leitura geral da planilha
  - `add_data()` → inserção de novas linhas
  - `obter_dados_acompanhamento()` → dados tratados para análise
  - `dados_analise_meta()` → cálculo de metas e junção com dados pessoais


## 📊 Exemplo de Uso

- João informa que pesa 80kg → o app recomenda 2,8 litros de água por dia.
- Ele registra que bebeu 1L de manhã, 1L à tarde e 0,8L à noite.
- O sistema indica que ele bateu a meta e exibe uma animação comemorativa.

Ao final do dia, o ranking é atualizado com base na meta atingida.

