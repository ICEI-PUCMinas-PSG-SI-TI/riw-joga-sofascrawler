## **Tema do Trabalho**
### **Sistemas para Coleta de Informações de Times e Jogadores de Futebol**
- **Objetivo:** Desenvolver um sistema de coleta de dados para análise estatística de times e jogadores, visando calcular probabilidades em plataformas de apostas online.

---

## **Equipe**
- **João Mello**:
- **Christian David Costa Vieira**:
- **Débora de Castro Sousa**
- **Joao Henrique Pereira Veloso Pimentel de Mello**
- **João Pedro Moreira Sena**
- **Nicolas Matheus Ferreira**

---

## **Problema**
- A falta de dados estruturados e acessíveis de desempenho de times e jogadores dificulta a tomada de decisão por apostadores.
- Sites especializados, como SofaScore, têm dados valiosos, mas eles não estão diretamente disponíveis para análises automatizadas.

---

## **Solução Proposta**
- Criar um **crawler automatizado** que:
  - Coleta estatísticas de campeonatos, times e jogadores diretamente do site SofaScore.
  - Organiza os dados em formatos utilizáveis (ex.: JSON ou TXT).
  - Gera insights que podem ser usados para análise de probabilidades em apostas online.

---

## **Ferramentas Utilizadas**
### **Tecnologias**
- **Python**: Linguagem principal para o desenvolvimento.
- **Selenium**: Automação de navegação no navegador.
- **BeautifulSoup**: Parsing e extração de elementos HTML.
- **Chromedriver**: Controle do navegador Google Chrome.

### **Dependências**
- `selenium==4.9.1`
- `beautifulsoup4==4.12.2`

---

## **Metodologia de Coleta**
### **Etapas do Processo**
1. **Identificação do Campeonato**:
   - O usuário fornece a URL do campeonato no formato `campeonatos.json`.
2. **Extração de URLs dos Times**:
   - O crawler navega pelo site SofaScore e identifica os times participantes.
3. **Coleta de Estatísticas dos Times**:
   - Estatísticas gerais como ataque, defesa e precisão de passe.
4. **Coleta de Estatísticas dos Jogadores**:
   - Dados individuais, como partidas jogadas, gols, e outros indicadores.
5. **Armazenamento Estruturado**:
   - Dados organizados em arquivos e pastas com hierarquia definida.

---

## **Resultados**
- **Dados Coletados**:
  - Estatísticas gerais do campeonato.
  - Estatísticas detalhadas de cada time.
  - Estatísticas individuais de cada jogador.
- **Escalabilidade**:
  - Pode ser ajustado para outros campeonatos e esportes.
- **Impacto**:
  - Facilitação da tomada de decisões por apostadores baseada em dados.

---

## **Limitações**
- Atualmente, o sistema funciona apenas para campeonatos no formato **pontos corridos**.
- Dependência do layout do site SofaScore (sujeito a alterações).

---

## **Demonstração**
- Exibição do processo automatizado:
  1. Extração de dados do campeonato.
  2. Geração de arquivos com estatísticas organizadas.
- Apresentação dos arquivos resultantes e sua estrutura.

---

## **Conclusão**
- O **SofasCrawler** é uma solução inovadora para coleta de dados esportivos.
- Ele possibilita análises mais precisas em apostas online, democratizando o acesso a informações.
- Nosso objetivo é continuar expandindo e aprimorando a ferramenta.
